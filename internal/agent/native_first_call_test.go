package agent

import (
	"context"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// TestNativeFirstCallSwitch locks the firstcall axis end to end: with a native
// tool completer present, "auto" compiles the first decision step with
// requireNative=false (tool_choice=auto), while "" and "required" keep the
// product tool_choice=required escalation.
func TestNativeFirstCallSwitch(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		value       string
		wantRequire bool
	}{
		{"", true},
		{"required", true},
		{"auto", false},
	} {
		options := ProductHarnessOptions(ProductHarnessConfig{
			MaxSteps:   3,
			Generation: continuation.Request{Model: "native-model", MaxOutputTokens: 256},
		})
		options.NativeFirstCall = testCase.value
		runner, err := NewRunner(&scriptedNativeGenerator{}, []Tool{nativeEchoTool{}}, options)
		if err != nil {
			t.Fatalf("NewRunner(NativeFirstCall=%q): %v", testCase.value, err)
		}
		turn := newRunnerTurn(runner, context.Background(), "Check the echo tool", nil)
		if got := turn.stepPromptInput().requireNative; got != testCase.wantRequire {
			t.Fatalf("NativeFirstCall=%q requireNative = %v, want %v", testCase.value, got, testCase.wantRequire)
		}
	}
}

// TestNativeFirstCallAutoReachesProvider runs one native turn with the axis
// set through the wire spec and asserts the provider request itself carries
// tool_choice=auto on the first step.
func TestNativeFirstCallAutoReachesProvider(t *testing.T) {
	t.Parallel()
	base := ProductHarnessOptions(ProductHarnessConfig{
		MaxSteps:   3,
		Generation: continuation.Request{Model: "native-model", MaxOutputTokens: 256},
	})
	spec := wire.Default()
	spec.Format = wire.FormatMDFence
	spec.Transport = wire.TransportNative
	spec.FirstCall = wire.FirstCallAuto
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
	if _, err := runner.Run(context.Background(), "Check the echo tool"); err != nil {
		t.Fatal(err)
	}
	if len(generator.requests) == 0 {
		t.Fatal("no native requests recorded")
	}
	if got := generator.requests[0].ToolChoice; got != toolchat.ToolChoiceAuto {
		t.Fatalf("first tool_choice = %q, want auto", got)
	}
}
