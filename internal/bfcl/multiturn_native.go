package bfcl

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// nativeStepper drives one multi-turn step through the provider's own tool
// channel (toolchat.Completer.Complete): the model receives a real chat message
// history plus a native tools array and returns structured tool_calls. This is
// the path that reproduces official Qwen numbers, so it deliberately carries no
// prefill anchor, no finish_task, no markdown preamble, and no wire-compat
// repair -- an empty tool_calls response is the official turn-end signal.
type nativeStepper struct {
	completer toolchat.Completer
}

func (s nativeStepper) Step(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, _ map[string]string, turn, step int, options MultiTurnRunnerOptions) (MultiTurnStepTrace, []toolchat.ToolCall, bool, error) {
	trace := MultiTurnStepTrace{Step: step, AssemblyMode: "native_fc"}
	tools, err := MultiTurnNativeTools(functions)
	if err != nil {
		return trace, nil, false, err
	}
	messages, err := multiTurnNativeMessages(transcript)
	if err != nil {
		return trace, nil, false, err
	}
	// The native request has no single prompt string; size it by the serialized
	// messages+tools instead, mirroring the single-turn native runner. Recorded
	// unconditionally as telemetry; a char-guard abort is terminal, never a parse
	// error (feeding a correction back would only make it larger).
	encoded, marshalErr := json.Marshal(struct {
		Messages []toolchat.Message `json:"messages"`
		Tools    []toolchat.Tool    `json:"tools"`
	}{Messages: messages, Tools: tools})
	if marshalErr != nil {
		return trace, nil, false, marshalErr
	}
	trace.PromptBytes = len(encoded)
	if options.MaxPromptChars > 0 && len(encoded) > options.MaxPromptChars {
		return trace, nil, false, &promptBudgetError{message: fmt.Sprintf("multi-turn native request %d bytes exceeds max_prompt_chars %d", len(encoded), options.MaxPromptChars)}
	}
	toolChoice := toolchat.ToolChoiceAuto
	parallelToolCalls := true
	if len(tools) == 0 {
		toolChoice = toolchat.ToolChoiceNone
		parallelToolCalls = false
	}
	started := time.Now()
	completion, err := s.completer.Complete(ctx, toolchat.Request{
		Model:           options.Model,
		Messages:        messages,
		Tools:           tools,
		ToolChoice:      toolChoice,
		MaxOutputTokens: options.MaxOutputTokens,
		Sampling: continuation.Sampling{
			Temperature:  options.Temperature,
			TopK:         1,
			TopP:         1,
			PenaltyDecay: 1,
		},
		ParallelToolCalls: parallelToolCalls,
	}, nil)
	trace.Latency = time.Since(started).Seconds()
	if err != nil {
		// A transport/provider failure is infrastructure, not a model failure, so
		// the case stays out of the scored denominator (matches the wrapped path).
		return trace, nil, false, &infrastructureError{err: err}
	}
	trace.GeneratedContent = strings.TrimSpace(completion.Content)
	trace.Content = trace.GeneratedContent
	trace.FinishReason = string(completion.FinishReason)
	trace.InputTokens = completion.Usage.PromptTokens
	trace.OutputTokens = completion.Usage.CompletionTokens
	trace.ToolCalls = completion.ToolCalls
	// Empty tool_calls ends the turn either way, matching official semantics (the
	// model emitting no call is the turn-end signal, and a truncated response that
	// never reached a call is scored as that failed turn -- not excluded). The
	// finish_reason is recorded so an inadequate --max-tokens (many "length"
	// truncations) is distinguishable from genuine non-convergence after the run.
	return trace, completion.ToolCalls, len(completion.ToolCalls) == 0, nil
}

// sanitizeToolName mirrors NativeTools: the OpenAI tools array forbids dotted
// names, so a BFCL name like "GorillaFileSystem.cd" becomes "GorillaFileSystem_cd".
// Multi-turn names are usually already flat, making this a no-op, but the
// transform and its inverse must be applied consistently.
func sanitizeToolName(name string) string {
	return strings.ReplaceAll(name, ".", "_")
}

// multiTurnNativeNames builds the sanitized->original map over the full catalog
// so the loop can un-sanitize any returned call before it reaches the simulator.
func multiTurnNativeNames(functions []MultiTurnFunction) (map[string]string, error) {
	names := make(map[string]string, len(functions))
	for _, function := range functions {
		sanitized := sanitizeToolName(function.Name)
		if previous, exists := names[sanitized]; exists && previous != function.Name {
			return nil, fmt.Errorf("multi-turn function name collision: %q and %q map to %q", previous, function.Name, sanitized)
		}
		names[sanitized] = function.Name
	}
	return names, nil
}

// MultiTurnNativeTools converts this turn's function docs into a native tools
// array through the shared schema rewrite (dict->object, float->number,
// tuple/list->array, any->string) so both paths present identical schemas.
func MultiTurnNativeTools(functions []MultiTurnFunction) ([]toolchat.Tool, error) {
	tools := make([]toolchat.Tool, 0, len(functions))
	for _, function := range functions {
		definition, err := decodeFunctionDefinition(function.Raw)
		if err != nil {
			return nil, fmt.Errorf("multi-turn function %q: %w", function.Name, err)
		}
		if strings.TrimSpace(definition.Name) == "" {
			return nil, fmt.Errorf("multi-turn function %q has no name", function.Name)
		}
		parameters, err := openAISchema(definition.Parameters)
		if err != nil {
			return nil, fmt.Errorf("multi-turn function %q parameters: %w", definition.Name, err)
		}
		tools = append(tools, toolchat.Tool{
			Name:        sanitizeToolName(definition.Name),
			Description: definition.Description,
			Parameters:  parameters,
			Strict:      false,
		})
	}
	return tools, nil
}

// multiTurnNativeMessages maps the running transcript to a native chat history.
// System/user/assistant text turns map one-to-one; an executed assistant step
// becomes an assistant message carrying its structured tool_calls; a Tool entry
// becomes one tool message per result, linked by tool_call_id.
func multiTurnNativeMessages(transcript []multiTurnTranscript) ([]toolchat.Message, error) {
	messages := make([]toolchat.Message, 0, len(transcript))
	for _, entry := range transcript {
		switch strings.ToLower(strings.TrimSpace(entry.Role)) {
		case "system":
			messages = append(messages, toolchat.Message{Role: toolchat.RoleSystem, Content: transcriptText(entry.Content)})
		case "assistant":
			if len(entry.ToolCalls) > 0 {
				messages = append(messages, toolchat.Message{Role: toolchat.RoleAssistant, ToolCalls: entry.ToolCalls})
				break
			}
			// A turn-ending native response is empty tool_calls with (often) empty
			// content. Such an assistant message carries no information and the API
			// rejects a content-less, call-less message, so drop it from history.
			text := transcriptText(entry.Content)
			if strings.TrimSpace(text) == "" {
				break
			}
			messages = append(messages, toolchat.Message{Role: toolchat.RoleAssistant, Content: text})
		case "tool":
			results, ok := entry.Content.([]string)
			if !ok {
				return nil, fmt.Errorf("multi-turn native tool entry content is %T, want []string", entry.Content)
			}
			for index, result := range results {
				id := ""
				if index < len(entry.CallIDs) {
					id = entry.CallIDs[index]
				}
				messages = append(messages, toolchat.Message{Role: toolchat.RoleTool, Content: result, ToolCallID: id})
			}
		default:
			messages = append(messages, toolchat.Message{Role: toolchat.RoleUser, Content: transcriptText(entry.Content)})
		}
	}
	return messages, nil
}

// transcriptText renders a transcript entry's Content as a string. Text turns
// hold a string directly; anything else is JSON-encoded (the wrapped renderer
// does the same for non-string content).
func transcriptText(content any) string {
	if text, ok := content.(string); ok {
		return text
	}
	encoded, err := json.Marshal(content)
	if err != nil {
		return ""
	}
	return string(encoded)
}
