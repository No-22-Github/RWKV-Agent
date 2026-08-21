package bfcl

import (
	"context"
	"encoding/json"
	"slices"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestMultiTurnStopsRespectTransportLimits(t *testing.T) {
	t.Parallel()
	rwkvStops := multiTurnStops(TransportRWKVContinuation)
	if len(rwkvStops) != 6 || !slices.Contains(rwkvStops, "\nTool:") || !slices.Contains(rwkvStops, "</s>") {
		t.Fatalf("RWKV multi-turn stops = %q", rwkvStops)
	}
	chatStops := multiTurnStops(TransportChatCompletionsWrapped)
	if len(chatStops) != 4 || !slices.Contains(chatStops, "\nTool:") || slices.Contains(chatStops, "</s>") {
		t.Fatalf("Chat Completions multi-turn stops = %q", chatStops)
	}
}

type recordingMultiTurnExecutor struct {
	calls [][]string
}

func (executor *recordingMultiTurnExecutor) Execute(_ context.Context, _ string, calls []string) ([]string, error) {
	executor.calls = append(executor.calls, append([]string(nil), calls...))
	return []string{`{"ok": true}`}, nil
}

func TestRunMultiTurnCasePreservesOfficialNestedResultShape(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`, FinishReason: continuation.FinishStop},
		{Text: `[]`, FinishReason: continuation.FinishStop},
		{Text: `[{"name":"cd","arguments":{"folder":"temp"}},{"name":"pwd","arguments":{}}]`, FinishReason: continuation.FinishStop},
		{Text: `[]`, FinishReason: continuation.FinishStop},
	}}
	executor := &recordingMultiTurnExecutor{}
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
		Generator: generator, Executor: executor, SessionID: "test", Model: "model",
		Tier: TierBaseline, Transport: TransportRWKVContinuation, MaxSteps: 20,
		MaxOutputTokens: 256, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if trace.Error != "" || len(trace.Result) != 2 || len(trace.Result[0]) != 1 || len(trace.Result[1]) != 1 {
		t.Fatalf("trace = %+v", trace)
	}
	if trace.Result[0][0][0] != `mkdir(dir_name="temp")` || len(trace.Result[1][0]) != 2 ||
		trace.Turns[0].EndedBy != "empty_response" || len(executor.calls) != 2 {
		t.Fatalf("result=%#v turns=%+v calls=%#v", trace.Result, trace.Turns, executor.calls)
	}
}

func TestMultiTurnExecutionCallsPreservesPythonLiterals(t *testing.T) {
	t.Parallel()
	calls, err := ParseMarkdownCalls(`{"name":"tool","arguments":{"enabled":true,"items":[1,"x"]}}`)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := MultiTurnExecutionCalls(calls)
	if err != nil {
		t.Fatal(err)
	}
	if len(encoded) != 1 || encoded[0] != `tool(enabled=True, items=[1, "x"])` {
		t.Fatalf("calls = %q", encoded)
	}
}

func TestEnhancedDuplicateLoopRecordsRejectionBeforeRescue(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `<route>inspect:GorillaFileSystem</route>`, FinishReason: continuation.FinishStop},
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`},
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`},
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`},
	}}
	entry := MultiTurnCase{
		ID: "multi_turn_base_0", Category: "multi_turn_base",
		Turns:         [][]Message{{{Role: "user", Content: "make temp"}}},
		InitialConfig: map[string]any{}, InvolvedClasses: []string{"GorillaFileSystem"},
	}
	catalog := MultiTurnCatalog{Functions: []MultiTurnFunction{{
		Name: "mkdir", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"mkdir","parameters":{"type":"dict"}}`),
	}}}
	trace := RunMultiTurnCase(context.Background(), entry, catalog, MultiTurnRunnerOptions{
		Generator: generator, Executor: &recordingMultiTurnExecutor{}, SessionID: "test", Model: "model",
		Tier: TierEnhanced, Transport: TransportRWKVContinuation, MaxSteps: 20, MaxOutputTokens: 256,
		DuplicateReplayLimit: 2, DuplicateRescueThreshold: 3, CaseTimeout: time.Second,
	})
	if trace.Error != "" || trace.Turns[0].EndedBy != "loop_rescue" || len(trace.Events) != 3 {
		t.Fatalf("trace = %+v", trace)
	}
	if trace.Events[1].Kind != "duplicate_rejected" || trace.Events[2].Kind != "loop_rescue" {
		t.Fatalf("events = %+v", trace.Events)
	}
}

// The reject-and-continue branch was unreachable under the old defaults: a
// streak of 3 satisfied both replay-limit 2 and rescue-threshold 3, and rescue
// broke first. With the threshold above the limit the model gets one rejection
// and a chance to change course.
func TestEnhancedDuplicateRejectionLetsModelRecover(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `<route>inspect:GorillaFileSystem</route>`, FinishReason: continuation.FinishStop},
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`},
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`},
		{Text: `{"name":"mkdir","arguments":{"dir_name":"temp"}}`},
		{Text: `{"name":"pwd","arguments":{}}`},
		{Text: `[]`},
	}}
	trace := RunMultiTurnCase(context.Background(), singleTurnMkdirCase(), mkdirPwdCatalog(), MultiTurnRunnerOptions{
		Generator: generator, Executor: &recordingMultiTurnExecutor{}, SessionID: "test", Model: "model",
		Tier: TierEnhanced, Transport: TransportRWKVContinuation, MaxSteps: 20, MaxOutputTokens: 256,
		DuplicateReplayLimit: 2, DuplicateRescueThreshold: 4, CaseTimeout: time.Second,
	})
	if trace.Error != "" || trace.Turns[0].EndedBy != "empty_response" {
		t.Fatalf("turn should end by the model finishing, not rescue: %+v", trace.Turns[0])
	}
	var rejected, rescued int
	for _, event := range trace.Events {
		switch event.Kind {
		case "duplicate_rejected":
			rejected++
		case "loop_rescue":
			rescued++
		}
	}
	if rejected != 1 || rescued != 0 {
		t.Fatalf("want one rejection and no rescue, got rejected=%d rescued=%d events=%+v", rejected, rescued, trace.Events)
	}
}

// Real loops alternate, so comparing only against the previous signature never
// fires. Qwen's E7 turn spent 8 steps on cd(document)/cd(workspace).
func TestEnhancedAlternatingLoopIsDetected(t *testing.T) {
	t.Parallel()
	results := []continuation.Result{{Text: `<route>inspect:GorillaFileSystem</route>`, FinishReason: continuation.FinishStop}}
	for i := 0; i < 8; i++ {
		folder := "document"
		if i%2 == 1 {
			folder = "workspace"
		}
		results = append(results, continuation.Result{Text: `{"name":"cd","arguments":{"folder":"` + folder + `"}}`})
	}
	generator := &recordingGenerator{results: results}
	catalog := MultiTurnCatalog{Functions: []MultiTurnFunction{
		{Name: "cd", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"cd","parameters":{"type":"dict"}}`)},
	}}
	trace := RunMultiTurnCase(context.Background(), singleTurnMkdirCase(), catalog, MultiTurnRunnerOptions{
		Generator: generator, Executor: &recordingMultiTurnExecutor{}, SessionID: "test", Model: "model",
		Tier: TierEnhanced, Transport: TransportRWKVContinuation, MaxSteps: 20, MaxOutputTokens: 256,
		DuplicateReplayLimit: 2, DuplicateRescueThreshold: 4,
		// Deliberately above the alternation length: signature counting must be
		// what catches this, not the same-tool backstop.
		SameToolRescueLimit: 12, CaseTimeout: time.Second,
	})
	if trace.Turns[0].EndedBy != "loop_rescue" {
		t.Fatalf("alternating loop was not rescued: ended_by=%q steps=%d", trace.Turns[0].EndedBy, len(trace.Turns[0].Steps))
	}
	for _, event := range trace.Events {
		if event.Kind == "loop_rescue" && event.Reason != "repeated_call" {
			t.Fatalf("rescue attributed to %q, want repeated_call", event.Reason)
		}
	}
}

func singleTurnMkdirCase() MultiTurnCase {
	return MultiTurnCase{
		ID: "multi_turn_base_0", Category: "multi_turn_base",
		Turns:         [][]Message{{{Role: "user", Content: "make temp"}}},
		InitialConfig: map[string]any{}, InvolvedClasses: []string{"GorillaFileSystem"},
	}
}

func mkdirPwdCatalog() MultiTurnCatalog {
	return MultiTurnCatalog{Functions: []MultiTurnFunction{
		{Name: "mkdir", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"mkdir","parameters":{"type":"dict"}}`)},
		{Name: "pwd", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"pwd","parameters":{"type":"dict"}}`)},
	}}
}

// A nil turn marshals to JSON null, and the official evaluator raises
// TypeError for the whole split on it (eval_runner.py:222) because
// multi_turn_runner has no per-entry guard. Reproduced against the real
// evaluator during the E8 pre-flight review.
func TestRouteRespondTurnMarshalsAsEmptyArrayNotNull(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `<route>respond</route>`, FinishReason: continuation.FinishStop},
	}}
	trace := RunMultiTurnCase(context.Background(), singleTurnMkdirCase(), mkdirPwdCatalog(), MultiTurnRunnerOptions{
		Generator: generator, Executor: &recordingMultiTurnExecutor{}, SessionID: "test", Model: "model",
		Tier: TierEnhanced, Transport: TransportRWKVContinuation, MaxSteps: 20, MaxOutputTokens: 256,
		CaseTimeout: time.Second,
	})
	if trace.Turns[0].EndedBy != "route_respond" {
		t.Fatalf("ended_by = %q", trace.Turns[0].EndedBy)
	}
	encoded, err := json.Marshal(trace.Result)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(encoded), "null") {
		t.Fatalf("result contains null and would crash the official evaluator: %s", encoded)
	}
	if string(encoded) != `[[]]` {
		t.Fatalf("result = %s, want [[]]", encoded)
	}
	// Same defect class: a turn that ends before any step must not emit a null
	// steps array, or trace aggregation scripts crash.
	turns, err := json.Marshal(trace.Turns)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(turns), `"steps":null`) {
		t.Fatalf("turn trace has null steps: %s", turns)
	}
}

// The array anchor opens a bracket the model does not close: it writes one
// complete call object and stops. Probe A recorded 13/20 Qwen cases failing on
// exactly this while the call itself was correct, which made the array tier look
// like the worst option for Qwen when it is the best.
func TestArrayAnchorClosesItsOwnBracket(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		name      string
		generated string
		want      string
		mode      string
	}{{
		name:      "complete object missing the array terminator",
		generated: `{"name":"mkdir","arguments":{"dir_name":"Projects"}}`,
		want:      `[{"name":"mkdir","arguments":{"dir_name":"Projects"}}]`,
		mode:      "array_elements_closed",
	}, {
		name:      "model closed the array itself",
		generated: `{"name":"ls","arguments":{"a":true}}]`,
		want:      `[{"name":"ls","arguments":{"a":true}}]`,
		mode:      "array_elements",
	}, {
		// A brace inside a string must not be counted as structure.
		name:      "brace inside a string value",
		generated: `{"name":"echo","arguments":{"text":"a{b}c["}}`,
		want:      `[{"name":"echo","arguments":{"text":"a{b}c["}}]`,
		mode:      "array_elements_closed",
	}} {
		content, mode := assembleMultiTurnContent("```json\n[", testCase.generated)
		if content != testCase.want || mode != testCase.mode {
			t.Errorf("%s: content=%q mode=%q, want %q/%q", testCase.name, content, mode, testCase.want, testCase.mode)
			continue
		}
		if _, err := ParseMarkdownCalls(content); err != nil {
			t.Errorf("%s: assembled content does not parse: %v", testCase.name, err)
		}
	}
}

// Truncation is a real model failure and must not be repaired into a pass.
func TestArrayAnchorRefusesToCloseTruncatedOutput(t *testing.T) {
	t.Parallel()
	for _, generated := range []string{
		`{"name":"get_watchlist","arguments":{"`, // unterminated string
		`{"name":"a","arguments":{"x":1}`,        // unbalanced brace
		`{"name":"a","arguments":{"path":"c:\\`,  // trailing escape
	} {
		content, mode := assembleMultiTurnContent("```json\n[", generated)
		if strings.HasSuffix(mode, "_closed") {
			t.Errorf("truncated output %q was closed into %q", generated, content)
		}
		if _, err := ParseMarkdownCalls(content); err == nil {
			t.Errorf("truncated output %q parsed successfully as %q", generated, content)
		}
	}
}

// Wire-compat repaired only a single top-level object, so under an array anchor
// it could not reach the stringified-arguments defect at all. Single-turn hides
// this because the anchor had already driven stringification to zero on the
// parallel splits.
func TestWireCompatRepairsStringifiedArgumentsInsideArray(t *testing.T) {
	t.Parallel()
	functions := []json.RawMessage{
		json.RawMessage(`{"name":"ls","parameters":{"type":"dict","properties":{"a":{"type":"boolean"}}}}`),
		json.RawMessage(`{"name":"cd","parameters":{"type":"dict","properties":{"folder":{"type":"string"}}}}`),
	}
	outcome, err := ParseMarkdownCallsWithMode(
		`[{"name":"ls","arguments":"{\"a\": true}"},{"name":"cd","arguments":"{\"folder\":\"tmp\"}"}]`,
		functions, ParserRWKVWireCompatV1)
	if err != nil {
		t.Fatalf("array of stringified-argument calls was not repaired: %v", err)
	}
	if len(outcome.Calls) != 2 || outcome.Calls[0].Name != "ls" || outcome.Calls[1].Name != "cd" {
		t.Fatalf("calls = %+v", outcome.Calls)
	}
	if len(outcome.Repairs) != 2 {
		t.Fatalf("each element should record its own repair, got %v", outcome.Repairs)
	}
	// Strict must still reject it, or the tiers stop differing.
	if _, err := ParseMarkdownCalls(`[{"name":"ls","arguments":"{\"a\": true}"}]`); err == nil {
		t.Fatal("strict must not accept stringified arguments")
	}
}

// The control tool is a turn-end signal, never an executable call. It must not
// reach the simulator or the official result, and per E3 only a pure
// finish_task counts -- mixing it with real calls cannot hide those calls.
func TestFinishToolEndsTurnWithoutExecuting(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `[{"name":"mkdir","arguments":{"dir_name":"temp"}}]`, FinishReason: continuation.FinishStop},
		{Text: `[{"name":"finish_task","arguments":{}}]`, FinishReason: continuation.FinishStop},
	}}
	executor := &recordingMultiTurnExecutor{}
	trace := RunMultiTurnCase(context.Background(), singleTurnMkdirCase(), mkdirPwdCatalog(), MultiTurnRunnerOptions{
		Generator: generator, Executor: executor, SessionID: "test", Model: "model",
		Tier: TierBaseline, Transport: TransportRWKVContinuation, Anchor: MultiTurnAnchorFence,
		FinishTool: true, MaxSteps: 20, MaxOutputTokens: 256, CaseTimeout: time.Second,
	})
	if trace.Turns[0].EndedBy != "finish_task" {
		t.Fatalf("ended_by = %q, want finish_task", trace.Turns[0].EndedBy)
	}
	if len(executor.calls) != 1 || executor.calls[0][0] != `mkdir(dir_name="temp")` {
		t.Fatalf("control tool must not be executed, got %#v", executor.calls)
	}
	// Only the real call may appear in the official result.
	encoded, err := json.Marshal(trace.Result)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(encoded), FinishTaskName) {
		t.Fatalf("control tool leaked into the official result: %s", encoded)
	}
	if !strings.Contains(string(encoded), "mkdir") {
		t.Fatalf("real call missing from result: %s", encoded)
	}
	// The tool must be offered, and the rule restated at the decision point.
	if !slices.Contains(trace.Turns[0].Catalog, FinishTaskName) {
		t.Fatalf("catalog does not offer the control tool: %v", trace.Turns[0].Catalog)
	}
	if !strings.Contains(generator.requests[0].Prompt, multiTurnFinishReminder) {
		t.Fatal("prompt does not restate the turn-end rule before the decision")
	}
}

// A finish_task mixed with real calls keeps the real calls and does not end the
// turn, so the control tool cannot be used to suppress a wrong call.
func TestFinishToolMixedWithRealCallsKeepsRealCalls(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `[{"name":"finish_task","arguments":{}},{"name":"mkdir","arguments":{"dir_name":"temp"}}]`, FinishReason: continuation.FinishStop},
		{Text: `[{"name":"finish_task","arguments":{}}]`, FinishReason: continuation.FinishStop},
	}}
	executor := &recordingMultiTurnExecutor{}
	trace := RunMultiTurnCase(context.Background(), singleTurnMkdirCase(), mkdirPwdCatalog(), MultiTurnRunnerOptions{
		Generator: generator, Executor: executor, SessionID: "test", Model: "model",
		Tier: TierBaseline, Transport: TransportRWKVContinuation, Anchor: MultiTurnAnchorFence,
		FinishTool: true, MaxSteps: 20, MaxOutputTokens: 256, CaseTimeout: time.Second,
	})
	if len(executor.calls) != 1 || executor.calls[0][0] != `mkdir(dir_name="temp")` {
		t.Fatalf("real call in a mixed response must still execute, got %#v", executor.calls)
	}
	var mixed bool
	for _, event := range trace.Events {
		if event.Kind == "finish_task_mixed" {
			mixed = true
		}
	}
	if !mixed {
		t.Fatalf("mixed selection was not recorded: %+v", trace.Events)
	}
}

func TestMultiTurnAnchorPrefillAndEmptyReachability(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		anchor    MultiTurnAnchor
		prefill   string
		reachable bool
	}{
		{MultiTurnAnchorFence, "```json\n", true},
		{MultiTurnAnchorArray, "```json\n[", true},
		// C1 measured 93.25% on simple_python for this shape, but it makes an
		// empty turn-ending response physically unreachable -- the same
		// mechanism that zeroed the parallel splits.
		{MultiTurnAnchorObject, "```json\n{\"name\":\"", false},
	} {
		if got := testCase.anchor.Prefill(); got != testCase.prefill {
			t.Errorf("%s prefill = %q, want %q", testCase.anchor, got, testCase.prefill)
		}
		if got := testCase.anchor.EmptyReachable(); got != testCase.reachable {
			t.Errorf("%s EmptyReachable = %v, want %v", testCase.anchor, got, testCase.reachable)
		}
	}
	if ValidMultiTurnAnchor("none") {
		t.Error("the none tier was removed: it only re-runs E7, and fence is the anchored lower bound")
	}
}

// V1 re-rendered initial_config into every step, so after the first executed
// call the block contradicted the Tool lines above it. RWKV was observed
// reading it on turn 1 of E7.
func TestMultiTurnPromptOmitsStaleInitialConfigByDefault(t *testing.T) {
	t.Parallel()
	entry := singleTurnMkdirCase()
	entry.InitialConfig = map[string]any{"GorillaFileSystem": map[string]any{"root": "workspace"}}
	transcript := []multiTurnTranscript{{Role: "User", Content: "make temp"}}
	prompt, err := RenderMultiTurnPrompt(entry, mkdirPwdCatalog().Functions, transcript, MultiTurnAnchorObject, false, false)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(prompt, "Initial state:") || strings.Contains(prompt, "workspace") {
		t.Fatalf("v2 prompt leaks the stale initial state: %s", prompt)
	}
	if !strings.HasSuffix(prompt, "Assistant: ```json\n{\"name\":\"") {
		t.Fatalf("prompt does not end with the anchor: %q", prompt[max(0, len(prompt)-40):])
	}
	legacy, err := RenderMultiTurnPrompt(entry, mkdirPwdCatalog().Functions, transcript, MultiTurnAnchorFence, true, false)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(legacy, "Initial state:") {
		t.Fatal("--render-initial-config must reproduce the v1 block for comparison runs")
	}
}

func TestMultiTurnParseFailureRemainsInFollowingTurnTranscript(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: "not-json"},
		{Text: `[]`},
	}}
	entry := MultiTurnCase{
		ID: "multi_turn_base_0", Category: "multi_turn_base",
		Turns: [][]Message{
			{{Role: "user", Content: "first"}},
			{{Role: "user", Content: "second"}},
		},
		InitialConfig: map[string]any{}, InvolvedClasses: []string{"GorillaFileSystem"},
	}
	catalog := MultiTurnCatalog{Functions: []MultiTurnFunction{{
		Name: "mkdir", Class: "GorillaFileSystem", Raw: json.RawMessage(`{"name":"mkdir","parameters":{"type":"dict"}}`),
	}}}
	trace := RunMultiTurnCase(context.Background(), entry, catalog, MultiTurnRunnerOptions{
		Generator: generator, Executor: &recordingMultiTurnExecutor{}, SessionID: "test", Model: "model",
		Tier: TierBaseline, Transport: TransportRWKVContinuation, MaxSteps: 20, MaxOutputTokens: 256,
		CaseTimeout: time.Second,
	})
	if trace.Error != "" || len(generator.requests) != 2 {
		t.Fatalf("trace=%+v requests=%d", trace, len(generator.requests))
	}
	if !strings.Contains(generator.requests[1].Prompt, "Assistant: not-json\nUser: second") {
		t.Fatalf("following prompt does not preserve invalid assistant response: %s", generator.requests[1].Prompt)
	}
}
