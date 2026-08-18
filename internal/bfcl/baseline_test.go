package bfcl

import (
	"context"
	"encoding/json"
	"slices"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

type recordingGenerator struct {
	requests []continuation.Request
	results  []continuation.Result
}

func TestBaselineStopsRespectTransportLimits(t *testing.T) {
	t.Parallel()
	rwkvStops := baselineStops(TransportRWKVContinuation)
	if len(rwkvStops) != 5 || !slices.Contains(rwkvStops, "\nUser:") {
		t.Fatalf("RWKV stops = %q", rwkvStops)
	}
	chatStops := baselineStops(TransportChatCompletionsWrapped)
	if len(chatStops) != 4 || slices.Contains(chatStops, "\nUser:") {
		t.Fatalf("Chat Completions stops = %q", chatStops)
	}
}

func (generator *recordingGenerator) Continue(
	_ context.Context,
	request continuation.Request,
	_ continuation.EventSink,
) (continuation.Result, error) {
	generator.requests = append(generator.requests, request)
	result := generator.results[0]
	generator.results = generator.results[1:]
	return result, nil
}

func TestRunBaselineMakesOneStrictCallPerCase(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `{"name":"math.tool","arguments":{"value":true}}`, FinishReason: continuation.FinishStop},
		{Text: `not a call`, FinishReason: continuation.FinishStop},
	}}
	cases := []Case{testBaselineCase("simple_python_0"), testBaselineCase("simple_python_1")}
	result, err := RunBaseline(context.Background(), cases, BaselineRunnerOptions{
		Generator: generator, Model: "model", Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(generator.requests) != 2 || result.Failed != 0 || result.ParseFailed != 1 {
		t.Fatalf("requests=%d result=%+v", len(generator.requests), result)
	}
	if result.Entries[0].Result != `[math.tool(value=True)]` || result.Entries[0].ModelCalls != 1 {
		t.Fatalf("first result = %+v", result.Entries[0])
	}
	if result.Entries[1].Result != "" || result.Entries[1].ModelCalls != 1 {
		t.Fatalf("second result = %+v", result.Entries[1])
	}
	for _, request := range generator.requests {
		if request.Sampling.TopK != 1 || request.Sampling.Temperature != 0.001 {
			t.Fatalf("request = %+v", request)
		}
	}
}

func testBaselineCase(id string) Case {
	return Case{
		ID: id, Category: "simple_python", Messages: []Message{{Role: "user", Content: "call it"}},
		Functions: []json.RawMessage{json.RawMessage(`{"name":"math.tool","parameters":{"type":"dict","properties":{"value":{"type":"boolean"}}}}`)},
	}
}
