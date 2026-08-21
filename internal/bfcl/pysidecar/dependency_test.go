package pysidecar

import (
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

func TestRuntimeDoesNotReferenceBFCLAnswerFiles(t *testing.T) {
	t.Parallel()
	_, current, _, ok := runtime.Caller(0)
	if !ok {
		t.Fatal("resolve test source path")
	}
	paths := []string{
		filepath.Join(filepath.Dir(current), "server.py"),
		filepath.Join(filepath.Dir(current), "..", "multiturn.go"),
	}
	for _, path := range paths {
		content, err := os.ReadFile(path)
		if err != nil {
			t.Fatal(err)
		}
		for _, forbidden := range []string{"possible_answer", "ground_truth"} {
			if strings.Contains(string(content), forbidden) {
				t.Fatalf("runtime source %s references forbidden answer dependency %q", path, forbidden)
			}
		}
	}
}
