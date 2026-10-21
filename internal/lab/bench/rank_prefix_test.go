package bench

import (
	"os"
	"path/filepath"
	"testing"
)

// makeRankRun writes the minimum a rank run needs to be counted: a directory
// named <prefix>-<suite>-<arm>-k<i>, a passing experiment.json and a summary.
func makeRankRun(t *testing.T, out, name string) {
	t.Helper()
	dir := filepath.Join(out, name)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "experiment.json"), []byte(`{"gate_passed":true}`), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "summary.json"), []byte(`{"cases":[]}`), 0o644); err != nil {
		t.Fatal(err)
	}
}

// A bench directory holds runs from before and after the prefix rename; with
// no --prefix both families are ranked, or half the runs would vanish.
func TestRankReadsBothDirectoryPrefixes(t *testing.T) {
	out := t.TempDir()
	makeRankRun(t, out, "g1k-workbank-greedy-k0")
	makeRankRun(t, out, "rwkv-workbank-t03-p05-k0")

	both := loadRankRuns(out, "")
	if len(both[rankKey{"workbank", "greedy"}]) != 1 {
		t.Fatalf("default prefix lost the g1k- run: %v", both)
	}
	if len(both[rankKey{"workbank", "t03-p05"}]) != 1 {
		t.Fatalf("default prefix lost the rwkv- run: %v", both)
	}
	oldOnly := loadRankRuns(out, "g1k")
	if len(oldOnly) != 1 || len(oldOnly[rankKey{"workbank", "greedy"}]) != 1 {
		t.Fatalf("--prefix g1k loaded %v, want only the g1k- run", oldOnly)
	}
	newOnly := loadRankRuns(out, "rwkv")
	if len(newOnly) != 1 || len(newOnly[rankKey{"workbank", "t03-p05"}]) != 1 {
		t.Fatalf("--prefix rwkv loaded %v, want only the rwkv- run", newOnly)
	}
}
