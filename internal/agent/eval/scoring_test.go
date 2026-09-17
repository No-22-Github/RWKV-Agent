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
		"USD 5",
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
