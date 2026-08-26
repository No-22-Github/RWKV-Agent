package bfcl

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestWriteMultiTurnResultOmitsSingleCaseLatency(t *testing.T) {
	t.Parallel()
	directory := t.TempDir()
	trace := MultiTurnTrace{
		ID: "multi_turn_base_0", Category: "multi_turn_base",
		Result: [][][]string{{{`mkdir(dir_name="temp")`}}}, Latency: 1.25,
	}
	if err := WriteMultiTurnResult(directory, "model", trace); err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(directory, "model", "multi_turn", "BFCL_v4_multi_turn_base_result.json")
	content, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(content), `"latency"`) {
		t.Fatalf("single-case official result contains latency: %s", content)
	}
}
