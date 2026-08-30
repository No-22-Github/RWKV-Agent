package eval

import (
	"context"
	"fmt"
	"runtime"
	"slices"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/inference"
)

const defaultCaseTimeout = 2 * time.Minute

func Run(ctx context.Context, config Config) (Report, error) {
	if err := ValidateCases(config.Cases); err != nil {
		return Report{}, err
	}
	if config.GeneratorFactory == nil {
		return Report{}, fmt.Errorf("eval generator factory is required")
	}
	if config.CaseTimeout <= 0 {
		config.CaseTimeout = defaultCaseTimeout
	}
	if config.CaseParallelism <= 0 {
		config.CaseParallelism = 1
	}
	if config.CaseParallelism > len(config.Cases) {
		config.CaseParallelism = len(config.Cases)
	}
	if IsPrimitiveSuite(config.Suite) {
		if config.PrimitiveProfile == "" {
			config.PrimitiveProfile = PrimitiveProfileUpstream
		}
		if config.PrimitiveProfile != PrimitiveProfileUpstream &&
			config.PrimitiveProfile != PrimitiveProfileGoNative {
			return Report{}, fmt.Errorf("unsupported Primitive tool profile %q", config.PrimitiveProfile)
		}
		config.Runner.Protocol = primitiveProtocol(config.PrimitiveProfile)
		config.Runner.Renderer = agent.G1IFunctionRenderer{HasSubmit: true}
		config.Runner.TaskControl = ""
		config.Runner.TerminalTool = "submit"
		config.Runner.EndOnTerminalTool = true
		// Primitive Bench allows a full 1024-token generation for tool calls;
		// write_file and run_lua legitimately carry multi-line source in JSON.
		// The interactive Harness's compact 96-token first-decision budget would
		// truncate those calls and score a transport artifact instead of agency.
		config.Runner.DecisionMaxOutputTokens = config.Runner.Generation.MaxOutputTokens
		// Primitive Bench defines a case-specific max_turns budget. Preserve the
		// largest effective budget in the harness manifest; runCase applies each
		// case's exact value instead of the generic CLI fallback.
		for _, testCase := range config.Cases {
			if testCase.Primitive != nil && testCase.Primitive.MaxTurns > config.Runner.MaxSteps {
				config.Runner.MaxSteps = testCase.Primitive.MaxTurns
			}
		}
	}
	if config.Suite == SuiteBFCLProduct {
		// Both product-facing transcripts may run this suite: comparing them on
		// the same cases is the point. Benchmark profiles (Primitive, BFCL
		// wrapped) still cannot, because their termination semantics differ.
		_, xmlProfile := config.Runner.Protocol.(agent.G1IProtocol)
		if !agent.OptionsProductProfile(config.Runner).Complete() && !xmlProfile {
			return Report{}, fmt.Errorf(
				"bfcl-product requires a product-facing Harness profile (markdown or xml)",
			)
		}
	}
	now := config.Now
	if now == nil {
		now = time.Now
	}
	started := now().UTC()
	runID := started.Format("20060102T150405.000000000Z")
	report := Report{
		Manifest: runManifest(config, runID, started),
	}
	report.Summary.RunID = runID

	type caseRun struct {
		result CaseResult
		trace  []TraceRecord
	}
	runs := make([]caseRun, len(config.Cases))
	jobs := make(chan int, len(config.Cases))
	for index := range config.Cases {
		jobs <- index
	}
	close(jobs)
	var workers sync.WaitGroup
	workers.Add(config.CaseParallelism)
	for range config.CaseParallelism {
		go func() {
			defer workers.Done()
			for index := range jobs {
				if ctx.Err() != nil {
					return
				}
				recorder := newTraceRecorder(now)
				runs[index] = caseRun{
					result: runCase(ctx, config, config.Cases[index], recorder),
					trace:  recorder.records(),
				}
			}
		}()
	}
	workers.Wait()
	for index, run := range runs {
		if run.result.ID == "" {
			run.result = CaseResult{
				ID:          config.Cases[index].ID,
				Description: config.Cases[index].Description,
				Category:    config.Cases[index].Category,
				Error:       context.Cause(ctx).Error(),
			}
		}
		report.Summary.Cases = append(report.Summary.Cases, run.result)
		for _, record := range run.trace {
			record.Sequence = len(report.Trace) + 1
			report.Trace = append(report.Trace, record)
		}
	}
	report.Manifest.CompletedAt = now().UTC()
	report.Summary = summarize(runID, config.Cases, report.Summary.Cases, report.Trace)
	report.Summary.Metrics.WallTimeMillis =
		report.Manifest.CompletedAt.Sub(report.Manifest.StartedAt).Milliseconds()
	return report, ctx.Err()
}

func runManifest(config Config, runID string, started time.Time) RunManifest {
	protocol := config.Runner.Protocol
	if protocol == nil {
		protocol = agent.G1IProtocol{}
	}
	renderer := config.Runner.Renderer
	if renderer == nil {
		renderer = agent.RWKVChatRenderer{}
	}
	routeRenderer := config.Runner.RouteRenderer
	if routeRenderer == nil {
		routeRenderer = agent.RWKVChatRenderer{}
	}
	controlPrompt := config.Runner.ControlPrompt
	if controlPrompt == "" {
		controlPrompt = agent.ControlPromptSystem
	}
	thinkingMode := evalRendererThinkingMode(renderer)
	routeThinkingMode := evalRendererThinkingMode(routeRenderer)
	productProfile := agent.ProductProfileOf(protocol, renderer)
	fewShot := false
	if g1iProtocol, ok := protocol.(agent.G1IProtocol); ok {
		fewShot = g1iProtocol.FewShot
	}
	// The route stage is optional: larger models route correctly inside the
	// decision stage, so it can be skipped to save a call per turn. Record which
	// mode ran, because with no router every turn defaults to the inspect route
	// and route_accuracy would otherwise credit that default as a decision.
	routeProtocol := ""
	switch {
	case config.Runner.Router != nil:
		routeProtocol = config.Runner.Router.ID()
	case config.Runner.ToolRouter != nil:
		routeProtocol = config.Runner.ToolRouter.ID()
	}
	routeStage := config.Runner.Router != nil || config.Runner.ToolRouter != nil
	caseIDs := make([]string, len(config.Cases))
	for index, testCase := range config.Cases {
		caseIDs[index] = testCase.ID
	}
	return RunManifest{
		SchemaVersion: RunSchemaVersion,
		RunID:         runID,
		Suite:         config.Suite,
		StartedAt:     started,
		Model:         config.Model,
		Harness: HarnessMetadata{
			Version:                  HarnessVersion,
			ScorerVersion:            ScorerVersion,
			OutcomeTaxonomyVersion:   OutcomeTaxonomyVersion,
			Protocol:                 protocol.ID(),
			Renderer:                 renderer.ID(),
			RouteRenderer:            routeRenderer.ID(),
			RouteProtocol:            routeProtocol,
			RouteStage:               routeStage,
			ControlPrompt:            string(controlPrompt),
			TaskControl:              config.Runner.TaskControl,
			TerminalTool:             config.Runner.TerminalTool,
			EndOnTerminalTool:        config.Runner.EndOnTerminalTool,
			ThinkingMode:             string(thinkingMode),
			RouteThinkingMode:        string(routeThinkingMode),
			Reasoning:                thinkingMode != inference.ThinkingOff,
			FewShot:                  fewShot,
			MaxSteps:                 config.Runner.MaxSteps,
			ProtocolRetries:          config.Runner.ProtocolRetries,
			RouteRetries:             config.Runner.RouteRetries,
			AnswerMaxOutputTokens:    config.Runner.Generation.MaxOutputTokens,
			DecisionMaxOutputTokens:  config.Runner.DecisionMaxOutputTokens,
			RouteMaxOutputTokens:     config.Runner.RouteMaxOutputTokens,
			TracePromptBytes:         config.Runner.TracePromptBytes,
			CaseParallelism:          config.CaseParallelism,
			ToolProfile:              config.PrimitiveProfile,
			DuplicateReplayLimit:     config.Runner.DuplicateReplayLimit,
			DuplicateRescueThreshold: config.Runner.DuplicateRescueThreshold,
			SameToolRescueLimit:      config.Runner.SameToolRescueLimit,
			SemanticNoTool:           evalSemanticNoTool(protocol),
			DecisionFakeThink:        productProfile.DecisionFakeThink,
			DeepToolAnchor:           productProfile.DeepToolAnchor,
			ScenarioHooks:            primitiveScenarioHookDescriptions(config.Cases),
		},
		Sampling: samplingSnapshot(config.Runner.Generation.Sampling),
		Environment: EnvironmentMetadata{
			OS:        runtime.GOOS,
			Arch:      runtime.GOARCH,
			GoVersion: runtime.Version(),
		},
		CaseIDs: caseIDs,
		Cases:   config.Cases,
	}
}

func evalRendererThinkingMode(renderer agent.PromptRenderer) inference.ThinkingMode {
	switch renderer := renderer.(type) {
	case agent.RWKVChatRenderer:
		if renderer.ThinkingMode != "" {
			return renderer.ThinkingMode
		}
		if renderer.Reasoning {
			return inference.ThinkingFast
		}
	case *agent.RWKVChatRenderer:
		if renderer.ThinkingMode != "" {
			return renderer.ThinkingMode
		}
		if renderer.Reasoning {
			return inference.ThinkingFast
		}
	}
	return inference.ThinkingOff
}

func runCase(
	parent context.Context,
	config Config,
	testCase Case,
	recorder *traceRecorder,
) (result CaseResult) {
	result = CaseResult{
		ID:          testCase.ID,
		Description: testCase.Description,
		Category:    testCase.Category,
		Turns:       make([]TurnResult, 0, len(testCase.Turns)),
	}
	workspace, cleanup, err := createWorkspace(config.TempDir, testCase)
	if err != nil {
		result.Error = fmt.Sprintf("create workspace: %v", err)
		return result
	}
	defer cleanup()
	tools, primitiveRun, err := evalTools(config, workspace, testCase)
	if err != nil {
		result.Error = fmt.Sprintf("create tools: %v", err)
		return result
	}
	caseContext, cancel := context.WithTimeout(parent, config.CaseTimeout)
	defer cancel()
	generator, closer, err := config.GeneratorFactory(caseContext)
	if err != nil {
		result.Error = fmt.Sprintf("create generator: %v", err)
		return result
	}
	if closer != nil {
		defer func() {
			if closeErr := closer.Close(); closeErr != nil && result.Error == "" {
				result.Error = fmt.Sprintf("close generator: %v", closeErr)
				result.Passed = false
			}
		}()
	}
	recording := &recordingGenerator{generator: generator, recorder: recorder}
	options := config.Runner
	if options.ToolRouter != nil {
		catalog := options.ToolBundles
		if len(catalog) == 0 {
			catalog = agent.DefaultToolBundles()
		}
		options.ToolBundles = agent.EnabledToolBundles(tools, catalog)
	}
	if testCase.Primitive != nil && testCase.Primitive.MaxTurns > 0 {
		options.MaxSteps = testCase.Primitive.MaxTurns
		hasSubmit := slices.Contains(testCase.Primitive.ToolNames, "submit")
		options.Protocol = primitiveProtocol(config.PrimitiveProfile)
		options.Renderer = agent.G1IFunctionRenderer{
			HasSubmit:   hasSubmit,
			HasRunTests: slices.Contains(testCase.Primitive.ToolNames, "run_tests"),
		}
		options.TerminalTool = ""
		options.EndOnTerminalTool = false
		if hasSubmit {
			options.TerminalTool = "submit"
			options.EndOnTerminalTool = true
		}
		options.PostToolHook = primitiveScenarioHook(testCase.ID, testCase.primitive)
	}
	runner, err := agent.NewRunner(recording, tools, options)
	if err != nil {
		result.Error = fmt.Sprintf("create runner: %v", err)
		return result
	}

	result.Passed = true
	for index, turn := range testCase.Turns {
		turnNumber := index + 1
		recorder.setContext(testCase.ID, turnNumber)
		runResult, runErr := runner.RunWithObserver(
			caseContext,
			turn.Prompt,
			func(event agent.Event) {
				recorder.runnerEvent(event)
			},
		)
		turnResult := TurnResult{
			Number:  turnNumber,
			Prompt:  turn.Prompt,
			Result:  runResult,
			Outcome: classifyTurnOutcome(runResult),
		}
		if runErr != nil {
			turnResult.RunnerError = runErr.Error()
		}
		turnResult.Failures = validateTurn(turn.Expect, runResult, runErr)
		turnResult.Failures = append(
			turnResult.Failures,
			primitiveFailures(testCase.primitive, primitiveRun, runResult)...,
		)
		turnResult.Passed = len(turnResult.Failures) == 0
		result.Turns = append(result.Turns, turnResult)
		recorder.turnResult(runResult, turnResult.Outcome, runErr)
		if !turnResult.Passed {
			result.Passed = false
		}
		if runErr != nil {
			break
		}
	}
	if len(result.Turns) != len(testCase.Turns) {
		result.Passed = false
	}
	return result
}

// evalSemanticNoTool reports the no_tool switch for either product-facing
// transcript, so an XML A/B cell records the factor it actually varied.
func evalSemanticNoTool(protocol agent.ActionProtocol) bool {
	switch typed := protocol.(type) {
	case agent.G1IFunctionProtocol:
		return typed.Product && typed.SemanticNoTool
	case agent.G1IProtocol:
		return typed.SemanticNoTool
	default:
		return false
	}
}

func primitiveProtocol(profile string) agent.G1IFunctionProtocol {
	return agent.G1IFunctionProtocol{
		AllowRepeatedCalls: profile == PrimitiveProfileUpstream,
	}
}

type fixedAssistantClock struct{ value time.Time }

func (c fixedAssistantClock) Now() time.Time { return c.value }

func evalTools(
	config Config,
	workspace string,
	testCase Case,
) ([]agent.Tool, *primitiveExecution, error) {
	if testCase.primitive != nil {
		execution := newPrimitiveExecution(workspace, testCase.primitive)
		execution.goNative = config.PrimitiveProfile == PrimitiveProfileGoNative
		tools, err := execution.tools()
		if err != nil {
			return nil, nil, err
		}
		if config.PrimitiveProfile == PrimitiveProfileGoNative &&
			slices.Contains(testCase.primitive.toolNames, "run_lua") {
			tools = slices.DeleteFunc(tools, func(tool agent.Tool) bool {
				return tool.Spec().Name == "run_lua"
			})
			core, coreErr := assistanttools.CoreTools(assistanttools.Options{Workspace: workspace})
			if coreErr != nil {
				return nil, nil, coreErr
			}
			tools = append(tools, core...)
		}
		return tools, execution, err
	}
	workspaceTools, err := agent.WorkspaceTools(workspace)
	if err != nil {
		return nil, nil, err
	}
	if config.FileToolForm != "" {
		// E6 A/B: the file-editing toolset rides on non-primitive suites so
		// custom case files can exercise both forms with identical tasks.
		editTools, editErr := assistanttools.FileEditTools(workspace, assistanttools.FileEditForm(config.FileToolForm))
		if editErr != nil {
			return nil, nil, editErr
		}
		workspaceTools = append(workspaceTools, editTools...)
	}
	clock := fixedAssistantClock{value: time.Date(
		2026,
		time.August,
		4,
		10,
		0,
		0,
		0,
		time.FixedZone("Asia/Shanghai", 8*60*60),
	)}
	switch config.Suite {
	case SuiteBoundary:
		compute, err := assistanttools.ComputeTools(assistanttools.Options{
			Clock:     clock,
			Workspace: workspace,
		})
		if err != nil {
			return nil, nil, err
		}
		return append(workspaceTools, compute...), nil, nil
	case SuiteAssistant:
		provider, err := assistanttools.DefaultMockProvider()
		if err != nil {
			return nil, nil, err
		}
		for _, name := range testCase.ProviderUnavailable {
			provider.Unavailable[name] = true
		}
		assistant, err := assistanttools.AssistantTools(assistanttools.Options{
			Provider:  provider,
			Clock:     clock,
			Workspace: workspace,
		})
		if err != nil {
			return nil, nil, err
		}
		return append(workspaceTools, assistant...), nil, nil
	default:
		return workspaceTools, nil, nil
	}
}
