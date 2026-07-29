package agent

import (
	"context"
	"net/http"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

func TestRemoteMultiTurnConversation(t *testing.T) {
	endpoint := os.Getenv("RWKV_AGENT_INTEGRATION_URL")
	if endpoint == "" {
		t.Skip("RWKV_AGENT_INTEGRATION_URL is not set")
	}
	model := os.Getenv("RWKV_AGENT_INTEGRATION_MODEL")
	if model == "" {
		model = "rwkv-g1i-13b-4922"
	}
	headers := make(http.Header)
	for header, environment := range map[string]string{
		"CF-Access-Client-Id":     "RWKV_CF_ACCESS_CLIENT_ID",
		"CF-Access-Client-Secret": "RWKV_CF_ACCESS_CLIENT_SECRET",
	} {
		if value := os.Getenv(environment); value != "" {
			headers.Set(header, value)
		}
	}
	client, err := rwkvlightning.New(rwkvlightning.Config{
		Endpoint: endpoint,
		Model:    model,
		Password: os.Getenv("RWKV_API_PASSWORD"),
		Headers:  headers,
	})
	if err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools("testdata")
	if err != nil {
		t.Fatal(err)
	}
	runner, err := NewRunner(client, tools, Options{
		MaxSteps:                6,
		ProtocolRetries:         1,
		DecisionMaxOutputTokens: 256,
		Protocol:                G1IProtocol{},
		Renderer:                RWKVChatRenderer{},
		Router:                  G1IRouteProtocol{},
		RouteRenderer:           RWKVChatRenderer{},
		RouteRetries:            1,
		RouteMaxOutputTokens:    16,
		Generation: continuation.Request{
			Model:           model,
			MaxOutputTokens: 512,
			Sampling: continuation.Sampling{
				Temperature:  1,
				TopK:         1,
				TopP:         1,
				PenaltyDecay: 1,
			},
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Minute)
	defer cancel()

	greeting, err := runner.Run(ctx, "你好")
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("greeting: %s", greeting.Output)
	requireNoToolCalls(t, greeting)
	if greeting.Route != RouteRespond {
		t.Fatalf("greeting route = %q", greeting.Route)
	}
	if strings.TrimSpace(greeting.Output) == "" ||
		len([]rune(greeting.Output)) > 100 ||
		strings.Contains(greeting.Output, "BLUE-LANTERN") ||
		strings.Contains(greeting.Output, "README") {
		t.Fatalf("greeting produced an unrelated repository answer: %q", greeting.Output)
	}

	capabilities, err := runner.Run(
		ctx,
		"你有哪些工具？不要调用它们，请原样列出工具名。",
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("capabilities: %s", capabilities.Output)
	requireNoToolCalls(t, capabilities)
	if capabilities.Route != RouteRespond ||
		!strings.Contains(capabilities.Output, "list_files") ||
		!strings.Contains(capabilities.Output, "read_file") ||
		!strings.Contains(capabilities.Output, "search_text") {
		t.Fatalf("capability answer = %+v", capabilities)
	}

	first, err := runner.Run(
		ctx,
		"读取 multiturn-note.txt，报告 project code 和 owner code。必须原样保留代码，后续还会追问。",
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("turn 1: %s", first.Output)
	requireContainsCodes(t, first.Output)
	if first.Route != RouteInspect {
		t.Fatalf("file task route = %q", first.Route)
	}
	if len(first.Steps) < 1 || first.Steps[0].Tool != "read_file" {
		t.Fatalf("first turn did not read the fixture: %+v", first.Steps)
	}

	second, err := runner.Run(
		ctx,
		"不要调用工具。仅根据我们上一轮的对话，重复刚才文件中的 project code 和 owner code。",
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("turn 2: %s", second.Output)
	requireContainsCodes(t, second.Output)
	requireNoToolCalls(t, second)
	if second.Route != RouteRespond {
		t.Fatalf("history follow-up route = %q", second.Route)
	}

	third, err := runner.Run(
		ctx,
		"不要调用工具。刚才读取的文件名是什么？在同一句话中附上 project code。",
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Logf("turn 3: %s", third.Output)
	if !strings.Contains(third.Output, "multiturn-note.txt") ||
		!strings.Contains(third.Output, "BLUE-LANTERN-7319") {
		t.Fatalf("third turn did not retain the conversation: %q", third.Output)
	}
	requireNoToolCalls(t, third)
	if third.Route != RouteRespond {
		t.Fatalf("history filename route = %q", third.Route)
	}
	if got := runner.History(); len(got) < 8 {
		t.Fatalf("committed multi-turn history is too short: %+v", got)
	}
}

func requireNoToolCalls(t *testing.T, result Result) {
	t.Helper()
	for _, step := range result.Steps {
		if step.Tool != "" {
			t.Fatalf("turn unexpectedly called %s: %+v", step.Tool, result.Steps)
		}
	}
}

func requireContainsCodes(t *testing.T, output string) {
	t.Helper()
	for _, code := range []string{"BLUE-LANTERN-7319", "ORCHID-2048"} {
		if !strings.Contains(output, code) {
			t.Fatalf("output does not contain %s: %q", code, output)
		}
	}
}
