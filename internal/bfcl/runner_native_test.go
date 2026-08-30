package bfcl

import (
	"context"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// Characterization tests for the RunNative worker pool failure paths. The
// existing runner_test.go covers the success aggregation only; these lock the
// per-case error isolation, prompt-size skipping, and result-conversion errors
// that the later worker-pool dedup must preserve.

type scriptedCompleter struct {
	respond func(request toolchat.Request) (toolchat.Result, error)
}

func (completer *scriptedCompleter) NativeToolCalling() bool { return true }

func (completer *scriptedCompleter) Complete(
	_ context.Context,
	request toolchat.Request,
	_ continuation.EventSink,
) (toolchat.Result, error) {
	return completer.respond(request)
}

func TestRunNativeCompleterFailureIsolatesOneCase(t *testing.T) {
	t.Parallel()
	completer := &scriptedCompleter{respond: func(request toolchat.Request) (toolchat.Result, error) {
		for _, message := range request.Messages {
			if strings.Contains(message.Content, "boom") {
				return toolchat.Result{}, &testRemoteError{"provider exploded"}
			}
		}
		return toolchat.Result{
			ToolCalls:    []toolchat.ToolCall{{Name: "math.tool", Arguments: `{"value":true}`}},
			FinishReason: continuation.FinishToolCalls,
		}, nil
	}}
	cases := []Case{
		testRunnerCase("simple_python_0", "math.tool"),
		{ID: "simple_python_boom", Category: "simple_python", Messages: []Message{{Role: "user", Content: "boom"}}},
		testRunnerCase("simple_python_2", "math.tool"),
	}
	result, err := RunNative(context.Background(), cases, RunnerOptions{
		Completer: completer, Model: "model", Concurrency: 3, MaxOutputTokens: 1024,
		Temperature: 0, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Failed != 1 || result.Skipped != 0 || len(result.Entries) != 3 {
		t.Fatalf("result = %+v", result)
	}
	var failed TraceEntry
	for _, entry := range result.Trace {
		if entry.ID == "simple_python_boom" {
			failed = entry
		} else if entry.Error != "" || entry.Result == "" {
			t.Fatalf("healthy case %s picked up a failure: %+v", entry.ID, entry)
		}
	}
	if failed.Error == "" || failed.ModelCalls != 1 || failed.Result != "" {
		t.Fatalf("failed case trace = %+v", failed)
	}
	if failed.InputTokens != 0 || failed.OutputTokens != 0 {
		t.Fatalf("failed case usage = %d/%d", failed.InputTokens, failed.OutputTokens)
	}
}

func TestRunNativeSkipsOversizedPromptWithoutCallingModel(t *testing.T) {
	t.Parallel()
	calls := 0
	completer := &scriptedCompleter{respond: func(toolchat.Request) (toolchat.Result, error) {
		calls++
		return toolchat.Result{FinishReason: continuation.FinishStop}, nil
	}}
	result, err := RunNative(context.Background(), []Case{
		testRunnerCase("simple_python_0", "math.tool"),
	}, RunnerOptions{
		Completer: completer, Model: "model", Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 10, Temperature: 0, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Skipped != 1 || result.Failed != 0 || calls != 0 {
		t.Fatalf("result = %+v calls = %d", result, calls)
	}
	entry := result.Trace[0]
	if entry.ModelCalls != 0 || !entry.Skipped ||
		!strings.Contains(entry.Error, "exceeds max_prompt_chars 10") {
		t.Fatalf("skipped trace = %+v", entry)
	}
}

func TestRunNativeInvalidToolNameBecomesCaseErrorWithUsage(t *testing.T) {
	t.Parallel()
	completer := &scriptedCompleter{respond: func(toolchat.Request) (toolchat.Result, error) {
		return toolchat.Result{
			ToolCalls:    []toolchat.ToolCall{{Name: "not a callable", Arguments: `{"value":true}`}},
			FinishReason: continuation.FinishToolCalls,
			Usage:        continuation.Usage{PromptTokens: 9, CompletionTokens: 4},
		}, nil
	}}
	result, err := RunNative(context.Background(), []Case{
		testRunnerCase("simple_python_0", "math.tool"),
	}, RunnerOptions{
		Completer: completer, Model: "model", Concurrency: 1, MaxOutputTokens: 1024,
		Temperature: 0, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Failed != 1 {
		t.Fatalf("result = %+v", result)
	}
	entry := result.Trace[0]
	if !strings.Contains(entry.Error, "invalid BFCL function name") ||
		entry.Result != "" ||
		entry.InputTokens != 9 || entry.OutputTokens != 4 {
		t.Fatalf("trace = %+v", entry)
	}
}

type testRemoteError struct{ message string }

func (err *testRemoteError) Error() string { return err.message }
