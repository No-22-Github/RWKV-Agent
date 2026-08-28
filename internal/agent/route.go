package agent

import (
	"errors"
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

type Route string

const (
	RouteRespond Route = "respond"
	RouteInspect Route = "inspect"
)

type RouteProtocol interface {
	ID() string
	Instructions() string
	Parse(string, continuation.FinishReason) (Route, error)
	Correction(error) string
	Stops() []string
}

type ToolRouteDecision struct {
	Route   Route
	Bundles []string
}

type ToolRouteProtocol interface {
	ID() string
	Instructions([]ToolBundle) string
	Parse(string, continuation.FinishReason, []ToolBundle) (ToolRouteDecision, error)
	Correction(error, []ToolBundle) string
	Stops() []string
}

type G1IProgressiveToolRouteProtocol struct{}

func (G1IProgressiveToolRouteProtocol) ID() string { return G1IToolRouteProtocolV1 }

func (G1IProgressiveToolRouteProtocol) Instructions(bundles []ToolBundle) string {
	var prompt strings.Builder
	prompt.WriteString(`Choose whether the current user message needs NEW tool evidence. Output exactly one route and nothing else.
Use <route>respond</route> when no new evidence is needed, required arguments are missing, or the user only asks about capabilities. Writing or explaining code, math, prose, or general knowledge never requires tool evidence.
Use exactly one of these concrete routes when a capability is needed:`)
	for _, bundle := range bundles {
		fmt.Fprintf(&prompt, "\n- <route>inspect:%s</route>: %s", bundle.Name, bundle.Description)
	}
	if len(bundles) >= 2 {
		fmt.Fprintf(
			&prompt,
			"\nOnly when two capabilities are genuinely required, join two listed names with +, for example <route>inspect:%s+%s</route>.",
			bundles[0].Name,
			bundles[1].Name,
		)
	}
	prompt.WriteString(`
Examples:
User: 写一个Python冒泡排序
Assistant: <route>respond</route>
User: 解释什么是快速排序
Assistant: <route>respond</route>
User: 你会哪些工具？
Assistant: <route>respond</route>`)
	for _, bundle := range bundles {
		if bundle.Name == ToolBundleWorkspace {
			fmt.Fprintf(&prompt, `
User: Read README.md and report its title
Assistant: <route>inspect:workspace</route>
User: 搜索代码里所有 TODO
Assistant: <route>inspect:workspace</route>`)
			break
		}
	}
	prompt.WriteString(`
Do not answer the user and do not output placeholder words.`)
	return prompt.String()
}

func (G1IProgressiveToolRouteProtocol) Parse(value string, finish continuation.FinishReason, bundles []ToolBundle) (ToolRouteDecision, error) {
	candidate := strings.TrimSpace(value)
	// Strip a leading think block first, like G1IRouteProtocol does: a reasoning
	// model opens its answer with <think>...</think> before the envelope.
	if match := leadingThinkBlocks.FindStringIndex(candidate); match != nil && match[0] == 0 {
		candidate = strings.TrimSpace(candidate[match[1]:])
	}
	// Locate the envelope anywhere, not only at the very start. RWKV routinely
	// prefaces the tag with prose ("我需要先创建目标目录...\n<route>inspect:X</route>");
	// requiring <route> as a strict prefix rejected every such (correct) route and
	// degraded the whole turn to respond. A complete envelope is authoritative
	// regardless of finish_reason; only when none is present does a length-
	// truncated generation fall back to the token-limit error.
	open, closeTag := "<route>", "</route>"
	start := strings.Index(candidate, open)
	if start < 0 {
		if finish == continuation.FinishLength {
			return ToolRouteDecision{}, ErrRouteTokenLimit
		}
		return ToolRouteDecision{}, fmt.Errorf("%w: progressive route envelope is missing or incomplete", ErrProtocol)
	}
	payload, closed := envelopeContent(candidate[start:], open, closeTag)
	if !closed && finish != continuation.FinishStop {
		if finish == continuation.FinishLength {
			return ToolRouteDecision{}, ErrRouteTokenLimit
		}
		return ToolRouteDecision{}, fmt.Errorf("%w: progressive route envelope is missing or incomplete", ErrProtocol)
	}
	if payload == string(RouteRespond) {
		return ToolRouteDecision{Route: RouteRespond}, nil
	}
	if !strings.HasPrefix(payload, string(RouteInspect)+":") {
		return ToolRouteDecision{}, fmt.Errorf("%w: invalid progressive route %q", ErrProtocol, payload)
	}
	names := strings.Split(strings.TrimPrefix(payload, string(RouteInspect)+":"), "+")
	if len(names) < 1 || len(names) > 2 {
		return ToolRouteDecision{}, fmt.Errorf("%w: progressive route must select one or two bundles", ErrProtocol)
	}
	known := make(map[string]struct{}, len(bundles))
	for _, bundle := range bundles {
		known[bundle.Name] = struct{}{}
	}
	seen := make(map[string]struct{}, len(names))
	for _, name := range names {
		if _, ok := known[name]; !ok {
			return ToolRouteDecision{}, fmt.Errorf("%w: unknown tool bundle %q", ErrProtocol, name)
		}
		if _, duplicate := seen[name]; duplicate {
			return ToolRouteDecision{}, fmt.Errorf("%w: duplicate tool bundle %q", ErrProtocol, name)
		}
		seen[name] = struct{}{}
	}
	return ToolRouteDecision{Route: RouteInspect, Bundles: names}, nil
}

func (G1IProgressiveToolRouteProtocol) Correction(_ error, bundles []ToolBundle) string {
	routes := make([]string, 0, len(bundles)+1)
	routes = append(routes, "<route>respond</route>")
	for _, bundle := range bundles {
		routes = append(routes, "<route>inspect:"+bundle.Name+"</route>")
	}
	return "Your previous route was invalid. Output exactly one concrete route from this list and nothing else: " + strings.Join(routes, ", ") + "."
}

func (G1IProgressiveToolRouteProtocol) Stops() []string {
	return []string{"</route>", "\nUser:", "\nSystem:", "\nTool:"}
}

// G1IRouteProtocol asks the model whether the committed conversation already
// contains enough evidence to answer. It deliberately does not expose tool
// names or schemas.
type G1IRouteProtocol struct{}

func (G1IRouteProtocol) ID() string {
	return G1IRouteProtocolV1
}

func (G1IRouteProtocol) Instructions() string {
	return strings.TrimSpace(`Classify whether answering the current user message correctly requires NEW evidence from available read-only tools.
Output exactly one route and nothing else:
- <route>respond</route>: casual conversation, general knowledge, questions about which tools/capabilities are available, or an answer already supported by the committed conversation.
- <route>inspect</route>: the answer requires current external facts, local files, deterministic calculation over tool data, or another read-only lookup now.
If required arguments are missing or ambiguous, route to respond so the assistant can ask a clarifying question instead of guessing.
Asking ABOUT available tools never requires USING those tools. Route capability questions to respond.
Do not answer the user. Do not guess file contents, locations, current conditions, or provider facts.
Examples:
User: 你好
Assistant: <route>respond</route>
User: What tools can you use?
Assistant: <route>respond</route>
User: 你有哪些工具？不要调用它们。
Assistant: <route>respond</route>
User: Read README.md and report its title.
Assistant: <route>inspect</route>
User: 今天上海天气怎么样？
Assistant: <route>inspect</route>
User: 看一下 notes 目录里这周的开销。
Assistant: <route>inspect</route>
User: 帮我查一下天气。
Assistant: <route>respond</route>
Earlier assistant: README.md is titled Example.
User: What was that title?
Assistant: <route>respond</route>`)
}

// ErrRouteTokenLimit marks a route classification truncated by its own budget.
// The route stage runs on a very small token budget, so a thinking model can
// exhaust it before emitting the envelope.
var ErrRouteTokenLimit = fmt.Errorf("%w: route reached the output token limit", ErrProtocol)

func (G1IRouteProtocol) Parse(
	value string,
	finish continuation.FinishReason,
) (Route, error) {
	candidate := strings.TrimSpace(value)
	if match := leadingThinkBlocks.FindStringIndex(candidate); match != nil && match[0] == 0 {
		candidate = strings.TrimSpace(candidate[match[1]:])
	}
	if strings.HasPrefix(candidate, "<think>") {
		return "", ErrUnclosedThink
	}
	if finish == continuation.FinishLength {
		return "", ErrRouteTokenLimit
	}
	const (
		open  = "<route>"
		close = "</route>"
	)
	if !strings.HasPrefix(candidate, open) {
		return "", fmt.Errorf("%w: route envelope is missing", ErrProtocol)
	}
	payload, closed := envelopeContent(candidate, open, close)
	if !closed && finish != continuation.FinishStop {
		return "", fmt.Errorf("%w: incomplete route envelope", ErrProtocol)
	}
	switch Route(payload) {
	case RouteRespond, RouteInspect:
		return Route(payload), nil
	default:
		return "", fmt.Errorf("%w: invalid route %q", ErrProtocol, payload)
	}
}

func (G1IRouteProtocol) Correction(err error) string {
	const contract = "Output exactly <route>respond</route> or <route>inspect</route> and nothing else."
	switch {
	case errors.Is(err, ErrUnclosedThink):
		return "Your previous reasoning never finished and was cut off. Do not reason about this. " +
			"Close it with </think> immediately, then classify in one step. " + contract
	case errors.Is(err, ErrRouteTokenLimit):
		return "Your previous route was cut off before it produced an envelope. Do not explain. " +
			contract
	default:
		return "Your previous route was invalid. " + contract
	}
}

func (G1IRouteProtocol) Stops() []string {
	return []string{"</route>", "\nUser:", "\nSystem:", "\nTool:"}
}

const maxRoutingHistoryMessages = 8

func routingHistory(history []Message) []Message {
	filtered := make([]Message, 0, min(len(history), maxRoutingHistoryMessages))
	for _, message := range history {
		if message.Role != RoleUser && message.Role != RoleAssistant {
			continue
		}
		if message.Role == RoleAssistant &&
			strings.HasPrefix(strings.TrimSpace(message.Content), "<tool_call>") {
			continue
		}
		filtered = append(filtered, message)
	}
	if len(filtered) > maxRoutingHistoryMessages {
		filtered = filtered[len(filtered)-maxRoutingHistoryMessages:]
	}
	return filtered
}
