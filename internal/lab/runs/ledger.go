package runs

import (
	"fmt"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Append-only scoring ledger for workbank runs.
//
// ingest reads run.json + summary.json from a run directory and appends one
// row per run to runs.jsonl and one row per run x case x k to cases.jsonl.
// Ingest is idempotent: a run row is skipped when (run_id, k_index) already
// exists, and a case row when (run_id, case_id, k_index) already exists. The
// write is an append and never a rewrite, because several sweeps can ingest
// concurrently and a rewrite would drop their rows (P10).
//
// matrix aggregates the two files into a markdown table whose rows are
// model x wire_hash.

// DefaultLedgerDir is where the ledgers live, relative to the repository root.
func DefaultLedgerDir() string {
	return filepath.Join(lab.RepoRoot(), "bench", "workbank", "ledger")
}

func runsJSONL(ledgerDir string) string  { return filepath.Join(ledgerDir, "runs.jsonl") }
func casesJSONL(ledgerDir string) string { return filepath.Join(ledgerDir, "cases.jsonl") }

// IngestArgs are the `run ledger ingest` flags.
type IngestArgs struct {
	RunDir      string
	ConfigName  string
	KIndex      int
	BankVersion string
	LedgerDir   string
}

// MatrixArgs are the `run ledger matrix` flags.
type MatrixArgs struct {
	BankVersion string
	LedgerDir   string
}

// RunLedgerIngest is `run ledger ingest`.
func RunLedgerIngest(args IngestArgs) int {
	runDir := strings.TrimRight(args.RunDir, "/")
	if runDir == "" {
		runDir = "."
	}
	manifest, err := LoadJSONFile(filepath.Join(args.RunDir, "run.json"), true)
	if err != nil {
		fmt.Fprintf(stderr, "error: %s\n", err)
		return 2
	}
	summary, err := LoadJSONFile(filepath.Join(args.RunDir, "summary.json"), true)
	if err != nil {
		fmt.Fprintf(stderr, "error: %s\n", err)
		return 2
	}
	if manifest == nil || summary == nil {
		fmt.Fprintln(stderr, "error: run.json/summary.json must be JSON objects")
		return 2
	}

	runID := stringOf(manifest, "run_id")
	if runID == "" {
		runID = stringOf(summary, "run_id")
	}
	tagsByID := map[string]map[string]any{}
	for _, c := range mapSlice(manifest["cases"]) {
		if id, ok := c["id"].(string); ok {
			tagsByID[id] = mapOf(c, "tags")
		}
	}

	existingRuns := ReadJSONL(runsJSONL(args.LedgerDir))
	existingCases := ReadJSONL(casesJSONL(args.LedgerDir))
	caseKeys := map[string]bool{}
	for _, r := range existingCases {
		caseKeys[ingestKey(stringOf(r, "run_id"), stringOf(r, "case_id"), intField(r, "k_index"))] = true
	}

	var newCaseRows []map[string]any
	totalCases := 0
	for _, sc := range mapSlice(summary["cases"]) {
		cid, ok := sc["id"].(string)
		if !ok {
			continue
		}
		totalCases++
		if caseKeys[ingestKey(runID, cid, args.KIndex)] {
			continue
		}
		newCaseRows = append(newCaseRows, buildCaseRow(runDir, sc, tagsByID, args, runID))
	}
	skippedCases := totalCases - len(newCaseRows)

	runExists := false
	for _, r := range existingRuns {
		if stringOf(r, "run_id") == runID && intField(r, "k_index") == args.KIndex {
			runExists = true
		}
	}
	var newRunRow map[string]any
	if !runExists {
		newRunRow = buildRunRow(manifest, summary, newCaseRows, args)
	}

	for _, row := range newCaseRows {
		if err := AppendJSONL(casesJSONL(args.LedgerDir), row); err != nil {
			fmt.Fprintf(stderr, "error: %s\n", err)
			return 2
		}
	}
	if newRunRow != nil {
		if err := AppendJSONL(runsJSONL(args.LedgerDir), newRunRow); err != nil {
			fmt.Fprintf(stderr, "error: %s\n", err)
			return 2
		}
	}

	fmt.Printf("run_id=%s config=%s k=%d\n", runID, args.ConfigName, args.KIndex)
	if newRunRow != nil {
		fmt.Println("runs.jsonl: +1 row")
	} else {
		fmt.Println("runs.jsonl: skipped (already ingested)")
	}
	if skippedCases < 0 {
		skippedCases = 0
	}
	fmt.Printf("cases.jsonl: +%d rows (%d already present)\n", len(newCaseRows), skippedCases)
	return 0
}

func ingestKey(runID, caseID string, k int) string {
	return runID + "\x00" + caseID + "\x00" + strconv.Itoa(k)
}

func intField(m map[string]any, key string) int {
	i, _ := intOf(m[key])
	return i
}

func deriveEndpoint(model map[string]any) any {
	if model == nil {
		return nil
	}
	var parts []string
	for _, key := range []string{"provider", "completion"} {
		if v, ok := model[key]; ok && truthy(v) {
			parts = append(parts, PyStr(v))
		}
	}
	if len(parts) == 0 {
		return nil
	}
	return strings.Join(parts, "/")
}

// protocolInvalidRate is 1 - the decision protocol validity rate for the run's
// channel. A missing score yields nil instead of crashing.
func protocolInvalidRate(metrics map[string]any, channel string) any {
	if metrics == nil {
		return nil
	}
	keys := []string{"decision_protocol_validity", "protocol_validity"}
	if channel == "native" {
		keys = []string{"native_protocol_validity"}
	}
	for _, key := range keys {
		score := mapOf(metrics, key)
		if score == nil {
			continue
		}
		total, hasTotal := numberValue(score["total"])
		correct, hasCorrect := numberValue(score["correct"])
		if hasTotal && total > 0 && hasCorrect {
			return lab.PyFloat(lab.RoundHalfEven(clamp01(1-correct/total), 6))
		}
		if rate, hasRate := numberValue(score["rate"]); hasRate {
			return lab.PyFloat(lab.RoundHalfEven(clamp01(1-rate), 6))
		}
	}
	return nil
}

func clamp01(x float64) float64 {
	if x < 0 {
		return 0
	}
	if x > 1 {
		return 1
	}
	return x
}

// deriveChannel maps model.completion to the step channel: chat-completions
// runs use structured provider tool calls, everything else is the text wire.
func deriveChannel(model map[string]any) string {
	if model != nil && stringOf(model, "completion") == "chat-completions" {
		return "native"
	}
	return "text"
}

func groupRates(rows []map[string]any, key string) map[string]any {
	out := map[string]any{}
	for _, row := range rows {
		val := row[key]
		name := "unknown"
		if val != nil {
			name = PyStr(val)
		}
		group, _ := out[name].(map[string]any)
		if group == nil {
			group = map[string]any{"passed": 0, "total": 0}
			out[name] = group
		}
		group["total"] = group["total"].(int) + 1
		if passed, _ := row["passed"].(bool); passed {
			group["passed"] = group["passed"].(int) + 1
		}
	}
	for _, groupAny := range out {
		group := groupAny.(map[string]any)
		total := group["total"].(int)
		if total > 0 {
			group["rate"] = lab.RoundHalfEven(float64(group["passed"].(int))/float64(total), 4)
		} else {
			group["rate"] = nil
		}
	}
	return out
}

// trapHit returns the trap id whose decoy value equals the final output.
func trapHit(finalOutput any, decoys map[string]any) any {
	text, ok := finalOutput.(string)
	if decoys == nil || !ok {
		return nil
	}
	out := strings.TrimSpace(text)
	if out == "" {
		return nil
	}
	outNum, hasNum := parseFloatLoose(out)
	traps := make([]string, 0, len(decoys))
	for trap := range decoys {
		traps = append(traps, trap)
	}
	sort.Strings(traps)
	for _, trap := range traps {
		val := decoys[trap]
		if val == nil {
			continue
		}
		if s, isStr := val.(string); isStr && out == s {
			return trap
		}
		if !hasNum {
			continue
		}
		if f, isNum := numberValue(val); isNum {
			if absFloat(outNum-f) <= 1e-6 {
				return trap
			}
		} else if s, isStr := val.(string); isStr {
			if f, err := strconv.ParseFloat(s, 64); err == nil && absFloat(outNum-f) <= 1e-6 {
				return trap
			}
		}
	}
	return nil
}

func parseFloatLoose(s string) (float64, bool) {
	f, err := strconv.ParseFloat(s, 64)
	return f, err == nil
}

func buildRunRow(manifest, summary map[string]any, caseRows []map[string]any, args IngestArgs) map[string]any {
	model := mapOf(manifest, "model")
	harness := mapOf(manifest, "harness")
	sampling, _ := manifest["sampling"].(map[string]any)
	metrics := mapOf(summary, "metrics")
	channel := deriveChannel(model)
	date := stringOf(manifest, "completed_at")
	if date == "" {
		date = stringOf(manifest, "started_at")
	}
	if date == "" {
		date = nowUTCIso()
	}
	var passMean any
	task := mapOf(metrics, "task_success")
	if rate, ok := numberValue(task["rate"]); ok {
		passMean = lab.RoundHalfEven(rate, 6)
	} else if len(caseRows) > 0 {
		passed := 0
		for _, r := range caseRows {
			if p, _ := r["passed"].(bool); p {
				passed++
			}
		}
		passMean = lab.RoundHalfEven(float64(passed)/float64(len(caseRows)), 6)
	}
	var scoredCases any
	if task != nil {
		scoredCases = task["total"]
	}
	invalidCases, _ := intOf(metrics["invalid_cases"])
	rescueAssisted := 0
	for _, r := range caseRows {
		if p, _ := r["passed"].(bool); p {
			if rescues, ok := intOf(r["rescues"]); ok && rescues > 0 {
				rescueAssisted++
			}
		}
	}
	runID := stringOf(manifest, "run_id")
	if runID == "" {
		runID = stringOf(summary, "run_id")
	}
	return map[string]any{
		"run_id":                     nilIfEmpty(runID),
		"date":                       date,
		"config_name":                args.ConfigName,
		"k_index":                    args.KIndex,
		"model_id":                   model["identifier"],
		"model_fingerprint":          model["fingerprint"],
		"state_sha256":               harness["state_sha256"],
		"wire_profile":               harness["wire_profile"],
		"wire_hash":                  harness["wire_hash"],
		"harness_version":            harness["version"],
		"scorer_version":             harness["scorer_version"],
		"tool_catalog":               harness["tool_catalog"],
		"tool_catalog_hash":          harness["tool_catalog_hash"],
		"sampling":                   sampling,
		"channel":                    channel,
		"case_parallelism":           harness["case_parallelism"],
		"max_steps":                  harness["max_steps"],
		"duplicate_replay_limit":     harness["duplicate_replay_limit"],
		"duplicate_rescue_threshold": harness["duplicate_rescue_threshold"],
		"same_tool_rescue_limit":     harness["same_tool_rescue_limit"],
		"endpoint":                   deriveEndpoint(model),
		"pass_mean":                  passMean,
		"scored_cases":               scoredCases,
		"invalid_cases":              invalidCases,
		"pass_all_k":                 nil,
		"by_level":                   groupRates(caseRows, "level"),
		"by_scenario":                groupRates(caseRows, "scenario"),
		"protocol_invalid_rate":      protocolInvalidRate(metrics, channel),
		"rescue_assisted_passes":     rescueAssisted,
		"bank_version":               nilIfEmpty(args.BankVersion),
	}
}

func buildCaseRow(runDir string, summaryCase map[string]any, tagsByID map[string]map[string]any, args IngestArgs, runID string) map[string]any {
	caseID := stringOf(summaryCase, "id")
	tags := mapOf(summaryCase, "tags")
	if len(tags) == 0 {
		tags = tagsByID[caseID]
	}
	if tags == nil {
		tags = map[string]any{}
	}
	turns := mapSlice(summaryCase["turns"])
	failures := len(stringList(summaryCase["failures"]))
	for _, t := range turns {
		failures += len(stringList(t["failures"]))
	}
	toolCalls := summaryCase["tool_calls"]
	refCalls := tags["ref_calls"]
	var redundancy any
	if tc, ok := numberValue(toolCalls); ok && isNumber(toolCalls) {
		if rc, ok := numberValue(refCalls); ok && isNumber(refCalls) && rc != 0 {
			redundancy = lab.RoundHalfEven(tc/rc, 4)
		}
	}
	maxTurnsHit := false
	for _, t := range turns {
		result := mapOf(t, "result")
		if stringOf(result, "forced_answer_reason") != "" {
			maxTurnsHit = true
		}
		if strings.Contains(strings.ToLower(stringOf(t, "runner_error")), "budget") {
			maxTurnsHit = true
		}
	}
	var finalOutput any
	if len(turns) > 0 {
		finalOutput = mapOf(turns[len(turns)-1], "result")["output"]
	}
	version := 1
	if v, ok := intOf(tags["version"]); ok {
		version = v
	}
	var toolCallsOut any
	if _, ok := numberValue(toolCalls); ok && isNumber(toolCalls) {
		toolCallsOut = toolCalls
	}
	var refCallsOut any
	if _, ok := numberValue(refCalls); ok && isNumber(refCalls) {
		refCallsOut = refCalls
	}
	var rescuesOut any
	if r, ok := numberValue(summaryCase["rescues"]); ok && isNumber(summaryCase["rescues"]) {
		rescuesOut = summaryCase["rescues"]
		_ = r
	}
	return map[string]any{
		"run_id":            nilIfEmpty(runID),
		"config_name":       args.ConfigName,
		"k_index":           args.KIndex,
		"case_id":           caseID,
		"case_version":      version,
		"family":            tags["family"],
		"level":             tags["level"],
		"scenario":          tags["scenario"],
		"passed":            truthy(summaryCase["passed"]),
		"failures":          failures,
		"tool_calls":        toolCallsOut,
		"ref_calls":         refCallsOut,
		"redundancy":        redundancy,
		"max_turns_hit":     maxTurnsHit,
		"duplicate_rejects": summaryCase["duplicate_rejects"],
		"rescues":           rescuesOut,
		"trap_hit":          trapHit(finalOutput, mapOf(tags, "trap_decoys")),
		"trace_ref":         fmt.Sprintf("%s#%s", runDir, caseID),
	}
}

func nilIfEmpty(s string) any {
	if s == "" {
		return nil
	}
	return s
}

// RunLedgerMatrix is `run ledger matrix`.
func RunLedgerMatrix(args MatrixArgs) int {
	runs := ReadJSONL(runsJSONL(args.LedgerDir))
	cases := ReadJSONL(casesJSONL(args.LedgerDir))
	if args.BankVersion != "" {
		var filtered []map[string]any
		for _, r := range runs {
			if stringOf(r, "bank_version") == args.BankVersion {
				filtered = append(filtered, r)
			}
		}
		runs = filtered
	}
	runIDs := map[string]bool{}
	for _, r := range runs {
		runIDs[stringOf(r, "run_id")] = true
	}
	var keptCases []map[string]any
	for _, c := range cases {
		if runIDs[stringOf(c, "run_id")] {
			keptCases = append(keptCases, c)
		}
	}
	if len(runs) == 0 {
		if args.BankVersion != "" {
			fmt.Printf("no runs in ledger for bank_version %s\n", args.BankVersion)
		} else {
			fmt.Println("no runs in ledger")
		}
		return 0
	}

	groups := map[string]map[string]bool{}
	for _, r := range runs {
		key := PyStr(r["model_id"]) + "\x00" + strOrNull(r["wire_hash"])
		if groups[key] == nil {
			groups[key] = map[string]bool{}
		}
		groups[key][stringOf(r, "run_id")] = true
	}
	keys := make([]string, 0, len(groups))
	for k := range groups {
		keys = append(keys, k)
	}
	sort.Strings(keys)

	fmt.Println("# workbank matrix")
	fmt.Println()
	fmt.Println("| model | wire | runs | pass | L0 | L1 | L2 | L3 | rescue-assisted |")
	fmt.Println("|---|---|---|---|---|---|---|---|---|")
	for _, key := range keys {
		parts := strings.SplitN(key, "\x00", 2)
		modelID, wireHash := parts[0], parts[1]
		members := groups[key]
		var rows []map[string]any
		for _, c := range keptCases {
			if members[stringOf(c, "run_id")] {
				rows = append(rows, c)
			}
		}
		passed := 0
		rescueAssisted := 0
		for _, c := range rows {
			if p, _ := c["passed"].(bool); p {
				passed++
				if rescues, ok := intOf(c["rescues"]); ok && rescues > 0 {
					rescueAssisted++
				}
			}
		}
		byLevel := groupRates(rows, "level")
		var levelCells []string
		for _, level := range []string{"L0", "L1", "L2", "L3"} {
			group, _ := byLevel[level].(map[string]any)
			if group == nil {
				levelCells = append(levelCells, "-")
				continue
			}
			levelCells = append(levelCells, fmtRate(group["passed"].(int), group["total"].(int)))
		}
		shownWire := wireHash
		if len(wireHash) > 8 {
			shownWire = wireHash[:8]
		}
		fmt.Printf("| %s | %s | %d | %s | %s | %d |\n",
			modelID, shownWire, len(members), fmtRate(passed, len(rows)),
			strings.Join(levelCells, " | "), rescueAssisted)
	}
	return 0
}

func strOrNull(v any) string {
	if v == nil {
		return "null"
	}
	return PyStr(v)
}

func fmtRate(passed, total int) string {
	if total == 0 {
		return "-"
	}
	return fmt.Sprintf("%.1f%% (%d/%d)", 100.0*float64(passed)/float64(total), passed, total)
}

func nowUTCIso() string {
	return time.Now().UTC().Format("2006-01-02T15:04:05Z")
}
