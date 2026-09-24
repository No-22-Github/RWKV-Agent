package runs

import (
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Layered failure attribution: is a run's score a capability reading at all?
//
// A single pass rate cannot answer that. G1K scored 2.5% on this bank and
// 81.7% on BFCL with the same weights: the bank score was measuring multi-step
// protocol discipline, not the reasoning the cases were written to test.
//
// Every non-pass is decomposed into ordered layers, first match wins, and the
// verdict reports whether `capability` is measurable for this model — not
// whether the model is good. Diagnostic only: official pass/fail is read from
// the artifacts and never recomputed.

// GateVersion is the report's schema tag.
const GateVersion = "capability-gate-v2"

// A model whose runs exceed these is not being measured on capability. The
// thresholds are deliberately loose: they mark "this score is not a capability
// reading", not "this model is bad".
const (
	protocolCeiling = 0.10
	closeoutCeiling = 0.15
)

// Layers are ordered: a case that broke at `protocol` never reached the
// question the case asks, so the order is the judgement order and must not be
// rearranged.
var Layers = []string{"infra", "protocol", "closeout", "toolchoice", "format", "capability"}

var (
	infraMarkers = []string{
		"upstream provider failure", "continuation error:",
		"http 4", "http 5",
		"connection refused", "connection reset", "no such host",
		"context deadline exceeded", "timeout", "unexpected eof", "broken pipe",
	}
	protocolMarkers = []string{
		"agent protocol error", "protocol error", "is not a json object",
		"action is not allowed", "stage violation", "envelope", "decode",
		"answer contract repaired",
	}
	// A case whose answer depends on a tool the model never reached for is not
	// a reading of the reasoning the case tests.
	toolchoiceMarkers = []string{"required tool"}
	closeoutMarkers   = []string{
		"step limit", "output token limit", "max turns", "forced answer",
		"reached the step limit",
	}
	gateNumberRe = regexp.MustCompile(`[+-]?\d+(?:,\d{3})*(?:\.\d+)?`)
	emphasis     = []string{"**", "__", "*", "_", "`"}
	answerMarker = []string{"final answer:", "answer:", "答案：", "答案:", "最终答案：", "最终答案:"}
)

// normalize mirrors the scorer's answer normalization, for classification only.
func normalize(text string) string {
	value := strings.TrimSpace(text)
	for changed := true; changed; {
		changed = false
		for _, marker := range emphasis {
			if len(value) > 2*len(marker) &&
				strings.HasPrefix(value, marker) && strings.HasSuffix(value, marker) &&
				!strings.Contains(value[len(marker):len(value)-len(marker)], marker) {
				value = strings.TrimSpace(value[len(marker) : len(value)-len(marker)])
				changed = true
			}
		}
	}
	return strings.ToLower(strings.TrimSpace(strings.TrimRight(value, ".。!！;；,，")))
}

func answerOf(caseObj map[string]any) string {
	for _, turn := range mapSlice(caseObj["turns"]) {
		result := mapOf(turn, "result")
		if s := stringOf(result, "original_output"); s != "" {
			return s
		}
		if s := stringOf(result, "output"); s != "" {
			return s
		}
		return ""
	}
	return ""
}

func failuresOf(caseObj map[string]any) []string {
	out := stringList(caseObj["failures"])
	if errText := stringOf(caseObj, "error"); errText != "" {
		out = append(out, "case error: "+errText)
	}
	for _, turn := range mapSlice(caseObj["turns"]) {
		out = append(out, stringList(turn["failures"])...)
		if runnerError := stringOf(turn, "runner_error"); runnerError != "" {
			out = append(out, "runner error: "+runnerError)
		}
	}
	return out
}

// expectedValues is every accepted answer string for a case.
func expectedValues(spec map[string]any) []string {
	var values []string
	for _, turn := range mapSlice(spec["turns"]) {
		expect := mapOf(turn, "expect")
		if v, ok := expect["output_equals"]; ok && v != nil {
			values = append(values, PyStr(v))
		}
		for _, v := range sliceOf(expect, "output_equals_any") {
			values = append(values, PyStr(v))
		}
		if v, ok := expect["expected_number"]; ok && v != nil {
			if f, isNum := numberValue(v); isNum {
				values = append(values, lab.PyFloat(f).String())
			}
		}
	}
	return values
}

// salientCandidates is where a reply's committed value plausibly sits: either
// end, or after a marker. The middle is deliberately not searched: on a case
// whose decoy is itself a number, position is the only thing separating a
// commitment from a mention.
func salientCandidates(answer string) []string {
	trimmed := strings.TrimSpace(answer)
	if trimmed == "" {
		return nil
	}
	var lines []string
	for _, line := range lab.SplitLines(trimmed) {
		if strings.TrimSpace(line) != "" {
			lines = append(lines, strings.TrimSpace(line))
		}
	}
	var out []string
	add := func(line string) {
		line = strings.TrimSpace(line)
		if line == "" {
			return
		}
		out = append(out, line)
		parts := strings.Fields(line)
		if len(parts) > 1 {
			out = append(out, parts[0], parts[len(parts)-1])
		}
	}
	if len(lines) > 0 {
		add(lines[0])
		add(lines[len(lines)-1])
	}
	lowered := strings.ToLower(trimmed)
	for _, marker := range answerMarker {
		if index := strings.LastIndex(lowered, marker); index >= 0 {
			add(trimmed[index+len(marker):])
		}
	}
	return out
}

// carriesExpected is true when an accepted value sits at a salient position but
// is not the whole reply.
func carriesExpected(answer string, spec map[string]any) bool {
	normalized := normalize(answer)
	if normalized == "" {
		return false
	}
	var candidates []string
	for _, c := range salientCandidates(answer) {
		candidates = append(candidates, normalize(c))
	}
	for _, want := range expectedValues(spec) {
		wantN := normalize(want)
		if wantN == "" || normalized == wantN {
			continue
		}
		for _, candidate := range candidates {
			if candidate == wantN {
				return true
			}
		}
		target, err := strconv.ParseFloat(strings.ReplaceAll(wantN, ",", ""), 64)
		if err != nil {
			continue
		}
		for _, candidate := range candidates {
			found := gateNumberRe.FindString(strings.TrimLeft(candidate, "$€£¥"))
			if found == "" {
				continue
			}
			value, err := strconv.ParseFloat(strings.ReplaceAll(found, ",", ""), 64)
			if err != nil {
				continue
			}
			if absFloat(value-target) <= 0.011 {
				return true
			}
		}
	}
	return false
}

// classify assigns one layer to a non-passing case. First match wins.
func classify(caseObj, spec map[string]any) string {
	if invalid, _ := caseObj["invalid"].(bool); invalid {
		return "infra"
	}
	blob := strings.ToLower(strings.Join(failuresOf(caseObj), " | "))
	if containsAny(blob, infraMarkers) {
		return "infra"
	}
	if containsAny(blob, protocolMarkers) {
		return "protocol"
	}
	if containsAny(blob, closeoutMarkers) {
		return "closeout"
	}
	if containsAny(blob, toolchoiceMarkers) {
		return "toolchoice"
	}
	answer := answerOf(caseObj)
	if normalize(answer) == "" && blob != "" {
		// Ran out of turns without ever committing an answer.
		return "closeout"
	}
	if carriesExpected(answer, spec) {
		return "format"
	}
	return "capability"
}

// decoyHits reports which declared decoys this answer matched. An unhit trap
// may be inert.
func decoyHits(caseObj, spec map[string]any) []string {
	tags := mapOf(spec, "tags")
	decoys := mapOf(tags, "trap_decoys")
	answer := normalize(answerOf(caseObj))
	if answer == "" {
		return nil
	}
	var hits []string
	traps := make([]string, 0, len(decoys))
	for trap := range decoys {
		traps = append(traps, trap)
	}
	sort.Strings(traps)
	for _, trap := range traps {
		value := decoys[trap]
		if value == nil {
			continue
		}
		want := normalize(PyStr(value))
		if want == "" {
			continue
		}
		if answer == want || strings.HasPrefix(answer, want+" ") || containsString(strings.Fields(answer), want) {
			hits = append(hits, trap)
			continue
		}
		target, err := strconv.ParseFloat(strings.ReplaceAll(want, ",", ""), 64)
		if err != nil {
			continue
		}
		cleaned := strings.ReplaceAll(strings.ReplaceAll(answer, "$", ""), "€", "")
		for _, found := range gateNumberRe.FindAllString(cleaned, -1) {
			value, err := strconv.ParseFloat(strings.ReplaceAll(found, ",", ""), 64)
			if err != nil {
				continue
			}
			if absFloat(value-target) <= 0.011 {
				hits = append(hits, trap)
				break
			}
		}
	}
	return hits
}

// GateArgs are the `run gate` flags.
type GateArgs struct {
	Runs  []string
	Label string
	JSON  string
}

// RunGate is the `run gate` command.
func RunGate(args GateArgs) int {
	label := args.Label
	if label == "" {
		label = baseName(args.Runs[0])
	}
	report, err := AnalyzeGate(args.Runs, label)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	renderGate(report)
	if args.JSON != "" {
		if err := WriteJSONFile(args.JSON, report); err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		fmt.Printf("   -> %s\n", args.JSON)
	}
	return 0
}

// AnalyzeGate is capability_gate.analyze.
func AnalyzeGate(runDirs []string, label string) (map[string]any, error) {
	layers := map[string]int{}
	scored, passed, voided := 0, 0, 0

	type caseStat struct {
		pass   int
		runs   int
		layers map[string]int
	}
	perCase := map[string]*caseStat{}
	var perCaseOrder []string
	decoyTotal := map[string]int{}
	decoyHit := map[string]int{}

	for _, runDir := range runDirs {
		summary, err := LoadJSONFile(runDir+"/summary.json", true)
		if err != nil {
			return nil, err
		}
		manifest, err := LoadJSONFile(runDir+"/run.json", true)
		if err != nil {
			return nil, err
		}
		specs := map[string]map[string]any{}
		for _, c := range mapSlice(manifest["cases"]) {
			if id, ok := c["id"].(string); ok {
				specs[id] = c
			}
		}
		for _, caseObj := range mapSlice(summary["cases"]) {
			caseID := stringOf(caseObj, "id")
			spec := specs[caseID]
			if spec == nil {
				spec = map[string]any{}
			}
			entry, seen := perCase[caseID]
			if !seen {
				entry = &caseStat{layers: map[string]int{}}
				perCase[caseID] = entry
				perCaseOrder = append(perCaseOrder, caseID)
			}
			if invalid, _ := caseObj["invalid"].(bool); invalid {
				voided++
				layers["infra"]++
				entry.layers["infra"]++
				continue
			}
			entry.runs++
			scored++
			if casePassed, _ := caseObj["passed"].(bool); casePassed {
				passed++
				entry.pass++
			} else {
				layer := classify(caseObj, spec)
				layers[layer]++
				entry.layers[layer]++
			}
			tags := mapOf(spec, "tags")
			for trap, value := range mapOf(tags, "trap_decoys") {
				if value != nil {
					decoyTotal[trap]++
				}
			}
			for _, trap := range decoyHits(caseObj, spec) {
				decoyHit[trap]++
			}
		}
	}

	totalAttempts := scored + voided
	protocolRate := 0.0
	closeoutRate := 0.0
	if scored > 0 {
		protocolRate = float64(layers["protocol"]) / float64(scored)
		closeoutRate = float64(layers["closeout"]) / float64(scored)
	}
	measurable := protocolRate <= protocolCeiling && closeoutRate <= closeoutCeiling

	layerOut := map[string]any{}
	for _, layer := range Layers {
		layerOut[layer] = layers[layer]
	}
	decoysOut := map[string]any{}
	traps := make([]string, 0, len(decoyTotal))
	for trap := range decoyTotal {
		traps = append(traps, trap)
	}
	sort.Strings(traps)
	for _, trap := range traps {
		rate := float64(decoyHit[trap]) / float64(decoyTotal[trap])
		decoysOut[trap] = map[string]any{
			"exposed": decoyTotal[trap], "hit": decoyHit[trap],
			"hit_rate": lab.RoundHalfEven(rate, 4),
		}
	}
	perCaseOut := map[string]any{}
	sortedCases := append([]string(nil), perCaseOrder...)
	sort.Strings(sortedCases)
	for _, cid := range sortedCases {
		entry := perCase[cid]
		perCaseOut[cid] = map[string]any{
			"pass": entry.pass, "runs": entry.runs, "layers": toAnyMap(entry.layers),
		}
	}

	var passRate any
	if scored > 0 {
		passRate = lab.RoundHalfEven(float64(passed)/float64(scored), 4)
	}
	return map[string]any{
		"version":               GateVersion,
		"label":                 label,
		"runs":                  toAnySlice(runDirs),
		"attempts":              totalAttempts,
		"voided":                voided,
		"scored":                scored,
		"passed":                passed,
		"pass_rate":             passRate,
		"layers":                layerOut,
		"protocol_rate":         lab.RoundHalfEven(protocolRate, 4),
		"closeout_rate":         lab.RoundHalfEven(closeoutRate, 4),
		"capability_measurable": measurable,
		"decoys":                decoysOut,
		"per_case":              perCaseOut,
	}, nil
}

func renderGate(report map[string]any) {
	runList := sliceOf(report, "runs")
	fmt.Printf("== %s  (%d run(s))\n", PyStr(report["label"]), len(runList))
	scored, _ := intOf(report["scored"])
	if scored > 0 {
		rate, _ := numberValue(report["pass_rate"])
		fmt.Printf("   官方通过 %s/%d = %s\n", PyStr(report["passed"]), scored, pct(rate, 1))
	} else {
		fmt.Println("   no scored cases")
	}
	if voided, _ := intOf(report["voided"]); voided > 0 {
		fmt.Printf("   作废(上游中断，不计分母) %d\n", voided)
	}
	fmt.Println("   失败分层:")
	layers := mapOf(report, "layers")
	for _, layer := range Layers {
		count, _ := intOf(layers[layer])
		if count > 0 {
			fmt.Printf("      %-11s %d\n", layer, count)
		}
	}
	measurable, _ := report["capability_measurable"].(bool)
	verdict := "不可当能力读数 —— 分数被协议/收尾主导"
	if measurable {
		verdict = "可以当能力读数"
	}
	protocolRate, _ := numberValue(report["protocol_rate"])
	closeoutRate, _ := numberValue(report["closeout_rate"])
	fmt.Printf("   判定: %s  (protocol %s, closeout %s)\n",
		verdict, pct(protocolRate, 1), pct(closeoutRate, 1))
	if decoys := mapOf(report, "decoys"); len(decoys) > 0 {
		fmt.Println("   陷阱 decoy 命中率:")
		traps := make([]string, 0, len(decoys))
		for trap := range decoys {
			traps = append(traps, trap)
		}
		sort.Strings(traps)
		for _, trap := range traps {
			stat := mapOf(decoys, trap)
			hit, _ := intOf(stat["hit"])
			exposed, _ := intOf(stat["exposed"])
			rate, _ := numberValue(stat["hit_rate"])
			note := ""
			if hit == 0 {
				note = "  <- 从未命中，陷阱可能是死的"
			}
			fmt.Printf("      %-16s %3d/%-3d = %s%s\n", trap, hit, exposed, pctWidth(rate, 5, 1), note)
		}
	}
}

func containsAny(text string, markers []string) bool {
	for _, marker := range markers {
		if strings.Contains(text, marker) {
			return true
		}
	}
	return false
}

func containsString(list []string, want string) bool {
	for _, item := range list {
		if item == want {
			return true
		}
	}
	return false
}

func absFloat(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}

func toAnyMap(m map[string]int) map[string]any {
	out := make(map[string]any, len(m))
	for k, v := range m {
		out[k] = v
	}
	return out
}

// pct is Python's {rate:.N%}: the whole formatted string, percent sign
// included, is what width applies to.
func pct(rate float64, prec int) string {
	return strconv.FormatFloat(100*rate, 'f', prec, 64) + "%"
}

func pctWidth(rate float64, width, prec int) string {
	s := pct(rate, prec)
	for len(s) < width {
		s = " " + s
	}
	return s
}
