package bfcl

import (
	"context"
	"encoding/json"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

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
