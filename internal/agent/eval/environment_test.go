package eval

import (
	"encoding/json"
	"testing"
)

// A run.json written by a `go build` binary carries the commit; `go run` and
// `go test` stamp nothing, so an empty value is not an error (§5.10). The test
// only checks that the field exists with the right type and that an older
// run.json without it still decodes.
func TestEnvironmentRecordsGitCommit(t *testing.T) {
	data, err := json.Marshal(EnvironmentMetadata{
		OS: "darwin", Arch: "arm64", GoVersion: "go1.0",
		GitCommit: "0123456789abcdef0123456789abcdef01234567", GitDirty: true,
	})
	if err != nil {
		t.Fatal(err)
	}
	var fields map[string]any
	if err := json.Unmarshal(data, &fields); err != nil {
		t.Fatal(err)
	}
	commit, ok := fields["git_commit"]
	if !ok {
		t.Fatalf("git_commit missing from %s", data)
	}
	if _, ok := commit.(string); !ok {
		t.Fatalf("git_commit is %T, want string", commit)
	}
	if dirty, ok := fields["git_dirty"].(bool); !ok || !dirty {
		t.Fatalf("git_dirty is %v, want true", fields["git_dirty"])
	}
}

func TestEnvironmentWithoutGitFieldsStillDecodes(t *testing.T) {
	var environment EnvironmentMetadata
	old := []byte(`{"os":"linux","arch":"amd64","go_version":"go1.0"}`)
	if err := json.Unmarshal(old, &environment); err != nil {
		t.Fatalf("run.json from before 2026-10-21 must still decode: %v", err)
	}
	if environment.GitCommit != "" || environment.GitDirty {
		t.Fatalf("git fields = %q/%v, want empty", environment.GitCommit, environment.GitDirty)
	}
}
