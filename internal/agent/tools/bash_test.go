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
	t.Helper()
	sidecar, err := ResolveBashSidecar(filepath.Join("..", "..", "..", "local", "bin", "justbash-sidecar"))
	if err != nil {
		t.Skip("bash sidecar not built; run scripts/build-justbash.sh")
	}
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "data.csv"), []byte("name,score\nalice,90\nbob,72\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools, err := BashTools(BashOptions{Workspace: root, Sidecar: sidecar})
	if err != nil {
		t.Fatal(err)
	}
	return tools[0].(*bashTool), root
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
	if data, _ := os.ReadFile(filepath.Join(root, "out.txt")); string(data) != "ok\n" {
		t.Fatalf("out.txt = %q", data)
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
