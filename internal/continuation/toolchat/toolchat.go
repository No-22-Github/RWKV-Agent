package toolchat

import (
	"context"
	"encoding/json"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

type Role string

const (
	RoleSystem    Role = "system"
	RoleUser      Role = "user"
	RoleAssistant Role = "assistant"
	RoleTool      Role = "tool"
)

type ToolCall struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

type Message struct {
	Role             Role       `json:"role"`
	Content          string     `json:"content,omitempty"`
	ReasoningContent string     `json:"reasoning_content,omitempty"`
	ToolCalls        []ToolCall `json:"tool_calls,omitempty"`
	ToolCallID       string     `json:"tool_call_id,omitempty"`
}

type Tool struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Parameters  json.RawMessage `json:"parameters"`
	Strict      bool            `json:"strict"`
}

type ToolChoice string

const (
	ToolChoiceNone     ToolChoice = "none"
	ToolChoiceAuto     ToolChoice = "auto"
	ToolChoiceRequired ToolChoice = "required"
)

type Request struct {
	Model             string
	Messages          []Message
	Tools             []Tool
	ToolChoice        ToolChoice
	AssistantPrefix   string
	MaxOutputTokens   int
	Stops             []string
	Sampling          continuation.Sampling
	ParallelToolCalls bool
}

type Result struct {
	Content          string
	ReasoningContent string
	ToolCalls        []ToolCall
	FinishReason     continuation.FinishReason
	Usage            continuation.Usage
}

type Completer interface {
	Complete(context.Context, Request, continuation.EventSink) (Result, error)
	NativeToolCalling() bool
}
