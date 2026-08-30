package agent

import (
	"context"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// The preview exists so settings can show the system prompt without a model
// connection; if it ever drifts from the Runner's enforcement assembly, the
// preview becomes a lie. This pins the two together byte for byte.
func TestPreviewPromptsMatchRunnerControl(t *testing.T) {
	t.Parallel()
	options := Options{
		MaxSteps:    3,
		TaskControl: "Always answer in Chinese.",
		Protocol:    G1IProtocol{},
		Renderer:    RWKVChatRenderer{ThinkingMode: inference.ThinkingFast},
	}
	tools := []Tool{echoTool{}}
	preview, err := PreviewPrompts(options, tools, false)
	if err != nil {
		t.Fatal(err)
	}
	runner, err := NewRunner(
		continuation.GenerateFunc(func(context.Context, continuation.Request, continuation.EventSink) (continuation.Result, error) {
			return continuation.Result{}, nil
		}),
		tools,
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	if want := runner.controlForSpecs(runner.toolSpecs); preview.Control != want {
		t.Fatalf("preview control drifted from runner control\n--- preview ---\n%s\n--- runner ---\n%s", preview.Control, want)
	}
	if !strings.Contains(preview.Control, "Task-specific contract:\nAlways answer in Chinese.") {
		t.Fatalf("preview control is missing the task contract:\n%s", preview.Control)
	}
	if preview.ProtocolID != G1IEnvelopeProtocolV1 {
		t.Fatalf("protocol id = %q", preview.ProtocolID)
	}
	if preview.ThinkingMode != inference.ThinkingFast {
		t.Fatalf("thinking mode = %q", preview.ThinkingMode)
	}
	if len(preview.ToolNames) != 1 || preview.ToolNames[0] != "echo" {
		t.Fatalf("tool names = %v", preview.ToolNames)
	}
	native, err := PreviewPrompts(options, tools, true)
	if err != nil {
		t.Fatal(err)
	}
	if native.Control == preview.Control {
		t.Fatal("native preview control equals the text-continuation control")
	}
	if !strings.Contains(native.Control, "supplied through the API") {
		t.Fatalf("native control is missing the native tool preamble:\n%s", native.Control)
	}
}
