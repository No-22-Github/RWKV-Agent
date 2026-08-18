package bfcl

import (
	"context"
	"encoding/json"
	"sync"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type recordingCompleter struct {
	mu       sync.Mutex
	requests []toolchat.Request
}

func (completer *recordingCompleter) NativeToolCalling() bool { return true }

func (completer *recordingCompleter) Complete(
	_ context.Context,
	request toolchat.Request,
	_ continuation.EventSink,
) (toolchat.Result, error) {
	completer.mu.Lock()
	completer.requests = append(completer.requests, request)
	completer.mu.Unlock()
	return toolchat.Result{
		ToolCalls:    []toolchat.ToolCall{{Name: request.Tools[0].Name, Arguments: `{"value":true}`}},
		FinishReason: continuation.FinishToolCalls,
		Usage:        continuation.Usage{PromptTokens: 10, CompletionTokens: 2},
	}, nil
}

func TestRunNativeMakesExactlyOneCallPerCase(t *testing.T) {
	t.Parallel()
	completer := &recordingCompleter{}
	cases := []Case{
		testRunnerCase("simple_python_0", "math.tool"),
		testRunnerCase("simple_python_1", "other"),
	}
	result, err := RunNative(context.Background(), cases, RunnerOptions{
		Completer: completer, Model: "model", Concurrency: 2, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(completer.requests) != 2 || len(result.Entries) != 2 || result.Failed != 0 || result.Skipped != 0 {
		t.Fatalf("requests=%d result=%+v", len(completer.requests), result)
	}
	if result.Entries[0].Result != `[math.tool(value=True)]` || result.Entries[0].ModelCalls != 1 {
		t.Fatalf("first result = %+v", result.Entries[0])
	}
	for _, request := range completer.requests {
		if request.ToolChoice != toolchat.ToolChoiceAuto || !request.ParallelToolCalls ||
			request.Sampling.TopK != 1 || request.Sampling.Temperature != 0.001 {
			t.Fatalf("request = %+v", request)
		}
	}
}

func testRunnerCase(id, name string) Case {
	return Case{
		ID: id, Category: "simple_python", Messages: []Message{{Role: "user", Content: "call it"}},
		Functions: []json.RawMessage{json.RawMessage(`{"name":"` + name + `","parameters":{"type":"dict","properties":{"value":{"type":"boolean"}}}}`)},
	}
}
