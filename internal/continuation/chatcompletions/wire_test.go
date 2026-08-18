//go:build chatcompletions

package chatcompletions

import "encoding/json"

type message struct {
	Role             string     `json:"role"`
	Content          *string    `json:"content,omitempty"`
	ReasoningContent string     `json:"reasoning_content,omitempty"`
	ToolCalls        []toolCall `json:"tool_calls,omitempty"`
	ToolCallID       string     `json:"tool_call_id,omitempty"`
}

type toolCall struct {
	ID       string       `json:"id"`
	Type     string       `json:"type"`
	Function functionCall `json:"function"`
}

type functionCall struct {
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

type requestTool struct {
	Type     string          `json:"type"`
	Function requestFunction `json:"function"`
}

type requestFunction struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Parameters  json.RawMessage `json:"parameters"`
	Strict      bool            `json:"strict"`
}

type thinkingBody struct {
	Type ThinkingMode `json:"type"`
}

type chatTemplateKwargs struct {
	EnableThinking *bool `json:"enable_thinking,omitempty"`
}

type requestBody struct {
	Model               string              `json:"model"`
	Messages            []message           `json:"messages"`
	Tools               []requestTool       `json:"tools,omitempty"`
	ToolChoice          string              `json:"tool_choice,omitempty"`
	ParallelToolCalls   *bool               `json:"parallel_tool_calls,omitempty"`
	MaxCompletionTokens int                 `json:"max_completion_tokens,omitempty"`
	MaxTokens           int                 `json:"max_tokens,omitempty"`
	Stop                []string            `json:"stop,omitempty"`
	Temperature         float32             `json:"temperature"`
	TopP                float32             `json:"top_p"`
	PresencePenalty     float32             `json:"presence_penalty"`
	FrequencyPenalty    float32             `json:"frequency_penalty"`
	Seed                *int64              `json:"seed,omitempty"`
	Thinking            *thinkingBody       `json:"thinking,omitempty"`
	ChatTemplateKwargs  *chatTemplateKwargs `json:"chat_template_kwargs,omitempty"`
	Stream              bool                `json:"stream"`
}
