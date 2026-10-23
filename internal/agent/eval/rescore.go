package eval

import (
	"errors"
	"strings"
)

// answerContractFailure is the product-harness failure runner.go adds on top
// of validateTurn; Rescore recomputes it rather than carrying it over.
const answerContractFailure = "answer contract repaired: the App showed the fallback reply, not the model's answer"

// Rescore re-judges a finished case against the current scorer and the
// case's current expectations, without rerunning the model. Turn-level
// checks are recomputed from the recorded agent.Result. What the record does
// not hold is carried over unchanged: case-level end-state failures
// (expect.files, expect.run, max_calls need the final workspace) and Primitive
// Bench failures. The returned result has Turns[i].Failures and Passed
// replaced; the input is not modified.
func Rescore(testCase Case, old CaseResult, productHarness bool) CaseResult {
	result := old
	result.Turns = make([]TurnResult, len(old.Turns))
	copy(result.Turns, old.Turns)
	result.Passed = old.Error == "" && len(old.Failures) == 0 &&
		len(old.Turns) == len(testCase.Turns)
	for index := range result.Turns {
		turn := &result.Turns[index]
		if index >= len(testCase.Turns) {
			turn.Passed = false
			result.Passed = false
			continue
		}
		expect := testCase.Turns[index].Expect
		var runErr error
		if turn.RunnerError != "" {
			runErr = errors.New(turn.RunnerError)
		}
		failures := validateTurn(expect, turn.Result, runErr)
		if productHarness && turn.Result.AnswerContractRepaired && hasAnswerExpectation(expect) {
			failures = append(failures, answerContractFailure)
		}
		for _, failure := range old.Turns[index].Failures {
			if strings.HasPrefix(failure, "Primitive Bench") {
				failures = append(failures, failure)
			}
		}
		turn.Failures = failures
		turn.Passed = len(failures) == 0
		if !turn.Passed {
			result.Passed = false
		}
	}
	return result
}
