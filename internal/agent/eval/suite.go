package eval

import (
	"fmt"
	"slices"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// SuiteSpec is the data description of how a built-in suite maps onto harness
// options. It exists so the suite-specific behavior lives in one place instead
// of being re-decided in Run, runCase, and the manifest.
type SuiteSpec struct {
	Name string
	// Primitive selects the fenced benchmark transcript with per-case
	// termination and a case-specific step budget.
	Primitive bool
}

// SuiteFor resolves a suite name. Unknown suites return Primitive=false; case
// validation rejects them earlier.
func SuiteFor(name string) SuiteSpec {
	return SuiteSpec{Name: name, Primitive: IsPrimitiveSuite(name)}
}

// resolveCaseOptions is the single resolver for one case's effective harness
// options: the suite-level base from Config.Runner plus the per-case contract
// (primitive transcript, terminal tool, renderer flags, step budget, scenario
// hook). Run, runCase and runManifest all call it, so the manifest records the
// configuration that actually executes instead of a suite-level approximation.
func resolveCaseOptions(config Config, testCase Case) (agent.Options, error) {
	options := config.Runner
	if !SuiteFor(config.Suite).Primitive {
		return options, nil
	}
	profile := config.PrimitiveProfile
	if profile == "" {
		profile = PrimitiveProfileUpstream
	}
	if profile != PrimitiveProfileUpstream && profile != PrimitiveProfileGoNative {
		return agent.Options{}, fmt.Errorf("unsupported Primitive tool profile %q", profile)
	}
	// The benchmark transcript owns its own fence and submit termination.
	options.Protocol = primitiveProtocol(profile)
	options.TaskControl = ""
	options.TerminalTool = ""
	options.EndOnTerminalTool = false
	options.PostToolHook = nil
	// Primitive Bench allows a full generation for tool calls; write_file and
	// run_lua legitimately carry multi-line source in JSON. The interactive
	// Harness's compact first-decision budget would truncate those calls and
	// score a transport artifact instead of agency.
	options.DecisionMaxOutputTokens = config.Runner.Generation.MaxOutputTokens
	if testCase.Primitive == nil {
		return options, nil
	}
	hasSubmit := slices.Contains(testCase.Primitive.ToolNames, "submit")
	options.Renderer = agent.G1IFunctionRenderer{
		HasSubmit:   hasSubmit,
		HasRunTests: slices.Contains(testCase.Primitive.ToolNames, "run_tests"),
	}
	if hasSubmit {
		options.TerminalTool = "submit"
		options.EndOnTerminalTool = true
	}
	if testCase.Primitive.MaxTurns > 0 {
		options.MaxSteps = testCase.Primitive.MaxTurns
	}
	options.PostToolHook = primitiveScenarioHook(testCase.ID, testCase.primitive)
	return options, nil
}
