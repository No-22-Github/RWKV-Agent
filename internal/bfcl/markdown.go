package bfcl

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type Tier string

const (
	TierBaseline Tier = "baseline"
)

type Transport string

const (
	TransportRWKVContinuation Transport = "rwkv-continuation"
)

func RenderPrompt(entry Case, tier Tier, transport Transport) (string, error) {
	if tier != TierBaseline {
		return "", fmt.Errorf("unsupported BFCL tier %q", tier)
	}
	if transport != TransportRWKVContinuation {
		return "", fmt.Errorf("unsupported BFCL transport %q", transport)
	}
	if len(entry.Messages) == 0 || len(entry.Functions) == 0 {
		return "", fmt.Errorf("BFCL case %q requires messages and functions", entry.ID)
	}

	var prompt strings.Builder
	prompt.WriteString("System: Tools:\n[\n")
	for index, function := range entry.Functions {
		if len(function) == 0 || !json.Valid(function) {
			return "", fmt.Errorf("BFCL case %q function %d is invalid JSON", entry.ID, index)
		}
		if index > 0 {
			prompt.WriteString(",\n")
		}
		prompt.Write(function)
	}
	prompt.WriteString("\n]\n")
	prompt.WriteString("Exact tool names only. Return exactly one fenced JSON function call and nothing else. ")
	prompt.WriteString(`Correct shape: {"name":"TOOL_NAME","arguments":{"ARGUMENT_NAME":"VALUE"}}. `)
	prompt.WriteString(`Never use this wrong shape: {"name":"TOOL_NAME","arguments":"{\"ARGUMENT_NAME\":\"VALUE\"}"}. `)
	prompt.WriteString("The arguments value must be a JSON object, never a quoted or escaped JSON string. ")
	prompt.WriteString("Do not output prose or role labels.\n\n")
	for index, message := range entry.Messages {
		if strings.TrimSpace(message.Content) == "" {
			return "", fmt.Errorf("BFCL case %q message %d is empty", entry.ID, index)
		}
		switch message.Role {
		case "system":
			prompt.WriteString("System: ")
		case "user":
			prompt.WriteString("User: ")
		default:
			return "", fmt.Errorf("BFCL case %q message %d has unsupported role %q", entry.ID, index, message.Role)
		}
		prompt.WriteString(message.Content)
		prompt.WriteString("\n\n")
	}
	prompt.WriteString("Assistant: ```json\n")
	return prompt.String(), nil
}

func ParseMarkdownCalls(value string) ([]toolchat.ToolCall, error) {
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
	var object map[string]json.RawMessage
	if err := decoder.Decode(&object); err != nil {
		return nil, fmt.Errorf("decode function call: %w", err)
	}
	if _, err := decoder.Token(); err != io.EOF {
		if err == nil {
			return nil, fmt.Errorf("unexpected trailing function call content")
		}
		return nil, fmt.Errorf("decode trailing function call content: %w", err)
	}
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
