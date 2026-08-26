package eval

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"reflect"
	"runtime"
	"slices"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
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

func validateTurn(
	expect Expectation,
	result agent.Result,
	runErr error,
) []string {
	var failures []string
	if runErr != nil {
		failures = append(failures, "runner error: "+runErr.Error())
	}
	outcome := classifyTurnOutcome(result)
	if expect.RequireActiveNoCall && !isActiveNoCall(result, outcome) {
		failures = append(failures, fmt.Sprintf("active no-call required, outcome = %q", outcome))
	}
	if expect.ForbidRouteFallback && routeFailedClosed(result) {
		failures = append(failures, "route fallback is forbidden")
	}
	// Route is only asserted when the route stage ran. Without it the runner
	// carries a hardcoded inspect default, so asserting the route would fail
	// respond-expecting cases on a technicality rather than on behaviour.
	if expect.Route != "" && len(result.RouteSteps) > 0 && result.Route != expect.Route {
		failures = append(
			failures,
			fmt.Sprintf("route = %q, want %q", result.Route, expect.Route),
		)
	}
	actualTools := stepTools(result.Steps)
	if expect.Tools != nil && !slices.Equal(actualTools, expect.Tools) {
		failures = append(
			failures,
			fmt.Sprintf("tools = %v, want %v", actualTools, expect.Tools),
		)
	}
	actualToolSet := makeToolSet(actualTools)
	for _, required := range expect.RequiredTools {
		if !toolRequirementMet(required, actualToolSet) {
			failures = append(
				failures,
				fmt.Sprintf("required tool %q was not called", required),
			)
		}
	}
	for _, forbidden := range expect.ForbiddenTools {
		if _, ok := actualToolSet[forbidden]; ok {
			failures = append(
				failures,
				fmt.Sprintf("forbidden tool %q was called", forbidden),
			)
		}
	}
	toolSteps := stepsWithTools(result.Steps)
	for index, expected := range expect.Calls {
		if index >= len(toolSteps) {
			failures = append(
				failures,
				fmt.Sprintf("missing expected call %d to %s", index+1, expected.Name),
			)
			continue
		}
		step := toolSteps[index]
		if step.Tool != expected.Name {
			failures = append(
				failures,
				fmt.Sprintf("call %d tool = %q, want %q", index+1, step.Tool, expected.Name),
			)
			continue
		}
		if !argumentsContain(step.ToolArguments, expected.Arguments) {
			failures = append(
				failures,
				fmt.Sprintf(
					"call %d arguments = %s, want fields %v",
					index+1,
					step.ToolArguments,
					expected.Arguments,
				),
			)
		}
	}
	requiredMatches := matchRequiredCalls(toolSteps, expect.RequiredCalls)
	for index, expected := range expect.RequiredCalls {
		if !requiredMatches[index] {
			failures = append(
				failures,
				fmt.Sprintf(
					"missing required call to %s with argument fields %v",
					expected.Name,
					expected.Arguments,
				),
			)
		}
	}
	failures = append(failures, answerFailures(expect, modelAnswer(result))...)
	if result.AnswerContractRepaired {
		failures = append(
			failures,
			fmt.Sprintf("answer contract repaired: %v", result.AnswerViolations),
		)
	}
	if result.Plan != nil && expect.Plan != nil {
		failures = append(failures, planFailures(*expect.Plan, *result.Plan)...)
	}
	for _, required := range expect.MustStateUnverified {
		if !strings.Contains(result.Output, required) {
			failures = append(failures, fmt.Sprintf("output does not explicitly state unverified item %q", required))
		}
	}
	return failures
}

func planFailures(expect PlanExpectation, actual agent.PlanTrace) []string {
	var failures []string
	if len(actual.Subtasks) != expect.SubtaskCount {
		failures = append(failures, fmt.Sprintf("plan subtasks = %d, want %d", len(actual.Subtasks), expect.SubtaskCount))
	}
	if !planWavesEqual(expect.Waves, actual) {
		failures = append(failures, fmt.Sprintf("plan waves do not match %v", expect.Waves))
	}
	for _, reference := range expect.References {
		if !planReferenceMatches(reference, actual) {
			failures = append(failures, fmt.Sprintf(
				"plan subtask %d argument %q does not use reference %q",
				reference.Subtask,
				reference.Argument,
				reference.Source,
			))
		}
	}
	return failures
}

func planWavesEqual(expected [][]string, actual agent.PlanTrace) bool {
	if len(expected) != len(actual.Waves) {
		return false
	}
	byID := make(map[int]string, len(actual.Subtasks))
	for _, subtask := range actual.Subtasks {
		byID[subtask.ID] = subtask.Tool
	}
	for index, ids := range actual.Waves {
		tools := make([]string, 0, len(ids))
		for _, id := range ids {
			name, ok := byID[id]
			if !ok {
				return false
			}
			tools = append(tools, name)
		}
		want := append([]string(nil), expected[index]...)
		sort.Strings(tools)
		sort.Strings(want)
		if !slices.Equal(tools, want) {
			return false
		}
	}
	return true
}

func planReferenceMatches(reference Reference, actual agent.PlanTrace) bool {
	for _, subtask := range actual.Subtasks {
		if subtask.ID != reference.Subtask {
			continue
		}
		var arguments map[string]any
		if json.Unmarshal(subtask.Arguments, &arguments) != nil {
			return false
		}
		value, ok := arguments[reference.Argument].(string)
		return ok && value == reference.Source
	}
	return false
}

func answerFailures(expect Expectation, output string) []string {
	var failures []string
	if expect.OutputEquals != nil &&
		strings.TrimSpace(output) != strings.TrimSpace(*expect.OutputEquals) {
		failures = append(
			failures,
			fmt.Sprintf(
				"output = %q, want %q after trimming outer whitespace",
				strings.TrimSpace(output),
				strings.TrimSpace(*expect.OutputEquals),
			),
		)
	}
	for _, required := range expect.OutputContains {
		if !strings.Contains(output, required) {
			failures = append(
				failures,
				fmt.Sprintf("output does not contain %q", required),
			)
		}
	}
	if len(expect.OutputContainsAny) > 0 {
		matched := false
		for _, alternative := range expect.OutputContainsAny {
			if strings.Contains(output, alternative) {
				matched = true
				break
			}
		}
		if !matched {
			failures = append(
				failures,
				fmt.Sprintf("output does not contain any of %q", expect.OutputContainsAny),
			)
		}
	}
	for _, forbidden := range expect.OutputExcludes {
		if strings.Contains(output, forbidden) {
			failures = append(
				failures,
				fmt.Sprintf("output contains forbidden text %q", forbidden),
			)
		}
	}
	if expect.ExpectedNumber != nil {
		actual, err := strconv.ParseFloat(strings.TrimSpace(output), 64)
		if err != nil || math.IsNaN(actual) || math.IsInf(actual, 0) {
			failures = append(
				failures,
				fmt.Sprintf("output %q is not a plain number", strings.TrimSpace(output)),
			)
		} else if math.Abs(actual-*expect.ExpectedNumber) > *expect.Tolerance {
			failures = append(
				failures,
				fmt.Sprintf(
					"numeric output = %g, want %g within %g",
					actual,
					*expect.ExpectedNumber,
					*expect.Tolerance,
				),
			)
		}
	}
	return failures
}

func argumentsContain(raw json.RawMessage, expected map[string]any) bool {
	if len(expected) == 0 {
		return true
	}
	var actual map[string]any
	if json.Unmarshal(raw, &actual) != nil {
		return false
	}
	return valueContains(actual, expected)
}

func valueContains(actual any, expected any) bool {
	switch expectedValue := expected.(type) {
	case map[string]any:
		actualValue, ok := actual.(map[string]any)
		if !ok {
			return false
		}
		for key, item := range expectedValue {
			candidate, exists := actualValue[key]
			if !exists || !valueContains(candidate, item) {
				return false
			}
		}
		return true
	default:
		return reflect.DeepEqual(actual, expected)
	}
}

func stepTools(steps []agent.Step) []string {
	tools := make([]string, 0, len(steps))
	for _, step := range steps {
		if step.Tool != "" {
			tools = append(tools, step.Tool)
		}
	}
	return tools
}

func stepsWithTools(steps []agent.Step) []agent.Step {
	result := make([]agent.Step, 0, len(steps))
	for _, step := range steps {
		if step.Tool != "" {
			result = append(result, step)
		}
	}
	return result
}

// discoveryTools are interchangeable ways to locate a file or value in the
// workspace. A case that mandates one of them is really asserting that the model
// investigated rather than guessed, so any of them satisfies that requirement.
// Forcing a specific one would penalise the cheaper path: search_text can find a
// file and its value in a single call where list_files plus read_file needs two.
var discoveryTools = map[string]struct{}{
	"list_files":  {},
	"search_text": {},
	"read_file":   {},
}

// toolRequirementMet reports whether a required tool was satisfied, treating the
// discovery tools as one equivalence class. Non-discovery tools still require an
// exact match, so calculator, fx_convert and friends stay strictly scored.
func toolRequirementMet(required string, actual map[string]struct{}) bool {
	if _, ok := actual[required]; ok {
		return true
	}
	if _, isDiscovery := discoveryTools[required]; !isDiscovery {
		return false
	}
	for candidate := range actual {
		if _, ok := discoveryTools[candidate]; ok {
			return true
		}
	}
	return false
}

// requiredCallMet reports which actual step satisfies an expected call, or -1.
// An exact tool-name match consumes a step one-to-one. Discovery calls also
// accept any discovery step, and may reuse one that already matched an earlier
// requirement: a single search_text can locate a file and yield its value, doing
// the work a case splits into search-then-read. The returned bool reports whether
// the step should be consumed, so equivalence matches stay reusable.
func requiredCallMet(call ExpectedCall, actual []agent.Step, used []bool) (int, bool) {
	for index, step := range actual {
		if used[index] || step.Tool != call.Name {
			continue
		}
		if argumentsContain(step.ToolArguments, call.Arguments) {
			return index, true
		}
	}
	if _, isDiscovery := discoveryTools[call.Name]; !isDiscovery {
		return -1, false
	}
	for index, step := range actual {
		if _, ok := discoveryTools[step.Tool]; ok {
			return index, false
		}
	}
	return -1, false
}

func makeToolSet(tools []string) map[string]struct{} {
	result := make(map[string]struct{}, len(tools))
	for _, tool := range tools {
		result[tool] = struct{}{}
	}
	return result
}

func matchRequiredCalls(actual []agent.Step, expected []ExpectedCall) []bool {
	matched := make([]bool, len(expected))
	used := make([]bool, len(actual))
	for expectedIndex, call := range expected {
		actualIndex, consume := requiredCallMet(call, actual, used)
		if actualIndex < 0 {
			continue
		}
		if consume {
			used[actualIndex] = true
		}
		matched[expectedIndex] = true
	}
	return matched
}

func hasAnswerExpectation(expect Expectation) bool {
	return expect.OutputEquals != nil ||
		len(expect.OutputContains) > 0 ||
		len(expect.OutputContainsAny) > 0 ||
		len(expect.OutputExcludes) > 0 ||
		expect.ExpectedNumber != nil
}

func modelAnswer(result agent.Result) string {
	if result.OriginalOutput != "" || result.AnswerContractRepaired {
		return result.OriginalOutput
	}
	return result.Output
}

func classifyTurnOutcome(result agent.Result) TurnOutcome {
	if routeFailedClosed(result) {
		return OutcomeRouteFailedClosed
	}
	for _, step := range result.Steps {
		if step.ProtocolError == "" || step.ProtocolFailure == "" {
			continue
		}
		switch step.ProtocolFailure {
		case agent.ProtocolFailureToolEnvelopeMissing:
			return OutcomeToolEnvelopeMissing
		case agent.ProtocolFailureToolJSONDecode:
			return OutcomeToolJSONDecodeFailed
		case agent.ProtocolFailureToolShapeInvalid:
			return OutcomeToolShapeInvalid
		}
	}
	for _, step := range result.Steps {
		if step.ProtocolRepaired {
			return OutcomeProtocolRepaired
		}
	}
	for _, step := range result.Steps {
		if step.ProtocolError != "" || step.ModelError != "" {
			return OutcomeDecisionProtocolError
		}
	}
	for _, step := range result.Steps {
		if step.ActionType == "tool" || step.Tool != "" {
			return OutcomeCalledTool
		}
	}
	if result.Route == agent.RouteRespond && len(result.RouteSteps) > 0 {
		return OutcomeExplicitRespond
	}
	for _, step := range result.Steps {
		if step.ActionType == "final" {
			return OutcomeDirectFinal
		}
	}
	return OutcomeDecisionProtocolError
}

func routeFailedClosed(result agent.Result) bool {
	for _, step := range result.RouteSteps {
		if step.FailedClosed {
			return true
		}
	}
	return false
}

func isActiveNoCall(result agent.Result, outcome TurnOutcome) bool {
	if outcome != OutcomeExplicitRespond && outcome != OutcomeDirectFinal {
		return false
	}
	return len(stepTools(result.Steps)) == 0
}

func summarize(
	runID string,
	cases []Case,
	results []CaseResult,
	trace []TraceRecord,
) Summary {
	summary := Summary{RunID: runID, Cases: results}
	summary.Metrics.Outcomes = make(map[TurnOutcome]int)
	summary.Metrics.ParseFailuresByClass = make(map[agent.ProtocolFailureClass]int)
	byID := make(map[string]Case, len(cases))
	for _, testCase := range cases {
		byID[testCase.ID] = testCase
	}
	for _, caseResult := range results {
		summary.Metrics.TaskSuccess.Total++
		if caseResult.Passed {
			summary.Metrics.TaskSuccess.Correct++
		}
		testCase := byID[caseResult.ID]
		for index, turnResult := range caseResult.Turns {
			if index >= len(testCase.Turns) {
				break
			}
			expect := testCase.Turns[index].Expect
			outcome := turnResult.Outcome
			if outcome == "" {
				outcome = classifyTurnOutcome(turnResult.Result)
			}
			summary.Metrics.Outcomes[outcome]++
			if hasAnswerExpectation(expect) {
				summary.Metrics.AnswerAccuracy.Total++
				answer := modelAnswer(turnResult.Result)
				if len(answerFailures(expect, answer)) == 0 {
					summary.Metrics.AnswerAccuracy.Correct++
				}
				summary.Metrics.AnswerContractRepaired.Total++
				if turnResult.Result.AnswerContractRepaired {
					summary.Metrics.AnswerContractRepaired.Correct++
				}
				for _, required := range expect.MustStateUnverified {
					summary.Metrics.ExplicitAbstention.Total++
					if strings.Contains(answer, required) {
						summary.Metrics.ExplicitAbstention.Correct++
					}
				}
				if expect.Plan != nil && turnResult.Result.Plan != nil {
					summary.Metrics.PlanSubtaskCount.Total++
					if len(turnResult.Result.Plan.Subtasks) == expect.Plan.SubtaskCount {
						summary.Metrics.PlanSubtaskCount.Correct++
					}
					summary.Metrics.PlanWaveOrder.Total++
					if planWavesEqual(expect.Plan.Waves, *turnResult.Result.Plan) {
						summary.Metrics.PlanWaveOrder.Correct++
					}
					for _, reference := range expect.Plan.References {
						summary.Metrics.PlanReferenceUse.Total++
						if planReferenceMatches(reference, *turnResult.Result.Plan) {
							summary.Metrics.PlanReferenceUse.Correct++
						}
					}
				}
				summary.Metrics.PlanRejections += turnResult.Result.PlanRejections
				summary.Metrics.PlanFallbacks += turnResult.Result.PlanFallbacks
			}
			// Only score routing when the route stage actually ran. With the
			// stage disabled every turn carries the hardcoded inspect default,
			// and counting that as a decision would report a free 100%.
			if expect.Route != "" && len(turnResult.Result.RouteSteps) > 0 {
				summary.Metrics.RouteAccuracy.Total++
				if turnResult.Result.Route == expect.Route {
					summary.Metrics.RouteAccuracy.Correct++
				}
			}
			actualTools := stepTools(turnResult.Result.Steps)
			actualToolSet := makeToolSet(actualTools)
			if expect.Tools != nil {
				summary.Metrics.ToolSelection.Total++
				if slices.Equal(actualTools, expect.Tools) {
					summary.Metrics.ToolSelection.Correct++
				}
				if len(expect.Tools) == 0 {
					summary.Metrics.NoCallAccuracy.Total++
					if len(actualTools) == 0 {
						summary.Metrics.NoCallAccuracy.Correct++
					}
					summary.Metrics.ActiveNoCall.Total++
					if isActiveNoCall(turnResult.Result, outcome) {
						summary.Metrics.ActiveNoCall.Correct++
					}
				}
			}
			for _, required := range expect.RequiredTools {
				summary.Metrics.RequiredToolCompletion.Total++
				if caseToolRequirementMet(testCase, required, actualToolSet) {
					summary.Metrics.RequiredToolCompletion.Correct++
				}
			}
			for _, forbidden := range expect.ForbiddenTools {
				summary.Metrics.ForbiddenToolAvoidance.Total++
				if _, ok := actualToolSet[forbidden]; !ok {
					summary.Metrics.ForbiddenToolAvoidance.Correct++
				}
			}
			toolSteps := stepsWithTools(turnResult.Result.Steps)
			for callIndex, expected := range expect.Calls {
				summary.Metrics.ArgumentAccuracy.Total++
				if callIndex < len(toolSteps) &&
					toolSteps[callIndex].Tool == expected.Name &&
					argumentsContain(toolSteps[callIndex].ToolArguments, expected.Arguments) {
					summary.Metrics.ArgumentAccuracy.Correct++
				}
			}
			requiredMatches := matchRequiredCalls(toolSteps, expect.RequiredCalls)
			for _, matched := range requiredMatches {
				summary.Metrics.RequiredCallAccuracy.Total++
				if matched {
					summary.Metrics.RequiredCallAccuracy.Correct++
				}
			}
			for _, step := range turnResult.Result.Steps {
				summary.Metrics.ProtocolValidity.Total++
				if step.ProtocolError == "" {
					summary.Metrics.ProtocolValidity.Correct++
				}
				if step.ActionType != "" || step.StageViolation {
					summary.Metrics.StageContractValidity.Total++
					if !step.StageViolation {
						summary.Metrics.StageContractValidity.Correct++
					}
				}
				if step.Stage == agent.StageAnswer && step.ActionType == "tool" {
					summary.Metrics.AnswerStageToolCalls++
				}
				if step.ProtocolRepaired {
					summary.Metrics.ProtocolRepairs++
				}
				if step.ProtocolFailure != "" {
					summary.Metrics.ParseFailuresByClass[step.ProtocolFailure]++
				}
				if step.Stage == agent.StageDecision {
					summary.Metrics.DecisionProtocolValidity.Total++
					if step.ModelError == "" && step.ProtocolError == "" &&
						!step.ProtocolRepaired && step.ProtocolFailure == "" {
						summary.Metrics.DecisionProtocolValidity.Correct++
					}
				}
				if step.Tool != "" {
					summary.Metrics.ToolCalls++
				}
				if step.ToolExecuted {
					summary.Metrics.ToolExecutions++
				}
				if step.ToolError != "" {
					summary.Metrics.ToolErrors++
				}
				if step.ToolRejected != "" {
					summary.Metrics.RejectedCalls++
				}
				switch step.ToolRejected {
				case "duplicate_tool_call":
					summary.Metrics.DuplicateCalls++
				case "consecutive_tool_failures":
					summary.Metrics.RecoveryBlocks++
				}
			}
			for _, routeStep := range turnResult.Result.RouteSteps {
				summary.Metrics.RouteProtocolValidity.Total++
				if routeStep.ProtocolError == "" && !routeStep.FailedClosed {
					summary.Metrics.RouteProtocolValidity.Correct++
				}
			}
			if turnResult.Result.ForcedAnswerReason != "" {
				summary.Metrics.ForcedAnswers++
			}
			if turnResult.Result.RescueAttempted {
				summary.Metrics.RescueAttempts++
			}
			if turnResult.Result.RescueSubmitted {
				summary.Metrics.RescueSubmits++
			}
		}
	}
	for _, record := range trace {
		if record.ModelCall != nil {
			summary.Metrics.ModelCalls++
			summary.Metrics.PromptTokens += record.ModelCall.Response.Usage.PromptTokens
			summary.Metrics.CompletionTokens +=
				record.ModelCall.Response.Usage.CompletionTokens
		}
		if record.RunnerEvent != nil {
			switch record.RunnerEvent.Kind {
			case agent.EventRetry:
				summary.Metrics.ProtocolRetries++
			case agent.EventRouteDone:
				if record.RunnerEvent.Error != "" {
					summary.Metrics.RouteFallbacks++
				}
			}
		}
	}
	finalizeScore(&summary.Metrics.TaskSuccess)
	finalizeScore(&summary.Metrics.AnswerAccuracy)
	finalizeScore(&summary.Metrics.RouteAccuracy)
	finalizeScore(&summary.Metrics.ProtocolValidity)
	finalizeScore(&summary.Metrics.StageContractValidity)
	finalizeScore(&summary.Metrics.ToolSelection)
	finalizeScore(&summary.Metrics.ArgumentAccuracy)
	finalizeScore(&summary.Metrics.RequiredToolCompletion)
	finalizeScore(&summary.Metrics.ForbiddenToolAvoidance)
	finalizeScore(&summary.Metrics.RequiredCallAccuracy)
	finalizeScore(&summary.Metrics.NoCallAccuracy)
	finalizeScore(&summary.Metrics.ActiveNoCall)
	finalizeScore(&summary.Metrics.RouteProtocolValidity)
	finalizeScore(&summary.Metrics.DecisionProtocolValidity)
	finalizeScore(&summary.Metrics.PlanSubtaskCount)
	finalizeScore(&summary.Metrics.PlanWaveOrder)
	finalizeScore(&summary.Metrics.PlanReferenceUse)
	finalizeScore(&summary.Metrics.ExplicitAbstention)
	finalizeScore(&summary.Metrics.AnswerContractRepaired)
	return summary
}

func caseToolRequirementMet(
	testCase Case,
	required string,
	actual map[string]struct{},
) bool {
	if testCase.primitive != nil {
		_, ok := actual[required]
		return ok
	}
	return toolRequirementMet(required, actual)
}

func finalizeScore(score *Score) {
	if score.Total == 0 {
		return
	}
	score.Rate = float64(score.Correct) / float64(score.Total)
}

type traceRecorder struct {
	mu       sync.Mutex
	now      func() time.Time
	caseID   string
	turn     int
	sequence int
	trace    []TraceRecord
}

func newTraceRecorder(now func() time.Time) *traceRecorder {
	return &traceRecorder{now: now}
}

func (r *traceRecorder) setContext(caseID string, turn int) {
	r.mu.Lock()
	r.caseID = caseID
	r.turn = turn
	r.mu.Unlock()
}

func (r *traceRecorder) append(record TraceRecord) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.sequence++
	record.Sequence = r.sequence
	record.Timestamp = r.now().UTC()
	record.CaseID = r.caseID
	record.Turn = r.turn
	r.trace = append(r.trace, record)
}

func (r *traceRecorder) runnerEvent(event agent.Event) {
	value := &RunnerEventTrace{
		Kind:  event.Kind,
		Step:  event.Step,
		Tool:  event.Tool,
		Route: event.Route,
	}
	if event.Err != nil {
		value.Error = event.Err.Error()
	}
	r.append(TraceRecord{Kind: "runner_event", RunnerEvent: value})
}

func (r *traceRecorder) turnResult(result agent.Result, outcome TurnOutcome, err error) {
	value := &TurnTrace{Result: result, Outcome: outcome}
	if err != nil {
		value.Error = err.Error()
	}
	r.append(TraceRecord{Kind: "turn_result", TurnResult: value})
}

func (r *traceRecorder) modelCall(value ModelCallTrace) {
	r.append(TraceRecord{Kind: "model_call", ModelCall: &value})
}

func (r *traceRecorder) records() []TraceRecord {
	r.mu.Lock()
	defer r.mu.Unlock()
	return append([]TraceRecord(nil), r.trace...)
}

type recordingGenerator struct {
	generator continuation.Generator
	recorder  *traceRecorder
}

func (g *recordingGenerator) Continue(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	started := time.Now()
	result, err := g.generator.Continue(ctx, request, sink)
	value := ModelCallTrace{
		Stage:          requestStage(request),
		Request:        requestSnapshot(request),
		Response:       responseSnapshot(result),
		DurationMillis: time.Since(started).Milliseconds(),
	}
	if err != nil {
		value.Error = err.Error()
	}
	g.recorder.modelCall(value)
	return result, err
}

func (g *recordingGenerator) NativeToolCalling() bool {
	completer, ok := g.generator.(toolchat.Completer)
	return ok && completer.NativeToolCalling()
}

func (g *recordingGenerator) Complete(
	ctx context.Context,
	request toolchat.Request,
	sink continuation.EventSink,
) (toolchat.Result, error) {
	completer, ok := g.generator.(toolchat.Completer)
	if !ok || !completer.NativeToolCalling() {
		return toolchat.Result{}, fmt.Errorf(
			"%w: generator does not support native tool calling",
			continuation.ErrInvalidRequest,
		)
	}
	started := time.Now()
	result, err := completer.Complete(ctx, request, sink)
	value := ModelCallTrace{
		Stage:          toolChatRequestStage(request),
		Request:        toolChatRequestSnapshot(request),
		Response:       toolChatResponseSnapshot(result),
		DurationMillis: time.Since(started).Milliseconds(),
	}
	if err != nil {
		value.Error = err.Error()
	}
	g.recorder.modelCall(value)
	return result, err
}

func toolChatRequestStage(request toolchat.Request) string {
	return requestStage(continuation.Request{Stops: request.Stops})
}

func toolChatRequestSnapshot(request toolchat.Request) RequestSnapshot {
	prompt, err := json.Marshal(struct {
		Messages          []toolchat.Message  `json:"messages"`
		Tools             []toolchat.Tool     `json:"tools,omitempty"`
		ToolChoice        toolchat.ToolChoice `json:"tool_choice,omitempty"`
		AssistantPrefix   string              `json:"assistant_prefix,omitempty"`
		ParallelToolCalls bool                `json:"parallel_tool_calls"`
	}{
		Messages:          request.Messages,
		Tools:             request.Tools,
		ToolChoice:        request.ToolChoice,
		AssistantPrefix:   request.AssistantPrefix,
		ParallelToolCalls: request.ParallelToolCalls,
	})
	if err != nil {
		prompt = []byte(`{"trace_error":"could not encode native Chat Completions request"}`)
	}
	return RequestSnapshot{
		Model:           request.Model,
		Prompt:          string(prompt),
		MaxOutputTokens: request.MaxOutputTokens,
		Stops:           append([]string(nil), request.Stops...),
		Sampling:        samplingSnapshot(request.Sampling),
	}
}

func toolChatResponseSnapshot(result toolchat.Result) ResponseSnapshot {
	text := result.Content
	if len(result.ToolCalls) > 0 {
		encoded, err := json.Marshal(result.ToolCalls)
		if err == nil {
			text = string(encoded)
		}
	}
	return ResponseSnapshot{
		Text:         text,
		FinishReason: result.FinishReason,
		Usage: UsageSnapshot{
			PromptTokens:     result.Usage.PromptTokens,
			CompletionTokens: result.Usage.CompletionTokens,
		},
	}
}

func requestStage(request continuation.Request) string {
	for _, stop := range request.Stops {
		switch stop {
		case "</route>":
			return "route"
		case "</answer>":
			return "answer"
		case "</tool_call>":
			return "decision"
		}
	}
	return "unknown"
}

func samplingSnapshot(sampling continuation.Sampling) SamplingSnapshot {
	return SamplingSnapshot{
		Temperature:      sampling.Temperature,
		TopK:             sampling.TopK,
		TopP:             sampling.TopP,
		PresencePenalty:  sampling.PresencePenalty,
		FrequencyPenalty: sampling.FrequencyPenalty,
		PenaltyDecay:     sampling.PenaltyDecay,
		Seed:             sampling.Seed,
	}
}

func requestSnapshot(request continuation.Request) RequestSnapshot {
	return RequestSnapshot{
		Model:           request.Model,
		Prompt:          request.Prompt,
		MaxOutputTokens: request.MaxOutputTokens,
		Stops:           append([]string(nil), request.Stops...),
		Sampling:        samplingSnapshot(request.Sampling),
	}
}

func responseSnapshot(result continuation.Result) ResponseSnapshot {
	return ResponseSnapshot{
		Text:         result.Text,
		FinishReason: result.FinishReason,
		Usage: UsageSnapshot{
			PromptTokens:     result.Usage.PromptTokens,
			CompletionTokens: result.Usage.CompletionTokens,
		},
	}
}

var _ continuation.Generator = (*recordingGenerator)(nil)
var _ toolchat.Completer = (*recordingGenerator)(nil)
