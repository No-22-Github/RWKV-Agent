package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

type submitTestTool struct{}

func (submitTestTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "submit",
		Description: "Submit the final answer.",
		Arguments:   `{"answer":"string"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"answer":{"type":"string"}},"required":["answer"],"additionalProperties":false}`),
		Strict:      true,
	}
}

func (submitTestTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Answer string `json:"answer"`
	}
	if err := json.Unmarshal(raw, &args); err != nil {
		return nil, err
	}
	return args.Answer, nil
}

func TestG1IFunctionProtocolRendersNativeCatalogAndContinuation(t *testing.T) {
	t.Parallel()
	spec := ToolSpec{
		Name:        "read_file",
		Description: "Read one file. Extra sentence is omitted.",
		Arguments:   `{"path":"relative file path"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"path":{"type":"string","description":"Relative path"}},"required":["path"]}`),
	}
	control := (G1IFunctionProtocol{}).Instructions([]ToolSpec{spec}, "")
	for _, fragment := range []string{
		"Tools:\n[",
		`"name":"read_file"`,
		`"arguments":{"path":{"type":"string"}}`,
		"Preserve exact paths and identifier names from Function output.",
		"submit it verbatim, including prefixes and punctuation",
		"Return only a JSON function call.",
	} {
		if !strings.Contains(control, fragment) {
			t.Fatalf("native control omits %q:\n%s", fragment, control)
		}
	}
	renderer := G1IFunctionRenderer{HasSubmit: true}
	prompt, err := renderer.Render([]Message{
		{Role: RoleSystem, Content: control},
		{Role: RoleUser, Content: "Read README.md."},
		{Role: RoleAssistant, Content: "```json\n{\"name\":\"read_file\",\"arguments\":{\"path\":\"README.md\"}}\n```"},
		{Role: RoleTool, Content: "1: # Project"},
	})
	if err != nil {
		t.Fatal(err)
	}
	for _, fragment := range []string{
		"System: Tools:\n",
		"User: Read README.md.",
		"User: Function output:\n1: # Project",
		"Assistant: ```json\n",
	} {
		if !strings.Contains(prompt, fragment) {
			t.Fatalf("native prompt omits %q:\n%s", fragment, prompt)
		}
	}
	if strings.Contains(prompt, "<tool_result>") || strings.Contains(prompt, "If the evidence is sufficient") {
		t.Fatalf("native prompt leaked generic transcript framing:\n%s", prompt)
	}
}

func TestG1IFunctionProtocolRepairsRawNewlineAndTruncation(t *testing.T) {
	t.Parallel()
	protocol := G1IFunctionProtocol{}
	action, err := protocol.Parse("```json\n"+`{"name":"write_file","arguments":{"path":"a.txt","content":"one`+"\n"+`two"}}`+"\n```", continuation.FinishStop)
	if err != nil {
		t.Fatal(err)
	}
	if action.Name != "write_file" || !action.ProtocolRepaired || string(action.Arguments) != `{"path":"a.txt","content":"one\ntwo"}` {
		t.Fatalf("repaired action = %+v", action)
	}
	action, err = protocol.Parse(`{"name":"read_file","arguments":{"path":"README.md"`, continuation.FinishLength)
	if err != nil || action.Name != "read_file" || !action.ProtocolRepaired || string(action.Arguments) != `{"path":"README.md"}` {
		t.Fatalf("truncated action = %+v, error = %v", action, err)
	}
	action, err = protocol.Parse(`{"name":"read_file","arguments":"{\"path\":\"README.md\"}"}`, continuation.FinishStop)
	if err != nil || action.Name != "read_file" || !action.ProtocolRepaired || string(action.Arguments) != `{"path":"README.md"}` {
		t.Fatalf("stringified arguments action = %+v, error = %v", action, err)
	}
	action, err = protocol.Parse(`{"name":"search_text","arguments":{"query":"^item\d+$"}}`, continuation.FinishStop)
	if err != nil || !action.ProtocolRepaired || string(action.Arguments) != `{"query":"^itemd+$"}` {
		t.Fatalf("invalid escape action = %+v, error = %v", action, err)
	}
	action, err = protocol.Parse(`{"path":"."}`, continuation.FinishStop)
	if err != nil || action.Name != "list_files" || !action.ProtocolRepaired || string(action.Arguments) != `{"path":"."}` {
		t.Fatalf("nameless action = %+v, error = %v", action, err)
	}
	action, err = protocol.Parse(`{"command":"submit","args":{"answer":"done"}}`, continuation.FinishStop)
	if err != nil || action.Name != "submit" || !action.ProtocolRepaired || string(action.Arguments) != `{"answer":"done"}` {
		t.Fatalf("aliased action = %+v, error = %v", action, err)
	}
	action, err = protocol.Parse(`<think>use multiply</think><tool_calls>[{"type":"function","function":{"name":"multiply","arguments":"{\"a\":4827,\"b\":391}"}}]</tool_calls>`, continuation.FinishStop)
	if err != nil || action.Name != "multiply" || !action.ProtocolRepaired || string(action.Arguments) != `{"a":4827,"b":391}` {
		t.Fatalf("plural wrapper action = %+v, error = %v", action, err)
	}
}

func TestG1IProductFunctionProtocolPreservesMarkdownAnswers(t *testing.T) {
	t.Parallel()
	protocol := G1IFunctionProtocol{Product: true}
	answer := "```go\nfunc main() {}\n```"
	action, err := protocol.Parse(answer, continuation.FinishStop)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != "final" || action.Content != answer {
		t.Fatalf("Markdown answer = %+v", action)
	}
	call, err := protocol.Parse("```json\n"+`{"name":"read_file","arguments":{"path":"README.md"}}`, continuation.FinishStop)
	if err != nil || call.Type != "tool" || call.Name != "read_file" {
		t.Fatalf("prefilled function call = %+v, error = %v", call, err)
	}
}

func TestG1IProductFunctionRunnerPrefillsEveryToolDecision(t *testing.T) {
	t.Parallel()
	responses := []string{
		`inspect</route>`,
		`{"name":"echo","arguments":{"value":"BLUEBIRD"}}`,
		`{"name":"submit","arguments":{"answer":"Result: BLUEBIRD"}}`,
	}
	var requests []continuation.Request
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			requests = append(requests, request)
			return continuation.Result{Text: responses[len(requests)-1], FinishReason: continuation.FinishStop}, nil
		}),
		[]Tool{echoTool{}, ProductSubmitTool()},
		Options{
			MaxSteps:          3,
			Protocol:          G1IFunctionProtocol{Product: true},
			Renderer:          G1IFunctionRenderer{Product: true},
			Router:            G1IRouteProtocol{},
			RouteRenderer:     RWKVChatRenderer{},
			TerminalTool:      "submit",
			EndOnTerminalTool: true,
			Generation:        continuation.Request{MaxOutputTokens: 128},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Echo BLUEBIRD.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "Result: BLUEBIRD" || len(requests) != 3 {
		t.Fatalf("result = %+v, requests = %d", result, len(requests))
	}
	if !strings.HasSuffix(requests[1].Prompt, "Assistant: ```json\n") ||
		!containsString(requests[1].Stops, "```") {
		t.Fatalf("first decision request = %+v", requests[1])
	}
	if !strings.HasSuffix(requests[2].Prompt, "Assistant: ```json\n") || !containsString(requests[2].Stops, "```") ||
		!strings.Contains(requests[2].Prompt, "User: Function output:\n") {
		t.Fatalf("second decision request = %+v", requests[2])
	}
}

func TestG1IFunctionRunnerDoesNotInjectGenericPostToolReminder(t *testing.T) {
	t.Parallel()
	responses := []string{
		`{"name":"echo","arguments":{"value":"one"}}`,
		`{"name":"echo","arguments":{"value":"two"}}`,
	}
	var prompts []string
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompts = append(prompts, request.Prompt)
			return continuation.Result{Text: responses[len(prompts)-1], FinishReason: continuation.FinishStop}, nil
		}),
		[]Tool{echoTool{}},
		Options{
			MaxSteps:          2,
			Protocol:          G1IFunctionProtocol{},
			Renderer:          G1IFunctionRenderer{HasSubmit: true},
			TerminalTool:      "submit",
			EndOnTerminalTool: false,
			Generation:        continuation.Request{MaxOutputTokens: 128},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	_, _ = runner.Run(context.Background(), "Call twice.")
	if len(prompts) != 2 {
		t.Fatalf("prompts = %d", len(prompts))
	}
	if strings.Contains(prompts[1], "Use the Tool results above") ||
		!strings.Contains(prompts[1], "User: Function output:") {
		t.Fatalf("second prompt has generic reminder framing:\n%s", prompts[1])
	}
}

func TestG1IFunctionRunnerExecutesRepeatedCallsWithOfficialNotes(t *testing.T) {
	t.Parallel()
	var prompts []string
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			prompts = append(prompts, request.Prompt)
			return continuation.Result{
				Text:         `{"name":"echo","arguments":{"value":"same"}}`,
				FinishReason: continuation.FinishStop,
			}, nil
		}),
		[]Tool{echoTool{}},
		Options{
			MaxSteps:     3,
			Protocol:     G1IFunctionProtocol{AllowRepeatedCalls: true},
			Renderer:     G1IFunctionRenderer{HasSubmit: true},
			TerminalTool: "submit",
			Generation:   continuation.Request{MaxOutputTokens: 128},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, _ := runner.Run(context.Background(), "Repeat for protocol testing.")
	if len(result.Steps) != 3 || !result.Steps[1].ToolExecuted || result.Steps[1].ToolRejected != "" {
		t.Fatalf("repeated calls were not executed: %+v", result.Steps)
	}
	if len(prompts) != 3 || !strings.Contains(prompts[2], "NOTE: identical tool call repeated") {
		t.Fatalf("official repeat note missing from third prompt: %v", prompts)
	}
}

func TestG1IFunctionRunnerRejectsRepeatedCallsByDefault(t *testing.T) {
	t.Parallel()
	responses := []string{
		`{"name":"echo","arguments":{"value":"same"}}`,
		`{"name":"echo","arguments":{"value":"same"}}`,
		`{"name":"submit","arguments":{"answer":"same"}}`,
	}
	index := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			response := responses[index]
			index++
			return continuation.Result{Text: response, FinishReason: continuation.FinishStop}, nil
		}),
		[]Tool{echoTool{}, submitTestTool{}},
		Options{
			MaxSteps:          3,
			Protocol:          G1IFunctionProtocol{},
			Renderer:          G1IFunctionRenderer{HasSubmit: true},
			TerminalTool:      "submit",
			EndOnTerminalTool: true,
			Generation:        continuation.Request{MaxOutputTokens: 128},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return same.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "same" || result.Steps[1].ToolExecuted ||
		result.Steps[1].ToolRejected != rejectedDuplicateCall {
		t.Fatalf("hardened repeated call result = %+v", result)
	}
}

func TestG1IFunctionRendererAllowsExpectedPlainAnswers(t *testing.T) {
	t.Parallel()
	messages := []Message{
		{Role: RoleSystem, Content: "Tools: []"},
		{Role: RoleUser, Content: "Calculate."},
		{Role: RoleTool, Content: "42"},
	}
	arithmetic, err := (G1IFunctionRenderer{}).Render(messages)
	if err != nil || !strings.HasSuffix(arithmetic, "Assistant:") || strings.HasSuffix(arithmetic, "```json\n") {
		t.Fatalf("arithmetic prompt = %q, error = %v", arithmetic, err)
	}
	invoice, err := (G1IFunctionRenderer{HasRunTests: true}).Render(messages)
	if err != nil || !strings.HasSuffix(invoice, "Assistant: ```json\n") {
		t.Fatalf("pre-PASS invoice prompt = %q, error = %v", invoice, err)
	}
	messages[len(messages)-1].Content = "PASS\ntests passed"
	invoice, err = (G1IFunctionRenderer{HasRunTests: true}).Render(messages)
	if err != nil || !strings.HasSuffix(invoice, "Assistant:") {
		t.Fatalf("post-PASS invoice prompt = %q, error = %v", invoice, err)
	}
}

func TestRunnerEndsOnSuccessfulTerminalTool(t *testing.T) {
	t.Parallel()
	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(context.Context, continuation.Request, continuation.EventSink) (continuation.Result, error) {
			calls++
			return continuation.Result{Text: `{"name":"echo","arguments":{"value":"BLUEBIRD"}}`, FinishReason: continuation.FinishStop}, nil
		}),
		[]Tool{echoTool{}},
		Options{
			MaxSteps:          2,
			Protocol:          G1IFunctionProtocol{},
			Renderer:          G1IFunctionRenderer{HasSubmit: true},
			TerminalTool:      "echo",
			EndOnTerminalTool: true,
			Generation:        continuation.Request{MaxOutputTokens: 128},
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Submit BLUEBIRD.")
	if err != nil {
		t.Fatal(err)
	}
	if calls != 1 || result.Output != `{"value":"BLUEBIRD"}` || len(result.Steps) != 1 {
		t.Fatalf("terminal result = %+v, calls = %d", result, calls)
	}
}

type replayableEchoTool struct {
	calls *int
}

func (t *replayableEchoTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "echo",
		Description: "Return a value.",
		Arguments:   `{"value":"string"}`,
		Replayable:  true,
	}
}

func (t *replayableEchoTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	if t.calls != nil {
		*t.calls++
	}
	var args struct {
		Value string `json:"value"`
	}
	if err := json.Unmarshal(raw, &args); err != nil {
		return nil, err
	}
	return map[string]string{"value": args.Value}, nil
}

func g1iRunnerOptions() Options {
	return Options{
		MaxSteps:          8,
		Protocol:          G1IFunctionProtocol{},
		Renderer:          G1IFunctionRenderer{HasSubmit: true},
		TerminalTool:      "submit",
		EndOnTerminalTool: true,
		Generation:        continuation.Request{MaxOutputTokens: 128},
	}
}

// sequenceGenerator replays scripted responses in order.
func sequenceGenerator(responses []string, prompts *[]string) continuation.Generator {
	index := 0
	return continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		if prompts != nil {
			*prompts = append(*prompts, request.Prompt)
		}
		response := responses[index]
		index++
		return continuation.Result{Text: response, FinishReason: continuation.FinishStop}, nil
	})
}

func TestG1IFunctionRunnerReplaysReplayableDuplicatesThenRejects(t *testing.T) {
	t.Parallel()
	echoCalls := 0
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 2
	options.DuplicateRescueThreshold = 0
	var prompts []string
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"submit","arguments":{"answer":"done"}}`,
		}, &prompts),
		[]Tool{&replayableEchoTool{calls: &echoCalls}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return same.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || len(result.Steps) != 4 {
		t.Fatalf("result = %+v", result)
	}
	if !result.Steps[0].ToolExecuted || result.Steps[0].ToolRejected != "" {
		t.Fatalf("first call was not a normal execution: %+v", result.Steps[0])
	}
	if !result.Steps[1].ToolExecuted || result.Steps[1].ToolRejected != "" ||
		result.Steps[1].ToolError != "" {
		t.Fatalf("first repeat was not replayed: %+v", result.Steps[1])
	}
	if result.Steps[2].ToolExecuted ||
		result.Steps[2].ToolRejected != rejectedDuplicateCall {
		t.Fatalf("second repeat was not rejected: %+v", result.Steps[2])
	}
	if echoCalls != 2 {
		t.Fatalf("echo executions = %d, want 2 (original + one replay)", echoCalls)
	}
	if !strings.Contains(prompts[2], "identical tool call re-executed") {
		t.Fatalf("replay note missing from third prompt:\n%s", prompts[2])
	}
	if !strings.Contains(prompts[3], "STOP repeating") {
		t.Fatalf("escalated rejection text missing from fourth prompt:\n%s", prompts[3])
	}
}

func TestG1IFunctionRunnerDuplicateRejectionEscalates(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 0
	options.DuplicateRescueThreshold = 0
	var prompts []string
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"submit","arguments":{"answer":"done"}}`,
		}, &prompts),
		[]Tool{echoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return same.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" ||
		result.Steps[1].ToolExecuted || result.Steps[1].ToolRejected != rejectedDuplicateCall ||
		result.Steps[2].ToolExecuted || result.Steps[2].ToolRejected != rejectedDuplicateCall {
		t.Fatalf("result = %+v", result)
	}
	if !strings.Contains(prompts[2], "RECOVERY: This exact call is disabled.") {
		t.Fatalf("first rejection must keep the legacy text:\n%s", prompts[2])
	}
	if !strings.Contains(prompts[3], "STOP repeating") ||
		!strings.Contains(prompts[3], "steps left") {
		t.Fatalf("second rejection must escalate:\n%s", prompts[3])
	}
	if legacy := strings.LastIndex(prompts[3], "This exact call is disabled."); legacy < 0 ||
		strings.LastIndex(prompts[3], "STOP repeating") < legacy {
		t.Fatalf("escalation must follow the legacy text in the transcript:\n%s", prompts[3])
	}
}

func TestG1IFunctionRunnerRescueModeSubmitsBestAnswer(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 1
	options.DuplicateRescueThreshold = 2
	var prompts []string
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"submit","arguments":{"answer":"best-effort"}}`,
		}, &prompts),
		[]Tool{&replayableEchoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return same.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "best-effort" || !result.RescueAttempted || !result.RescueSubmitted {
		t.Fatalf("rescue result = %+v", result)
	}
	if !strings.Contains(prompts[2], "Call submit now with your best answer") {
		t.Fatalf("rescue instruction missing from third prompt:\n%s", prompts[2])
	}
	catalog := g1iCatalogText(t, prompts[2])
	if !strings.Contains(catalog, `"name":"submit"`) || strings.Contains(catalog, `"name":"echo"`) {
		t.Fatalf("rescue catalog must offer submit only:\n%s", catalog)
	}
}

func TestG1IFunctionRunnerRescueModeRejectsOtherTools(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 1
	options.DuplicateRescueThreshold = 2
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"submit","arguments":{"answer":"rescued"}}`,
		}, nil),
		[]Tool{&replayableEchoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return same.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "rescued" || !result.RescueAttempted || !result.RescueSubmitted {
		t.Fatalf("rescue result = %+v", result)
	}
	blocked := result.Steps[2]
	if blocked.ToolExecuted || blocked.ToolRejected != rejectedRescueRestricted ||
		!strings.Contains(blocked.ToolError, "only submit is available") {
		t.Fatalf("post-rescue tool call was not restricted: %+v", blocked)
	}
}

func TestG1IFunctionRunnerDuplicateControlsDisabledByZero(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 0
	options.DuplicateRescueThreshold = 0
	var prompts []string
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"submit","arguments":{"answer":"done"}}`,
		}, &prompts),
		[]Tool{&replayableEchoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return same.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || result.RescueAttempted || result.RescueSubmitted {
		t.Fatalf("zero thresholds must preserve strict rejection: %+v", result)
	}
	for index := 1; index <= 2; index++ {
		if result.Steps[index].ToolExecuted || result.Steps[index].ToolRejected != rejectedDuplicateCall {
			t.Fatalf("step %d was not strictly rejected: %+v", index, result.Steps[index])
		}
	}
	for _, prompt := range prompts {
		if strings.Contains(prompt, "Call submit now with your best answer") ||
			strings.Contains(prompt, "identical tool call re-executed") {
			t.Fatalf("disabled controls leaked into prompt:\n%s", prompt)
		}
	}
}

// g1iCatalogText extracts the System: Tools catalog from a rendered G1i prompt.
func g1iCatalogText(t *testing.T, prompt string) string {
	t.Helper()
	const startMarker = "Tools:\n[\n"
	const endMarker = "\n]\n"
	start := strings.Index(prompt, startMarker)
	if start < 0 {
		t.Fatalf("catalog start missing from prompt:\n%s", prompt)
	}
	start += len(startMarker)
	end := strings.Index(prompt[start:], endMarker)
	if end < 0 {
		t.Fatalf("catalog end missing from prompt:\n%s", prompt)
	}
	return prompt[start : start+end]
}

func TestG1IFunctionRunnerAppliesPostToolHookAfterSuccess(t *testing.T) {
	t.Parallel()
	var prompts []string
	hooked := 0
	options := g1iRunnerOptions()
	options.PostToolHook = func(name string, _ json.RawMessage, result any, err error) string {
		if err != nil {
			t.Errorf("hook invoked with error: %v", err)
			return ""
		}
		hooked++
		if name != "echo" {
			return ""
		}
		return "HOOK: remember the value above."
	}
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"one"}}`,
			`{"name":"submit","arguments":{"answer":"one"}}`,
		}, &prompts),
		[]Tool{echoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Return one.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "one" || hooked != 1 {
		t.Fatalf("result = %+v, hook calls = %d", result, hooked)
	}
	if !strings.Contains(prompts[1], "HOOK: remember the value above.") {
		t.Fatalf("hook text missing from the prompt after the tool result:\n%s", prompts[1])
	}
	committed := false
	for _, message := range runner.History() {
		if message.Role == RoleTool && strings.Contains(message.Content, "HOOK: remember the value above.") {
			committed = true
		}
	}
	if !committed {
		t.Fatalf("hook text was not committed to history: %+v", runner.History())
	}
}

func TestG1IFunctionRunnerSkipsPostToolHookOnFailure(t *testing.T) {
	t.Parallel()
	hooked := 0
	options := g1iRunnerOptions()
	options.PostToolHook = func(string, json.RawMessage, any, error) string {
		hooked++
		return "HOOK"
	}
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"failing","arguments":{"value":"x"}}`,
			`{"name":"submit","arguments":{"answer":"x"}}`,
		}, nil),
		[]Tool{&failingTool{calls: new(int)}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "Fail then submit."); err != nil {
		t.Fatal(err)
	}
	if hooked != 0 {
		t.Fatalf("hook ran %d times for a failing tool call", hooked)
	}
}

func TestG1IFunctionRunnerSkipsPostToolHookOnReplay(t *testing.T) {
	t.Parallel()
	hooked := 0
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 2
	options.DuplicateRescueThreshold = 0
	options.PostToolHook = func(string, json.RawMessage, any, error) string {
		hooked++
		return "HOOK"
	}
	runner, err := NewRunner(
		sequenceGenerator([]string{
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"echo","arguments":{"value":"same"}}`,
			`{"name":"submit","arguments":{"answer":"same"}}`,
		}, nil),
		[]Tool{&replayableEchoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "Return same."); err != nil {
		t.Fatal(err)
	}
	if hooked != 1 {
		t.Fatalf("hook ran %d times; want once (first execution, not the replay)", hooked)
	}
}

func TestG1IFunctionRunnerRescueModeAfterSameToolSpiral(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 0
	options.DuplicateRescueThreshold = 0
	options.SameToolRescueLimit = 8
	responses := make([]string, 0, 9)
	options.MaxSteps = 12
	for index := 1; index <= 8; index++ {
		responses = append(responses, fmt.Sprintf(`{"name":"echo","arguments":{"value":"v%d"}}`, index))
	}
	responses = append(responses, `{"name":"submit","arguments":{"answer":"best-effort"}}`)
	var prompts []string
	runner, err := NewRunner(
		sequenceGenerator(responses, &prompts),
		[]Tool{echoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Keep echoing.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "best-effort" || !result.RescueAttempted || !result.RescueSubmitted {
		t.Fatalf("spiral rescue result = %+v", result)
	}
	for index := 0; index < 8; index++ {
		if !result.Steps[index].ToolExecuted || result.Steps[index].ToolRejected != "" {
			t.Fatalf("step %d was not a plain execution: %+v", index+1, result.Steps[index])
		}
	}
	if result.Steps[8].Tool != "submit" {
		t.Fatalf("rescue was not followed by submit: %+v", result.Steps[8])
	}
	if !strings.Contains(prompts[8], "same tool ran successfully 8 times in a row") {
		t.Fatalf("spiral rescue reason missing from the ninth prompt:\n%s", prompts[8])
	}
}

func TestG1IFunctionRunnerSameToolStreakResetsOnFailure(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.MaxSteps = 12
	options.DuplicateReplayLimit = 0
	options.DuplicateRescueThreshold = 0
	options.SameToolRescueLimit = 8
	responses := []string{
		`{"name":"echo","arguments":{"value":"v1"}}`,
		`{"name":"echo","arguments":{"value":"v2"}}`,
		`{"name":"echo","arguments":{"value":"v3"}}`,
		`{"name":"echo","arguments":{"value":"v4"}}`,
		`{"name":"failing","arguments":{"value":"x"}}`,
		`{"name":"echo","arguments":{"value":"v5"}}`,
		`{"name":"echo","arguments":{"value":"v6"}}`,
		`{"name":"echo","arguments":{"value":"v7"}}`,
		`{"name":"echo","arguments":{"value":"v8"}}`,
		`{"name":"submit","arguments":{"answer":"done"}}`,
	}
	runner, err := NewRunner(
		sequenceGenerator(responses, nil),
		[]Tool{echoTool{}, &failingTool{calls: new(int)}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Echo with a failure in between.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || result.RescueAttempted {
		t.Fatalf("interleaved failure must reset the streak: %+v", result)
	}
}

func TestG1IFunctionRunnerSameToolRescueDisabledByZero(t *testing.T) {
	t.Parallel()
	options := g1iRunnerOptions()
	options.DuplicateReplayLimit = 0
	options.DuplicateRescueThreshold = 0
	options.SameToolRescueLimit = 0
	responses := make([]string, 0, 9)
	options.MaxSteps = 12
	for index := 1; index <= 8; index++ {
		responses = append(responses, fmt.Sprintf(`{"name":"echo","arguments":{"value":"v%d"}}`, index))
	}
	responses = append(responses, `{"name":"submit","arguments":{"answer":"done"}}`)
	runner, err := NewRunner(
		sequenceGenerator(responses, nil),
		[]Tool{echoTool{}, submitTestTool{}},
		options,
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Keep echoing.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "done" || result.RescueAttempted {
		t.Fatalf("zero limit must disable the spiral rescue: %+v", result)
	}
}
