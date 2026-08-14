package agent

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"
)

func TestWorkspaceToolsClassifyInvalidArguments(t *testing.T) {
	t.Parallel()
	tools, err := WorkspaceTools(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	for _, tool := range tools {
		var arguments json.RawMessage
		switch tool.Spec().Name {
		case "list_files":
			arguments = json.RawMessage(`{"path":".","max_depth":9}`)
		case "read_file":
			arguments = json.RawMessage(`{"path":"README.md","max_bytes":64}`)
		case "search_text":
			arguments = json.RawMessage(`{"path":"."}`)
		default:
			t.Fatalf("unexpected tool %q", tool.Spec().Name)
		}
		if _, executeErr := tool.Execute(context.Background(), arguments); !errors.Is(executeErr, ErrInvalidToolArguments) {
			t.Fatalf("%s error = %v, want ErrInvalidToolArguments", tool.Spec().Name, executeErr)
		}
	}
}

func TestWorkspaceToolsReadListAndSearch(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, "docs"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(
		filepath.Join(root, "README.md"),
		[]byte("RWKV Agent\nread-only tools\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(
		filepath.Join(root, "docs", "plan.md"),
		[]byte("Next milestone: agent harness\n"),
		0o644,
	); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	byName := make(map[string]Tool)
	for _, tool := range tools {
		byName[tool.Spec().Name] = tool
	}

	readValue, err := byName["read_file"].Execute(
		context.Background(),
		json.RawMessage(`{"path":"README.md"}`),
	)
	if err != nil {
		t.Fatal(err)
	}
	readResult := readValue.(readFileResult)
	if !strings.Contains(readResult.Content, "read-only tools") || readResult.Truncated {
		t.Fatalf("read result = %+v", readResult)
	}

	listValue, err := byName["list_files"].Execute(
		context.Background(),
		json.RawMessage(`{"path":".","max_depth":2}`),
	)
	if err != nil {
		t.Fatal(err)
	}
	listResult := listValue.(listFilesResult)
	if len(listResult.Entries) != 3 {
		t.Fatalf("entries = %+v", listResult.Entries)
	}

	searchValue, err := byName["search_text"].Execute(
		context.Background(),
		json.RawMessage(`{"query":"MILESTONE","path":"docs"}`),
	)
	if err != nil {
		t.Fatal(err)
	}
	searchResult := searchValue.(searchTextResult)
	if len(searchResult.Matches) != 1 ||
		searchResult.Matches[0].Path != "docs/plan.md" ||
		searchResult.Matches[0].Line != 1 {
		t.Fatalf("matches = %+v", searchResult.Matches)
	}
}

func TestWorkspaceToolsNormalizeNotionalAbsolutePaths(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	if err := os.MkdirAll(filepath.Join(root, "logs"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(
		filepath.Join(root, "logs", "deploy.log"), []byte("ERROR boom\n"), 0o644,
	); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	var read, list Tool
	for _, tool := range tools {
		switch tool.Spec().Name {
		case "read_file":
			read = tool
		case "list_files":
			list = tool
		}
	}
	for _, path := range []string{
		"/workspace/logs/deploy.log",
		"/workspace/project-repo.git/logs/deploy.log",
		"/logs/deploy.log",
		"/workspace/workspace/logs/deploy.log",
		filepath.Join(root, "logs", "deploy.log"),
	} {
		arguments := json.RawMessage(`{"path":` + strconv.Quote(path) + `}`)
		value, err := read.Execute(context.Background(), arguments)
		if err != nil {
			t.Fatalf("read_file(%q) error = %v, want normalized success", path, err)
		}
		if content := value.(readFileResult).Content; !strings.Contains(content, "ERROR boom") {
			t.Fatalf("read_file(%q) content = %q", path, content)
		}
	}
	if _, err := list.Execute(
		context.Background(), json.RawMessage(`{"path":"/workspace/logs"}`),
	); err != nil {
		t.Fatalf("list_files absolute error = %v, want normalized success", err)
	}
}

func TestWorkspaceMalformedAbsolutePathIsArgumentError(t *testing.T) {
	t.Parallel()
	tools, err := WorkspaceTools(t.TempDir())
	if err != nil {
		t.Fatal(err)
	}
	var read Tool
	for _, tool := range tools {
		if tool.Spec().Name == "read_file" {
			read = tool
		}
	}
	// A path that cannot be normalized onto an existing workspace entry must be
	// an argument error so it never counts as workspace evidence.
	_, err = read.Execute(context.Background(), json.RawMessage(`{"path":"/etc/hosts"}`))
	if !errors.Is(err, ErrInvalidToolArguments) {
		t.Fatalf("error = %v, want ErrInvalidToolArguments", err)
	}
	if !strings.Contains(err.Error(), "workspace-relative") {
		t.Fatalf("error = %v, want the corrected path shape", err)
	}
}

func TestWorkspaceToolsRejectEscapesAndSymlinkTraversal(t *testing.T) {
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
	if err := os.Symlink(outside, filepath.Join(root, "link.txt")); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	var read Tool
	for _, tool := range tools {
		if tool.Spec().Name == "read_file" {
			read = tool
		}
	}
	for _, arguments := range []string{
		`{"path":"../secret.txt"}`,
		`{"path":"link.txt"}`,
		`{"path":"/etc/hosts"}`,
	} {
		if _, err := read.Execute(context.Background(), json.RawMessage(arguments)); err == nil {
			t.Fatalf("read_file accepted %s", arguments)
		}
	}
}

func TestReadFileTruncatesLargeInput(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	content := strings.Repeat("x", maxReadBytes+100)
	if err := os.WriteFile(filepath.Join(root, "large.txt"), []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
	tools, err := WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	for _, tool := range tools {
		if tool.Spec().Name != "read_file" {
			continue
		}
		value, err := tool.Execute(context.Background(), json.RawMessage(`{"path":"large.txt"}`))
		if err != nil {
			t.Fatal(err)
		}
		result := value.(readFileResult)
		if !result.Truncated || len(result.Content) != maxReadBytes {
			t.Fatalf("result length=%d truncated=%t", len(result.Content), result.Truncated)
		}
	}
}
