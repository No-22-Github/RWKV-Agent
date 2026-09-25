package corpus

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// Per-row labels (docs/distill-workflow.md §4.4).
//
// A row's text and loss_spans come from the harness replay and must never be
// touched here; everything in this file only fills in meta. The label block
// is attached to the case the row was rendered from, so `corpus rows` can
// read it back without joining against the source records.

// DefaultTagMap is the reviewed mapping that turns the 700 records' mixed
// behaviour_tags into the authoring vocabulary.
func DefaultTagMap() string {
	return filepath.Join(RepoRoot(), "bench", "distill", "tag-map.json")
}

// DefaultVocab is the authoring vocabulary that defines legal task types.
func DefaultVocab() string {
	return filepath.Join(RepoRoot(), "bench", "workbank", "docs", "tag-vocab.json")
}

// TagMap is bench/distill/tag-map.json. The normalisation rules live in data
// rather than in Go because the task_type choices needed human judgement:
// they have to be reviewable and correctable without a rebuild.
type TagMap struct {
	overrides map[string]tagOverride
	behaviors map[string]*string
	undefined map[string]bool
}

type tagOverride struct {
	TaskType string
	Reason   string
}

// LoadTagMap reads and validates the tag map.
func LoadTagMap(path string) (*TagMap, error) {
	obj, err := lab.DecodeOrderedJSONFile(path)
	if err != nil {
		return nil, err
	}
	root, ok := obj.(*lab.OrderedMap)
	if !ok {
		return nil, fmt.Errorf("%s is not a JSON object", path)
	}
	tagMap := &TagMap{
		overrides: map[string]tagOverride{},
		behaviors: map[string]*string{},
		undefined: map[string]bool{},
	}
	for _, id := range keysOf(mapValue(root, "task_type_overrides")) {
		entry := anyMapValue(mapValue(root, "task_type_overrides"), id)
		taskType := stringFieldOf(entry, "task_type")
		if taskType == "" {
			return nil, fmt.Errorf("%s: task_type_overrides[%s] has no task_type", path, id)
		}
		tagMap.overrides[id] = tagOverride{TaskType: taskType, Reason: stringFieldOf(entry, "reason")}
	}
	behaviorObj, _ := mapValue(root, "behaviors").(*lab.OrderedMap)
	if behaviorObj != nil {
		for _, tag := range behaviorObj.Keys {
			value, _ := behaviorObj.Get(tag)
			if value == nil {
				tagMap.behaviors[tag] = nil
				continue
			}
			name, ok := value.(string)
			if !ok {
				return nil, fmt.Errorf("%s: behaviors[%s] must be a string or null", path, tag)
			}
			mapped := name
			tagMap.behaviors[tag] = &mapped
		}
	}
	for _, item := range anySliceValue(mapValue(root, "undefined")) {
		if tag, ok := item.(string); ok {
			tagMap.undefined[tag] = true
		}
	}
	return tagMap, nil
}

// OverrideIDs lists the records the tag map overrides, sorted.
func (t *TagMap) OverrideIDs() []string {
	out := make([]string, 0, len(t.overrides))
	for id := range t.overrides {
		out = append(out, id)
	}
	sort.Strings(out)
	return out
}

// Vocab is the authoring vocabulary's task-type table.
type Vocab struct {
	taskTypes map[string][]string
	all       map[string]bool
}

// LoadVocab reads tag-vocab.json's task types.
func LoadVocab(path string) (*Vocab, error) {
	obj, err := lab.DecodeOrderedJSONFile(path)
	if err != nil {
		return nil, err
	}
	root, ok := obj.(*lab.OrderedMap)
	if !ok {
		return nil, fmt.Errorf("%s is not a JSON object", path)
	}
	vocab := &Vocab{taskTypes: map[string][]string{}, all: map[string]bool{}}
	table, _ := mapValue(root, "task_types").(*lab.OrderedMap)
	if table == nil {
		return nil, fmt.Errorf("%s has no task_types", path)
	}
	for _, scenario := range table.Keys {
		var types []string
		for _, item := range anySliceValue(table.Values[scenario]) {
			if name, ok := item.(string); ok {
				types = append(types, name)
				vocab.all[name] = true
			}
		}
		vocab.taskTypes[scenario] = types
	}
	return vocab, nil
}

// IsTaskType reports whether a label names a task type for some scenario. Such
// labels describe what the task is, not how it behaves, so they are dropped
// from case_tags.behaviors — the task_type field carries them.
func (v *Vocab) IsTaskType(label string) bool { return v.all[label] }

// NormalizeRecord converts one 700-record's labels into the authoring
// vocabulary. It refuses to guess: a record whose task type cannot be derived
// and has no override is an error, never an empty field.
func (t *TagMap) NormalizeRecord(record *lab.OrderedMap, vocab *Vocab) (eval.CaseTags, error) {
	scenario := mapString(record, "scenario")
	taskType, err := t.resolveTaskType(record, vocab)
	if err != nil {
		return eval.CaseTags{}, err
	}
	behaviors, err := t.normalizeBehaviors(record, vocab)
	if err != nil {
		return eval.CaseTags{}, err
	}
	return eval.CaseTags{
		Scenario:  scenario,
		TaskType:  taskType,
		Traps:     []string{},
		Level:     nil,
		Family:    mapString(record, "instance_group_id"),
		Behaviors: behaviors,
		Origin: &eval.TagOrigin{
			ParentSeedID: mapString(record, "parent_seed_id"),
			Branch:       mapString(record, "generator_branch"),
			Split:        mapString(record, "split"),
			BehaviorTags: tagStrings(record, "behavior_tags"),
		},
	}, nil
}

func (t *TagMap) resolveTaskType(record *lab.OrderedMap, vocab *Vocab) (string, error) {
	id := mapString(record, "id")
	scenario := mapString(record, "scenario")
	legal := vocab.taskTypes[scenario]
	if len(legal) == 0 {
		return "", fmt.Errorf("%s: scenario %q has no task types in the vocabulary", id, scenario)
	}
	if override, ok := t.overrides[id]; ok {
		if !containsString(legal, override.TaskType) {
			return "", fmt.Errorf("%s: tag map override %q is not legal for scenario %s", id, override.TaskType, scenario)
		}
		return override.TaskType, nil
	}
	tags := tagStrings(record, "behavior_tags")
	var found []string
	for _, tag := range tags {
		if containsString(legal, tag) {
			found = append(found, tag)
		}
	}
	switch len(found) {
	case 1:
		return found[0], nil
	case 0:
		return "", fmt.Errorf("%s: none of behavior_tags %v is a task type for scenario %s and the tag map has no override",
			id, tags, scenario)
	default:
		return "", fmt.Errorf("%s: behavior_tags %v name %d task types legal for scenario %s; the tag map needs an override",
			id, found, len(found), scenario)
	}
}

func (t *TagMap) normalizeBehaviors(record *lab.OrderedMap, vocab *Vocab) ([]string, error) {
	id := mapString(record, "id")
	var out []string
	seen := map[string]bool{}
	for _, tag := range tagStrings(record, "behavior_tags") {
		if vocab.IsTaskType(tag) {
			continue
		}
		if t.undefined[tag] {
			// Named in the map as undefined; origin.behavior_tags keeps it.
			continue
		}
		mapped, known := t.behaviors[tag]
		if !known {
			return nil, fmt.Errorf("%s: behavior tag %q has no entry in the tag map", id, tag)
		}
		if mapped == nil || *mapped == "" {
			continue
		}
		if seen[*mapped] {
			continue
		}
		seen[*mapped] = true
		out = append(out, *mapped)
	}
	return out, nil
}

// TagsFromCase reads the label block a rendered case carries. seededFromTest
// is true only for cases rendered from records whose parent_seed_id is a test
// bank case.
func TagsFromCase(caseObj *lab.OrderedMap) (eval.CaseTags, bool) {
	tags, _ := mapValue(caseObj, "tags").(*lab.OrderedMap)
	if tags == nil {
		return eval.CaseTags{}, false
	}
	seeded, _ := mapValue(tags, "seeded_from_test").(bool)
	return eval.CaseTags{
		Scenario:  stringFieldOf(tags, "scenario"),
		TaskType:  stringFieldOf(tags, "task_type"),
		Traps:     tagStrings(tags, "traps"),
		Level:     levelField(tags),
		Family:    stringFieldOf(tags, "family"),
		Behaviors: tagStrings(tags, "behaviors"),
		Origin:    originField(tags),
	}, seeded
}

// CaseTagsValue is the case.json `tags` block a rendered records-mode case
// carries: the normalised labels plus the fields `corpus rows` reads back.
func CaseTagsValue(tags eval.CaseTags, seededFromTest bool) *lab.OrderedMap {
	out := lab.NewOrderedMap()
	out.Set("scenario", tags.Scenario)
	out.Set("task_type", tags.TaskType)
	out.Set("traps", stringValues(tags.Traps))
	if tags.Level == nil {
		out.Set("level", nil)
	} else {
		out.Set("level", *tags.Level)
	}
	out.Set("family", tags.Family)
	out.Set("behaviors", stringValues(tags.Behaviors))
	if tags.Origin != nil {
		origin := lab.NewOrderedMap()
		origin.Set("parent_seed_id", tags.Origin.ParentSeedID)
		origin.Set("branch", tags.Origin.Branch)
		origin.Set("split", tags.Origin.Split)
		origin.Set("behavior_tags", stringValues(tags.Origin.BehaviorTags))
		out.Set("origin", origin)
	}
	out.Set("seeded_from_test", seededFromTest)
	return out
}

// TestBankIDs is the set of case IDs in the test bank, shelved cases
// included: a record descended from either is leaked material.
func TestBankIDs() (map[string]bool, error) {
	ids := map[string]bool{}
	for _, name := range []string{"cases", "cases-shelved"} {
		root := filepath.Join(RepoRoot(), "bench", "workbank", name)
		if info, err := os.Stat(root); err != nil || !info.IsDir() {
			continue
		}
		cases, err := Load(root)
		if err != nil {
			return nil, err
		}
		for _, caseObj := range cases {
			if id := mapString(caseObj, "id"); id != "" {
				ids[id] = true
			}
		}
	}
	return ids, nil
}

// --- traj and kind ---------------------------------------------------------

const (
	kindSmalltalk = "smalltalk"
	kindRefuse    = "refuse"
	kindClarify   = "clarify"
	kindDirect    = "direct"
	kindScript    = "script"
	kindWrite     = "write"
	kindWebLocal  = "web_local"
	kindWeb       = "web"
	kindLocal     = "local"
)

var (
	webTools   = map[string]bool{"web_search": true, "web_fetch": true}
	writeTools = map[string]bool{"write_file": true, "replace_lines": true, "append_file": true}
	// neutralTools move the trajectory but leave no local evidence behind.
	neutralTools = map[string]bool{"calculator": true, "datetime": true}
	toolCallOpen = "<tool_call>"
)

// BuildTraj describes one row's turn: the outputs the row covers are
// outputs[first : first+generations].
func BuildTraj(outputs []eval.ScriptOutput, first, generations, turn, turnsTotal, tokens int,
	expect *lab.OrderedMap) eval.TrajStats {

	traj := eval.TrajStats{TurnsTotal: turnsTotal, Tokens: tokens, ToolSeq: []string{}}
	last := ""
	lastIsCall := false
	for index := first; index < first+generations && index < len(outputs); index++ {
		output := outputs[index]
		if !output.Supervised {
			traj.UnsupervisedOutputs++
			continue
		}
		name, isCall := scriptToolName(output.Text)
		last, lastIsCall = output.Text, isCall
		if !isCall {
			continue
		}
		traj.ToolCalls++
		traj.ToolSeq = append(traj.ToolSeq, name)
		switch {
		case webTools[name]:
			traj.Web = true
		case writeTools[name]:
			traj.Writes = true
		case !neutralTools[name]:
			traj.Local = true
		}
	}
	traj.ZeroCall = traj.ToolCalls == 0
	traj.FinalKind = finalKind(last, lastIsCall, expect)
	return traj
}

// finalKind classifies how the turn ended. Only the turn's last output
// decides; a turn that ends in a tool call is an intermediate turn of a
// multi-turn case and has no final at all.
func finalKind(last string, lastIsCall bool, expect *lab.OrderedMap) string {
	if lastIsCall {
		return "none"
	}
	switch strings.TrimSpace(last) {
	case "UNKNOWN":
		return "unknown"
	case "DONE":
		return "done"
	}
	if expect != nil {
		if _, ok := expect.Get("expected_number"); ok {
			return "value"
		}
		if _, ok := expect.Get("output_equals"); ok {
			return "value"
		}
	}
	return "text"
}

// DeriveKind classifies a row the way docs/distill-workflow.md §4.4.2
// prescribes: the first matching rule wins, so a smalltalk row stays
// smalltalk however it was produced.
func DeriveKind(tags eval.CaseTags, traj eval.TrajStats, turn int, hasRunExpect bool) string {
	switch {
	case tags.TaskType == "smalltalk":
		return kindSmalltalk
	case traj.ZeroCall && (tags.TaskType == "beyond_capability" || containsString(tags.Traps, "TR-NOCAP")):
		return kindRefuse
	case traj.ZeroCall && containsString(tags.Traps, "TR-AMBIG") && turn < traj.TurnsTotal:
		return kindClarify
	case traj.ZeroCall:
		return kindDirect
	case tags.Scenario == "script" || hasRunExpect:
		return kindScript
	case traj.Writes:
		return kindWrite
	case traj.Web && traj.Local:
		return kindWebLocal
	case traj.Web:
		return kindWeb
	default:
		return kindLocal
	}
}

// scriptToolName reads the tool a scripted output calls. Script outputs are
// built by ToolCall, so the payload parses; a missing closing tag (the stop
// sequence ate it) is normal.
func scriptToolName(text string) (string, bool) {
	body, ok := strings.CutPrefix(strings.TrimSpace(text), toolCallOpen)
	if !ok {
		return "", false
	}
	body = strings.TrimSuffix(strings.TrimSpace(body), "</tool_call>")
	var payload struct {
		Name string `json:"name"`
	}
	if err := json.Unmarshal([]byte(body), &payload); err != nil {
		return "", true
	}
	return payload.Name, true
}

// --- small helpers over the ordered maps -----------------------------------

func stringFieldOf(m *lab.OrderedMap, key string) string {
	return mapString(m, key)
}

func keysOf(v any) []string {
	if m, ok := v.(*lab.OrderedMap); ok {
		return m.Keys
	}
	return nil
}

func anyMapValue(container any, key string) *lab.OrderedMap {
	root, _ := container.(*lab.OrderedMap)
	if root == nil {
		return nil
	}
	value, _ := root.Get(key)
	out, _ := value.(*lab.OrderedMap)
	return out
}

func anySliceValue(v any) []any {
	items, _ := v.([]any)
	return items
}

func tagStrings(m *lab.OrderedMap, key string) []string {
	if m == nil {
		return []string{}
	}
	value, _ := m.Get(key)
	items, _ := value.([]any)
	out := make([]string, 0, len(items))
	for _, item := range items {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

func stringValues(values []string) []any {
	out := make([]any, len(values))
	for i, value := range values {
		out[i] = value
	}
	return out
}

// levelField keeps a case's level as written; the records have none.
func levelField(tags *lab.OrderedMap) *string {
	value, ok := tags.Get("level")
	if !ok || value == nil {
		return nil
	}
	if s, ok := value.(string); ok {
		return &s
	}
	return nil
}

func originField(tags *lab.OrderedMap) *eval.TagOrigin {
	origin, _ := mapValue(tags, "origin").(*lab.OrderedMap)
	if origin == nil {
		return nil
	}
	return &eval.TagOrigin{
		ParentSeedID: stringFieldOf(origin, "parent_seed_id"),
		Branch:       stringFieldOf(origin, "branch"),
		Split:        stringFieldOf(origin, "split"),
		BehaviorTags: tagStrings(origin, "behavior_tags"),
	}
}

func containsString(list []string, value string) bool {
	for _, item := range list {
		if item == value {
			return true
		}
	}
	return false
}

// caseTurns lists a case's turns as they are written in case.json.
func caseTurns(caseObj *lab.OrderedMap) []*lab.OrderedMap {
	items, _ := mapValue(caseObj, "turns").([]any)
	out := make([]*lab.OrderedMap, 0, len(items))
	for _, item := range items {
		if turn, ok := item.(*lab.OrderedMap); ok {
			out = append(out, turn)
		}
	}
	return out
}

// turnExpect is the expectation of a 1-based turn, or nil when the case does
// not declare one.
func turnExpect(caseObj *lab.OrderedMap, turn int) *lab.OrderedMap {
	turns := caseTurns(caseObj)
	if turn < 1 || turn > len(turns) {
		return nil
	}
	expect, _ := mapValue(turns[turn-1], "expect").(*lab.OrderedMap)
	return expect
}
