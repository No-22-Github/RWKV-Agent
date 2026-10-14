package eval

import (
	"os"
	"path/filepath"
	"testing"
)

// TestProbeCasesLoad keeps the generated probes (bench/bashprobe,
// bench/weatherprobe: the original cases, the b14 part and the reserve)
// loadable and valid under the current case schema.
func TestProbeCasesLoad(t *testing.T) {
	for dir, minimum := range map[string]int{
		"bashprobe/cases": 20, "bashprobe/cases-b14": 60, "bashprobe/reserve": 140,
		"weatherprobe/cases": 14, "weatherprobe/cases-b14": 30, "weatherprobe/reserve": 70,
	} {
		t.Run(dir, func(t *testing.T) {
			root := filepath.Join("..", "..", "..", "bench", filepath.FromSlash(dir))
			if _, err := os.Stat(root); err != nil {
				t.Skipf("bench/%s not generated", dir)
			}
			cases, err := LoadCasesDir(root, true)
			if err != nil {
				t.Fatal(err)
			}
			if err := ValidateCases(cases); err != nil {
				t.Fatal(err)
			}
			if len(cases) < minimum {
				t.Fatalf("loaded %d cases from bench/%s", len(cases), dir)
			}
		})
	}
}
