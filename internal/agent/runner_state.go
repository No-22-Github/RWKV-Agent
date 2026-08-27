package agent

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// History returns a copy of the committed multi-turn transcript. The control
// prompt is intentionally excluded.
func (r *Runner) History() []Message {
	r.stateMu.RLock()
	defer r.stateMu.RUnlock()
	return cloneMessages(r.history)
}

// Reset clears committed conversation history. It does not change the tool
// registry or generation configuration.
func (r *Runner) Reset() {
	r.runMu.Lock()
	defer r.runMu.Unlock()
	r.stateMu.Lock()
	r.history = nil
	r.stateMu.Unlock()
}

// RestoreHistory replaces the committed transcript after validating that it
// contains only conversation roles. It is intended for application-level
// persistence; the control prompt and runtime tool registry are never stored.
func (r *Runner) RestoreHistory(messages []Message) error {
	for index, message := range messages {
		switch message.Role {
		case RoleUser, RoleAssistant, RoleTool:
		default:
			return fmt.Errorf("history message %d has unsupported role %q", index, message.Role)
		}
	}
	r.runMu.Lock()
	defer r.runMu.Unlock()
	r.stateMu.Lock()
	r.history = cloneMessages(messages)
	r.stateMu.Unlock()
	return nil
}

func (r *Runner) commit(messages []Message) {
	r.stateMu.Lock()
	r.history = append(r.history, cloneMessages(messages)...)
	r.stateMu.Unlock()
}

func cloneMessages(messages []Message) []Message {
	result := append([]Message(nil), messages...)
	for index := range result {
		result[index].ToolCalls = append([]toolchat.ToolCall(nil), result[index].ToolCalls...)
	}
	return result
}

func canonicalToolCall(action Action) string {
	var arguments bytes.Buffer
	if err := json.Compact(&arguments, action.Arguments); err != nil {
		arguments.Write(action.Arguments)
	}
	return action.Name + "\x00" + arguments.String()
}

func (r *Runner) observe(event Event, observer func(Event)) {
	if r.options.Observe != nil {
		r.options.Observe(event)
	}
	if observer != nil {
		observer(event)
	}
}

type toolEventObserverKey struct{}

func withToolEventObserver(ctx context.Context, observer func(Event)) context.Context {
	return context.WithValue(ctx, toolEventObserverKey{}, observer)
}

// EmitToolEvent forwards a nested tool event through the observer attached by
// Runner. Calls outside tool execution are harmless no-ops.
func EmitToolEvent(ctx context.Context, event Event) {
	observer, _ := ctx.Value(toolEventObserverKey{}).(func(Event))
	if observer != nil {
		observer(event)
	}
}

func cloneSubagentTraces(values []SubagentTrace) []SubagentTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]SubagentTrace, len(values))
	copy(result, values)
	for index := range result {
		result[index].Bundles = append([]string(nil), values[index].Bundles...)
		result[index].Sources = append([]string(nil), values[index].Sources...)
		result[index].Steps = append([]SubagentStep(nil), values[index].Steps...)
		for step := range result[index].Steps {
			result[index].Steps[step].Arguments = append(json.RawMessage(nil), values[index].Steps[step].Arguments...)
		}
	}
	return result
}

type toolResult struct {
	OK     bool   `json:"ok"`
	Tool   string `json:"tool"`
	Result any    `json:"result,omitempty"`
	Error  string `json:"error,omitempty"`
}
