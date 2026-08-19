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

func TestRunBaselineAcceptsEmptyResponseForZeroToolIrrelevance(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text: "", FinishReason: continuation.FinishStop,
	}}}
	result, err := RunBaseline(context.Background(), []Case{{
		ID:       "live_irrelevance_120-9-0",
		Category: "live_irrelevance",
		Messages: []Message{{Role: "user", Content: "weather"}},
	}}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.ParseFailed != 0 || len(result.Entries) != 1 || result.Entries[0].Result != "" {
		t.Fatalf("result = %+v", result)
	}
}

func TestRunBaselineTreatsUndecodableIrrelevanceAsNoCall(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text: "I cannot use these tools.", FinishReason: continuation.FinishStop,
	}}}
	entry := testBaselineCase("irrelevance_0")
	entry.Category = "irrelevance"
	result, err := RunBaseline(context.Background(), []Case{entry}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.ParseFailed != 0 || result.Trace[0].ParseError != "" || result.Entries[0].Result != "" {
		t.Fatalf("result = %+v", result)
	}
}

func TestRunBaselineUsesJavaResultEncoding(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text: `{"name":"tool","arguments":{"enabled":true,"limit":50}}`, FinishReason: continuation.FinishStop,
	}}}
	entry := testBaselineCase("simple_java_0")
	entry.Category = "simple_java"
	result, err := RunBaseline(context.Background(), []Case{entry}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.01, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Entries[0].Result != `[tool(enabled="true", limit="50")]` {
		t.Fatalf("result = %q", result.Entries[0].Result)
	}
}

func testBaselineCase(id string) Case {
	return Case{
		ID: id, Category: "simple_python", Messages: []Message{{Role: "user", Content: "call it"}},
		Functions: []json.RawMessage{json.RawMessage(`{"name":"math.tool","parameters":{"type":"dict","properties":{"value":{"type":"boolean"}}}}`)},
	}
}
