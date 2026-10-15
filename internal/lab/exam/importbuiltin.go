package exam

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// The built-in suites live in Go code and JSON next to the harness. The exam
// needs them as ordinary case.json files so they share one loader, one
// manifest and one tag scheme. This exporter is the only writer of
// bench/exam/imported/: edit the generator here, never the output.
//
// Two changes are made on the way out, both because the exam scores what an
// App user would accept rather than one prescribed tool path:
//   - route and required_calls are dropped (they pinned exact arguments, so a
//     model that solved the task with bash, or with read_file instead of
//     search_text, failed);
//   - required_tools are dropped except where calling a tool is the lesson
//     (the bfcl "supplied information" and state cases keep read_file).
// No-call contracts (tools: [] and require_active_no_call) are kept verbatim.

type importTags struct {
	Scenario     string
	TaskType     string
	Traps        []string
	Difficulties []string // exam_difficulties override, nil = derive
}

func bfclTags(c eval.Case) importTags {
	switch {
	case strings.HasPrefix(c.ID, "bfcl_irrelevance_"):
		return importTags{Scenario: "notool", TaskType: "concept"}
	case strings.HasPrefix(c.ID, "bfcl_missing_"):
		return importTags{Scenario: "notool", TaskType: "ambiguous_request", Traps: []string{"TR-AMBIG"}}
	case strings.HasPrefix(c.ID, "bfcl_supplied_"):
		return importTags{Scenario: "filesystem", TaskType: "find_file"}
	case strings.HasPrefix(c.ID, "bfcl_state_"):
		return importTags{Scenario: "hybrid", TaskType: "multi_turn"}
	case strings.HasPrefix(c.ID, "bfcl_recovery_"):
		return importTags{Scenario: "hybrid", TaskType: "multi_turn", Traps: []string{"TR-NEARNAME"}}
	}
	return importTags{Scenario: "notool", TaskType: "concept"}
}

var boundaryTagMap = map[string]importTags{
	"pb_find_read_submit":          {Scenario: "filesystem", TaskType: "find_file"},
	"pb_search_read_submit":        {Scenario: "filesystem", TaskType: "find_file"},
	"pb_csv_sum":                   {Scenario: "tabular", TaskType: "aggregate"},
	"pb_json_extract":              {Scenario: "config", TaskType: "read_effective"},
	"pb_multi_file_compare":        {Scenario: "docs", TaskType: "extract_items", Traps: []string{"TR-MULTISRC"}},
	"pb_avoid_forbidden_tool":      {Scenario: "filesystem", TaskType: "find_file", Traps: []string{"TR-EARLYHIT"}},
	"pb_read_only_repo_explain":    {Scenario: "code", TaskType: "explain_readonly", Traps: []string{"TR-READONLY"}},
	"pb_missing_file_recover":      {Scenario: "filesystem", TaskType: "find_file", Traps: []string{"TR-NEARNAME"}},
	"pb_long_context_small_need":   {Scenario: "filesystem", TaskType: "find_file", Traps: []string{"TR-LONG"}},
	"pb_loc_interest_8_months":     {Scenario: "tabular", TaskType: "policy_calc"},
	"pb_eur_trip_card_vs_fx":       {Scenario: "tabular", TaskType: "policy_calc", Traps: []string{"TR-DIRMAP"}},
	"pb_fx_column_trap":            {Scenario: "tabular", TaskType: "reconcile", Traps: []string{"TR-DIRMAP", "TR-DECOY"}},
	"pb_log_incident_root_cause":   {Scenario: "logs", TaskType: "root_cause", Traps: []string{"TR-MULTISRC"}},
	"pb_config_precedence_resolve": {Scenario: "config", TaskType: "precedence", Traps: []string{"TR-PRECEDENCE"}},
	"pb_jsonl_event_aggregate":     {Scenario: "logs", TaskType: "aggregate_jsonl"},
	"pb_csv_reconcile_returns":     {Scenario: "tabular", TaskType: "reconcile", Traps: []string{"TR-SIGN"}},
	"pb_prompt_injection_in_file":  {Scenario: "docs", TaskType: "policy_lookup", Traps: []string{"TR-INJECT"}},
	"pb_markdown_release_notes":    {Scenario: "docs", TaskType: "latest_version", Traps: []string{"TR-SUPERSEDE"}},
}

func relaxExpect(e eval.Expectation, keepRequired bool) eval.Expectation {
	// Same scoring rules as the 2026-10-15 rewrite of the authored banks
	// (docs/evaluations/bench-composition-20261015/naturalize.py): the answer
	// is prose, so values are found inside it.
	if e.ExpectedNumber != nil {
		e.ExpectedNumberInText = true
	}
	if e.OutputEquals != nil {
		e.OutputContains = append(e.OutputContains, *e.OutputEquals)
		e.OutputContainsToken = true
		e.OutputEquals = nil
	}
	if len(e.OutputEqualsAny) > 0 {
		e.OutputContainsAny = e.OutputEqualsAny
		e.OutputContainsAnyToken = true
		e.OutputEqualsAny = nil
	}
	e.MaxOutputChars = 0
	e.Route = ""
	e.RequiredCalls = nil
	e.ForbidRouteFallback = false
	if !keepRequired {
		e.RequiredTools = nil
	}
	return e
}

func exportCase(c eval.Case, suite, author string, tags importTags, keepRequired bool) eval.Case {
	out := c
	out.Turns = make([]eval.Turn, len(c.Turns))
	for i, turn := range c.Turns {
		out.Turns[i] = eval.Turn{Prompt: turn.Prompt, Expect: relaxExpect(turn.Expect, keepRequired)}
	}
	traps := tags.Traps
	if traps == nil {
		traps = []string{}
	}
	out.Tags = map[string]any{
		"scenario":      tags.Scenario,
		"task_type":     tags.TaskType,
		"traps":         traps,
		"level":         "L0",
		"status":        "draft",
		"version":       1,
		"author":        author,
		"import_suite":  suite,
		"import_source": c.Source,
		"answer_style":  "natural",
	}
	if tags.Difficulties != nil {
		out.Tags["exam_difficulties"] = tags.Difficulties
	}
	return out
}

func writeImported(root, suite string, cases []eval.Case) error {
	dir := filepath.Join(root, "bench", "exam", "imported", suite)
	if err := os.RemoveAll(dir); err != nil {
		return err
	}
	for _, c := range cases {
		data, err := json.MarshalIndent(c, "", "  ")
		if err != nil {
			return err
		}
		caseDir := filepath.Join(dir, c.ID)
		if err := os.MkdirAll(caseDir, 0o755); err != nil {
			return err
		}
		if err := os.WriteFile(filepath.Join(caseDir, "case.json"), append(data, '\n'), 0o644); err != nil {
			return err
		}
		// Round-trip through the bank loader so an export the loader would
		// reject never lands on disk silently.
		if _, err := eval.LoadCaseFile(filepath.Join(caseDir, "case.json")); err != nil {
			return err
		}
	}
	readme := "# " + suite + "（导出件，勿手改）\n\n由 `rwkv-lab exam import-builtin` 从内置题集生成。" +
		"改题请改生成器 `internal/lab/exam/importbuiltin.go` 或内置题源，再重新导出。\n"
	return os.WriteFile(filepath.Join(dir, "README.md"), []byte(readme), 0o644)
}

func runImportBuiltin(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam import-builtin", flag.ContinueOnError)
	if err := flags.Parse(args); err != nil {
		return 2
	}
	root := DefaultPaths().Root
	bfcl, err := eval.BFCLProductCases()
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam import-builtin:", err)
		return 1
	}
	var bfclOut []eval.Case
	for _, c := range bfcl {
		keep := strings.HasPrefix(c.ID, "bfcl_supplied_") || strings.HasPrefix(c.ID, "bfcl_state_") ||
			strings.HasPrefix(c.ID, "bfcl_recovery_")
		bfclOut = append(bfclOut, exportCase(c, "bfcl-product", "import:bfcl-v4", bfclTags(c), keep))
	}
	boundary, err := eval.BoundaryCases()
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam import-builtin:", err)
		return 1
	}
	var boundaryOut []eval.Case
	for _, c := range boundary {
		tags, ok := boundaryTagMap[c.ID]
		if !ok {
			fmt.Fprintf(os.Stderr, "rwkv-lab exam import-builtin: boundary case %q has no tag mapping\n", c.ID)
			return 1
		}
		boundaryOut = append(boundaryOut, exportCase(c, "boundary", "import:primitive-bench", tags, false))
	}
	for suite, cases := range map[string][]eval.Case{"bfcl-product": bfclOut, "boundary": boundaryOut} {
		if err := writeImported(root, suite, cases); err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam import-builtin:", err)
			return 1
		}
		fmt.Printf("exported %d %s case(s)\n", len(cases), suite)
	}
	return 0
}
