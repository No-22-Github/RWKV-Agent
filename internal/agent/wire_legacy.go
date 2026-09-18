package agent

import (
	"fmt"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// WireSpecOf describes an Options value as a canonical wire.Spec. It is the
// bridge between the existing runtime fields and the canonical description:
// every construction path keeps working, while the Spec becomes the single
// description recorded in manifests and compared across runs.
//
// When Options.Wire is set it is returned after validation. Otherwise the spec
// is derived from the protocol/renderer pair and the loop fields.
//
// The derived spec is returned even when validation fails, together with the
// error, so a manifest can record an invalid legacy combination (for example
// XML + thinking + router, whose envelope prefix the runner silently drops).
// NewRunner rejects such a combination once P2 lands.
func WireSpecOf(options Options) (wire.Spec, error) {
	if options.Wire != nil {
		return *options.Wire, options.Wire.Validate()
	}
	spec := wire.Default()
	allowRepeated := false
	switch protocol := options.Protocol.(type) {
	case nil:
		// applyRunnerDefaults selects the XML protocol; the default spec
		// already describes it.
	case G1Protocol:
		spec.Format = wire.FormatXML
		spec.Transcript = wire.TranscriptProduct
		spec.Thinking = wire.Thinking(rendererThinkingMode(options.Renderer))
		if protocol.AlignQwen36 {
			spec.Align = wire.AlignQwen36
		}
		if protocol.OneStage {
			spec.Stages = wire.StagesOne
		}
		if protocol.FewShot {
			spec.Control = wire.ControlFewShot
		}
		if protocol.NoCallDemo {
			spec.Control = wire.ControlBaseNoCall
		}
		if protocol.GreetingExamples {
			spec.Control = wire.ControlGreeting
		}
		if protocol.BareExamples {
			spec.Control = wire.ControlBare
		}
		if protocol.SemanticNoTool {
			spec.Abstain = wire.AbstainNoTool
		}
		if (options.Router != nil || options.ToolRouter != nil) &&
			spec.Thinking == wire.ThinkingOff {
			// The runner arms the envelope prefix only on an inspect decision,
			// and the chat renderer refuses to inject any prefix while a think
			// block owns the opening. The spec records the effective policy:
			// with thinking on, there is no envelope prefill at all.
			spec.Prefill = wire.PrefillEnvelope
		}
	case G1FunctionProtocol:
		spec.Format = wire.FormatMDFence
		spec.Transcript = wire.TranscriptProduct
		if !protocol.Product {
			spec.Transcript = wire.TranscriptBenchmark
		}
		if protocol.SemanticNoTool {
			spec.Abstain = wire.AbstainNoTool
		}
		if protocol.SubagentRawFeedback {
			spec.SubagentFeedback = wire.SubagentFeedbackRaw
		}
		allowRepeated = protocol.AllowRepeatedCalls
		spec.Prefill = wire.PrefillFence
		if renderer, ok := options.Renderer.(G1FunctionRenderer); ok {
			switch {
			case renderer.DecisionFakeThink && renderer.ClosedFakeThink:
				spec.Prefill = wire.PrefillFakeThinkClosed
			case renderer.DecisionFakeThink:
				spec.Prefill = wire.PrefillFakeThinkHalf
			case protocol.DeepToolAnchor:
				spec.Prefill = wire.PrefillDeepFence
			}
		} else if protocol.DeepToolAnchor {
			spec.Prefill = wire.PrefillDeepFence
		}
	default:
		return spec, fmt.Errorf("wire spec: unsupported protocol %T", options.Protocol)
	}
	switch {
	case options.ToolRouter != nil:
		spec.Route = wire.RouteProgressive
		spec.Catalog = wire.CatalogProgressive
	case options.Router != nil:
		spec.Route = wire.RouteRespondInspect
	}
	// The gate is a harness-level policy layered on the no_tool action; the
	// protocol only knows whether the action exists at all.
	switch options.NoToolGate {
	case "state":
		spec.Abstain = wire.AbstainNoToolGateState
	case "evidence":
		spec.Abstain = wire.AbstainNoToolGateEvidence
	}
	if options.NativeFirstCall == "auto" {
		spec.FirstCall = wire.FirstCallAuto
	}
	switch options.UserMerge {
	case "", "split":
	default:
		spec.UserMerge = wire.UserMerge(options.UserMerge)
	}
	if options.SourceHint == "on" {
		spec.SourceHint = wire.SourceHintOn
	}
	if options.TerminalTool != "" {
		spec.Terminal = wire.Terminal(options.TerminalTool)
	}
	if options.CompressFetch {
		spec.Feedback = wire.FeedbackCompressFetch
	}
	spec.Loop = wire.Loop{
		MaxSteps:                 options.MaxSteps,
		ProtocolRetries:          options.ProtocolRetries,
		RouteRetries:             options.RouteRetries,
		DecisionMaxOutputTokens:  options.DecisionMaxOutputTokens,
		AnswerMaxOutputTokens:    options.Generation.MaxOutputTokens,
		RouteMaxOutputTokens:     options.RouteMaxOutputTokens,
		DuplicateReplayLimit:     options.DuplicateReplayLimit,
		DuplicateRescueThreshold: options.DuplicateRescueThreshold,
		SameToolRescueLimit:      options.SameToolRescueLimit,
		AnswerStageLead:          options.AnswerStageLead,
		AllowRepeatedCalls:       allowRepeated,
	}
	return spec, spec.Validate()
}

// OptionsWithWire applies a Spec to base and returns the runtime Options. It
// is the single place that translates the canonical description into protocol,
// renderer, router, terminal and loop fields, so the longhand CLI flags, the
// preset shorthand, the API config and the eval suite defaults cannot drift
// apart.
//
// The native transport cannot be applied here: it is detected from the
// generator at NewRunner time. The spec is carried on Options.Wire for that
// reconciliation.
func OptionsWithWire(base Options, spec wire.Spec) (Options, error) {
	if err := spec.Validate(); err != nil {
		return Options{}, err
	}
	options := base
	switch spec.Format {
	case wire.FormatXML:
		options.Protocol = G1Protocol{
			FewShot:          spec.Control == wire.ControlFewShot,
			NoCallDemo:       spec.Control == wire.ControlBaseNoCall,
			GreetingExamples: spec.Control == wire.ControlGreeting,
			BareExamples:     spec.Control == wire.ControlBare,
			SemanticNoTool:   spec.Abstain != wire.AbstainNone,
			AlignQwen36:      spec.Align == wire.AlignQwen36,
			OneStage:         spec.Stages == wire.StagesOne,
			SourceHint:       spec.SourceHint == wire.SourceHintOn,
		}
		options.Renderer = RWKVChatRenderer{ThinkingMode: inference.ThinkingMode(spec.Thinking)}
	case wire.FormatMDFence:
		options.Protocol = G1FunctionProtocol{
			Product:             spec.Transcript == wire.TranscriptProduct,
			SemanticNoTool:      spec.Abstain != wire.AbstainNone,
			DeepToolAnchor:      spec.Prefill == wire.PrefillDeepFence,
			SubagentRawFeedback: spec.SubagentFeedback == wire.SubagentFeedbackRaw,
			AllowRepeatedCalls:  spec.Loop.AllowRepeatedCalls,
		}
		renderer := G1FunctionRenderer{Product: spec.Transcript == wire.TranscriptProduct}
		switch spec.Prefill {
		case wire.PrefillFakeThinkHalf:
			renderer.DecisionFakeThink = true
		case wire.PrefillFakeThinkClosed:
			renderer.DecisionFakeThink = true
			renderer.ClosedFakeThink = true
		}
		if spec.Transcript == wire.TranscriptBenchmark {
			// HasRunTests stays catalog-derived: the benchmark renderer flips
			// back to plain answers only after a PASS from run_tests.
			renderer.HasSubmit = spec.Terminal == wire.TerminalSubmit
		}
		options.Renderer = renderer
	default:
		return Options{}, fmt.Errorf("wire spec: unsupported format %q", spec.Format)
	}

	switch spec.Route {
	case wire.RouteNone:
		options.Router = nil
		options.ToolRouter = nil
	case wire.RouteRespondInspect:
		options.Router = G1RouteProtocol{}
		options.ToolRouter = nil
		options.RouteRenderer = RWKVChatRenderer{}
	case wire.RouteProgressive:
		options.ToolRouter = G1ProgressiveToolRouteProtocol{}
		options.Router = nil
		options.RouteRenderer = RWKVChatRenderer{}
	default:
		return Options{}, fmt.Errorf("wire spec: unsupported route %q", spec.Route)
	}

	switch spec.Terminal {
	case wire.TerminalNone, "":
		options.TerminalTool = ""
		options.EndOnTerminalTool = false
	default:
		options.TerminalTool = string(spec.Terminal)
		options.EndOnTerminalTool = true
	}

	switch spec.Abstain {
	case wire.AbstainNoToolGateState:
		options.NoToolGate = "state"
	case wire.AbstainNoToolGateEvidence:
		options.NoToolGate = "evidence"
	default:
		options.NoToolGate = ""
	}

	options.CompressFetch = spec.Feedback == wire.FeedbackCompressFetch

	if spec.FirstCall != "" {
		options.NativeFirstCall = string(spec.FirstCall)
	}
	if spec.UserMerge != "" {
		options.UserMerge = string(spec.UserMerge)
	}
	if spec.SourceHint != "" {
		options.SourceHint = string(spec.SourceHint)
	}

	if !spec.Loop.Zero() {
		options.MaxSteps = spec.Loop.MaxSteps
		options.ProtocolRetries = spec.Loop.ProtocolRetries
		options.RouteRetries = spec.Loop.RouteRetries
		options.DecisionMaxOutputTokens = spec.Loop.DecisionMaxOutputTokens
		options.RouteMaxOutputTokens = spec.Loop.RouteMaxOutputTokens
		options.DuplicateReplayLimit = spec.Loop.DuplicateReplayLimit
		options.DuplicateRescueThreshold = spec.Loop.DuplicateRescueThreshold
		options.SameToolRescueLimit = spec.Loop.SameToolRescueLimit
		options.AnswerStageLead = spec.Loop.AnswerStageLead
		options.Generation.MaxOutputTokens = spec.Loop.AnswerMaxOutputTokens
	}
	if spec.Route != wire.RouteNone && options.RouteRetries == 0 {
		// applyProgressiveTools has always granted the route stage one retry;
		// keep that behavior when the spec did not spell it out.
		options.RouteRetries = 1
	}
	options.Wire = &spec
	return options, nil
}
