package agent

import (
	"context"
	"strings"
	"testing"
	"time"
)

func TestPreviewCall(t *testing.T) {
	content := strings.Repeat("x", 5000)
	cases := []struct {
		name   string
		output string
		ok     bool
		tool   string
		target string
	}{
		{"thinking only", "<think>should I write it", false, "", ""},
		{"name not closed", "<think>ok</think>\n<tool_call>\n{\"name\": \"write_fi", false, "", ""},
		{"name before target", "<think>ok</think>\n<tool_call>\n{\"name\": \"write_file\", \"arguments\": {\"path\": \"repo", true, "write_file", ""},
		{"target closed", "<think>ok</think>\n<tool_call>\n{\"name\": \"write_file\", \"arguments\": {\"path\": \"report.html\", \"content\": \"" + content, true, "write_file", "report.html"},
		{"prose then call", "Let me check.\n<tool_call>\n{\"name\": \"web_search\", \"arguments\": {\"query\": \"天气\"}}", true, "web_search", "天气"},
		{"fenced", "```json\n{\"name\": \"read_file\", \"arguments\": {\"path\": \"a\\\"b.md\"}}", true, "read_file", "a\"b.md"},
		{"plain answer", "The answer is \"name\": \"x\"", false, "", ""},
	}
	for _, tc := range cases {
		call, ok := previewCall(tc.output)
		if ok != tc.ok || call.tool != tc.tool || call.target != tc.target {
			t.Errorf("%s: got %+v %v, want tool=%q target=%q ok=%v", tc.name, call, ok, tc.tool, tc.target, tc.ok)
		}
	}
	big, _ := previewCall("<tool_call>{\"name\": \"write_file\", \"arguments\": {\"path\": \"a\", \"content\": \"" + content)
	if len(big.body) < 5000 {
		t.Errorf("body = %d bytes, want the call text so far", len(big.body))
	}
}

func TestCallPreviewThrottle(t *testing.T) {
	last := callPreview{tool: "write_file", target: "a", body: "abc"}
	grown := callPreview{tool: "write_file", target: "a", body: "abcd"}
	if grown.worthSending(last, 20*time.Millisecond) {
		t.Error("growth inside the interval should be held back")
	}
	if !grown.worthSending(last, callPreviewInterval) {
		t.Error("growth after the interval should be sent")
	}
	if last.worthSending(last, time.Second) {
		t.Error("an unchanged call should not be resent")
	}
	if !(callPreview{tool: "write_file", target: "b", body: "abc"}).worthSending(last, 0) {
		t.Error("a new target should always be sent")
	}
}

func TestRunnerPreviewsCallWhileGenerating(t *testing.T) {
	t.Parallel()
	value := strings.Repeat("p", 3000)
	runner, err := NewRunner(
		chunkedGenerator([]string{
			`<tool_call>{"name":"echo","arguments":{"value":"` + value + `"}}</tool_call>`,
			"done",
		}),
		[]Tool{echoTool{}},
		Options{MaxSteps: 3, Protocol: G1Protocol{}, Renderer: RWKVChatRenderer{}, TokenCount: func(text string) int { return len(text) / 4 }},
	)
	if err != nil {
		t.Fatal(err)
	}
	var previews []Event
	if _, err := runner.RunWithObserver(context.Background(), "echo", func(event Event) {
		if event.Kind == EventCallPreview {
			previews = append(previews, event)
		}
	}); err != nil {
		t.Fatal(err)
	}
	if len(previews) == 0 || previews[0].Tool != "echo" || previews[0].Step != 1 {
		t.Fatalf("previews = %+v, want echo named during step 1", previews)
	}
	// The test generator streams faster than callPreviewInterval, so only the
	// naming preview is guaranteed; it must still carry a count.
	if previews[0].Tokens <= 0 {
		t.Fatalf("previews = %+v, want a token count", previews)
	}
}
