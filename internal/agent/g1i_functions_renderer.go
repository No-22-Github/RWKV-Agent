package agent

import (
	"fmt"
	"strings"
)

// G1IFunctionRenderer renders the trained continuation transcript. Cases with
// submit always stay in function-call mode. Arithmetic answers directly after
// their tool result; invoice cases switch to direct answer only after PASS.
type G1IFunctionRenderer struct {
	HasSubmit   bool
	HasRunTests bool
	Product     bool
}

func (renderer G1IFunctionRenderer) ID() string {
	if renderer.Product {
		return G1IProductFunctionRendererV1
	}
	return G1IFunctionRendererV1
}

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
	plainAnswer := renderer.Product || (!renderer.HasSubmit && (!renderer.HasRunTests || strings.HasPrefix(lastToolResult, "PASS")))
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
	if strings.HasSuffix(prompt, "Assistant:") && strings.HasPrefix(prefix, "```") {
		return prompt + " " + prefix, true
	}
	return prompt + prefix, prefix != ""
}
