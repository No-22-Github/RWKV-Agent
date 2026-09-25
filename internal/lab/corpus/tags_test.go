package corpus

import (
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

func strptr(s string) *string { return &s }

// §4.4.2: nine rules, first match wins. Each case turns on exactly one rule
// and the rows below it, so a reordering shows up as a wrong kind.
func TestDeriveKindFollowsTheFirstMatchingRule(t *testing.T) {
	cases := []struct {
		name      string
		tags      eval.CaseTags
		traj      eval.TrajStats
		turn      int
		runExpect bool
		want      string
	}{
		{
			name: "smalltalk wins over everything",
			tags: eval.CaseTags{Scenario: "notool", TaskType: "smalltalk", Traps: []string{"TR-NOCAP"}},
			traj: eval.TrajStats{ZeroCall: true, Writes: true},
			turn: 1, want: "smalltalk",
		},
		{
			name: "capability refusal",
			tags: eval.CaseTags{Scenario: "notool", TaskType: "beyond_capability", Traps: []string{}},
			traj: eval.TrajStats{ZeroCall: true},
			turn: 1, want: "refuse",
		},
		{
			name: "TR-NOCAP refusal outside notool",
			tags: eval.CaseTags{Scenario: "config", TaskType: "edit_value", Traps: []string{"TR-NOCAP"}},
			traj: eval.TrajStats{ZeroCall: true},
			turn: 1, want: "refuse",
		},
		{
			name: "clarifying first turn",
			tags: eval.CaseTags{Scenario: "hybrid", TaskType: "multi_turn", Traps: []string{"TR-AMBIG"}},
			traj: eval.TrajStats{ZeroCall: true, TurnsTotal: 2},
			turn: 1, want: "clarify",
		},
		{
			name: "a TR-AMBIG answer on the last turn is a normal row",
			tags: eval.CaseTags{Scenario: "hybrid", TaskType: "multi_turn", Traps: []string{"TR-AMBIG"}},
			traj: eval.TrajStats{ZeroCall: true, TurnsTotal: 2},
			turn: 2, want: "direct",
		},
		{
			name: "zero call direct answer",
			tags: eval.CaseTags{Scenario: "notool", TaskType: "concept"},
			traj: eval.TrajStats{ZeroCall: true},
			turn: 1, want: "direct",
		},
		{
			name: "script scenario",
			tags: eval.CaseTags{Scenario: "script", TaskType: "write_new"},
			traj: eval.TrajStats{ToolCalls: 3, Local: true},
			turn: 1, want: "script",
		},
		{
			name: "expect.run makes any scenario a script row",
			tags: eval.CaseTags{Scenario: "docs", TaskType: "write_structured"},
			traj: eval.TrajStats{ToolCalls: 2, Writes: true},
			turn: 1, runExpect: true, want: "script",
		},
		{
			name: "writes beat web and local",
			tags: eval.CaseTags{Scenario: "hybrid", TaskType: "web_then_edit"},
			traj: eval.TrajStats{ToolCalls: 3, Web: true, Local: true, Writes: true},
			turn: 1, want: "write",
		},
		{
			name: "web and local evidence",
			tags: eval.CaseTags{Scenario: "hybrid", TaskType: "web_then_calc"},
			traj: eval.TrajStats{ToolCalls: 3, Web: true, Local: true},
			turn: 1, want: "web_local",
		},
		{
			name: "web only",
			tags: eval.CaseTags{Scenario: "web", TaskType: "lookup_value"},
			traj: eval.TrajStats{ToolCalls: 2, Web: true},
			turn: 1, want: "web",
		},
		{
			name: "local only, calculator included",
			tags: eval.CaseTags{Scenario: "tabular", TaskType: "aggregate"},
			traj: eval.TrajStats{ToolCalls: 1, Local: false},
			turn: 1, want: "local",
		},
	}
	for _, item := range cases {
		t.Run(item.name, func(t *testing.T) {
			if got := DeriveKind(item.tags, item.traj, item.turn, item.runExpect); got != item.want {
				t.Errorf("kind = %q, want %q", got, item.want)
			}
		})
	}
}

// §4.4.1: final_kind has five values and the case's expectation decides
// between "value" and "text".
func TestFinalKindCoversEveryValue(t *testing.T) {
	numberExpect := lab.NewOrderedMap()
	numberExpect.Set("expected_number", 5)
	textExpect := lab.NewOrderedMap()
	textExpect.Set("output_contains_any", []any{"hello"})

	cases := []struct {
		name       string
		last       string
		lastIsCall bool
		expect     *lab.OrderedMap
		want       string
	}{
		{"unknown", "UNKNOWN", false, numberExpect, "unknown"},
		{"done", "DONE\n", false, textExpect, "done"},
		{"value", "5", false, numberExpect, "value"},
		{"text", "Hello there", false, textExpect, "text"},
		{"none for an intermediate turn", "<tool_call>{\"name\":\"read_file\"}</tool_call>", true, textExpect, "none"},
	}
	for _, item := range cases {
		t.Run(item.name, func(t *testing.T) {
			if got := finalKind(item.last, item.lastIsCall, item.expect); got != item.want {
				t.Errorf("final_kind = %q, want %q", got, item.want)
			}
		})
	}
}

// Only supervised outputs count as this turn's actions; a recovery prefix is
// replayed but never trained, so it must not turn a direct answer into a tool
// trajectory.
func TestBuildTrajCountsSupervisedOutputsOnly(t *testing.T) {
	outputs := []eval.ScriptOutput{
		{Text: `<tool_call>{"name":"web_search","arguments":{}}</tool_call>`, Supervised: false},
		{Text: `<tool_call>{"name":"read_file","arguments":{}}</tool_call>`, Supervised: true},
		{Text: `<tool_call>{"name":"write_file","arguments":{}}</tool_call>`, Supervised: true},
		{Text: "DONE", Supervised: true},
	}
	expect := lab.NewOrderedMap()
	traj := BuildTraj(outputs, 0, len(outputs), 1, 1, 2500, expect)
	if traj.ToolCalls != 2 {
		t.Errorf("tool_calls = %d, want 2", traj.ToolCalls)
	}
	if len(traj.ToolSeq) != 2 || traj.ToolSeq[0] != "read_file" || traj.ToolSeq[1] != "write_file" {
		t.Errorf("tool_seq = %v, want [read_file write_file]", traj.ToolSeq)
	}
	if traj.Web {
		t.Error("web = true, but the only web call was unsupervised")
	}
	if !traj.Local || !traj.Writes {
		t.Errorf("local = %v, writes = %v, want both true", traj.Local, traj.Writes)
	}
	if traj.UnsupervisedOutputs != 1 {
		t.Errorf("unsupervised_outputs = %d, want 1", traj.UnsupervisedOutputs)
	}
	if traj.ZeroCall {
		t.Error("zero_call = true, want false")
	}
	if traj.FinalKind != "done" {
		t.Errorf("final_kind = %q, want done", traj.FinalKind)
	}
	if traj.Tokens != 2500 || traj.TurnsTotal != 1 {
		t.Errorf("tokens = %d, turns_total = %d, want 2500 and 1", traj.Tokens, traj.TurnsTotal)
	}
}

func TestBuildTrajDirectAnswerNeedsNoTool(t *testing.T) {
	outputs := []eval.ScriptOutput{{Text: "Hi!", Supervised: true}}
	traj := BuildTraj(outputs, 0, 1, 1, 1, 1200, nil)
	if !traj.ZeroCall || traj.ToolCalls != 0 {
		t.Errorf("zero_call = %v, tool_calls = %d, want true and 0", traj.ZeroCall, traj.ToolCalls)
	}
	if traj.Local || traj.Web || traj.Writes {
		t.Errorf("a direct answer moved a tool axis: %+v", traj)
	}
}

func TestScriptToolNameReadsTheCalledTool(t *testing.T) {
	cases := []struct {
		text   string
		name   string
		isCall bool
	}{
		{`<tool_call>{"name":"read_file","arguments":{"path":"a.txt"}}</tool_call>`, "read_file", true},
		{`<tool_call>{"name":"web_search","arguments":{}}`, "web_search", true},
		{"Final answer.", "", false},
		{"UNKNOWN", "", false},
	}
	for _, item := range cases {
		name, isCall := scriptToolName(item.text)
		if name != item.name || isCall != item.isCall {
			t.Errorf("scriptToolName(%q) = %q, %v; want %q, %v", item.text, name, isCall, item.name, item.isCall)
		}
	}
}

// The tag map is reviewed data: the tests pin the two properties the spec
// checks (39 overrides) and the drift guards (an unmapped label is an error).
func TestTagMapCoversTheReviewedOverrides(t *testing.T) {
	tagMap, err := LoadTagMap(DefaultTagMap())
	if err != nil {
		t.Fatal(err)
	}
	if got := len(tagMap.OverrideIDs()); got != 39 {
		t.Errorf("tag-map overrides = %d, want 39", got)
	}
}

func TestTagMapREfusesUnmappedBehaviorTag(t *testing.T) {
	tagMap, err := LoadTagMap(DefaultTagMap())
	if err != nil {
		t.Fatal(err)
	}
	vocab, err := LoadVocab(DefaultVocab())
	if err != nil {
		t.Fatal(err)
	}
	record := recordObject("ws7-fs-0001-a00", "filesystem", []any{"find_file", "brand_new_label"}, "fs-0001")
	if _, err := tagMap.NormalizeRecord(record, vocab); err == nil {
		t.Fatal("NormalizeRecord accepted a behavior tag the tag map does not define")
	}
}

// A record whose task type cannot be derived and has no override must fail:
// an empty task_type would silently corrupt every downstream group-by.
func TestNormalizeRecordRefusesUnresolvableTaskType(t *testing.T) {
	tagMap, err := LoadTagMap(DefaultTagMap())
	if err != nil {
		t.Fatal(err)
	}
	vocab, err := LoadVocab(DefaultVocab())
	if err != nil {
		t.Fatal(err)
	}
	record := recordObject("ws7-log-9999-b10", "logs", []any{"filter_count"}, "log-9999")
	if _, err := tagMap.NormalizeRecord(record, vocab); err == nil {
		t.Fatal("NormalizeRecord accepted a record with no legal task type and no override")
	}
}

// The reviewed overrides resolve exactly the records the automatic rule
// cannot: one legal label passes through, several or none need the map.
func TestNormalizeRecordUsesLegalLabelOrOverride(t *testing.T) {
	tagMap, err := LoadTagMap(DefaultTagMap())
	if err != nil {
		t.Fatal(err)
	}
	vocab, err := LoadVocab(DefaultVocab())
	if err != nil {
		t.Fatal(err)
	}
	auto := recordObject("ws7-cfg-0001-a00", "config", []any{"read_effective", "pure_value"}, "cfg-0001")
	tags, err := tagMap.NormalizeRecord(auto, vocab)
	if err != nil {
		t.Fatal(err)
	}
	if tags.TaskType != "read_effective" {
		t.Errorf("task_type = %q, want read_effective", tags.TaskType)
	}
	if len(tags.Behaviors) != 0 {
		t.Errorf("behaviors = %v, want none: pure_value is a default answer shape", tags.Behaviors)
	}
	if tags.Origin == nil || tags.Origin.ParentSeedID != "cfg-0001" {
		t.Errorf("origin = %+v, want the raw labels kept", tags.Origin)
	}

	overridden := recordObject("ws7-fs-0002-x10", "filesystem", []any{"aggregate", "count_discipline"}, "fs-0002")
	tags, err = tagMap.NormalizeRecord(overridden, vocab)
	if err != nil {
		t.Fatal(err)
	}
	if tags.TaskType != "count_by_type" {
		t.Errorf("task_type = %q, want the tag map's count_by_type", tags.TaskType)
	}
}

// A rendered case carries its labels back to `corpus rows` unchanged.
func TestCaseTagsRoundTripThroughTheRenderedCase(t *testing.T) {
	origin := &eval.TagOrigin{ParentSeedID: "cfg-0001", Branch: "anchor", Split: "train",
		BehaviorTags: []string{"read_effective", "multi_hop"}}
	want := eval.CaseTags{Scenario: "config", TaskType: "read_effective",
		Traps: []string{}, Level: strptr("L1"), Family: "grp-cfg-0001-anchor",
		Behaviors: []string{"multi_hop"}, Origin: origin}
	caseObj := lab.NewOrderedMap()
	caseObj.Set("tags", CaseTagsValue(want, true))

	got, seeded := TagsFromCase(caseObj)
	if !seeded {
		t.Error("seeded_from_test = false, want true")
	}
	if got.Scenario != want.Scenario || got.TaskType != want.TaskType || got.Family != want.Family {
		t.Errorf("tags = %+v, want %+v", got, want)
	}
	if got.Level == nil || *got.Level != "L1" {
		t.Errorf("level = %v, want L1", got.Level)
	}
	if len(got.Behaviors) != 1 || got.Behaviors[0] != "multi_hop" {
		t.Errorf("behaviors = %v, want [multi_hop]", got.Behaviors)
	}
	if got.Origin == nil || got.Origin.ParentSeedID != "cfg-0001" || len(got.Origin.BehaviorTags) != 2 {
		t.Errorf("origin = %+v, want the raw labels kept", got.Origin)
	}
}

// A distilled case has no records behind it: no origin, no behaviors, and it
// is never marked as seeded from a test-bank case.
func TestTagsFromCaseWithoutOrigin(t *testing.T) {
	caseObj := lab.NewOrderedMap()
	tags := lab.NewOrderedMap()
	tags.Set("scenario", "notool")
	tags.Set("task_type", "smalltalk")
	tags.Set("traps", []any{"TR-NOTOOLNEED"})
	tags.Set("level", "L1")
	tags.Set("family", "fam-nt-smalltalk-01")
	caseObj.Set("tags", tags)

	got, seeded := TagsFromCase(caseObj)
	if seeded {
		t.Error("seeded_from_test = true for a distilled case")
	}
	if got.TaskType != "smalltalk" || got.Origin != nil {
		t.Errorf("tags = %+v, want no origin", got)
	}
	if len(got.Traps) != 1 || got.Traps[0] != "TR-NOTOOLNEED" {
		t.Errorf("traps = %v, want [TR-NOTOOLNEED]", got.Traps)
	}
}

// §4.4.1 negative test: --source has no default, so render cannot label a
// batch by accident.
func TestRenderRequiresSource(t *testing.T) {
	dir := t.TempDir()
	args := RenderArgs{
		Records: filepath.Join(dir, "records.jsonl"),
		Out:     filepath.Join(dir, "out"),
	}
	if code := RunRender(args); code != 1 {
		t.Errorf("render without --source exited %d, want 1", code)
	}
}

func recordObject(id, scenario string, behaviorTags []any, seedID string) *lab.OrderedMap {
	record := lab.NewOrderedMap()
	record.Set("id", id)
	record.Set("scenario", scenario)
	record.Set("behavior_tags", behaviorTags)
	record.Set("parent_seed_id", seedID)
	record.Set("generator_branch", "anchor")
	record.Set("split", "train")
	record.Set("instance_group_id", "grp-"+scenario+"-0001-anchor")
	return record
}

// §4.4.2 rule 5 names expect.run: a case-level expect.files (with max_calls)
// is a write case, not a script case.
func TestDeriveKindTreatsOnlyRunExpectAsScript(t *testing.T) {
	writeCase := lab.NewOrderedMap()
	files := lab.NewOrderedMap()
	files.Set("reports/totals.csv", lab.NewOrderedMap())
	maxCalls := lab.NewOrderedMap()
	maxCalls.Set("web_search", 1)
	expect := lab.NewOrderedMap()
	expect.Set("files", files)
	expect.Set("max_calls", maxCalls)
	writeCase.Set("expect", expect)
	if caseHasRunExpect(writeCase) {
		t.Error("expect.files alone was read as expect.run")
	}

	scriptCase := lab.NewOrderedMap()
	run := lab.NewOrderedMap()
	run.Set("path", "statement.py")
	expect = lab.NewOrderedMap()
	expect.Set("run", run)
	scriptCase.Set("expect", expect)
	if !caseHasRunExpect(scriptCase) {
		t.Error("expect.run was not detected")
	}
}
