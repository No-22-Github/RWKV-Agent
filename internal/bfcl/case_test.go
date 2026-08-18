package bfcl

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadSplitPreservesMessagesAndFinalLine(t *testing.T) {
	t.Parallel()
	directory := t.TempDir()
	content := `{"id":"live_simple_1-0-0","question":[[{"role":"system","content":"\n keep  \n"},{"role":"user","content":"call it"}]],"function":[{"name":"math.factorial","description":"factorial","parameters":{"type":"dict","properties":{"number":{"type":"integer"}}}}]}`
	if err := os.WriteFile(filepath.Join(directory, "BFCL_v4_live_simple.json"), []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
	cases, err := LoadSplit(directory, "live_simple")
	if err != nil {
		t.Fatal(err)
	}
	if len(cases) != 1 || cases[0].ID != "live_simple_1-0-0" || len(cases[0].Messages) != 2 {
		t.Fatalf("cases = %+v", cases)
	}
	if cases[0].Messages[0].Content != "\n keep  \n" {
		t.Fatalf("system content = %q", cases[0].Messages[0].Content)
	}
}
