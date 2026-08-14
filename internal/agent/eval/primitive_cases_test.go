package eval

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"slices"
	"sort"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestLoadPrimitiveCasesConvertsDeclarativeFixtures(t *testing.T) {
	directory := t.TempDir()
	caseJSON := `{
  "name": "numeric_case",
  "title": "Numeric case",
  "mode": "benchmark",
  "system": "base",
  "prompt": "Read the files, calculate, and submit.",
  "tools": "nav",
  "environment": {
    "kind": "emulated",
    "files": {
      "lines.txt": ["alpha", "beta"],
      "text.txt": {"text": "plain"},
      "noise.txt": {"repeat": {"text": "noise\n", "count": 3}}
    },
    "expected_submit": "42",
    "required_tools": ["read_file", "submit"],
    "forbidden_tools": ["list_schedules"]
  },
  "evaluation": {"scorer": "numeric_submit_tolerance", "tolerance": 0.5},
  "max_turns": 8,
  "suite": "original"
}`
	if err := os.WriteFile(filepath.Join(directory, "001_numeric.json"), []byte(caseJSON), 0o600); err != nil {
		t.Fatal(err)
	}
	// Python plugins are deliberately ignored rather than imported.
	if err := os.WriteFile(filepath.Join(directory, "cases.py"), []byte("raise RuntimeError('must not execute')\n"), 0o600); err != nil {
		t.Fatal(err)
	}

	cases, err := LoadPrimitiveCases(directory)
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != 1 {
		t.Fatalf("cases = %d, want 1", len(cases))
	}
	testCase := cases[0]
	if testCase.ID != "numeric_case" || testCase.Category != "Primitive Bench / original" {
		t.Fatalf("case metadata = %+v", testCase)
	}
	if testCase.Files["lines.txt"] != "alpha\nbeta\n" ||
		testCase.Files["noise.txt"] != "noise\nnoise\nnoise\n" {
		t.Fatalf("decoded files = %#v", testCase.Files)
	}
	if testCase.primitive == nil || testCase.primitive.scorer != "numeric_submit_tolerance" ||
		testCase.primitive.tolerance != 0.5 {
		t.Fatalf("Primitive runtime = %+v", testCase.primitive)
	}
	if testCase.Primitive == nil || testCase.Primitive.ExpectedSubmit == nil ||
		*testCase.Primitive.ExpectedSubmit != "42" || testCase.Primitive.Tolerance == nil {
		t.Fatalf("Primitive manifest metadata = %+v", testCase.Primitive)
	}
	if !strings.Contains(testCase.Source, "/"+filepath.Base(directory)+"/001_numeric.json") {
		t.Fatalf("source = %q", testCase.Source)
	}
}

func TestPrimitivePatchConfigToolsAndScoring(t *testing.T) {
	expected := "production"
	runtime := &primitiveRuntime{
		toolNames:      []string{"read_file", "write_file", "run_tests", "submit"},
		requiredTools:  []string{"read_file", "write_file", "run_tests", "submit"},
		expectedSubmit: &expected,
		scenario:       "patch_config",
		scorer:         "submit_after_tests",
	}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "app.conf"), []byte("mode = development\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	execution := newPrimitiveExecution(root, runtime)
	call := func(name, arguments string) {
		t.Helper()
		tool, err := execution.tool(name)
		if err != nil {
			t.Fatal(err)
		}
		if _, err := tool.Execute(context.Background(), json.RawMessage(arguments)); err != nil {
			t.Fatalf("%s: %v", name, err)
		}
	}
	call("read_file", `{"path":"app.conf"}`)
	call("write_file", `{"path":"app.conf","content":"mode = production\n"}`)
	call("run_tests", `{}`)
	call("submit", `{"answer":"production"}`)
	result := agent.Result{
		Output: "production",
		Steps: []agent.Step{
			{Tool: "read_file"},
			{Tool: "write_file"},
			{Tool: "run_tests"},
			{Tool: "submit"},
		},
	}
	if failures := primitiveFailures(runtime, execution, result); len(failures) != 0 {
		t.Fatalf("failures = %v", failures)
	}
}

func TestPrimitiveRunFileRequiresChmod(t *testing.T) {
	runtime := &primitiveRuntime{
		toolNames:  []string{"chmod", "run_file"},
		runOutputs: map[string]string{"hello.py": "READY"},
	}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "hello.py"), []byte("print('READY')\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	execution := newPrimitiveExecution(root, runtime)
	run, _ := execution.tool("run_file")
	if _, err := run.Execute(context.Background(), json.RawMessage(`{"path":"hello.py"}`)); err == nil ||
		!strings.Contains(err.Error(), "permission denied") {
		t.Fatalf("initial run error = %v", err)
	}
	chmod, _ := execution.tool("chmod")
	if _, err := chmod.Execute(context.Background(), json.RawMessage(`{"path":"hello.py","mode":"755"}`)); err != nil {
		t.Fatal(err)
	}
	output, err := run.Execute(context.Background(), json.RawMessage(`{"path":"hello.py"}`))
	if err != nil || output != "READY" {
		t.Fatalf("run output = %v, %v", output, err)
	}
}

func TestPrimitiveLuaSeesOnlyFixtureTable(t *testing.T) {
	if _, err := exec.LookPath("lua"); err != nil {
		t.Skip("Lua is not installed")
	}
	runtime := &primitiveRuntime{toolNames: []string{"run_lua"}}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "value.txt"), []byte("EMBER-91\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	execution := newPrimitiveExecution(root, runtime)
	tool, err := execution.tool("run_lua")
	if err != nil {
		t.Fatal(err)
	}
	output, err := tool.Execute(
		context.Background(),
		json.RawMessage(`{"code":"print(read_file('value.txt')); print(os == nil and io ~= nil and package == nil)"}`),
	)
	if err != nil {
		t.Fatal(err)
	}
	text, _ := output.(string)
	if !strings.Contains(text, "EMBER-91") || !strings.Contains(text, "true") {
		t.Fatalf("Lua output = %q", text)
	}
}

func TestPrimitiveArithmeticRunsThroughAgentEval(t *testing.T) {
	directory := t.TempDir()
	caseJSON := `{
  "name": "arithmetic",
  "title": "Arithmetic Tool Smoke Test",
  "mode": "benchmark",
  "system": "base",
  "prompt": "What's 4827 times 391? Call multiply, then reply with only the product digits.",
  "tools": "multiply",
  "environment": {"kind": "emulated", "files": {}},
  "evaluation": "arithmetic",
  "max_turns": 6,
  "suite": "original"
}`
	if err := os.WriteFile(filepath.Join(directory, "001_arithmetic.json"), []byte(caseJSON), 0o600); err != nil {
		t.Fatal(err)
	}
	cases, err := LoadPrimitiveCases(directory)
	if err != nil {
		t.Fatal(err)
	}
	responses := []continuation.Result{
		{Text: `<tool_call>{"name":"multiply","arguments":{"a":4827,"b":391}}</tool_call>`, FinishReason: continuation.FinishStop},
		{Text: "1887357", FinishReason: continuation.FinishStop},
	}
	index := 0
	report, err := Run(context.Background(), Config{
		Cases: cases,
		Suite: SuitePrimitive,
		Model: ModelMetadata{Identifier: "scripted", Completion: "test"},
		Runner: agent.Options{
			MaxSteps:                3,
			ProtocolRetries:         1,
			DecisionMaxOutputTokens: 64,
			Generation: continuation.Request{
				Model:           "scripted",
				MaxOutputTokens: 64,
			},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return continuation.GenerateFunc(func(
				context.Context,
				continuation.Request,
				continuation.EventSink,
			) (continuation.Result, error) {
				result := responses[index]
				index++
				return result, nil
			}), nil, nil
		},
		TempDir: t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if report.Summary.Metrics.TaskSuccess.Correct != 1 || index != 2 {
		t.Fatalf("Primitive arithmetic report = %+v, calls = %d", report.Summary, index)
	}
}

func TestPrimitiveSuiteUsesFullToolCallBudget(t *testing.T) {
	t.Parallel()

	cases, err := PrimitiveCases()
	if err != nil {
		t.Fatal(err)
	}
	selected, err := SelectCases(cases, []string{"arithmetic"})
	if err != nil {
		t.Fatal(err)
	}
	var requests []continuation.Request
	_, err = Run(context.Background(), Config{
		Cases: selected,
		Suite: SuitePrimitive,
		Model: ModelMetadata{Identifier: "scripted", Completion: "test"},
		Runner: agent.Options{
			MaxSteps:                3,
			DecisionMaxOutputTokens: 96,
			Generation: continuation.Request{
				Model:           "scripted",
				MaxOutputTokens: 1024,
			},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return continuation.GenerateFunc(func(
				_ context.Context,
				request continuation.Request,
				_ continuation.EventSink,
			) (continuation.Result, error) {
				requests = append(requests, request)
				if len(requests) == 1 {
					return continuation.Result{Text: `<tool_call>{"name":"multiply","arguments":{"a":4827,"b":391}}</tool_call>`}, nil
				}
				return continuation.Result{Text: "1887357"}, nil
			}), nil, nil
		},
		TempDir: t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(requests) != 2 || requests[0].MaxOutputTokens != 1024 {
		t.Fatalf("Primitive request budgets = %+v", requests)
	}
}

func TestPrimitiveSuiteUsesCaseMaxTurns(t *testing.T) {
	t.Parallel()

	cases, err := PrimitiveCases()
	if err != nil {
		t.Fatal(err)
	}
	selected, err := SelectCases(cases, []string{"find_read_submit"})
	if err != nil {
		t.Fatal(err)
	}
	responses := []string{
		`<tool_call>{"name":"list_files","arguments":{"path":"."}}</tool_call>`,
		`<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
		`<tool_call>{"name":"read_file","arguments":{"path":"src/answer.txt"}}</tool_call>`,
		`<tool_call>{"name":"submit","arguments":{"answer":"BLUEBIRD"}}</tool_call>`,
	}
	index := 0
	report, err := Run(context.Background(), Config{
		Cases: selected,
		Suite: SuitePrimitive,
		Model: ModelMetadata{Identifier: "scripted", Completion: "test"},
		Runner: agent.Options{
			// The imported case permits ten turns. A generic two-step fallback
			// would stop before submit if the case budget were not applied.
			MaxSteps: 2,
			Generation: continuation.Request{
				Model:           "scripted",
				MaxOutputTokens: 128,
			},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return continuation.GenerateFunc(func(
				context.Context,
				continuation.Request,
				continuation.EventSink,
			) (continuation.Result, error) {
				if index >= len(responses) {
					return continuation.Result{}, errors.New("unexpected model call")
				}
				response := responses[index]
				index++
				return continuation.Result{Text: response, FinishReason: continuation.FinishStop}, nil
			}), nil, nil
		},
		TempDir: t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if report.Summary.Metrics.TaskSuccess.Correct != 1 || index != len(responses) {
		t.Fatalf("Primitive max_turns report = %+v, calls = %d", report.Summary, index)
	}
	if report.Manifest.Harness.MaxSteps != 10 {
		t.Fatalf("manifest max steps = %d, want 10", report.Manifest.Harness.MaxSteps)
	}
	if report.Manifest.Harness.Protocol != agent.G1IFunctionProtocolV1 ||
		report.Manifest.Harness.Renderer != agent.G1IFunctionRendererV1 ||
		!report.Manifest.Harness.EndOnTerminalTool ||
		report.Manifest.Harness.ToolProfile != PrimitiveProfileUpstream {
		t.Fatalf("Primitive native G1i harness = %+v", report.Manifest.Harness)
	}
}

func TestLoadPrimitiveCasesExternalOrig30(t *testing.T) {
	directory := os.Getenv("RWKV_PRIMITIVE_CASES")
	if directory == "" {
		t.Skip("RWKV_PRIMITIVE_CASES is not set")
	}
	cases, err := LoadPrimitiveCases(directory)
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != 30 {
		t.Fatalf("external Primitive Bench cases = %d, want 30", len(cases))
	}
	for _, testCase := range cases {
		if testCase.primitive == nil {
			t.Fatalf("case %q has no Primitive runtime", testCase.ID)
		}
		expect := testCase.Turns[0].Expect
		if len(testCase.primitive.toolNames) > 0 && expect.Tools != nil && len(expect.Tools) == 0 {
			t.Fatalf("tool-using case %q was converted to a no-tool expectation", testCase.ID)
		}
	}
}

func TestPrimitiveCasesEmbeddedSnapshot(t *testing.T) {
	t.Parallel()

	cases, err := PrimitiveCases()
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != primitiveOrig30Count {
		t.Fatalf("embedded Primitive Bench cases = %d, want %d", len(cases), primitiveOrig30Count)
	}
	if cases[0].ID != "arithmetic" || cases[len(cases)-1].ID != "markdown_release_notes" {
		t.Fatalf("embedded Primitive Bench bounds = %q ... %q", cases[0].ID, cases[len(cases)-1].ID)
	}
	for _, testCase := range cases {
		if testCase.primitive == nil || testCase.Primitive == nil {
			t.Fatalf("embedded case %q has no Primitive metadata", testCase.ID)
		}
		if !strings.Contains(testCase.Source, "416b073d2c5442ae34bfbf8a3b84ed414b5b85ff/agent_cases_orig30/") {
			t.Fatalf("embedded case %q source = %q", testCase.ID, testCase.Source)
		}
	}
	canonical, err := BuiltinSuite(SuitePrimitiveOrig30)
	if err != nil {
		t.Fatal(err)
	}
	legacy, err := BuiltinSuite(SuitePrimitive)
	if err != nil {
		t.Fatal(err)
	}
	if len(canonical) != primitiveOrig30Count || len(legacy) != primitiveOrig30Count ||
		CanonicalBuiltinSuiteName(SuitePrimitive) != SuitePrimitiveOrig30 {
		t.Fatalf(
			"Primitive orig30 suite routing = canonical:%d legacy:%d alias:%q",
			len(canonical),
			len(legacy),
			CanonicalBuiltinSuiteName(SuitePrimitive),
		)
	}
}

func TestPrimitiveFeedback30CasesEmbeddedSnapshot(t *testing.T) {
	t.Parallel()

	wantIDs := []string{
		"lts_eol_status",
		"repo_path_precise",
		"false_premise",
		"calc_readback_verify",
		"install_command_literal",
		"id_cross_table_bind",
		"commit_author_date_bind",
		"meeting_room_conflict",
		"branch_pr_author_bind",
		"top_n_with_tiebreak",
		"running_balance_last",
		"weighted_vote_winner",
		"csv_null_skip_avg",
		"unique_pair_count",
		"ratio_safe_divide",
		"csv_schema_mismatch_cols",
		"policy_refund_exceeds_cap",
		"policy_vip_override",
		"checksum_mismatch_flag",
		"insufficient_evidence",
		"boolean_expr_eval",
		"set_difference_report",
		"nginx_upstream_count",
		"dockerfile_user_name",
		"openapi_path_method",
		"env_subst_literal",
		"cidr_host_capacity",
		"url_query_param",
		"snake_to_camel",
		"round_half_up",
	}
	cases, err := PrimitiveFeedback30Cases()
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != primitiveFeedback30Count {
		t.Fatalf("embedded Primitive feedback case count = %d, want %d", len(cases), primitiveFeedback30Count)
	}
	gotIDs := make([]string, len(cases))
	for index, testCase := range cases {
		gotIDs[index] = testCase.ID
		if testCase.primitive == nil || testCase.Primitive == nil {
			t.Fatalf("embedded feedback case %q has no Primitive metadata", testCase.ID)
		}
		if !strings.Contains(testCase.Source, "416b073d2c5442ae34bfbf8a3b84ed414b5b85ff/agent_cases_feedback/") {
			t.Fatalf("embedded feedback case %q source = %q", testCase.ID, testCase.Source)
		}
		if !slices.Equal(testCase.primitive.toolNames, primitiveToolSets["nav"]) {
			t.Fatalf("embedded feedback case %q tools = %v", testCase.ID, testCase.primitive.toolNames)
		}
		if testCase.primitive.scorer != "submit" || testCase.primitive.expectedSubmit == nil {
			t.Fatalf("embedded feedback case %q runtime = %+v", testCase.ID, testCase.primitive)
		}
		if !slices.Equal(testCase.Turns[0].Expect.RequiredTools, []string{"submit"}) {
			t.Fatalf("embedded feedback case %q required tools = %v", testCase.ID, testCase.Turns[0].Expect.RequiredTools)
		}
		if testCase.ID == "weighted_vote_winner" {
			const wantVotes = "candidate,weight\nOak,2\nPine,5\nOak,5\nMaple,6\nPine,1\n"
			if testCase.Files["votes.csv"] != wantVotes || *testCase.primitive.expectedSubmit != "Oak" {
				t.Fatalf(
					"weighted vote correction = votes:%q expected:%q",
					testCase.Files["votes.csv"],
					*testCase.primitive.expectedSubmit,
				)
			}
		}
	}
	if !slices.Equal(gotIDs, wantIDs) {
		t.Fatalf("embedded Primitive feedback IDs = %v, want %v", gotIDs, wantIDs)
	}
	builtin, err := BuiltinSuite(SuitePrimitiveFeedback30)
	if err != nil {
		t.Fatal(err)
	}
	if len(builtin) != primitiveFeedback30Count || !IsPrimitiveSuite(SuitePrimitiveFeedback30) {
		t.Fatalf("Primitive feedback suite routing = %d cases, primitive=%t", len(builtin), IsPrimitiveSuite(SuitePrimitiveFeedback30))
	}
}

func TestPrimitiveToolContractsMatchUpstreamSnapshot(t *testing.T) {
	t.Parallel()

	want := map[string]struct {
		properties []string
		required   []string
	}{
		"multiply":       {properties: []string{"a", "b"}, required: []string{"a", "b"}},
		"list_files":     {properties: []string{"path"}, required: []string{"path"}},
		"ls":             {properties: []string{"path"}, required: []string{"path"}},
		"stat":           {properties: []string{"path"}, required: []string{"path"}},
		"read_file":      {properties: []string{"path"}, required: []string{"path"}},
		"write_file":     {properties: []string{"content", "path"}, required: []string{"content", "path"}},
		"chmod":          {properties: []string{"mode", "path"}, required: []string{"mode", "path"}},
		"run_file":       {properties: []string{"path"}, required: []string{"path"}},
		"run_awk":        {properties: []string{"input_path", "script_path"}, required: []string{"input_path", "script_path"}},
		"run_lua":        {properties: []string{"code"}, required: []string{"code"}},
		"search":         {properties: []string{"query"}, required: []string{"query"}},
		"run_tests":      {},
		"submit":         {properties: []string{"answer"}, required: []string{"answer"}},
		"list_schedules": {properties: []string{"state"}},
	}
	names := make([]string, 0, len(want))
	for name := range want {
		names = append(names, name)
	}
	sort.Strings(names)
	runtime := &primitiveRuntime{toolNames: names}
	execution := newPrimitiveExecution(t.TempDir(), runtime)
	tools, err := execution.tools()
	if err != nil {
		t.Fatal(err)
	}
	if len(tools) != len(want) {
		t.Fatalf("Primitive tool count = %d, want %d", len(tools), len(want))
	}
	for _, tool := range tools {
		spec := tool.Spec()
		contract := want[spec.Name]
		var schema struct {
			Properties           map[string]json.RawMessage `json:"properties"`
			Required             []string                   `json:"required"`
			AdditionalProperties bool                       `json:"additionalProperties"`
		}
		if err := json.Unmarshal(spec.Parameters, &schema); err != nil {
			t.Fatalf("%s parameters: %v", spec.Name, err)
		}
		if schema.AdditionalProperties {
			t.Fatalf("%s allows additional properties", spec.Name)
		}
		properties := make([]string, 0, len(schema.Properties))
		for name := range schema.Properties {
			properties = append(properties, name)
		}
		sort.Strings(properties)
		sort.Strings(schema.Required)
		if !slices.Equal(properties, contract.properties) {
			t.Fatalf("%s properties = %v, want %v", spec.Name, properties, contract.properties)
		}
		if !slices.Equal(schema.Required, contract.required) {
			t.Fatalf("%s required = %v, want %v", spec.Name, schema.Required, contract.required)
		}
	}
}

func TestPrimitiveGoNativeProfileReplacesLuaWithCoreTools(t *testing.T) {
	t.Parallel()

	runtime := &primitiveRuntime{toolNames: []string{
		"list_files", "read_file", "run_lua", "submit",
	}}
	testCase := Case{
		Primitive: &PrimitiveMetadata{ToolNames: append([]string(nil), runtime.toolNames...)},
		primitive: runtime,
	}
	tools, execution, err := evalTools(Config{
		Suite:            SuitePrimitive,
		PrimitiveProfile: PrimitiveProfileGoNative,
	}, t.TempDir(), testCase)
	if err != nil {
		t.Fatal(err)
	}
	if execution == nil {
		t.Fatal("Go-native Primitive profile did not preserve scoring execution")
	}
	names := make(map[string]bool, len(tools))
	for _, tool := range tools {
		names[tool.Spec().Name] = true
	}
	for _, required := range []string{"list_files", "read_file", "submit", "calculator", "data_query"} {
		if !names[required] {
			t.Errorf("Go-native Primitive profile is missing %q: %v", required, names)
		}
	}
	if names["run_lua"] {
		t.Errorf("Go-native Primitive profile still exposes run_lua: %v", names)
	}
}

func TestPrimitiveGoNativeWriteAndTestsReportWorkspaceProgress(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	original := "from datetime import datetime\n\n\ndef parse_date(text):\n    return datetime.strptime(text, \"%Y-%m-%d\").date().isoformat()\n"
	if err := os.WriteFile(filepath.Join(root, "parser.py"), []byte(original), 0o600); err != nil {
		t.Fatal(err)
	}
	execution := newPrimitiveExecution(root, &primitiveRuntime{scenario: "date_parser_patch"})
	execution.goNative = true

	unchanged, err := execution.writeFile(context.Background(), json.RawMessage(`{
		"path":"parser.py",
		"content":"from datetime import datetime\n\n\ndef parse_date(text):\n    return datetime.strptime(text, \"%Y-%m-%d\").date().isoformat()\n"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	unchangedJSON, _ := json.Marshal(unchanged)
	if !bytes.Contains(unchangedJSON, []byte(`"changed":false`)) ||
		!bytes.Contains(unchangedJSON, []byte(`"revision":"r0"`)) {
		t.Fatalf("unchanged write = %s", unchangedJSON)
	}
	firstTest, err := execution.runTests(context.Background(), json.RawMessage(`{}`))
	if err != nil {
		t.Fatal(err)
	}
	firstJSON, _ := json.Marshal(firstTest)
	if !bytes.Contains(firstJSON, []byte(`"status":"FAIL"`)) ||
		!bytes.Contains(firstJSON, []byte(`"last_write_changed":false`)) {
		t.Fatalf("first test = %s", firstJSON)
	}

	changed, err := execution.writeFile(context.Background(), json.RawMessage(`{
		"path":"parser.py",
		"content":"from datetime import datetime\n\n\ndef parse_date(text):\n    return datetime.strptime(text.strip().replace('/', '-'), \"%Y-%m-%d\").date().isoformat()\n"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	changedJSON, _ := json.Marshal(changed)
	if !bytes.Contains(changedJSON, []byte(`"changed":true`)) ||
		!bytes.Contains(changedJSON, []byte(`"revision":"r1"`)) {
		t.Fatalf("changed write = %s", changedJSON)
	}
	secondTest, err := execution.runTests(context.Background(), json.RawMessage(`{}`))
	if err != nil {
		t.Fatal(err)
	}
	secondJSON, _ := json.Marshal(secondTest)
	if !bytes.Contains(secondJSON, []byte(`"status":"PASS"`)) ||
		!bytes.Contains(secondJSON, []byte(`"changed_since_previous_test":true`)) {
		t.Fatalf("second test = %s", secondJSON)
	}
}
