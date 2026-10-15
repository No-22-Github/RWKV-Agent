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

// Turn.ReviewBefore plays the user resolving the file-changes panel between
// turns: reject leaves the disk as it was and nothing staged, accept writes.
func TestReviewStagedChanges(t *testing.T) {
	sidecar := filepath.Join("..", "..", "..", "local", "bin", "justbash-sidecar")
	if _, err := tools.ResolveBashSidecar(sidecar); err != nil {
		t.Skip("bash sidecar not built; run scripts/build-justbash.sh")
	}
	for _, accept := range []bool{false, true} {
		root := t.TempDir()
		view, err := tools.NewStagedWorkspace(root, sidecar)
		if err != nil {
			t.Fatal(err)
		}
		bash, err := tools.BashTools(tools.BashOptions{Workspace: root, Sidecar: sidecar, Overlay: view})
		if err != nil {
			t.Fatal(err)
		}
		if _, err := bash[0].Execute(context.Background(), json.RawMessage(`{"command":"echo hi > note.txt"}`)); err != nil {
			t.Fatal(err)
		}
		if err := reviewStagedChanges(view, accept); err != nil {
			t.Fatal(err)
		}
		pending, err := view.Changes()
		if err != nil {
			t.Fatal(err)
		}
		_, statErr := os.Stat(filepath.Join(root, "note.txt"))
		if len(pending) != 0 || (statErr == nil) != accept {
			t.Errorf("accept=%v: pending=%d, on disk=%v", accept, len(pending), statErr == nil)
		}
		_ = view.Close()
	}
	if err := reviewStagedChanges(nil, false); err == nil {
		t.Error("review without a staged view must fail")
	}
}

func TestReviewBeforeValidated(t *testing.T) {
	loose := Expectation{ForbiddenTools: []string{"bash"}}
	for _, tc := range []struct {
		turns []Turn
		want  string
	}{
		{[]Turn{{Prompt: "a", Expect: loose}, {Prompt: "b", Expect: loose, ReviewBefore: "maybe"}}, "invalid review_before"},
		{[]Turn{{Prompt: "a", Expect: loose, ReviewBefore: "reject"}}, "nothing is staged yet"},
	} {
		err := ValidateCases([]Case{{ID: "review", Description: "review", Category: "files", Turns: tc.turns}})
		if err == nil || !strings.Contains(err.Error(), tc.want) {
			t.Errorf("err = %v, want %q", err, tc.want)
		}
	}
}
