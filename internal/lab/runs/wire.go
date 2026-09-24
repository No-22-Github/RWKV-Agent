package runs

import (
	"bytes"
	"encoding/json"
	"fmt"
	"math"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Read-only wire audit. Official case passes are never replaced by text
// heuristics: shape metrics use generation denominators, termination uses
// turns, pass uses cases, and the optional answer-text match is diagnostic
// only.

// WireVersion is the report's schema tag.
const WireVersion = "wire-audit-v2"

// SplitThink separates a generation's reasoning from its body. kind is one of
// none, self, prefilled, unclosed or empty.
//
// The Python original has a second `if not text.startswith("<think>") and
// opening == "<think></think": return "empty", "", text` branch that the first
// branch already returns from, so it can never run; it is not reproduced.
func SplitThink(raw, prompt string) (kind, thought, body string) {
	text := strings.TrimSpace(raw)
	opening := ""
	if idx := strings.LastIndex(prompt, "Assistant:"); idx != -1 {
		opening = strings.TrimSpace(prompt[idx+len("Assistant:"):])
	}
	if !strings.HasPrefix(text, "<think>") && opening == "<think></think" {
		if strings.HasPrefix(text, ">") {
			return "empty", "", strings.TrimSpace(text[1:])
		}
		return "unclosed", text, ""
	}
	prefilled := strings.HasPrefix(opening, "<think") && !strings.Contains(opening, "</think>")
	source := ""
	switch {
	case strings.HasPrefix(text, "<think>"):
		text = text[len("<think>"):]
		source = "self"
	case prefilled:
		if opening == "<think" && strings.HasPrefix(text, ">") {
			text = text[1:]
		}
		source = "prefilled"
	default:
		return "none", "", text
	}
	if !strings.Contains(text, "</think>") {
		return "unclosed", text, ""
	}
	parts := strings.SplitN(text, "</think>", 2)
	thought, body = parts[0], parts[1]
	if strings.TrimSpace(thought) == "" {
		return "empty", strings.TrimSpace(thought), strings.TrimSpace(body)
	}
	return source, strings.TrimSpace(thought), strings.TrimSpace(body)
}

// CallObject recognizes one complete JSON call; a missing stop-consumed close
// is allowed. This is an audit recognizer, not a tool execution parser: tags in
// prose or quoted JSON examples do not establish that a call was intended.
func CallObject(text string) map[string]any {
	text = strings.TrimSpace(text)
	switch {
	case strings.HasPrefix(text, "<tool_call>"):
		text = text[len("<tool_call>"):]
	case strings.HasPrefix(text, "```json"):
		text = text[len("```json"):]
	case !strings.HasPrefix(text, "{"):
		return nil
	}
	lstripped := strings.TrimLeft(text, " \t\n\r\v\f")
	dec := json.NewDecoder(strings.NewReader(lstripped))
	dec.UseNumber()
	var obj any
	if err := dec.Decode(&obj); err != nil {
		return nil
	}
	tail := strings.TrimSpace(lstripped[dec.InputOffset():])
	if tail != "" && tail != "</tool_call>" && tail != "```" {
		return nil
	}
	m, ok := obj.(map[string]any)
	if !ok || len(m) != 2 {
		return nil
	}
	if _, hasName := m["name"]; !hasName {
		return nil
	}
	if _, hasArguments := m["arguments"]; !hasArguments {
		return nil
	}
	if _, isString := m["name"].(string); !isString {
		return nil
	}
	if _, isObject := m["arguments"].(map[string]any); !isObject {
		return nil
	}
	return m
}

var answerNumberRe = regexp.MustCompile(`-?\d[\d,]*(?:\.\d+)?(?:[eE][+-]?\d+)?`)

// AnswerTextMatch reports whether the output plausibly contains an accepted
// answer. It is diagnostic only: it never rescored a case in the original and
// does not here.
func AnswerTextMatch(expect map[string]any, output string) bool {
	if expected, ok := expect["expected_number"]; ok {
		target, isNum := numberValue(expected)
		if !isNum {
			return false
		}
		tolerance := 0.01
		if tol, ok := expect["tolerance"]; ok {
			if f, isNum := numberValue(tol); isNum {
				tolerance = f
			}
		}
		for _, loc := range answerNumberRe.FindAllStringIndex(output, -1) {
			if !numberBoundariesOK(output, loc[0], loc[1]) {
				continue
			}
			value, err := strconv.ParseFloat(strings.ReplaceAll(output[loc[0]:loc[1]], ",", ""), 64)
			if err != nil {
				continue
			}
			if math.Abs(value-target) <= tolerance {
				return true
			}
		}
		return false
	}
	var values []any
	if anyOf, ok := expect["output_equals_any"].([]any); ok {
		values = anyOf
	} else {
		values = []any{expect["output_equals"]}
	}
	for _, value := range values {
		s, ok := value.(string)
		if !ok {
			continue
		}
		if containsWithWordBoundaries(output, s) {
			return true
		}
	}
	return false
}

// numberBoundariesOK applies the lookarounds the Python regex uses, which Go's
// regexp cannot express: no word character or dot before, and no word character
// (nor a decimal point followed by a digit) after.
func numberBoundariesOK(s string, start, end int) bool {
	if before, ok := runeBefore(s, start); ok && (isWordRune(before) || before == '.') {
		return false
	}
	after, ok := runeAt(s, end)
	if !ok {
		return true
	}
	if isWordRune(after) {
		return false
	}
	if after == '.' {
		if next, ok := runeAt(s, end+1); ok && next >= '0' && next <= '9' {
			return false
		}
	}
	return true
}

// containsWithWordBoundaries is re.search(r"(?<!\w)" + re.escape(literal) +
// r"(?!\w)", text, re.I) without lookarounds.
func containsWithWordBoundaries(text, literal string) bool {
	if literal == "" {
		return false
	}
	re, err := regexp.Compile(`(?i)` + regexp.QuoteMeta(literal))
	if err != nil {
		return false
	}
	for _, loc := range re.FindAllStringIndex(text, -1) {
		if before, ok := runeBefore(text, loc[0]); ok && isWordRune(before) {
			continue
		}
		if after, ok := runeAt(text, loc[1]); ok && isWordRune(after) {
			continue
		}
		return true
	}
	return false
}

// WireArgs are the `run wire` flags.
type WireArgs struct {
	Runs []string
	Bank string
	JSON bool
}

// RunWire is the `run wire` command.
func RunWire(args WireArgs) int {
	var bank map[string]map[string]any
	if args.Bank != "" {
		obj, err := LoadJSONFile(args.Bank, true)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		bank = map[string]map[string]any{}
		for _, c := range mapSlice(obj["cases"]) {
			if id, ok := c["id"].(string); ok {
				bank[id] = c
			}
		}
	}
	reports := make([]map[string]any, 0, len(args.Runs))
	for _, run := range args.Runs {
		report, err := AnalyzeWire(run, bank)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		reports = append(reports, report)
	}
	if args.JSON {
		data, err := lab.EncodeJSON(reports, 2)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		fmt.Println(string(data))
		return 0
	}
	printWireTable(reports)
	return 0
}

// AnalyzeWire is wire_metrics.analyze.
func AnalyzeWire(runDir string, bank map[string]map[string]any) (map[string]any, error) {
	summary, err := LoadJSONFile(runDir+"/summary.json", true)
	if err != nil {
		return nil, err
	}
	manifest, err := LoadJSONFile(runDir+"/run.json", false)
	if err != nil {
		return nil, err
	}
	if manifest == nil {
		manifest = map[string]any{}
	}

	m := newOrderedCounts()
	reasons := newOrderedCounts()
	repairs := newOrderedCounts()
	details := []any{}
	var lengths, thoughtLengths []float64

	terminal := "none"
	harness := mapOf(manifest, "harness")
	if canonical := stringOf(harness, "wire_canonical"); canonical != "" {
		for _, part := range strings.Split(canonical, ";") {
			if idx := strings.Index(part, "="); idx != -1 {
				if part[:idx] == "terminal" {
					terminal = part[idx+1:]
				}
			}
		}
	}

	for _, caseObj := range mapSlice(summary["cases"]) {
		m.add("cases", 1)
		passed, _ := caseObj["passed"].(bool)
		m.addBool("passed", passed)
		caseID := stringOf(caseObj, "id")
		if strings.Contains(caseID, "irrelevance") {
			m.add("irrelevance_cases", 1)
			casePassed, _ := caseObj["passed"].(bool)
			m.addBool("irrelevance_passed", casePassed)
		}
		for ti, turn := range mapSlice(caseObj["turns"]) {
			m.add("turns", 1)
			result := mapOf(turn, "result")
			steps := mapSlice(result["steps"])
			failures := stringList(turn["failures"])

			infra := false
			for _, f := range failures {
				if InfrastructureFailure(f) {
					infra = true
				}
			}
			m.addBool("infra_error_turns", infra)
			forced := stringOf(result, "forced_answer_reason")
			var answerSteps []map[string]any
			for _, st := range steps {
				if stringOf(st, "stage") == "answer" {
					answerSteps = append(answerSteps, st)
				}
			}
			if forced != "" {
				reasons.add(forced, 1)
			}
			m.addBool("forced_triggered", forced != "")
			m.addBool("answer_turns", len(answerSteps) > 0)
			m.addBool("forced_without_answer", forced != "" && len(answerSteps) == 0)

			var decisions, real, executed []map[string]any
			for _, st := range steps {
				if stringOf(st, "stage") != "answer" {
					decisions = append(decisions, st)
				}
			}
			for _, st := range decisions {
				if stringOf(st, "action_type") != "tool" {
					continue
				}
				if stringOf(st, "tool") == terminal && terminal != "none" {
					continue
				}
				real = append(real, st)
			}
			evidence := false
			for _, st := range real {
				if executedFlag, _ := st["tool_executed"].(bool); executedFlag {
					executed = append(executed, st)
				}
				if evidenceFlag, _ := st["tool_evidence"].(bool); evidenceFlag {
					evidence = true
				}
			}
			m.addBool("tool_attempt_turns", len(real) > 0)
			m.addBool("tool_executed_turns", len(executed) > 0)

			last := map[string]any{}
			if len(steps) > 0 {
				last = steps[len(steps)-1]
			}
			lastToolExecuted, _ := last["tool_executed"].(bool)
			lastToolError := stringOf(last, "tool_error")
			terminalOK := terminal != "none" && stringOf(last, "tool") == terminal &&
				lastToolExecuted && lastToolError == ""
			lastStageViolation, _ := last["stage_violation"].(bool)
			lastAction := stringOf(last, "action_type")
			cleanExit := stringOf(result, "output") != "" && !lastStageViolation &&
				stringOf(last, "protocol_error") == "" && (lastAction == "final" || lastAction == "no_tool" || terminalOK)
			runnerError := false
			for _, f := range failures {
				if strings.HasPrefix(f, "runner error:") {
					runnerError = true
				}
			}
			autonomous := cleanExit && forced == "" && len(answerSteps) == 0 && !runnerError
			m.addBool("self_term_tool_attempts", len(real) > 0 && autonomous)
			m.addBool("self_term_tool_executed", len(executed) > 0 && autonomous)
			tags := mapOf(caseObj, "tags")
			if ref, ok := intOf(tags["ref_calls"]); ok && ref > 0 {
				m.add("needs_tool_turns", 1)
				m.addBool("zero_evidence_exit", autonomous && !evidence)
			}

			previousRaw := ""
			var previousCall any
			for di, st := range decisions {
				raw := stringOf(st, "model_output")
				native := stringOf(st, "channel") == "native"
				kind, thought, body := SplitThink(raw, stringOf(mapOf(st, "request"), "prompt"))
				prefix := "later"
				if di == 0 {
					prefix = "first"
				}
				if !native {
					m.add(prefix+"_text_gens", 1)
					m.addBool(prefix+"_think", kind == "self" || kind == "prefilled")
					m.add("think_"+kind, 1)
					if thought != "" {
						thoughtLengths = append(thoughtLengths, float64(len([]rune(thought))))
					}
					if strings.Contains(body, "<tool_call>") && !strings.HasPrefix(body, "<tool_call>") &&
						stringOf(st, "action_type") == "final" {
						candidate := body[strings.Index(body, "<tool_call>"):]
						if CallObject(candidate) != nil {
							m.add("preamble_call_as_final", 1)
							details = append(details, map[string]any{
								"case": caseID, "turn": ti + 1, "step": st["number"], "kind": "preamble_call_as_final"})
						}
					}
					if kind == "unclosed" && strings.Contains(raw, "<tool_call>") {
						m.add("unclosed_mentions_call", 1)
						candidate := raw[strings.LastIndex(raw, "<tool_call>"):]
						if CallObject(candidate) != nil {
							m.add("unclosed_complete_call_candidate", 1)
						}
					}
				}
				var actionCall any
				if stringOf(st, "action_type") == "tool" {
					actionCall = []any{stringOf(st, "tool"), st["tool_arguments"]}
				}
				if di > 0 && !native {
					m.addBool("adjacent_raw_repeat", CallObject(body) != nil && body == previousRaw)
				}
				if di > 0 && actionCall != nil {
					m.addBool("adjacent_same_action", canonicalJSON(actionCall) == canonicalJSON(previousCall))
				}
				previousRaw, previousCall = body, actionCall

				for _, repair := range stringList(st["protocol_repairs"]) {
					repairs.add(repair, 1)
				}
				if stringOf(st, "tool_rejected_reason") == "duplicate_tool_call" {
					m.add("duplicate_reject", 1)
					if di+1 < len(decisions) {
						nxt := decisions[di+1]
						m.add("duplicate_with_next_decision", 1)
						changed := canonicalJSON([]any{stringOf(nxt, "tool"), nxt["tool_arguments"]}) != canonicalJSON(actionCall)
						nxtAction := stringOf(nxt, "action_type")
						nxtStageViolation, _ := nxt["stage_violation"].(bool)
						nxtExecuted, _ := nxt["tool_executed"].(bool)
						m.addBool("duplicate_next_changed_or_exit",
							nxtAction == "no_tool" || (nxtAction == "final" && !nxtStageViolation) ||
								(changed && nxtExecuted))
					}
				}
				if stringOf(st, "action_type") == "no_tool" {
					payload := stringOf(st, "no_tool_answer")
					if payload == "" {
						payload = stringOf(st, "no_tool_rationale")
					}
					lengths = append(lengths, float64(len([]rune(payload))))
				}
			}
			for _, st := range answerSteps {
				m.add("answer_generations", 1)
				m.addBool("answer_parsed_real_call", stringOf(st, "action_type") == "tool")
				_, _, body := SplitThink(stringOf(st, "model_output"), stringOf(mapOf(st, "request"), "prompt"))
				m.addBool("answer_call_shape", CallObject(body) != nil)
			}
			if bank != nil {
				spec, ok := bank[caseID]
				turnPassed, _ := turn["passed"].(bool)
				if ok && !turnPassed {
					turns := mapSlice(spec["turns"])
					if ti < len(turns) && AnswerTextMatch(mapOf(turns[ti], "expect"), stringOf(result, "output")) {
						m.add("failed_answer_text_match", 1)
						var other []string
						for _, f := range failures {
							if !strings.HasPrefix(f, "output ") && !strings.HasPrefix(f, "output =") {
								other = append(other, f)
							}
						}
						m.addBool("answer_match_with_other_failures", len(other) > 0)
						details = append(details, map[string]any{
							"case": caseID, "turn": ti + 1, "kind": "answer_text_match_not_rescore",
							"other_failures": toAnySlice(other)})
					}
				}
			}
		}
	}

	casePass := map[string]any{}
	for _, c := range mapSlice(summary["cases"]) {
		casePass[stringOf(c, "id")] = c["passed"]
	}
	var exitMedian, thinkMedian any
	if len(lengths) > 0 {
		exitMedian = median(lengths)
	}
	if len(thoughtLengths) > 0 {
		thinkMedian = median(thoughtLengths)
	}
	report := map[string]any{
		"version":                    WireVersion,
		"run":                        runDir,
		"valid_for_model_comparison": m.get("infra_error_turns") == 0,
		"metrics":                    m.asMap(),
		"forced_reasons":             reasons.asMap(),
		"repairs":                    repairs.asMap(),
		"exit_payload_median":        exitMedian,
		"think_chars_median":         thinkMedian,
		"details":                    details,
		"case_pass":                  casePass,
		"wire":                       harness["wire_canonical"],
		"model":                      manifest["model"],
		"sampling":                   manifest["sampling"],
	}
	return report, nil
}

// median is statistics.median: the middle value, or the mean of the two
// middle values for an even count.
func median(values []float64) float64 {
	sorted := append([]float64(nil), values...)
	sort.Float64s(sorted)
	n := len(sorted)
	if n%2 == 1 {
		return sorted[n/2]
	}
	return (sorted[n/2-1] + sorted[n/2]) / 2
}

func printWireTable(reports []map[string]any) {
	names := make([]string, 0, len(reports))
	for _, r := range reports {
		names = append(names, baseName(stringOf(r, "run")))
	}
	fmt.Println("| 指标 | " + strings.Join(names, " | ") + " |")
	fmt.Println("|---|" + strings.Repeat("---|", len(reports)))

	metrics := func(r map[string]any) map[string]any { return mapOf(r, "metrics") }
	num := func(m map[string]any, key string) float64 {
		f, _ := numberValue(m[key])
		return f
	}
	rows := []struct {
		name string
		fn   func(map[string]any) string
	}{
		{"通过/cases", func(r map[string]any) string {
			m := metrics(r)
			prefix := ""
			if valid, _ := r["valid_for_model_comparison"].(bool); !valid {
				prefix = "无效 run；原始记录 "
			}
			return prefix + fmt.Sprintf("%s/%s", formatNumber(num(m, "passed")), formatNumber(num(m, "cases")))
		}},
		{"基础设施错误/turns", func(r map[string]any) string { return formatNumber(num(metrics(r), "infra_error_turns")) }},
		{"BFCL irrelevance", func(r map[string]any) string {
			m := metrics(r)
			return fmt.Sprintf("%s/%s", formatNumber(num(m, "irrelevance_passed")), formatNumber(num(m, "irrelevance_cases")))
		}},
		{"开场白调用判为final/gens", func(r map[string]any) string { return formatNumber(num(metrics(r), "preamble_call_as_final")) }},
		{"未闭合提到调用/完整候选", func(r map[string]any) string {
			m := metrics(r)
			return fmt.Sprintf("%s/%s", formatNumber(num(m, "unclosed_mentions_call")), formatNumber(num(m, "unclosed_complete_call_candidate")))
		}},
		{"后续有思考/text gens", func(r map[string]any) string {
			m := metrics(r)
			return fmt.Sprintf("%s/%s", formatNumber(num(m, "later_think")), formatNumber(num(m, "later_text_gens")))
		}},
		{"自主收尾/有工具尝试turns", func(r map[string]any) string {
			m := metrics(r)
			return fmt.Sprintf("%s/%s", formatNumber(num(m, "self_term_tool_attempts")), formatNumber(num(m, "tool_attempt_turns")))
		}},
		{"强制触发/answer turns", func(r map[string]any) string {
			m := metrics(r)
			return fmt.Sprintf("%s/%s", formatNumber(num(m, "forced_triggered")), formatNumber(num(m, "answer_turns")))
		}},
		{"dup拒绝", func(r map[string]any) string { return formatNumber(num(metrics(r), "duplicate_reject")) }},
		{"出口payload中位字符", func(r map[string]any) string { return formatValue(r["exit_payload_median"]) }},
		{"答案文本命中/仍有其他失败", func(r map[string]any) string {
			m := metrics(r)
			return fmt.Sprintf("%s/%s", formatNumber(num(m, "failed_answer_text_match")), formatNumber(num(m, "answer_match_with_other_failures")))
		}},
	}
	for _, row := range rows {
		cells := make([]string, 0, len(reports))
		for _, r := range reports {
			cells = append(cells, row.fn(r))
		}
		fmt.Println("| " + row.name + " | " + strings.Join(cells, " | ") + " |")
	}
	if len(reports) > 1 {
		base, _ := reports[0]["case_pass"].(map[string]any)
		for _, report := range reports[1:] {
			other, _ := report["case_pass"].(map[string]any)
			if len(base) != len(other) {
				continue
			}
			same := true
			for k := range base {
				if _, ok := other[k]; !ok {
					same = false
					break
				}
			}
			if !same {
				continue
			}
			var gains, losses []any
			keys := make([]string, 0, len(base))
			for k := range base {
				keys = append(keys, k)
			}
			sort.Strings(keys)
			for _, k := range keys {
				b, _ := base[k].(bool)
				o, _ := other[k].(bool)
				if !b && o {
					gains = append(gains, k)
				}
				if b && !o {
					losses = append(losses, k)
				}
			}
			out, err := lab.EncodeOrderedJSON(map[string]any{
				"compare": baseName(stringOf(report, "run")), "gains": gains, "losses": losses,
			}, lab.EncodeOptions{SortKeys: true, SpacedSeparators: true})
			if err == nil {
				fmt.Println(string(out))
			}
		}
	}
}

func formatNumber(f float64) string {
	if f == math.Trunc(f) && math.Abs(f) < 1e15 {
		return strconv.FormatInt(int64(f), 10)
	}
	return lab.PyFloat(f).String()
}

func formatValue(v any) string {
	if v == nil {
		return "<nil>"
	}
	if f, ok := numberValue(v); ok {
		return formatNumber(f)
	}
	return fmt.Sprintf("%v", v)
}

func baseName(path string) string {
	path = strings.TrimRight(path, "/")
	if idx := strings.LastIndex(path, "/"); idx != -1 {
		return path[idx+1:]
	}
	return path
}

func stringList(v any) []string {
	items, _ := v.([]any)
	out := make([]string, 0, len(items))
	for _, item := range items {
		if s, ok := item.(string); ok {
			out = append(out, s)
		}
	}
	return out
}

func toAnySlice(items []string) []any {
	out := make([]any, len(items))
	for i, item := range items {
		out[i] = item
	}
	return out
}

// canonicalJSON renders a value with sorted keys, for Python's dict equality.
func canonicalJSON(v any) string {
	data, err := lab.EncodeOrderedJSON(v, lab.EncodeOptions{SortKeys: true})
	if err != nil {
		return fmt.Sprintf("%v", v)
	}
	return string(bytes.TrimSpace(data))
}

// orderedCounts is a Counter that keeps insertion order, which print paths
// depend on when counts tie (P6).
type orderedCounts struct {
	keys   []string
	counts map[string]int
}

func newOrderedCounts() *orderedCounts {
	return &orderedCounts{counts: map[string]int{}}
}

func (c *orderedCounts) add(key string, delta int) {
	if _, seen := c.counts[key]; !seen {
		c.keys = append(c.keys, key)
	}
	c.counts[key] += delta
}

func (c *orderedCounts) get(key string) int { return c.counts[key] }

// addBool is Python's `counter[key] += bool(...)`: the key is created even when
// the value is False, and the JSON report shows the zero.
func (c *orderedCounts) addBool(key string, cond bool) {
	if cond {
		c.add(key, 1)
		return
	}
	if _, seen := c.counts[key]; !seen {
		c.keys = append(c.keys, key)
		c.counts[key] += 0
	}
}

func (c *orderedCounts) asMap() map[string]any {
	out := make(map[string]any, len(c.keys))
	for _, key := range c.keys {
		out[key] = c.counts[key]
	}
	return out
}
