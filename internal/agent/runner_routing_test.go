package agent

import (
	"context"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// Characterization tests for the route-stage retry loop. runner_test.go covers
// routing end-to-end; these lock the RouteStep bookkeeping (attempt numbering,
// recorded prompt traces, error text, failed-closed fallback) and the retry
// echo/correction transcript bytes that the decideRoute/decideToolRoute
// unification must preserve.

func scriptedRouteGenerator(outputs []string, prompts *[]string) continuation.Generator {
	return continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		*prompts = append(*prompts, request.Prompt)
		output := outputs[len(*prompts)-1]
		return continuation.Result{Text: output, FinishReason: continuation.FinishStop}, nil
	})
}

func TestDecideRouteRecordsRetryStepsThenSucceeds(t *testing.T) {
	t.Parallel()
	var prompts []string
	generator := scriptedRouteGenerator([]string{
		"garbage without an envelope",
		"<route>inspect</route>",
		`<tool_call>{"name":"echo","arguments":{"value":"hi"}}</tool_call>`,
		"The tool returned hi.",
	}, &prompts)
	runner, err := NewRunner(generator, []Tool{echoTool{}}, Options{
		MaxSteps:             4,
		Router:               G1IRouteProtocol{},
		RouteRetries:         1,
		Generation:           continuation.Request{MaxOutputTokens: 16},
		TracePromptBytes:     4096,
		RouteMaxOutputTokens: 16,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Read README.md and report its title.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Route != RouteInspect {
		t.Fatalf("route = %q", result.Route)
	}
	if len(result.RouteSteps) != 2 {
		t.Fatalf("route steps = %+v", result.RouteSteps)
	}
	first := result.RouteSteps[0]
	if first.Attempt != 1 ||
		first.Request == nil ||
		first.ModelOutput != "garbage without an envelope" ||
		first.DurationMS < 0 ||
		!strings.Contains(first.ProtocolError, `invalid route "garbage without an envelope"`) ||
		first.Route != "" ||
		first.FailedClosed {
		t.Fatalf("first route step = %+v", first)
	}
	second := result.RouteSteps[1]
	if second.Attempt != 2 ||
		second.ProtocolError != "" ||
		second.Route != RouteInspect ||
		second.FailedClosed {
		t.Fatalf("second route step = %+v", second)
	}
	if len(prompts) != 4 {
		t.Fatalf("generation prompts = %d", len(prompts))
	}
	// The rejected attempt is echoed back and answered by the correction turn.
	if !strings.Contains(prompts[1], "garbage without an envelope") ||
		!strings.Contains(prompts[1], "Your previous route was invalid.") {
		t.Fatalf("retry prompt lost the echo or correction:\n%s", prompts[1])
	}
}

func TestDecideRouteFailsClosedToRespondAfterRetries(t *testing.T) {
	t.Parallel()
	var prompts []string
	generator := scriptedRouteGenerator([]string{
		"first garbage",
		"second garbage",
		"plain answer",
	}, &prompts)
	runner, err := NewRunner(generator, nil, Options{
		MaxSteps:             2,
		Router:               G1IRouteProtocol{},
		RouteRetries:         1,
		Generation:           continuation.Request{MaxOutputTokens: 16},
		TracePromptBytes:     4096,
		RouteMaxOutputTokens: 16,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "What tools can you use?")
	if err != nil {
		t.Fatal(err)
	}
	if result.Route != RouteRespond {
		t.Fatalf("route = %q, want failed-closed respond", result.Route)
	}
	if len(result.RouteSteps) != 2 {
		t.Fatalf("route steps = %+v", result.RouteSteps)
	}
	last := result.RouteSteps[1]
	if last.Attempt != 2 ||
		last.Route != RouteRespond ||
		!last.FailedClosed ||
		last.ProtocolError == "" {
		t.Fatalf("failed-closed step = %+v", last)
	}
}

func TestDecideToolRouteRecordsRetryStepsThenSelectsBundle(t *testing.T) {
	t.Parallel()
	var prompts []string
	generator := scriptedRouteGenerator([]string{
		"no envelope here",
		"<route>inspect:workspace</route>",
		`<tool_call>{"name":"echo","arguments":{"value":"hi"}}</tool_call>`,
		"The tool returned hi.",
	}, &prompts)
	runner, err := NewRunner(
		generator,
		[]Tool{bundledEchoTool{name: "echo", bundle: ToolBundleWorkspace}},
		Options{
			MaxSteps:             4,
			ToolRouter:           G1IProgressiveToolRouteProtocol{},
			ToolBundles:          DefaultToolBundles(),
			RouteRetries:         1,
			Generation:           continuation.Request{MaxOutputTokens: 16},
			TracePromptBytes:     4096,
			RouteMaxOutputTokens: 16,
		})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "List files in the workspace root.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Route != RouteInspect {
		t.Fatalf("route = %q", result.Route)
	}
	if len(result.Bundles) != 1 || result.Bundles[0] != "workspace" {
		t.Fatalf("bundles = %v", result.Bundles)
	}
	if len(result.RouteSteps) != 2 {
		t.Fatalf("route steps = %+v", result.RouteSteps)
	}
	first := result.RouteSteps[0]
	if first.Attempt != 1 ||
		first.Request == nil ||
		!strings.Contains(first.ProtocolError, `invalid progressive route "no envelope here"`) ||
		first.FailedClosed {
		t.Fatalf("first tool route step = %+v", first)
	}
	second := result.RouteSteps[1]
	if second.Attempt != 2 ||
		second.Route != RouteInspect ||
		len(second.Bundles) != 1 ||
		second.Bundles[0] != "workspace" ||
		second.ProtocolError != "" {
		t.Fatalf("second tool route step = %+v", second)
	}
	if !strings.Contains(prompts[1], "no envelope here") ||
		!strings.Contains(prompts[1], "Output exactly one concrete route from this list") {
		t.Fatalf("retry prompt lost the echo or correction:\n%s", prompts[1])
	}
}
