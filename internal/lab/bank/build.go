package bank

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// runBuild ports build.py. The output file's bytes are load-bearing: its
// sha256 is the bank_version that past reports quote, so a re-run on the same
// cases must reproduce the file exactly — compact separators, sorted keys,
// and Python's int-vs-float spelling preserved.
func runBuild(args []string) int {
	fs := newFlagSet("bank build",
		"Merge case.json files into a canonical bank file with a bank_version hash.")
	cases := fs.String("cases", DefaultCases(),
		"case root directory (searched recursively for case.json), or a single case dir")
	status := fs.String("status", "all",
		"only include cases whose tags.status matches: draft|reviewed|frozen|all")
	out := fs.String("out", "", "output file path (refuses to overwrite without --force)")
	force := fs.Bool("force", false, "overwrite an existing output file")
	if err := fs.Parse(args); err != nil {
		return 2
	}
	if *out == "" {
		fmt.Fprintln(os.Stderr, "error: --out is required")
		return 2
	}
	switch *status {
	case "draft", "reviewed", "frozen", "all":
	default:
		fmt.Fprintf(os.Stderr, "error: --status must be draft|reviewed|frozen|all, got %q\n", *status)
		return 2
	}

	caseDirs, err := findCaseFiles(*cases)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: --cases %s is not a directory\n", *cases)
		return 2
	}

	merged := make([]any, 0, len(caseDirs))
	skipped, broken := 0, 0
	for _, dir := range caseDirs {
		path := filepath.Join(dir, "case.json")
		caseObj, err := loadCaseJSON(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "warning: skipping unreadable %s: %s\n", path, err)
			broken++
			continue
		}
		if *status != "all" && stringField(tagsOf(caseObj), "status") != *status {
			skipped++
			continue
		}
		merged = append(merged, caseObj)
	}
	sort.SliceStable(merged, func(i, j int) bool {
		return caseID(merged[i]) < caseID(merged[j])
	})

	payload := map[string]any{"schema_version": 5, "cases": merged}
	data, err := encodeCompact(payload)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}

	if _, err := os.Stat(*out); err == nil && !*force {
		fmt.Fprintf(os.Stderr, "error: %s already exists (use --force to overwrite)\n", *out)
		return 2
	}
	if dir := filepath.Dir(*out); dir != "" && dir != "." {
		if err := os.MkdirAll(dir, 0o755); err != nil {
			fmt.Fprintf(os.Stderr, "error: %s\n", err)
			return 2
		}
	}
	if err := os.WriteFile(*out, data, 0o644); err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}

	sum := sha256.Sum256(data)
	fmt.Printf("cases: %d (skipped %d by status=%s, %d unreadable)\n", len(merged), skipped, *status, broken)
	fmt.Printf("bank_version = sha256:%s\n", hex.EncodeToString(sum[:]))
	fmt.Printf("out: %s (%d bytes)\n", *out, len(data))
	return 0
}

func caseID(v any) string {
	m, ok := v.(map[string]any)
	if !ok {
		return ""
	}
	return stringField(m, "id")
}

// encodeCompact is json.dumps(..., ensure_ascii=False, separators=(",", ":"),
// sort_keys=True) — the exact serialisation the bank_version hashes.
func encodeCompact(v any) ([]byte, error) {
	return lab.EncodeJSON(v, 0)
}
