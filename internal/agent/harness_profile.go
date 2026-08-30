package agent

import (
	"encoding/json"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// Loop-policy defaults shared by every harness profile. They are one set on
// purpose: the limits describe how much repetition the Runner tolerates before
// forcing an answer, which is a property of the model's looping habits rather
// than of the transcript format.
const (
	ProductDuplicateReplayLimit     = 2
	ProductDuplicateRescueThreshold = 3
	ProductSameToolRescueLimit      = 3
)

// ProductHarnessConfig contains the transport-neutral knobs shared by the App
// and product evaluations. Benchmark-specific protocols (Primitive and BFCL
// wrapped continuations) deliberately do not use this profile.
type ProductHarnessConfig struct {
	MaxSteps                 int
	DecisionMaxOutputTokens  int
	RouteMaxOutputTokens     int
	TracePromptBytes         int
	DuplicateReplayLimit     int
	DuplicateRescueThreshold int
	SameToolRescueLimit      int
	Generation               continuation.Request
	ProgressiveTools         bool
	ToolBundles              []ToolBundle
	SemanticNoTool           bool
	DecisionFakeThink        bool
	// ClosedFakeThink prefills the fully closed think block instead of the
	// half-open one. Only meaningful with DecisionFakeThink.
	ClosedFakeThink bool
	// DeepToolAnchor extends the decision prefill to `{"name":"`. It removes
	// every syntactic abstention exit, so pair it with SemanticNoTool.
	DeepToolAnchor bool
	TaskControl    string
	PostToolHook   func(string, json.RawMessage, any, error) string
	Observe        func(Event)
}

// ProductHarnessOptions is the single constructor for the optional Markdown
// continuation profile. It owns the protocol/renderer pairing, the optional
// progressive router, and the loop-policy wiring that must match between the
// App and product evals.
func ProductHarnessOptions(config ProductHarnessConfig) Options {
	options := Options{
		MaxSteps:                 config.MaxSteps,
		ProtocolRetries:          1,
		DecisionMaxOutputTokens:  config.DecisionMaxOutputTokens,
		ControlPrompt:            ControlPromptSystem,
		TaskControl:              config.TaskControl,
		TerminalTool:             "",
		EndOnTerminalTool:        false,
		DuplicateReplayLimit:     config.DuplicateReplayLimit,
		DuplicateRescueThreshold: config.DuplicateRescueThreshold,
		SameToolRescueLimit:      config.SameToolRescueLimit,
		PostToolHook:             config.PostToolHook,
		Protocol: G1IFunctionProtocol{
			Product:        true,
			SemanticNoTool: config.SemanticNoTool,
			DeepToolAnchor: config.DeepToolAnchor,
		},
		Renderer: G1IFunctionRenderer{
			Product:           true,
			DecisionFakeThink: config.DecisionFakeThink,
			ClosedFakeThink:   config.ClosedFakeThink,
		},
		Generation:       config.Generation,
		Observe:          config.Observe,
		TracePromptBytes: config.TracePromptBytes,
	}
	applyProgressiveTools(&options, config.ProgressiveTools, config.ToolBundles, config.RouteMaxOutputTokens)
	return options
}

// XMLHarnessConfig contains the knobs for the default XML envelope profile. It
// mirrors ProductHarnessConfig except for the fields that only the
// XML transcript supports.
type XMLHarnessConfig struct {
	MaxSteps                 int
	DecisionMaxOutputTokens  int
	RouteMaxOutputTokens     int
	TracePromptBytes         int
	DuplicateReplayLimit     int
	DuplicateRescueThreshold int
	SameToolRescueLimit      int
	Generation               continuation.Request
	ProgressiveTools         bool
	ToolBundles              []ToolBundle
	TaskControl              string
	PostToolHook             func(string, json.RawMessage, any, error) string
	Observe                  func(Event)
	// SemanticNoTool offers the same text-only abstention action as the product
	// profile, expressed as a <tool_call> envelope.
	SemanticNoTool bool
	// ThinkingMode is the one capability the product profile does not have: the
	// XML renderer can prefill a half-open think block for fast/full thinking.
	ThinkingMode inference.ThinkingMode
	// FewShot appends complete decision trajectories to the control prompt.
	// Only the XML protocol carries them.
	FewShot bool
}

// XMLHarnessOptions is the single constructor for the default XML envelope
// profile (--agent-protocol xml). It exists so the App and the
// CLI stop hand-rolling the same Options literal and drifting apart on the
// loop-policy limits.
func XMLHarnessOptions(config XMLHarnessConfig) Options {
	options := Options{
		MaxSteps:                 config.MaxSteps,
		ProtocolRetries:          1,
		DecisionMaxOutputTokens:  config.DecisionMaxOutputTokens,
		ControlPrompt:            ControlPromptSystem,
		TaskControl:              config.TaskControl,
		TerminalTool:             "",
		EndOnTerminalTool:        false,
		DuplicateReplayLimit:     config.DuplicateReplayLimit,
		DuplicateRescueThreshold: config.DuplicateRescueThreshold,
		SameToolRescueLimit:      config.SameToolRescueLimit,
		PostToolHook:             config.PostToolHook,
		Protocol: G1IProtocol{
			FewShot:        config.FewShot,
			SemanticNoTool: config.SemanticNoTool,
		},
		Renderer:         RWKVChatRenderer{ThinkingMode: config.ThinkingMode},
		Generation:       config.Generation,
		Observe:          config.Observe,
		TracePromptBytes: config.TracePromptBytes,
	}
	applyProgressiveTools(&options, config.ProgressiveTools, config.ToolBundles, config.RouteMaxOutputTokens)
	return options
}

// applyProgressiveTools wires the progressive tool router. The route renderer
// is always thinking-off: NewRunner rejects any other mode for the route stage,
// because a 16-token route budget cannot hold a think block.
func applyProgressiveTools(
	options *Options,
	enabled bool,
	bundles []ToolBundle,
	routeMaxOutputTokens int,
) {
	if !enabled {
		return
	}
	options.ToolRouter = G1IProgressiveToolRouteProtocol{}
	options.ToolBundles = append([]ToolBundle(nil), bundles...)
	options.RouteRenderer = RWKVChatRenderer{}
	options.RouteRetries = 1
	options.RouteMaxOutputTokens = routeMaxOutputTokens
}
