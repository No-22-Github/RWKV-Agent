package eval

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/tools"
)

// Case fixtures carry the bank clock as their modification time, and the App
// harness's bash agrees with the datetime tool on what "today" is, so a case
// about "yesterday" means the same day whichever tool the model reaches for.
func TestProductBashSeesBankClock(t *testing.T) {
	sidecar := filepath.Join("..", "..", "..", "local", "bin", "justbash-sidecar")
	if _, err := tools.ResolveBashSidecar(sidecar); err != nil {
		t.Skip("bash sidecar not built; run scripts/build-justbash.sh")
	}
	t.Setenv(tools.BashSidecarEnv, sidecar)
	testCase := Case{ID: "clock", Files: map[string]string{"logs/app.log": "ok\n"}}
	workspace, cleanup, err := createWorkspace(t.TempDir(), testCase)
	if err != nil {
		t.Fatal(err)
	}
	defer cleanup()
	for _, path := range []string{"logs", "logs/app.log"} {
		info, err := os.Stat(filepath.Join(workspace, path))
		if err != nil {
			t.Fatal(err)
		}
		if !info.ModTime().Equal(fixtureModTime) {
			t.Errorf("%s mtime = %v, want %v", path, info.ModTime(), fixtureModTime)
		}
	}

	catalog, view, err := productCaseTools(Config{}, workspace, testCase)
	if err != nil {
		t.Fatal(err)
	}
	defer view.Close()
	var bash interface {
		Execute(context.Context, json.RawMessage) (any, error)
	}
	for _, tool := range catalog {
		if tool.Spec().Name == "bash" {
			bash = tool
		}
	}
	if bash == nil {
		t.Fatal("App catalog has no bash tool")
	}
	value, err := bash.Execute(context.Background(), json.RawMessage(`{"command":"date +%F; date -d yesterday +%F; ls -l logs/app.log"}`))
	if err != nil {
		t.Fatal(err)
	}
	out := value.(tools.BashResult).Stdout
	if !strings.HasPrefix(out, "2026-09-16\n2026-09-15\n") || !strings.Contains(out, "Sep 16 09:00 logs/app.log") {
		t.Fatalf("bash output = %q", out)
	}
}
