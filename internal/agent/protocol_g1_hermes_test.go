package agent

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func hermesProtocol(t *testing.T) G1Protocol {
	t.Helper()
	spec, _, err := wire.Resolve("g1k+hermes")
	if err != nil {
		t.Fatal(err)
	}
	options, err := OptionsWithWire(Options{}, spec)
	if err != nil {
		t.Fatal(err)
	}
	protocol, ok := options.Protocol.(G1Protocol)
	if !ok || !protocol.Hermes || !protocol.AlignQwen36 {
		t.Fatalf("g1k+hermes protocol = %#v", options.Protocol)
	}
	return protocol
}

func TestHermesRendersFunctionSchemasAndPaddedTags(t *testing.T) {
	protocol := hermesProtocol(t)
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read a file.",
		Arguments:   `{"path":"relative path"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}`),
	}, {
		Name:        "calculator",
		Description: "Evaluate arithmetic.",
		Arguments:   `{"expression":"arithmetic expression"}`,
	}}
	prompt := protocol.Instructions(specs, inference.ThinkingOff)
	if testing.Verbose() {
		t.Log("\n" + prompt)
	}
	for _, want := range []string{
		"# Tools\n\nYou may call one or more functions",
		`<tools>` + "\n" + `{"type": "function", "function": {"name": "read_file", "description": "Read a file.", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}}`,
		`"name": "calculator"`,
		`"parameters": {"properties": {"expression": {"description": "arithmetic expression"}}, "type": "object"}`,
		`"name": "no_tool"`,
		"</tools>\n\nFor each function call",
		"<tool_call>\n{\"name\": <function-name>, \"arguments\": <args-json-object>}\n</tool_call>",
	} {
		if !strings.Contains(prompt, want) {
			t.Errorf("prompt lacks %q", want)
		}
	}
	if strings.Contains(prompt, `"arguments":{"path"`) {
		t.Errorf("hermes prompt still carries the flat qwen36 catalog")
	}

	recorded := protocol.RecordAction(Action{Type: "tool", Name: "read_file", Arguments: json.RawMessage(`{"path":"a, b: c.txt"}`)}, "")
	if recorded != "<tool_call>\n{\"name\": \"read_file\", \"arguments\": {\"path\": \"a, b: c.txt\"}}\n</tool_call>" {
		t.Errorf("recorded call = %q", recorded)
	}
	if got := protocol.FormatToolResult("", "", `{"ok":true}`); got != "<tool_response>\n{\"ok\":true}\n</tool_response>" {
		t.Errorf("tool result = %q", got)
	}
}

func TestHermesParsesPaddedCall(t *testing.T) {
	protocol := hermesProtocol(t)
	action, err := protocol.Parse(" <think>\nreasoning\n</think>\n<tool_call>\n{\"name\": \"read_file\", \"arguments\": {\"path\": \"a.txt\"}}\n</tool_call>", "stop")
	if err != nil || action.Type != ActionTypeTool || action.Name != "read_file" {
		t.Fatalf("parse = %#v, %v", action, err)
	}
}
