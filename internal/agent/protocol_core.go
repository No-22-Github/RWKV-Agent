package agent

import (
	"encoding/json"
	"errors"
	"fmt"
	"regexp"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

const (
	G1IActionProtocolV1  = "rwkv-g1i-envelope-v1"
	RWKVPromptRendererV1 = "rwkv-chat-continuation-v1"
	RWKVPromptRendererV2 = "rwkv-chat-continuation-v2"
)

var leadingThinkBlocks = regexp.MustCompile(`(?s)\A\s*(?:<think>.*?</think>\s*)+`)

// Protocol failure classes that need targeted correction guidance. They wrap
// ErrProtocol so existing callers keep matching on that sentinel.
var (
	// ErrUnclosedThink marks a response whose leading think block never closed,
	// which in practice means reasoning ran away until the budget ran out.
	ErrUnclosedThink = fmt.Errorf("%w: incomplete leading think block", ErrProtocol)
	// ErrOutputTokenLimit marks a response truncated by the output budget.
	ErrOutputTokenLimit = fmt.Errorf("%w: model response reached the output token limit", ErrProtocol)
	// ErrToolEnvelopeMissing marks tool-like output that omitted the protocol's
	// required tool-call envelope.
	ErrToolEnvelopeMissing = fmt.Errorf("%w: tool call envelope missing", ErrProtocol)
	// ErrToolJSONDecode marks a recognized tool envelope whose JSON payload
	// could not be decoded.
	ErrToolJSONDecode = fmt.Errorf("%w: tool call JSON decode failed", ErrProtocol)
	// ErrToolShapeInvalid marks a decoded tool call with an invalid name or
	// arguments shape.
	ErrToolShapeInvalid = fmt.Errorf("%w: tool call shape invalid", ErrProtocol)
)

type ProtocolFailureClass string

const (
	ProtocolFailureToolEnvelopeMissing ProtocolFailureClass = "tool_envelope_missing"
	ProtocolFailureToolJSONDecode      ProtocolFailureClass = "tool_json_decode_failed"
	ProtocolFailureToolShapeInvalid    ProtocolFailureClass = "tool_shape_invalid"
)

// ProtocolFailureClassOf returns a stable class only for tool extraction
// failures. Ordinary final text and unrelated protocol failures remain
// unclassified rather than being mislabeled as tool-like output.
func ProtocolFailureClassOf(err error) ProtocolFailureClass {
	switch {
	case errors.Is(err, ErrToolEnvelopeMissing):
		return ProtocolFailureToolEnvelopeMissing
	case errors.Is(err, ErrToolJSONDecode):
		return ProtocolFailureToolJSONDecode
	case errors.Is(err, ErrToolShapeInvalid):
		return ProtocolFailureToolShapeInvalid
	default:
		return ""
	}
}

type Action struct {
	Type                    string               `json:"type"`
	Name                    string               `json:"name,omitempty"`
	Arguments               json.RawMessage      `json:"arguments,omitempty"`
	Content                 string               `json:"content,omitempty"`
	NoToolRationale         string               `json:"no_tool_rationale,omitempty"`
	NoToolAnswer            string               `json:"no_tool_answer,omitempty"`
	ProtocolRepaired        bool                 `json:"protocol_repaired,omitempty"`
	OriginalProtocolFailure ProtocolFailureClass `json:"original_protocol_failure,omitempty"`
}

const (
	ActionTypeFinal  = "final"
	ActionTypeTool   = "tool"
	ActionTypeNoTool = "no_tool"
)

type ActionProtocol interface {
	ID() string
	Instructions([]ToolSpec, inference.ThinkingMode) string
	Parse(string, continuation.FinishReason) (Action, error)
	Correction(error) string
	RecordAction(Action, string) string
	FormatToolResult(name string, callID string, payload string) string
	ToolCallPrefix() string
	PostToolReminder() string
	PrepareAnswer(
		messages []Message,
		unverified []string,
		thinkingMode inference.ThinkingMode,
	) ([]Message, string)
	Stops(GenerationStage) []string
}

type GenerationStage string

const (
	StageDecision GenerationStage = "decision"
	StageAnswer   GenerationStage = "answer"
)
