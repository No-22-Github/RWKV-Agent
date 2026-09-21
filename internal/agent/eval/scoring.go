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
	"unicode"

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
	// An empty (but present) tools list is the zero-call contract: the task is
	// answerable from the prompt alone, or the honest reply is a refusal. It is
	// scored as call discipline, not as task success, through no_call_accuracy
	// and active_no_call. Folding it into pass/fail conflated two independent
	// questions and answered both with the harsher one: a model that answered
	// "443" correctly after one look at the workspace scored the same as one
	// that answered wrongly, and a model that refused an impossible request
	// after checking whether it was possible scored below one that refused
	// blind. A non-empty list is still an exact-sequence assertion.
	if len(expect.Tools) > 0 && !slices.Equal(actualTools, expect.Tools) {
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
	// Answer-contract repair is wire hygiene, not task success. A reply that
	// opens with "Assistant:" or carries a protocol tag has the harness replace
	// it with a fallback string, and the violation is counted in
	// answer_contract_repaired. Failing the case on top of that scored the
	// wrapper rather than the work: the repaired replies in the 2026-09-21
	// round included a correctly rebuilt report.py and a plain "Assistant:
	// DONE". Content checks already read through the repair via modelAnswer,
	// so a repaired reply whose answer is wrong still fails on its answer.
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
		!answerEquals(output, *expect.OutputEquals) {
		failures = append(
			failures,
			fmt.Sprintf(
				"output = %q, want %q after answer normalization",
				strings.TrimSpace(output),
				strings.TrimSpace(*expect.OutputEquals),
			),
		)
	}
	if len(expect.OutputEqualsAny) > 0 {
		matched := false
		for _, alternative := range expect.OutputEqualsAny {
			if answerEquals(output, alternative) {
				matched = true
				break
			}
		}
		if !matched {
			failures = append(
				failures,
				fmt.Sprintf(
					"output = %q, want one of %q after answer normalization",
					strings.TrimSpace(output),
					expect.OutputEqualsAny,
				),
			)
		}
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
		actual, err := parseNumericOutput(output)
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

// answerTrailingPunctuation is the sentence punctuation a model appends out of
// prose habit. It carries no answer content, so it is stripped before an exact
// comparison: "45 days." and "45 days" are the same answer.
const answerTrailingPunctuation = ".。!！;；,，"

// normalizeAnswer folds the surface variation that a fixed-string answer may
// carry without changing what was answered: outer whitespace, trailing
// sentence punctuation and letter case. Case folding is what lets a model
// answer a yes/no question with "No" — capitalising the first word of a reply
// is orthography, not a different answer. Everything inside the answer (word
// order, spacing between words, every non-final character) still has to match.
func normalizeAnswer(text string) string {
	trimmed := stripEmphasis(strings.TrimSpace(text))
	trimmed = strings.TrimRight(trimmed, answerTrailingPunctuation)
	return strings.ToLower(strings.TrimSpace(stripEmphasis(strings.TrimSpace(trimmed))))
}

// emphasisMarkers are the Markdown wrappers a model reaches for when it thinks
// it is presenting a result rather than writing plain text.
var emphasisMarkers = []string{"**", "__", "*", "_", "`"}

// stripEmphasis removes one matched pair of Markdown emphasis markers around
// the whole answer. "**9**" is the answer 9 typeset, not a different answer.
// Only a matched pair wrapping the entire string is removed, so an answer that
// merely contains an asterisk keeps it.
func stripEmphasis(text string) string {
	for changed := true; changed; {
		changed = false
		for _, marker := range emphasisMarkers {
			if len(text) > 2*len(marker) &&
				strings.HasPrefix(text, marker) &&
				strings.HasSuffix(text, marker) {
				inner := text[len(marker) : len(text)-len(marker)]
				if !strings.Contains(inner, marker) {
					text = strings.TrimSpace(inner)
					changed = true
				}
			}
		}
	}
	return text
}

func answerEquals(output string, expected string) bool {
	normalizedOutput := normalizeAnswer(output)
	normalizedExpected := normalizeAnswer(expected)
	if normalizedOutput == normalizedExpected {
		return true
	}
	// A numeric answer may carry its unit, the same allowance expected_number
	// makes: web-0002 asks for the default of checkpoint_interval_secs and
	// "45 seconds" is the value the question asked for, not a second claim.
	//
	// The allowance is restricted to numeric expectations because a unit only
	// attaches to a number. Extending it to word answers would read "no idea"
	// as the answer "no" — an abstention scored as a verdict.
	if _, err := parseNumericOutput(normalizedExpected); err != nil {
		return false
	}
	head, unit, found := strings.Cut(normalizedOutput, " ")
	return found && head == normalizedExpected && isUnitSuffix(unit)
}

// unitLeadingFunctionWords are words a unit never starts with. They are how a
// sentence continues ("42 the answer is") rather than how a unit reads, and
// rejecting them keeps a clause from passing the shape check below.
var unitLeadingFunctionWords = map[string]struct{}{
	"the": {}, "a": {}, "an": {}, "is": {}, "was": {}, "are": {}, "were": {},
	"of": {}, "in": {}, "for": {}, "and": {}, "or": {}, "but": {}, "that": {},
	"this": {}, "it": {}, "at": {}, "to": {}, "as": {}, "approximately": {},
	"about": {}, "roughly": {},
}

// parseNumericOutput parses the model's numeric answer, accepting the surface
// forms a finance-flavoured answer naturally takes: an optional leading sign,
// then an optional single leading currency symbol ($ € £ ¥), and comma
// thousands separators anywhere in the digits ("$5,548.95", "1,234.50",
// "€9,806.55").
//
// A unit may follow the number, separated by whitespace ("9000 MiB per hour",
// "9806.55 EUR"). Cases routinely ask for the figure in a named unit —
// "express that rate in MiB per hour", "their total value in euros" — and
// repeating that unit in the reply is what the question invites, not a second
// claim to check. The unit is required to be short, free of digits and free of
// sentence punctuation, so it cannot smuggle in a second figure or a sentence:
// "45 seconds (it was 120 before)" is still not a number. The number itself
// must lead, so "approximately 5" and "USD 5" still fail, and the separating
// space is still required, so "5,548.95abc" still fails.
func parseNumericOutput(output string) (float64, error) {
	normalized := stripEmphasis(strings.TrimSpace(output))
	normalized = strings.TrimRight(normalized, answerTrailingPunctuation)
	normalized = stripEmphasis(strings.TrimSpace(normalized))
	// A currency may be written as a leading code rather than a symbol:
	// "EUR 14,746.84" is the same answer as "€14,746.84". This is tried before
	// the trailing-unit rule, since the leading token is not the figure.
	// Only a short, all-letter token qualifies and function words are excluded,
	// so "approximately 5" and "the 5" are still not numbers.
	if head, rest, found := strings.Cut(normalized, " "); found && isLeadingUnit(head) {
		normalized = strings.TrimSpace(rest)
	}
	if head, unit, found := strings.Cut(normalized, " "); found {
		if !isUnitSuffix(unit) {
			return 0, fmt.Errorf("output is not a number followed by a unit")
		}
		normalized = head
	}
	sign := ""
	if strings.HasPrefix(normalized, "+") || strings.HasPrefix(normalized, "-") {
		sign = normalized[:1]
		normalized = normalized[1:]
	}
	for _, symbol := range []string{"$", "€", "£", "¥"} {
		if strings.HasPrefix(normalized, symbol) {
			normalized = strings.TrimPrefix(normalized, symbol)
			break
		}
	}
	normalized = strings.ReplaceAll(normalized, ",", "")
	return strconv.ParseFloat(sign+normalized, 64)
}

// isUnitSuffix reports whether text reads as a unit rather than as prose or a
// second value. A unit is one or two words ("EUR", "GB", "seconds", "US
// dollars"), optionally a rate written as "<unit> per <unit>" ("MiB per
// hour"). Digits are refused so a second figure cannot ride along, and
// punctuation is refused so a clause cannot, which is what keeps
// "45 seconds (it was 120 before)" from parsing as forty-five.
func isUnitSuffix(text string) bool {
	fields := strings.Fields(text)
	switch {
	case len(fields) == 0:
		return false
	case len(fields) == 3 && strings.ToLower(fields[1]) != "per":
		return false
	case len(fields) > 3:
		return false
	}
	if _, isFunctionWord := unitLeadingFunctionWords[strings.ToLower(fields[0])]; isFunctionWord {
		return false
	}
	for _, field := range fields {
		for _, character := range field {
			switch {
			case unicode.IsLetter(character):
			case character == '%' || character == '/' || character == '·':
			default:
				return false
			}
		}
	}
	return true
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

// isAnswerFormatViolation reports whether a failed answer expectation carries
// the right value and fails only on the surrounding text.
//
// The distinction matters because the two are indistinguishable in a bare
// score: web-0002 answering "45 seconds (raised from 120 in the 3.0.0
// release)" and web-0002 answering "120" both read as one lost case, though
// the first resolved the stale-source trap and the second fell for it. It also
// corrects a bias rather than just a tally — a model is most likely to append
// provenance on exactly the supersede and stale-source cases, so the format
// penalty lands hardest on the traps the bank most wants to measure.
//
// The value has to lead the answer. Requiring only that it appear somewhere
// would count "it was 120 before, now 45" as well-formed, and on a case whose
// decoy is itself a number that reading cannot be trusted.
func isAnswerFormatViolation(expect Expectation, output string) bool {
	normalized := normalizeAnswer(output)
	if normalized == "" {
		return false
	}
	// A numeric answer is compared numerically, not textually: the leading
	// figure may be bolded, carry a currency symbol and use thousands
	// separators, and still be the same number. "**$23,609.60**" followed by
	// prose led with the right value.
	if expect.ExpectedNumber != nil && expect.Tolerance != nil {
		for _, candidate := range salientCandidates(output) {
			value, err := parseNumericOutput(candidate)
			if err == nil && math.Abs(value-*expect.ExpectedNumber) <= *expect.Tolerance {
				return true
			}
		}
	}
	var expected []string
	if expect.OutputEquals != nil {
		expected = append(expected, *expect.OutputEquals)
	}
	expected = append(expected, expect.OutputEqualsAny...)
	for _, want := range expected {
		want = normalizeAnswer(want)
		if want == "" || normalized == want {
			continue
		}
		for _, candidate := range salientCandidates(output) {
			if normalizeAnswer(candidate) == want {
				return true
			}
		}
	}
	return false
}

// answerMarkers introduce the value in a reply that explains first. A model
// that reasons in prose and then commits usually labels the commitment.
var answerMarkers = []string{
	"final answer:", "answer:", "答案：", "答案:", "最终答案：", "最终答案:",
}

// salientCandidates returns the positions where a reply's committed value
// plausibly sits: the first line or token, the last line or token, and
// whatever follows an explicit answer marker.
//
// Both ends are needed. Some models lead with the figure and then justify it;
// others reason first and commit at the end ("... = 9000 MiB per hour.\n\n9000",
// "Final answer: 8431"). Scoring only the leading position would file the
// second group under wrong answers, which is exactly backwards for the small
// instruct models this bank is meant to track.
//
// The middle of a reply is deliberately not searched: on a case whose decoy is
// itself a number, "it was 120 before, now 45" must not count on the strength
// of containing the value somewhere.
func salientCandidates(output string) []string {
	trimmed := strings.TrimSpace(output)
	if trimmed == "" {
		return nil
	}
	lines := strings.FieldsFunc(trimmed, func(r rune) bool {
		return r == '\n' || r == '\r'
	})
	candidates := []string{}
	addWithHead := func(line string) {
		line = strings.TrimSpace(line)
		if line == "" {
			return
		}
		candidates = append(candidates, line)
		if head, _, found := strings.Cut(line, " "); found {
			candidates = append(candidates, strings.TrimSpace(head))
		}
		if _, tail, found := strings.Cut(line, " "); found {
			if index := strings.LastIndex(tail, " "); index >= 0 {
				candidates = append(candidates, strings.TrimSpace(tail[index+1:]))
			} else {
				candidates = append(candidates, strings.TrimSpace(tail))
			}
		}
	}
	if len(lines) > 0 {
		addWithHead(lines[0])
		addWithHead(lines[len(lines)-1])
	}
	lowered := strings.ToLower(trimmed)
	for _, marker := range answerMarkers {
		if index := strings.LastIndex(lowered, marker); index >= 0 {
			addWithHead(trimmed[index+len(marker):])
		}
	}
	return candidates
}

func hasAnswerExpectation(expect Expectation) bool {
	return expect.OutputEquals != nil ||
		len(expect.OutputEqualsAny) > 0 ||
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
		if step.Channel == agent.ChannelNative {
			// Native steps do not carry text-wire failure classes.
			continue
		}
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
		if step.Channel != agent.ChannelNative && step.ProtocolRepaired {
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
	summary.Metrics.RepairsByID = make(map[string]int)
	byID := make(map[string]Case, len(cases))
	for _, testCase := range cases {
		byID[testCase.ID] = testCase
	}
	for _, caseResult := range results {
		// An upstream-aborted case never produced an answer, so it is counted
		// as a lost sample rather than scored as a failure. Its turn-level
		// counters below still accumulate: whatever the run did manage to
		// record stays visible, it just does not price a provider break as a
		// model error.
		if caseResult.Invalid {
			summary.Metrics.InvalidCases++
		} else {
			summary.Metrics.TaskSuccess.Total++
			if caseResult.Passed {
				summary.Metrics.TaskSuccess.Correct++
			}
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
				} else if isAnswerFormatViolation(expect, answer) {
					summary.Metrics.AnswerFormatViolations++
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
				if step.Channel != agent.ChannelNative {
					// Text-wire counters: repairs, recovery stages and envelope
					// failure classes only exist where the model itself writes
					// the wire bytes. Native steps are scored by
					// NativeProtocolValidity below.
					if step.ProtocolRepaired {
						summary.Metrics.ProtocolRepairs++
					}
					for _, repair := range step.ProtocolRepairs {
						summary.Metrics.RepairsByID[string(repair)]++
					}
					if step.ProtocolFailure != "" {
						summary.Metrics.ParseFailuresByClass[step.ProtocolFailure]++
					}
				}
				if step.Stage == agent.StageDecision {
					if step.Channel == agent.ChannelNative {
						summary.Metrics.NativeProtocolValidity.Total++
						if step.ModelError == "" && step.ProtocolError == "" {
							summary.Metrics.NativeProtocolValidity.Correct++
						}
					} else {
						summary.Metrics.DecisionProtocolValidity.Total++
						if step.ModelError == "" && step.ProtocolError == "" &&
							!step.ProtocolRepaired && step.ProtocolFailure == "" {
							summary.Metrics.DecisionProtocolValidity.Correct++
						}
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
	finalizeScore(&summary.Metrics.NativeProtocolValidity)
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

// isLeadingUnit reports whether a token in front of a figure is a currency
// code or similar unit rather than the start of a sentence. Currency codes are
// three letters ("EUR", "USD"); four is allowed for the occasional longer unit.
// Function words are excluded so prose cannot qualify.
func isLeadingUnit(token string) bool {
	if len(token) < 2 || len(token) > 4 {
		return false
	}
	for _, character := range token {
		if !unicode.IsLetter(character) {
			return false
		}
	}
	_, isFunctionWord := unitLeadingFunctionWords[strings.ToLower(token)]
	return !isFunctionWord
}
