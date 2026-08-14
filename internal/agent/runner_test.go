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
	"github.com/no22/RWKV-Agent/internal/inference"
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
		"System: You are a local-first assistant with read-only tools.",
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

func TestRunnerProgressivelyExposesOnlySelectedBundle(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`inspect:workspace</route>`,
		`<tool_call>{"name":"workspace_echo","arguments":{"value":"hello"}}</tool_call>`,
		`done`,
	}
	var prompts []string
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		prompts = append(prompts, request.Prompt)
		output := outputs[len(prompts)-1]
		return continuation.Result{Text: output, FinishReason: continuation.FinishStop}, nil
	})
	runner, err := NewRunner(generator, []Tool{
		bundledEchoTool{name: "workspace_echo", bundle: ToolBundleWorkspace},
		bundledEchoTool{name: "compute_echo", bundle: ToolBundleCompute},
	}, Options{
		MaxSteps:             4,
		ToolRouter:           G1IProgressiveToolRouteProtocol{},
		ToolBundles:          DefaultToolBundles(),
		RouteRenderer:        RWKVChatRenderer{},
		RouteMaxOutputTokens: 48,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use the workspace echo.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || len(result.Bundles) != 1 || result.Bundles[0] != ToolBundleWorkspace {
		t.Fatalf("result = %+v", result)
	}
	decisionPrompt := prompts[1]
	if !strings.Contains(decisionPrompt, "workspace_echo") ||
		!strings.Contains(decisionPrompt, "load_tools") ||
		strings.Contains(decisionPrompt, "compute_echo") {
		t.Fatalf("progressive decision prompt = %q", decisionPrompt)
	}
}

func TestRunnerLoadToolsExpandsActiveView(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`inspect:workspace</route>`,
		`<tool_call>{"name":"load_tools","arguments":{"bundle":"compute"}}</tool_call>`,
		`<tool_call>{"name":"compute_echo","arguments":{"value":"42"}}</tool_call>`,
		`done`,
	}
	var calls int
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		_ continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		output := outputs[calls]
		calls++
		return continuation.Result{Text: output, FinishReason: continuation.FinishStop}, nil
	})
	runner, err := NewRunner(generator, []Tool{
		bundledEchoTool{name: "workspace_echo", bundle: ToolBundleWorkspace},
		bundledEchoTool{name: "compute_echo", bundle: ToolBundleCompute},
	}, Options{
		MaxSteps:             5,
		ToolRouter:           G1IProgressiveToolRouteProtocol{},
		ToolBundles:          DefaultToolBundles(),
		RouteRenderer:        RWKVChatRenderer{},
		RouteMaxOutputTokens: 48,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Load compute, then use it.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || len(result.Bundles) != 2 ||
		result.Steps[0].ToolEvidence || result.Steps[1].Tool != "compute_echo" {
		t.Fatalf("result = %+v", result)
	}
}

func TestRunnerExplainsHowToActivateHiddenKnownTool(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`inspect:workspace</route>`,
		`<tool_call>{"name":"compute_echo","arguments":{"value":"42"}}</tool_call>`,
		`<tool_call>{"name":"load_tools","arguments":{"bundle":"compute"}}</tool_call>`,
		`<tool_call>{"name":"compute_echo","arguments":{"value":"42"}}</tool_call>`,
		`done`,
	}
	var prompts []string
	runner, err := NewRunner(continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		prompts = append(prompts, request.Prompt)
		return continuation.Result{Text: outputs[len(prompts)-1], FinishReason: continuation.FinishStop}, nil
	}), []Tool{
		bundledEchoTool{name: "workspace_echo", bundle: ToolBundleWorkspace},
		bundledEchoTool{name: "compute_echo", bundle: ToolBundleCompute},
	}, Options{
		MaxSteps:             5,
		ToolRouter:           G1IProgressiveToolRouteProtocol{},
		ToolBundles:          DefaultToolBundles(),
		RouteRenderer:        RWKVChatRenderer{},
		RouteMaxOutputTokens: 48,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use compute.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || result.Steps[0].ToolExecuted ||
		!strings.Contains(result.Steps[0].ToolError, `load_tools with {"bundle":"compute"}`) ||
		result.Steps[2].Tool != "compute_echo" || !result.Steps[2].ToolExecuted {
		t.Fatalf("hidden tool recovery = %+v", result)
	}
}

// TestRunnerRecoversFromRunawayReasoning reproduces the 13B failure mode seen in
// runs/cmp-rwkv13b-think-boundary: reasoning loops until the output budget is
// gone, so the response is an unclosed <think> block with no action. The retry
// must not carry that reasoning back into the prompt, and it must be told to
// close the block, otherwise it loops the same way and the turn is lost.
// TestRunnerWithoutRouterStillAnswersAndCallsTools covers --route-stage=false.
// The route stage exists to steer small models, but it costs a model call per
// turn and both RWKV 13B and DeepSeek v4-flash route at 100%, so larger models
// can skip it. With no router the route defaults to inspect; a turn that never
// attempts a tool must still be allowed to answer, and tool use must still work.
func TestRunnerWithoutRouterStillAnswersAndCallsTools(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		name       string
		outputs    []string
		task       string
		wantOutput string
		wantSteps  int
	}{
		{
			name:       "direct answer needs no tool evidence",
			outputs:    []string{"你好！有什么可以帮你的？"},
			task:       "你好",
			wantOutput: "你好！有什么可以帮你的？",
			wantSteps:  1,
		},
		{
			name: "tool use still works",
			outputs: []string{
				`<tool_call>{"name":"echo","arguments":{"value":"hi"}}</tool_call>`,
				"The tool returned hi.",
			},
			task:       "Use echo.",
			wantOutput: "The tool returned hi.",
			wantSteps:  2,
		},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			calls := 0
			runner, err := NewRunner(
				continuation.GenerateFunc(func(
					_ context.Context,
					_ continuation.Request,
					_ continuation.EventSink,
				) (continuation.Result, error) {
					calls++
					return continuation.Result{
						Text:         testCase.outputs[calls-1],
						FinishReason: continuation.FinishStop,
					}, nil
				}),
				[]Tool{echoTool{}},
				// No Router: the route stage is disabled.
				Options{MaxSteps: 3},
			)
			if err != nil {
				t.Fatal(err)
			}
			result, err := runner.Run(context.Background(), testCase.task)
			if err != nil {
				t.Fatal(err)
			}
			if result.Output != testCase.wantOutput {
				t.Fatalf("output = %q, want %q", result.Output, testCase.wantOutput)
			}
			if len(result.Steps) != testCase.wantSteps {
				t.Fatalf("steps = %d, want %d", len(result.Steps), testCase.wantSteps)
			}
			if len(result.RouteSteps) != 0 {
				t.Fatalf("route steps = %d, want none", len(result.RouteSteps))
			}
		})
	}
}

func TestRunnerRecoversFromRunawayReasoning(t *testing.T) {
	t.Parallel()
	runaway := "<think>" + strings.Repeat("wait, let me re-read the task. ", 300)
	var prompts []string
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		prompts = append(prompts, request.Prompt)
		if len(prompts) == 1 {
			// No finish_reason from the server, exactly like the deployment.
			return continuation.Result{
				Text:         runaway,
				FinishReason: continuation.FinishUnknown,
			}, nil
		}
		return continuation.Result{
			Text:         "EMBER-7",
			FinishReason: continuation.FinishStop,
		}, nil
	})
	runner, err := NewRunner(generator, nil, Options{
		MaxSteps:        4,
		ProtocolRetries: 2,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Report the project code.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "EMBER-7" {
		t.Fatalf("output = %q, want the recovered answer", result.Output)
	}
	if len(prompts) != 2 {
		t.Fatalf("continuation calls = %d, want a single retry", len(prompts))
	}
	retry := prompts[1]
	if strings.Contains(retry, "wait, let me re-read the task") {
		t.Fatal("retry prompt carried the runaway reasoning back into context")
	}
	if !strings.Contains(retry, "</think>") {
		t.Fatalf("retry prompt lacks the closing-tag instruction:\n%s", retry)
	}
	if !errors.Is(errFromStep(result.Steps, 0), ErrUnclosedThink) {
		t.Fatalf("first step error = %q, want an unclosed think classification",
			result.Steps[0].ProtocolError)
	}
}

// errFromStep re-derives a sentinel from a recorded step so the assertion above
// reads against the classification rather than a message substring.
func errFromStep(steps []Step, index int) error {
	if index >= len(steps) {
		return nil
	}
	if strings.Contains(steps[index].ProtocolError, "incomplete leading think block") {
		return ErrUnclosedThink
	}
	return errors.New(steps[index].ProtocolError)
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

func TestRunnerRendersThinkingModeAwareControlAndExactBoundary(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name        string
		mode        inference.ThinkingMode
		response    string
		wantControl string
		wantSuffix  string
	}{
		{
			name:        "off",
			mode:        inference.ThinkingOff,
			response:    ">done",
			wantControl: "Do not emit <think>",
			wantSuffix:  "Assistant:",
		},
		{
			name:        "fast",
			mode:        inference.ThinkingFast,
			response:    ">done",
			wantControl: "Output exactly one action.",
			wantSuffix:  "Assistant: <think></think",
		},
		{
			name:        "full",
			mode:        inference.ThinkingFull,
			response:    ">plan</think>done",
			wantControl: "Close your thinking with </think>",
			wantSuffix:  "Assistant: <think",
		},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			for _, controlPrompt := range []ControlPromptMode{
				ControlPromptSystem,
				ControlPromptInline,
			} {
				var prompt string
				runner, err := NewRunner(
					continuation.GenerateFunc(func(
						_ context.Context,
						request continuation.Request,
						_ continuation.EventSink,
					) (continuation.Result, error) {
						prompt = request.Prompt
						return continuation.Result{
							Text:         test.response,
							FinishReason: continuation.FinishStop,
						}, nil
					}),
					nil,
					Options{
						ControlPrompt: controlPrompt,
						Renderer:      RWKVChatRenderer{ThinkingMode: test.mode},
					},
				)
				if err != nil {
					t.Fatal(err)
				}
				if _, err := runner.Run(context.Background(), "task"); err != nil {
					t.Fatal(err)
				}
				if !strings.Contains(prompt, test.wantControl) ||
					!strings.HasSuffix(prompt, test.wantSuffix) {
					t.Fatalf("control=%s prompt=%q", controlPrompt, prompt)
				}
			}
		})
	}
}

func TestDirectResponseControlUsesThinkingModeBoundary(t *testing.T) {
	t.Parallel()
	fast := directResponseControl(inference.ThinkingFast)
	full := directResponseControl(inference.ThinkingFull)
	if !strings.Contains(fast, "Answer directly.") ||
		strings.Contains(fast, "Close your thinking") {
		t.Fatalf("fast control = %q", fast)
	}
	if !strings.Contains(full, "Close your thinking with </think>") ||
		!strings.Contains(full, "answer directly") {
		t.Fatalf("full control = %q", full)
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
		"System: You are a local-first assistant with read-only tools.",
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
		"System: You are the final local-assistant answer stage.",
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

func TestValidateAnswerRejectsProtocolTag(t *testing.T) {
	t.Parallel()
	assertAnswerViolation(t, "Use <tool_call> only internally.", violationProtocolTag)
}

func TestValidateAnswerRejectsRoleHeader(t *testing.T) {
	t.Parallel()
	assertAnswerViolation(t, "Assistant: The answer is 42.", violationRoleHeader)
}

func TestValidateAnswerRejectsJSONPayload(t *testing.T) {
	t.Parallel()
	assertAnswerViolation(t, `{"answer":42}`, violationJSONPayload)
}

func TestValidateAnswerRejectsToolEcho(t *testing.T) {
	t.Parallel()
	assertAnswerViolation(
		t,
		`Raw payload: {"ok":true,"tool":"weather","result":{"temp_c":27}}`,
		violationToolEcho,
	)
}

func TestRunnerRepairsAnswerContractBeforeCommit(t *testing.T) {
	t.Parallel()
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			return continuation.Result{Text: "Assistant: leaked answer"}, nil
		}),
		nil,
		Options{},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "answer")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != answerContractFallbackEN ||
		result.OriginalOutput != "Assistant: leaked answer" ||
		!result.AnswerContractRepaired ||
		len(result.AnswerViolations) != 1 ||
		result.AnswerViolations[0] != string(violationRoleHeader) {
		t.Fatalf("repair result = %+v", result)
	}
	history := runner.History()
	if len(history) != 2 || history[1].Content != answerContractFallbackEN {
		t.Fatalf("committed history = %+v", history)
	}
	if answerContractFallback("请回答") != answerContractFallbackZH {
		t.Fatal("Chinese task did not receive the Chinese contract fallback")
	}
}

func assertAnswerViolation(t *testing.T, output string, expected answerViolation) {
	t.Helper()
	violations := validateAnswer(output)
	if len(violations) != 1 || violations[0] != expected {
		t.Fatalf("validateAnswer(%q) = %v, want [%s]", output, violations, expected)
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

func TestRunnerRejectsToolCallDuringAnswerStage(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`<tool_call>{"name":"counting_echo","arguments":{"value":"same"}}</tool_call>`,
		`<tool_call>{"name":"counting_echo","arguments":{"value":"same"}}</tool_call>`,
		`<tool_call>{"name":"counting_echo","arguments":{"value":"must-not-run"}}</tool_call>`,
		"final from existing evidence",
	}
	generations := 0
	executions := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := continuation.Result{Text: outputs[generations], FinishReason: continuation.FinishStop}
			generations++
			return result, nil
		}),
		[]Tool{&countingEchoTool{calls: &executions}},
		Options{MaxSteps: 4, ProtocolRetries: 1},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Use echo once, then answer.")
	if err != nil {
		t.Fatal(err)
	}
	if executions != 1 || result.Output != "final from existing evidence" || len(result.Steps) != 4 {
		t.Fatalf("answer-stage guard result = %+v, executions = %d", result, executions)
	}
	violation := result.Steps[2]
	if violation.Stage != StageAnswer || violation.ActionType != "tool" ||
		!violation.StageViolation || !strings.Contains(violation.ProtocolError, ErrStageViolation.Error()) {
		t.Fatalf("answer-stage violation = %+v", violation)
	}
}

func TestRunnerAllowsRepeatedReadAfterWorkspaceMutation(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`<tool_call>{"name":"counting_echo","arguments":{"value":"same"}}</tool_call>`,
		`<tool_call>{"name":"mutation","arguments":{}}</tool_call>`,
		`<tool_call>{"name":"counting_echo","arguments":{"value":"same"}}</tool_call>`,
		"done",
	}
	index := 0
	reads := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := continuation.Result{Text: outputs[index], FinishReason: continuation.FinishStop}
			index++
			return result, nil
		}),
		[]Tool{&countingEchoTool{calls: &reads}, mutationTool{}},
		Options{MaxSteps: 4},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Read, mutate, then read again.")
	if err != nil {
		t.Fatal(err)
	}
	if reads != 2 || result.Output != "done" || !result.Steps[2].ToolExecuted {
		t.Fatalf("revision-aware result = %+v, reads = %d", result, reads)
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

func TestRunnerAllowsFailedCallAfterSuccessfulRecoveryAction(t *testing.T) {
	t.Parallel()
	outputs := []string{
		`<tool_call>{"name":"failing","arguments":{"value":"same"}}</tool_call>`,
		`<tool_call>{"name":"echo","arguments":{"value":"recovered"}}</tool_call>`,
		`<tool_call>{"name":"failing","arguments":{"value":"same"}}</tool_call>`,
		"could not verify",
	}
	calls := 0
	executions := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := continuation.Result{Text: outputs[calls], FinishReason: continuation.FinishStop}
			calls++
			return result, nil
		}),
		[]Tool{&failingTool{calls: &executions}, echoTool{}},
		Options{MaxSteps: 5},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Recover, then retry.")
	if err != nil {
		t.Fatal(err)
	}
	if executions != 2 || result.Output != "could not verify" || result.Steps[2].ToolRejected != "" {
		t.Fatalf("recovery retry result=%+v executions=%d", result, executions)
	}
}

func TestRunnerRequiresTerminalToolBeforeFinal(t *testing.T) {
	t.Parallel()
	outputs := []string{
		"premature answer",
		`<tool_call>{"name":"echo","arguments":{"value":"submitted"}}</tool_call>`,
		"submitted",
	}
	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			context.Context,
			continuation.Request,
			continuation.EventSink,
		) (continuation.Result, error) {
			result := continuation.Result{Text: outputs[calls], FinishReason: continuation.FinishStop}
			calls++
			return result, nil
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 4, TerminalTool: "echo", TaskControl: "Call echo before final."},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Submit this answer.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "submitted" || len(result.Steps) != 3 ||
		!strings.Contains(result.Steps[0].ProtocolError, "successful echo call required") ||
		result.Steps[1].Tool != "echo" {
		t.Fatalf("terminal-tool result = %+v", result)
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

// A turn whose every tool call was rejected for a malformed path observed no
// workspace state. It must roll back instead of letting the model answer from
// nothing, which is how an unsupported value reached a committed answer before.
func TestRunnerRecordsPromptTraceForEveryGeneration(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	if err := os.WriteFile(
		filepath.Join(root, "answer.txt"), []byte("BLUEBIRD\n"), 0o644,
	); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	outputs := []continuation.Result{
		{Text: "<route>inspect</route>", FinishReason: continuation.FinishStop},
		{
			Text:         `<tool_call>{"name":"read_file","arguments":{"path":"answer.txt"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "BLUEBIRD", FinishReason: continuation.FinishStop},
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
		Options{
			MaxSteps:         3,
			Router:           G1IRouteProtocol{},
			RouteRenderer:    RWKVChatRenderer{},
			RouteRetries:     1,
			TracePromptBytes: DefaultTracePromptBytes,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Read answer.txt.")
	if err != nil {
		t.Fatal(err)
	}
	if len(result.RouteSteps) != 1 {
		t.Fatalf("route steps = %+v, want 1", result.RouteSteps)
	}
	route := result.RouteSteps[0]
	if route.Request == nil || route.Request.Prompt == "" ||
		route.Request.Bytes != len(route.Request.Prompt) ||
		route.Route != RouteInspect {
		t.Fatalf("route trace = %+v", route)
	}
	for _, step := range result.Steps {
		if step.Request == nil || step.Request.Prompt == "" {
			t.Fatalf("step %d has no prompt trace: %+v", step.Number, step)
		}
		if step.Request.Bytes != len(step.Request.Prompt) {
			t.Fatalf("step %d byte count disagrees with prompt", step.Number)
		}
	}
	// The tool list must be recorded on decision steps: changing it changes
	// every decision prompt, which under greedy decoding moves other cases.
	decision := result.Steps[0]
	if len(decision.Request.ToolsOffered) != 3 {
		t.Fatalf("tools offered = %v, want 3 workspace tools", decision.Request.ToolsOffered)
	}
	if decision.Request.MaxOutputTokens == 0 && decision.Request.Stops == nil {
		t.Fatalf("decision trace lost sampling context: %+v", decision.Request)
	}
}

func TestRunnerPromptTraceRespectsBudget(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		name      string
		budget    int
		wantNil   bool
		truncated bool
	}{
		{"disabled", 0, true, false},
		{"tiny budget truncates", 64, false, true},
		{"unlimited", -1, false, false},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			runner, err := NewRunner(
				continuation.GenerateFunc(func(
					context.Context,
					continuation.Request,
					continuation.EventSink,
				) (continuation.Result, error) {
					return continuation.Result{
						Text:         "done",
						FinishReason: continuation.FinishStop,
					}, nil
				}),
				nil,
				Options{MaxSteps: 2, TracePromptBytes: testCase.budget},
			)
			if err != nil {
				t.Fatal(err)
			}
			result, err := runner.Run(context.Background(), strings.Repeat("task ", 200))
			if err != nil {
				t.Fatal(err)
			}
			trace := result.Steps[0].Request
			if testCase.wantNil {
				if trace != nil {
					t.Fatalf("budget 0 still recorded a prompt: %+v", trace)
				}
				return
			}
			if trace == nil {
				t.Fatal("prompt trace missing")
			}
			if trace.Truncated != testCase.truncated {
				t.Fatalf("truncated = %v, want %v", trace.Truncated, testCase.truncated)
			}
			// Bytes always reports the true pre-truncation size.
			if trace.Bytes < len(trace.Prompt) && !trace.Truncated {
				t.Fatalf("bytes %d < prompt %d without truncation", trace.Bytes, len(trace.Prompt))
			}
			if testCase.truncated && !strings.Contains(trace.Prompt, "trace truncated") {
				t.Fatalf("truncated prompt lacks marker: %q", trace.Prompt)
			}
		})
	}
}

func TestRunnerRollsBackWhenOnlyMalformedPathsWereTried(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	if err := os.WriteFile(
		filepath.Join(root, "notes.md"), []byte("--enable-v2-auth\n"), 0o644,
	); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	outputs := []continuation.Result{
		{
			Text:         `<tool_call>{"name":"search_text","arguments":{"query":"flag","path":"/nowhere/deep"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{
			Text:         `<tool_call>{"name":"list_files","arguments":{"path":"/nowhere/other"}}</tool_call>`,
			FinishReason: continuation.FinishStop,
		},
		{Text: "The required flag is --migration-flag=2.4.0", FinishReason: continuation.FinishStop},
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
		Options{MaxSteps: 3},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Find the required migration flag.")
	if !errors.Is(err, ErrNoWorkspaceEvidence) {
		t.Fatalf("error = %v, want ErrNoWorkspaceEvidence", err)
	}
	if result.Output != "" {
		t.Fatalf("ungrounded answer was committed: %q", result.Output)
	}
	for index, step := range result.Steps {
		if step.ToolEvidence {
			t.Fatalf("step %d marked a rejected path as evidence: %+v", index, step)
		}
	}
	if history := runner.History(); len(history) != 0 {
		t.Fatalf("rolled-back turn contaminated history: %+v", history)
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

func TestRunnerProviderUnavailableForcesExplicitLimitation(t *testing.T) {
	t.Parallel()
	outputs := []continuation.Result{
		{Text: `<tool_call>{"name":"echo","arguments":{"value":"人民币总额 150 元"}}</tool_call>`, FinishReason: continuation.FinishStop},
		{Text: `<tool_call>{"name":"fx_convert","arguments":{"amount":150,"from":"CNY","to":"USD"}}</tool_call>`, FinishReason: continuation.FinishStop},
		{Text: "人民币总额是 150 元；fx_convert 不可用，因此美元换算未完成。", FinishReason: continuation.FinishStop},
	}
	var prompts []string
	fxExecutions := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompts = append(prompts, request.Prompt)
			return outputs[len(prompts)-1], nil
		}),
		[]Tool{echoTool{}, &providerUnavailableTool{calls: &fxExecutions}},
		Options{MaxSteps: 4},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "把人民币总额换成美元；汇率不可用时不要猜。")
	if err != nil {
		t.Fatal(err)
	}
	if fxExecutions != 1 ||
		len(result.Steps) != 3 ||
		!result.Steps[1].ToolUnavailable ||
		result.Steps[1].ToolRejected != rejectedProviderUnavailable ||
		result.Steps[2].Stage != StageAnswer ||
		!strings.Contains(prompts[2], "- fx_convert") ||
		!strings.Contains(result.Output, "150") ||
		!strings.Contains(result.Output, "未完成") ||
		strings.Contains(result.Output, "21") {
		t.Fatalf("provider fallback result=%+v prompts=%+v executions=%d", result, prompts, fxExecutions)
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

type mutationTool struct{}

type bundledEchoTool struct {
	name   string
	bundle string
}

func (t bundledEchoTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        t.name,
		Description: "Return a value from one capability bundle.",
		Arguments:   `{"value":"string"}`,
		Bundle:      t.bundle,
	}
}

func (bundledEchoTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Value string `json:"value"`
	}
	if err := json.Unmarshal(raw, &args); err != nil {
		return nil, err
	}
	return map[string]string{"value": args.Value}, nil
}

type mutationResult struct{ changed bool }

func (r mutationResult) WorkspaceChanged() bool { return r.changed }

func (mutationTool) Spec() ToolSpec {
	return ToolSpec{
		Name:             "mutation",
		Description:      "Mutate the workspace.",
		Arguments:        `{}`,
		MutatesWorkspace: true,
	}
}

func (mutationTool) Execute(context.Context, json.RawMessage) (any, error) {
	return mutationResult{changed: true}, nil
}

func (echoTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "echo",
		Description: "Return a value.",
		Arguments:   `{"value":"string"}`,
	}
}

type providerUnavailableTool struct{ calls *int }

func (*providerUnavailableTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "fx_convert",
		Description: "Convert currency.",
		Arguments:   `{"amount":"number","from":"string","to":"string"}`,
	}
}

func (t *providerUnavailableTool) Execute(context.Context, json.RawMessage) (any, error) {
	*t.calls++
	return nil, ErrProviderUnavailable
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
