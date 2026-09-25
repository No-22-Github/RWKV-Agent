package corpus

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// Render corpus rows by replaying teacher actions through the real eval
// harness.
//
// Instead of re-implementing the wire here, each script entry is replayed
// through `rwkv-cli agent-eval --script` under the flags a workbank benchmark
// uses, and the rows command cuts training rows out of the trace. Every byte
// between teacher actions (tool receipts, post-tool reminders, RECOVERY notes,
// duplicate rejections, forced-answer blocks) is therefore exactly what the
// model sees at eval time.
//
// agent-eval stays a subprocess on purpose: the point is to use the same flag
// parser the benchmarks use, so the run's wire_hash matches a scoring run's
// (§2.1.1). The bank-loadability probe is in-process instead, calling the real
// loader rather than repeatedly invoking agent-eval and regexing its stderr.

// benchFlags is the workbank arm of .claude/skills/rwkv-bench/sweep.py:
// catalog, file tools, budgets and wire. Sampling flags are omitted because a
// script ignores them.
var benchFlags = []string{
	"--tool-catalog", "work-v1", "--file-tools", "lines",
	"--max-steps", "16", "--max-tokens", "4096", "--decision-max-tokens", "2048",
	"--profile", "g1k", "--strict-spec",
	"--trace-prompt-bytes", "-1",
}

// RenderArgs are the `corpus render` flags.
type RenderArgs struct {
	Records       string
	Cases         string
	Script        string
	Out           string
	CLI           string
	Source        string
	TagMap        string
	Parallelism   int
	AllowTestBank bool
	KeepFailing   bool
	Extra         []string
}

// RunRender is the `corpus render` command.
func RunRender(args RenderArgs) int {
	hasRecords := args.Records != ""
	hasCasesOrScript := args.Cases != "" || args.Script != ""
	if hasRecords == hasCasesOrScript || (args.Cases != "") != (args.Script != "") {
		fmt.Fprintln(stderr, "error: give either --records, or both --cases and --script")
		return 2
	}
	// --source has no default on purpose: a default would silently label a
	// batch with the wrong origin, and every row carries the field.
	if args.Source == "" {
		fmt.Fprintln(stderr, "error: --source is required (the dataset name every row records, e.g. base700 or distill-b01)")
		return 1
	}
	if args.Cases != "" && IsTestBank(args.Cases) && !args.AllowTestBank {
		fmt.Fprintf(stderr, "error: --cases %s is the test bank; distill from a separate bank "+
			"(pass --allow-test-bank only for a smoke test)\n", args.Cases)
		return 2
	}

	var cases []*lab.OrderedMap
	var entries []*lab.OrderedMap
	if hasRecords {
		records, err := ReadJSONL(args.Records)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		tagMap, err := LoadTagMap(args.TagMap)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		vocab, err := LoadVocab(DefaultVocab())
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		testBank, err := TestBankIDs()
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		seeded := 0
		for _, record := range records {
			caseObj, err := RecordToCase(record)
			if err != nil {
				fmt.Fprintln(stderr, err)
				return 2
			}
			tags, err := tagMap.NormalizeRecord(record, vocab)
			if err != nil {
				fmt.Fprintln(stderr, err)
				return 1
			}
			fromTest := testBank[mapString(record, "parent_seed_id")]
			if fromTest {
				seeded++
			}
			// The label block travels with the case so `corpus rows` can read
			// it back without joining against the records.
			caseObj.Set("tags", CaseTagsValue(tags, fromTest))
			cases = append(cases, caseObj)
			entry, err := RecordToScript(record)
			if err != nil {
				fmt.Fprintln(stderr, err)
				return 2
			}
			entries = append(entries, scriptEntryOrdered(entry))
		}
		fmt.Fprintf(stderr, "records: %d case(s), %d seeded from a test-bank case\n", len(cases), seeded)
	} else {
		var err error
		entries, err = ReadJSONL(args.Script)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		bankCases, err := Load(args.Cases)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		index, err := ByID(bankCases)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		cases, err = CasesForScript(index, entries)
		if err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
	}

	if _, err := os.Stat(args.Out); err == nil {
		fmt.Fprintf(stderr, "error: --out %s already exists\n", args.Out)
		return 2
	}
	if err := os.MkdirAll(args.Out, 0o755); err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	casesPath := filepath.Join(args.Out, "cases")
	scriptPath := filepath.Join(args.Out, "script.jsonl")
	runDir := filepath.Join(args.Out, "run")
	if err := Write(casesPath, cases); err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	if err := WriteJSONL(scriptPath, entries, "x"); err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}

	unloadable, err := SetAsideUnloadable(casesPath, filepath.Join(args.Out, "unloadable"))
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	for _, item := range unloadable {
		fmt.Fprintf(stderr, "unloadable %s: %s\n", item.caseID, item.reason)
	}

	replay(args.CLI, scriptPath, casesPath, runDir, args.Parallelism, args.Extra)
	if !fileExists(filepath.Join(runDir, "trace.jsonl")) {
		fmt.Fprintln(stderr, "agent-eval produced no trace")
		return 1
	}
	code := cutRows(runDir, scriptPath, args.Out, args.Source, args.KeepFailing)
	if len(unloadable) > 0 {
		rows := make([]*lab.OrderedMap, 0, len(unloadable))
		for _, item := range unloadable {
			row := lab.NewOrderedMap()
			row.Set("case_id", item.caseID)
			row.Set("reason", "unloadable: "+item.reason)
			rows = append(rows, row)
		}
		if err := WriteJSONL(filepath.Join(args.Out, "rejects.jsonl"), rows, "a"); err != nil {
			fmt.Fprintln(stderr, err)
			return 2
		}
		fmt.Printf("  %4d  unloadable by the bank loader (see rejects.jsonl)\n", len(unloadable))
	}
	return code
}

// CasesForScript makes one case copy per script entry, renamed to the entry's
// ID: script IDs are "<case id>--p<n>" and agent-eval keys cases by ID.
func CasesForScript(cases map[string]*lab.OrderedMap, entries []*lab.OrderedMap) ([]*lab.OrderedMap, error) {
	resolved := make([]*lab.OrderedMap, 0, len(entries))
	for _, entry := range entries {
		entryID := stringField(entry, "case_id")
		base := BaseCaseID(entryID)
		original, ok := cases[base]
		if !ok {
			return nil, fmt.Errorf("script entry %s has no case %s", entryID, base)
		}
		// Python's {**case, "id": new_id} keeps the original key order and the
		// original position of "id"; Set on an existing key does the same.
		copied := lab.NewOrderedMap()
		for _, key := range original.Keys {
			copied.Set(key, original.Values[key])
		}
		copied.Set("id", entryID)
		resolved = append(resolved, copied)
	}
	return resolved, nil
}

func replay(cli, scriptPath, casesPath, runDir string, parallelism int, extra []string) {
	command := []string{cli, "agent-eval", "--script", scriptPath, "--cases", casesPath,
		"--include-draft", "--case-parallelism", fmt.Sprintf("%d", parallelism),
		"--output", runDir}
	command = append(command, benchFlags...)
	command = append(command, extra...)
	fmt.Fprintln(stderr, "+ "+strings.Join(command, " "))
	cmd := exec.Command(command[0], command[1:]...)
	cmd.Dir = RepoRoot()
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	// agent-eval exits nonzero when cases fail; the teacher's failures are
	// reported by the rows step, so only a missing run directory is fatal.
	_ = cmd.Run()
}

func cutRows(runDir, scriptPath, out, source string, keepFailing bool) int {
	args := RowsArgs{
		Run:         runDir,
		Script:      scriptPath,
		Cases:       filepath.Join(out, "cases"),
		Source:      source,
		Out:         filepath.Join(out, "rows.jsonl"),
		Rejects:     filepath.Join(out, "rejects.jsonl"),
		RequirePass: !keepFailing,
	}
	return RunRows(args)
}

var loadErrorRe = regexp.MustCompile(`cases/([^/]+)/case\.json: (.*)`)

type unloadable struct {
	caseID string
	reason string
}

// SetAsideUnloadable moves the cases the bank loader rejects out of casesPath
// until it loads.
//
// The loader enforces authoring rules (for example an expect.run script must
// ship in files) that some trajectories cannot meet without changing the
// workspace the teacher saw. The real validator decides; this calls it
// directly instead of probing agent-eval and regexing its stderr, and moves
// one case per round so it always makes progress.
func SetAsideUnloadable(casesPath, parking string) ([]unloadable, error) {
	var rejected []unloadable
	for {
		_, err := eval.LoadCasesDir(casesPath, true)
		if err == nil {
			return rejected, nil
		}
		match := loadErrorRe.FindStringSubmatch(err.Error())
		if match == nil {
			// Not attributable to one case; let agent-eval report it.
			return rejected, nil
		}
		caseID, reason := match[1], strings.TrimSpace(match[2])
		if err := os.MkdirAll(parking, 0o755); err != nil {
			return rejected, err
		}
		if err := os.Rename(filepath.Join(casesPath, caseID), filepath.Join(parking, caseID)); err != nil {
			return rejected, nil
		}
		rejected = append(rejected, unloadable{caseID: caseID, reason: reason})
	}
}

func fileExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && !info.IsDir()
}
