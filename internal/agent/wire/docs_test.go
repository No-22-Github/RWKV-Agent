package wire

import (
	"flag"
	"os"
	"path/filepath"
	"testing"
)

var updateWireDocs = flag.Bool("update-wire-docs", false, "rewrite docs/refactor/wire-profiles.md")

// TestDocsAreGenerated locks the P6 contract: the profile/axis/recovery tables
// are generated from the registry, so a new preset or repair ID cannot land
// without the documentation following.
func TestDocsAreGenerated(t *testing.T) {
	t.Parallel()
	path := filepath.Join("..", "..", "..", "docs", "refactor", "wire-profiles.md")
	got := DocsMarkdown()
	if *updateWireDocs {
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(got), 0o644); err != nil {
			t.Fatal(err)
		}
		return
	}
	want, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("generated docs missing; run with -update-wire-docs: %v", err)
	}
	if got != string(want) {
		t.Fatalf("docs drifted from the registry; run with -update-wire-docs:\n--- want ---\n%s\n--- got ---\n%s", want, got)
	}
}
