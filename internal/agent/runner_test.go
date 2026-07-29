package agent

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestRunnerExecutesToolThenReturnsFinal(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`<tool_call>{"name":"echo","arguments":{"value":"hello"}}</tool_call>`,
		`The tool returned hello.`,
	}
	var prompts []string
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		prompts = append(prompts, request.Prompt)
		output := outputs[len(prompts)-1]
		return continuation.Result{
			Text:         output,
			FinishReason: continuation.FinishStop,
		}, nil
	})
	runner, err := NewRunner(generator, []Tool{echoTool{}}, Options{MaxSteps: 3})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use echo.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "The tool returned hello." {
		t.Fatalf("output = %q", result.Output)
	}
	if len(result.Steps) != 2 || result.Steps[0].Tool != "echo" {
		t.Fatalf("steps = %+v", result.Steps)
	}
	if len(prompts) != 2 {
		t.Fatalf("continuation prompts = %+v", prompts)
	}
	for _, fragment := range []string{
		"System: You are the final repository answer stage.",
		"User: Use echo.",
		"Tool: <tool_result>",
		`"ok":true`,
		`"result":{"value":"hello"}`,
		`"tool":"echo"`,
		"Assistant: <answer>",
	} {
		if !strings.Contains(prompts[1], fragment) {
			t.Fatalf("second prompt does not contain %q:\n%s", fragment, prompts[1])
		}
	}
}

func TestRunnerSupportsInlineControlPrompt(t *testing.T) {
	t.Parallel()
	var prompt string
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompt = request.Prompt
			return continuation.Result{Text: `<answer>done</answer>`}, nil
		}),
		nil,
		Options{ControlPrompt: ControlPromptInline},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "task"); err != nil {
		t.Fatal(err)
	}
	if strings.Contains(prompt, "System:") ||
		!strings.Contains(prompt, "Repository task:\ntask") ||
		!strings.HasSuffix(prompt, "Assistant:") {
		t.Fatalf("prompt = %q", prompt)
	}
}

func TestRunnerRoutesCasualGreetingWithoutWorkspaceTools(t *testing.T) {
	t.Parallel()

	var prompts []string
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompts = append(prompts, request.Prompt)
			if len(prompts) == 1 {
				return continuation.Result{
					Text:         "respond",
					FinishReason: continuation.FinishStop,
				}, nil
			}
			return continuation.Result{
				Text:         "你好！有什么我可以帮你的吗？",
				FinishReason: continuation.FinishStop,
			}, nil
		}),
		[]Tool{echoTool{}},
		Options{
			Router:               G1IRouteProtocol{},
			RouteMaxOutputTokens: 16,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "你好")
	if err != nil {
		t.Fatal(err)
	}
	if len(prompts) != 2 ||
		strings.Contains(prompts[0], "Available tools:") ||
		!strings.Contains(prompts[0], "requires NEW evidence") ||
		strings.Contains(prompts[1], "Available tools:") ||
		!strings.Contains(prompts[1], "Workspace tools are unavailable") {
		t.Fatalf("greeting prompts were not isolated from tools:\n%q", prompts)
	}
	if result.Output != "你好！有什么我可以帮你的吗？" ||
		result.Route != RouteRespond ||
		len(result.Steps) != 1 ||
		result.Steps[0].Tool != "" {
		t.Fatalf("greeting result = %+v", result)
	}
}

func TestRunnerRejectsToolAttemptForCasualGreeting(t *testing.T) {
	t.Parallel()

	outputs := []continuation.Result{
		{Text: "respond", FinishReason: continuation.FinishStop},
		{
			Text:         `<tool_call>{"name":"counting_echo","arguments":{"value":"wrong"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "你好！", FinishReason: continuation.FinishStop},
	}
	calls := 0
	tool := &countingEchoTool{calls: &calls}
	generations := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			result := outputs[generations]
			generations++
			return result, nil
		}),
		[]Tool{tool},
		Options{
			MaxSteps:        3,
			ProtocolRetries: 1,
			Router:          G1IRouteProtocol{},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "你好！")
	if err != nil {
		t.Fatal(err)
	}
	if calls != 0 {
		t.Fatalf("casual greeting executed a workspace tool %d time(s)", calls)
	}
	if result.Output != "你好！" ||
		result.Route != RouteRespond ||
		len(runner.History()) != 2 {
		t.Fatalf("greeting result=%+v history=%+v", result, runner.History())
	}
}

func TestRunnerUsesIndependentG1IAnswerStageAfterTool(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"hello"}}`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         "The tool returned hello.",
			FinishReason: continuation.FinishStop,
		},
	}
	var requests []continuation.Request
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			requests = append(requests, request)
			return outputs[len(requests)-1], nil
		}),
		[]Tool{echoTool{}},
		Options{
			MaxSteps:                3,
			DecisionMaxOutputTokens: 256,
			Protocol:                G1IProtocol{},
			Generation: continuation.Request{
				MaxOutputTokens: 1024,
			},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use echo.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "The tool returned hello." || len(requests) != 2 {
		t.Fatalf("result=%+v requests=%d", result, len(requests))
	}
	second := requests[1].Prompt
	for _, fragment := range []string{
		"System: You are the final repository answer stage.",
		"User: Use echo.",
		`"result":{"value":"hello"}`,
		`"tool":"echo"}</tool_result>`,
		"Assistant: <answer>",
	} {
		if !strings.Contains(second, fragment) {
			t.Fatalf("second prompt does not contain %q:\n%s", fragment, second)
		}
	}
	if strings.Contains(second, "Available tools:") {
		t.Fatalf("answer prompt leaked tool routing instructions:\n%s", second)
	}
	if strings.Contains(strings.Join(requests[0].Stops, "\x00"), "</answer>") ||
		strings.Contains(strings.Join(requests[1].Stops, "\x00"), "</tool_call>") {
		t.Fatalf("stage stops = decision:%q answer:%q", requests[0].Stops, requests[1].Stops)
	}
	if requests[0].MaxOutputTokens != 256 || requests[1].MaxOutputTokens != 1024 {
		t.Fatalf(
			"stage token limits = decision:%d answer:%d",
			requests[0].MaxOutputTokens,
			requests[1].MaxOutputTokens,
		)
	}
}

func TestRunnerRetriesProtocolOnce(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`{"name":"missing","arguments":{}}`,
		`done`,
	}
	calls := 0
	retries := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			output := outputs[calls]
			calls++
			return continuation.Result{Text: output}, nil
		}),
		nil,
		Options{
			MaxSteps:        3,
			ProtocolRetries: 1,
			Observe: func(event Event) {
				if event.Kind == EventRetry {
					retries++
				}
			},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Answer.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || calls != 2 || retries != 1 {
		t.Fatalf("result=%+v calls=%d retries=%d", result, calls, retries)
	}
}

func TestRunnerCarriesCommittedHistoryAcrossTurns(t *testing.T) {
	t.Parallel()

	outputs := []string{"The title is Example.", "It was README.md."}
	var prompts []string
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompts = append(prompts, request.Prompt)
			return continuation.Result{
				Text:         outputs[len(prompts)-1],
				FinishReason: continuation.FinishStop,
			}, nil
		}),
		nil,
		Options{},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "What is the title?"); err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "Which file was that from?"); err != nil {
		t.Fatal(err)
	}
	for _, fragment := range []string{
		"User: What is the title?",
		"Assistant: The title is Example.",
		"User: Which file was that from?",
	} {
		if !strings.Contains(prompts[1], fragment) {
			t.Fatalf("second prompt does not contain %q:\n%s", fragment, prompts[1])
		}
	}
	history := runner.History()
	if len(history) != 4 ||
		history[0].Role != RoleUser ||
		history[1].Role != RoleAssistant ||
		history[2].Content != "Which file was that from?" ||
		history[3].Content != "It was README.md." {
		t.Fatalf("history = %+v", history)
	}
}

func TestRunnerCommitsToolTraceAndRollsBackFailedTurn(t *testing.T) {
	t.Parallel()

	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			calls++
			switch calls {
			case 1:
				return continuation.Result{
					Text: `<tool_call>{"name":"echo","arguments":{"value":"hello"}}</tool_call>`,
				}, nil
			case 2:
				return continuation.Result{
					Text:         "hello",
					FinishReason: continuation.FinishStop,
				}, nil
			default:
				return continuation.Result{}, context.Canceled
			}
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "Use echo."); err != nil {
		t.Fatal(err)
	}
	history := runner.History()
	if len(history) != 4 ||
		history[1].Role != RoleAssistant ||
		history[2].Role != RoleTool ||
		history[3].Content != "hello" {
		t.Fatalf("tool history = %+v", history)
	}
	if _, err := runner.Run(context.Background(), "This turn fails."); !errors.Is(err, context.Canceled) {
		t.Fatalf("failed turn error = %v", err)
	}
	if got := runner.History(); len(got) != len(history) {
		t.Fatalf("failed turn changed history: before=%+v after=%+v", history, got)
	}
	runner.Reset()
	if got := runner.History(); len(got) != 0 {
		t.Fatalf("history after reset = %+v", got)
	}
}

func TestToolAnswerStageRetainsEarlierTurns(t *testing.T) {
	t.Parallel()

	outputs := []continuation.Result{
		{Text: "README.md is the relevant file.", FinishReason: continuation.FinishStop},
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"# Example"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "Its title is Example.", FinishReason: continuation.FinishStop},
	}
	var prompts []string
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompts = append(prompts, request.Prompt)
			return outputs[len(prompts)-1], nil
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "Which file is relevant?"); err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "Read it and tell me its title."); err != nil {
		t.Fatal(err)
	}
	answerPrompt := prompts[2]
	for _, fragment := range []string{
		"User: Which file is relevant?",
		"Assistant: README.md is the relevant file.",
		"User: Read it and tell me its title.",
		`"value":"# Example"`,
	} {
		if !strings.Contains(answerPrompt, fragment) {
			t.Fatalf("answer prompt does not contain %q:\n%s", fragment, answerPrompt)
		}
	}
}

func TestRunnerStopsAtStepLimitAfterToolFailures(t *testing.T) {
	t.Parallel()
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			return continuation.Result{
				Text: `<tool_call>{"name":"missing","arguments":{"value":"again"}}</tool_call>`,
			}, nil
		}),
		nil,
		Options{MaxSteps: 2},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Loop.")
	if !errors.Is(err, ErrMaxSteps) {
		t.Fatalf("error = %v, want ErrMaxSteps", err)
	}
	if len(result.Steps) != 2 {
		t.Fatalf("steps = %d", len(result.Steps))
	}
	if result.Steps[1].ToolError != `unknown tool "missing"` {
		t.Fatalf("failed step = %+v", result.Steps[1])
	}
}

type echoTool struct{}

func (echoTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "echo",
		Description: "Return a value.",
		Arguments:   `{"value":"string"}`,
	}
}

type countingEchoTool struct {
	calls *int
}

func (t *countingEchoTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "counting_echo",
		Description: "Count executions and return a value.",
		Arguments:   `{"value":"string"}`,
	}
}

func (t *countingEchoTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	*t.calls++
	var args struct {
		Value string `json:"value"`
	}
	if err := json.Unmarshal(raw, &args); err != nil {
		return nil, err
	}
	return args.Value, nil
}

func (echoTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Value string `json:"value"`
	}
	if err := json.Unmarshal(raw, &args); err != nil {
		return nil, err
	}
	if args.Value == "" {
		return nil, fmt.Errorf("value is required")
	}
	return map[string]string{"value": args.Value}, nil
}
