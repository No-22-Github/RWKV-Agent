package agent

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// The golden tests pin the exact bytes of every compiled model prompt across
// the profile matrix. The framing interacts with tokenizer boundaries (the
// withheld ">" of the think prefix, fence anchoring, trailing role openings),
// so a prompt refactor must keep these files byte-identical.

var updateGoldenPrompts = flag.Bool("update-golden-prompts", false, "rewrite the golden prompt files")

type goldenStep struct {
	Prompt string
	Stops  []string
	Budget int
}

func runGoldenTurn(
	t *testing.T,
	options Options,
	tools []Tool,
	outputs []string,
	history []Message,
	task string,
) []goldenStep {
	t.Helper()
	steps := make([]goldenStep, 0, len(outputs))
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		if len(steps) >= len(outputs) {
			return continuation.Result{}, fmt.Errorf("unexpected generation: %q", request.Prompt)
		}
		index := len(steps)
		steps = append(steps, goldenStep{
			Prompt: request.Prompt,
			Stops:  request.Stops,
			Budget: request.MaxOutputTokens,
		})
		return continuation.Result{
			Text:         outputs[index],
			FinishReason: continuation.FinishStop,
		}, nil
	})
	runner, err := NewRunner(generator, tools, options)
	if err != nil {
		t.Fatal(err)
	}
	if len(history) > 0 {
		if err := runner.RestoreHistory(history); err != nil {
			t.Fatal(err)
		}
	}
	if _, err := runner.RunWithObserver(context.Background(), task, nil); err != nil {
		t.Fatalf("run: %v", err)
	}
	if len(steps) != len(outputs) {
		t.Fatalf("captured %d prompts, want %d", len(steps), len(outputs))
	}
	return steps
}

func formatGolden(steps []goldenStep) string {
	var out strings.Builder
	for index, step := range steps {
		fmt.Fprintf(&out, "### step %d\n", index+1)
		fmt.Fprintf(&out, "max_output_tokens: %d\n", step.Budget)
		fmt.Fprintf(&out, "stops: %q\n", step.Stops)
		out.WriteString("prompt: <<<GOLDEN\n")
		out.WriteString(step.Prompt)
		out.WriteString("\nGOLDEN\n")
	}
	return out.String()
}

func compareGoldenPrompt(t *testing.T, name string, got string) {
	t.Helper()
	path := filepath.Join("testdata", "golden_prompt", name)
	if *updateGoldenPrompts {
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(got), 0o644); err != nil {
			t.Fatal(err)
		}
		return
	}
	want, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("golden file missing; run with -update-golden-prompts: %v", err)
	}
	if got != string(want) {
		t.Fatalf("compiled prompt drifted from %s\n--- want ---\n%s\n--- got ---\n%s", path, want, got)
	}
}

func TestGoldenPromptXMLToolThenFinal(t *testing.T) {
	t.Parallel()
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps: 3,
			Protocol: G1IProtocol{},
			Renderer: RWKVChatRenderer{},
		},
		[]Tool{echoTool{}},
		[]string{
			`<tool_call>{"name":"echo","arguments":{"value":"ping"}}</tool_call>`,
			"Echo: ping",
		},
		[]Message{
			{Role: RoleUser, Content: "Earlier question"},
			{Role: RoleAssistant, Content: "Earlier answer"},
		},
		"Check the echo tool",
	)
	compareGoldenPrompt(t, "xml_tool_then_final.txt", formatGolden(steps))
}

func TestGoldenPromptXMLThinkingFast(t *testing.T) {
	t.Parallel()
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps: 2,
			Protocol: G1IProtocol{},
			Renderer: RWKVChatRenderer{ThinkingMode: inference.ThinkingFast},
		},
		// The fast prompt withholds the closing ">" of the think prefix, so the
		// model's first byte completes the tag before the visible answer.
		[]Tool{echoTool{}},
		[]string{">你好！有什么我可以帮你的吗？"},
		nil,
		"你好",
	)
	compareGoldenPrompt(t, "xml_thinking_fast.txt", formatGolden(steps))
}

func TestGoldenPromptXMLThinkingFull(t *testing.T) {
	t.Parallel()
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps: 2,
			Protocol: G1IProtocol{},
			Renderer: RWKVChatRenderer{ThinkingMode: inference.ThinkingFull},
		},
		// The full prompt withholds the ">" that opens the think block; the
		// model writes the whole block itself before the visible answer.
		[]Tool{echoTool{}},
		[]string{"><think></think>你好！有什么我可以帮你的吗？"},
		nil,
		"你好",
	)
	compareGoldenPrompt(t, "xml_thinking_full.txt", formatGolden(steps))
}

func TestGoldenPromptXMLAnswerStage(t *testing.T) {
	t.Parallel()
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps: 2,
			Protocol: G1IProtocol{},
			Renderer: RWKVChatRenderer{},
		},
		[]Tool{echoTool{}},
		[]string{
			`<tool_call>{"name":"echo","arguments":{"value":"ping"}}</tool_call>`,
			"All done.",
		},
		nil,
		"Check the echo tool",
	)
	compareGoldenPrompt(t, "xml_answer_stage.txt", formatGolden(steps))
}

func TestGoldenPromptProductFencedToolThenAnswer(t *testing.T) {
	t.Parallel()
	// Three steps so the second decision runs after a tool result: that is the
	// step where the runner re-arms the fenced prefill prefix and the stop
	// list gains the fence terminator.
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps: 3,
			Protocol: G1IFunctionProtocol{Product: true},
			Renderer: G1IFunctionRenderer{Product: true},
		},
		[]Tool{echoTool{}},
		[]string{
			`{"name":"echo","arguments":{"value":"ping"}}`,
			`{"name":"echo","arguments":{"value":"pong"}}`,
			"All done.",
		},
		nil,
		"Check the echo tool",
	)
	compareGoldenPrompt(t, "product_fenced_tool_then_answer.txt", formatGolden(steps))
}

func TestGoldenPromptProductSubmitFencePrefix(t *testing.T) {
	t.Parallel()
	// Benchmark shape: the submit terminal tool keeps decisions in fenced-call
	// mode, and after one tool result the runner re-arms the fence prefill as
	// an injected assistant prefix (the prompt ends " ```json\n") while the
	// stop list gains the fence terminator.
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps:          2,
			Protocol:          G1IFunctionProtocol{Product: true},
			Renderer:          G1IFunctionRenderer{Product: true},
			TerminalTool:      "submit",
			EndOnTerminalTool: true,
		},
		[]Tool{echoTool{}, submitTestTool{}},
		[]string{
			`{"name":"echo","arguments":{"value":"ping"}}`,
			`{"name":"submit","arguments":{"answer":"All done."}}`,
		},
		nil,
		"Check the echo tool",
	)
	compareGoldenPrompt(t, "product_submit_fence_prefix.txt", formatGolden(steps))
}

func TestGoldenPromptFunctionsBenchmarkFence(t *testing.T) {
	t.Parallel()
	// Upstream benchmark transcript: non-product protocol/renderer pair with
	// submit and run_tests offered, where the renderer itself ends every
	// decision prompt inside the fence.
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps:          2,
			Protocol:          G1IFunctionProtocol{},
			Renderer:          G1IFunctionRenderer{HasSubmit: true, HasRunTests: true},
			TerminalTool:      "submit",
			EndOnTerminalTool: true,
		},
		[]Tool{echoTool{}, submitTestTool{}},
		[]string{
			`{"name":"echo","arguments":{"value":"ping"}}`,
			`{"name":"submit","arguments":{"answer":"All done."}}`,
		},
		nil,
		"Check the echo tool",
	)
	compareGoldenPrompt(t, "functions_benchmark_fence.txt", formatGolden(steps))
}
