package bfcl

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type Tier string

const (
	TierBaseline        Tier = "baseline"
	TierEnhanced        Tier = "enhanced"
	TierFinishTaskProbe Tier = "finish-task-probe"
)

const RenderProtocolAnchorV1 = "bfcl-markdown-anchor-v1"
const RenderProtocolFinishTaskV1 = "bfcl-markdown-finish-task-v1"

const FinishTaskName = "finish_task"

var finishTaskFunction = json.RawMessage(`{"name":"finish_task","description":"End the task without calling any other tool when no listed tool applies to the user request.","parameters":{"type":"dict","properties":{},"required":[]}}`)

type RenderedPrompt struct {
	Prompt string
	Anchor string
}

type Transport string

type ParserMode string

type ParseOutcome struct {
	Calls   []toolchat.ToolCall
	Repairs []string
}

const (
	TransportRWKVContinuation        Transport = "rwkv-continuation"
	TransportChatCompletionsWrapped  Transport = "chat-completions-wrapped"
	TransportChatCompletionsNativeFC Transport = "chat-completions-native-fc"

	ParserStrict           ParserMode = "strict"
	ParserRWKVWireCompatV1 ParserMode = "rwkv-wire-compat-v1"

	RepairArgumentsUnwrapped = "arguments_unwrapped"
	RepairCallIDDropped      = "call_id_dropped"
)

func ParseParserMode(value string) (ParserMode, error) {
	mode := ParserMode(strings.ToLower(strings.TrimSpace(value)))
	if mode == "" {
		mode = ParserStrict
	}
	switch mode {
	case ParserStrict, ParserRWKVWireCompatV1:
		return mode, nil
	default:
		return "", fmt.Errorf("unsupported BFCL parser mode %q", value)
	}
}

func RenderPrompt(entry Case, tier Tier, transport Transport) (string, error) {
	rendered, err := RenderPromptWithAnchor(entry, tier, transport)
	if err != nil {
		return "", err
	}
	return rendered.Prompt, nil
}

func RenderPromptWithAnchor(entry Case, tier Tier, transport Transport) (RenderedPrompt, error) {
	if tier != TierBaseline && tier != TierEnhanced && tier != TierFinishTaskProbe {
		return RenderedPrompt{}, fmt.Errorf("unsupported BFCL tier %q", tier)
	}
	if transport != TransportRWKVContinuation && transport != TransportChatCompletionsWrapped {
		return RenderedPrompt{}, fmt.Errorf("unsupported BFCL transport %q", transport)
	}
	if len(entry.Messages) == 0 {
		return RenderedPrompt{}, fmt.Errorf("BFCL case %q requires messages", entry.ID)
	}

	var prompt strings.Builder
	prompt.WriteString("System: Tools:\n[\n")
	for index, function := range entry.Functions {
		if len(function) == 0 || !json.Valid(function) {
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q function %d is invalid JSON", entry.ID, index)
		}
		if index > 0 {
			prompt.WriteString(",\n")
		}
		prompt.Write(function)
	}
	if tier == TierFinishTaskProbe {
		if len(entry.Functions) > 0 {
			prompt.WriteString(",\n")
		}
		prompt.Write(finishTaskFunction)
	}
	prompt.WriteString("\n]\n")
	if tier == TierFinishTaskProbe {
		prompt.WriteString("Use an exact tool name only. If no listed task tool can satisfy the request, call finish_task with an empty arguments object. ")
		prompt.WriteString("Otherwise call exactly one relevant task tool. Return exactly one fenced JSON function call and nothing else. ")
	} else if entry.Category == "irrelevance" || entry.Category == "live_irrelevance" {
		prompt.WriteString("Use an exact tool name only when a listed tool can satisfy the request. ")
		prompt.WriteString("If no listed tool is relevant, return no function call. Otherwise return exactly one fenced JSON function call and nothing else. ")
	} else if strings.Contains(entry.Category, "parallel") {
		prompt.WriteString("Exact tool names only. Return exactly one fenced JSON array of function calls and nothing else. ")
		prompt.WriteString(`Correct shape: [{"name":"TOOL_NAME","arguments":{"ARGUMENT_NAME":"VALUE"}},{"name":"TOOL_NAME","arguments":{"ARGUMENT_NAME":"VALUE"}}]. `)
	} else {
		prompt.WriteString("Exact tool names only. Return exactly one fenced JSON function call and nothing else. ")
	}
	if !strings.Contains(entry.Category, "parallel") {
		prompt.WriteString(`Correct shape: {"name":"TOOL_NAME","arguments":{"ARGUMENT_NAME":"VALUE"}}. `)
	}
	prompt.WriteString(`Never use this wrong shape: {"name":"TOOL_NAME","arguments":"{\"ARGUMENT_NAME\":\"VALUE\"}"}. `)
	prompt.WriteString("The arguments value must be a JSON object, never a quoted or escaped JSON string. ")
	prompt.WriteString("Do not output prose or role labels.\n\n")
	for index, message := range entry.Messages {
		if strings.TrimSpace(message.Content) == "" {
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q message %d is empty", entry.ID, index)
		}
		switch message.Role {
		case "system":
			prompt.WriteString("System: ")
		case "user":
			prompt.WriteString("User: ")
		case "assistant":
			prompt.WriteString("Assistant: ")
		default:
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q message %d has unsupported role %q", entry.ID, index, message.Role)
		}
		prompt.WriteString(message.Content)
		prompt.WriteString("\n\n")
	}
	anchor := prefillAnchor(entry.Category)
	prompt.WriteString("Assistant: ```json\n")
	prompt.WriteString(anchor)
	return RenderedPrompt{Prompt: prompt.String(), Anchor: anchor}, nil
}

func prefillAnchor(category string) string {
	if strings.Contains(category, "parallel") {
		return `[{"name":"`
	}
	return `{"name":"`
}

func ParseMarkdownCalls(value string) ([]toolchat.ToolCall, error) {
	raw, err := decodeMarkdownCallValue(value)
	if err != nil {
		return nil, err
	}
	if len(raw) > 0 && raw[0] == '[' {
		var objects []map[string]json.RawMessage
		if err := json.Unmarshal(raw, &objects); err != nil {
			return nil, fmt.Errorf("decode function call array: %w", err)
		}
		calls := make([]toolchat.ToolCall, 0, len(objects))
		for index, object := range objects {
			parsed, err := parseStrictCallObject(object)
			if err != nil {
				return nil, fmt.Errorf("function call %d: %w", index, err)
			}
			calls = append(calls, parsed[0])
		}
		return calls, nil
	}
	var object map[string]json.RawMessage
	if err := json.Unmarshal(raw, &object); err != nil {
		return nil, fmt.Errorf("decode function call: %w", err)
	}
	return parseStrictCallObject(object)
}

func ParseMarkdownCallsWithMode(
	value string,
	functions []json.RawMessage,
	mode ParserMode,
) (ParseOutcome, error) {
	switch mode {
	case ParserStrict:
		calls, err := ParseMarkdownCalls(value)
		return ParseOutcome{Calls: calls}, err
	case ParserRWKVWireCompatV1:
		if calls, err := ParseMarkdownCalls(value); err == nil {
			return ParseOutcome{Calls: calls}, nil
		}
		return parseRWKVWireCompatV1(value, functions)
	default:
		return ParseOutcome{}, fmt.Errorf("unsupported BFCL parser mode %q", mode)
	}
}

func decodeMarkdownCallValue(value string) (json.RawMessage, error) {
	candidate := strings.TrimSpace(value)
	if strings.HasPrefix(candidate, "```json") {
		candidate = strings.TrimPrefix(candidate, "```json")
		if !strings.HasSuffix(candidate, "```") {
			return nil, fmt.Errorf("unterminated JSON fence")
		}
		candidate = strings.TrimSpace(strings.TrimSuffix(candidate, "```"))
	}
	if candidate == "" {
		return nil, fmt.Errorf("empty function call")
	}

	decoder := json.NewDecoder(strings.NewReader(candidate))
	decoder.UseNumber()
	var raw json.RawMessage
	if err := decoder.Decode(&raw); err != nil {
		return nil, fmt.Errorf("decode function call: %w", err)
	}
	if _, err := decoder.Token(); err != io.EOF {
		if err == nil {
			return nil, fmt.Errorf("unexpected trailing function call content")
		}
		return nil, fmt.Errorf("decode trailing function call content: %w", err)
	}
	return raw, nil
}

func parseStrictCallObject(object map[string]json.RawMessage) ([]toolchat.ToolCall, error) {
	if len(object) != 2 {
		return nil, fmt.Errorf("function call must contain exactly name and arguments")
	}
	var name string
	if err := json.Unmarshal(object["name"], &name); err != nil || strings.TrimSpace(name) == "" {
		return nil, fmt.Errorf("function call name is required")
	}
	arguments := object["arguments"]
	if len(arguments) == 0 {
		return nil, fmt.Errorf("function call arguments are required")
	}
	argumentDecoder := json.NewDecoder(bytes.NewReader(arguments))
	argumentDecoder.UseNumber()
	var argumentObject map[string]json.RawMessage
	if err := argumentDecoder.Decode(&argumentObject); err != nil {
		return nil, fmt.Errorf("function call arguments must be an object: %w", err)
	}
	if _, err := argumentDecoder.Token(); err != io.EOF {
		return nil, fmt.Errorf("function call arguments contain trailing content")
	}
	return []toolchat.ToolCall{{Name: name, Arguments: string(arguments)}}, nil
}

// parseRWKVWireCompatV1 repairs a single call object or an array of them.
//
// The array branch matters only where an anchor commits the model to array
// shape. Single-turn reaches it just on the parallel splits, where the anchor
// had already driven stringification to zero, so it went unexercised; the
// multi-turn array anchor makes every output an array, and without this the
// enhanced tier has nothing it can repair.
func parseRWKVWireCompatV1(value string, functions []json.RawMessage) (ParseOutcome, error) {
	raw, err := decodeMarkdownCallValue(value)
	if err != nil {
		return ParseOutcome{}, err
	}
	if len(raw) > 0 && bytes.TrimSpace(raw)[0] == '[' {
		var elements []map[string]json.RawMessage
		if err := json.Unmarshal(raw, &elements); err != nil {
			return ParseOutcome{}, fmt.Errorf("decode function call array: %w", err)
		}
		if len(elements) == 0 {
			return ParseOutcome{}, fmt.Errorf("function call array is empty")
		}
		outcome := ParseOutcome{Calls: make([]toolchat.ToolCall, 0, len(elements))}
		for index, element := range elements {
			single, err := repairRWKVCallObject(element, functions)
			if err != nil {
				return ParseOutcome{}, fmt.Errorf("function call %d: %w", index, err)
			}
			outcome.Calls = append(outcome.Calls, single.Calls...)
			outcome.Repairs = append(outcome.Repairs, single.Repairs...)
		}
		return outcome, nil
	}
	var object map[string]json.RawMessage
	if err := json.Unmarshal(raw, &object); err != nil {
		return ParseOutcome{}, fmt.Errorf("decode function call: %w", err)
	}
	return repairRWKVCallObject(object, functions)
}

func repairRWKVCallObject(object map[string]json.RawMessage, functions []json.RawMessage) (ParseOutcome, error) {
	var name string
	if err := json.Unmarshal(object["name"], &name); err != nil || strings.TrimSpace(name) == "" {
		return ParseOutcome{}, fmt.Errorf("function call name is required")
	}
	parameterNames, err := functionParameterNames(functions, name)
	if err != nil {
		return ParseOutcome{}, err
	}
	arguments := object["arguments"]
	if len(arguments) == 0 {
		return ParseOutcome{}, fmt.Errorf("function call arguments are required")
	}
	repairs := make([]string, 0, 3)
	argumentBytes := bytes.TrimSpace(arguments)
	if len(argumentBytes) > 0 && argumentBytes[0] == '"' {
		var encoded string
		if err := json.Unmarshal(argumentBytes, &encoded); err != nil {
			return ParseOutcome{}, fmt.Errorf("decode stringified function call arguments: %w", err)
		}
		argumentBytes = []byte(strings.TrimSpace(encoded))
		repairs = append(repairs, RepairArgumentsUnwrapped)
	}
	argumentObject, err := decodeArgumentObject(argumentBytes)
	if err != nil {
		return ParseOutcome{}, err
	}

	keys := make([]string, 0, len(object))
	for key := range object {
		if key != "name" && key != "arguments" {
			keys = append(keys, key)
		}
	}
	sort.Strings(keys)
	movedArgument := false
	for _, key := range keys {
		if _, isParameter := parameterNames[key]; isParameter {
			if _, exists := argumentObject[key]; exists {
				return ParseOutcome{}, fmt.Errorf("top-level function argument %q conflicts with arguments object", key)
			}
			argumentObject[key] = object[key]
			repairs = append(repairs, "top_level_argument_moved:"+key)
			movedArgument = true
			continue
		}
		if key == "id" {
			var callID string
			if err := json.Unmarshal(object[key], &callID); err != nil || strings.TrimSpace(callID) == "" {
				return ParseOutcome{}, fmt.Errorf("function call id metadata must be a non-empty string")
			}
			repairs = append(repairs, RepairCallIDDropped)
			continue
		}
		return ParseOutcome{}, fmt.Errorf("unsupported top-level function call field %q", key)
	}
	if movedArgument {
		argumentBytes, err = json.Marshal(argumentObject)
		if err != nil {
			return ParseOutcome{}, fmt.Errorf("encode normalized function call arguments: %w", err)
		}
	}
	return ParseOutcome{
		Calls:   []toolchat.ToolCall{{Name: name, Arguments: string(argumentBytes)}},
		Repairs: repairs,
	}, nil
}

func decodeArgumentObject(arguments []byte) (map[string]json.RawMessage, error) {
	decoder := json.NewDecoder(bytes.NewReader(arguments))
	decoder.UseNumber()
	var object map[string]json.RawMessage
	if err := decoder.Decode(&object); err != nil || object == nil {
		if err == nil {
			err = fmt.Errorf("arguments must be a JSON object")
		}
		return nil, fmt.Errorf("function call arguments must be an object: %w", err)
	}
	if _, err := decoder.Token(); err != io.EOF {
		if err == nil {
			return nil, fmt.Errorf("function call arguments contain trailing content")
		}
		return nil, fmt.Errorf("function call arguments contain trailing content: %w", err)
	}
	return object, nil
}

func functionParameterNames(functions []json.RawMessage, name string) (map[string]struct{}, error) {
	type functionDefinition struct {
		Name       string `json:"name"`
		Parameters struct {
			Properties map[string]json.RawMessage `json:"properties"`
		} `json:"parameters"`
	}
	var matched *functionDefinition
	for index, raw := range functions {
		var definition functionDefinition
		if err := json.Unmarshal(raw, &definition); err != nil {
			return nil, fmt.Errorf("decode function schema %d: %w", index, err)
		}
		if definition.Name != name {
			continue
		}
		if matched != nil {
			return nil, fmt.Errorf("duplicate function schema %q", name)
		}
		matched = &definition
	}
	if matched == nil {
		return nil, fmt.Errorf("function call name %q is not available", name)
	}
	result := make(map[string]struct{}, len(matched.Parameters.Properties))
	for parameter := range matched.Parameters.Properties {
		result[parameter] = struct{}{}
	}
	return result, nil
}
