package wire

import (
	"errors"
	"flag"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

var updateWireDocs = flag.Bool("update-wire-docs", false, "rewrite the generated section of docs/wire-configuration.md")

const (
	docsPath    = "docs/wire-configuration.md"
	beginMarker = "<!-- BEGIN GENERATED: wire-profiles -->"
	endMarker   = "<!-- END GENERATED: wire-profiles -->"
)

// TestDocsAreGenerated keeps the profile/axis/recovery tables in the usage
// guide generated from the registry, so a new preset, axis value or repair ID
// cannot land without the documentation following.
func TestDocsAreGenerated(t *testing.T) {
	t.Parallel()
	path := filepath.Join("..", "..", "..", "docs", "wire-configuration.md")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatalf("read %s: %v", docsPath, err)
	}
	want := strings.TrimSpace(DocsMarkdown())
	if *updateWireDocs {
		updated, err := replaceGeneratedSection(string(data), want)
		if err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(updated), 0o644); err != nil {
			t.Fatal(err)
		}
		return
	}
	got, err := generatedSection(string(data))
	if err != nil {
		t.Fatal(err)
	}
	if got != want {
		t.Fatalf("generated docs drifted from the registry; run with -update-wire-docs:\n--- want ---\n%s\n--- got ---\n%s", want, got)
	}
}

func generatedSection(content string) (string, error) {
	start := strings.Index(content, beginMarker)
	end := strings.Index(content, endMarker)
	if start < 0 || end < 0 || end < start {
		return "", errors.New("generated markers are missing or out of order in " + docsPath)
	}
	return strings.TrimSpace(content[start+len(beginMarker) : end]), nil
}

func replaceGeneratedSection(content, section string) (string, error) {
	start := strings.Index(content, beginMarker)
	end := strings.Index(content, endMarker)
	if start < 0 || end < 0 || end < start {
		return "", errors.New("generated markers are missing or out of order in " + docsPath)
	}
	return content[:start+len(beginMarker)] + "\n" + strings.TrimRight(section, "\n") + "\n" + content[end:], nil
}
