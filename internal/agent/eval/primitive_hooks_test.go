package eval

import (
	"encoding/json"
	"errors"
	"strings"
	"testing"
)

func TestPrimitiveScenarioHookTwoStepRemindsOnFinalStdout(t *testing.T) {
	hook := primitiveScenarioHook("two_step_program_output", &primitiveRuntime{})
	if hook == nil {
		t.Fatal("two_step case has no hook")
	}
	if text := hook("run_file", json.RawMessage(`{"path":"make_token.py"}`), "wrote token.txt", nil); text != "" {
		t.Fatalf("hook fired on the first program run: %q", text)
	}
	text := hook("run_file", json.RawMessage(`{"path":"use_token.py"}`), "FINAL=RIVER-42-OK", nil)
	if !strings.Contains(text, "verbatim") || !strings.Contains(text, "FINAL= prefix") {
		t.Fatalf("hook text = %q", text)
	}
	if text := hook("read_file", nil, "FINAL=irrelevant", nil); text != "" {
		t.Fatalf("hook fired for a non-run_file tool: %q", text)
	}
	if text := hook("run_file", nil, "FINAL=x", nopeError()); text != "" {
		t.Fatalf("hook fired for a failed call: %q", text)
	}
}

func TestPrimitiveScenarioHookLocInterestRemindsOnScheduleRead(t *testing.T) {
	hook := primitiveScenarioHook("loc_interest_8_months", &primitiveRuntime{scenario: ""})
	if hook == nil {
		t.Fatal("loc_interest case has no hook")
	}
	if text := hook("read_file", json.RawMessage(`{"path":"loan_terms.txt"}`), "terms", nil); text != "" {
		t.Fatalf("hook fired for loan_terms read: %q", text)
	}
	text := hook("read_file", json.RawMessage(`{"path":"balance_schedule.csv"}`), "1: month,balance,days", nil)
	if !strings.Contains(text, "SUM") || !strings.Contains(text, "2 decimals") ||
		!strings.Contains(text, "single final number") {
		t.Fatalf("hook text = %q", text)
	}
	if text := hook("read_file", json.RawMessage(`{"path":"balance_schedule.csv"}`), "rows", nopeError()); text != "" {
		t.Fatalf("hook fired for a failed read: %q", text)
	}
}

func TestPrimitiveScenarioHookKeyedByIDEvenWithEmptyScenario(t *testing.T) {
	// Fixture 021 imports with an empty scenario field; the hook must still
	// attach via the case ID.
	hook := primitiveScenarioHook("loc_interest_8_months", &primitiveRuntime{scenario: ""})
	if hook == nil {
		t.Fatal("empty-scenario case did not receive its ID-keyed hook")
	}
	if primitiveScenarioHook("read_only_repo_explain", &primitiveRuntime{scenario: "read_only_repo_explain"}) != nil {
		t.Fatal("unwired case received a hook")
	}
}

func TestPrimitiveScenarioHookDescriptionsListsOnlyWiredCases(t *testing.T) {
	cases := []Case{
		{ID: "two_step_program_output", primitive: &primitiveRuntime{scenario: "two_step_program_output"}},
		{ID: "loc_interest_8_months", primitive: &primitiveRuntime{scenario: ""}},
		{ID: "code_patch_edge_case", primitive: &primitiveRuntime{scenario: "code_patch_edge_case"}},
		{ID: "read_only_repo_explain", primitive: &primitiveRuntime{scenario: "read_only_repo_explain"}},
	}
	descriptions := primitiveScenarioHookDescriptions(cases)
	if len(descriptions) != 2 ||
		descriptions[0] != "two_step_program_output=verbatim-stdout-reminder" ||
		descriptions[1] != "loc_interest_8_months=sum-all-rows-reminder" {
		t.Fatalf("descriptions = %v", descriptions)
	}
}

func nopeError() error {
	return errors.New("planned failure")
}
