package agent

import (
	"encoding/json"
	"fmt"
	"io"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

const SemanticNoToolName = "no_tool"

func looksLikeG1FunctionFence(value string) bool {
	candidate := strings.TrimSpace(value)
	if !strings.HasPrefix(candidate, "```json") {
		return false
	}
	body := strings.TrimSpace(strings.TrimPrefix(candidate, "```json"))
	closed := false
	if index := strings.Index(body, "```"); index >= 0 {
		body = strings.TrimSpace(body[:index])
		closed = true
	}
	if !closed {
		return true
	}
	if !strings.HasPrefix(body, "{") {
		return false
	}
	for _, marker := range []string{`"name"`, `"command"`, `"cmd"`, `"tool"`, `"function"`} {
		if strings.Contains(body, marker) {
			return true
		}
	}
	return false
}

// callEnvelopeKeys are the keys a tool call is spelled with inside a fenced
// envelope. A fence is framing only when its body is a JSON object carrying
// one of them; every other fence is answer content.
var callEnvelopeKeys = []string{"name", "arguments", "function", "tool", "tool_calls", "command", "cmd"}

// fencedToolCall returns the JSON payload of a fenced tool-call envelope
// anywhere in value, and whether one was found.
//
// The md-fence transcript wraps a tool call in a ``` or ```json fence, and a
// model may put the envelope after a line of prose ("I will read the file:").
// Only a fence whose body starts with "{" and spells a call counts: a fence
// around a table, a CSV block or a code sample is answer content and must
// survive verbatim. Before harness v22 the parser dropped everything from the
// first fence on, which silently truncated answers that ended with a fenced
// block (and lost a fenced call that followed prose).
func fencedToolCall(value string) (string, bool) {
	for _, opener := range []string{"```json", "```"} {
		for search := 0; search < len(value); {
			index := strings.Index(value[search:], opener)
			if index < 0 {
				break
			}
			start := search + index
			search = start + len(opener)
			body := strings.TrimLeft(value[start+len(opener):], " \t\r\n")
			if !strings.HasPrefix(body, "{") {
				continue
			}
			if end := strings.Index(body, "```"); end >= 0 {
				body = body[:end]
			}
			payload := strings.TrimSpace(body)
			if fencedBodyIsToolCall(payload) {
				return payload, true
			}
		}
	}
	return "", false
}

// fencedBodyIsToolCall reports whether a fence body is a tool-call envelope.
// A body that is broken JSON while still spelling a call key counts: a
// malformed call must fail the protocol, not quietly turn into an answer made
// of the surrounding prose.
func fencedBodyIsToolCall(payload string) bool {
	var object map[string]json.RawMessage
	if json.Unmarshal([]byte(payload), &object) == nil {
		for _, key := range callEnvelopeKeys {
			if _, ok := object[key]; ok {
				return true
			}
		}
		return false
	}
	for _, key := range callEnvelopeKeys {
		if strings.Contains(payload, `"`+key+`"`) {
			return true
		}
	}
	return false
}

// unwrapLeadingFence strips a leading fence opener and cuts at the next
// fence. It is the pre-v22 unwrapping, kept for the two shapes that still
// have to fail the protocol the way they always did: a malformed leading
// fence in the product transcript, and every non-product caller, whose
// envelope is a fence without a body the caller can inspect.
func unwrapLeadingFence(candidate string) string {
	candidate = strings.TrimPrefix(candidate, "```json")
	candidate = strings.TrimPrefix(candidate, "```")
	candidate = strings.TrimSpace(candidate)
	if index := strings.Index(candidate, "```"); index >= 0 {
		candidate = strings.TrimSpace(candidate[:index])
	}
	return candidate
}

// standaloneTextAction is the terminal path for a response that carries no
// tool call: a final answer, an output-token-limit abort, or a protocol error
// when the response is empty.
func standaloneTextAction(candidate string, finish continuation.FinishReason) (Action, error) {
	if finish == continuation.FinishLength {
		return Action{}, ErrOutputTokenLimit
	}
	if candidate == "" {
		return Action{}, fmt.Errorf("%w: empty G1 function response", ErrProtocol)
	}
	return Action{Type: ActionTypeFinal, Content: candidate}, nil
}

func (protocol G1FunctionProtocol) Parse(value string, finish continuation.FinishReason) (Action, error) {
	candidate := strings.TrimSpace(value)
	repairs := &repairLog{}
	originalFailure := ProtocolFailureClass("")
	markOriginalFailure := func(class ProtocolFailureClass) {
		if originalFailure == "" {
			originalFailure = class
		}
	}
	markRepair := func(repair wire.Repair, class ProtocolFailureClass) {
		repairs.mark(repair)
		markOriginalFailure(class)
	}
	if index := strings.LastIndex(candidate, "</think>"); index >= 0 {
		candidate = strings.TrimSpace(candidate[index+len("</think>"):])
		markRepair(wire.RepairThinkStripped, ProtocolFailureToolEnvelopeMissing)
	}
	// Markdown fences are handled after the envelopes below: the product
	// transcript wraps a call in a fence, but a fence is framing only when it
	// wraps one (see fencedToolCall).
	if start := strings.Index(candidate, "<tool_calls>"); start >= 0 {
		body := candidate[start+len("<tool_calls>"):]
		if end := strings.Index(body, "</tool_calls>"); end >= 0 {
			body = body[:end]
		}
		var calls []json.RawMessage
		if err := json.Unmarshal([]byte(strings.TrimSpace(body)), &calls); err != nil || len(calls) != 1 {
			if err != nil {
				return Action{}, fmt.Errorf("%w: decode G1 tool_calls: %v", ErrToolJSONDecode, err)
			}
			return Action{}, fmt.Errorf("%w: G1 tool_calls must contain exactly one call", ErrToolShapeInvalid)
		}
		candidate = string(calls[0])
		markRepair(wire.RepairArrayEnvelope, ProtocolFailureToolEnvelopeMissing)
	} else if start := strings.Index(candidate, "<tool_call>"); start >= 0 {
		candidate = candidate[start+len("<tool_call>"):]
		if end := strings.Index(candidate, "</tool_call>"); end >= 0 {
			candidate = candidate[:end]
		}
		candidate = strings.TrimSpace(candidate)
		markRepair(wire.RepairEnvelopeRecovered, ProtocolFailureToolEnvelopeMissing)
	}
	if protocol.Product {
		// A fence is framing only when it wraps a tool call. Any other fence
		// belongs to the answer, which is returned whole: the product
		// transcript teaches models to answer in ordinary Markdown, so a
		// fenced table or code block in a final answer is expected output, not
		// a malformed envelope (harness v22).
		if payload, ok := fencedToolCall(candidate); ok {
			candidate = payload
		} else if looksLikeG1FunctionFence(candidate) {
			// An unterminated ```json fence with no object body: a call the
			// model failed to finish. Keep the pre-v22 unwrapping so it still
			// fails the protocol rather than turning into an answer.
			candidate = unwrapLeadingFence(candidate)
		} else if !strings.HasPrefix(candidate, "{") {
			return standaloneTextAction(candidate, finish)
		}
	} else {
		candidate = unwrapLeadingFence(candidate)
	}
	if !strings.HasPrefix(candidate, "{") {
		return standaloneTextAction(candidate, finish)
	}
	repaired := repairG1FunctionJSON(candidate)
	var call struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}
	var object map[string]json.RawMessage
	decoder := json.NewDecoder(strings.NewReader(repaired))
	if err := decoder.Decode(&call); err != nil {
		return Action{}, fmt.Errorf("%w: decode G1 function call: %v", ErrToolJSONDecode, err)
	}
	_ = json.Unmarshal([]byte(repaired), &object)
	if repaired != candidate {
		markRepair(wire.RepairJSONRepaired, ProtocolFailureToolJSONDecode)
	}
	if function, ok := rawJSONObject(object["function"]); ok {
		if name := rawJSONString(function["name"]); call.Name == "" && name != "" {
			call.Name = name
			markRepair(wire.RepairFunctionWrapper, ProtocolFailureToolShapeInvalid)
		}
		if len(call.Arguments) == 0 {
			call.Arguments = firstRaw(function, "arguments", "args", "parameters")
			markRepair(wire.RepairFunctionWrapper, ProtocolFailureToolShapeInvalid)
		}
	}
	if call.Name == "" {
		for _, key := range []string{"command", "cmd", "tool"} {
			if name := rawJSONString(object[key]); name != "" && !strings.Contains(name, " ") {
				call.Name = strings.TrimSpace(name)
				markRepair(wire.RepairKeyAlias, ProtocolFailureToolShapeInvalid)
				break
			}
		}
	}
	if len(call.Arguments) == 0 {
		call.Arguments = firstRaw(object, "args", "parameters")
		if len(call.Arguments) > 0 {
			markRepair(wire.RepairKeyAlias, ProtocolFailureToolShapeInvalid)
		}
	}
	if len(call.Arguments) == 0 {
		hoisted := make(map[string]json.RawMessage)
		for key, raw := range object {
			switch key {
			case "name", "command", "cmd", "tool", "type", "function", "arguments", "args", "parameters", "id", "index":
				continue
			}
			hoisted[key] = raw
		}
		if len(hoisted) > 0 {
			call.Arguments, _ = json.Marshal(hoisted)
			markRepair(wire.RepairArgumentsHoisted, ProtocolFailureToolShapeInvalid)
		}
	}
	if len(call.Arguments) > 0 && call.Arguments[0] == '"' {
		var encodedArguments string
		if err := json.Unmarshal(call.Arguments, &encodedArguments); err == nil {
			call.Arguments = json.RawMessage(repairG1FunctionJSON(encodedArguments))
			markRepair(wire.RepairStringifiedArguments, ProtocolFailureToolShapeInvalid)
		}
	}
	if arguments, ok := rawJSONObject(call.Arguments); ok &&
		(call.Name == "" || call.Name == "function" || call.Name == "tool" || call.Name == "tool_call") {
		if nestedName := rawJSONString(arguments["name"]); nestedName != "" {
			call.Name = nestedName
			if nestedArguments := firstRaw(arguments, "arguments", "args", "parameters"); len(nestedArguments) > 0 {
				call.Arguments = nestedArguments
			} else {
				delete(arguments, "name")
				call.Arguments, _ = json.Marshal(arguments)
			}
			markRepair(wire.RepairNestedName, ProtocolFailureToolShapeInvalid)
		}
	}
	if call.Name == "" {
		if arguments, ok := rawJSONObject(call.Arguments); ok {
			if inferred := inferG1ToolName(arguments); inferred != "" {
				call.Name = inferred
				markRepair(wire.RepairNameInferred, ProtocolFailureToolShapeInvalid)
			}
		}
	}
	if decoder.Decode(&struct{}{}) != io.EOF || strings.TrimSpace(call.Name) == "" || !isJSONObject(call.Arguments) {
		return Action{}, fmt.Errorf("%w: invalid G1 function call", ErrToolShapeInvalid)
	}
	if protocol.Product && protocol.SemanticNoTool && call.Name == SemanticNoToolName {
		rationale, answer, err := parseSemanticNoToolArguments(call.Arguments)
		if err != nil {
			return Action{}, err
		}
		return Action{
			Type:                    ActionTypeNoTool,
			Name:                    call.Name,
			Arguments:               call.Arguments,
			NoToolRationale:         rationale,
			NoToolAnswer:            answer,
			ProtocolRepaired:        repairs.any(),
			OriginalProtocolFailure: originalFailure,
			Repairs:                 repairs.list(),
		}, nil
	}
	return Action{
		Type:                    ActionTypeTool,
		Name:                    call.Name,
		Arguments:               call.Arguments,
		ProtocolRepaired:        repairs.any(),
		OriginalProtocolFailure: originalFailure,
		Repairs:                 repairs.list(),
	}, nil
}

func parseSemanticNoToolArguments(raw json.RawMessage) (string, string, error) {
	var arguments map[string]json.RawMessage
	if json.Unmarshal(raw, &arguments) != nil || arguments == nil {
		return "", "", fmt.Errorf("%w: no_tool arguments must be an object", ErrToolShapeInvalid)
	}
	values := make(map[string]string, len(arguments))
	for name, encoded := range arguments {
		if name != "reason" && name != "answer" {
			return "", "", fmt.Errorf(
				"%w: no_tool arguments only allow optional string fields reason and answer",
				ErrToolShapeInvalid,
			)
		}
		var value string
		if json.Unmarshal(encoded, &value) != nil {
			return "", "", fmt.Errorf(
				"%w: no_tool argument %s must be a string",
				ErrToolShapeInvalid,
				name,
			)
		}
		values[name] = strings.TrimSpace(value)
	}
	return values["reason"], values["answer"], nil
}

func firstRaw(object map[string]json.RawMessage, keys ...string) json.RawMessage {
	for _, key := range keys {
		if raw := object[key]; len(raw) > 0 && string(raw) != "null" {
			return raw
		}
	}
	return nil
}

func rawJSONString(raw json.RawMessage) string {
	var value string
	if json.Unmarshal(raw, &value) != nil {
		return ""
	}
	return strings.TrimSpace(value)
}

func rawJSONObject(raw json.RawMessage) (map[string]json.RawMessage, bool) {
	var object map[string]json.RawMessage
	if len(raw) == 0 || json.Unmarshal(raw, &object) != nil || object == nil {
		return nil, false
	}
	return object, true
}

func inferG1ToolName(arguments map[string]json.RawMessage) string {
	hasValue := func(keys ...string) bool {
		for _, key := range keys {
			raw, ok := arguments[key]
			value := strings.TrimSpace(string(raw))
			if ok && value != "" && value != "null" && value != `""` {
				return true
			}
		}
		return false
	}
	if hasValue("answer") {
		return "submit"
	}
	if hasValue("code", "script") {
		return "run_lua"
	}
	if hasValue("content", "file_text") && hasValue("path", "file_path", "filename") {
		return "write_file"
	}
	if hasValue("path", "file_path", "filename") {
		path := rawJSONString(firstRaw(arguments, "path", "file_path", "filename"))
		if path == "." || path == "./" {
			return "list_files"
		}
		return "read_file"
	}
	if hasValue("query", "pattern") {
		return "search"
	}
	return ""
}

func repairG1FunctionJSON(value string) string {
	var output strings.Builder
	inString := false
	escaped := false
	stack := make([]byte, 0, 8)
	for _, char := range value {
		if escaped {
			switch char {
			case '\n':
				output.WriteString(`\n`)
			case '\r':
				output.WriteString(`\r`)
			case '\t':
				output.WriteString(`\t`)
			case '"', '\\', '/', 'b', 'f', 'n', 'r', 't', 'u':
				output.WriteByte('\\')
				output.WriteRune(char)
			default:
				// Match the official runner's tolerant repair: a model often
				// emits regex-style escapes such as \d, which are invalid JSON.
				// Keeping the character while dropping the slash preserves intent.
				output.WriteRune(char)
			}
			escaped = false
			continue
		}
		if inString && char == '\\' {
			escaped = true
			continue
		}
		if char == '"' {
			inString = !inString
			output.WriteRune(char)
			continue
		}
		if inString {
			switch char {
			case '\n':
				output.WriteString(`\n`)
			case '\r':
				output.WriteString(`\r`)
			case '\t':
				output.WriteString(`\t`)
			default:
				output.WriteRune(char)
			}
			continue
		}
		switch char {
		case '{', '[':
			stack = append(stack, byte(char))
		case '}', ']':
			if len(stack) > 0 {
				stack = stack[:len(stack)-1]
			}
		}
		output.WriteRune(char)
	}
	if escaped {
		// Preserve a trailing literal backslash as a valid escaped backslash
		// before closing a truncated JSON string.
		output.WriteString(`\\`)
	}
	if inString {
		output.WriteByte('"')
	}
	for index := len(stack) - 1; index >= 0; index-- {
		if stack[index] == '{' {
			output.WriteByte('}')
		} else {
			output.WriteByte(']')
		}
	}
	return output.String()
}
