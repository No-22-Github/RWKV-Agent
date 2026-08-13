package agent

import (
	"context"
	"encoding/json"
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
