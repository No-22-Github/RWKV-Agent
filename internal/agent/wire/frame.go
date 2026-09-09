package wire

import "github.com/no22/RWKV-Agent/internal/inference"

// Assistant-opening byte constants. They live here, next to the axis that
// selects them, so the runner, the golden fixtures and the explain output all
// read the same bytes. The values are measured artifacts: the compact deep
// anchor has no space after the colon, and the half-open think prefix withholds
// the ">" on purpose (">{" is one token on this tokenizer).
const (
	// EnvelopePrefix opens the XML tool-call envelope.
	EnvelopePrefix = "<tool_call>"
	// EnvelopeClose closes the XML tool-call envelope.
	EnvelopeClose = "</tool_call>"
	// FencePrefix opens the fenced-JSON function call.
	FencePrefix = "```json\n"
	// CallBodyAnchor is the object continuation the model writes after a
	// fence: the deep-anchor body. The compact spelling (no space after the
	// colon) is a measured artifact.
	CallBodyAnchor = "{\"name\":\""
	// ArrayCallAnchor is the parallel-call continuation.
	ArrayCallAnchor = "[{\"name\":\""
	// DeepFencePrefix is FencePrefix extended into the call object.
	DeepFencePrefix = FencePrefix + CallBodyAnchor
	// FakeThinkHalfPrefix is the half-open think block; the model completes it.
	FakeThinkHalfPrefix = inference.ThinkBlockFast
	// FakeThinkClosedPrefix closes the block in the prompt.
	FakeThinkClosedPrefix = inference.ThinkBlockClosed
)

// Frame is the assistant-opening prefill for one generation. Inject means the
// bytes belong in the continuation prompt; Strip is the byte sequence the
// harness removes again before parsing so its own framing is never recorded as
// a model repair.
type Frame struct {
	Text   string
	Inject bool
	Strip  string
}

// DecisionState is the turn state that selects a decision-stage prefill. It is
// deliberately small: route, whether any tool action has run in this turn, and
// whether the terminal tool has completed.
type DecisionState struct {
	// Inspect is false on the respond route, where the model answers directly
	// and no tool format may be pre-filled.
	Inspect bool
	// AfterTool is true once at least one tool action has been attempted in
	// this turn.
	AfterTool bool
	// TerminalComplete reports whether the terminal tool has succeeded (or
	// whether the turn has no terminal tool).
	TerminalComplete bool
}

// DecisionFrame is the single owner of the decision-stage assistant opening.
// Every prefill decision in the runner goes through it: the turn no longer
// mutates a prefix field at tool transitions, so the policy cannot drift from
// the spec.
//
// Rules, in order:
//
//  1. The respond route and the answer stage never pre-fill a tool format.
//  2. fake-think is a product experiment that owns the opening on every
//     decision step (including after a tool result), because it is the only
//     mechanism that replaces the format anchor rather than adding to it.
//  3. The format anchors (envelope, fence, deep fence) are armed on the first
//     decision and re-armed after a tool step only while the terminal tool has
//     not completed. A completed terminal tool means the next generation is an
//     answer, so the anchor would be wrong.
func (s Spec) DecisionFrame(state DecisionState) Frame {
	if !state.Inspect {
		return Frame{}
	}
	if s.Transcript == TranscriptBenchmark {
		// The benchmark renderer ends every decision prompt inside the fence
		// itself (plain answers only return after a PASS). Injecting the
		// product fence on top would double it.
		return Frame{}
	}
	switch s.Prefill {
	case PrefillFakeThinkHalf:
		return Frame{
			Text:   FakeThinkHalfPrefix,
			Inject: true,
			Strip:  FakeThinkHalfPrefix + ">",
		}
	case PrefillFakeThinkClosed:
		return Frame{
			Text:   FakeThinkClosedPrefix,
			Inject: true,
			Strip:  FakeThinkClosedPrefix,
		}
	}
	if state.AfterTool && state.TerminalComplete {
		return Frame{}
	}
	switch s.Prefill {
	case PrefillEnvelope:
		return Frame{Text: EnvelopePrefix, Inject: true}
	case PrefillFence:
		return Frame{Text: FencePrefix, Inject: true}
	case PrefillDeepFence:
		return Frame{Text: DeepFencePrefix, Inject: true}
	default:
		return Frame{}
	}
}
