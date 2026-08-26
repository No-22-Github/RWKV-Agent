package eval

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestBuiltinCasesValidate(t *testing.T) {
	smoke := SmokeCases()
	if len(smoke) != 10 {
		t.Fatalf("smoke cases = %d, want 10", len(smoke))
	}
	if err := ValidateCases(smoke); err != nil {
		t.Fatal(err)
	}
	boundary, err := BoundaryCases()
	if err != nil {
		t.Fatal(err)
	}
	if len(boundary) != 18 {
		t.Fatalf("boundary cases = %d, want 18", len(boundary))
	}
	if err := ValidateCases(boundary); err != nil {
		t.Fatal(err)
	}
	for _, testCase := range boundary {
		if testCase.Category == "" || testCase.Source == "" {
			t.Fatalf("boundary case lacks attribution metadata: %+v", testCase)
		}
	}
	assistant, err := AssistantCases()
	if err != nil {
		t.Fatal(err)
	}
	if len(assistant) != 6 {
		t.Fatalf("assistant cases = %d, want 6", len(assistant))
	}
	bfclProduct, err := BFCLProductCases()
	if err != nil {
		t.Fatal(err)
	}
	if len(bfclProduct) != 60 {
		t.Fatalf("BFCL product cases = %d, want 60", len(bfclProduct))
	}
	categoryCounts := map[string]int{}
	for _, testCase := range bfclProduct {
		categoryCounts[testCase.Category]++
	}
	for _, category := range []string{"bfcl-irrelevance", "bfcl-missing-required", "bfcl-multiturn"} {
		if categoryCounts[category] != 20 {
			t.Fatalf("BFCL product category %q = %d, want 20", category, categoryCounts[category])
		}
	}
	builtin, err := BuiltinSuite(SuiteBFCLProduct)
	if err != nil {
		t.Fatal(err)
	}
	if len(builtin) != len(bfclProduct) {
		t.Fatalf("BFCL product builtin routing = %d, want %d", len(builtin), len(bfclProduct))
	}
}

func TestLoadCasesUsesStrictVersionedSchema(t *testing.T) {
	valid := `{
		  "schema_version": 4,
	  "cases": [{
	    "id": "read",
	    "description": "Read a fixture.",
	    "files": {"note.txt": "hello"},
	    "turns": [{
	      "prompt": "Read note.txt.",
	      "expect": {
	        "route": "inspect",
	        "tools": ["read_file"],
	        "calls": [{"name": "read_file", "arguments": {"path": "note.txt"}}]
	      }
	    }]
	  }]
	}`
	path := filepath.Join(t.TempDir(), "cases.json")
	if err := os.WriteFile(path, []byte(valid), 0o600); err != nil {
		t.Fatal(err)
	}
	cases, err := LoadCases(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != 1 || cases[0].ID != "read" {
		t.Fatalf("cases = %+v", cases)
	}

	unknown := strings.Replace(valid, `"prompt": "Read note.txt."`, `"prompt": "Read note.txt.", "unknown": true`, 1)
	if err := os.WriteFile(path, []byte(unknown), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := LoadCases(path); err == nil ||
		!strings.Contains(err.Error(), "unknown field") {
		t.Fatalf("unknown field error = %v", err)
	}

	wrongVersion := strings.Replace(valid, `"schema_version": 4`, `"schema_version": 1`, 1)
	if err := os.WriteFile(path, []byte(wrongVersion), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := LoadCases(path); err == nil ||
		!strings.Contains(err.Error(), "unsupported case schema version") {
		t.Fatalf("schema version error = %v", err)
	}
}

func TestValidateCasesAcceptsBoundaryExpectations(t *testing.T) {
	answer := "42"
	number := 42.0
	tolerance := 0.1
	cases := []Case{{
		ID:          "boundary",
		Description: "Boundary scoring contract.",
		Turns: []Turn{{
			Prompt: "Inspect evidence.",
			Expect: Expectation{
				RequiredTools:  []string{"read_file"},
				ForbiddenTools: []string{"list_files"},
				RequiredCalls: []ExpectedCall{{
					Name:      "read_file",
					Arguments: map[string]any{"path": "data.txt"},
				}},
				OutputEquals: &answer,
			},
		}, {
			Prompt: "Compute a value.",
			Expect: Expectation{
				RequiredTools:  []string{"read_file"},
				ExpectedNumber: &number,
				Tolerance:      &tolerance,
			},
		}},
	}}
	if err := ValidateCases(cases); err != nil {
		t.Fatal(err)
	}

	cases[0].Turns[0].Expect.RequiredTools = []string{"read_file", "read_file"}
	if err := ValidateCases(cases); err == nil ||
		!strings.Contains(err.Error(), "repeats required tool") {
		t.Fatalf("duplicate required tool error = %v", err)
	}
}

func TestValidateCasesRequiresExactEmptyToolsForActiveNoCall(t *testing.T) {
	testCase := Case{
		ID:          "active-no-call",
		Description: "Require a deliberate no-call decision.",
		Turns: []Turn{{
			Prompt: "Ask for missing arguments.",
			Expect: Expectation{
				ForbiddenTools:      []string{"read_file"},
				RequireActiveNoCall: true,
			},
		}},
	}
	if err := ValidateCases([]Case{testCase}); err == nil ||
		!strings.Contains(err.Error(), "exact empty list") {
		t.Fatalf("active no-call validation error = %v", err)
	}
	testCase.Turns[0].Expect.Tools = []string{}
	testCase.Turns[0].Expect.ForbiddenTools = nil
	if err := ValidateCases([]Case{testCase}); err != nil {
		t.Fatal(err)
	}
}

func TestValidateCasesRejectsFixturePathTraversal(t *testing.T) {
	testCase := Case{
		ID:          "escape",
		Description: "Invalid fixture.",
		Files:       map[string]string{"../secret.txt": "secret"},
		Turns: []Turn{{
			Prompt: "Read it.",
			Expect: Expectation{
				Tools: []string{},
			},
		}},
	}
	if err := ValidateCases([]Case{testCase}); err == nil ||
		!strings.Contains(err.Error(), "escapes its fixture root") {
		t.Fatalf("path traversal error = %v", err)
	}
}

func TestSelectCasesPreservesRequestedOrderAndRejectsInvalidIDs(t *testing.T) {
	cases := BuiltinCases()
	selected, err := SelectCases(cases, []string{"list_directory", "respond_arithmetic"})
	if err != nil {
		t.Fatal(err)
	}
	if len(selected) != 2 ||
		selected[0].ID != "list_directory" ||
		selected[1].ID != "respond_arithmetic" {
		t.Fatalf("selected cases = %+v", selected)
	}
	if _, err := SelectCases(cases, []string{"respond_arithmetic", "respond_arithmetic"}); err == nil ||
		!strings.Contains(err.Error(), "duplicate selected case") {
		t.Fatalf("duplicate selection error = %v", err)
	}
	if _, err := SelectCases(cases, []string{"not_a_case"}); err == nil ||
		!strings.Contains(err.Error(), "unknown eval case") {
		t.Fatalf("unknown selection error = %v", err)
	}
}
