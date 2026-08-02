package eval

import (
	"context"
	"encoding/json"
	"fmt"
	"math"
	"reflect"
	"runtime"
	"slices"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

const defaultCaseTimeout = 2 * time.Minute

func Run(ctx context.Context, config Config) (Report, error) {
	if err := ValidateCases(config.Cases); err != nil {
		return Report{}, err
	}
	if config.GeneratorFactory == nil {
		return Report{}, fmt.Errorf("eval generator factory is required")
	}
	if config.Runner.Router == nil {
		return Report{}, fmt.Errorf("eval runner requires a route protocol")
	}
	if config.CaseTimeout <= 0 {
		config.CaseTimeout = defaultCaseTimeout
	}
	now := config.Now
	if now == nil {
		now = time.Now
	}
	started := now().UTC()
	runID := started.Format("20060102T150405.000000000Z")
	recorder := newTraceRecorder(now)
	report := Report{
		Manifest: runManifest(config, runID, started),
	}
	report.Summary.RunID = runID

	for _, testCase := range config.Cases {
		if err := ctx.Err(); err != nil {
			report.Manifest.CompletedAt = now().UTC()
			report.Trace = recorder.records()
			report.Summary = summarize(runID, config.Cases, report.Summary.Cases, report.Trace)
			report.Summary.Metrics.WallTimeMillis =
				report.Manifest.CompletedAt.Sub(report.Manifest.StartedAt).Milliseconds()
			return report, err
		}
		result := runCase(ctx, config, testCase, recorder)
		report.Summary.Cases = append(report.Summary.Cases, result)
	}
	report.Manifest.CompletedAt = now().UTC()
	report.Trace = recorder.records()
	report.Summary = summarize(runID, config.Cases, report.Summary.Cases, report.Trace)
	report.Summary.Metrics.WallTimeMillis =
		report.Manifest.CompletedAt.Sub(report.Manifest.StartedAt).Milliseconds()
	return report, nil
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
	reasoning := false
	if rwkvRenderer, ok := renderer.(agent.RWKVChatRenderer); ok {
		reasoning = rwkvRenderer.Reasoning
	}
	fewShot := false
	if g1iProtocol, ok := protocol.(agent.G1IProtocol); ok {
		fewShot = g1iProtocol.FewShot
	}
	caseIDs := make([]string, len(config.Cases))
	for index, testCase := range config.Cases {
		caseIDs[index] = testCase.ID
	}
	return RunManifest{
		SchemaVersion: SchemaVersion,
		RunID:         runID,
		Suite:         config.Suite,
		StartedAt:     started,
		Model:         config.Model,
		Harness: HarnessMetadata{
			Version:                 HarnessVersion,
			Protocol:                protocol.ID(),
			Renderer:                renderer.ID(),
			RouteRenderer:           routeRenderer.ID(),
			RouteProtocol:           config.Runner.Router.ID(),
			ControlPrompt:           string(controlPrompt),
			Reasoning:               reasoning,
			FewShot:                 fewShot,
			MaxSteps:                config.Runner.MaxSteps,
			ProtocolRetries:         config.Runner.ProtocolRetries,
			RouteRetries:            config.Runner.RouteRetries,
			AnswerMaxOutputTokens:   config.Runner.Generation.MaxOutputTokens,
			DecisionMaxOutputTokens: config.Runner.DecisionMaxOutputTokens,
			RouteMaxOutputTokens:    config.Runner.RouteMaxOutputTokens,
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
	tools, err := agent.WorkspaceTools(workspace)
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
			Number: turnNumber,
			Prompt: turn.Prompt,
			Result: runResult,
		}
		if runErr != nil {
			turnResult.RunnerError = runErr.Error()
		}
		turnResult.Failures = validateTurn(turn.Expect, runResult, runErr)
		turnResult.Passed = len(turnResult.Failures) == 0
		result.Turns = append(result.Turns, turnResult)
		recorder.turnResult(runResult, runErr)
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

func validateTurn(
	expect Expectation,
	result agent.Result,
	runErr error,
) []string {
	var failures []string
	if runErr != nil {
		failures = append(failures, "runner error: "+runErr.Error())
	}
	if expect.Route != "" && result.Route != expect.Route {
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
		if _, ok := actualToolSet[required]; !ok {
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
	failures = append(failures, answerFailures(expect, result.Output)...)
	return failures
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
		for actualIndex, step := range actual {
			if used[actualIndex] ||
				step.Tool != call.Name ||
				!argumentsContain(step.ToolArguments, call.Arguments) {
				continue
			}
			used[actualIndex] = true
			matched[expectedIndex] = true
			break
		}
	}
	return matched
}

func hasAnswerExpectation(expect Expectation) bool {
	return expect.OutputEquals != nil ||
		len(expect.OutputContains) > 0 ||
		len(expect.OutputExcludes) > 0 ||
		expect.ExpectedNumber != nil
}

func summarize(
	runID string,
	cases []Case,
	results []CaseResult,
	trace []TraceRecord,
) Summary {
	summary := Summary{RunID: runID, Cases: results}
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
			if hasAnswerExpectation(expect) {
				summary.Metrics.AnswerAccuracy.Total++
				if len(answerFailures(expect, turnResult.Result.Output)) == 0 {
					summary.Metrics.AnswerAccuracy.Correct++
				}
			}
			if expect.Route != "" {
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
				}
			}
			for _, required := range expect.RequiredTools {
				summary.Metrics.RequiredToolCompletion.Total++
				if _, ok := actualToolSet[required]; ok {
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
			if turnResult.Result.ForcedAnswerReason != "" {
				summary.Metrics.ForcedAnswers++
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
	finalizeScore(&summary.Metrics.ToolSelection)
	finalizeScore(&summary.Metrics.ArgumentAccuracy)
	finalizeScore(&summary.Metrics.RequiredToolCompletion)
	finalizeScore(&summary.Metrics.ForbiddenToolAvoidance)
	finalizeScore(&summary.Metrics.RequiredCallAccuracy)
	finalizeScore(&summary.Metrics.NoCallAccuracy)
	return summary
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

func (r *traceRecorder) turnResult(result agent.Result, err error) {
	value := &TurnTrace{Result: result}
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
