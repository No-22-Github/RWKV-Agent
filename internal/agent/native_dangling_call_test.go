package agent

import (
	"context"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// assertNativeToolCallsAnswered mirrors the Chat Completions history check:
// every assistant tool_call must be answered by a tool message before the
// next system, user or assistant message, and before the completion.
func assertNativeToolCallsAnswered(t *testing.T, index int, messages []toolchat.Message) {
	t.Helper()
	pending := make(map[string]struct{})
	for position, message := range messages {
		switch message.Role {
		case toolchat.RoleTool:
			if _, ok := pending[message.ToolCallID]; !ok {
				t.Fatalf("request %d message %d: tool_call_id %q has no pending call", index, position, message.ToolCallID)
			}
			delete(pending, message.ToolCallID)
		default:
			if len(pending) > 0 {
				t.Fatalf("request %d message %d (%s): pending tool calls %v\n%+v",
					index, position, message.Role, pending, messages)
			}
			for _, call := range message.ToolCalls {
				pending[call.ID] = struct{}{}
			}
		}
	}
	if len(pending) > 0 {
		t.Fatalf("request %d ends with pending tool calls %v", index, pending)
	}
}

// TestNativeDuplicateThenForcedAnswerKeepsToolCallsAnswered reproduces the
// teacher-k1 failure: a duplicate call forces the answer stage, the model
// calls a tool again there, and the stage-violation retry used to leave that
// assistant tool_call without a tool message, which Chat Completions rejects.
func TestNativeDuplicateThenForcedAnswerKeepsToolCallsAnswered(t *testing.T) {
	t.Parallel()
	base := ProductHarnessOptions(ProductHarnessConfig{
		MaxSteps:         6,
		TracePromptBytes: DefaultTracePromptBytes,
		Generation:       continuation.Request{Model: "native-model", MaxOutputTokens: 256},
	})
	spec := wire.Default()
	spec.Format = wire.FormatMDFence
	spec.Transport = wire.TransportNative
	options, err := OptionsWithWire(base, spec)
	if err != nil {
		t.Fatal(err)
	}
	call := func(id string) toolchat.Result {
		return toolchat.Result{
			ToolCalls: []toolchat.ToolCall{{
				ID:        id,
				Name:      "echo",
				Arguments: `{"value":"ping"}`,
			}},
			FinishReason: continuation.FinishToolCalls,
		}
	}
	generator := &scriptedNativeGenerator{results: []toolchat.Result{
		call("call_1"),
		call("call_2"), // duplicate: rejected, forces the answer stage
		call("call_3"), // tool call in the answer stage: stage violation
		{Content: "The echo tool returned ping.", FinishReason: continuation.FinishStop},
	}}
	runner, err := NewRunner(generator, []Tool{nativeEchoTool{}}, options)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Check the echo tool")
	if err != nil {
		t.Fatal(err)
	}
	if result.ForcedAnswerReason != forcedAnswerDuplicateCall {
		t.Fatalf("forced answer reason = %q, want %q", result.ForcedAnswerReason, forcedAnswerDuplicateCall)
	}
	if result.Output != "The echo tool returned ping." {
		t.Fatalf("output = %q", result.Output)
	}
	if len(generator.requests) != 4 {
		t.Fatalf("native completions = %d, want 4", len(generator.requests))
	}
	for index, request := range generator.requests {
		assertNativeToolCallsAnswered(t, index, request.Messages)
	}
	// The rejected answer-stage call is answered by its own tool message.
	var answered bool
	for _, message := range generator.requests[3].Messages {
		if message.Role == toolchat.RoleTool && message.ToolCallID == "call_3" &&
			strings.Contains(message.Content, "rejected and not executed") {
			answered = true
		}
	}
	if !answered {
		t.Fatalf("call_3 has no tool message: %+v", generator.requests[3].Messages)
	}
}

func TestNativeMessagesClosesDanglingToolCall(t *testing.T) {
	t.Parallel()
	messages := nativeMessages([]Message{
		{Role: RoleSystem, Content: "system"},
		{Role: RoleUser, Content: "task"},
		{Role: RoleAssistant, ToolCalls: []toolchat.ToolCall{{ID: "call_x", Name: "echo", Arguments: `{}`}}},
		{Role: RoleUser, Content: "Tools are unavailable in the final answer stage."},
	})
	assertNativeToolCallsAnswered(t, 0, messages)
	if len(messages) != 5 || messages[3].Role != toolchat.RoleTool || messages[3].ToolCallID != "call_x" {
		t.Fatalf("messages = %+v", messages)
	}
}
