package agent

import (
	"context"
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// answerStageRunner scripts a turn that executes one call, repeats it (which
// forces the answer stage) and then keeps emitting tool calls.
func answerStageRunner(t *testing.T, outputs []string, prompts *[]string) *Runner {
	t.Helper()
	generations := 0
	executions := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			request continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			*prompts = append(*prompts, request.Prompt)
			result := continuation.Result{Text: outputs[generations], FinishReason: continuation.FinishStop}
			generations++
			return result, nil
		}),
		[]Tool{&countingEchoTool{calls: &executions}},
		Options{MaxSteps: 8, ProtocolRetries: 1},
	)
	if err != nil {
		t.Fatal(err)
	}
	return runner
}

const answerStageToolCall = `<tool_call>{"name":"counting_echo","arguments":{"value":"same"}}</tool_call>`

func TestAnswerStagePrefillsOpeningAfterRepeatedToolCalls(t *testing.T) {
	t.Parallel()
	var prompts []string
	runner := answerStageRunner(t, []string{
		answerStageToolCall, answerStageToolCall, // execute, then duplicate
		answerStageToolCall, answerStageToolCall, // answer stage: retry, then opener
		" the echo returned same.",
	}, &prompts)
	result, err := runner.Run(context.Background(), "Use echo once, then answer.")
	if err != nil {
		t.Fatalf("err = %v", err)
	}
	opener := answerOpener("Use echo once, then answer.")
	if !strings.HasSuffix(prompts[len(prompts)-1], opener) {
		t.Fatalf("last prompt does not end with the opener:\n%s", prompts[len(prompts)-1])
	}
	if result.AnswerFallback != AnswerFallbackOpener || !strings.Contains(result.Output, "the echo returned same") {
		t.Fatalf("fallback = %q output = %q", result.AnswerFallback, result.Output)
	}
	for _, prompt := range prompts[3:] {
		// Rejected answer-stage calls are not echoed into later prompts.
		if strings.Count(prompt, `"value":"same"`) > 2 {
			t.Fatalf("rejected call echoed back:\n%s", prompt)
		}
	}
}

func TestAnswerStageSummarizesWhenOpenerAlsoCallsTools(t *testing.T) {
	t.Parallel()
	var prompts []string
	runner := answerStageRunner(t, []string{
		answerStageToolCall, answerStageToolCall,
		answerStageToolCall, answerStageToolCall,
		" let me check again " + answerStageToolCall,
	}, &prompts)
	result, err := runner.Run(context.Background(), "Use echo once, then answer.")
	if err != nil {
		t.Fatalf("err = %v", err)
	}
	if result.AnswerFallback != AnswerFallbackSummary ||
		!strings.Contains(result.Output, "- counting_echo: returned a result") {
		t.Fatalf("fallback = %q output = %q", result.AnswerFallback, result.Output)
	}
}

func TestSalvageAnswerProse(t *testing.T) {
	t.Parallel()
	opener := "根据上面的工具结果，"
	for _, tc := range []struct{ in, want string }{
		{opener + "页面没有正文，无法确认 4 号线今天是否运行。<tool_call>{}</tool_call>", opener + "页面没有正文，无法确认 4 号线今天是否运行。"},
		{opener + "让我再搜索一次。<tool_call>{}</tool_call>", ""},
		{opener + "<tool_call>{}</tool_call>", ""},
		{"<think>x</think>" + opener + "搜索没有结果，没查到这个版本号。", opener + "搜索没有结果，没查到这个版本号。"},
	} {
		if got := salvageAnswerProse(tc.in, opener); got != tc.want {
			t.Fatalf("salvage(%q) = %q, want %q", tc.in, got, tc.want)
		}
	}
}

func TestAnswerFallbackSummaryText(t *testing.T) {
	t.Parallel()
	steps := []Step{
		{Tool: "web_search", ToolExecuted: true, ToolArguments: json.RawMessage(`{"query":"quillbrook-sdk"}`),
			ToolResult: json.RawMessage(`{"ok":true,"tool":"web_search","result":{"query":"quillbrook-sdk","results":[]}}`)},
		{Tool: "web_search", ToolExecuted: true, ToolArguments: json.RawMessage(`{"query":"quillbrook-sdk"}`),
			ToolResult: json.RawMessage(`{"ok":true,"tool":"web_search","result":{"query":"quillbrook-sdk","results":[]}}`)},
		{Tool: "web_search", ToolRejected: "duplicate_tool_call", ToolArguments: json.RawMessage(`{"query":"quillbrook-sdk"}`)},
		{Tool: "web_fetch", ToolExecuted: true, ToolArguments: json.RawMessage(`{"urls":["https://a.example/x"]}`),
			ToolResult: json.RawMessage(`{"ok":true,"tool":"web_fetch","result":{"pages":[{"url":"https://a.example/x","content":""}]}}`)},
		{Tool: "read_file", ToolExecuted: true, ToolArguments: json.RawMessage(`{"path":"notes.md"}`),
			ToolResult: json.RawMessage(`{"ok":false,"tool":"read_file","error":"file not found"}`)},
	}
	got := answerFallbackSummaryText("帮我查一下 quillbrook-sdk 的版本", steps)
	want := "这次没能直接给出回答。我查过的内容：\n" +
		"- web_search「quillbrook-sdk」：没有结果\n" +
		"- web_fetch「https://a.example/x」：页面没有正文\n" +
		"- read_file「notes.md」：出错（file not found）\n" +
		"没有查到能回答这个问题的信息。你可以换个说法再问，或者提供具体的网址或文件，我再查一次。"
	if got != want {
		t.Fatalf("summary =\n%s\nwant\n%s", got, want)
	}
	if violations := validateAnswer(got); len(violations) != 0 {
		t.Fatalf("summary violates the answer contract: %v", violations)
	}
	english := answerFallbackSummaryText("check the quillbrook-sdk version", steps[:1])
	for _, text := range []string{got, english} {
		if strings.Contains(text, "\n\n") {
			t.Fatalf("summary contains a blank line, which splits the RWKV block: %q", text)
		}
	}
}
