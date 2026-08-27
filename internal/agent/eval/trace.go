package eval

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type traceRecorder struct {
	mu       sync.Mutex
	now      func() time.Time
	caseID   string
	turn     int
	sequence int
	trace    []TraceRecord
}

func newTraceRecorder(now func() time.Time) *traceRecorder {
	return &traceRecorder{now: now}
}

func (r *traceRecorder) setContext(caseID string, turn int) {
	r.mu.Lock()
	r.caseID = caseID
	r.turn = turn
	r.mu.Unlock()
}

func (r *traceRecorder) append(record TraceRecord) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.sequence++
	record.Sequence = r.sequence
	record.Timestamp = r.now().UTC()
	record.CaseID = r.caseID
	record.Turn = r.turn
	r.trace = append(r.trace, record)
}

func (r *traceRecorder) runnerEvent(event agent.Event) {
	value := &RunnerEventTrace{
		Kind:  event.Kind,
		Step:  event.Step,
		Tool:  event.Tool,
		Route: event.Route,
	}
	if event.Err != nil {
		value.Error = event.Err.Error()
	}
	r.append(TraceRecord{Kind: "runner_event", RunnerEvent: value})
}

func (r *traceRecorder) turnResult(result agent.Result, outcome TurnOutcome, err error) {
	value := &TurnTrace{Result: result, Outcome: outcome}
	if err != nil {
		value.Error = err.Error()
	}
	r.append(TraceRecord{Kind: "turn_result", TurnResult: value})
}

func (r *traceRecorder) modelCall(value ModelCallTrace) {
	r.append(TraceRecord{Kind: "model_call", ModelCall: &value})
}

func (r *traceRecorder) records() []TraceRecord {
	r.mu.Lock()
	defer r.mu.Unlock()
	return append([]TraceRecord(nil), r.trace...)
}

type recordingGenerator struct {
	generator continuation.Generator
	recorder  *traceRecorder
}

func (g *recordingGenerator) Continue(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	started := time.Now()
	result, err := g.generator.Continue(ctx, request, sink)
	value := ModelCallTrace{
		Stage:          requestStage(request),
		Request:        requestSnapshot(request),
		Response:       responseSnapshot(result),
		DurationMillis: time.Since(started).Milliseconds(),
	}
	if err != nil {
		value.Error = err.Error()
	}
	g.recorder.modelCall(value)
	return result, err
}

func (g *recordingGenerator) NativeToolCalling() bool {
	completer, ok := g.generator.(toolchat.Completer)
	return ok && completer.NativeToolCalling()
}

func (g *recordingGenerator) Complete(
	ctx context.Context,
	request toolchat.Request,
	sink continuation.EventSink,
) (toolchat.Result, error) {
	completer, ok := g.generator.(toolchat.Completer)
	if !ok || !completer.NativeToolCalling() {
		return toolchat.Result{}, fmt.Errorf(
			"%w: generator does not support native tool calling",
			continuation.ErrInvalidRequest,
		)
	}
	started := time.Now()
	result, err := completer.Complete(ctx, request, sink)
	value := ModelCallTrace{
		Stage:          toolChatRequestStage(request),
		Request:        toolChatRequestSnapshot(request),
		Response:       toolChatResponseSnapshot(result),
		DurationMillis: time.Since(started).Milliseconds(),
	}
	if err != nil {
		value.Error = err.Error()
	}
	g.recorder.modelCall(value)
	return result, err
}

func toolChatRequestStage(request toolchat.Request) string {
	return requestStage(continuation.Request{Stops: request.Stops})
}

func toolChatRequestSnapshot(request toolchat.Request) RequestSnapshot {
	prompt, err := json.Marshal(struct {
		Messages          []toolchat.Message  `json:"messages"`
		Tools             []toolchat.Tool     `json:"tools,omitempty"`
		ToolChoice        toolchat.ToolChoice `json:"tool_choice,omitempty"`
		AssistantPrefix   string              `json:"assistant_prefix,omitempty"`
		ParallelToolCalls bool                `json:"parallel_tool_calls"`
	}{
		Messages:          request.Messages,
		Tools:             request.Tools,
		ToolChoice:        request.ToolChoice,
		AssistantPrefix:   request.AssistantPrefix,
		ParallelToolCalls: request.ParallelToolCalls,
	})
	if err != nil {
		prompt = []byte(`{"trace_error":"could not encode native Chat Completions request"}`)
	}
	return RequestSnapshot{
		Model:           request.Model,
		Prompt:          string(prompt),
		MaxOutputTokens: request.MaxOutputTokens,
		Stops:           append([]string(nil), request.Stops...),
		Sampling:        samplingSnapshot(request.Sampling),
	}
}

func toolChatResponseSnapshot(result toolchat.Result) ResponseSnapshot {
	text := result.Content
	if len(result.ToolCalls) > 0 {
		encoded, err := json.Marshal(result.ToolCalls)
		if err == nil {
			text = string(encoded)
		}
	}
	return ResponseSnapshot{
		Text:         text,
		FinishReason: result.FinishReason,
		Usage: UsageSnapshot{
			PromptTokens:     result.Usage.PromptTokens,
			CompletionTokens: result.Usage.CompletionTokens,
		},
	}
}

func requestStage(request continuation.Request) string {
	for _, stop := range request.Stops {
		switch stop {
		case "</route>":
			return "route"
		case "</answer>":
			return "answer"
		case "</tool_call>":
			return "decision"
		}
	}
	return "unknown"
}

func samplingSnapshot(sampling continuation.Sampling) SamplingSnapshot {
	return SamplingSnapshot{
		Temperature:      sampling.Temperature,
		TopK:             sampling.TopK,
		TopP:             sampling.TopP,
		PresencePenalty:  sampling.PresencePenalty,
		FrequencyPenalty: sampling.FrequencyPenalty,
		PenaltyDecay:     sampling.PenaltyDecay,
		Seed:             sampling.Seed,
	}
}

func requestSnapshot(request continuation.Request) RequestSnapshot {
	return RequestSnapshot{
		Model:           request.Model,
		Prompt:          request.Prompt,
		MaxOutputTokens: request.MaxOutputTokens,
		Stops:           append([]string(nil), request.Stops...),
		Sampling:        samplingSnapshot(request.Sampling),
	}
}

func responseSnapshot(result continuation.Result) ResponseSnapshot {
	return ResponseSnapshot{
		Text:         result.Text,
		FinishReason: result.FinishReason,
		Usage: UsageSnapshot{
			PromptTokens:     result.Usage.PromptTokens,
			CompletionTokens: result.Usage.CompletionTokens,
		},
	}
}

var _ continuation.Generator = (*recordingGenerator)(nil)
var _ toolchat.Completer = (*recordingGenerator)(nil)
