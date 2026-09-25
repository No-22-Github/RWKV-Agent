package corpus

import (
	"crypto/sha256"
	"encoding/hex"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

// Pack a validated dataset out of rendered training rows (§4.2, S7/S8).
//
// Inputs are concatenated in command-line order; --exclude drops every row of
// the listed case IDs (a multi-turn case contributes one row per turn, and all
// of them go). Four gates then run over what is left, and a single failure
// stops the pack before any file is written:
//
//  1. every row carries the same meta.wire_hash;
//  2. every text fits in --max-tokens World tokens;
//  3. no text contains WORKBANK-CANARY or DISTILL-CANARY;
//  4. no two texts are identical (by sha256).
//
// The statistics block is printed to stdout both for --dry-run and for a real
// run, and both print the same block. --out writes train.jsonl ({"text": …}
// only), rows.jsonl (the accepted input lines, byte for byte) and
// manifest.json. An existing --out directory is refused.

// packVocab is the vocabulary lab.RunTokcount counts with. The two commands
// must agree, so the path is repeated here rather than owned by pack.
const packVocab = "third_party/rwkv-mobile/assets/rwkv_vocab_v20230424.txt"

// canaries are the prefixes lint puts in bench descriptions; seeing one in a
// training text means a fixture leaked the marker into model-visible bytes.
const (
	canaryWorkbank = "WORKBANK-CANARY"
	canaryDistill  = "DISTILL-CANARY"
)

// PackArgs are the `corpus pack` flags.
type PackArgs struct {
	Rows      []string
	Exclude   string
	Out       string
	DryRun    bool
	MaxTokens int
}

// packFlagSet parses the command line on its own so tests can exercise the
// flags without running the command (the cli.go convention).
func packFlagSet(args *PackArgs, rows *stringList) *flag.FlagSet {
	fs := newFlagSet("corpus pack",
		"Validate rendered training rows and pack a dataset directory.")
	fs.Var(rows, "rows", "rows.jsonl to pack, in order (repeatable)")
	fs.StringVar(&args.Exclude, "exclude", "", "JSONL whose case_id values are dropped, every turn of them")
	fs.StringVar(&args.Out, "out", "", "new output directory")
	fs.BoolVar(&args.DryRun, "dry-run", false, "validate and print the summary; write nothing")
	fs.IntVar(&args.MaxTokens, "max-tokens", 4096, "reject rows whose text is longer than this many World tokens")
	return fs
}

func runPackCmd(argv []string) int {
	var args PackArgs
	var rows stringList
	fs := packFlagSet(&args, &rows)
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	args.Rows = rows
	return RunPack(args)
}

// packInput is one --rows file as the manifest records it.
type packInput struct {
	Path string
	SHA  string
	// Rows counts the lines this file contributes to the pack, after
	// --exclude. The sum over inputs equals the manifest's row count.
	Rows int
}

// packRow is one decoded input line: the raw bytes (rows.jsonl is rewritten
// as-is, never re-encoded) next to the fields the gates and statistics read.
type packRow struct {
	raw      string
	text     string
	spans    any
	meta     *lab.OrderedMap
	caseID   string
	scenario string
	turn     string
	kind     string
	source   string
	wireHash string
	harness  string
	input    int
}

// RunPack is the `corpus pack` command.
func RunPack(args PackArgs) int {
	if len(args.Rows) == 0 {
		fmt.Fprintln(stderr, "error: --rows is required")
		return 2
	}
	if (args.Out == "") == !args.DryRun {
		fmt.Fprintln(stderr, "error: give exactly one of --out or --dry-run")
		return 2
	}
	if args.MaxTokens <= 0 {
		fmt.Fprintf(stderr, "error: --max-tokens must be positive, got %d\n", args.MaxTokens)
		return 2
	}
	// Refuse an existing directory up front: a pack never merges into an
	// earlier dataset (same rule as the other corpus outputs, §4.1).
	if args.Out != "" {
		if _, err := os.Stat(args.Out); err == nil {
			fmt.Fprintf(stderr, "pack: %s already exists\n", args.Out)
			return 1
		}
	}

	inputs, rows, err := readPackInputs(args.Rows)
	if err != nil {
		fmt.Fprintf(stderr, "pack: %v\n", err)
		return 1
	}
	read := len(rows)

	// An exclude entry may carry a batch (the one that recorded it). That batch
	// only excuses the rows that came from it: a case whose earlier batch's rows
	// were struck out can be re-authored and re-run in a later batch, and those
	// fresh rows must survive the older entry. Entries without a batch apply to
	// every row, which is what a hand-written exclusion means.
	excluded := map[string]map[string]bool{}
	excludeSHA := ""
	if args.Exclude != "" {
		text, err := lab.ReadText(args.Exclude)
		if err != nil {
			fmt.Fprintf(stderr, "pack: %v\n", err)
			return 1
		}
		sum := sha256.Sum256([]byte(text))
		excludeSHA = hex.EncodeToString(sum[:])
		entries, err := decodePackLines(args.Exclude, text)
		if err != nil {
			fmt.Fprintf(stderr, "pack: %v\n", err)
			return 1
		}
		for _, entry := range entries {
			id := stringField(entry, "case_id")
			if id == "" {
				fmt.Fprintf(stderr, "pack: %s: exclude entry without a case_id\n", args.Exclude)
				return 1
			}
			batch := stringField(entry, "batch")
			if excluded[id] == nil {
				excluded[id] = map[string]bool{}
			}
			excluded[id][batch] = true
		}
	}

	var kept []*packRow
	removed := 0
	for _, row := range rows {
		if batches := excluded[row.caseID]; batches != nil {
			// A row's batch is its source with the distill- prefix removed, so
			// a batch's own entries match the rows it produced. A row with no
			// source predates the field and matches every entry.
			if batches[""] || row.source == "" || batches[strings.TrimPrefix(row.source, "distill-")] {
				removed++
				continue
			}
		}
		kept = append(kept, row)
		inputs[row.input].Rows++
	}

	// The World vocabulary is loaded once and reused for every row; the
	// process-wide cache in tokenizer keeps repeated commands cheap too.
	world, err := tokenizer.OpenWorldCached(packVocabPath())
	if err != nil {
		fmt.Fprintf(stderr, "pack: %v\n", err)
		return 1
	}
	tokens := make([]int, len(kept))
	for index, row := range kept {
		tokens[index] = world.Count(row.text)
	}

	if failures := packGateFailures(kept, tokens, args.MaxTokens); len(failures) > 0 {
		for _, failure := range failures {
			fmt.Fprintf(stderr, "pack: %s\n", failure)
		}
		return 1
	}

	stats := collectPackStats(kept, tokens, read, removed)
	printPackStats(stats)

	if args.DryRun {
		fmt.Println("pack: dry run, nothing written")
		return 0
	}

	manifest := buildPackManifest(args, inputs, excludeSHA, removed, stats, kept)
	if err := writePackOutputs(args.Out, kept, manifest); err != nil {
		fmt.Fprintf(stderr, "pack: %v\n", err)
		return 1
	}
	fmt.Printf("pack: wrote train.jsonl, rows.jsonl and manifest.json to %s\n", args.Out)
	return 0
}

// readPackInputs reads every --rows file in order, hashing it and keeping each
// accepted line's original bytes aside for the verbatim rows.jsonl.
func readPackInputs(paths []string) ([]*packInput, []*packRow, error) {
	inputs := make([]*packInput, 0, len(paths))
	var rows []*packRow
	for index, path := range paths {
		text, err := lab.ReadText(path)
		if err != nil {
			return nil, nil, err
		}
		sum := sha256.Sum256([]byte(text))
		inputs = append(inputs, &packInput{Path: path, SHA: hex.EncodeToString(sum[:])})
		objects, raws, err := decodePackLinesWithRaw(path, text)
		if err != nil {
			return nil, nil, err
		}
		for position, obj := range objects {
			row, err := newPackRow(raws[position], obj, index)
			if err != nil {
				return nil, nil, fmt.Errorf("%s: %w", path, err)
			}
			rows = append(rows, row)
		}
	}
	return inputs, rows, nil
}

func decodePackLines(path, text string) ([]*lab.OrderedMap, error) {
	objects, _, err := decodePackLinesWithRaw(path, text)
	return objects, err
}

// decodePackLinesWithRaw splits a rows/exclude file into decoded objects and
// the raw line each came from, skipping blank lines exactly like ReadJSONL.
func decodePackLinesWithRaw(path, text string) ([]*lab.OrderedMap, []string, error) {
	var objects []*lab.OrderedMap
	var raws []string
	for _, line := range lab.SplitLines(text) {
		if isBlank(line) {
			continue
		}
		obj, err := lab.DecodeOrderedJSON([]byte(line))
		if err != nil {
			return nil, nil, fmt.Errorf("parse %s: %w", path, err)
		}
		om, ok := obj.(*lab.OrderedMap)
		if !ok {
			return nil, nil, fmt.Errorf("%s: line is not a JSON object", path)
		}
		objects = append(objects, om)
		raws = append(raws, line)
	}
	return objects, raws, nil
}

// newPackRow lifts the fields pack works with out of one decoded line. A
// missing meta (or a missing field inside it) is not an error: kind/source are
// being added to the renderer in parallel, and absent values tally as "".
func newPackRow(raw string, obj *lab.OrderedMap, input int) (*packRow, error) {
	textValue, ok := obj.Get("text")
	text, isString := textValue.(string)
	if !ok || !isString {
		return nil, fmt.Errorf("row has no text")
	}
	row := &packRow{raw: raw, text: text, input: input}
	row.spans = mapValue(obj, "loss_spans")
	row.meta, _ = mapValue(obj, "meta").(*lab.OrderedMap)
	row.caseID = stringField(row.meta, "case_id")
	row.scenario = packScenario(row.caseID, row.meta)
	row.kind = stringField(row.meta, "kind")
	row.source = stringField(row.meta, "source")
	row.wireHash = stringField(row.meta, "wire_hash")
	row.harness = stringField(row.meta, "harness_version")
	if turn := mapValue(row.meta, "turn"); turn != nil {
		if number, ok := asInt64(turn); ok {
			row.turn = strconv.Itoa(int(number))
		}
	}
	return row, nil
}

// packGateFailures runs the four gates over the rows that would be packed and
// returns one message per broken gate. Every gate is evaluated so a run reports
// all the problems it can, not just the first.
func packGateFailures(rows []*packRow, tokens []int, maxTokens int) []string {
	var failures []string

	hashes := newOrderedCounter()
	for _, row := range rows {
		hashes.Add(row.wireHash)
	}
	if len(hashes.Counts) > 1 {
		failures = append(failures, fmt.Sprintf(
			"wire_hash gate: %d distinct values across %d rows: %s",
			len(hashes.Counts), len(rows), packCounterSummary(hashes)))
	}

	over, worst, first := 0, 0, ""
	for index, row := range rows {
		if tokens[index] <= maxTokens {
			continue
		}
		over++
		if tokens[index] > worst {
			worst = tokens[index]
		}
		if first == "" {
			first = row.caseID
		}
	}
	if over > 0 {
		failures = append(failures, fmt.Sprintf(
			"max-tokens gate: %d rows exceed %d tokens (worst %d; first %s)",
			over, maxTokens, worst, packLabel(first)))
	}

	for _, canary := range []string{canaryWorkbank, canaryDistill} {
		count, first := 0, ""
		for _, row := range rows {
			if strings.Contains(row.text, canary) {
				count++
				if first == "" {
					first = row.caseID
				}
			}
		}
		if count > 0 {
			failures = append(failures, fmt.Sprintf(
				"canary gate: %d rows contain %s (first %s)", count, canary, packLabel(first)))
		}
	}

	seen := map[[32]byte]bool{}
	duplicates, firstDup := 0, ""
	for _, row := range rows {
		sum := sha256.Sum256([]byte(row.text))
		if seen[sum] {
			duplicates++
			if firstDup == "" {
				firstDup = row.caseID
			}
			continue
		}
		seen[sum] = true
	}
	if duplicates > 0 {
		failures = append(failures, fmt.Sprintf(
			"duplicate gate: %d rows repeat another row's text (first %s)",
			duplicates, packLabel(firstDup)))
	}

	return failures
}

// packStats is everything the summary block prints.
type packStats struct {
	read      int
	removed   int
	kept      int
	scenarios *orderedCounter
	turns     *orderedCounter
	kinds     *orderedCounter
	sources   *orderedCounter
	zeroCalls int
	p50       int
	p99       int
	maxTokens int
}

func collectPackStats(rows []*packRow, tokens []int, read, removed int) *packStats {
	stats := &packStats{
		read:      read,
		removed:   removed,
		kept:      len(rows),
		scenarios: newOrderedCounter(),
		turns:     newOrderedCounter(),
		kinds:     newOrderedCounter(),
		sources:   newOrderedCounter(),
	}
	for _, row := range rows {
		stats.scenarios.Add(row.scenario)
		stats.turns.Add(row.turn)
		stats.kinds.Add(row.kind)
		stats.sources.Add(row.source)
		if !strings.Contains(packCoveredText(row.text, row.spans), "<tool_call>") {
			stats.zeroCalls++
		}
	}
	sorted := append([]int(nil), tokens...)
	sort.Ints(sorted)
	stats.p50 = packPercentile(sorted, 50)
	stats.p99 = packPercentile(sorted, 99)
	if len(sorted) > 0 {
		stats.maxTokens = sorted[len(sorted)-1]
	}
	return stats
}

// packScenario names the scenario a row belongs to. Rows rendered after
// §4.4 carry it in meta.case_tags; older rows fall back to the case_id's
// prefix, where tab-5001--p1 and tab-5002--p1 are both "tab". The records the
// 700 corpus was built from prefix every id with "ws7", which is why the label
// is preferred when it is there.
func packScenario(caseID string, meta *lab.OrderedMap) string {
	caseTags, _ := mapValue(meta, "case_tags").(*lab.OrderedMap)
	if caseTags != nil {
		if scenario := stringField(caseTags, "scenario"); scenario != "" {
			return scenario
		}
	}
	if index := strings.IndexByte(caseID, '-'); index >= 0 {
		return caseID[:index]
	}
	return caseID
}

// packPercentile is the nearest-rank percentile of a sorted slice: the value
// at ceil(p/100*n), so p99 is the 664th of 670 and p50 the 335th.
func packPercentile(sorted []int, percent int) int {
	if len(sorted) == 0 {
		return 0
	}
	rank := (percent*len(sorted) + 99) / 100
	if rank < 1 {
		rank = 1
	}
	return sorted[rank-1]
}

// packCoveredText returns the text loss_spans covers: spans are Unicode code
// point offsets into text. Out-of-range or malformed spans are skipped rather
// than failing the pack — the gates do not police span shape, and a bad span
// only shows up in the zero-call tally.
func packCoveredText(text string, spans any) string {
	list, ok := spans.([]any)
	if !ok || len(list) == 0 {
		return ""
	}
	runes := []rune(text)
	var builder strings.Builder
	for _, item := range list {
		pair, ok := item.([]any)
		if !ok || len(pair) != 2 {
			continue
		}
		start, startOK := asInt64(pair[0])
		end, endOK := asInt64(pair[1])
		if !startOK || !endOK {
			continue
		}
		if start < 0 {
			start = 0
		}
		if end > int64(len(runes)) {
			end = int64(len(runes))
		}
		if start >= end {
			continue
		}
		builder.WriteString(string(runes[start:end]))
	}
	return builder.String()
}

func printPackStats(stats *packStats) {
	fmt.Printf("pack: %d rows read, %d excluded, %d to pack\n", stats.read, stats.removed, stats.kept)
	packPrintTable("scenario", stats.scenarios)
	packPrintTable("turn", stats.turns)
	share := 0.0
	if stats.kept > 0 {
		share = float64(stats.zeroCalls) / float64(stats.kept)
	}
	// The 15% floor is a working number printed with the share, not enforced
	// yet: the first real batches set it (§4.2, §8).
	fmt.Printf("  zero-call: %d/%d (%.1f%%) rows have no <tool_call> in the loss spans (floor 15%%, not enforced)\n",
		stats.zeroCalls, stats.kept, share*100)
	fmt.Printf("  tokens: p50=%d p99=%d max=%d\n", stats.p50, stats.p99, stats.maxTokens)
	packPrintTable("kind", stats.kinds)
	packPrintTable("source", stats.sources)
}

func packPrintTable(name string, counts *orderedCounter) {
	fmt.Printf("  by %s:\n", name)
	for _, item := range counts.MostCommon() {
		fmt.Printf("  %4d  %s\n", item.Count, packLabel(item.Key))
	}
}

// packLabel prints an absent grouping key (missing meta.kind / meta.source)
// readably; the tally itself still keys it as "".
func packLabel(key string) string {
	if key == "" {
		return "(none)"
	}
	return key
}

// packCounterSummary renders a counter for an error message, newest-first
// values truncated.
func packCounterSummary(counts *orderedCounter) string {
	entries := counts.MostCommon()
	shown := entries
	suffix := ""
	if len(shown) > 3 {
		shown = shown[:3]
		suffix = ", …"
	}
	parts := make([]string, 0, len(shown))
	for _, item := range shown {
		parts = append(parts, fmt.Sprintf("%s (%d)", item.Key, item.Count))
	}
	return strings.Join(parts, ", ") + suffix
}

func buildPackManifest(args PackArgs, inputs []*packInput, excludeSHA string, removed int,
	stats *packStats, rows []*packRow) *lab.OrderedMap {
	manifest := lab.NewOrderedMap()

	inputList := make([]any, 0, len(inputs))
	for _, input := range inputs {
		item := lab.NewOrderedMap()
		item.Set("path", input.Path)
		item.Set("sha256", input.SHA)
		item.Set("rows", input.Rows)
		inputList = append(inputList, item)
	}
	manifest.Set("inputs", inputList)

	if args.Exclude == "" {
		manifest.Set("exclude", nil)
	} else {
		exclude := lab.NewOrderedMap()
		exclude.Set("path", args.Exclude)
		exclude.Set("sha256", excludeSHA)
		exclude.Set("removed", removed)
		manifest.Set("exclude", exclude)
	}

	wireHash, harness := "", ""
	if len(rows) > 0 {
		wireHash = rows[0].wireHash
	}
	for _, row := range rows {
		if row.harness != "" {
			harness = row.harness
			break
		}
	}
	manifest.Set("wire_hash", wireHash)
	manifest.Set("harness_version", harness)
	manifest.Set("rows", len(rows))
	tokens := lab.NewOrderedMap()
	tokens.Set("p50", stats.p50)
	tokens.Set("p99", stats.p99)
	tokens.Set("max", stats.maxTokens)
	manifest.Set("tokens", tokens)
	share := 0.0
	if stats.kept > 0 {
		share = float64(stats.zeroCalls) / float64(stats.kept)
	}
	manifest.Set("zero_call_share", lab.PyFloat(lab.RoundHalfEven(share, 4)))
	manifest.Set("created_at", time.Now().UTC().Format(time.RFC3339))
	return manifest
}

// writePackOutputs materialises the dataset directory. The caller has already
// checked that it does not exist; MkdirAll still creates missing parents.
func writePackOutputs(out string, rows []*packRow, manifest *lab.OrderedMap) error {
	if err := os.MkdirAll(out, 0o755); err != nil {
		return err
	}
	train := make([]*lab.OrderedMap, 0, len(rows))
	for _, row := range rows {
		line := lab.NewOrderedMap()
		line.Set("text", row.text)
		train = append(train, line)
	}
	if err := WriteJSONL(filepath.Join(out, "train.jsonl"), train, "x"); err != nil {
		return err
	}
	var verbatim strings.Builder
	for _, row := range rows {
		verbatim.WriteString(row.raw)
		verbatim.WriteByte('\n')
	}
	if err := os.WriteFile(filepath.Join(out, "rows.jsonl"), []byte(verbatim.String()), 0o644); err != nil {
		return err
	}
	data, err := lab.EncodeOrderedJSON(manifest, lab.EncodeOptions{Indent: 1})
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(out, "manifest.json"), data, 0o644)
}

// packVocabPath resolves the World vocabulary like tokcount does: the shipped
// relative path, then relative to the repository root so the tool works from
// any working directory.
func packVocabPath() string {
	if _, err := os.Stat(packVocab); err == nil {
		return packVocab
	}
	candidate := filepath.Join(lab.RepoRoot(), packVocab)
	if _, err := os.Stat(candidate); err == nil {
		return candidate
	}
	return packVocab
}
