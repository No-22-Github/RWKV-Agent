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

func TestUnifiedSessionDefaultsToXMLWithoutRouter(t *testing.T) {
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
	config, err := normalizeConfig(Config{
		Provider: ProviderChatCompletions, Model: "scripted", Endpoint: "https://example.test/v1/chat/completions", MaxSteps: 4,
		MaxTokens: 1024, Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1,
		Thinking: "off",
	})
	if err != nil {
		t.Fatal(err)
	}
	service.config = config
	// With no Router the XML decision stage chooses directly between a complete
	// tool envelope and ordinary final text.
	outputs := []string{
		`<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
		firstLine,
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
	if len(requests) != 2 || requests[0].MaxOutputTokens != 512 ||
		!strings.Contains(requests[0].Prompt, `<tool_call>{"name":"TOOL_NAME"`) ||
		!strings.HasSuffix(requests[0].Prompt, "Assistant:") ||
		!strings.Contains(requests[1].Prompt, "Tool: <tool_result>") ||
		!strings.HasSuffix(requests[1].Prompt, "Assistant:") {
		t.Fatalf("XML transcript requests = %+v", requests)
	}
	if len(result.Steps) != 2 || result.Steps[0].Tool != "read_file" || !result.Steps[0].ToolExecuted {
		t.Fatalf("steps = %+v", result.Steps)
	}
	if len(result.RouteSteps) != 0 || result.Steps[0].Request == nil ||
		result.Steps[0].Request.Bytes == 0 || result.Steps[0].ToolResult == "" {
		t.Fatalf("public trace = %+v", result)
	}
	toolStarted := false
	routeStarted := false
	for _, event := range events {
		if event.Kind == EventToolStart && event.Tool == "read_file" {
			toolStarted = true
		}
		if event.Kind == EventRouteStart {
			routeStarted = true
		}
	}
	if !toolStarted || routeStarted {
		t.Fatalf("events = %+v", events)
	}
}

func TestSessionProductExperimentsUseSharedTextProfile(t *testing.T) {
	t.Parallel()
	workspace := t.TempDir()
	service, err := NewService(Options{Workspace: workspace})
	if err != nil {
		t.Fatal(err)
	}
	defer service.Close()
	progressive := false
	service.config = Config{
		Provider: ProviderRWKVLightning, Model: "scripted", MaxSteps: 2,
		MaxTokens: 128, RouteMaxTokens: 48,
		Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1,
		AgentProtocol: AgentProtocolMarkdown, ProgressiveTools: &progressive,
		SemanticNoTool: boolPointer(true), DecisionFakeThink: true,
	}
	outputs := []string{
		`>{"name":"no_tool","arguments":{"reason":"No tool is needed for this question.","answer":"Candidate text."}}`,
	}
	var requests []continuation.Request
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		requests = append(requests, request)
		return continuation.Result{Text: outputs[len(requests)-1], FinishReason: continuation.FinishStop}, nil
	})
	session, err := newSession(
		service,
		generator,
		io.NopCloser(strings.NewReader("")),
		workspace,
		Status{Model: "scripted"},
	)
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	result, err := session.Run(context.Background(), "Answer this self-contained question.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "Candidate text." || len(result.Steps) != 1 ||
		result.Steps[0].ActionType != "no_tool" || result.Steps[0].ToolExecuted ||
		result.Steps[0].ToolEvidence ||
		result.Steps[0].NoToolRationale != "No tool is needed for this question." ||
		result.Steps[0].NoToolAnswer != "Candidate text." ||
		!strings.HasSuffix(requests[0].Prompt, "Assistant: <think></think") ||
		len(requests) != 1 {
		t.Fatalf("product experiment result = %+v, requests = %+v", result, requests)
	}
}

// TestSessionXMLProtocolUsesEnvelopeProfile pins the byte shape of the
// --agent-protocol xml branch after it moved from a hand-written agent.Options
// literal to agent.XMLHarnessOptions: the XML control frame, the half-open
// think prefix that only this profile supports, and the <tool_call> envelope.
func TestSessionXMLProtocolUsesEnvelopeProfile(t *testing.T) {
	t.Parallel()
	workspace := t.TempDir()
	const firstLine = "# XML profile fixture"
	if err := os.WriteFile(
		filepath.Join(workspace, "README.md"),
		[]byte(firstLine+"\n"),
		0o600,
	); err != nil {
		t.Fatal(err)
	}
	service, err := NewService(Options{Workspace: workspace})
	if err != nil {
		t.Fatal(err)
	}
	defer service.Close()
	progressive := false
	service.config = Config{
		Provider: ProviderRWKVLightning, Model: "scripted", MaxSteps: 4,
		MaxTokens: 256, DecisionMaxTokens: 128, RouteMaxTokens: 48,
		Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1,
		AgentProtocol: AgentProtocolXML, ProgressiveTools: &progressive,
		Thinking: "fast",
	}
	outputs := []string{
		`><tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
		`>` + firstLine,
	}
	var requests []continuation.Request
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		requests = append(requests, request)
		return continuation.Result{
			Text:         outputs[len(requests)-1],
			FinishReason: continuation.FinishStop,
		}, nil
	})
	session, err := newSession(
		service,
		generator,
		io.NopCloser(strings.NewReader("")),
		workspace,
		Status{Model: "scripted"},
	)
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	result, err := session.Run(context.Background(), "Read README.md and report its title.")
	if err != nil {
		t.Fatal(err)
	}
	if len(requests) != 2 {
		t.Fatalf("xml profile made %d model calls: %+v", len(requests), requests)
	}
	// The XML control frame, not the product Tools: catalog.
	if !strings.Contains(requests[0].Prompt, "<tool_call>{\"name\":\"TOOL_NAME\"") ||
		strings.Contains(requests[0].Prompt, "System: Tools:\n[") {
		t.Fatalf("xml control prompt = %q", requests[0].Prompt)
	}
	// Only the XML renderer prefills the half-open think prefix.
	if !strings.HasSuffix(requests[0].Prompt, "Assistant: <think></think") {
		t.Fatalf("xml decision prompt tail = %q", requests[0].Prompt)
	}
	if result.Steps[0].Tool != "read_file" || !result.Steps[0].ToolExecuted {
		t.Fatalf("xml tool step = %+v", result.Steps[0])
	}
	if !strings.Contains(result.Output, firstLine) {
		t.Fatalf("xml output = %q", result.Output)
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
