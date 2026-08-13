package agent

import (
	"encoding/json"
	"fmt"
	"io"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

const (
	G1IFunctionProtocolV1 = "rwkv-g1i-functions-v1"
	G1IFunctionRendererV1 = "rwkv-g1i-functions-continuation-v1"
)

// G1IFunctionProtocol implements the JSON function-call transcript used to
// train G1i checkpoints: System: Tools, Assistant: ```json, and User: Function
// output. It is intentionally separate from the general XML agent protocol.
type G1IFunctionProtocol struct {
	// AllowRepeatedCalls preserves the upstream Primitive Bench controller,
	// which executes identical calls repeatedly. Product-facing Go-native runs
	// leave this false so the Runner can reject loops and provide recovery.
	AllowRepeatedCalls bool
}

func (G1IFunctionProtocol) ID() string { return G1IFunctionProtocolV1 }

func (G1IFunctionProtocol) Instructions(specs []ToolSpec, _ inference.ThinkingMode) string {
	catalog := make([]g1iCatalogEntry, 0, len(specs))
	for _, spec := range specs {
		catalog = append(catalog, makeG1ICatalogEntry(spec))
	}
	entries := make([]string, 0, len(catalog))
	for _, entry := range catalog {
		encoded, _ := json.Marshal(entry)
		entries = append(entries, string(encoded))
	}
	computeGuidance := ""
	if hasToolSpec(specs, "calculator") || hasToolSpec(specs, "data_query") {
		computeGuidance = "Read relevant task files with read_file first. calculator accepts only numeric literals, operators, and its listed math functions—never file names, SQL, or prose. " +
			"For multi-row tables use data_query; filter is a direct column-to-exact-value object and each call performs one operation. " +
			"Do not repeat a successful call or reread unchanged files. "
	}
	return "Tools:\n[\n" + strings.Join(entries, ",\n") + "\n]\n" +
		"Exact tool names only. Paths are relative (e.g. src/a.txt), never absolute. " +
		`Call shape: {"name":"read_file","arguments":{"path":"file.txt"}}. ` +
		computeGuidance + "After each Function output, return the next JSON function call. " +
		"Preserve exact paths and identifier names from Function output. " +
		"When the user requests exact stdout or file content, submit it verbatim, including prefixes and punctuation; do not paraphrase it. " +
		"Finish with submit when it is offered. read_file lines: omit leading 'N: '. Money: two decimals.\n" +
		"Return only a JSON function call."
}

type g1iCatalogEntry struct {
	Name        string                     `json:"name"`
	Description string                     `json:"description"`
	Arguments   map[string]json.RawMessage `json:"arguments"`
}

func makeG1ICatalogEntry(spec ToolSpec) g1iCatalogEntry {
	description := strings.TrimSpace(spec.Description)
	if index := strings.IndexAny(description, ".!?"); index >= 0 {
		description = strings.TrimSpace(description[:index+1])
	}
	if len([]rune(description)) > 140 {
		description = string([]rune(description)[:137]) + "..."
	}
	var schema struct {
		Properties map[string]json.RawMessage `json:"properties"`
	}
	_ = json.Unmarshal(spec.Parameters, &schema)
	arguments := make(map[string]json.RawMessage, len(schema.Properties))
	for name, raw := range schema.Properties {
		var property map[string]json.RawMessage
		if json.Unmarshal(raw, &property) != nil {
			continue
		}
		compact := make(map[string]json.RawMessage, 3)
		for _, key := range []string{"type", "enum", "items"} {
			if value, ok := property[key]; ok {
				compact[key] = value
			}
		}
		if len(compact) == 0 {
			compact["type"] = json.RawMessage(`"string"`)
		}
		encoded, _ := json.Marshal(compact)
		arguments[name] = encoded
	}
	return g1iCatalogEntry{Name: spec.Name, Description: description, Arguments: arguments}
}

func (G1IFunctionProtocol) Parse(value string, finish continuation.FinishReason) (Action, error) {
	candidate := strings.TrimSpace(value)
	protocolRepaired := false
	if index := strings.LastIndex(candidate, "</think>"); index >= 0 {
		candidate = strings.TrimSpace(candidate[index+len("</think>"):])
		protocolRepaired = true
	}
	if start := strings.Index(candidate, "<tool_calls>"); start >= 0 {
		body := candidate[start+len("<tool_calls>"):]
		if end := strings.Index(body, "</tool_calls>"); end >= 0 {
			body = body[:end]
		}
		var calls []json.RawMessage
		if err := json.Unmarshal([]byte(strings.TrimSpace(body)), &calls); err != nil || len(calls) != 1 {
			return Action{}, fmt.Errorf("%w: G1i tool_calls must contain exactly one call", ErrProtocol)
		}
		candidate = string(calls[0])
		protocolRepaired = true
	} else if start := strings.Index(candidate, "<tool_call>"); start >= 0 {
		candidate = candidate[start+len("<tool_call>"):]
		if end := strings.Index(candidate, "</tool_call>"); end >= 0 {
			candidate = candidate[:end]
		}
		candidate = strings.TrimSpace(candidate)
		protocolRepaired = true
	}
	candidate = strings.TrimPrefix(candidate, "```json")
	candidate = strings.TrimPrefix(candidate, "```")
	candidate = strings.TrimSpace(candidate)
	if index := strings.Index(candidate, "```"); index >= 0 {
		candidate = strings.TrimSpace(candidate[:index])
	}
	if !strings.HasPrefix(candidate, "{") {
		if finish == continuation.FinishLength {
			return Action{}, ErrOutputTokenLimit
		}
		if candidate == "" {
			return Action{}, fmt.Errorf("%w: empty G1i function response", ErrProtocol)
		}
		return Action{Type: "final", Content: candidate}, nil
	}
	repaired := repairG1IFunctionJSON(candidate)
	var call struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}
	var object map[string]json.RawMessage
	decoder := json.NewDecoder(strings.NewReader(repaired))
	if err := decoder.Decode(&call); err != nil {
		return Action{}, fmt.Errorf("%w: decode G1i function call: %v", ErrProtocol, err)
	}
	_ = json.Unmarshal([]byte(repaired), &object)
	protocolRepaired = protocolRepaired || repaired != candidate
	if function, ok := rawJSONObject(object["function"]); ok {
		if name := rawJSONString(function["name"]); call.Name == "" && name != "" {
			call.Name = name
			protocolRepaired = true
		}
		if len(call.Arguments) == 0 {
			call.Arguments = firstRaw(function, "arguments", "args", "parameters")
			protocolRepaired = true
		}
	}
	if call.Name == "" {
		for _, key := range []string{"command", "cmd", "tool"} {
			if name := rawJSONString(object[key]); name != "" && !strings.Contains(name, " ") {
				call.Name = strings.TrimSpace(name)
				protocolRepaired = true
				break
			}
		}
	}
	if len(call.Arguments) == 0 {
		call.Arguments = firstRaw(object, "args", "parameters")
		if len(call.Arguments) > 0 {
			protocolRepaired = true
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
			protocolRepaired = true
		}
	}
	if len(call.Arguments) > 0 && call.Arguments[0] == '"' {
		var encodedArguments string
		if err := json.Unmarshal(call.Arguments, &encodedArguments); err == nil {
			call.Arguments = json.RawMessage(repairG1IFunctionJSON(encodedArguments))
			protocolRepaired = true
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
			protocolRepaired = true
		}
	}
	if call.Name == "" {
		if arguments, ok := rawJSONObject(call.Arguments); ok {
			call.Name = inferG1IToolName(arguments)
			protocolRepaired = call.Name != ""
		}
	}
	if decoder.Decode(&struct{}{}) != io.EOF || strings.TrimSpace(call.Name) == "" || !isJSONObject(call.Arguments) {
		return Action{}, fmt.Errorf("%w: invalid G1i function call", ErrProtocol)
	}
	return Action{
		Type:             "tool",
		Name:             call.Name,
		Arguments:        call.Arguments,
		ProtocolRepaired: protocolRepaired,
	}, nil
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

func inferG1IToolName(arguments map[string]json.RawMessage) string {
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

func repairG1IFunctionJSON(value string) string {
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

func (G1IFunctionProtocol) Correction(error) string {
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

func (G1IFunctionProtocol) ToolCallPrefix() string   { return "" }
func (G1IFunctionProtocol) PostToolReminder() string { return "" }
func (G1IFunctionProtocol) PrepareAnswer(messages []Message, _ []string, _ inference.ThinkingMode) ([]Message, string) {
	return messages, "Assistant:"
}
func (G1IFunctionProtocol) Stops(GenerationStage) []string {
	return []string{"```", "\n\nUser:", "\nUser:", "</s>"}
}

func preservesToolOrder(protocol ActionProtocol) bool {
	_, ok := protocol.(G1IFunctionProtocol)
	return ok
}

func allowsRepeatedToolCalls(protocol ActionProtocol) bool {
	value, ok := protocol.(G1IFunctionProtocol)
	return ok && value.AllowRepeatedCalls
}

// G1IFunctionRenderer renders the trained continuation transcript. Cases with
// submit always stay in function-call mode. Arithmetic answers directly after
// their tool result; invoice cases switch to direct answer only after PASS.
type G1IFunctionRenderer struct {
	HasSubmit   bool
	HasRunTests bool
}

func (G1IFunctionRenderer) ID() string { return G1IFunctionRendererV1 }

func (renderer G1IFunctionRenderer) Render(messages []Message) (string, error) {
	if len(messages) == 0 {
		return "", fmt.Errorf("render G1i function prompt: no messages")
	}
	var prompt strings.Builder
	lastToolResult := ""
	for _, message := range messages {
		if strings.TrimSpace(message.Content) == "" {
			return "", fmt.Errorf("render G1i function prompt: %s message is empty", message.Role)
		}
		switch message.Role {
		case RoleSystem:
			fmt.Fprintf(&prompt, "System: %s\n\n", cleanMessageText(message.Content))
		case RoleUser:
			fmt.Fprintf(&prompt, "User: %s\n\n", cleanMessageText(message.Content))
		case RoleAssistant:
			fmt.Fprintf(&prompt, "Assistant: %s\n\n", message.Content)
		case RoleTool:
			lastToolResult = message.Content
			fmt.Fprintf(&prompt, "User: Function output:\n%s\n\n", message.Content)
		default:
			return "", fmt.Errorf("render G1i function prompt: unknown role %q", message.Role)
		}
	}
	plainAnswer := !renderer.HasSubmit && (!renderer.HasRunTests || strings.HasPrefix(lastToolResult, "PASS"))
	if plainAnswer {
		prompt.WriteString("Assistant:")
	} else {
		prompt.WriteString("Assistant: ```json\n")
	}
	return prompt.String(), nil
}

func (G1IFunctionRenderer) appendAssistantPrefix(prompt, prefix string) (string, bool) {
	if prefix == "Assistant:" && strings.HasSuffix(prompt, "Assistant:") {
		return prompt, false
	}
	return prompt + prefix, prefix != ""
}
