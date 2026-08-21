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

func TestAssembleMarkdownContentHandlesContinuationShapes(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name      string
		anchor    string
		generated string
		content   string
		mode      string
	}{
		{
			name: "deep object continuation", anchor: `{"name":"`,
			generated: `tool","arguments":{}}`, content: `{"name":"tool","arguments":{}}`,
			mode: "prefill_continuation",
		},
		{
			name: "self-contained object", anchor: `{"name":"`,
			generated: `{"name":"tool","arguments":{}}`, content: `{"name":"tool","arguments":{}}`,
			mode: "self_contained",
		},
		{
			name: "array element continuation", anchor: `[{"name":"`,
			generated: `{"name":"tool","arguments":{}}]`, content: `[{"name":"tool","arguments":{}}]`,
			mode: "array_elements",
		},
		{
			name: "deep array continuation", anchor: `[{"name":"`,
			generated: `tool","arguments":{}}]`, content: `[{"name":"tool","arguments":{}}]`,
			mode: "prefill_continuation",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			content, mode := assembleMarkdownContent(test.anchor, test.generated)
			if content != test.content || mode != test.mode {
				t.Fatalf("content=%q mode=%q", content, mode)
			}
		})
	}
}

func TestCorrectedPromptUsesAssembledContentOnce(t *testing.T) {
	t.Parallel()
	rendered := RenderedPrompt{
		Prompt: "User: call it\n\nAssistant: ```json\n{\"name\":\"",
		Anchor: `{"name":"`,
	}
	content := `{"name":"tool","arguments":{"value":invalid}}`
	prompt := correctedPrompt(rendered, content, "json_syntax")
	if strings.Count(prompt, content) != 1 {
		t.Fatalf("assembled content count = %d in %q", strings.Count(prompt, content), prompt)
	}
	if strings.Contains(prompt, `{"name":"{"name":"`) {
		t.Fatalf("prompt duplicated prefill anchor: %q", prompt)
	}
	if !strings.HasSuffix(prompt, "Assistant: ```json\n{\"name\":\"") {
		t.Fatalf("retry suffix = %q", prompt)
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
		{Text: `math.tool","arguments":{"value":true}}`, FinishReason: continuation.FinishStop},
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
	if result.Trace[0].GeneratedContent != `math.tool","arguments":{"value":true}}` ||
		result.Trace[0].Content != `{"name":"math.tool","arguments":{"value":true}}` ||
		result.Trace[0].PrefillAnchor != `{"name":"` || result.Trace[0].PromptSHA256 == "" {
		t.Fatalf("first trace = %+v", result.Trace[0])
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
		Text: `tool","arguments":{"enabled":true,"limit":50}}`, FinishReason: continuation.FinishStop,
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

func TestRunBaselineReconstructsParallelArrayAnchor(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text:         `play","arguments":{"artist":"A"}},{"name":"play","arguments":{"artist":"B"}}]`,
		FinishReason: continuation.FinishStop,
	}}}
	entry := Case{
		ID:       "parallel_0",
		Category: "parallel",
		Messages: []Message{{Role: "user", Content: "play both"}},
		Functions: []json.RawMessage{json.RawMessage(
			`{"name":"play","parameters":{"type":"dict","properties":{"artist":{"type":"string"}}}}`,
		)},
	}
	result, err := RunBaseline(context.Background(), []Case{entry}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.ParseFailed != 0 || result.Trace[0].PrefillAnchor != `[{"name":"` ||
		result.Entries[0].Result != `[play(artist="A"), play(artist="B")]` {
		t.Fatalf("result=%+v trace=%+v", result, result.Trace[0])
	}
}

func TestRunEnhancedRepairsBeforeRetry(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text: `math.tool","arguments":"{\"value\":true}"}`, FinishReason: continuation.FinishStop,
	}}}
	result, err := RunBaseline(context.Background(), []Case{testBaselineCase("simple_python_0")}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Tier: TierEnhanced, Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(generator.requests) != 1 || result.Repaired != 1 || result.Retried != 0 ||
		result.Entries[0].Result != `[math.tool(value=True)]` {
		t.Fatalf("requests=%d result=%+v trace=%+v", len(generator.requests), result, result.Trace[0])
	}
	if !slices.Equal(result.Trace[0].Repairs, []string{RepairArgumentsUnwrapped}) {
		t.Fatalf("repairs = %q", result.Trace[0].Repairs)
	}
}

func TestRunEnhancedRetriesOnceAfterCompatFailure(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{
		{Text: `broken`, FinishReason: continuation.FinishStop},
		{Text: `math.tool","arguments":{"value":true}}`, FinishReason: continuation.FinishStop},
	}}
	result, err := RunBaseline(context.Background(), []Case{testBaselineCase("simple_python_0")}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Tier: TierEnhanced, Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(generator.requests) != 2 || result.Retried != 1 || result.RetryParsed != 1 ||
		result.Entries[0].ModelCalls != 2 || result.Entries[0].Result != `[math.tool(value=True)]` {
		t.Fatalf("requests=%d result=%+v trace=%+v", len(generator.requests), result, result.Trace[0])
	}
	if !strings.Contains(generator.requests[1].Prompt, "error: json_syntax") ||
		!strings.HasSuffix(generator.requests[1].Prompt, "Assistant: ```json\n{\"name\":\"") {
		t.Fatalf("retry prompt = %q", generator.requests[1].Prompt)
	}
	if len(result.Trace[0].Attempts) != 2 || result.Trace[0].Attempts[0].Adopted ||
		!result.Trace[0].Attempts[1].Adopted {
		t.Fatalf("attempts = %+v", result.Trace[0].Attempts)
	}
}

func TestRunEnhancedDoesNotRetryIrrelevanceParseFailure(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text: "I cannot use these tools.", FinishReason: continuation.FinishStop,
	}}}
	entry := testBaselineCase("irrelevance_0")
	entry.Category = "irrelevance"
	result, err := RunBaseline(context.Background(), []Case{entry}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Tier: TierEnhanced, Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(generator.requests) != 1 || result.Retried != 0 || result.ParseFailed != 0 ||
		!result.Trace[0].Attempts[0].NoCall {
		t.Fatalf("requests=%d result=%+v trace=%+v", len(generator.requests), result, result.Trace[0])
	}
}

func TestRunEnhancedDoesNotHideIrrelevanceToolCall(t *testing.T) {
	t.Parallel()
	generator := &recordingGenerator{results: []continuation.Result{{
		Text: `math.tool","arguments":{"value":true}}`, FinishReason: continuation.FinishStop,
	}}}
	entry := testBaselineCase("irrelevance_0")
	entry.Category = "irrelevance"
	result, err := RunBaseline(context.Background(), []Case{entry}, BaselineRunnerOptions{
		Generator: generator, Model: "model", Tier: TierEnhanced, Transport: TransportRWKVContinuation,
		Concurrency: 1, MaxOutputTokens: 1024,
		MaxPromptChars: 40000, Temperature: 0.001, CaseTimeout: time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Entries[0].Result != `[math.tool(value=True)]` || result.Trace[0].Attempts[0].NoCall {
		t.Fatalf("result=%+v trace=%+v", result, result.Trace[0])
	}
}

func testBaselineCase(id string) Case {
	return Case{
		ID: id, Category: "simple_python", Messages: []Message{{Role: "user", Content: "call it"}},
		Functions: []json.RawMessage{json.RawMessage(`{"name":"math.tool","parameters":{"type":"dict","properties":{"value":{"type":"boolean"}}}}`)},
	}
}
