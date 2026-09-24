package corpus

import (
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// Pick teacher paths out of agent-eval runs and write them as a replay script.
//
// A teacher (for example DeepSeek over chat-completions, native tool calling)
// runs a bank of distillation cases k times; each passing, clean run of a case
// is a candidate path. Only actions cross over (tool name, arguments, final
// text) — the teacher's own wire, reasoning and receipts stay behind, and
// render replays the actions through the student's wire.
//
// Per case: drop failing or unclean runs and exact duplicates, then keep the
// shortest path first and further paths only when their tool sequence differs,
// up to --max-per-case. Script case IDs are "<case id>--p<n>".

// defaults are the work-v1 implementation defaults for tool arguments.
// Arguments equal to them carry no information; teachers that fill every
// schema field would otherwise teach the student to spell them out. Values
// from internal/agent/tools.go and internal/agent/tools/{web,assistant}.go.
var defaults = map[string]map[string]any{
	"list_files":  {"path": "", "max_depth": 3, "max_results": 200},
	"search_text": {"path": "", "case_sensitive": false, "max_results": 50},
	"web_search":  {"max_results": 5},
}

// emptyMeansAbsent are optional arguments whose empty value means "not given".
var emptyMeansAbsent = map[string]map[string]bool{
	"read_lines": {"start_line": true, "end_line": true},
	"calculator": {"precision": true},
	"data_query": {"filter": true, "select": true, "group_by": true,
		"operation": true, "field": true, "expression": true},
}

// Action is one generation's contribution to a path: a tool call or a final
// answer.
type Action struct {
	Text  string // the generation's raw output
	Tool  string // empty for a final answer
	Final bool
}

// Trajectory is one case's actions, in order.
type Trajectory []Action

// Unclean is a passing run whose path cannot be replayed as-is; the message is
// the drop reason.
type Unclean string

func (u Unclean) Error() string { return string(u) }

// NormalizeArguments drops the arguments that carry no information: values
// equal to the harness default (and of the same type — Python's
// `type(value) is type(default)` distinguishes 3 from 3.0, and dropping 3.0
// would change what the student is taught, P3), and optional arguments whose
// empty value means "not given".
func NormalizeArguments(name string, arguments *lab.OrderedMap) *lab.OrderedMap {
	toolDefaults := defaults[name]
	optional := emptyMeansAbsent[name]
	kept := lab.NewOrderedMap()
	if arguments == nil {
		return kept
	}
	for _, key := range arguments.Keys {
		value := arguments.Values[key]
		if value == nil {
			continue
		}
		if def, ok := toolDefaults[key]; ok && pythonEqual(value, def) {
			continue
		}
		if optional[key] && emptyMeansAbsentValue(value) {
			continue
		}
		kept.Set(key, value)
	}
	return kept
}

// Extract returns the actions of one passing run, or an Unclean reason.
func Extract(run CaseRun) (Trajectory, error) {
	if run.Retries > 0 {
		return nil, Unclean("protocol retry")
	}
	var actions []Action
	for _, result := range run.Turns {
		if len(result.Steps) == 0 {
			return nil, Unclean("turn without steps")
		}
		for index, step := range result.Steps {
			if step.Stage != agent.StageDecision {
				stage := string(step.Stage)
				if stage == "" {
					stage = "None"
				}
				return nil, Unclean(stage + " stage (forced closeout)")
			}
			switch step.ActionType {
			case "tool":
				if step.ToolError != "" || step.ToolRejected != "" || !step.ToolExecuted {
					return nil, Unclean("tool error or rejection")
				}
				arguments, err := orderedArguments(step.ToolArguments)
				if err != nil {
					return nil, Unclean("non-object tool arguments")
				}
				name := step.Tool
				text, err := ToolCall(name, NormalizeArguments(name, arguments))
				if err != nil {
					return nil, err
				}
				actions = append(actions, Action{Text: text, Tool: name})
			case "final":
				if index != len(result.Steps)-1 {
					return nil, Unclean("final before the last step")
				}
				text := strings.TrimSpace(step.ModelOutput)
				if text != strings.TrimSpace(result.Output) {
					return nil, Unclean("answer repaired by the harness")
				}
				if text == "" {
					return nil, Unclean("empty final answer")
				}
				actions = append(actions, Action{Text: text, Final: true})
			default:
				return nil, Unclean("action " + pyRepr(step.ActionType))
			}
		}
	}
	return actions, nil
}

// orderedArguments decodes a step's tool arguments without losing key order
// (P1) or number spelling (P3). Python's `step.get("tool_arguments") or {}`
// means a falsy value counts as an empty object.
func orderedArguments(raw json.RawMessage) (*lab.OrderedMap, error) {
	if len(raw) == 0 {
		return lab.NewOrderedMap(), nil
	}
	obj, err := lab.DecodeOrderedJSON(raw)
	if err != nil {
		return nil, err
	}
	if !truthy(obj) {
		return lab.NewOrderedMap(), nil
	}
	om, ok := obj.(*lab.OrderedMap)
	if !ok {
		return nil, fmt.Errorf("tool arguments are not an object")
	}
	return om, nil
}

// CaseStats accumulates one case's runs across the teacher run directories.
type CaseStats struct {
	Runs       int
	Passed     int
	Drops      *orderedCounter
	Candidates []candidate
}

type candidate struct {
	path     Trajectory
	runIndex int
}

// Collect groups runs by case, counting drops. The returned order is the order
// cases were first seen, which print_summary's drop tally depends on.
func Collect(runDirs []string) (map[string]*CaseStats, []string, error) {
	stats := map[string]*CaseStats{}
	var order []string
	for runIndex, runDir := range runDirs {
		runs, err := LoadRunDir(runDir)
		if err != nil {
			return nil, nil, err
		}
		for _, run := range runs {
			if strings.Contains(run.CaseID, PathSeparator) {
				return nil, nil, fmt.Errorf("case id %s contains the reserved separator %s",
					pyRepr(run.CaseID), pyRepr(PathSeparator))
			}
			stat, seen := stats[run.CaseID]
			if !seen {
				stat = &CaseStats{Drops: newOrderedCounter()}
				stats[run.CaseID] = stat
				order = append(order, run.CaseID)
			}
			stat.Runs++
			if !run.Passed {
				stat.Drops.Add("failed")
				continue
			}
			stat.Passed++
			path, err := Extract(run)
			if err != nil {
				stat.Drops.Add(err.Error())
				continue
			}
			stat.Candidates = append(stat.Candidates, candidate{path: path, runIndex: runIndex})
		}
	}
	return stats, order, nil
}

// Select keeps the shortest paths first (ties in run order), then only paths
// whose tool sequence is new, up to maxPerCase.
func Select(stat *CaseStats, maxPerCase int) []Trajectory {
	seen := map[string]bool{}
	shapes := map[string]bool{}
	var kept []Trajectory
	ordered := append([]candidate(nil), stat.Candidates...)
	sort.SliceStable(ordered, func(i, j int) bool {
		if len(ordered[i].path) != len(ordered[j].path) {
			return len(ordered[i].path) < len(ordered[j].path)
		}
		return ordered[i].runIndex < ordered[j].runIndex
	})
	for _, item := range ordered {
		key := trajectoryKey(item.path)
		if seen[key] {
			stat.Drops.Add("duplicate path")
			continue
		}
		seen[key] = true
		shape := shapeKey(item.path)
		if len(kept) > 0 && shapes[shape] {
			stat.Drops.Add("same tool sequence")
			continue
		}
		if len(kept) >= maxPerCase {
			stat.Drops.Add("over per-case cap")
			continue
		}
		shapes[shape] = true
		kept = append(kept, item.path)
	}
	return kept
}

// PathsArgs are the `corpus paths` flags.
type PathsArgs struct {
	Run        []string
	Out        string
	Report     string
	MaxPerCase int
}

// RunPaths is the `corpus paths` command.
func RunPaths(args PathsArgs) int {
	stats, order, err := Collect(args.Run)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	var entries []*lab.OrderedMap
	var report []*lab.OrderedMap
	for _, caseID := range sortedKeys(order) {
		stat := stats[caseID]
		kept := Select(stat, args.MaxPerCase)
		for number, path := range kept {
			texts := make([]string, 0, len(path))
			for _, action := range path {
				texts = append(texts, action.Text)
			}
			entries = append(entries, scriptEntryOrdered(Entry(PathID(caseID, number+1), texts, nil)))
		}
		steps := make([]any, 0, len(kept))
		for _, path := range kept {
			steps = append(steps, len(path))
		}
		row := lab.NewOrderedMap()
		row.Set("case_id", caseID)
		row.Set("runs", stat.Runs)
		row.Set("passed", stat.Passed)
		row.Set("kept", len(kept))
		row.Set("steps", steps)
		row.Set("drops", stat.Drops.OrderedMap())
		report = append(report, row)
	}

	if err := WriteJSONL(args.Out, entries, "x"); err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	if args.Report != "" {
		if err := WriteJSONL(args.Report, report, "x"); err != nil {
			fmt.Fprintln(stderr, err)
			return 1
		}
	}
	printPathsSummary(stats, order, entries, report)
	return 0
}

// printPathsSummary reproduces paths.py's console summary: the pass@k tally,
// then drop reasons by count.
//
// Python's Counter.most_common() breaks ties by first-insertion order, and Go
// map iteration has none, so the tally carries its own key order (P6).
func printPathsSummary(stats map[string]*CaseStats, order []string, entries, report []*lab.OrderedMap) {
	drops := newOrderedCounter()
	for _, caseID := range order {
		drops.Merge(stats[caseID].Drops)
	}
	passAt := newPassAtCount()
	for _, row := range report {
		passAt.Add(intField(row, "passed"), intField(row, "runs"))
	}
	withAtLeastOne := 0
	for _, row := range report {
		if intField(row, "kept") > 0 {
			withAtLeastOne++
		}
	}
	fmt.Printf("paths: %d cases, %d paths kept (%d cases with at least one)\n",
		len(stats), len(entries), withAtLeastOne)

	var passParts []string
	for _, item := range passAt.Sorted() {
		passParts = append(passParts, fmt.Sprintf("%s: %d", item.Key, item.Count))
	}
	fmt.Println("  pass@k: " + strings.Join(passParts, ", "))

	for _, item := range drops.MostCommon() {
		fmt.Printf("  %5d  dropped: %s\n", item.Count, item.Key)
	}

	var never []string
	for _, row := range report {
		if intField(row, "passed") == 0 {
			never = append(never, stringField(row, "case_id"))
		}
	}
	if len(never) > 0 {
		shown := never
		suffix := ""
		if len(never) > 20 {
			shown = never[:20]
			suffix = " …"
		}
		fmt.Printf("  %d cases never passed (check the case before distilling): %s%s\n",
			len(never), strings.Join(shown, " "), suffix)
	}
}

func sortedKeys(keys []string) []string {
	out := append([]string(nil), keys...)
	sort.Strings(out)
	return out
}

func trajectoryKey(path Trajectory) string {
	var b strings.Builder
	for _, action := range path {
		fmt.Fprintf(&b, "%d:%s\x00%s\x01", len(action.Text), action.Text, action.Tool)
	}
	return b.String()
}

func shapeKey(path Trajectory) string {
	parts := make([]string, 0, len(path))
	for _, action := range path {
		if action.Final {
			parts = append(parts, "final")
		} else {
			parts = append(parts, action.Tool)
		}
	}
	return strings.Join(parts, "\x00")
}

// scriptEntryOrdered renders a ScriptEntry with Python's key order and
// separators.
func scriptEntryOrdered(entry eval.ScriptEntry) *lab.OrderedMap {
	outputs := make([]any, 0, len(entry.Outputs))
	for _, output := range entry.Outputs {
		item := lab.NewOrderedMap()
		item.Set("text", output.Text)
		item.Set("supervised", output.Supervised)
		outputs = append(outputs, item)
	}
	m := lab.NewOrderedMap()
	m.Set("case_id", entry.CaseID)
	m.Set("outputs", outputs)
	return m
}
