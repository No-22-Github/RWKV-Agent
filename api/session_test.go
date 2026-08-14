package api

import (
	"context"
	"io"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestUnifiedSessionReadsREADMEAndReturnsFirstLine(t *testing.T) {
	t.Parallel()
	workspace := t.TempDir()
	const firstLine = "# RWKV Agent acceptance fixture"
	if err := os.WriteFile(filepath.Join(workspace, "README.md"), []byte(firstLine+"\nsecond line\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	service, err := NewService(Options{Workspace: workspace})
	if err != nil {
		t.Fatal(err)
	}
	service.config = Config{
		Provider: ProviderChatCompletions, Model: "scripted", MaxSteps: 4,
		MaxTokens: 256, Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1,
		Thinking: "off",
	}
	outputs := []string{
		`inspect:workspace</route>`,
		`{"name":"read_file","arguments":{"path":"README.md"}}`,
		`{"name":"submit","arguments":{"answer":"` + firstLine + `"}}`,
	}
	var requests []continuation.Request
	var mu sync.Mutex
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		mu.Lock()
		defer mu.Unlock()
		if len(outputs) == 0 {
			t.Fatalf("unexpected extra generation; prompt=%q", request.Prompt)
		}
		requests = append(requests, request)
		output := outputs[0]
		outputs = outputs[1:]
		return continuation.Result{Text: output, FinishReason: continuation.FinishStop}, nil
	})
	session, err := newSession(service, generator, io.NopCloser(strings.NewReader("")), workspace, Status{Model: "scripted"})
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	var events []Event
	result, err := session.RunWithObserver(context.Background(), "读取 README 并只输出第一行。", func(event Event) {
		events = append(events, event)
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != firstLine {
		t.Fatalf("output = %q", result.Output)
	}
	if len(requests) != 3 || !strings.HasSuffix(requests[1].Prompt, "Assistant: ```json\n") ||
		!strings.Contains(requests[2].Prompt, "User: Function output:\n") ||
		!strings.HasSuffix(requests[2].Prompt, "Assistant: ```json\n") {
		t.Fatalf("Markdown transcript requests = %+v", requests)
	}
	if len(result.Steps) != 2 || result.Steps[0].Tool != "read_file" || !result.Steps[0].ToolExecuted {
		t.Fatalf("steps = %+v", result.Steps)
	}
	toolStarted := false
	for _, event := range events {
		if event.Kind == EventToolStart && event.Tool == "read_file" {
			toolStarted = true
		}
	}
	if !toolStarted {
		t.Fatalf("events = %+v", events)
	}
}

func TestOwnerWebProvidersAreSharedAcrossSessions(t *testing.T) {
	t.Parallel()
	service, err := NewService(Options{Workspace: t.TempDir()})
	if err != nil {
		t.Fatal(err)
	}
	config := Config{
		EnableWeb: true, BraveAPIKey: "brave-secret", TavilyAPIKey: "tavily-secret",
	}
	first, err := ownerWebProviders(service, config)
	if err != nil {
		t.Fatal(err)
	}
	second, err := ownerWebProviders(service, config)
	if err != nil {
		t.Fatal(err)
	}
	if first != second || first.search != second.search || first.fetch != second.fetch {
		t.Fatalf("web providers were not shared: first=%p second=%p", first, second)
	}
}
