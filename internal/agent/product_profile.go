package agent

import (
	"encoding/json"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

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
	TaskControl              string
	PostToolHook             func(string, json.RawMessage, any, error) string
	Observe                  func(Event)
}

// ProductHarnessOptions is the single constructor for the product Markdown
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
		},
		Renderer: G1IFunctionRenderer{
			Product:           true,
			DecisionFakeThink: config.DecisionFakeThink,
		},
		Generation:       config.Generation,
		Observe:          config.Observe,
		TracePromptBytes: config.TracePromptBytes,
	}
	if config.ProgressiveTools {
		options.ToolRouter = G1IProgressiveToolRouteProtocol{}
		options.ToolBundles = append([]ToolBundle(nil), config.ToolBundles...)
		options.RouteRenderer = RWKVChatRenderer{}
		options.RouteRetries = 1
		options.RouteMaxOutputTokens = config.RouteMaxOutputTokens
	}
	return options
}
