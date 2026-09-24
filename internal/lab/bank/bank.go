// Package bank ports the workbank authoring tools: lint, dedup, build,
// coverage, calibrate, hitcheck and verify.
//
// These read the case tree under bench/workbank/cases (a directory of
// <scenario>/<id>/case.json) and the tag vocabulary that defines what a valid
// case looks like. The port is byte-for-byte with the Python originals
// (docs/go-tooling-migration.md §4.3); where Python and Go disagree about
// numbers, sorting or text, the Python behaviour wins and the reason is
// recorded in the migration doc's §5.
package bank

import (
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"

	"github.com/no22/RWKV-Agent/internal/lab"
)

const usage = `rwkv-lab bank — workbank authoring tools

usage: rwkv-lab bank <command> [flags]

  lint       validate cases against the authoring rules (exit 1 on violations)
  dedup      mark near-duplicate case pairs within a scenario (always exits 0)
  build      merge case.json files into one bank file with a bank_version hash
  coverage   scenario x level fill status against the quotas
  calibrate  flag cases whose measured pass rate contradicts their level
  hitcheck   check that a web case's fixture answers its own NOTES
  verify     run every case's verify.py against its expected answer
`

// Run dispatches a bank subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "lint":
		return runLint(args[1:])
	case "dedup":
		return runDedup(args[1:])
	case "build":
		return runBuild(args[1:])
	case "coverage":
		return runCoverage(args[1:])
	case "calibrate":
		return runCalibrate(args[1:])
	case "hitcheck":
		return runHitcheck(args[1:])
	case "verify":
		return runVerify(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab bank: unknown command %q\n\n%s", args[0], usage)
		return 2
	}
}

// DefaultCases is the case tree, stated relative to the repository root rather
// than to the executable as the Python originals did (§4.1).
func DefaultCases() string {
	return filepath.Join(lab.RepoRoot(), "bench", "workbank", "cases")
}

// DefaultVocab is the tag vocabulary that carries the quotas and enums.
func DefaultVocab() string {
	return filepath.Join(lab.RepoRoot(), "bench", "workbank", "docs", "tag-vocab.json")
}

// DefaultLedgerCases is the per-case ledger the calibration reads.
func DefaultLedgerCases() string {
	return filepath.Join(lab.RepoRoot(), "bench", "workbank", "ledger", "cases.jsonl")
}

// findCaseFiles mirrors build.py's find_case_files: a root that is itself a
// case dir yields just that dir, otherwise every directory under it that
// holds a case.json, sorted by path.
func findCaseFiles(root string) ([]string, error) {
	if _, err := os.Stat(filepath.Join(root, "case.json")); err == nil {
		return []string{root}, nil
	}
	info, err := os.Stat(root)
	if err != nil || !info.IsDir() {
		return nil, fmt.Errorf("%s is not a directory", root)
	}
	var dirs []string
	err = filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil // Python's rglob skips unreadable directories
		}
		if d.IsDir() {
			return nil
		}
		if d.Name() == "case.json" {
			dirs = append(dirs, filepath.Dir(path))
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Strings(dirs)
	return dirs, nil
}

// loadCaseJSON reads a case file, keeping number literals as written so that
// re-encoding reproduces Python's int-vs-float spelling.
func loadCaseJSON(path string) (map[string]any, error) {
	v, err := lab.DecodeJSONFile(path)
	if err != nil {
		return nil, err
	}
	m, ok := v.(map[string]any)
	if !ok {
		return nil, errors.New("case.json is not a JSON object")
	}
	return m, nil
}

// tagsOf returns the case's tags object, tolerating a missing or mistyped one
// the way the originals' `case.get("tags") or {}` does.
func tagsOf(caseObj map[string]any) map[string]any {
	if tags, ok := caseObj["tags"].(map[string]any); ok {
		return tags
	}
	return map[string]any{}
}

func stringField(m map[string]any, key string) string {
	s, _ := m[key].(string)
	return s
}

// newFlagSet builds a flag set that reports errors the way the Python tools
// did: message on stderr, exit code 2.
func newFlagSet(name, description string) *flag.FlagSet {
	fs := flag.NewFlagSet(name, flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	fs.Usage = func() {
		fmt.Fprintf(os.Stderr, "%s\n\nusage: rwkv-lab %s\n\nflags:\n", description, name)
		fs.PrintDefaults()
	}
	return fs
}
