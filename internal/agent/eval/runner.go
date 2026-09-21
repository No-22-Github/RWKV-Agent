package eval

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"slices"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	tools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
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
	if SuiteFor(config.Suite).Primitive {
		if config.PrimitiveProfile == "" {
			config.PrimitiveProfile = PrimitiveProfileUpstream
		}
		if config.PrimitiveProfile != PrimitiveProfileUpstream &&
			config.PrimitiveProfile != PrimitiveProfileGoNative {
			return Report{}, fmt.Errorf("unsupported Primitive tool profile %q", config.PrimitiveProfile)
		}
		// The primitive transcript, terminal tool and step budget are resolved
		// per case by resolveCaseOptions; Run no longer rewrites the shared
		// Runner options, so the manifest and the executed configuration come
		// from the same resolver.
	}
	if config.Suite == SuiteBFCLProduct {
		// Both product-facing transcripts may run this suite: comparing them on
		// the same cases is the point. Benchmark profiles (Primitive, BFCL
		// wrapped) still cannot, because their termination semantics differ.
		_, xmlProfile := config.Runner.Protocol.(agent.G1Protocol)
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
		protocol = agent.G1Protocol{}
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
	if g1Protocol, ok := protocol.(agent.G1Protocol); ok {
		fewShot = g1Protocol.FewShot
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
	// The canonical wire spec is the machine-readable identity of the
	// model-facing configuration. A legacy combination that the spec rejects
	// is recorded rather than dropped, so a silent prefill conflict (for
	// example XML + thinking + router) is visible in run.json.
	wireSpec, wireErr := agent.WireSpecOf(config.Runner)
	wireConflict := ""
	if wireErr != nil {
		wireConflict = wireErr.Error()
	}
	wirePreset, _ := wireSpec.MatchPreset()
	// State identity: the harness never sees the .pth bytes, so a reused
	// rwkv_lightning state is fingerprinted by digesting its ID string.
	stateSHA256 := config.StateSHA256
	if stateSHA256 == "" && config.StateID != "" {
		digest := sha256.Sum256([]byte(config.StateID))
		stateSHA256 = hex.EncodeToString(digest[:])
	}
	// Tool catalog identity: build the registered catalog once (schemas do
	// not depend on fixtures) and pin its schema hash in the manifest.
	toolCatalogHash := ""
	if config.ToolCatalog == WorkToolCatalogName {
		root, err := os.MkdirTemp(config.TempDir, "rwkv-agent-catalog-")
		if err != nil {
			toolCatalogHash = ""
		} else {
			workspace := filepath.Join(root, "workspace")
			toolCatalogHash = ""
			if err := os.MkdirAll(workspace, 0o700); err == nil {
				catalog, catalogErr := buildWorkToolCatalog(workspace, nil, 0, nil)
				if catalogErr == nil {
					toolCatalogHash = workToolCatalogHash(catalog)
				}
			}
			_ = os.RemoveAll(root)
		}
	}
	// Per-case effective configuration: the suite-level fields above cannot
	// describe a per-case terminal tool, step budget or transcript.
	caseWires := make([]CaseWireRecord, 0, len(config.Cases))
	resolved := make([]agent.Options, 0, len(config.Cases))
	for _, testCase := range config.Cases {
		record := CaseWireRecord{ID: testCase.ID}
		options, err := resolveCaseOptions(config, testCase)
		if err != nil {
			record.WireConflict = err.Error()
			caseWires = append(caseWires, record)
			continue
		}
		spec, specErr := agent.WireSpecOf(options)
		record.WireCanonical = spec.Canonical()
		record.WireHash = spec.Hash()
		record.WirePreset, _ = spec.MatchPreset()
		if specErr != nil {
			record.WireConflict = specErr.Error()
		}
		record.TerminalTool = options.TerminalTool
		record.MaxSteps = options.MaxSteps
		record.DecisionMaxOutputTokens = options.DecisionMaxOutputTokens
		caseWires = append(caseWires, record)
		resolved = append(resolved, options)
	}
	// Suite-level summary: preserve the historical aggregate meaning for
	// readers of harness.* while CaseWires stays authoritative. A field that
	// differs across cases falls back to the base value (for a mixed primitive
	// suite, terminal_tool is empty rather than the misleading "submit").
	summaryProtocol, summaryRenderer := protocol.ID(), renderer.ID()
	summaryTerminal := config.Runner.TerminalTool
	summaryEndOnTerminal := config.Runner.EndOnTerminalTool
	summaryMaxSteps := config.Runner.MaxSteps
	summaryDecisionBudget := config.Runner.DecisionMaxOutputTokens
	if len(resolved) > 0 {
		first := resolved[0]
		protocolID, rendererID := "", ""
		sameProtocol := first.Protocol != nil
		sameRenderer := first.Renderer != nil
		if sameProtocol {
			protocolID = first.Protocol.ID()
		}
		if sameRenderer {
			rendererID = first.Renderer.ID()
		}
		terminal := first.TerminalTool
		endOnTerminal := first.EndOnTerminalTool
		decisionBudget := first.DecisionMaxOutputTokens
		sameTerminal, sameEnd, sameDecision := true, true, true
		for _, options := range resolved[1:] {
			sameProtocol = sameProtocol && options.Protocol != nil && options.Protocol.ID() == protocolID
			sameRenderer = sameRenderer && options.Renderer != nil && options.Renderer.ID() == rendererID
			sameTerminal = sameTerminal && options.TerminalTool == terminal
			sameEnd = sameEnd && options.EndOnTerminalTool == endOnTerminal
			sameDecision = sameDecision && options.DecisionMaxOutputTokens == decisionBudget
		}
		if sameProtocol {
			summaryProtocol = protocolID
		}
		if sameRenderer {
			summaryRenderer = rendererID
		}
		if sameTerminal {
			summaryTerminal = terminal
		}
		if sameEnd {
			summaryEndOnTerminal = endOnTerminal
		}
		if sameDecision {
			summaryDecisionBudget = decisionBudget
		}
		for _, options := range resolved {
			if options.MaxSteps > summaryMaxSteps {
				summaryMaxSteps = options.MaxSteps
			}
		}
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
			Protocol:                 summaryProtocol,
			Renderer:                 summaryRenderer,
			RouteRenderer:            routeRenderer.ID(),
			RouteProtocol:            routeProtocol,
			RouteStage:               routeStage,
			ControlPrompt:            string(controlPrompt),
			TaskControl:              config.Runner.TaskControl,
			TerminalTool:             summaryTerminal,
			EndOnTerminalTool:        summaryEndOnTerminal,
			ThinkingMode:             string(thinkingMode),
			RouteThinkingMode:        string(routeThinkingMode),
			Reasoning:                thinkingMode != inference.ThinkingOff,
			FewShot:                  fewShot,
			MaxSteps:                 summaryMaxSteps,
			ProtocolRetries:          config.Runner.ProtocolRetries,
			RouteRetries:             config.Runner.RouteRetries,
			AnswerMaxOutputTokens:    config.Runner.Generation.MaxOutputTokens,
			DecisionMaxOutputTokens:  summaryDecisionBudget,
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
			CompressFetch:            config.Runner.CompressFetch,
			WebFixture:               len(config.WebFixture) > 0,
			SubagentFixture:          len(config.SubagentFixture) > 0,
			TokenCountVocabSHA256:    config.TokenCountVocabSHA256,
			ToolCatalog:              config.ToolCatalog,
			ToolCatalogHash:          toolCatalogHash,
			WireProfile:              config.WireProfile,
			StateID:                  config.StateID,
			StateSHA256:              stateSHA256,
			WireCanonical:            wireSpec.Canonical(),
			WireHash:                 wireSpec.Hash(),
			WirePreset:               wirePreset,
			WireConflict:             wireConflict,
		},
		Sampling: samplingManifest(
			config.Runner.Generation.Sampling,
			config.Model.UnsupportedSampling,
		),
		Environment: EnvironmentMetadata{
			OS:        runtime.GOOS,
			Arch:      runtime.GOARCH,
			GoVersion: runtime.Version(),
		},
		CaseIDs:   caseIDs,
		CaseWires: caseWires,
		Cases:     config.Cases,
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
		Tags:        testCase.Tags,
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
	options, err := resolveCaseOptions(config, testCase)
	if err != nil {
		result.Error = fmt.Sprintf("resolve case options: %v", err)
		return result
	}
	if options.ToolRouter != nil {
		catalog := options.ToolBundles
		if len(catalog) == 0 {
			catalog = agent.DefaultToolBundles()
		}
		options.ToolBundles = agent.EnabledToolBundles(tools, catalog)
	}
	options.TokenCount = config.TokenCount
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
			if errors.Is(runErr, continuation.ErrUpstream) {
				result.Invalid = true
				result.InvalidReason = runErr.Error()
			}
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
	// Case-level end-state expectations (v5) score the final workspace and the
	// whole transcript after the last turn, before the deferred cleanup.
	evaluateCaseExpect(caseContext, workspace, testCase, &result)
	return result
}

// evalSemanticNoTool reports the no_tool switch for either product-facing
// transcript, so an XML A/B cell records the factor it actually varied.
func evalSemanticNoTool(protocol agent.ActionProtocol) bool {
	switch typed := protocol.(type) {
	case agent.G1FunctionProtocol:
		return typed.Product && typed.SemanticNoTool
	case agent.G1Protocol:
		return typed.SemanticNoTool
	default:
		return false
	}
}

func primitiveProtocol(profile string) agent.G1FunctionProtocol {
	return agent.G1FunctionProtocol{
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
	if config.ToolCatalog == WorkToolCatalogName && testCase.primitive == nil {
		// The fixed bank catalog: every case faces the same twelve tools, the
		// same fixed clock, and web tools registered even when the case
		// fixture is empty (empty search results / deterministic not-found).
		// Case-level fixtures win over the suite-level map to keep a bank of
		// web tasks from cross-contaminating through one shared keyword set.
		fixture := testCase.WebFixture
		if len(fixture) == 0 {
			fixture = config.WebFixture
		}
		catalog, err := buildWorkToolCatalog(
			workspace,
			fixture,
			config.FetchBudgetTokens,
			config.TokenCount,
		)
		if err != nil {
			return nil, nil, err
		}
		return catalog, nil, nil
	}
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
	if len(config.SubagentFixture) > 0 {
		// Class-3 e2e: a fixture-backed spawn_agents. Subtasks are matched by
		// keyword so the parent's model-authored task strings resolve to
		// deterministic canned outputs without nested model calls.
		fixture := config.SubagentFixture
		run := func(_ context.Context, task string, _ func(agent.Event)) (tools.AgentTaskResult, error) {
			lowered := normalizeSubtaskText(task)
			for _, entry := range fixture {
				if entry.Match != "" && strings.Contains(lowered, strings.ToLower(entry.Match)) {
					return tools.AgentTaskResult{Output: entry.Output, Sources: entry.Sources, StepCount: 2}, nil
				}
			}
			for _, entry := range fixture {
				if len(entry.MatchAll) == 0 {
					continue
				}
				matched := true
				for _, keyword := range entry.MatchAll {
					if !strings.Contains(lowered, normalizeSubtaskText(keyword)) {
						matched = false
						break
					}
				}
				if matched {
					return tools.AgentTaskResult{Output: entry.Output, Sources: entry.Sources, StepCount: 2}, nil
				}
			}
			fallback := fixture[len(fixture)-1]
			return tools.AgentTaskResult{Output: fallback.Output, Sources: fallback.Sources, StepCount: 2}, nil
		}
		delegation := assistanttools.DelegationTools(assistanttools.DelegationOptions{
			Run:         run,
			MaxParallel: 4,
			Timeout:     time.Minute,
		})
		workspaceTools = append(workspaceTools, delegation...)
	}
	if len(config.WebFixture) > 0 {
		// Web e2e: fixture-backed web_search and web_fetch, matched by keyword
		// or URL substring, so fetch compression (E5) can be exercised in the
		// evaluation runner without network access.
		fixture := webFixtureProviders{entries: config.WebFixture}
		workspaceTools = append(workspaceTools, tools.WebTools(tools.WebOptions{
			Search:            fixture,
			Fetch:             fixture,
			FetchBudgetTokens: config.FetchBudgetTokens,
			TokenCount:        config.TokenCount,
		})...)
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
