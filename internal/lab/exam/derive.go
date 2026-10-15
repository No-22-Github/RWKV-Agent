package exam

import (
	"regexp"
	"slices"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// Task kinds: what the user is asking the App to do. Every case has exactly
// one, so the exam can be stratified and reported by it.
const (
	TaskAnswerDirect = "answer-direct"
	TaskFindRead     = "find-read"
	TaskCompute      = "compute"
	TaskWrite        = "write"
	TaskExternal     = "external"
)

// Difficulty factors: what makes the case hard. A case carries zero or more.
const (
	DiffMultiSource = "multi-source"
	DiffCheck       = "check"
	DiffRecovery    = "recovery"
	DiffLongInput   = "long-input"
	DiffFollowUp    = "follow-up"
	DiffDecoy       = "decoy"
)

// TaskOrder and DifficultyOrder fix the reporting order.
var (
	TaskOrder       = []string{TaskAnswerDirect, TaskFindRead, TaskCompute, TaskWrite, TaskExternal}
	DifficultyOrder = []string{DiffMultiSource, DiffCheck, DiffRecovery, DiffLongInput, DiffFollowUp, DiffDecoy}
)

// TaskLabel and DifficultyLabel are the plain-language names used in
// SUITES.md; the ids above are what the JSON carries.
var TaskLabel = map[string]string{
	TaskAnswerDirect: "直接回答（不该调工具 / 该先反问）",
	TaskFindRead:     "查找与阅读本地文件",
	TaskCompute:      "统计与计算",
	TaskWrite:        "改文件与写产物",
	TaskExternal:     "外部信息（上网、天气）",
}

var DifficultyLabel = map[string]string{
	DiffMultiSource: "多个来源拼答案",
	DiffCheck:       "核对与守约束（版本冲突、数据里的指令、只读）",
	DiffRecovery:    "出错恢复（路径不对、链接失效、工具报错）",
	DiffLongInput:   "长输入（大文件、截断、分页）",
	DiffFollowUp:    "用户追问（不止一条用户消息）",
	DiffDecoy:       "有相似的干扰答案",
}

// Answer forms: how the final reply is judged.
const (
	FormNumber   = "number"
	FormExact    = "exact"
	FormContains = "contains"
	FormAbstain  = "abstain"
	FormNoCall   = "no-call"
	FormFile     = "file"
)

var FormLabel = map[string]string{
	FormNumber:   "数字（允许误差）",
	FormExact:    "整句精确相等",
	FormContains: "回答里包含正确值",
	FormAbstain:  "应说明查不到",
	FormNoCall:   "不调工具直接答",
	FormFile:     "只看文件最后的样子",
}

var cjk = regexp.MustCompile(`[\p{Han}]`)

// Language is "zh" when the first prompt contains Han characters.
func Language(c eval.Case) string {
	if len(c.Turns) > 0 && cjk.MatchString(c.Turns[0].Prompt) {
		return "zh"
	}
	return "en"
}

func tagString(c eval.Case, key string) string {
	value, _ := c.Tags[key].(string)
	return value
}

func tagStrings(c eval.Case, key string) []string {
	raw, _ := c.Tags[key].([]any)
	out := make([]string, 0, len(raw))
	for _, item := range raw {
		if text, ok := item.(string); ok {
			out = append(out, text)
		}
	}
	return out
}

func tagInt(c eval.Case, key string) (int, bool) {
	switch value := c.Tags[key].(type) {
	case float64:
		return int(value), true
	case int:
		return value, true
	}
	return 0, false
}

func noCallTurn(e eval.Expectation) bool {
	return (e.Tools != nil && len(e.Tools) == 0) || e.RequireActiveNoCall
}

func hasOutputCheck(e eval.Expectation) bool {
	return e.OutputEquals != nil || len(e.OutputEqualsAny) > 0 || len(e.OutputContains) > 0 ||
		len(e.OutputContainsAny) > 0 || e.ExpectedNumber != nil || len(e.MustStateUnverified) > 0
}

// AnswerForm classifies the last turn's expectation.
func AnswerForm(c eval.Case) string {
	if len(c.Turns) == 0 {
		return FormFile
	}
	e := c.Turns[len(c.Turns)-1].Expect
	switch {
	case e.ExpectedNumber != nil:
		return FormNumber
	case e.OutputEquals != nil && *e.OutputEquals == "UNKNOWN", slices.Contains(e.OutputEqualsAny, "UNKNOWN"),
		len(e.MustStateUnverified) > 0:
		return FormAbstain
	case e.OutputEquals != nil || len(e.OutputEqualsAny) > 0:
		return FormExact
	case len(e.OutputContains) > 0 || len(e.OutputContainsAny) > 0:
		return FormContains
	case noCallTurn(e):
		return FormNoCall
	}
	return FormFile
}

var computeTaskTypes = map[string]bool{
	"aggregate": true, "reconcile": true, "join": true, "filter_count": true, "rank": true,
	"policy_calc": true, "count_events": true, "time_window": true, "aggregate_jsonl": true,
	"count_markers": true, "largest": true, "count_by_type": true, "duplicates": true,
	"web_then_calc": true, "unit_convert": true,
}

var writeTaskTypes = map[string]bool{
	"write_summary": true, "edit_value": true, "merge": true, "write_structured": true,
	"bulk_edit": true, "scoped_delete": true, "write_new": true, "add_flag": true,
	"fix_from_traceback": true, "stdlib_only": true, "fix_output": true, "fix_edge_case": true,
	"web_then_edit": true, "tool_then_write": true,
}

func requiredTool(c eval.Case, names ...string) bool {
	for _, turn := range c.Turns {
		for _, tool := range turn.Expect.RequiredTools {
			if slices.Contains(names, tool) {
				return true
			}
		}
	}
	return false
}

// Task returns the case's task kind. tags.exam_task overrides the rules.
func Task(c eval.Case, suite string) string {
	if override := tagString(c, "exam_task"); override != "" {
		return override
	}
	scenario := tagString(c, "scenario")
	taskType := tagString(c, "task_type")
	probe := tagString(c, "probe_axis")
	if scenario == "notool" || (len(c.Turns) > 0 && noCallTurn(c.Turns[0].Expect)) {
		return TaskAnswerDirect
	}
	if scenario == "web" || strings.HasPrefix(taskType, "web_") || taskType == "special_tool" ||
		strings.HasPrefix(suite, "weatherprobe") || len(c.WeatherFixture) > 0 ||
		requiredTool(c, "web_search", "web_fetch", "get_weather") {
		return TaskExternal
	}
	if writeTaskTypes[taskType] || scenario == "script" || probe == "edit" || probe == "artifact" ||
		probe == "closure" || AnswerForm(c) == FormFile {
		return TaskWrite
	}
	if computeTaskTypes[taskType] || scenario == "tabular" || probe == "aggregate" ||
		AnswerForm(c) == FormNumber {
		return TaskCompute
	}
	return TaskFindRead
}

// Difficulties returns the case's difficulty factors in DifficultyOrder.
// tags.exam_difficulties overrides the rules.
func Difficulties(c eval.Case) []string {
	if _, present := c.Tags["exam_difficulties"]; present {
		return orderDifficulties(tagStrings(c, "exam_difficulties"))
	}
	axes := tagStrings(c, "axes")
	traps := tagStrings(c, "traps")
	probe := tagString(c, "probe_axis")
	has := func(list []string, items ...string) bool {
		for _, item := range items {
			if slices.Contains(list, item) {
				return true
			}
		}
		return false
	}
	set := map[string]bool{}
	if has(axes, "CHN") || has(traps, "TR-MULTISRC", "TR-RULEFILE", "TR-PRECEDENCE") {
		set[DiffMultiSource] = true
	}
	if has(axes, "VER", "CON") || has(traps, "TR-INJECT", "TR-READONLY", "TR-SUPERSEDE", "TR-CLAIM", "TR-WEBSTALE") ||
		probe == "safety" {
		set[DiffCheck] = true
	}
	if has(axes, "ERR") || has(traps, "TR-NEARNAME", "TR-FETCHFAIL") || probe == "recover" {
		set[DiffRecovery] = true
	}
	if bytes, ok := tagInt(c, "fixture_bytes"); has(axes, "LNG") || has(traps, "TR-LONG", "TR-TRUNC") ||
		(ok && bytes >= 64*1024) {
		set[DiffLongInput] = true
	}
	if len(c.Turns) > 1 {
		set[DiffFollowUp] = true
	}
	if has(traps, "TR-DECOY") {
		set[DiffDecoy] = true
	}
	out := make([]string, 0, len(set))
	for _, item := range DifficultyOrder {
		if set[item] {
			out = append(out, item)
		}
	}
	return out
}

func orderDifficulties(items []string) []string {
	out := make([]string, 0, len(items))
	for _, item := range DifficultyOrder {
		if slices.Contains(items, item) {
			out = append(out, item)
		}
	}
	return out
}

// Row derives a manifest row for a case at a repository-relative path.
func Row(c eval.Case, suite, relPath, sha string) eval.ExamCase {
	row := eval.ExamCase{
		ID:           c.ID,
		Suite:        suite,
		Path:         relPath,
		SHA256:       sha,
		Scenario:     tagString(c, "scenario"),
		TaskType:     tagString(c, "task_type"),
		Level:        tagString(c, "level"),
		Language:     Language(c),
		UserTurns:    len(c.Turns),
		AnswerForm:   AnswerForm(c),
		Task:         Task(c, suite),
		Difficulties: Difficulties(c),
		Author:       tagString(c, "author"),
		Status:       tagString(c, "status"),
	}
	if row.Scenario == "" {
		row.Scenario = c.Category
	}
	if calls, ok := tagInt(c, "ref_calls"); ok {
		row.RefCalls = &calls
	}
	return row
}
