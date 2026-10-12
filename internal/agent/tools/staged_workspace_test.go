package tools

import (
	"context"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

func executeStaged(t *testing.T, tools []agent.Tool, name string, args string) any {
	t.Helper()
	for _, tool := range tools {
		if tool.Spec().Name == name {
			v, e := tool.Execute(context.Background(), json.RawMessage(args))
			if e != nil {
				t.Fatal(e)
			}
			return v
		}
	}
	t.Fatalf("missing tool %s", name)
	return nil
}
func readStaged(t *testing.T, w *StagedWorkspace, path string) string {
	t.Helper()
	f, e := w.Open(filepath.Join(w.root, path))
	if e != nil {
		t.Fatal(e)
	}
	defer f.Close()
	b, e := io.ReadAll(f)
	if e != nil {
		t.Fatal(e)
	}
	return string(b)
}
func TestStagedWorkspaceSharedToolsAndSelectiveReview(t *testing.T) {
	bash, root := newTestBashTool(t)
	w := bash.overlay
	if r := runBash(t, bash, "sed -i 's/alice/charlie/' data.csv; mkdir -p notes; echo transient > notes/temp.txt"); r.ExitCode != 0 {
		t.Fatal(r)
	}
	reads, e := agent.WorkspaceToolsWithFS(root, w)
	if e != nil {
		t.Fatal(e)
	}
	b, _ := json.Marshal(executeStaged(t, reads, "read_file", `{"path":"data.csv"}`))
	if !strings.Contains(string(b), "charlie") {
		t.Fatal(string(b))
	}
	edits, e := FileEditToolsWithFS(root, FileEditLines, w)
	if e != nil {
		t.Fatal(e)
	}
	executeStaged(t, edits, "write_file", `{"path":"notes/new.txt","content":"native overlay"}`)
	if r := runBash(t, bash, "cat notes/new.txt"); r.Stdout != "native overlay" {
		t.Fatal(r)
	}
	b, _ = json.Marshal(executeStaged(t, reads, "search_text", `{"query":"native","path":"notes"}`))
	if !strings.Contains(string(b), "notes/new.txt") {
		t.Fatal(string(b))
	}
	b, _ = json.Marshal(executeStaged(t, reads, "list_files", `{"path":"/workspace/notes"}`))
	if !strings.Contains(string(b), "new.txt") {
		t.Fatal(string(b))
	}
	local, e := LocalTools(Options{Workspace: root, Filesystem: w})
	if e != nil {
		t.Fatal(e)
	}
	b, _ = json.Marshal(executeStaged(t, local, "data_query", `{"path":"data.csv","filter":{"name":"charlie"},"select":"name"}`))
	if !strings.Contains(string(b), "charlie") {
		t.Fatal(string(b))
	}
	disk, _ := os.ReadFile(filepath.Join(root, "data.csv"))
	if strings.Contains(string(disk), "charlie") {
		t.Fatal("unapproved bash write persisted")
	}
	changes, e := w.Changes()
	if e != nil {
		t.Fatal(e)
	}
	var selected []FileChange
	for _, c := range changes {
		if c.Path == "data.csv" {
			selected = append(selected, c)
		}
	}
	remaining, e := w.Resolve(selected, true)
	if e != nil {
		t.Fatal(e)
	}
	disk, _ = os.ReadFile(filepath.Join(root, "data.csv"))
	if !strings.Contains(string(disk), "charlie") {
		t.Fatal("approved write missing")
	}
	if readStaged(t, w, "notes/new.txt") != "native overlay" {
		t.Fatal("partial review lost other writes")
	}
	if _, e = w.Resolve(remaining, false); e != nil {
		t.Fatal(e)
	}
	if _, e = os.Stat(filepath.Join(root, "notes")); !os.IsNotExist(e) {
		t.Fatal("discard touched disk")
	}
	if c, e := w.Changes(); e != nil || len(c) != 0 {
		t.Fatalf("remaining %v %v", c, e)
	}
	// A previously read, unmodified file must reflect subsequent host edits.
	_ = readStaged(t, w, "data.csv")
	if e := os.WriteFile(filepath.Join(root, "data.csv"), []byte("external\n"), 0644); e != nil {
		t.Fatal(e)
	}
	if r := runBash(t, bash, "cat data.csv"); r.Stdout != "external\n" {
		t.Fatal(r)
	}
}
func TestStagedWorkspaceConflictsAndStaleReview(t *testing.T) {
	bash, root := newTestBashTool(t)
	w := bash.overlay
	runBash(t, bash, "echo staged > data.csv")
	reviewed, e := w.Changes()
	if e != nil {
		t.Fatal(e)
	}
	runBash(t, bash, "echo newer > data.csv")
	if _, e = w.Resolve(reviewed, true); e == nil {
		t.Fatal("stale review accepted")
	}
	reviewed, e = w.Changes()
	if e != nil {
		t.Fatal(e)
	}
	if e := os.WriteFile(filepath.Join(root, "data.csv"), []byte("external"), 0644); e != nil {
		t.Fatal(e)
	}
	if _, e = w.Resolve(reviewed, true); e == nil {
		t.Fatal("external conflict overwritten")
	}
	if readStaged(t, w, "data.csv") != "newer\n" {
		t.Fatal("conflict lost staged edit")
	}
	if _, e = w.Resolve(reviewed, false); e != nil {
		t.Fatal(e)
	}
	if readStaged(t, w, "data.csv") != "external" {
		t.Fatal("discard did not refresh disk")
	}
}
func TestStagedWorkspaceDeletionRenameAndBinary(t *testing.T) {
	bash, root := newTestBashTool(t)
	w := bash.overlay
	if e := os.Mkdir(filepath.Join(root, "old"), 0755); e != nil {
		t.Fatal(e)
	}
	if e := os.WriteFile(filepath.Join(root, "old", "a.bin"), []byte{0, 1, 255}, 0640); e != nil {
		t.Fatal(e)
	}
	if r := runBash(t, bash, "mv old/a.bin moved.bin; rmdir old"); r.ExitCode != 0 {
		t.Fatal(r)
	}
	changes, e := w.Changes()
	if e != nil {
		t.Fatal(e)
	}
	if len(changes) != 3 {
		t.Fatalf("changes %+v", changes)
	}
	if _, e = w.Resolve(changes, true); e != nil {
		t.Fatal(e)
	}
	b, e := os.ReadFile(filepath.Join(root, "moved.bin"))
	if e != nil || string(b) != string([]byte{0, 1, 255}) {
		t.Fatalf("binary %v %v", b, e)
	}
	if _, e = os.Stat(filepath.Join(root, "old")); !os.IsNotExist(e) {
		t.Fatal("directory deletion missing")
	}
}
func TestStagedSessionsAreIsolated(t *testing.T) {
	bash, root := newTestBashTool(t)
	other, e := NewStagedWorkspace(root, bash.sidecar)
	if e != nil {
		t.Fatal(e)
	}
	defer other.Close()
	runBash(t, bash, "echo one > data.csv")
	if strings.Contains(readStaged(t, other, "data.csv"), "one") {
		t.Fatal("sessions shared writes")
	}
}

func TestStagedWorkspaceRejectsSymlinksAndRootRemoval(t *testing.T) {
	bash, root := newTestBashTool(t)
	if e := os.Symlink("data.csv", filepath.Join(root, "alias.csv")); e != nil {
		t.Fatal(e)
	}
	reads, e := agent.WorkspaceToolsWithFS(root, bash.overlay)
	if e != nil {
		t.Fatal(e)
	}
	for _, tool := range reads {
		if tool.Spec().Name == "read_file" {
			if _, e = tool.Execute(context.Background(), json.RawMessage(`{"path":"alias.csv"}`)); e == nil {
				t.Fatal("native tool followed symlink")
			}
		}
	}
	// just-bash's rm -f suppresses its filesystem error; check the actual
	// staged state rather than treating an exit status as deletion evidence.
	runBash(t, bash, "rm -rf /workspace")
	if r := runBash(t, bash, "cat data.csv"); !strings.Contains(r.Stdout, "alice") {
		t.Fatalf("workspace root was removed: %+v", r)
	}
	if _, e = os.Stat(filepath.Join(root, "data.csv")); e != nil {
		t.Fatal("root removal touched disk")
	}
}
