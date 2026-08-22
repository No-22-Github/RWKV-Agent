package bfcl

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// fakeCompleter is a scripted toolchat.Completer that records every request. It
// also implements continuation.Generator (returning an error) so it can satisfy
// the runner's non-nil Generator guard exactly as the real chatcompletions
// Client does -- one value that is both a Generator and a Completer.
type fakeCompleter struct {
	results  []toolchat.Result
	requests []toolchat.Request
	index    int
}

func (f *fakeCompleter) NativeToolCalling() bool { return true }

func (f *fakeCompleter) Complete(_ context.Context, request toolchat.Request, _ continuation.EventSink) (toolchat.Result, error) {
	f.requests = append(f.requests, request)
	if f.index >= len(f.results) {
		return toolchat.Result{}, fmt.Errorf("fakeCompleter ran out of scripted results at call %d", f.index)
	}
	result := f.results[f.index]
	f.index++
	return result, nil
}

func (f *fakeCompleter) Continue(context.Context, continuation.Request, continuation.EventSink) (continuation.Result, error) {
	return continuation.Result{}, fmt.Errorf("native path must not call Continue")
}

// echoPerCallExecutor returns one result per call, like the real sidecar, so the
// native tool-result-to-tool_call_id linkage stays one-to-one.
type echoPerCallExecutor struct {
	calls [][]string
}

func (executor *echoPerCallExecutor) Execute(_ context.Context, _ string, calls []string) ([]string, error) {
	executor.calls = append(executor.calls, append([]string(nil), calls...))
	results := make([]string, len(calls))
	for index := range calls {
		results[index] = fmt.Sprintf(`{"ok": %d}`, index)
	}
	return results, nil
}

func nativeToolCall(id, name, arguments string) toolchat.ToolCall {
	return toolchat.ToolCall{ID: id, Name: name, Arguments: arguments}
}

// The native path speaks the provider's own tool channel: structured tool_calls
// in, an empty tool_calls response ends the turn (the official termination), and
// prior calls plus their results are replayed as assistant/tool messages linked
// by tool_call_id. This one case exercises all of that plus a parallel step.
func TestMultiTurnNativeEndToEndReplaysToolCallsAndResults(t *testing.T) {
	t.Parallel()
	completer := &fakeCompleter{results: []toolchat.Result{
		{ToolCalls: []toolchat.ToolCall{nativeToolCall("call_mkdir", "mkdir", `{"dir_name":"temp"}`)}, FinishReason: continuation.FinishToolCalls},
		{FinishReason: continuation.FinishStop}, // empty tool_calls ends turn 0
		{ToolCalls: []toolchat.ToolCall{
			nativeToolCall("call_cd", "cd", `{"folder":"temp"}`),
			nativeToolCall("call_pwd", "pwd", `{}`),
		}, FinishReason: continuation.FinishToolCalls},
		{FinishReason: continuation.FinishStop}, // empty tool_calls ends turn 1
	}}
	executor := &echoPerCallExecutor{}
	entry := MultiTurnCase{
		ID: "multi_turn_base_0", Category: "multi_turn_base",
		Turns:         [][]Message{{{Role: "user", Content: "make temp"}}, {{Role: "user", Content: "enter it"}}},
		InitialConfig: map[string]any{}, InvolvedClasses: []string{"GorillaFileSystem"},
	}
	catalog := MultiTurnCatalog{Functions: []MultiTurnFunction{
		{Name: "mkdir", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"mkdir","parameters":{"type":"dict"}}`)},
		{Name: "cd", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"cd","parameters":{"type":"dict"}}`)},
		{Name: "pwd", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"pwd","parameters":{"type":"dict"}}`)},
	}}
	trace := RunMultiTurnCase(context.Background(), entry, catalog, MultiTurnRunnerOptions{
		Generator: completer, Completer: completer, Executor: executor, SessionID: "test", Model: "model",
		Tier: TierBaseline, Transport: TransportChatCompletionsNativeFC, MaxSteps: 20,
		MaxOutputTokens: 256, Temperature: 0, CaseTimeout: time.Second,
	})
	if trace.Error != "" {
		t.Fatalf("unexpected error: %s", trace.Error)
	}
	if len(trace.Result) != 2 || len(trace.Result[0]) != 1 || len(trace.Result[1]) != 1 {
		t.Fatalf("result shape = %#v", trace.Result)
	}
	if trace.Result[0][0][0] != `mkdir(dir_name="temp")` {
		t.Fatalf("turn 0 call = %q", trace.Result[0][0][0])
	}
	if len(trace.Result[1][0]) != 2 || trace.Result[1][0][0] != `cd(folder="temp")` || trace.Result[1][0][1] != "pwd()" {
		t.Fatalf("turn 1 parallel step = %#v", trace.Result[1][0])
	}
	if trace.Turns[0].EndedBy != "empty_response" || trace.Turns[1].EndedBy != "empty_response" {
		t.Fatalf("turns must end on empty tool_calls: %q / %q", trace.Turns[0].EndedBy, trace.Turns[1].EndedBy)
	}
	// The third Complete call (turn 1, step 0) must replay turn 0's assistant
	// tool_call and its tool result, the result linked by tool_call_id.
	third := completer.requests[2]
	var sawAssistantCall, sawLinkedResult bool
	for _, message := range third.Messages {
		if message.Role == toolchat.RoleAssistant {
			for _, call := range message.ToolCalls {
				if call.Name == "mkdir" {
					sawAssistantCall = true
				}
			}
		}
		if message.Role == toolchat.RoleTool && message.ToolCallID == "call_mkdir" {
			sawLinkedResult = true
		}
	}
	if !sawAssistantCall || !sawLinkedResult {
		t.Fatalf("turn 1 request did not replay linked history: assistantCall=%v linkedResult=%v messages=%+v", sawAssistantCall, sawLinkedResult, third.Messages)
	}
	// No markdown preamble or prefill anchor may leak into the native request.
	for _, message := range third.Messages {
		if strings.Contains(message.Content, "Output JSON only") || strings.Contains(message.Content, "```json") {
			t.Fatalf("native request leaked wrapped-protocol text: %q", message.Content)
		}
	}
	// Tools are presented natively, not as a system tool list.
	if len(third.Tools) == 0 {
		t.Fatal("native request carried no tools array")
	}
}

// The native-only transcript fields (ToolCalls, CallIDs) must be invisible to
// the wrapped renderer, or populating them would break byte-identity with the
// frozen E1/E2/E8 prompts. This is the guarantee that lets the two protocols
// share one transcript.
func TestAdditiveTranscriptFieldsDoNotChangeWrappedRender(t *testing.T) {
	t.Parallel()
	entry := singleTurnMkdirCase()
	functions := mkdirPwdCatalog().Functions
	plain := []multiTurnTranscript{
		{Role: "User", Content: "make temp"},
		{Role: "Assistant", Content: `{"name":"mkdir","arguments":{"dir_name":"t"}}`},
		{Role: "Tool", Content: []string{`{"ok":true}`}},
	}
	enriched := []multiTurnTranscript{
		{Role: "User", Content: "make temp"},
		{Role: "Assistant", Content: `{"name":"mkdir","arguments":{"dir_name":"t"}}`, ToolCalls: []toolchat.ToolCall{nativeToolCall("call_0", "mkdir", `{"dir_name":"t"}`)}},
		{Role: "Tool", Content: []string{`{"ok":true}`}, CallIDs: []string{"call_0"}},
	}
	for _, anchor := range []MultiTurnAnchor{MultiTurnAnchorFence, MultiTurnAnchorArray, MultiTurnAnchorObject} {
		want, err := RenderMultiTurnPrompt(entry, functions, plain, anchor, false, false)
		if err != nil {
			t.Fatal(err)
		}
		got, err := RenderMultiTurnPrompt(entry, functions, enriched, anchor, false, false)
		if err != nil {
			t.Fatal(err)
		}
		if want != got {
			t.Fatalf("anchor %s: additive fields changed the wrapped render:\n want %q\n got  %q", anchor, want, got)
		}
	}
}

// A step that runs out of budget mid-response (finish_reason=length, no
// tool_calls) ends the turn like any no-call response -- it is scored as that
// failed turn, matching official semantics, not excluded. The finish_reason is
// recorded so a too-small --max-tokens is diagnosable afterward.
func TestMultiTurnNativeTruncationEndsTurnAndRecordsFinishReason(t *testing.T) {
	t.Parallel()
	completer := &fakeCompleter{results: []toolchat.Result{
		{ToolCalls: nil, Content: "", FinishReason: continuation.FinishLength},
	}}
	trace := RunMultiTurnCase(context.Background(), singleTurnMkdirCase(), mkdirPwdCatalog(), MultiTurnRunnerOptions{
		Generator: completer, Completer: completer, Executor: &echoPerCallExecutor{}, SessionID: "test", Model: "model",
		Tier: TierBaseline, Transport: TransportChatCompletionsNativeFC, MaxSteps: 20,
		MaxOutputTokens: 8, Temperature: 0, CaseTimeout: time.Second,
	})
	if trace.Error != "" || trace.FailureKind == MultiTurnFailureInfrastructure {
		t.Fatalf("truncation must not fail the case as infra: error=%q kind=%q", trace.Error, trace.FailureKind)
	}
	if trace.Turns[0].EndedBy != "empty_response" {
		t.Fatalf("truncation should end the turn as a no-call response, got %q", trace.Turns[0].EndedBy)
	}
	if len(trace.Turns[0].Steps) != 1 || trace.Turns[0].Steps[0].FinishReason != string(continuation.FinishLength) {
		t.Fatalf("finish_reason=length was not recorded: %+v", trace.Turns[0].Steps)
	}
}

func TestMultiTurnNativeToolsRewritesSchemaTypes(t *testing.T) {
	t.Parallel()
	tools, err := MultiTurnNativeTools([]MultiTurnFunction{{
		Name: "resize", Class: "VehicleControlAPI",
		Raw: json.RawMessage(`{"name":"resize","description":"d","parameters":{"type":"dict","properties":{"scale":{"type":"float"},"tags":{"type":"tuple"}}}}`),
	}})
	if err != nil {
		t.Fatal(err)
	}
	if len(tools) != 1 {
		t.Fatalf("tools = %+v", tools)
	}
	schema := string(tools[0].Parameters)
	if !strings.Contains(schema, `"type":"object"`) || !strings.Contains(schema, `"type":"number"`) || !strings.Contains(schema, `"type":"array"`) {
		t.Fatalf("schema types not rewritten to OpenAI form: %s", schema)
	}
	if strings.Contains(schema, `"dict"`) || strings.Contains(schema, `"float"`) || strings.Contains(schema, `"tuple"`) {
		t.Fatalf("schema still carries BFCL types: %s", schema)
	}
}

// A dotted BFCL name is sanitized for the OpenAI tools array; the returned call
// must be un-sanitized back to the original before it reaches the simulator.
func TestMultiTurnNativeUnsanitizesDottedNames(t *testing.T) {
	t.Parallel()
	functions := []MultiTurnFunction{{Name: "API.call", Class: "WebSearchAPI", Raw: json.RawMessage(`{"name":"API.call","parameters":{"type":"dict"}}`)}}
	names, err := multiTurnNativeNames(functions)
	if err != nil {
		t.Fatal(err)
	}
	if names["API_call"] != "API.call" {
		t.Fatalf("names = %#v", names)
	}
	tools, err := MultiTurnNativeTools(functions)
	if err != nil {
		t.Fatal(err)
	}
	if tools[0].Name != "API_call" {
		t.Fatalf("tool name not sanitized: %q", tools[0].Name)
	}
	encoded, err := multiTurnExecutionCalls([]toolchat.ToolCall{nativeToolCall("id", "API_call", `{"q":"x"}`)}, names)
	if err != nil {
		t.Fatal(err)
	}
	if len(encoded) != 1 || encoded[0] != `API.call(q="x")` {
		t.Fatalf("execution call not un-sanitized: %q", encoded)
	}
}
