package agent

import (
	"context"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// scriptedGenerator returns one canned result per call and records requests.
type scriptedGenerator struct {
	results  []continuation.Result
	requests []continuation.Request
}

func (g *scriptedGenerator) Continue(
	_ context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	g.requests = append(g.requests, request)
	result := g.results[len(g.requests)-1]
	if sink != nil && result.Text != "" {
		if err := sink(continuation.Event{Kind: continuation.EventTextDelta, Text: result.Text}); err != nil {
			return result, err
		}
	}
	return result, nil
}

func stopped(text, stop string) continuation.Result {
	return continuation.Result{Text: text, FinishReason: continuation.FinishStop, Stop: stop}
}

func TestThinkStopResumesQuotedToolCall(t *testing.T) {
	generator := &scriptedGenerator{results: []continuation.Result{
		stopped(`>The contract says <tool_call>{"name":"...","arguments":{...}}`, "</tool_call>"),
		stopped(" so I list files.\n</think>\n<tool_call>{\"name\":\"list_files\",\"arguments\":{}}", "</tool_call>"),
	}}
	runner := &Runner{generator: generator}
	var streamed strings.Builder
	request := continuation.Request{Prompt: "System: s\n\nUser: q\n\nAssistant: <think", MaxOutputTokens: 4096}
	result, err := runner.continueThroughThinkStops(context.Background(), request, func(event continuation.Event) error {
		streamed.WriteString(event.Text)
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	want := `>The contract says <tool_call>{"name":"...","arguments":{...}}</tool_call> so I list files.` +
		"\n</think>\n<tool_call>{\"name\":\"list_files\",\"arguments\":{}}"
	if result.Text != want || streamed.String() != want {
		t.Fatalf("text = %q\nstreamed = %q", result.Text, streamed.String())
	}
	if result.Stop != "</tool_call>" || result.FinishReason != continuation.FinishStop {
		t.Fatalf("final stop = %q finish = %q", result.Stop, result.FinishReason)
	}
	if len(generator.requests) != 2 {
		t.Fatalf("calls = %d, want 2", len(generator.requests))
	}
	resumed := generator.requests[1]
	if resumed.Prompt != request.Prompt+`>The contract says <tool_call>{"name":"...","arguments":{...}}</tool_call>` {
		t.Fatalf("resume prompt tail = %q", resumed.Prompt[len(request.Prompt):])
	}
	if resumed.MaxOutputTokens >= request.MaxOutputTokens || resumed.MaxOutputTokens <= 0 {
		t.Fatalf("resume budget = %d", resumed.MaxOutputTokens)
	}
}

func TestThinkStopSpontaneousThinkUnderThinkingOff(t *testing.T) {
	generator := &scriptedGenerator{results: []continuation.Result{
		stopped(`<think>Format: <tool_call>{"name":"TOOL_NAME","arguments":{}}`, "</tool_call>"),
		stopped(" ok</think>\n<tool_call>{\"name\":\"read_file\",\"arguments\":{}}", "</tool_call>"),
	}}
	runner := &Runner{generator: generator}
	result, err := runner.continueThroughThinkStops(context.Background(),
		continuation.Request{Prompt: "User: q\n\nAssistant:", MaxOutputTokens: 2048}, nil)
	if err != nil || len(generator.requests) != 2 || !strings.HasSuffix(result.Text, `"arguments":{}}`) {
		t.Fatalf("calls = %d text = %q err = %v", len(generator.requests), result.Text, err)
	}
}

func TestThinkStopLeavesOrdinaryStopsAlone(t *testing.T) {
	cases := map[string]struct {
		prompt string
		result continuation.Result
	}{
		"think closed":    {"Assistant: <think", stopped(">done</think>\n<tool_call>{}", "</tool_call>")},
		"no think":        {"Assistant:", stopped("<tool_call>{}", "</tool_call>")},
		"role label stop": {"Assistant: <think", stopped(">reasoning", "\nUser:")},
		"real call inside open think": {
			"Assistant: <think", stopped(">I will list.\n<tool_call>{\"name\":\"list_files\",\"arguments\":{}}", "</tool_call>"),
		},
		"answer stop": {"Assistant: <think", stopped(">x <answer>y", "</answer>")},
		"eos":         {"Assistant: <think", continuation.Result{Text: ">x", FinishReason: continuation.FinishStop}},
		"budget":      {"Assistant: <think", continuation.Result{Text: ">x", FinishReason: continuation.FinishLength}},
		"earlier turn closed think only": {
			"Assistant: <think>a</think>x\n\nUser: y\n\nAssistant:", stopped("<tool_call>{}", "</tool_call>"),
		},
	}
	for name, tc := range cases {
		generator := &scriptedGenerator{results: []continuation.Result{tc.result}}
		runner := &Runner{generator: generator}
		result, err := runner.continueThroughThinkStops(context.Background(),
			continuation.Request{Prompt: tc.prompt, MaxOutputTokens: 512}, nil)
		if err != nil || len(generator.requests) != 1 || result.Text != tc.result.Text {
			t.Fatalf("%s: calls = %d text = %q err = %v", name, len(generator.requests), result.Text, err)
		}
	}
}

func TestThinkStopRespectsBudgetAndResumeCap(t *testing.T) {
	long := ">" + strings.Repeat("x", 3000) + "<tool_call>"
	generator := &scriptedGenerator{results: []continuation.Result{stopped(long, "</tool_call>")}}
	runner := &Runner{generator: generator}
	result, err := runner.continueThroughThinkStops(context.Background(),
		continuation.Request{Prompt: "Assistant: <think", MaxOutputTokens: 1000}, nil)
	if err != nil || len(generator.requests) != 1 || result.FinishReason != continuation.FinishLength {
		t.Fatalf("calls = %d finish = %q err = %v", len(generator.requests), result.FinishReason, err)
	}

	loop := make([]continuation.Result, maxThinkStopResumes+1)
	for index := range loop {
		loop[index] = stopped("<tool_call>", "</tool_call>")
	}
	generator = &scriptedGenerator{results: loop}
	runner = &Runner{generator: generator}
	if _, err := runner.continueThroughThinkStops(context.Background(),
		continuation.Request{Prompt: "Assistant: <think", MaxOutputTokens: 100000}, nil); err != nil {
		t.Fatal(err)
	}
	if len(generator.requests) != maxThinkStopResumes+1 {
		t.Fatalf("calls = %d, want %d", len(generator.requests), maxThinkStopResumes+1)
	}
}
