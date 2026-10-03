package corpus

import (
	"os"
	"path/filepath"
	"testing"
)

func TestRunSegcheck(t *testing.T) {
	tmpDir := t.TempDir()

	validContent := `{"segments":[{"text":"User: Hello\n\nAssistant:","train":false},{"text":" World","train":true}]}
`
	validPath := filepath.Join(tmpDir, "valid.jsonl")
	if err := os.WriteFile(validPath, []byte(validContent), 0644); err != nil {
		t.Fatal(err)
	}

	code := RunSegcheck(SegcheckArgs{Path: validPath})
	if code != 0 {
		t.Fatalf("expected 0 for valid segments, got %d", code)
	}

	// Negative test 1: missing Assistant: prefix
	invalidPrefixContent := `{"segments":[{"text":"User: Hello","train":false},{"text":" World","train":true}]}
`
	invalidPrefixPath := filepath.Join(tmpDir, "invalid_prefix.jsonl")
	if err := os.WriteFile(invalidPrefixPath, []byte(invalidPrefixContent), 0644); err != nil {
		t.Fatal(err)
	}
	code = RunSegcheck(SegcheckArgs{Path: invalidPrefixPath})
	if code != 1 {
		t.Fatalf("expected 1 for missing Assistant: prefix, got %d", code)
	}

	// Negative test 2: token split mismatch (e.g. cutting inside a token or space mismatch)
	// Without moving space: "Assistant: " then "World"
	invalidSplitContent := `{"segments":[{"text":"User: Hello\n\nAssistant: ","train":false},{"text":"World","train":true}]}
`
	invalidSplitPath := filepath.Join(tmpDir, "invalid_split.jsonl")
	if err := os.WriteFile(invalidSplitPath, []byte(invalidSplitContent), 0644); err != nil {
		t.Fatal(err)
	}
	code = RunSegcheck(SegcheckArgs{Path: invalidSplitPath})
	if code != 1 {
		t.Fatalf("expected 1 for split token mismatch / bad suffix, got %d", code)
	}
}
