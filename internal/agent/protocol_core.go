package agent

import (
	"encoding/json"
	"errors"
	"fmt"
	"regexp"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// Protocol, renderer and route identifiers are a public contract: eval
// manifests record them verbatim, so archived runs stay comparable only while
// each string keeps its exact spelling. They live together here so that adding
// a profile means adding one line to this block rather than an inline literal
// next to an ID method.
const (
	// G1IEnvelopeProtocolV1 is the default product XML <tool_call>/<answer>
	// envelope protocol.
	G1IEnvelopeProtocolV1 = "rwkv-g1i-envelope-v1"
	// G1IFunctionProtocolV1 is the benchmark fenced-JSON function protocol with
	// submit termination. G1IProductFunctionProtocolV1 is its product variant,
	// which answers in Markdown instead of gating on submit.
	G1IFunctionProtocolV1        = "rwkv-g1i-functions-v1"
	G1IProductFunctionProtocolV1 = "rwkv-g1i-functions-product-v1"

	// RWKVPromptRendererV2 renders the XML chat transcript.
	RWKVPromptRendererV2 = "rwkv-chat-continuation-v2"
	// G1IFunctionRendererV1 renders the trained G1i function transcript.
	// G1IProductFunctionRendererV1 is its product variant.
	G1IFunctionRendererV1        = "rwkv-g1i-functions-continuation-v1"
	G1IProductFunctionRendererV1 = "rwkv-g1i-functions-product-continuation-v1"

	// G1IRouteProtocolV1 is the respond/inspect route. G1IToolRouteProtocolV1
	// is the progressive variant that also selects tool bundles.
	G1IRouteProtocolV1     = "rwkv-g1i-route-v1"
	G1IToolRouteProtocolV1 = "rwkv-g1i-tool-route-v1"
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

// Protocol capability predicates. The Runner branches on these instead of
// naming a concrete protocol type at each call site.

// preservesToolOrder reports whether the protocol keeps the assistant/tool
// message pair in transcript order rather than folding results into one turn.
func preservesToolOrder(protocol ActionProtocol) bool {
	_, ok := protocol.(G1IFunctionProtocol)
	return ok
}

// allowsRepeatedToolCalls reports whether the protocol lets an identical call
// run again. Only the upstream Primitive Bench controller does.
func allowsRepeatedToolCalls(protocol ActionProtocol) bool {
	value, ok := protocol.(G1IFunctionProtocol)
	return ok && value.AllowRepeatedCalls
}
