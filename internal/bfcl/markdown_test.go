package bfcl

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestRenderPromptPreservesFunctionAndMessageBytes(t *testing.T) {
	t.Parallel()
	function := json.RawMessage(`{"name":"math.factorial","description":"keep  spaces","parameters":{"type":"dict","properties":{"number":{"type":"integer"}}}}`)
	entry := Case{
		ID:        "simple_python_0",
		Messages:  []Message{{Role: "user", Content: "call it\n exactly  "}},
		Functions: []json.RawMessage{function},
	}
	prompt, err := RenderPrompt(entry, TierBaseline, TransportRWKVContinuation)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(prompt, string(function)) || !strings.Contains(prompt, "User: call it\n exactly  \n\n") {
		t.Fatalf("prompt did not preserve input bytes:\n%s", prompt)
	}
	if !strings.HasSuffix(prompt, "Assistant: ```json\n") {
		t.Fatalf("prompt suffix = %q", prompt)
	}
	if !strings.Contains(prompt, "arguments value must be a JSON object") {
		t.Fatalf("prompt lacks strict arguments guidance:\n%s", prompt)
	}
}

func TestParseMarkdownCallsAcceptsPrefilledAndCompleteFence(t *testing.T) {
	t.Parallel()
	for _, value := range []string{
		`{"name":"math.factorial","arguments":{"number":5}}`,
		"```json\n{\"name\":\"math.factorial\",\"arguments\":{\"number\":5}}\n```",
	} {
		calls, err := ParseMarkdownCalls(value)
		if err != nil {
			t.Fatal(err)
		}
		if len(calls) != 1 || calls[0].Name != "math.factorial" || calls[0].Arguments != `{"number":5}` {
			t.Fatalf("calls = %+v", calls)
		}
	}
}

func TestParseMarkdownCallsRejectsBaselineRepairs(t *testing.T) {
	t.Parallel()
	values := []string{
		`Here is the call: {"name":"tool","arguments":{}}`,
		`{"name":"tool","arguments":{},"extra":true}`,
		`{"name":"tool","arguments":{}} trailing`,
		"```json\n{\"name\":\"tool\",\"arguments\":{}}",
	}
	for _, value := range values {
		if _, err := ParseMarkdownCalls(value); err == nil {
			t.Fatalf("ParseMarkdownCalls(%q) unexpectedly succeeded", value)
		}
	}
}
