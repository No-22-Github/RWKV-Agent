package tools

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

func TestWorkspaceWriteFileCreatesNewFiles(t *testing.T) {
	t.Parallel()
	parent := t.TempDir()
	root := filepath.Join(parent, "workspace")
	if err := os.Mkdir(root, 0o755); err != nil {
		t.Fatal(err)
	}
	outside := filepath.Join(parent, "secret.txt")
	if err := os.WriteFile(outside, []byte("secret"), 0o644); err != nil {
		t.Fatal(err)
	}
	// A symlinked directory sits in the existing prefix: resolution must
	// evaluate it, so writes through it cannot escape.
	if err := os.Symlink(parent, filepath.Join(root, "linkdir")); err != nil {
		t.Fatal(err)
	}
	editTools, err := FileEditTools(root, FileEditLines)
	if err != nil {
		t.Fatal(err)
	}
	var write agent.Tool
	for _, tool := range editTools {
		if tool.Spec().Name == "write_file" {
			write = tool
		}
	}
	// Creating a brand-new file is part of the write_file contract.
	if _, err := write.Execute(context.Background(), json.RawMessage(
		`{"path":"reports/summary.csv","content":"month,revenue\nAug,14817.35\n"}`,
	)); err != nil {
		t.Fatalf("write_file to a new path failed: %v", err)
	}
	data, err := os.ReadFile(filepath.Join(root, "reports", "summary.csv"))
	if err != nil || !strings.Contains(string(data), "14817.35") {
		_ = filepath.WalkDir(parent, func(p string, entry os.DirEntry, werr error) error {
			t.Logf("walk %s (dir=%v err=%v)", p, entry.IsDir(), werr)
			return nil
		})
		t.Fatalf("new file not written: err=%v data=%q", err, data)
	}
	// Writing through a symlink into the parent must stay blocked, even when
	// the write target itself does not exist yet.
	if _, err := write.Execute(context.Background(), json.RawMessage(
		`{"path":"linkdir/escaped.txt","content":"no"}`,
	)); err == nil {
		t.Fatal("write_file escaped the workspace through a symlinked directory")
	}
	if _, err := os.Stat(filepath.Join(parent, "escaped.txt")); !os.IsNotExist(err) {
		t.Fatal("escaped file was created outside the workspace")
	}
	// Reads of missing files still fail as before.
	workspaceTools, err := agent.WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	for _, tool := range workspaceTools {
		if tool.Spec().Name == "read_file" {
			if _, err := tool.Execute(context.Background(), json.RawMessage(
				`{"path":"missing.txt"}`,
			)); err == nil {
				t.Fatal("read_file of a missing file must fail")
			}
		}
	}
}
