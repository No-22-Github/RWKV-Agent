package agent

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestRunnerRequiresTwoStepsForToolConvergence(t *testing.T) {
	t.Parallel()
	_, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			return continuation.Result{}, nil
		}),
		nil,
		Options{MaxSteps: 1},
	)
	if !errors.Is(err, continuation.ErrInvalidRequest) ||
		!strings.Contains(err.Error(), "at least two steps") {
		t.Fatalf("error = %v", err)
	}
}

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
			Usage: continuation.Usage{
				PromptTokens:     10 + len(prompts),
				CompletionTokens: len(prompts),
			},
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
	first := result.Steps[0]
	if first.Stage != StageDecision ||
		first.ActionType != "tool" ||
		first.FinishReason != continuation.FinishStop ||
		first.Usage.PromptTokens != 11 ||
		string(first.ToolArguments) != `{"value":"hello"}` ||
		!strings.Contains(string(first.ToolResult), `"value":"hello"`) ||
		first.ToolError != "" ||
		first.ProtocolError != "" {
		t.Fatalf("first step trace = %+v", first)
	}
	second := result.Steps[1]
	if second.Stage != StageDecision ||
		second.ActionType != "final" ||
		second.FinishReason != continuation.FinishStop ||
		second.Usage.CompletionTokens != 2 ||
		second.Tool != "" {
		t.Fatalf("second step trace = %+v", second)
	}
	if len(prompts) != 2 {
		t.Fatalf("continuation prompts = %+v", prompts)
	}
	for _, fragment := range []string{
		"System: You are a read-only repository agent.",
		"User: Use echo.",
		`Assistant: <tool_call>{"name":"echo","arguments":{"value":"hello"}}</tool_call>`,
		"Tool: <tool_result>",
		`"ok":true`,
		`"result":{"value":"hello"}`,
		`"tool":"echo"`,
		"If the evidence is sufficient, answer now.",
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

func TestRunnerCanUseMultipleSuccessfulToolsBeforeAnswer(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"first"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"second"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         "The tools returned first and second.",
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
	if result.Output != "The tools returned first and second." ||
		len(requests) != 3 ||
		len(result.Steps) != 3 ||
		result.Steps[0].Tool != "echo" ||
		result.Steps[1].Tool != "echo" {
		t.Fatalf("result=%+v requests=%d", result, len(requests))
	}
	second := requests[1].Prompt
	for _, fragment := range []string{
		"System: You are a read-only repository agent.",
		"User: Use echo.",
		`"result":{"value":"first"}`,
		`"tool":"echo"}</tool_result>`,
		"Available tools:",
		"If the evidence is sufficient, answer now.",
	} {
		if !strings.Contains(second, fragment) {
			t.Fatalf("second prompt does not contain %q:\n%s", fragment, second)
		}
	}
	third := requests[2].Prompt
	for _, fragment := range []string{
		"System: You are the final repository answer stage.",
		`"result":{"value":"first"}`,
		`"result":{"value":"second"}`,
		"Assistant: <answer>",
	} {
		if !strings.Contains(third, fragment) {
			t.Fatalf("third prompt does not contain %q:\n%s", fragment, third)
		}
	}
	for index, request := range requests[:2] {
		if !strings.Contains(strings.Join(request.Stops, "\x00"), "</tool_call>") ||
			strings.Contains(strings.Join(request.Stops, "\x00"), "</answer>") {
			t.Fatalf("request %d stops = %q", index+1, request.Stops)
		}
	}
	if !strings.Contains(strings.Join(requests[2].Stops, "\x00"), "</answer>") ||
		strings.Contains(strings.Join(requests[2].Stops, "\x00"), "</tool_call>") {
		t.Fatalf("answer stops = %q", requests[2].Stops)
	}
	if requests[0].MaxOutputTokens != 256 ||
		requests[1].MaxOutputTokens != 1024 ||
		requests[2].MaxOutputTokens != 1024 {
		t.Fatalf(
			"stage token limits = decision:%d post-tool:%d final:%d",
			requests[0].MaxOutputTokens,
			requests[1].MaxOutputTokens,
			requests[2].MaxOutputTokens,
		)
	}
	if result.Steps[0].Stage != StageDecision ||
		result.Steps[1].Stage != StageDecision ||
		result.Steps[2].Stage != StageAnswer {
		t.Fatalf("step stages = %+v", result.Steps)
	}
	history := runner.History()
	if len(history) != 6 ||
		history[0].Role != RoleUser ||
		history[1].Role != RoleAssistant ||
		history[2].Role != RoleTool ||
		history[3].Role != RoleAssistant ||
		history[4].Role != RoleTool ||
		history[5].Role != RoleAssistant {
		t.Fatalf("multi-tool history = %+v", history)
	}
}

func TestRunnerDuplicateCallForcesAnswerFromSuccessfulEvidence(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`<tool_call>{"name":"echo","arguments":{"value":"same"}}</tool_call>`,
		`<tool_call>{"name":"echo","arguments":{"value":"same"}}</tool_call>`,
		"done",
	}
	generations := 0
	var requests []continuation.Request
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			requests = append(requests, request)
			result := continuation.Result{
				Text:         outputs[generations],
				FinishReason: continuation.FinishStop,
			}
			generations++
			return result, nil
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use echo once.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" ||
		result.ForcedAnswerReason != forcedAnswerDuplicateCall ||
		result.Steps[0].ToolExecuted != true ||
		result.Steps[1].ToolExecuted ||
		result.Steps[1].ToolRejected != rejectedDuplicateCall ||
		result.Steps[1].ToolError != "duplicate tool call rejected" {
		t.Fatalf("duplicate call result = %+v", result)
	}
	if len(requests) != 3 ||
		result.Steps[2].Stage != StageAnswer ||
		!strings.Contains(requests[2].Prompt, "Tools are unavailable") ||
		!strings.Contains(requests[2].Prompt, `"result":{"value":"same"}`) ||
		!strings.Contains(requests[2].Prompt, "repeats a successful call") ||
		!strings.Contains(requests[2].Prompt, "Assistant: <answer>") {
		t.Fatalf("forced answer requests=%+v result=%+v", requests, result)
	}
	history := runner.History()
	if len(history) != 6 ||
		history[1].Role != RoleAssistant ||
		history[2].Role != RoleTool ||
		history[3].Role != RoleAssistant ||
		history[4].Role != RoleTool ||
		history[5].Content != "done" {
		t.Fatalf("duplicate-call history = %+v", history)
	}
}

func TestRunnerDuplicateFailedCallForcesLimitedAnswer(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`<tool_call>{"name":"failing","arguments":{"value":"same"}}</tool_call>`,
		`<tool_call>{"name":"failing","arguments":{"value":"same"}}</tool_call>`,
		"could not verify",
	}
	generations := 0
	executions := 0
	var requests []continuation.Request
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			requests = append(requests, request)
			result := continuation.Result{
				Text:         outputs[generations],
				FinishReason: continuation.FinishStop,
			}
			generations++
			return result, nil
		}),
		[]Tool{&failingTool{calls: &executions}},
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use the failing tool.")
	if err != nil {
		t.Fatal(err)
	}
	if executions != 1 ||
		result.Output != "could not verify" ||
		result.ForcedAnswerReason != forcedAnswerDuplicateCall ||
		result.Steps[0].ToolError != "planned failure" ||
		result.Steps[1].ToolExecuted ||
		result.Steps[1].ToolRejected != rejectedDuplicateCall ||
		result.Steps[2].Stage != StageAnswer {
		t.Fatalf("duplicate failed-call result=%+v executions=%d", result, executions)
	}
	if len(requests) != 3 ||
		!strings.Contains(requests[2].Prompt, "repeats an earlier failed call") ||
		!strings.Contains(requests[2].Prompt, "clearly state anything that could not be verified") {
		t.Fatalf("duplicate failed-call requests = %+v", requests)
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

func TestToolContinuationRetainsEarlierTurns(t *testing.T) {
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

func TestRunnerRejectsForcedAnswerWithoutWorkspaceEvidence(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"missing","arguments":{"value":"again"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
	}
	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := outputs[calls]
			calls++
			return result, nil
		}),
		nil,
		Options{MaxSteps: 2},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Loop.")
	if !errors.Is(err, ErrNoWorkspaceEvidence) {
		t.Fatalf("error = %v, want ErrNoWorkspaceEvidence", err)
	}
	if calls != 1 || result.Output != "" || len(result.Steps) != 1 {
		t.Fatalf("ungrounded result = %+v calls=%d", result, calls)
	}
	if result.Steps[0].ToolError != `unknown tool "missing"` {
		t.Fatalf("failed step = %+v", result.Steps[0])
	}
	if history := runner.History(); len(history) != 0 {
		t.Fatalf("ungrounded turn committed history = %+v", history)
	}
}

func TestRunnerRepairsWorkspaceToolArgumentsBeforeReadingEvidence(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("# Example\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"read_file","arguments":{"path":"README.md","max_limit":64}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"read_file","arguments":{"path":"README.md","max_bytes":64}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "# Example", FinishReason: continuation.FinishStop},
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
		tools,
		Options{MaxSteps: 5},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Read README.md.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "# Example" || len(result.Steps) != 4 {
		t.Fatalf("result = %+v", result)
	}
	if !result.Steps[0].ToolExecuted || result.Steps[0].ToolEvidence ||
		!result.Steps[1].ToolExecuted || result.Steps[1].ToolEvidence ||
		!result.Steps[2].ToolExecuted || !result.Steps[2].ToolEvidence {
		t.Fatalf("evidence trace = %+v", result.Steps)
	}
	for _, index := range []int{1, 2} {
		prompt := requests[index].Prompt
		if !strings.Contains(prompt, `exact argument shape: {"path":"relative file path"}`) ||
			!strings.Contains(prompt, "Do not add optional limit, byte, offset, or pagination fields") {
			t.Fatalf("repair prompt %d = %q", index, prompt)
		}
	}
}

func TestRunnerRollsBackRepeatedInvalidArgumentsWithoutGuessing(t *testing.T) {
	t.Parallel()
	tools, err := WorkspaceTools(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	invalid := `<tool_call>{"name":"read_file","arguments":{"path":"README.md","max_bytes":64}}</tool_call>`
	outputs := []continuation.Result{
		{Text: invalid, FinishReason: continuation.FinishStop},
		{Text: invalid, FinishReason: continuation.FinishStop},
	}
	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := outputs[calls]
			calls++
			return result, nil
		}),
		tools,
		Options{MaxSteps: 4},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Read README.md.")
	if !errors.Is(err, ErrNoWorkspaceEvidence) {
		t.Fatalf("error = %v, want ErrNoWorkspaceEvidence", err)
	}
	if calls != 2 || result.Output != "" || len(result.Steps) != 2 ||
		result.ForcedAnswerReason != forcedAnswerDuplicateCall ||
		result.Steps[0].ToolEvidence ||
		result.Steps[1].ToolRejected != rejectedDuplicateCall {
		t.Fatalf("result=%+v calls=%d", result, calls)
	}
	if history := runner.History(); len(history) != 0 {
		t.Fatalf("invalid-argument turn contaminated history: %+v", history)
	}
}

func TestRunnerDoesNotRouteFromRolledBackUngroundedTurn(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "README.md"), []byte("# Example\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	invalid := `{"name":"read_file","arguments":{"path":"README.md","max_bytes":64}}`
	outputs := []continuation.Result{
		{Text: "inspect", FinishReason: continuation.FinishStop},
		{Text: invalid, FinishReason: continuation.FinishStop},
		{Text: `<tool_call>` + invalid + `</tool_call>`, FinishReason: continuation.FinishStop},
		{Text: "inspect", FinishReason: continuation.FinishStop},
		{Text: `{"name":"read_file","arguments":{"path":"README.md"}}`, FinishReason: continuation.FinishStop},
		{Text: "# Example", FinishReason: continuation.FinishStop},
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
		tools,
		Options{
			MaxSteps:             4,
			Router:               G1IRouteProtocol{},
			RouteMaxOutputTokens: 16,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, runErr := runner.Run(
		context.Background(),
		"Read README.md for the unique GROUNDING-TURN-ONE request.",
	); !errors.Is(runErr, ErrNoWorkspaceEvidence) {
		t.Fatalf("first error = %v, want ErrNoWorkspaceEvidence", runErr)
	}
	result, err := runner.Run(context.Background(), "Read README.md correctly now.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "# Example" || len(requests) != len(outputs) {
		t.Fatalf("second result=%+v requests=%d", result, len(requests))
	}
	secondRoutePrompt := requests[3].Prompt
	if strings.Contains(secondRoutePrompt, "GROUNDING-TURN-ONE") ||
		strings.Contains(secondRoutePrompt, "max_bytes") {
		t.Fatalf("rolled-back turn leaked into next route prompt: %q", secondRoutePrompt)
	}
}

func TestRunnerPrefillsFirstInspectToolCall(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{Text: "inspect", FinishReason: continuation.FinishStop},
		{
			Text:         `{"name":"echo","arguments":{"value":"prefilled"}}`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "done", FinishReason: continuation.FinishStop},
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
			MaxSteps: 3,
			Router:   G1IRouteProtocol{},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use echo.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Route != RouteInspect ||
		result.Output != "done" ||
		len(result.Steps) != 2 ||
		result.Steps[0].Tool != "echo" {
		t.Fatalf("prefilled inspect result = %+v", result)
	}
	if len(requests) != 3 ||
		!strings.HasSuffix(requests[1].Prompt, "Assistant: <tool_call>") ||
		!strings.HasSuffix(requests[2].Prompt, "Assistant:") ||
		strings.HasSuffix(requests[2].Prompt, "Assistant: <tool_call>") {
		t.Fatalf("inspect prompts = %+v", requests)
	}
	if history := runner.History(); len(history) != 4 ||
		history[1].Content !=
			`<tool_call>{"name":"echo","arguments":{"value":"prefilled"}}</tool_call>` {
		t.Fatalf("prefilled tool history = %+v", history)
	}
}

func TestRunnerBlocksThirdConsecutiveFailureAndRecoversWithDifferentTool(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"failing","arguments":{"value":"one"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"failing","arguments":{"value":"two"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"failing","arguments":{"value":"three"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"recovered"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "recovered", FinishReason: continuation.FinishStop},
	}
	generations := 0
	executions := 0
	var requests []continuation.Request
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			requests = append(requests, request)
			result := outputs[generations]
			generations++
			return result, nil
		}),
		[]Tool{&failingTool{calls: &executions}, echoTool{}},
		Options{MaxSteps: 5},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Recover.")
	if err != nil {
		t.Fatal(err)
	}
	if executions != maxConsecutiveToolFailures ||
		result.Output != "recovered" ||
		result.ForcedAnswerReason != forcedAnswerStepBudget ||
		len(result.Steps) != 5 ||
		result.Steps[0].ToolExecuted != true ||
		result.Steps[1].ToolExecuted != true ||
		result.Steps[2].ToolExecuted ||
		result.Steps[2].ToolRejected != rejectedFailureLimit ||
		!strings.Contains(result.Steps[2].ToolError, "blocked after 2 consecutive failures") ||
		result.Steps[3].ToolError != "" ||
		result.Steps[4].Stage != StageAnswer {
		t.Fatalf("recovery result=%+v executions=%d", result, executions)
	}
	if !strings.Contains(requests[3].Prompt, "Do not call the same tool again") {
		t.Fatalf("recovery prompt = %q", requests[3].Prompt)
	}
}

func TestRunnerSuggestsDiscoveryAfterMissingReadPath(t *testing.T) {
	t.Parallel()
	tools, err := WorkspaceTools(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"read_file","arguments":{"path":"missing.txt"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "The file was not found.", FinishReason: continuation.FinishStop},
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
		tools,
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Read missing.txt.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != outputs[1].Text ||
		len(prompts) != 2 ||
		!strings.Contains(
			prompts[1],
			"use list_files or search_text before another read_file call",
		) {
		t.Fatalf("missing-path recovery result=%+v prompts=%+v", result, prompts)
	}
}

func TestRunnerRollsBackMultiToolTurnWhenForcedAnswerFails(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"first"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"echo","arguments":{"value":"second"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         "truncated final answer",
			FinishReason: continuation.FinishLength,
		},
	}
	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := outputs[calls]
			calls++
			return result, nil
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use both values.")
	if !errors.Is(err, ErrProtocol) {
		t.Fatalf("error = %v, want ErrProtocol", err)
	}
	if len(result.Steps) != 3 ||
		result.Steps[2].Stage != StageAnswer ||
		result.Steps[2].ProtocolError == "" {
		t.Fatalf("failed multi-tool result = %+v", result)
	}
	if len(runner.History()) != 0 {
		t.Fatalf("failed multi-tool turn committed history = %+v", runner.History())
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

type failingTool struct {
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

func (t *failingTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "failing",
		Description: "Always fail.",
		Arguments:   `{"value":"string"}`,
	}
}

func (t *failingTool) Execute(_ context.Context, _ json.RawMessage) (any, error) {
	*t.calls++
	return nil, fmt.Errorf("planned failure")
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
