package agent

import (
	"context"
	"encoding/json"
	"errors"
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// scriptedNativeGenerator is a native-only provider: the text-continuation
// path is an error, so a regression that falls back to it fails loudly.
type scriptedNativeGenerator struct {
	results  []toolchat.Result
	requests []toolchat.Request
}

func (g *scriptedNativeGenerator) Continue(
	context.Context,
	continuation.Request,
	continuation.EventSink,
) (continuation.Result, error) {
	return continuation.Result{}, errors.New("text continuation used on the native path")
}

func (g *scriptedNativeGenerator) Complete(
	_ context.Context,
	request toolchat.Request,
	_ continuation.EventSink,
) (toolchat.Result, error) {
	g.requests = append(g.requests, request)
	if len(g.requests) > len(g.results) {
		return toolchat.Result{}, errors.New("unexpected native completion")
	}
	return g.results[len(g.requests)-1], nil
}

func (*scriptedNativeGenerator) NativeToolCalling() bool { return true }

type nativeEchoTool struct{}

func (nativeEchoTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "echo",
		Description: "Return a value.",
		Arguments:   `{"value":"string"}`,
		Parameters: json.RawMessage(`{"type":"object","properties":{"value":{"type":"string"}},` +
			`"required":["value"],"additionalProperties":false}`),
		Strict: true,
	}
}

func (nativeEchoTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Value string `json:"value"`
	}
	if err := json.Unmarshal(raw, &args); err != nil {
		return nil, err
	}
	return map[string]string{"value": args.Value}, nil
}

// TestNativeTransportGolden locks the native Chat Completions path, which the
// text-continuation golden matrix cannot reach: the JSON request trace, the
// native message translation, the tool catalog ordering, and the tool_choice
// escalation on the first decision.
func TestNativeTransportGolden(t *testing.T) {
	t.Parallel()
	// Native transport: the spec must say so (transport=native, no prefill),
	// because the runner only detects the provider, not the intent.
	base := ProductHarnessOptions(ProductHarnessConfig{
		MaxSteps:         3,
		TracePromptBytes: DefaultTracePromptBytes,
		Generation:       continuation.Request{Model: "native-model", MaxOutputTokens: 256},
	})
	spec := wire.Default()
	spec.Format = wire.FormatMDFence
	spec.Transport = wire.TransportNative
	options, err := OptionsWithWire(base, spec)
	if err != nil {
		t.Fatal(err)
	}
	generator := &scriptedNativeGenerator{results: []toolchat.Result{
		{
			ToolCalls: []toolchat.ToolCall{{
				ID:        "call_1",
				Name:      "echo",
				Arguments: `{"value":"ping"}`,
			}},
			FinishReason: continuation.FinishToolCalls,
		},
		{Content: "All done.", FinishReason: continuation.FinishStop},
	}}
	runner, err := NewRunner(generator, []Tool{nativeEchoTool{}}, options)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Check the echo tool")
	if err != nil {
		t.Fatal(err)
	}

	// The trace prompt on the native path is the JSON request description.
	steps := make([]goldenStep, 0, len(result.Steps))
	for _, step := range result.Steps {
		if step.Request == nil {
			continue
		}
		steps = append(steps, goldenStep{
			Prompt: step.Request.Prompt,
			Stops:  step.Request.Stops,
			Budget: step.Request.MaxOutputTokens,
		})
	}
	compareGoldenPrompt(
		t,
		filepath.Join("wire", "native_tool_then_answer.txt"),
		formatGolden(steps),
	)

	if len(generator.requests) != 2 {
		t.Fatalf("native completions = %d, want 2", len(generator.requests))
	}
	first := generator.requests[0]
	if first.ToolChoice != toolchat.ToolChoiceRequired {
		t.Fatalf("first tool_choice = %q, want required", first.ToolChoice)
	}
	if len(first.Tools) != 1 || first.Tools[0].Name != "echo" {
		t.Fatalf("first tools = %+v", first.Tools)
	}
	if first.AssistantPrefix != "" {
		t.Fatalf("native prefill must be cleared when tools are offered: %q", first.AssistantPrefix)
	}
	second := generator.requests[1]
	if second.ToolChoice != toolchat.ToolChoiceAuto {
		t.Fatalf("second tool_choice = %q, want auto", second.ToolChoice)
	}
	// The tool result must travel back as a proper assistant/tool pair.
	var sawAssistantCall, sawToolResult bool
	for _, message := range second.Messages {
		if message.Role == toolchat.RoleAssistant && len(message.ToolCalls) == 1 &&
			message.ToolCalls[0].ID == "call_1" {
			sawAssistantCall = true
		}
		if message.Role == toolchat.RoleTool && message.ToolCallID == "call_1" &&
			message.Content == `{"value":"ping"}` {
			sawToolResult = true
		}
	}
	if !sawAssistantCall || !sawToolResult {
		t.Fatalf("second request messages = %+v", second.Messages)
	}
}
