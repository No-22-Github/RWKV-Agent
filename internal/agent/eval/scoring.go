package eval

import (
	"encoding/json"
	"fmt"
	"math"
	"reflect"
	"slices"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
)

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
		if step.ActionType == agent.ActionTypeNoTool {
			return OutcomeSemanticNoCall
		}
	}
	for _, step := range result.Steps {
		if step.ActionType == agent.ActionTypeTool || step.Tool != "" {
			return OutcomeCalledTool
		}
	}
	if result.Route == agent.RouteRespond && len(result.RouteSteps) > 0 {
		return OutcomeExplicitRespond
	}
	for _, step := range result.Steps {
		if step.ActionType == agent.ActionTypeFinal {
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
	if outcome != OutcomeExplicitRespond &&
		outcome != OutcomeDirectFinal &&
		outcome != OutcomeSemanticNoCall {
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
				if step.Stage == agent.StageAnswer && step.ActionType == agent.ActionTypeTool {
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
	accumulateTraceMetrics(&summary, trace)
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

// accumulateTraceMetrics folds the raw trace records (model calls and runner
// events) into the run-level counters.
func accumulateTraceMetrics(summary *Summary, trace []TraceRecord) {
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
