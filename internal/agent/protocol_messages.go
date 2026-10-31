package agent

import (
	"encoding/json"
	"fmt"
	"regexp"
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
	// HistoryThinkFast restores the empty think prefix on assistant history
	// for opt-in evaluation of states trained with that prefix on every turn.
	HistoryThinkFast bool
	// HistoryEmptyThink writes the transcript the way the think-sft corpus
	// does: an empty think block before every past assistant step, and no
	// blank line or trailing space inside any block.
	HistoryEmptyThink bool
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
		if message.Role == RoleAssistant && renderer.HistoryThinkFast && !strings.HasPrefix(strings.TrimSpace(content), "<think>") {
			content = inference.ThinkBlockClosed + content
		}
		if renderer.HistoryEmptyThink {
			content = collapseBlock(content)
			if message.Role == RoleAssistant && !strings.HasPrefix(content, "<think>") {
				content = inference.ThinkBlockClosed + content
			}
		}
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

// Blank-line and trailing-space patterns of the think-sft corpus
// (bench/distill/tools/think_sft/collapse_blank.py); collapseBlock must stay
// byte-identical to it, including the indentation a blank line swallows from
// the line after it.
var (
	blankLinesPattern    = regexp.MustCompile(`\n[ \t\x{3000}]*(?:\n[ \t\x{3000}]*)+`)
	trailingSpacePattern = regexp.MustCompile(`[ \t\x{3000}]+\n`)
)

// collapseBlock keeps "\n\n" for separating turns only: blank lines fold
// into one newline and trailing spaces are trimmed.
func collapseBlock(text string) string {
	text = strings.ReplaceAll(text, "\r\n", "\n")
	text = blankLinesPattern.ReplaceAllString(text, "\n")
	text = trailingSpacePattern.ReplaceAllString(text, "\n")
	return strings.TrimSpace(text)
}

func (renderer RWKVChatRenderer) thinkingMode() inference.ThinkingMode {
	if renderer.ThinkingMode != "" {
		return renderer.ThinkingMode
	}
	return inference.ThinkingOff
}

func (renderer RWKVChatRenderer) appendAssistantPrefix(prompt, prefix string) (string, bool) {
	// Render already ends with the role opening; an "Assistant:" prefix (the
	// empty no_tool answer stage) must not double it into "Assistant:
	// Assistant:". Nothing was injected, as in G1FunctionRenderer, so the
	// output is not re-prefixed either.
	if prefix == "Assistant:" && strings.HasSuffix(prompt, "Assistant:") {
		return prompt, false
	}
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
