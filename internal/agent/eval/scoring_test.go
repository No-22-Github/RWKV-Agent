package eval

import (
	"math"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// TestParseNumericOutputNormalization locks the accepted surface forms of a
// numeric answer: sign, one leading currency symbol, comma separators.
func TestParseNumericOutputNormalization(t *testing.T) {
	t.Parallel()
	valid := map[string]float64{
		"290.00":        290,
		"$5,548.95":     5548.95,
		"$17,090.00":    17090,
		"€9,806.55":     9806.55,
		"£1,000":        1000,
		"¥1200":         1200,
		"1,234.50":      1234.5,
		"-$42.5":        -42.5,
		"+1,234":        1234,
		"  $5,548.95  ": 5548.95,
		"1,234,567.89":  1234567.89,
		"0":             0,
		"-1,234.50":     -1234.5,
	}
	for input, want := range valid {
		got, err := parseNumericOutput(input)
		if err != nil {
			t.Fatalf("parseNumericOutput(%q) err = %v, want %g", input, err, want)
		}
		if math.Abs(got-want) > 1e-9 {
			t.Fatalf("parseNumericOutput(%q) = %g, want %g", input, got, want)
		}
	}
	invalid := []string{
		"approximately 5",
		"5,548.95abc",
		"$$5",
		"€",
		"",
		"abc",
		"5 548.95",
	}
	for _, input := range invalid {
		if got, err := parseNumericOutput(input); err == nil {
			t.Fatalf("parseNumericOutput(%q) = %g, want an error", input, got)
		}
	}
}

// TestExpectedNumberAcceptsCurrencyFormattedAnswers covers the bank false
// negatives: tab-0001 "$5,548.95", tab-0002 "$17,090.00", hyb-0002 "€9,806.55".
func TestExpectedNumberAcceptsCurrencyFormattedAnswers(t *testing.T) {
	t.Parallel()
	expected := 5548.95
	tolerance := 0.01
	expect := Expectation{ExpectedNumber: &expected, Tolerance: &tolerance}
	if failures := answerFailures(expect, "$5,548.95"); len(failures) != 0 {
		t.Fatalf("currency failures = %v", failures)
	}
	if failures := answerFailures(expect, "approximately $5,548.95"); len(failures) != 1 ||
		!strings.Contains(failures[0], "not a plain number") {
		t.Fatalf("prose failures = %v", failures)
	}
}

// TestOutputEqualsAnyMatchesTrimmedAlternatives locks the exact-match
// semantics of output_equals_any: outer whitespace is trimmed, then the
// output must equal one of the entries byte for byte.
func TestOutputEqualsAnyMatchesTrimmedAlternatives(t *testing.T) {
	t.Parallel()
	expect := Expectation{OutputEqualsAny: []string{"yes", "no"}}
	if failures := answerFailures(expect, " yes \n"); len(failures) != 0 {
		t.Fatalf("trimmed match failures = %v", failures)
	}
	if failures := answerFailures(expect, "no"); len(failures) != 0 {
		t.Fatalf("second alternative failures = %v", failures)
	}
	failures := answerFailures(expect, "yes it is")
	if len(failures) != 1 || !strings.Contains(failures[0], "want one of") {
		t.Fatalf("non-match failures = %v", failures)
	}
	if !hasAnswerExpectation(Expectation{OutputEqualsAny: []string{"yes"}}) {
		t.Fatal("output_equals_any alone must count as an answer expectation")
	}
}

// TestSummarizeScopesTextWireCountersByChannel locks the channel split: a
// text step feeds the text-wire counters and decision_protocol_validity,
// while a native step only feeds native_protocol_validity, even when its
// fields still carry (legacy or synthetic) repair markers.
func TestSummarizeScopesTextWireCountersByChannel(t *testing.T) {
	t.Parallel()
	testCase := Case{ID: "channels", Turns: []Turn{{Prompt: "ping"}}}
	result := agent.Result{
		Route: agent.RouteInspect,
		Steps: []agent.Step{
			{
				Stage:            agent.StageDecision,
				Channel:          agent.ChannelText,
				ActionType:       agent.ActionTypeTool,
				Tool:             "read_file",
				ProtocolRepaired: true,
				ProtocolFailure:  agent.ProtocolFailureToolEnvelopeMissing,
			},
			{
				Stage:      agent.StageDecision,
				Channel:    agent.ChannelNative,
				ActionType: agent.ActionTypeFinal,
			},
		},
	}
	summary := summarize("run", []Case{testCase}, []CaseResult{{
		ID:     "channels",
		Passed: true,
		Turns:  []TurnResult{{Result: result, Passed: true}},
	}}, nil)
	metrics := summary.Metrics
	assertScore(t, "decision protocol validity", metrics.DecisionProtocolValidity, 0, 1)
	assertScore(t, "native protocol validity", metrics.NativeProtocolValidity, 1, 1)
	if metrics.ProtocolRepairs != 1 ||
		metrics.ParseFailuresByClass[agent.ProtocolFailureToolEnvelopeMissing] != 1 {
		t.Fatalf("text-wire counters = %+v", metrics)
	}

	// The same markers on a native step must not move any text-wire counter.
	result.Steps[0].Channel = agent.ChannelNative
	result.Steps[1].Channel = agent.ChannelNative
	summary = summarize("run", []Case{testCase}, []CaseResult{{
		ID:     "channels",
		Passed: true,
		Turns:  []TurnResult{{Result: result, Passed: true}},
	}}, nil)
	metrics = summary.Metrics
	assertScore(t, "decision protocol validity", metrics.DecisionProtocolValidity, 0, 0)
	assertScore(t, "native protocol validity", metrics.NativeProtocolValidity, 2, 2)
	if metrics.ProtocolRepairs != 0 || len(metrics.ParseFailuresByClass) != 0 {
		t.Fatalf("native steps leaked into text-wire counters = %+v", metrics)
	}
}

// TestNativeOutcomeClassificationSkipsTextWireOutcomes verifies that native
// steps cannot produce the text-wire outcomes, even with genuine failures.
func TestNativeOutcomeClassificationSkipsTextWireOutcomes(t *testing.T) {
	t.Parallel()
	repaired := agent.Result{Steps: []agent.Step{{
		Stage:            agent.StageDecision,
		Channel:          agent.ChannelNative,
		ActionType:       agent.ActionTypeTool,
		Tool:             "read_file",
		ProtocolRepaired: true,
	}}}
	if outcome := classifyTurnOutcome(repaired); outcome == OutcomeProtocolRepaired {
		t.Fatalf("native repaired outcome = %q", outcome)
	}
	genuineFailure := agent.Result{Steps: []agent.Step{{
		Stage:           agent.StageDecision,
		Channel:         agent.ChannelNative,
		ProtocolError:   "decode failed",
		ProtocolFailure: agent.ProtocolFailureToolJSONDecode,
	}}}
	if outcome := classifyTurnOutcome(genuineFailure); outcome != OutcomeDecisionProtocolError {
		t.Fatalf("native genuine failure outcome = %q, want %q", outcome, OutcomeDecisionProtocolError)
	}
}

// TestParseNumericOutputAcceptsUnitSuffix covers the 2026-09-21 false
// negatives: nt-0001 "9000 MiB per hour" and hyb-0002 "9806.55 EUR". Both
// prompts name the unit they want the figure in, so repeating it in the reply
// answers the question asked rather than adding an unchecked second claim.
func TestParseNumericOutputAcceptsUnitSuffix(t *testing.T) {
	t.Parallel()
	valid := map[string]float64{
		"9000 MiB per hour": 9000,
		"9806.55 EUR":       9806.55,
		"720 GB":            720,
		"45 seconds":        45,
		"€14,746.84 EUR":    14746.84,
		"12.5 %":            12.5,
		"3 km/h":            3,
		"45 days.":          45,
	}
	for input, want := range valid {
		got, err := parseNumericOutput(input)
		if err != nil {
			t.Fatalf("parseNumericOutput(%q) err = %v, want %g", input, err, want)
		}
		if math.Abs(got-want) > 1e-9 {
			t.Fatalf("parseNumericOutput(%q) = %g, want %g", input, got, want)
		}
	}
	// A unit may not carry a second figure, a clause or a sentence.
	invalid := []string{
		"45 seconds (it was 120 seconds before 3.0.0)",
		"9000 MiB per hour, but only while the backup runs",
		"14746.84 at the September rate rather than the June one",
		"42 the answer is",
		"42 the answer",
		"42 approximately GB",
		"5 548.95",
	}
	for _, input := range invalid {
		if got, err := parseNumericOutput(input); err == nil {
			t.Fatalf("parseNumericOutput(%q) = %g, want an error", input, got)
		}
	}
}

// TestOutputEqualsNormalizesCaseAndTrailingPunctuation covers cfg-0003 "No"
// and doc-0002 "45 days." — orthography, not a different answer.
func TestOutputEqualsNormalizesCaseAndTrailingPunctuation(t *testing.T) {
	t.Parallel()
	expected := "no"
	for _, output := range []string{"no", "No", "NO", " No. ", "no."} {
		if failures := answerFailures(
			Expectation{OutputEquals: &expected},
			output,
		); len(failures) != 0 {
			t.Fatalf("answerFailures(%q) = %v, want none", output, failures)
		}
	}
	for _, output := range []string{"yes", "no idea", "not enabled", ""} {
		if failures := answerFailures(
			Expectation{OutputEquals: &expected},
			output,
		); len(failures) != 1 {
			t.Fatalf("answerFailures(%q) = %v, want one failure", output, failures)
		}
	}
	if failures := answerFailures(
		Expectation{OutputEqualsAny: []string{"45", "45 days"}},
		"45 days.",
	); len(failures) != 0 {
		t.Fatalf("output_equals_any failures = %v, want none", failures)
	}
}

// TestZeroCallContractIsNotATurnFailure locks the notool decoupling: the
// contract is reported through no_call_accuracy / active_no_call, and a
// correct answer is not cancelled by an exploratory call. A non-empty tools
// list stays an exact-sequence assertion.
func TestZeroCallContractIsNotATurnFailure(t *testing.T) {
	t.Parallel()
	answer := "443"
	expect := Expectation{Tools: []string{}, OutputEquals: &answer}
	explored := agent.Result{
		Output: "443",
		Steps:  []agent.Step{{Tool: "list_files"}},
	}
	if failures := validateTurn(expect, explored, nil); len(failures) != 0 {
		t.Fatalf("zero-call turn failures = %v, want none", failures)
	}
	testCase := Case{ID: "nt", Turns: []Turn{{Expect: expect}}}
	summary := summarize("run", []Case{testCase}, []CaseResult{{
		ID:     "nt",
		Passed: true,
		Turns:  []TurnResult{{Result: explored, Passed: true}},
	}}, nil)
	assertScore(t, "no-call accuracy", summary.Metrics.NoCallAccuracy, 0, 1)
	assertScore(t, "answer accuracy", summary.Metrics.AnswerAccuracy, 1, 1)

	exact := Expectation{Tools: []string{"read_file"}}
	if failures := validateTurn(exact, explored, nil); len(failures) != 1 {
		t.Fatalf("exact tools failures = %v, want one", failures)
	}
}

// TestInvalidCasesLeaveTheTaskSuccessDenominator locks the voiding rule: an
// upstream-aborted case is a lost sample, not a wrong answer.
func TestInvalidCasesLeaveTheTaskSuccessDenominator(t *testing.T) {
	t.Parallel()
	cases := []Case{{ID: "ok"}, {ID: "aborted"}}
	summary := summarize("run", cases, []CaseResult{
		{ID: "ok", Passed: true},
		{ID: "aborted", Invalid: true, InvalidReason: "upstream provider failure: boom"},
	}, nil)
	assertScore(t, "task success", summary.Metrics.TaskSuccess, 1, 1)
	if summary.Metrics.InvalidCases != 1 {
		t.Fatalf("invalid cases = %d, want 1", summary.Metrics.InvalidCases)
	}
}

// TestOutputEqualsAcceptsUnitOnNumericAnswersOnly covers web-0002 ("45
// seconds") while keeping the abstention guard: a unit attaches to a number,
// so the allowance must not read "no idea" as the answer "no".
func TestOutputEqualsAcceptsUnitOnNumericAnswersOnly(t *testing.T) {
	t.Parallel()
	numeric := "45"
	for _, output := range []string{"45", "45 seconds", "45 s", "45 seconds."} {
		if failures := answerFailures(
			Expectation{OutputEquals: &numeric}, output,
		); len(failures) != 0 {
			t.Fatalf("answerFailures(%q) = %v, want none", output, failures)
		}
	}
	// Provenance is still not a bare answer: it carries the decoy 120.
	for _, output := range []string{
		"45 seconds (raised from 120 in the 3.0.0 release)",
		"120",
		"UNKNOWN",
	} {
		if failures := answerFailures(
			Expectation{OutputEquals: &numeric}, output,
		); len(failures) != 1 {
			t.Fatalf("answerFailures(%q) = %v, want one failure", output, failures)
		}
	}
	word := "no"
	for _, output := range []string{"no idea", "no such setting", "not enabled"} {
		if failures := answerFailures(
			Expectation{OutputEquals: &word}, output,
		); len(failures) != 1 {
			t.Fatalf("word answer %q = %v, want one failure", output, failures)
		}
	}
}

// TestAnswerFormatViolationsSeparateShapeFromCorrectness locks the new
// counter: a right value in the wrong shape is reported apart from a wrong
// value, so a trap case's score is not silently depressed by formatting.
func TestAnswerFormatViolationsSeparateShapeFromCorrectness(t *testing.T) {
	t.Parallel()
	answer := "45"
	expect := Expectation{OutputEquals: &answer}
	if !isAnswerFormatViolation(expect, "45 seconds (raised from 120 in 3.0.0)") {
		t.Fatal("leading correct value must count as a format violation")
	}
	// The value has to sit at one end of the reply. Buried mid-sentence it is
	// a mention, not a commitment, and on a case whose decoy is itself a
	// number that difference is all there is to go on.
	for _, wrong := range []string{
		"120",
		"the old value 45 was replaced by 120",
		"UNKNOWN",
		"",
	} {
		if isAnswerFormatViolation(expect, wrong) {
			t.Fatalf("%q must not count as a format violation", wrong)
		}
	}
	number := 9000.0
	tolerance := 0.01
	numeric := Expectation{ExpectedNumber: &number, Tolerance: &tolerance}
	if !isAnswerFormatViolation(numeric, "9000 MiB per hour, measured over the window") {
		t.Fatal("numeric expectation must report a leading-value format violation")
	}
}

// TestEmphasisMarkersAreNormalized covers code-0004 "**9**" and tab-0004's
// bolded figure: Markdown emphasis is typesetting, not a different answer.
// A bolded answer trailed by prose stays a failure — it is a format violation,
// which the counter reports separately.
func TestEmphasisMarkersAreNormalized(t *testing.T) {
	t.Parallel()
	number := 9.0
	tolerance := 0.01
	expect := Expectation{ExpectedNumber: &number, Tolerance: &tolerance}
	for _, output := range []string{"9", "**9**", "__9__", "`9`", " **9** "} {
		if failures := answerFailures(expect, output); len(failures) != 0 {
			t.Fatalf("answerFailures(%q) = %v, want none", output, failures)
		}
	}
	money := 23609.6
	cents := Expectation{ExpectedNumber: &money, Tolerance: &tolerance}
	if failures := answerFailures(cents, "**$23,609.60**"); len(failures) != 0 {
		t.Fatalf("bolded currency = %v, want none", failures)
	}
	verbose := "**$23,609.60**\n\nOrders totaled $24,555.50 and refunds reduce revenue."
	if failures := answerFailures(cents, verbose); len(failures) != 1 {
		t.Fatalf("bolded figure plus prose = %v, want one failure", failures)
	}
	if !isAnswerFormatViolation(cents, verbose) {
		t.Fatal("bolded figure plus prose must count as a format violation")
	}
	// An asterisk inside the answer is content, not emphasis.
	glob := "*.log"
	if failures := answerFailures(Expectation{OutputEquals: &glob}, "*.log"); len(failures) != 0 {
		t.Fatalf("glob answer = %v, want none", failures)
	}
}

// TestAnswerFormatViolationDetectsTrailingCommitment covers the small-instruct
// shape: reason in prose, then commit the value at the end. Qwen3-8B answers
// nt-0001 and cfg-0001 correctly this way, and scoring only the leading
// position would file both under wrong answers.
func TestAnswerFormatViolationDetectsTrailingCommitment(t *testing.T) {
	t.Parallel()
	number := 9000.0
	tolerance := 0.01
	numeric := Expectation{ExpectedNumber: &number, Tolerance: &tolerance}
	if !isAnswerFormatViolation(numeric,
		"The ingest rate of 2.5 MiB per second is equivalent to 2.5 * 3600 = 9000 MiB per hour.\n\n9000") {
		t.Fatal("trailing bare value must count as a format violation")
	}
	port := "8431"
	text := Expectation{OutputEquals: &port}
	if !isAnswerFormatViolation(text,
		"The notify-hub service listens on TCP port **8431**.\n\nFinal answer: 8431") {
		t.Fatal("marker-introduced value must count as a format violation")
	}
	// A value buried mid-sentence still does not count: on a case whose decoy
	// is a number, position is the only thing separating answer from mention.
	answer := "45"
	if isAnswerFormatViolation(Expectation{OutputEquals: &answer},
		"it was 120 before, now 45 was chosen instead by the team") {
		t.Fatal("mid-sentence mention must not count as a format violation")
	}
	if isAnswerFormatViolation(Expectation{OutputEquals: &answer}, "120") {
		t.Fatal("a wrong answer must not count as a format violation")
	}
}

// TestParseNumericOutputAcceptsLeadingCurrencyCode covers hyb-0004's
// "EUR 14,746.84": a currency written as a code in front of the figure is the
// same answer as the same figure with a symbol.
func TestParseNumericOutputAcceptsLeadingCurrencyCode(t *testing.T) {
	t.Parallel()
	valid := map[string]float64{
		"EUR 14,746.84": 14746.84,
		"USD 5":         5,
		"GBP 12,680.00": 12680,
		"eur 1.5":       1.5,
	}
	for input, want := range valid {
		got, err := parseNumericOutput(input)
		if err != nil || math.Abs(got-want) > 1e-9 {
			t.Fatalf("parseNumericOutput(%q) = %g, %v; want %g", input, got, err, want)
		}
	}
	for _, input := range []string{"approximately 5", "the 5", "about 42", "roughly 7"} {
		if got, err := parseNumericOutput(input); err == nil {
			t.Fatalf("parseNumericOutput(%q) = %g, want an error", input, got)
		}
	}
}
