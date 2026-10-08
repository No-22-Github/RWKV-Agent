package agent

import (
	"context"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestPreviewAnswerTextHoldsAmbiguousOutput(t *testing.T) {
	t.Parallel()
	cases := []struct {
		output string
		want   string
		ok     bool
	}{
		{"你好，我是", "你好，我是", true},
		{"<tool_call>{\"name\"", "", false},
		{"<tool_", "", false},
		{"<", "", false},
		{"```json\n{\"name\"", "", false},
		{"{\"name\":\"no_tool\"", "", false},
		{"<think>still thinking", "", false},
		{"<think>done</think>\n答案", "答案", true},
		{"<answer>答案在", "答案在", true},
		{"<answer>答案</answer>", "答案", true},
		{"<answer>答案</ans", "答案", true},
		{"我来读一下文件：\n<tool_call>{", "我来读一下文件：", true},
		{"我来读一下文件：\n```json\n{\"name\"", "我来读一下文件：", true},
		{"我来读一下：\n```", "我来读一下：", true},
		{"示例：\n```python\nprint(1)\n```", "示例：\n```python\nprint(1)\n```", true},
		{"第一行\n\n", "第一行", true},
	}
	for _, test := range cases {
		got, ok := previewAnswerText(test.output)
		if got != test.want || ok != test.ok {
			t.Errorf("previewAnswerText(%q) = %q, %v; want %q, %v", test.output, got, ok, test.want, test.ok)
		}
	}
}

// chunkedGenerator replays scripted responses through the sink a few runes at
// a time, the way a streaming provider delivers them.
func chunkedGenerator(responses []string) continuation.Generator {
	index := 0
	return continuation.GenerateFunc(func(
		_ context.Context,
		_ continuation.Request,
		sink continuation.EventSink,
	) (continuation.Result, error) {
		response := []rune(responses[index])
		index++
		for start := 0; start < len(response); start += 3 {
			end := min(start+3, len(response))
			if sink != nil {
				if err := sink(continuation.Event{Kind: continuation.EventTextDelta, Text: string(response[start:end])}); err != nil {
					return continuation.Result{}, err
				}
			}
		}
		return continuation.Result{Text: string(response), FinishReason: continuation.FinishStop}, nil
	})
}

// streamedAnswer folds answer events the way a live view would.
func streamedAnswer(events []Event) (text string, resets int) {
	for _, event := range events {
		switch event.Kind {
		case EventAnswerDelta:
			text += event.Text
		case EventAnswerReset:
			text = ""
			resets++
		}
	}
	return text, resets
}

func TestRunnerStreamsFinalAnswerAfterToolStep(t *testing.T) {
	t.Parallel()
	runner, err := NewRunner(
		chunkedGenerator([]string{
			`<tool_call>{"name":"echo","arguments":{"value":"ping"}}</tool_call>`,
			"Echo 返回了 ping。",
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 3, Protocol: G1Protocol{}, Renderer: RWKVChatRenderer{}},
	)
	if err != nil {
		t.Fatal(err)
	}
	var events []Event
	result, err := runner.RunWithObserver(context.Background(), "Check the echo tool", func(event Event) {
		events = append(events, event)
	})
	if err != nil {
		t.Fatal(err)
	}
	text, resets := streamedAnswer(events)
	if text != result.Output || text == "" || resets != 0 {
		t.Fatalf("streamed %q with %d resets, output %q; events = %+v", text, resets, result.Output, events)
	}
	for _, event := range events {
		if event.Kind == EventAnswerDelta && strings.Contains(event.Text, "tool_call") {
			t.Fatalf("tool envelope leaked into the preview: %+v", event)
		}
	}
}

func TestRunnerRetractsProseBeforeFencedCall(t *testing.T) {
	t.Parallel()
	runner, err := NewRunner(
		chunkedGenerator([]string{
			"I will search first.\n```json\n{\"name\":\"web_search\",\"arguments\":{\"query\":\"RWKV\"}}\n```",
			`{"name":"submit","arguments":{"answer":"recovered"}}`,
		}),
		[]Tool{retryingWebTool{}, submitTestTool{}},
		g1RunnerOptions(),
	)
	if err != nil {
		t.Fatal(err)
	}
	var events []Event
	result, err := runner.RunWithObserver(context.Background(), "Search for RWKV.", func(event Event) {
		events = append(events, event)
	})
	if err != nil {
		t.Fatal(err)
	}
	text, resets := streamedAnswer(events)
	if result.Output != "recovered" || text != "" || resets != 1 {
		t.Fatalf("streamed %q with %d resets, output %q", text, resets, result.Output)
	}
	retracted := false
	for _, event := range events {
		if event.Kind == EventAnswerReset {
			retracted = true
		}
		if event.Kind == EventToolStart && !retracted {
			t.Fatal("the prose preview must be retracted before the tool runs")
		}
	}
}

func TestRunnerStreamPreviewHidesWithheldThinkOpening(t *testing.T) {
	t.Parallel()
	for _, mode := range []inference.ThinkingMode{inference.ThinkingFast, inference.ThinkingFull} {
		response := ">你好！有什么我可以帮你的吗？"
		if mode == inference.ThinkingFull {
			response = "><think></think>你好！有什么我可以帮你的吗？"
		}
		runner, err := NewRunner(
			chunkedGenerator([]string{response}),
			[]Tool{echoTool{}},
			Options{MaxSteps: 2, Protocol: G1Protocol{}, Renderer: RWKVChatRenderer{ThinkingMode: mode}},
		)
		if err != nil {
			t.Fatal(err)
		}
		var events []Event
		result, err := runner.RunWithObserver(context.Background(), "你好", func(event Event) {
			events = append(events, event)
		})
		if err != nil {
			t.Fatal(err)
		}
		if text, _ := streamedAnswer(events); text != result.Output {
			t.Fatalf("%s: streamed %q, output %q", mode, text, result.Output)
		}
	}
}

func TestRunnerWithoutObserverPassesNoSink(t *testing.T) {
	t.Parallel()
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			sink continuation.EventSink,
		) (continuation.Result, error) {
			if sink != nil {
				t.Error("a run without observers should not stream")
			}
			return continuation.Result{Text: "ok", FinishReason: continuation.FinishStop}, nil
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 2, Protocol: G1Protocol{}, Renderer: RWKVChatRenderer{}},
	)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := runner.Run(context.Background(), "hi"); err != nil {
		t.Fatal(err)
	}
}
