package agent

import (
	"encoding/json"
	"strings"

	"github.com/no22/RWKV-Agent/internal/inference"
)

func (protocol G1IFunctionProtocol) Correction(error) string {
	if protocol.Product {
		correction := "Either answer the user directly in ordinary Markdown, or return one fenced JSON function call with this shape: " +
			`{"name":"TOOL_NAME","arguments":{...}}.`
		if protocol.SemanticNoTool {
			correction += ` When no offered tool is needed, use {"name":"no_tool","arguments":{"reason":"brief complete user-facing response"}}; reason becomes the final reply.`
		}
		return correction
	}
	return `Return only one JSON function call with this shape: {"name":"TOOL_NAME","arguments":{...}}.`
}

func (G1IFunctionProtocol) RecordAction(action Action, _ string) string {
	payload, _ := json.Marshal(struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}{Name: action.Name, Arguments: action.Arguments})
	return "```json\n" + string(payload) + "\n```"
}

func (G1IFunctionProtocol) FormatToolResult(_ string, _ string, payload string) string {
	var result struct {
		OK     bool            `json:"ok"`
		Result json.RawMessage `json:"result"`
		Error  string          `json:"error"`
	}
	if json.Unmarshal([]byte(payload), &result) != nil {
		return payload
	}
	if !result.OK {
		return "ERROR: " + result.Error
	}
	var text string
	if json.Unmarshal(result.Result, &text) == nil {
		return text
	}
	return strings.TrimSpace(string(result.Result))
}

// G1IDeepToolAnchorSuffix is the exact byte sequence appended to the product
// fence when DeepToolAnchor is on. The compact spelling (no space after the
// colon) must match the JSON examples in Instructions: on 7B a single space
// here flips the model into stringified arguments.
const G1IDeepToolAnchorSuffix = `{"name":"`

func (protocol G1IFunctionProtocol) ToolCallPrefix() string {
	if !protocol.Product {
		return ""
	}
	if protocol.DeepToolAnchor {
		return "```json\n" + G1IDeepToolAnchorSuffix
	}
	return "```json\n"
}
func (G1IFunctionProtocol) PostToolReminder() string { return "" }
func (protocol G1IFunctionProtocol) PrepareAnswer(messages []Message, unverified []string, _ inference.ThinkingMode) ([]Message, string) {
	if protocol.Product {
		prepared := append([]Message(nil), messages...)
		instruction := "Tool execution is complete and tools are now unavailable. Answer the original current task directly in ordinary Markdown using the Function output above. Do not call another tool or repeat Function output."
		if len(unverified) > 0 {
			instruction += " The following providers could not be verified: " + strings.Join(unverified, ", ") + ". State those limitations instead of inventing values."
		}
		prepared = append(prepared, Message{Role: RoleUser, Content: instruction})
		return prepared, "Assistant:"
	}
	return messages, "Assistant:"
}
func (protocol G1IFunctionProtocol) Stops(GenerationStage) []string {
	if protocol.Product {
		return []string{"\n\nUser:", "\nUser:", "\nSystem:", "</s>"}
	}
	return []string{"```", "\n\nUser:", "\nUser:", "</s>"}
}

func (protocol G1IFunctionProtocol) stopsWithPrefix(stage GenerationStage, prefix string) []string {
	stops := protocol.Stops(stage)
	if protocol.Product && strings.HasPrefix(strings.TrimSpace(prefix), "```json") {
		return append([]string{"```"}, stops...)
	}
	return stops
}
