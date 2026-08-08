//go:build chatcompletions

package chatcompletions

import (
	"context"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

func TestRemoteChatCompletionsIntegration(t *testing.T) {
	endpoint := strings.TrimSpace(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_URL"))
	model := strings.TrimSpace(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_MODEL"))
	if endpoint == "" || model == "" {
		t.Skip("set CHAT_COMPLETIONS_INTEGRATION_URL and CHAT_COMPLETIONS_INTEGRATION_MODEL")
	}
	thinking, err := ParseThinkingMode(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_THINKING"))
	if err != nil {
		t.Fatal(err)
	}
	promptMode, err := ParsePromptMode(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_PROMPT_MODE"))
	if err != nil {
		t.Fatal(err)
	}
	client, err := New(Config{
		Endpoint:   endpoint,
		Model:      model,
		APIKey:     os.Getenv("CHAT_COMPLETIONS_INTEGRATION_API_KEY"),
		Thinking:   thinking,
		PromptMode: promptMode,
		TokenLimit: TokenLimitField(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_TOKEN_LIMIT_FIELD")),
	})
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	request := continuation.Request{
		Prompt:          "System: Return only the requested marker.\n\nUser: Reply exactly CHAT_OK.\n\nAssistant:",
		MaxOutputTokens: 32,
		Stops:           []string{"\nUser:", "\nSystem:"},
		Sampling: continuation.Sampling{
			Temperature:  1,
			TopK:         1,
			TopP:         1,
			PenaltyDecay: 1,
		},
	}
	if thinking == ThinkingEnabled {
		request.MaxOutputTokens = 128
	}
	var text string
	if promptMode == PromptNativeChat {
		result, completeErr := client.Complete(ctx, toolchat.Request{
			Messages: []toolchat.Message{
				{Role: toolchat.RoleSystem, Content: "Return only the requested marker."},
				{Role: toolchat.RoleUser, Content: "Reply exactly CHAT_OK."},
			},
			MaxOutputTokens: request.MaxOutputTokens,
			Stops:           request.Stops,
			Sampling:        request.Sampling,
		}, nil)
		err = completeErr
		text = result.Content
	} else {
		result, continueErr := client.Continue(ctx, request, nil)
		err = continueErr
		text = result.Text
	}
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(text, "CHAT_OK") {
		t.Fatalf("response = %q, want CHAT_OK", text)
	}
}

func TestRemoteChatCompletionsNativeToolIntegration(t *testing.T) {
	endpoint := strings.TrimSpace(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_URL"))
	model := strings.TrimSpace(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_MODEL"))
	if endpoint == "" || model == "" {
		t.Skip("set CHAT_COMPLETIONS_INTEGRATION_URL and CHAT_COMPLETIONS_INTEGRATION_MODEL")
	}
	thinking, err := ParseThinkingMode(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_THINKING"))
	if err != nil {
		t.Fatal(err)
	}
	tokenLimit, err := ParseTokenLimitField(os.Getenv("CHAT_COMPLETIONS_INTEGRATION_TOKEN_LIMIT_FIELD"))
	if err != nil {
		t.Fatal(err)
	}
	client, err := New(Config{
		Endpoint:   endpoint,
		Model:      model,
		APIKey:     os.Getenv("CHAT_COMPLETIONS_INTEGRATION_API_KEY"),
		Thinking:   thinking,
		PromptMode: PromptNativeChat,
		TokenLimit: tokenLimit,
	})
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 45*time.Second)
	defer cancel()
	sampling := continuation.Sampling{Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1}
	toolMaxOutputTokens := 64
	answerMaxOutputTokens := 32
	if thinking == ThinkingEnabled {
		toolMaxOutputTokens = 256
		answerMaxOutputTokens = 128
	}
	tools := []toolchat.Tool{{
		Name:        "echo_marker",
		Description: "Return the supplied marker unchanged.",
		Parameters: []byte(
			`{"type":"object","properties":{"marker":{"type":"string"}},"required":["marker"],"additionalProperties":false}`,
		),
		Strict: true,
	}}
	first, err := client.Complete(ctx, toolchat.Request{
		Messages: []toolchat.Message{
			{Role: toolchat.RoleSystem, Content: "Call the supplied function exactly once."},
			{Role: toolchat.RoleUser, Content: "Call echo_marker with marker CHAT_TOOL_OK."},
		},
		Tools:           tools,
		ToolChoice:      toolchat.ToolChoiceRequired,
		MaxOutputTokens: toolMaxOutputTokens,
		Sampling:        sampling,
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	if len(first.ToolCalls) != 1 || first.ToolCalls[0].Name != "echo_marker" {
		t.Fatalf("first response = %+v", first)
	}
	call := first.ToolCalls[0]
	second, err := client.Complete(ctx, toolchat.Request{
		Messages: []toolchat.Message{
			{Role: toolchat.RoleSystem, Content: "After the tool result, return only its marker."},
			{Role: toolchat.RoleUser, Content: "Call echo_marker with marker CHAT_TOOL_OK."},
			{Role: toolchat.RoleAssistant, ToolCalls: []toolchat.ToolCall{call}},
			{Role: toolchat.RoleTool, ToolCallID: call.ID, Content: `{"marker":"CHAT_TOOL_OK"}`},
		},
		ToolChoice:      toolchat.ToolChoiceNone,
		MaxOutputTokens: answerMaxOutputTokens,
		Sampling:        sampling,
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(second.Content, "CHAT_TOOL_OK") {
		t.Fatalf("second response = %+v", second)
	}
}
