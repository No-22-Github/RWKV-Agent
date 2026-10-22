package bench

import (
	"strings"
	"testing"
)

// The exam suites are recognised by their manifest, not their name: the 10-21
// rename to agent-exam broke a "exam-" prefix test and sent exams to the bench
// budget (380 cases, 16 steps) instead of the manifest's count and the App's.
func TestExamSuitesUseTheManifest(t *testing.T) {
	for _, suite := range []string{"agent-exam", "agent-exam-quick"} {
		if !isExamSuite(suite) {
			t.Fatalf("%s is not recognised as an exam suite", suite)
		}
	}
	for _, suite := range []string{"workbank", "p13", "bfcl-product", "boundary"} {
		if isExamSuite(suite) {
			t.Fatalf("%s recognised as an exam suite", suite)
		}
	}
	budget, err := gateBudget(&SweepArgs{}, "agent-exam")
	if err != nil {
		t.Fatal(err)
	}
	if budget.cases != 568 {
		t.Fatalf("agent-exam gate expects %d cases, want the manifest's 568", budget.cases)
	}
}

func TestResolveSuiteName(t *testing.T) {
	for name, want := range map[string]string{
		"exam-full": "agent-exam", "exam-quick": "agent-exam-quick",
		"agent-exam": "agent-exam", "agent-exam-v1.1": "agent-exam",
		"agent-exam-quick-v1.1": "agent-exam-quick", "workbank": "workbank",
	} {
		if got, err := resolveSuiteName(name); err != nil || got != want {
			t.Fatalf("resolveSuiteName(%q) = %q, %v; want %q", name, got, err, want)
		}
	}
	// A versioned name that is not the manifest's version must not run the
	// newer exam silently.
	if _, err := resolveSuiteName("agent-exam-v9.9"); err == nil || !strings.Contains(err.Error(), "agent-exam-v1.1") {
		t.Fatalf("stale exam version error = %v", err)
	}
}
