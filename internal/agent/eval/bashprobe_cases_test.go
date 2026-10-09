package eval

import (
	"os"
	"path/filepath"
	"testing"
)

// TestBashProbeCasesLoad keeps the generated bash probe (bench/bashprobe)
// loadable and valid under the current case schema.
func TestBashProbeCasesLoad(t *testing.T) {
	root := filepath.Join("..", "..", "..", "bench", "bashprobe", "cases")
	if _, err := os.Stat(root); err != nil {
		t.Skip("bench/bashprobe/cases not generated")
	}
	cases, err := LoadCasesDir(root, true)
	if err != nil {
		t.Fatal(err)
	}
	if err := ValidateCases(cases); err != nil {
		t.Fatal(err)
	}
	if len(cases) < 20 {
		t.Fatalf("loaded %d bash probe cases", len(cases))
	}
}
