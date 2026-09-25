package bank

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// requiredTags are the tag keys every case must carry.
var requiredTags = []string{
	"scenario", "task_type", "traps", "trap_decoys", "axes", "level",
	"ref_calls", "fixture_bytes", "status", "version", "author", "reviewer",
}

var (
	caseIDRe  = regexp.MustCompile(`^([a-z]+)-(\d{4})$`)
	canaryRe  = regexp.MustCompile(`WORKBANK-CANARY-[0-9a-f]{8}`)
	notesSecs = []string{"Traps", "Reference solution", "Why the answer is unique"}
)

// lintCtx is the vocabulary the checks are run against (lint.py's Ctx).
type lintCtx struct {
	scenarios     []string
	abbrev        map[string]string
	taskTypes     map[string][]string
	traps         map[string]trapEntry
	axes          map[string]struct{}
	levels        map[string]struct{}
	statuses      map[string]struct{}
	tools         []string
	contracts     map[string]string
	contractOrder []string
	scenarioTraps map[string][]string
}

type trapEntry struct {
	axis           string
	forbiddenWords []string
	scenarios      []string
}

// runLint ports lint.py. Violations are one JSON object per line on stdout,
// the summary goes to stderr, and the exit code is 1 when anything remains.
func runLint(args []string) int {
	fs := newFlagSet("bank lint",
		"Validate workbank cases (schema v5) against docs/tag-vocab.json and the authoring rules.")
	casesRoot := fs.String("cases", DefaultCases(), "cases root directory")
	var caseArgs stringList
	fs.Var(&caseArgs, "case", "single case directory containing case.json (repeatable; overrides --cases)")
	fix := fs.Bool("fix", false, "backfill tags.fixture_bytes from files content (nothing else is modified)")
	vocabPath := fs.String("vocab", DefaultVocab(), "tag vocabulary file")
	if err := fs.Parse(args); err != nil {
		return 2
	}

	ctx, err := loadLintCtx(*vocabPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}

	type caseJob struct {
		dir      string
		relParts []string
	}
	var jobs []caseJob
	if len(caseArgs) > 0 {
		for _, item := range caseArgs {
			abs, err := filepath.Abs(item)
			if err != nil || !fileExists(filepath.Join(abs, "case.json")) {
				fmt.Fprintf(os.Stderr, "error: --case %s: no case.json inside\n", item)
				return 2
			}
			jobs = append(jobs, caseJob{dir: abs, relParts: []string{filepath.Base(filepath.Dir(abs)), filepath.Base(abs)}})
		}
	} else {
		root, err := filepath.Abs(*casesRoot)
		if err != nil || !isDir(root) {
			fmt.Fprintf(os.Stderr, "error: --cases %s: not a directory\n", *casesRoot)
			return 2
		}
		paths, err := caseFilePaths(root)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %s\n", err)
			return 2
		}
		for _, path := range paths {
			dir := filepath.Dir(path)
			rel, err := filepath.Rel(root, dir)
			if err != nil {
				rel = dir
			}
			jobs = append(jobs, caseJob{dir: dir, relParts: strings.Split(filepath.ToSlash(rel), "/")})
		}
	}

	var violations []*lab.OrderedMap
	var fixedNotes []string
	seenIDs := map[string]string{}
	checked := 0
	for _, job := range jobs {
		caseObj, err := loadCaseJSON(filepath.Join(job.dir, "case.json"))
		if err != nil {
			violations = append(violations, violation(filepath.Base(job.dir), "case_json",
				"case.json does not parse: "+err.Error()))
			continue
		}
		checked++
		cid, _ := caseObj["id"].(string)
		if cid == "" {
			cid = filepath.Base(job.dir)
		}
		if prev, dup := seenIDs[cid]; dup {
			violations = append(violations, violation(cid, "id.unique", "id already used by "+prev))
		} else {
			seenIDs[cid] = job.dir
		}
		checkCase(job.dir, caseObj, ctx, job.relParts, &violations, &fixedNotes, *fix)
	}

	for _, note := range fixedNotes {
		fmt.Fprintf(os.Stderr, "fixed: %s\n", note)
	}
	for _, item := range violations {
		line, err := lab.EncodeOrderedJSON(item, lab.EncodeOptions{SpacedSeparators: true})
		if err == nil {
			fmt.Println(string(line))
		}
	}
	fmt.Fprintf(os.Stderr, "%d case(s) checked, %d violation(s)\n", checked, len(violations))
	if len(violations) > 0 {
		return 1
	}
	return 0
}

func violation(cid, rule, detail string) *lab.OrderedMap {
	m := lab.NewOrderedMap()
	m.Set("case_id", cid)
	m.Set("rule", rule)
	m.Set("detail", detail)
	return m
}

func checkCase(caseDir string, caseObj map[string]any, ctx *lintCtx, relParts []string,
	violations *[]*lab.OrderedMap, fixedNotes *[]string, fix bool) {

	cid, _ := caseObj["id"].(string)
	if cid == "" {
		cid = filepath.Base(caseDir)
	}
	tags := tagsOf(caseObj)
	bad := func(rule, detail string) {
		*violations = append(*violations, violation(cid, rule, detail))
	}

	// (a) required tag keys + enums
	for _, key := range requiredTags {
		if _, ok := tags[key]; !ok {
			bad("tags.required", "missing tags."+key)
		}
	}
	scenario, scenarioIsString := tags["scenario"].(string)
	if !containsString(ctx.scenarios, scenario) {
		bad("tags.enum", fmt.Sprintf("scenario %s not in vocabulary", pyReprValue(tags["scenario"])))
	}
	taskType := tags["task_type"]
	if allowed, ok := ctx.taskTypes[scenario]; ok && !containsString(allowed, asString(taskType)) {
		bad("tags.enum", fmt.Sprintf("task_type %s not allowed for scenario %s",
			pyReprValue(taskType), pyReprValue(tags["scenario"])))
	}
	for _, axis := range anySlice(tags["axes"]) {
		if _, ok := ctx.axes[asString(axis)]; !ok {
			bad("tags.enum", fmt.Sprintf("axis %s not in vocabulary", pyReprValue(axis)))
		}
	}
	for _, trap := range anySlice(tags["traps"]) {
		if _, ok := ctx.traps[asString(trap)]; !ok {
			bad("tags.enum", fmt.Sprintf("trap %s not in vocabulary", pyReprValue(trap)))
		}
	}
	if _, ok := ctx.levels[asString(tags["level"])]; !ok {
		bad("tags.enum", fmt.Sprintf("level %s not in vocabulary", pyReprValue(tags["level"])))
	}
	if _, ok := ctx.statuses[asString(tags["status"])]; !ok {
		bad("tags.enum", fmt.Sprintf("status %s not in vocabulary", pyReprValue(tags["status"])))
	}

	// (f) fixture_bytes — with --fix, backfill from the files content first
	computedBytes := fixtureBytesOf(caseObj)
	storedBytes, hasStored := tags["fixture_bytes"]
	if !numbersEqual(storedBytes, hasStored, computedBytes) {
		if fix {
			*fixedNotes = append(*fixedNotes,
				fmt.Sprintf("%s: fixture_bytes %s -> %d", cid, pyReprValue(storedBytes), computedBytes))
			tags["fixture_bytes"] = json.Number(fmt.Sprintf("%d", computedBytes))
			writeCaseIndented(filepath.Join(caseDir, "case.json"), caseObj)
		} else {
			bad("fixture_bytes", fmt.Sprintf("tags.fixture_bytes is %s, files sum to %d bytes",
				pyReprValue(storedBytes), computedBytes))
		}
	}

	// (b) prompts: tool names + forbidden words of declared traps and of traps
	// intrinsic to this scenario. The mandated answer contract is boilerplate,
	// not author-written task text, and may itself contain a forbidden token
	// ("cannot"), so it is stripped before the scan.
	turns := turnObjects(caseObj)
	prompts := make([]string, 0, len(turns))
	for _, turn := range turns {
		s, _ := turn["prompt"].(string)
		prompts = append(prompts, s)
	}
	var forbiddenTraps []string
	for _, trap := range anySlice(tags["traps"]) {
		forbiddenTraps = append(forbiddenTraps, asString(trap))
	}
	for _, trap := range ctx.scenarioTraps[scenario] {
		if !containsString(forbiddenTraps, trap) {
			forbiddenTraps = append(forbiddenTraps, trap)
		}
	}
	for idx, prompt := range prompts {
		low := strings.ToLower(prompt)
		body := prompt
		for _, key := range ctx.contractOrder {
			contract := ctx.contracts[key]
			if strings.HasSuffix(body, contract) {
				body = body[:len(body)-len(contract)]
				break
			}
		}
		norm := normalizePrompt(body)
		for _, tool := range ctx.tools {
			if strings.Contains(low, tool) {
				bad("prompt.tool_name", fmt.Sprintf("turn %d: tool name %s in prompt", idx+1, pyReprValue(tool)))
			}
		}
		for _, trap := range forbiddenTraps {
			entry, ok := ctx.traps[trap]
			if !ok {
				continue
			}
			for _, word := range entry.forbiddenWords {
				if re := forbiddenPhraseRe(word); re != nil && re.MatchString(norm) {
					bad("prompt.forbidden_word",
						fmt.Sprintf("turn %d: forbidden word %s of %s in prompt", idx+1, pyReprValue(word), trap))
				}
			}
		}
	}

	// (c) answer contract, byte-exact, at the end of the last prompt
	caseExpect, _ := caseObj["expect"].(map[string]any)
	writeCase := false
	if caseExpect != nil {
		writeCase = truthy(caseExpect["files"]) || truthy(caseExpect["run"])
	}
	required := ctx.contracts["unknown"]
	if writeCase {
		required = ctx.contracts["done"]
	}
	if len(prompts) > 0 {
		if !strings.HasSuffix(prompts[len(prompts)-1], required) {
			kind := "UNKNOWN"
			if writeCase {
				kind = "DONE"
			}
			bad("answer_contract", "last turn prompt must end with the exact "+kind+" contract")
		}
	} else {
		bad("answer_contract", "case has no turns")
	}

	// (d) canary
	description, _ := caseObj["description"].(string)
	if !canaryOK(description) {
		bad("canary", "description must end with WORKBANK-CANARY-<8 lowercase hex>")
	}

	// (e) level rule
	nTraps := len(anySlice(tags["traps"]))
	refCalls, refCallsIsInt := intValue(tags["ref_calls"])
	nFiles := len(anyMap(caseObj["files"]))
	multiTurn := len(turns) > 1
	if _, present := tags["ref_calls"]; present && !refCallsIsInt {
		bad("level", fmt.Sprintf("ref_calls must be an integer, got %s", pyReprValue(tags["ref_calls"])))
	} else if refCallsIsInt {
		valid := allowedLevels(nTraps, refCalls, nFiles, multiTurn)
		if _, ok := valid[asString(tags["level"])]; !ok {
			bad("level", fmt.Sprintf("declared %s but traps=%d, ref_calls=%d, files=%d, multi_turn=%s allows %s",
				pyReprValue(tags["level"]), nTraps, refCalls, nFiles, pyStrValue(multiTurn), sortedListOr(valid, "no level")))
		}
	}

	// (g) trap_decoys present and != expected answer (null allowed for write cases)
	decoys := anyMap(tags["trap_decoys"])
	var expectedAnswers []any
	for _, turn := range turns {
		texp, _ := turn["expect"].(map[string]any)
		if v, ok := texp["expected_number"]; ok {
			expectedAnswers = append(expectedAnswers, v)
		}
		if v, ok := texp["output_equals"]; ok {
			expectedAnswers = append(expectedAnswers, v)
		}
		if anyOf, ok := texp["output_equals_any"].([]any); ok {
			expectedAnswers = append(expectedAnswers, anyOf...)
		}
	}
	for _, trapAny := range anySlice(tags["traps"]) {
		trap := asString(trapAny)
		value, ok := decoys[trap]
		if !ok {
			bad("trap_decoys", "no trap_decoys entry for "+trap)
			continue
		}
		if value == nil {
			if !writeCase {
				bad("trap_decoys", fmt.Sprintf("trap_decoys[%s] is null but the case has a single-value expectation", trap))
			}
			continue
		}
		for _, answer := range expectedAnswers {
			if answersEqual(value, answer) {
				bad("trap_decoys", fmt.Sprintf("trap_decoys[%s] (%s) equals the expected answer (%s)",
					trap, pyReprValue(value), pyReprValue(answer)))
			}
		}
	}

	// (h) axes must cover every trap's axis
	need := map[string]struct{}{}
	for _, trapAny := range anySlice(tags["traps"]) {
		if entry, ok := ctx.traps[asString(trapAny)]; ok {
			need[entry.axis] = struct{}{}
		}
	}
	have := map[string]struct{}{}
	for _, axisAny := range anySlice(tags["axes"]) {
		axis := asString(axisAny)
		if _, ok := ctx.axes[axis]; ok {
			have[axis] = struct{}{}
		}
	}
	var missing []string
	for axis := range need {
		if _, ok := have[axis]; !ok {
			missing = append(missing, axis)
		}
	}
	if len(missing) > 0 {
		sort.Strings(missing)
		bad("axes.coverage", "axes missing trap axes: "+pyReprList(missing))
	}

	// (i) expect.files write targets need their directories pre-created
	var fileKeys []string
	for key := range anyMap(caseObj["files"]) {
		fileKeys = append(fileKeys, key)
	}
	if caseExpect != nil {
		for path := range anyMap(caseExpect["files"]) {
			parent := ""
			if idx := strings.LastIndex(path, "/"); idx != -1 {
				parent = path[:idx]
			}
			if parent == "" {
				continue
			}
			covered := false
			for _, key := range fileKeys {
				if key == parent || strings.HasPrefix(key, parent+"/") {
					covered = true
					break
				}
			}
			if !covered {
				bad("m0.write_dir", fmt.Sprintf("expect.files target %s: no files entry under %s "+
					"(workspace tools cannot create directories)", pyReprValue(path), pyReprValue(parent)))
			}
		}
	}

	// (j) directory structure <scenario>/<id>/
	if len(relParts) != 2 {
		shown := strings.Join(relParts, "/")
		if shown == "" {
			shown = "(root)"
		}
		bad("dir_structure", fmt.Sprintf("expected <scenario>/<id>/layout, got %s", shown))
	} else {
		scenDir, dirname := relParts[0], relParts[1]
		match := caseIDRe.FindStringSubmatch(dirname)
		if match == nil {
			bad("dir_structure", fmt.Sprintf("case id %s must be <scenario abbrev>-<4 digits>", pyReprValue(dirname)))
		}
		if scenarioIsString && containsString(ctx.scenarios, scenario) && scenDir != scenario {
			bad("dir_structure", fmt.Sprintf("case sits under %s but tags.scenario is %s",
				pyReprValue(scenDir), pyReprValue(scenario)))
		}
		if match != nil {
			if abbrev, ok := ctx.abbrev[scenario]; ok && match[1] != abbrev {
				bad("dir_structure", fmt.Sprintf("id prefix %s != scenario abbrev %s",
					pyReprValue(match[1]), pyReprValue(abbrev)))
			}
		}
	}

	// (k) verify.py + NOTES.md
	for _, item := range verifyPyViolations(caseDir) {
		bad(item[0], item[1])
	}
	for _, item := range notesViolations(caseDir, scenario) {
		bad(item[0], item[1])
	}

	// (m) notes state the answer, hidden inputs stay inside the workspace
	for _, item := range notesAnswerViolations(caseDir, caseObj) {
		bad(item[0], item[1])
	}
	for _, item := range hiddenFileViolations(caseObj) {
		bad(item[0], item[1])
	}
	for _, item := range webFixtureViolations(caseObj) {
		bad(item[0], item[1])
	}

	// (l) llm-authored cases stay draft until a human reviewer takes ownership
	author, _ := tags["author"].(string)
	reviewer, _ := tags["reviewer"].(string)
	humanReviewed := strings.HasPrefix(reviewer, "human:")
	if strings.HasPrefix(author, "llm:") && !humanReviewed && asString(tags["status"]) != "draft" {
		bad("author.status", fmt.Sprintf("author %s requires status 'draft', got %s",
			pyReprValue(author), pyReprValue(tags["status"])))
	}
}

// loadLintCtx reads the vocabulary lint checks against. Traps are walked in
// file order because the order they contribute forbidden words decides the
// order violations are printed in.
func loadLintCtx(vocabPath string) (*lintCtx, error) {
	raw, err := os.ReadFile(vocabPath)
	if err != nil {
		return nil, err
	}
	obj, err := lab.DecodeJSONBytes(raw)
	if err != nil {
		return nil, err
	}
	m, ok := obj.(map[string]any)
	if !ok {
		return nil, fmt.Errorf("%s is not a JSON object", vocabPath)
	}
	ctx := &lintCtx{
		abbrev:        map[string]string{},
		taskTypes:     map[string][]string{},
		traps:         map[string]trapEntry{},
		axes:          map[string]struct{}{},
		levels:        map[string]struct{}{},
		statuses:      map[string]struct{}{},
		contracts:     map[string]string{},
		scenarioTraps: map[string][]string{},
	}
	for _, entryAny := range anySlice(m["scenarios"]) {
		entry := anyMap(entryAny)
		name := stringField(entry, "name")
		ctx.scenarios = append(ctx.scenarios, name)
		ctx.abbrev[name] = stringField(entry, "abbrev")
	}
	for scenario, typesAny := range anyMap(m["task_types"]) {
		var types []string
		for _, t := range anySlice(typesAny) {
			types = append(types, asString(t))
		}
		ctx.taskTypes[scenario] = types
	}
	trapKeys, err := lab.OrderedObjectKeys(raw, "traps")
	if err != nil {
		return nil, err
	}
	trapObj := anyMap(m["traps"])
	for _, id := range trapKeys {
		entry := anyMap(trapObj[id])
		te := trapEntry{axis: stringField(entry, "axis")}
		for _, word := range anySlice(entry["forbidden_words"]) {
			te.forbiddenWords = append(te.forbiddenWords, asString(word))
		}
		for _, scen := range anySlice(entry["scenarios"]) {
			te.scenarios = append(te.scenarios, asString(scen))
			ctx.scenarioTraps[asString(scen)] = append(ctx.scenarioTraps[asString(scen)], id)
		}
		ctx.traps[id] = te
	}
	for _, axis := range anySlice(m["axes"]) {
		ctx.axes[asString(axis)] = struct{}{}
	}
	for _, level := range anySlice(m["levels"]) {
		ctx.levels[asString(level)] = struct{}{}
	}
	for _, status := range anySlice(m["statuses"]) {
		ctx.statuses[asString(status)] = struct{}{}
	}
	for _, tool := range anySlice(m["tools"]) {
		ctx.tools = append(ctx.tools, asString(tool))
	}
	contractKeys, err := lab.OrderedObjectKeys(raw, "answer_contracts")
	if err != nil {
		return nil, err
	}
	contractObj := anyMap(m["answer_contracts"])
	for _, key := range contractKeys {
		ctx.contracts[key] = stringField(contractObj, key)
		ctx.contractOrder = append(ctx.contractOrder, key)
	}
	return ctx, nil
}

// canaryOK mirrors Python's CANARY_RE.search(description), where "$" also
// matches just before a single trailing newline.
func canaryOK(description string) bool {
	for _, loc := range canaryRe.FindAllStringIndex(description, -1) {
		if loc[1] == len(description) {
			return true
		}
		if loc[1] == len(description)-1 && description[len(description)-1] == '\n' {
			return true
		}
	}
	return false
}

// pySpaceRe is Python's \s for str patterns: ASCII whitespace plus the Unicode
// spaces, which Go's \s (ASCII only) would miss.
var pySpaceRe = regexp.MustCompile("[\t\n\v\f\r\x1c-\x1f \u0085   -     　]+")

func normalizePrompt(text string) string {
	return pySpaceRe.ReplaceAllString(strings.ToLower(text), " ")
}

// forbiddenPhraseRe builds the matcher for one forbidden phrase over
// whitespace-normalized lowercase text. A single word matches as a substring
// (historic semantics); a multi-word phrase matches when its words appear in
// order with at most 3 extra words between consecutive phrase words, so
// "without tools" also matches "without using any tools".
func forbiddenPhraseRe(phrase string) *regexp.Regexp {
	words := strings.Fields(strings.ToLower(phrase))
	if len(words) == 0 {
		return nil
	}
	if len(words) == 1 {
		return regexp.MustCompile(regexp.QuoteMeta(words[0]))
	}
	pat := regexp.QuoteMeta(words[0])
	for _, word := range words[1:] {
		pat += `(?: \S+){0,3} ` + regexp.QuoteMeta(word)
	}
	re, err := regexp.Compile(pat)
	if err != nil {
		return nil
	}
	return re
}

func allowedLevels(nTraps, refCalls, nFiles int, multiTurn bool) map[string]struct{} {
	valid := map[string]struct{}{}
	if nTraps == 0 && refCalls <= 3 {
		valid["L0"] = struct{}{}
	}
	if nTraps == 1 && refCalls <= 4 {
		valid["L1"] = struct{}{}
	}
	if nTraps == 2 || (nTraps == 1 && (nFiles >= 3 || refCalls >= 5)) {
		valid["L2"] = struct{}{}
	}
	if nTraps >= 3 || (multiTurn && nTraps >= 1) || refCalls >= 8 {
		valid["L3"] = struct{}{}
	}
	return valid
}

func fixtureBytesOf(caseObj map[string]any) int {
	total := 0
	for _, content := range anyMap(caseObj["files"]) {
		if s, ok := content.(string); ok {
			total += len(s)
		}
	}
	return total
}

func turnObjects(caseObj map[string]any) []map[string]any {
	var out []map[string]any
	for _, turn := range anySlice(caseObj["turns"]) {
		if tm, ok := turn.(map[string]any); ok {
			out = append(out, tm)
		}
	}
	return out
}

// writeCaseIndented is lint.py's --fix write: json.dump(indent=2,
// ensure_ascii=False) plus a trailing newline, with the case's key order
// preserved (Python dicts keep it; a Go map would not).
func writeCaseIndented(path string, caseObj map[string]any) {
	ordered, err := lab.DecodeOrderedJSONFile(path)
	if err != nil {
		return
	}
	if om, ok := ordered.(*lab.OrderedMap); ok {
		if tags, ok := om.Get("tags"); ok {
			if tm, ok := tags.(*lab.OrderedMap); ok {
				tm.Set("fixture_bytes", tagsOf(caseObj)["fixture_bytes"])
			}
		}
	}
	data, err := lab.EncodeOrderedJSON(ordered, lab.EncodeOptions{Indent: 2})
	if err != nil {
		return
	}
	_ = os.WriteFile(path, append(data, '\n'), 0o644)
}

// truthy is Python's bool(x) for the JSON shapes a case's expect fields can
// take: an empty object, array, string, zero or null is false, anything else
// is true.
func truthy(v any) bool {
	switch t := v.(type) {
	case nil:
		return false
	case bool:
		return t
	case string:
		return t != ""
	case json.Number:
		f, err := t.Float64()
		return err != nil || f != 0
	case []any:
		return len(t) > 0
	case map[string]any:
		return len(t) > 0
	}
	return true
}

func containsString(list []string, want string) bool {
	for _, item := range list {
		if item == want {
			return true
		}
	}
	return false
}

func asString(v any) string {
	s, _ := v.(string)
	return s
}

func anyMap(v any) map[string]any {
	m, _ := v.(map[string]any)
	return m
}

func sortedListOr(set map[string]struct{}, fallback string) string {
	if len(set) == 0 {
		return fallback
	}
	items := make([]string, 0, len(set))
	for item := range set {
		items = append(items, item)
	}
	sort.Strings(items)
	return pyReprList(items)
}
