package agent

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/inference"
)

type MessageRole string

const (
	RoleSystem    MessageRole = "system"
	RoleUser      MessageRole = "user"
	RoleAssistant MessageRole = "assistant"
	RoleTool      MessageRole = "tool"
)

type Message struct {
	Role             MessageRole
	Content          string
	ReasoningContent string
	Name             string
	ToolCallID       string
	ToolCalls        []toolchat.ToolCall
}

type PromptRenderer interface {
	ID() string
	Render([]Message) (string, error)
}

type RWKVChatRenderer struct {
	ThinkingMode inference.ThinkingMode
	// Reasoning preserves the former fast-thinking renderer construction.
	Reasoning bool
}

func (RWKVChatRenderer) ID() string {
	return RWKVPromptRendererV2
}

func (renderer RWKVChatRenderer) Render(messages []Message) (string, error) {
	if len(messages) == 0 {
		return "", fmt.Errorf("render agent prompt: no messages")
	}
	var prompt strings.Builder
	for _, message := range messages {
		if strings.TrimSpace(message.Content) == "" {
			return "", fmt.Errorf("render agent prompt: %s message is empty", message.Role)
		}
		label, ok := inference.ChatRoleLabel(inference.Role(message.Role))
		if !ok {
			return "", fmt.Errorf("render agent prompt: unknown role %q", message.Role)
		}
		content := message.Content
		if message.Role != RoleAssistant {
			content = inference.CleanChatText(inference.Role(message.Role), content)
		}
		fmt.Fprintf(&prompt, "%s: %s\n\n", label, content)
	}
	// The final ">" is withheld on purpose; see AppendAssistantOpening. The
	// model generates it, and reconstructOutput puts the prefix back before
	// parsing.
	inference.AppendAssistantOpening(&prompt, renderer.thinkingMode())
	return prompt.String(), nil
}

func (renderer RWKVChatRenderer) thinkingMode() inference.ThinkingMode {
	if renderer.ThinkingMode != "" {
		return renderer.ThinkingMode
	}
	if renderer.Reasoning {
		return inference.ThinkingFast
	}
	return inference.ThinkingOff
}

func (renderer RWKVChatRenderer) appendAssistantPrefix(prompt, prefix string) (string, bool) {
	if renderer.thinkingMode() != inference.ThinkingOff {
		return prompt, false
	}
	return prompt + " " + prefix, true
}

// reconstructOutput restores the think prefix that Render withheld, so the parser
// sees a well-formed block. The model's output opens with the ">" that completes
// the tag Render left unfinished.
func (renderer RWKVChatRenderer) reconstructOutput(output string) string {
	if strings.HasPrefix(strings.TrimSpace(output), "<think>") {
		return output
	}
	switch renderer.thinkingMode() {
	case inference.ThinkingFast:
		return inference.ThinkBlockFast + output
	case inference.ThinkingFull:
		return inference.ThinkBlockFull + output
	default:
		return output
	}
}

func isJSONObject(value json.RawMessage) bool {
	var object map[string]json.RawMessage
	return len(value) != 0 && json.Unmarshal(value, &object) == nil && object != nil
}
