package agent

import (
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/inference"
)

// G1FunctionRenderer renders the trained continuation transcript. Cases with
// submit always stay in function-call mode. Arithmetic answers directly after
// their tool result; invoice cases switch to direct answer only after PASS.
type G1FunctionRenderer struct {
	HasSubmit   bool
	HasRunTests bool
	Product     bool
	// DecisionFakeThink prefills a think block on unanchored tool decisions.
	// ClosedFakeThink selects the fully closed form instead of the half-open
	// one; it has no effect unless DecisionFakeThink is set.
	DecisionFakeThink bool
	ClosedFakeThink   bool
}

func (renderer G1FunctionRenderer) ID() string {
	if renderer.Product {
		return G1ProductFunctionRendererV1
	}
	return G1FunctionRendererV1
}

func (renderer G1FunctionRenderer) Render(messages []Message) (string, error) {
	if len(messages) == 0 {
		return "", fmt.Errorf("render G1 function prompt: no messages")
	}
	var prompt strings.Builder
	lastToolResult := ""
	for _, message := range messages {
		if strings.TrimSpace(message.Content) == "" {
			return "", fmt.Errorf("render G1 function prompt: %s message is empty", message.Role)
		}
		switch message.Role {
		case RoleSystem:
			fmt.Fprintf(&prompt, "System: %s\n\n", inference.CleanChatText(inference.Role(message.Role), message.Content))
		case RoleUser:
			fmt.Fprintf(&prompt, "User: %s\n\n", inference.CleanChatText(inference.Role(message.Role), message.Content))
		case RoleAssistant:
			fmt.Fprintf(&prompt, "Assistant: %s\n\n", message.Content)
		case RoleTool:
			lastToolResult = message.Content
			fmt.Fprintf(&prompt, "User: Function output:\n%s\n\n", message.Content)
		default:
			return "", fmt.Errorf("render G1 function prompt: unknown role %q", message.Role)
		}
	}
	plainAnswer := renderer.Product || (!renderer.HasSubmit && (!renderer.HasRunTests || strings.HasPrefix(lastToolResult, "PASS")))
	if plainAnswer {
		prompt.WriteString("Assistant:")
	} else {
		prompt.WriteString("Assistant: ```json\n")
	}
	return prompt.String(), nil
}

func (G1FunctionRenderer) appendAssistantPrefix(prompt, prefix string) (string, bool) {
	if prefix == "Assistant:" && strings.HasSuffix(prompt, "Assistant:") {
		return prompt, false
	}
	if strings.HasSuffix(prompt, "Assistant:") && strings.HasPrefix(prefix, "```") {
		return prompt + " " + prefix, true
	}
	if strings.HasSuffix(prompt, "Assistant:") &&
		(prefix == G1DecisionFakeThinkPrefix || prefix == G1DecisionClosedThinkPrefix) {
		return prompt + " " + prefix, true
	}
	return prompt + prefix, prefix != ""
}
