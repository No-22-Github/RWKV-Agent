package pysidecar

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func TestOfficialSidecarPersistsSessionState(t *testing.T) {
	repoRoot := filepath.Clean(filepath.Join("..", "..", ".."))
	repoRoot, err := filepath.Abs(repoRoot)
	if err != nil {
		t.Fatal(err)
	}
	python := filepath.Join(repoRoot, ".venv", "bin", "python")
	if _, err := os.Stat(python); err != nil {
		t.Skip("project BFCL virtualenv is unavailable")
	}
	client, err := Start(Config{
		Python:     python,
		Script:     filepath.Join("internal", "bfcl", "pysidecar", "server.py"),
		WorkingDir: repoRoot,
	})
	if err != nil {
		t.Fatal(err)
	}
	defer client.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	sid, err := client.NewSession(ctx, SessionOptions{
		ID: "sidecar-test", TestEntryID: "multi_turn_base_sidecar_test",
		InvolvedClasses: []string{"GorillaFileSystem"},
		InitialConfig: map[string]any{"GorillaFileSystem": map[string]any{
			"root": map[string]any{"workspace": map[string]any{"type": "directory", "contents": map[string]any{}}},
		}},
	})
	if err != nil {
		t.Fatal(err)
	}
	results, err := client.Execute(ctx, sid, []string{"mkdir(dir_name='temp')", "ls()"})
	if err != nil {
		t.Fatal(err)
	}
	if len(results) != 2 || !strings.Contains(results[1], "temp") {
		t.Fatalf("results = %q", results)
	}
	results, err = client.Execute(ctx, sid, []string{"cd(folder='temp')", "pwd()"})
	if err != nil {
		t.Fatal(err)
	}
	if len(results) != 2 || !strings.Contains(results[1], "temp") {
		t.Fatalf("persistent results = %q", results)
	}
	if err := client.CloseSession(ctx, sid); err != nil {
		t.Fatal(err)
	}
}
