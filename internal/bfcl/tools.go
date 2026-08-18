package bfcl

import (
	"bytes"
	"encoding/json"
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type functionDefinition struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Parameters  json.RawMessage `json:"parameters"`
}

func NativeTools(entry Case) ([]toolchat.Tool, map[string]string, error) {
	tools := make([]toolchat.Tool, 0, len(entry.Functions))
	originalNames := make(map[string]string, len(entry.Functions))
	for index, raw := range entry.Functions {
		decoder := json.NewDecoder(bytes.NewReader(raw))
		decoder.UseNumber()
		var definition functionDefinition
		if err := decoder.Decode(&definition); err != nil {
			return nil, nil, fmt.Errorf("case %q function %d: %w", entry.ID, index, err)
		}
		if strings.TrimSpace(definition.Name) == "" {
			return nil, nil, fmt.Errorf("case %q function %d has no name", entry.ID, index)
		}
		name := strings.ReplaceAll(definition.Name, ".", "_")
		if previous, exists := originalNames[name]; exists && previous != definition.Name {
			return nil, nil, fmt.Errorf(
				"case %q function name collision: %q and %q map to %q",
				entry.ID,
				previous,
				definition.Name,
				name,
			)
		}
		parameters, err := openAISchema(definition.Parameters)
		if err != nil {
			return nil, nil, fmt.Errorf("case %q function %q parameters: %w", entry.ID, definition.Name, err)
		}
		originalNames[name] = definition.Name
		tools = append(tools, toolchat.Tool{
			Name:        name,
			Description: definition.Description,
			Parameters:  parameters,
			Strict:      false,
		})
	}
	return tools, originalNames, nil
}

func openAISchema(raw json.RawMessage) (json.RawMessage, error) {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.UseNumber()
	var value any
	if err := decoder.Decode(&value); err != nil {
		return nil, err
	}
	convertSchemaTypes(value)
	encoded, err := json.Marshal(value)
	if err != nil {
		return nil, err
	}
	return encoded, nil
}

func convertSchemaTypes(value any) {
	switch current := value.(type) {
	case map[string]any:
		if kind, ok := current["type"].(string); ok {
			current["type"] = openAIType(kind)
		}
		for _, child := range current {
			convertSchemaTypes(child)
		}
	case []any:
		for _, child := range current {
			convertSchemaTypes(child)
		}
	}
}

func openAIType(value string) string {
	switch strings.ToLower(value) {
	case "dict":
		return "object"
	case "float":
		return "number"
	case "tuple", "list":
		return "array"
	case "any":
		return "string"
	default:
		return value
	}
}

func NativeMessages(entry Case) []toolchat.Message {
	messages := make([]toolchat.Message, 0, len(entry.Messages))
	for _, message := range entry.Messages {
		messages = append(messages, toolchat.Message{
			Role:    toolchat.Role(message.Role),
			Content: message.Content,
		})
	}
	return messages
}
