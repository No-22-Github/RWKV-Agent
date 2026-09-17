package tools

import (
	"context"
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// TestReadLinesErrorHidesHostPath locks the file-edit tools' error contract:
// a missing file is reported with its workspace-relative path, never the host
// absolute workspace root.
func TestReadLinesErrorHidesHostPath(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	resolved, err := filepath.EvalSymlinks(root)
	if err != nil {
		t.Fatal(err)
	}
	editTools, err := FileEditTools(root, FileEditLines)
	if err != nil {
		t.Fatal(err)
	}
	var readLines agent.Tool
	for _, tool := range editTools {
		if tool.Spec().Name == "read_lines" {
			readLines = tool
		}
	}
	_, err = readLines.Execute(context.Background(), json.RawMessage(
		`{"path":"logs/missing.log","start_line":1,"end_line":10}`,
	))
	if err == nil {
		t.Fatal("read_lines on a missing path succeeded")
	}
	if strings.Contains(err.Error(), resolved) || strings.Contains(err.Error(), root) {
		t.Fatalf("error leaks the host workspace root: %v", err)
	}
	if !strings.Contains(err.Error(), "logs/missing.log") {
		t.Fatalf("error lost the workspace-relative path: %v", err)
	}
}
