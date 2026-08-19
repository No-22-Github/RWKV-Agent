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

func TestRenderPromptUsesSameProtocolAcrossContinuationTransports(t *testing.T) {
	t.Parallel()
	entry := Case{
		ID:        "simple_python_0",
		Messages:  []Message{{Role: "user", Content: "call it"}},
		Functions: []json.RawMessage{json.RawMessage(`{"name":"tool","parameters":{"type":"dict"}}`)},
	}
	rwkvPrompt, err := RenderPrompt(entry, TierBaseline, TransportRWKVContinuation)
	if err != nil {
		t.Fatal(err)
	}
	chatPrompt, err := RenderPrompt(entry, TierBaseline, TransportChatCompletionsWrapped)
	if err != nil {
		t.Fatal(err)
	}
	if rwkvPrompt != chatPrompt {
		t.Fatalf("transport changed Markdown protocol\nrwkv=%q\nchat=%q", rwkvPrompt, chatPrompt)
	}
}

func TestRenderPromptPreservesIrrelevanceAssistantHistoryAndAllowsNoCall(t *testing.T) {
	t.Parallel()
	entry := Case{
		ID:       "live_irrelevance_125-11-0",
		Category: "live_irrelevance",
		Messages: []Message{
			{Role: "user", Content: "first"},
			{Role: "assistant", Content: "prior answer"},
			{Role: "user", Content: "follow up"},
		},
	}
	prompt, err := RenderPrompt(entry, TierBaseline, TransportRWKVContinuation)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(prompt, "Assistant: prior answer\n\n") ||
		!strings.Contains(prompt, "If no listed tool is relevant, return no function call.") {
		t.Fatalf("irrelevance prompt = %q", prompt)
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

func TestParseMarkdownCallsAcceptsParallelArray(t *testing.T) {
	t.Parallel()
	calls, err := ParseMarkdownCalls(`[{"name":"play","arguments":{"artist":"Taylor Swift"}},{"name":"play","arguments":{"artist":"Maroon 5"}}]`)
	if err != nil {
		t.Fatal(err)
	}
	if len(calls) != 2 || calls[0].Name != "play" || calls[1].Arguments != `{"artist":"Maroon 5"}` {
		t.Fatalf("calls = %+v", calls)
	}
}

func TestRenderPromptRequestsParallelArray(t *testing.T) {
	t.Parallel()
	entry := Case{
		ID: "parallel_0", Category: "parallel", Messages: []Message{{Role: "user", Content: "play both"}},
		Functions: []json.RawMessage{json.RawMessage(`{"name":"play","parameters":{"type":"dict"}}`)},
	}
	prompt, err := RenderPrompt(entry, TierBaseline, TransportChatCompletionsWrapped)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(prompt, "JSON array of function calls") {
		t.Fatalf("prompt = %q", prompt)
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

func TestRWKVWireCompatPreservesStrictOutput(t *testing.T) {
	t.Parallel()
	value := `{"name":"math.factorial","arguments":{"number":5}}`
	strict, err := ParseMarkdownCalls(value)
	if err != nil {
		t.Fatal(err)
	}
	outcome, err := ParseMarkdownCallsWithMode(value, compatFunctions("math.factorial", "number"), ParserRWKVWireCompatV1)
	if err != nil {
		t.Fatal(err)
	}
	if len(outcome.Repairs) != 0 || len(outcome.Calls) != 1 ||
		outcome.Calls[0] != strict[0] {
		t.Fatalf("outcome = %+v strict = %+v", outcome, strict)
	}
}

func TestRWKVWireCompatNormalizesKnownEnvelopeVariants(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name      string
		value     string
		functions []json.RawMessage
		arguments string
		repairs   []string
	}{
		{
			name:      "stringified arguments",
			value:     `{"name":"math.factorial","arguments":"{\"number\":5}"}`,
			functions: compatFunctions("math.factorial", "number"),
			arguments: `{"number":5}`,
			repairs:   []string{RepairArgumentsUnwrapped},
		},
		{
			name:      "call id metadata",
			value:     `{"name":"math.factorial","arguments":"{\"number\":5}","id":"call_1"}`,
			functions: compatFunctions("math.factorial", "number"),
			arguments: `{"number":5}`,
			repairs:   []string{RepairArgumentsUnwrapped, RepairCallIDDropped},
		},
		{
			name:      "misplaced schema argument",
			value:     `{"name":"poker_game_winner","arguments":"{\"players\":[\"Alex\"]}","type":"Texas Holdem"}`,
			functions: compatFunctions("poker_game_winner", "players", "type"),
			arguments: `{"players":["Alex"],"type":"Texas Holdem"}`,
			repairs:   []string{RepairArgumentsUnwrapped, "top_level_argument_moved:type"},
		},
		{
			name:      "id is a schema argument",
			value:     `{"name":"lookup","arguments":"{}","id":"business-id"}`,
			functions: compatFunctions("lookup", "id"),
			arguments: `{"id":"business-id"}`,
			repairs:   []string{RepairArgumentsUnwrapped, "top_level_argument_moved:id"},
		},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			outcome, err := ParseMarkdownCallsWithMode(test.value, test.functions, ParserRWKVWireCompatV1)
			if err != nil {
				t.Fatal(err)
			}
			if len(outcome.Calls) != 1 || outcome.Calls[0].Arguments != test.arguments ||
				strings.Join(outcome.Repairs, ",") != strings.Join(test.repairs, ",") {
				t.Fatalf("outcome = %+v", outcome)
			}
		})
	}
}

func TestRWKVWireCompatRejectsSemanticAndRecursiveRepairs(t *testing.T) {
	t.Parallel()
	functions := compatFunctions("tool", "value")
	values := []string{
		`{"name":"other","arguments":"{\"value\":1}"}`,
		`{"name":"tool","arguments":"\"{\\\"value\\\":1}\""}`,
		`{"name":"tool","arguments":"{\"value\":1}","unknown":true}`,
		`{"name":"tool","arguments":"{\"value\":1}","value":2}`,
		`{"name":"tool","arguments":"{\"value\":1}","id":7}`,
		`Here is the call: {"name":"tool","arguments":"{\"value\":1}"}`,
	}
	for _, value := range values {
		if _, err := ParseMarkdownCallsWithMode(value, functions, ParserRWKVWireCompatV1); err == nil {
			t.Fatalf("compat parser unexpectedly accepted %q", value)
		}
	}
}

func compatFunctions(name string, parameters ...string) []json.RawMessage {
	properties := make(map[string]map[string]string, len(parameters))
	for _, parameter := range parameters {
		properties[parameter] = map[string]string{"type": "string"}
	}
	encoded, err := json.Marshal(map[string]any{
		"name": name,
		"parameters": map[string]any{
			"type":       "dict",
			"properties": properties,
		},
	})
	if err != nil {
		panic(err)
	}
	return []json.RawMessage{encoded}
}
