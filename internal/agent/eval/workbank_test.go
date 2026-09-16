package eval

import (
	"context"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func generatedWork(text string) continuation.Result {
	return continuation.Result{Text: text, FinishReason: continuation.FinishStop}
}

func TestLoadCasesAcceptsSchemaV5WorkbankCase(t *testing.T) {
	t.Parallel()
	file := `{
		"schema_version": 5,
		"cases": [{
			"id": "tab-0001",
			"description": "Sum revenue. WORKBANK-CANARY-3f9a1c2e",
			"tags": {
				"scenario": "tabular",
				"level": "L1",
				"status": "draft"
			},
			"web_fixture": [{
				"query_match": "northwind",
				"url": "https://example.invalid/northwind",
				"title": "Northwind rates",
				"published_at": "2026-08-01"
			}],
			"expect": {
				"files": {"out/answer.txt": {"contains": ["14817.35"]}},
				"max_calls": {"read_file": 6}
			},
			"files": {"orders.csv": "order_id,amount\nA-1041,14817.35\n"},
			"turns": [{
				"prompt": "Sum revenue and write it to out/answer.txt.",
				"expect": {"expected_number": 14817.35, "tolerance": 0.01}
			}]
		}]
	}`
	cases, err := decodeCases([]byte(file))
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != 1 {
		t.Fatalf("cases = %d, want 1", len(cases))
	}
	testCase := cases[0]
	if testCase.Tags["scenario"] != "tabular" {
		t.Fatalf("tags not preserved: %v", testCase.Tags)
	}
	if len(testCase.WebFixture) != 1 || testCase.WebFixture[0].PublishedAt != "2026-08-01" {
		t.Fatalf("web fixture not preserved: %+v", testCase.WebFixture)
	}
	if testCase.Expect == nil || len(testCase.Expect.Files) != 1 {
		t.Fatalf("case expect not preserved: %+v", testCase.Expect)
	}
}

func TestLoadCasesStillAcceptsLegacyV4(t *testing.T) {
	t.Parallel()
	file := `{
		"schema_version": 4,
		"cases": [{
			"id": "legacy-0",
			"description": "v4 case without tags or case-level expect.",
			"files": {"facts.txt": "TRACE-9001\n"},
			"turns": [{
				"prompt": "Report the code.",
				"expect": {
					"tools": ["read_file"],
					"output_contains": ["TRACE-9001"]
				}
			}]
		}]
	}`
	cases, err := decodeCases([]byte(file))
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != 1 || cases[0].ID != "legacy-0" {
		t.Fatalf("v4 case not loaded: %+v", cases)
	}
}

func TestValidateCasesRelaxesToolExpectationForResultTurns(t *testing.T) {
	t.Parallel()
	answer := 14817.35
	relaxed := []Case{{
		ID:          "relaxed-0",
		Description: "answer-only turn without tool expectations",
		Turns: []Turn{{
			Prompt: "What is the answer?",
			Expect: Expectation{ExpectedNumber: &answer, Tolerance: &[]float64{0.01}[0]},
		}},
	}}
	if err := ValidateCases(relaxed); err != nil {
		t.Fatalf("answer-only turn should validate: %v", err)
	}
	empty := []Case{{
		ID:          "empty-0",
		Description: "turn with no expectation at all",
		Turns: []Turn{{
			Prompt: "What is the answer?",
			Expect: Expectation{},
		}},
	}}
	if err := ValidateCases(empty); err == nil {
		t.Fatal("a turn with no expectation must still be rejected")
	}
	viaCaseLevel := []Case{{
		ID:          "caselevel-0",
		Description: "turn without expectations but case-level files",
		Expect: &CaseExpect{Files: map[string]FileExpectation{
			"out.txt": {Contains: []string{"done"}},
		}},
		Turns: []Turn{{Prompt: "Write out.txt."}},
	}}
	if err := ValidateCases(viaCaseLevel); err != nil {
		t.Fatalf("case-level result expectation should relax turns: %v", err)
	}
}

func TestValidateCaseExpectRejections(t *testing.T) {
	t.Parallel()
	cases := []struct {
		name   string
		testCase Case
	}{
		{
			name: "files combine equals and contains",
			testCase: Case{
				ID: "bad-0", Description: "bad",
				Expect: &CaseExpect{Files: map[string]FileExpectation{
					"out.txt": {Equals: &[]string{"a"}[0], Contains: []string{"a"}},
				}},
				Turns: []Turn{{Prompt: "x", Expect: Expectation{}}},
			},
		},
		{
			name: "unchanged without initial fixture",
			testCase: Case{
				ID: "bad-1", Description: "bad",
				Expect: &CaseExpect{Files: map[string]FileExpectation{
					"out.txt": {Unchanged: true},
				}},
				Turns: []Turn{{Prompt: "x", Expect: Expectation{}}},
			},
		},
		{
			name: "absent on an initial fixture file",
			testCase: Case{
				ID: "bad-2", Description: "bad",
				Files: map[string]string{"cfg.yml": "a: 1\n"},
				Expect: &CaseExpect{Files: map[string]FileExpectation{
					"cfg.yml": {Absent: true},
				}},
				Turns: []Turn{{Prompt: "x", Expect: Expectation{}}},
			},
		},
		{
			name: "run script not shipped in files",
			testCase: Case{
				ID: "bad-3", Description: "bad",
				Expect: &CaseExpect{Run: &RunExpectation{
					Path: "verify.py", ExpectedStdout: "1",
				}},
				Turns: []Turn{{Prompt: "x", Expect: Expectation{}}},
			},
		},
		{
			name: "max_calls budget below one",
			testCase: Case{
				ID: "bad-4", Description: "bad",
				Expect: &CaseExpect{MaxCalls: map[string]int{"read_file": 0}},
				Turns: []Turn{{Prompt: "x", Expect: Expectation{}}},
			},
		},
	}
	for _, item := range cases {
		if err := ValidateCases([]Case{item.testCase}); err == nil {
			t.Fatalf("%s: expected validation error", item.name)
		}
	}
}

func TestLoadCasesDirDraftGatingAndOrder(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	write := func(rel, id, status string) {
		path := filepath.Join(root, rel)
		if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
			t.Fatal(err)
		}
		content := fmt.Sprintf(
			`{"id":%q,"description":"bank case","tags":{"status":%q},"turns":[{"prompt":"p","expect":{"expected_number":1,"tolerance":0}}]}`,
			id, status,
		)
		if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
			t.Fatal(err)
		}
	}
	write("tabular/tab-0002/case.json", "tab-0002", "reviewed")
	write("tabular/tab-0001/case.json", "tab-0001", "draft")
	write("logs/log-0001/case.json", "log-0001", "frozen")

	byDefault, err := LoadCasesDir(root, false)
	if err != nil {
		t.Fatal(err)
	}
	if len(byDefault) != 2 {
		t.Fatalf("default load = %d cases, want drafts excluded", len(byDefault))
	}
	if byDefault[0].ID != "log-0001" || byDefault[1].ID != "tab-0002" {
		t.Fatalf("cases not sorted by ID: %v", []string{byDefault[0].ID, byDefault[1].ID})
	}
	withDrafts, err := LoadCasesDir(root, true)
	if err != nil {
		t.Fatal(err)
	}
	if len(withDrafts) != 3 {
		t.Fatalf("include-draft load = %d cases, want 3", len(withDrafts))
	}
}

func TestWorkCatalogShapeAndHash(t *testing.T) {
	t.Parallel()
	workspace := filepath.Join(t.TempDir(), "workspace")
	if err := os.MkdirAll(workspace, 0o700); err != nil {
		t.Fatal(err)
	}
	catalog, err := buildWorkToolCatalog(workspace, nil, 0, nil)
	if err != nil {
		t.Fatal(err)
	}
	if len(catalog) != len(workToolCatalogNames) {
		t.Fatalf("catalog size = %d, want %d", len(catalog), len(workToolCatalogNames))
	}
	names := map[string]bool{}
	for _, tool := range catalog {
		names[tool.Spec().Name] = true
	}
	for _, want := range workToolCatalogNames {
		if !names[want] {
			t.Fatalf("catalog is missing tool %q", want)
		}
	}
	first := workToolCatalogHash(catalog)
	second, err := buildWorkToolCatalog(workspace, nil, 0, nil)
	if err != nil {
		t.Fatal(err)
	}
	if first != workToolCatalogHash(second) {
		t.Fatal("catalog hash is not stable across builds")
	}
}

func TestWebFixturePublishedAtPassthrough(t *testing.T) {
	t.Parallel()
	providers := webFixtureProviders{entries: []WebFixtureEntry{{
		QueryMatch:  "northwind",
		URL:         "https://example.invalid/northwind",
		Title:       "Northwind rates",
		PublishedAt: "2026-08-01",
	}}}
	results, err := providers.Search(context.Background(), tools.WebSearchRequest{
		Query:      "northwind rates",
		MaxResults: 5,
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(results) != 1 || results[0].PublishedAt != "2026-08-01" {
		t.Fatalf("published_at not passed through: %+v", results)
	}
}

func TestFileExpectFailuresDetectByteChanges(t *testing.T) {
	t.Parallel()
	workspace := t.TempDir()
	writeWorkFile(t, workspace, "cfg.yml", "port: 8080\n")
	writeWorkFile(t, workspace, "out.txt", "done: 14817.35\n")
	testCase := Case{
		ID:    "files-0",
		Files: map[string]string{"cfg.yml": "port: 8080\n"},
		Expect: &CaseExpect{Files: map[string]FileExpectation{
			"cfg.yml":   {Unchanged: true},
			"out.txt":   {Contains: []string{"done"}},
			"ghost.txt": {Absent: true},
		}},
	}
	if failures := fileExpectFailures(workspace, testCase); len(failures) != 0 {
		t.Fatalf("intact workspace: failures = %v, want none", failures)
	}
	if err := os.WriteFile(filepath.Join(workspace, "cfg.yml"), []byte("port: 9090\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	failures := fileExpectFailures(workspace, testCase)
	if len(failures) != 1 || !strings.Contains(failures[0], "changed from the initial fixture") {
		t.Fatalf("failures = %v, want the unchanged violation", failures)
	}
}

func TestMaxCallsCountsRejectedCalls(t *testing.T) {
	t.Parallel()
	result := CaseResult{Turns: []TurnResult{{
		Result: agent.Result{Steps: []agent.Step{
			{Tool: "read_file", ToolExecuted: true},
			{Tool: "read_file", ToolRejected: "duplicate_tool_call"},
			{Tool: "read_file", ToolRejected: "duplicate_tool_call"},
		}},
	}}}
	testCase := Case{
		ID:     "calls-0",
		Expect: &CaseExpect{MaxCalls: map[string]int{"read_file": 2}},
	}
	aggregateCaseInterventions(testCase, &result)
	failures := maxCallsFailures(testCase, &result)
	if len(failures) != 1 || !strings.Contains(failures[0], "issued 3 calls") {
		t.Fatalf("failures = %v, want budget violation counting rejected calls", failures)
	}
	if result.ToolCalls != 3 || result.DuplicateRejects != 2 {
		t.Fatalf("intervention counters = %d/%d, want 3/2", result.ToolCalls, result.DuplicateRejects)
	}
}

func TestRunExpectationScriptIsolationAndComparison(t *testing.T) {
	t.Parallel()
	workspace := t.TempDir()
	writeWorkFile(t, workspace, "verify.py", "import sys\nprint(sys.argv[1])\n")
	testCase := Case{
		ID: "run-0",
		Expect: &CaseExpect{Run: &RunExpectation{
			Path:           "verify.py",
			Args:           []string{"42"},
			ExpectedStdout: "42",
		}},
	}
	if failures, err := runExpectationScript(context.Background(), workspace, testCase); err != nil || len(failures) != 0 {
		t.Fatalf("happy path: err=%v failures=%v", err, failures)
	}
	// -I -S strips site-packages: pandas must not import.
	writeWorkFile(t, workspace, "heavy.py", "import pandas\nprint('nope')\n")
	isolated := Case{ID: "run-1", Expect: &CaseExpect{Run: &RunExpectation{
		Path: "heavy.py", ExpectedStdout: "nope",
	}}}
	if _, err := runExpectationScript(context.Background(), workspace, isolated); err == nil {
		t.Fatal("import pandas must fail under python3 -I -S")
	}
	// Hidden files land in the sandbox but never in the model workspace.
	writeWorkFile(t, workspace, "hidden_check.py", "import pathlib\nprint(pathlib.Path('hidden/key.txt').read_text())\n")
	hidden := Case{ID: "run-2", Expect: &CaseExpect{Run: &RunExpectation{
		Path:           "hidden_check.py",
		ExpectedStdout: "s3cret",
		HiddenFiles:    map[string]string{"hidden/key.txt": "s3cret"},
	}}}
	if failures, err := runExpectationScript(context.Background(), workspace, hidden); err != nil || len(failures) != 0 {
		t.Fatalf("hidden files: err=%v failures=%v", err, failures)
	}
	if _, err := os.Stat(filepath.Join(workspace, "hidden")); !os.IsNotExist(err) {
		t.Fatal("hidden files must not leak into the live workspace")
	}
	// Wrong expected stdout must fail line by line.
	mismatch := Case{ID: "run-3", Expect: &CaseExpect{Run: &RunExpectation{
		Path: "verify.py", Args: []string{"41"}, ExpectedStdout: "42",
	}}}
	failures, err := runExpectationScript(context.Background(), workspace, mismatch)
	if err != nil || len(failures) != 1 || !strings.Contains(failures[0], "stdout line 1") {
		t.Fatalf("mismatch: err=%v failures=%v", err, failures)
	}
}

func writeWorkFile(t *testing.T, root, rel, content string) {
	t.Helper()
	path := filepath.Join(root, rel)
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
}

func TestRunCaseLevelExpectationsEndToEnd(t *testing.T) {
	t.Parallel()
	writeAnswer := [][]continuation.Result{
		{
			generatedWork("inspect"),
			generatedWork(`<tool_call>{"name":"write_file","arguments":{"path":"out/answer.txt","content":"14817.35"}}</tool_call>`),
			generatedWork("14817.35"),
		},
	}
	report, err := Run(context.Background(), Config{
		Cases: []Case{{
			ID:          "tab-9001",
			Description: "write the answer into out/answer.txt",
			Tags:        map[string]any{"scenario": "tabular", "status": "draft"},
			Files: map[string]string{
				"orders.csv":     "order_id,amount\nA-1041,14817.35\n",
				"out/.keep":      "",
			},
			Expect: &CaseExpect{
				Files:    map[string]FileExpectation{"out/answer.txt": {Contains: []string{"14817.35"}}},
				MaxCalls: map[string]int{"write_file": 2},
			},
			Turns: []Turn{{
				Prompt: "Write the total to out/answer.txt.",
				Expect: Expectation{OutputContains: []string{"14817.35"}},
			}},
		}},
		Suite:       "workbank",
		ToolCatalog: WorkToolCatalogName,
		Model: ModelMetadata{Identifier: "scripted", Backend: "test", Provider: "test", Completion: "test"},
		Runner: agent.Options{
			MaxSteps:                4,
			ProtocolRetries:         1,
			DecisionMaxOutputTokens: 64,
			Protocol:                agent.G1Protocol{FewShot: true},
			Renderer:                agent.RWKVChatRenderer{},
			Router:                  agent.G1RouteProtocol{},
			RouteRenderer:           agent.RWKVChatRenderer{},
			RouteRetries:            1,
			RouteMaxOutputTokens:    8,
			Generation: continuation.Request{
				Model:           "scripted",
				MaxOutputTokens: 64,
			},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			index := 0
			script := writeAnswer[0]
			return continuation.GenerateFunc(func(
				context.Context,
				continuation.Request,
				continuation.EventSink,
			) (continuation.Result, error) {
				result := script[index]
				index++
				return result, nil
			}), noopTestCloser{}, nil
		},
		TempDir: t.TempDir(),
		Now:     func() time.Time { return time.Date(2026, 9, 17, 8, 0, 0, 0, time.UTC) },
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(report.Summary.Cases) != 1 || !report.Summary.Cases[0].Passed {
		failures := "none"
		if len(report.Summary.Cases) == 1 {
			failures = fmt.Sprintf("turns=%+v caseFailures=%v", report.Summary.Cases[0].Turns, report.Summary.Cases[0].Failures)
		}
		t.Fatalf("case should pass: %s", failures)
	}
	if report.Summary.Cases[0].Tags["scenario"] != "tabular" {
		t.Fatal("tags should ride into the case result")
	}
	if report.Summary.Cases[0].ToolCalls != 1 {
		t.Fatalf("tool calls = %d, want 1", report.Summary.Cases[0].ToolCalls)
	}
}

func TestRunManifestRecordsCatalogProfileAndState(t *testing.T) {
	t.Parallel()
	answer := "ok"
	report, err := Run(context.Background(), Config{
		Cases: []Case{{
			ID:          "manifest-0",
			Description: "manifest field check",
			Turns: []Turn{{
				Prompt: "answer ok",
				Expect: Expectation{Tools: []string{}, OutputEquals: &answer},
			}},
		}},
		Suite:       "workbank",
		ToolCatalog: WorkToolCatalogName,
		WireProfile: "xml-v1+align-qwen36+no-tool+bare+one-stage",
		StateID:     "state-test-1234",
		Model:       ModelMetadata{Identifier: "scripted", Backend: "test", Provider: "test", Completion: "test"},
		Runner: agent.Options{
			MaxSteps:   2,
			Generation: continuation.Request{MaxOutputTokens: 32},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return continuation.GenerateFunc(func(
				context.Context,
				continuation.Request,
				continuation.EventSink,
			) (continuation.Result, error) {
				return generatedWork(answer), nil
			}), noopTestCloser{}, nil
		},
		TempDir: t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	harness := report.Manifest.Harness
	if harness.ToolCatalog != WorkToolCatalogName {
		t.Fatalf("tool catalog = %q", harness.ToolCatalog)
	}
	if len(harness.ToolCatalogHash) != 64 {
		t.Fatalf("tool catalog hash = %q", harness.ToolCatalogHash)
	}
	if harness.WireProfile != "xml-v1+align-qwen36+no-tool+bare+one-stage" {
		t.Fatalf("wire profile = %q", harness.WireProfile)
	}
	if harness.StateID != "state-test-1234" || len(harness.StateSHA256) != 64 {
		t.Fatalf("state fields = %q / %q", harness.StateID, harness.StateSHA256)
	}
}
