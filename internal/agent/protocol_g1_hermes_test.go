package agent

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func hermesProtocol(t *testing.T, profile string) (G1Protocol, wire.Spec) {
	t.Helper()
	spec, _, err := wire.Resolve(profile)
	if err != nil {
		t.Fatal(err)
	}
	options, err := OptionsWithWire(Options{}, spec)
	if err != nil {
		t.Fatal(err)
	}
	protocol, ok := options.Protocol.(G1Protocol)
	if !ok || !protocol.Hermes || !protocol.AlignQwen36 {
		t.Fatalf("%s protocol = %#v", profile, options.Protocol)
	}
	return protocol, spec
}

func TestHermesTrajectoryShape(t *testing.T) {
	protocol, _ := hermesProtocol(t, "g1k+hermes")
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read <a> file.",
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
		"You are a function calling AI model. You are provided with function signatures within <tools> </tools> XML tags. ",
		"Here are the available tools:\n<tools>\n[{\"type\": \"function\", \"function\": {\"name\": \"read_file\", \"description\": \"Read <a> file.\", \"parameters\": {\"type\": \"object\", \"properties\": {\"path\": {\"type\": \"string\"}}, \"required\": [\"path\"]}}}, ",
		`"name": "calculator"`,
		`"name": "no_tool"`,
		"]\n</tools>\nFor each function call return a JSON object",
		"Example:\n<tool_call>\n{'name': <function-name>,'arguments': <args-dict>}\n</tool_call>",
	} {
		if !strings.Contains(prompt, want) {
			t.Errorf("prompt lacks %q", want)
		}
	}
	if strings.Contains(prompt, "local-first assistant") {
		t.Errorf("hermes prompt still carries the product instructions")
	}

	recorded := protocol.RecordAction(Action{Type: "tool", Name: "read_file", Arguments: json.RawMessage(`{"path":"a, b: c.txt","max":2}`)}, "")
	if recorded != "<think>\n</think>\n<tool_call>\n{\"name\": \"read_file\", \"arguments\": {\"path\": \"a, b: c.txt\", \"max\": 2}}\n</tool_call>" {
		t.Errorf("recorded call = %q", recorded)
	}
	if got := protocol.RecordAction(Action{Type: ActionTypeFinal}, " <think>\nx\n</think>\n42"); got != "<think>\n</think>\n42" {
		t.Errorf("recorded answer = %q", got)
	}
	if got := protocol.FormatToolResult("read_file", "call_1", `{"ok":true,"result":{"z":1,"a":"<b>"}}`); got != "<tool_response>\n{\"tool_call_id\": \"call_1\", \"name\": \"read_file\", \"content\": {\"ok\": true, \"result\": {\"z\": 1, \"a\": \"<b>\"}}}\n</tool_response>" {
		t.Errorf("tool result = %q", got)
	}
	if got := protocol.FormatToolResult("calculator", "call_2", "not json"); !strings.Contains(got, `"content": "not json"`) {
		t.Errorf("text tool result = %q", got)
	}
}

func TestHermesThinkPrefillFrame(t *testing.T) {
	_, spec := hermesProtocol(t, "g1k+hermes+hermes-think")
	frame := spec.DecisionFrame(wire.DecisionState{Inspect: true})
	if frame.Text != "<think>\n</think>\n" || !frame.Inject {
		t.Fatalf("frame = %#v", frame)
	}
	if _, _, err := wire.Resolve("g1k+hermes-think"); err == nil {
		t.Fatalf("hermes-think without align=hermes must be rejected")
	}
}

func TestHermesParsesPaddedCall(t *testing.T) {
	protocol, _ := hermesProtocol(t, "g1k+hermes")
	action, err := protocol.Parse(" <think>\nreasoning\n</think>\n<tool_call>\n{\"name\": \"read_file\", \"arguments\": {\"path\": \"a.txt\"}}\n</tool_call>", "stop")
	if err != nil || action.Type != ActionTypeTool || action.Name != "read_file" {
		t.Fatalf("parse = %#v, %v", action, err)
	}
}
