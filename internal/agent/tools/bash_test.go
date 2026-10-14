package tools

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func newTestBashTool(t *testing.T) (*bashTool, string) {
	return newTestBashToolWith(t, BashOptions{})
}

func newTestBashToolWith(t *testing.T, options BashOptions) (*bashTool, string) {
	t.Helper()
	sidecar, err := ResolveBashSidecar(filepath.Join("..", "..", "..", "local", "bin", "justbash-sidecar"))
	if err != nil {
		t.Skip("bash sidecar not built; run scripts/build-justbash.sh")
	}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "data.csv"), []byte("name,score\nalice,90\nbob,72\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	options.Workspace, options.Sidecar = root, sidecar
	tools, err := BashTools(options)
	if err != nil {
		t.Fatal(err)
	}
	tool := tools[0].(*bashTool)
	t.Cleanup(func() { _ = tool.overlay.Close() })
	return tool, root
}

func runBash(t *testing.T, tool *bashTool, command string) BashResult {
	t.Helper()
	raw, _ := json.Marshal(map[string]string{"command": command})
	value, err := tool.Execute(context.Background(), raw)
	if err != nil {
		t.Fatalf("%s: %v", command, err)
	}
	return value.(BashResult)
}

func TestBashToolRunsPipelinesInWorkspace(t *testing.T) {
	tool, _ := newTestBashTool(t)
	result := runBash(t, tool, "pwd; awk -F, 'NR>1{s+=$2} END{print s}' data.csv")
	if result.ExitCode != 0 || result.Stdout != "/workspace\n162\n" {
		t.Fatalf("result = %+v", result)
	}
	if result.WorkspaceChanged() {
		t.Fatal("a read-only command reported a workspace change")
	}
}

func TestBashToolWritesStayInsideWorkspace(t *testing.T) {
	tool, root := newTestBashTool(t)
	result := runBash(t, tool, "echo ok > out.txt; echo x > ../escape.txt; echo t > /tmp/t; cat /etc/hosts")
	if !result.WorkspaceChanged() {
		t.Fatal("writing out.txt did not report a workspace change")
	}
	if _, err := os.Stat(filepath.Join(root, "out.txt")); !os.IsNotExist(err) {
		t.Fatal("bash wrote an unapproved file to disk")
	}
	if result := runBash(t, tool, "cat out.txt"); result.Stdout != "ok\n" {
		t.Fatalf("overlay read = %+v", result)
	}
	if _, err := os.Stat(filepath.Join(filepath.Dir(root), "escape.txt")); err == nil {
		t.Fatal("../escape.txt escaped the workspace")
	}
	if _, err := os.Stat(filepath.Join(root, "tmp")); err == nil {
		t.Fatal("/tmp landed in the workspace")
	}
	if !strings.Contains(result.Stderr, "/etc/hosts: No such file") {
		t.Fatalf("host file readable: %+v", result)
	}
}

func TestBashToolApplyToDiskWritesEveryChange(t *testing.T) {
	tool, root := newTestBashToolWith(t, BashOptions{ApplyToDisk: true})
	if strings.Contains(tool.Spec().Description, "staged") {
		t.Fatal("apply-to-disk description still says changes are staged")
	}
	if err := os.WriteFile(filepath.Join(root, "old.txt"), []byte("gone\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	result := runBash(t, tool, "sed -i 's/bob/carol/' data.csv && mkdir -p out && echo ok > out/new.txt && mv old.txt out/moved.txt")
	if !result.WorkspaceChanged() {
		t.Fatal("edits did not report a workspace change")
	}
	for path, want := range map[string]string{"data.csv": "name,score\nalice,90\ncarol,72\n", "out/new.txt": "ok\n", "out/moved.txt": "gone\n"} {
		got, err := os.ReadFile(filepath.Join(root, path))
		if err != nil || string(got) != want {
			t.Fatalf("%s on disk = %q, %v; want %q", path, got, err, want)
		}
	}
	if _, err := os.Stat(filepath.Join(root, "old.txt")); !os.IsNotExist(err) {
		t.Fatal("the moved file is still on disk")
	}
	// Another tool writes the disk between commands; bash must see it and keep applying.
	if err := os.WriteFile(filepath.Join(root, "data.csv"), []byte("name,score\ndave,50\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if result := runBash(t, tool, "cat data.csv; echo more >> data.csv"); result.Stdout != "name,score\ndave,50\n" {
		t.Fatalf("bash read a stale file: %q", result.Stdout)
	}
	if got, _ := os.ReadFile(filepath.Join(root, "data.csv")); string(got) != "name,score\ndave,50\nmore\n" {
		t.Fatalf("second edit on disk = %q", got)
	}
	if changes, err := tool.overlay.Changes(); err != nil || len(changes) != 0 {
		t.Fatalf("changes left staged = %v, %v", changes, err)
	}
}

func TestBashToolRefusesEntriesBelowAFile(t *testing.T) {
	tool, root := newTestBashToolWith(t, BashOptions{ApplyToDisk: true})
	result := runBash(t, tool, "mkdir -p data.csv/old; echo rc=$?; mv data.csv data.csv/old/x; echo rc=$?")
	if result.Stdout != "rc=1\nrc=1\n" || !strings.Contains(result.Stderr, "ENOTDIR") {
		t.Fatalf("result = %+v", result)
	}
	if got, _ := os.ReadFile(filepath.Join(root, "data.csv")); string(got) != "name,score\nalice,90\nbob,72\n" {
		t.Fatalf("data.csv on disk = %q", got)
	}
}

func TestBashToolReportsMissingCommands(t *testing.T) {
	tool, _ := newTestBashTool(t)
	result := runBash(t, tool, "python3 -V")
	if result.ExitCode != 127 || result.Stderr != "bash: python3: command not found\n" {
		t.Fatalf("result = %+v", result)
	}
}

func TestCapBashStreamKeepsRuneBoundary(t *testing.T) {
	text := strings.Repeat("界", bashMaxStreamBytes)
	capped := capBashStream(text)
	head, _, _ := strings.Cut(capped, "\n... [output truncated")
	if !strings.HasSuffix(head, "界") || len(head)%3 != 0 {
		t.Fatalf("cut inside a rune: %d bytes", len(head))
	}
}
