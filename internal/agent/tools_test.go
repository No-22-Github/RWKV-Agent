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

func TestWorkspaceToolsUnavailableWithoutRoot(t *testing.T) {
	t.Parallel()
	resolver, err := NewWorkspaceResolver("")
	if err != nil {
		t.Fatal(err)
	}
	if _, resolveErr := resolver.Resolve("README.md"); !strings.Contains(resolveErr.Error(), "没有打开工作区") {
		t.Fatalf("resolve error = %v, want workspace-unavailable hint", resolveErr)
	}
	tools, err := WorkspaceTools("")
	if err != nil {
		t.Fatal(err)
	}
	byName := make(map[string]Tool)
	for _, tool := range tools {
		byName[tool.Spec().Name] = tool
	}
	arguments := map[string]string{
		"list_files":  `{"path":"README.md","max_depth":1,"max_results":10}`,
		"read_file":   `{"path":"README.md"}`,
		"search_text": `{"path":".","query":"TODO","max_results":10}`,
	}
	for name, raw := range arguments {
		if _, executeErr := byName[name].Execute(context.Background(), json.RawMessage(raw)); !strings.Contains(executeErr.Error(), "没有打开工作区") {
			t.Fatalf("%s error = %v, want workspace-unavailable hint", name, executeErr)
		}
	}
}

func TestDecodeToolArgumentsCoercesNumericStrings(t *testing.T) {
	var args struct {
		Query      string `json:"query"`
		MaxResults int    `json:"max_results"`
		Limit      int    `json:"limit"`
	}
	raw := json.RawMessage(`{"query":"q","max_results":"10"}`)
	if err := DecodeToolArguments(raw, &args); err != nil {
		t.Fatalf("coercing decode failed: %v", err)
	}
	if args.MaxResults != 10 || args.Query != "q" {
		t.Fatalf("coerced values wrong: %+v", args)
	}
	// Non-numeric strings for numeric fields stay rejected.
	raw = json.RawMessage(`{"query":"q","max_results":"many"}`)
	if err := DecodeToolArguments(raw, &args); err == nil {
		t.Fatal("non-numeric string must stay rejected for an integer field")
	}
}

// TestDecodeToolArgumentsCoercesBoolStrings locks the g1j finding: the model
// spells search_text's case_sensitive as "true", and rejecting that spelling
// turned one bad call into a duplicate-blocked dead end with no evidence.
func TestDecodeToolArgumentsCoercesBoolStrings(t *testing.T) {
	var args struct {
		Query         string `json:"query"`
		CaseSensitive bool   `json:"case_sensitive"`
		MaxResults    int    `json:"max_results"`
	}
	raw := json.RawMessage(`{"query":"q","case_sensitive":"true","max_results":"5"}`)
	if err := DecodeToolArguments(raw, &args); err != nil {
		t.Fatalf("coercing decode failed: %v", err)
	}
	if !args.CaseSensitive || args.MaxResults != 5 || args.Query != "q" {
		t.Fatalf("coerced values wrong: %+v", args)
	}
	// Case and surrounding whitespace are tolerated; other spellings are not.
	raw = json.RawMessage(`{"query":"q","case_sensitive":" FALSE "}`)
	if err := DecodeToolArguments(raw, &args); err != nil {
		t.Fatalf("case-insensitive bool decode failed: %v", err)
	}
	if args.CaseSensitive {
		t.Fatalf("false was coerced to true: %+v", args)
	}
	for _, bad := range []string{`"1"`, `"yes"`, `"on"`, `""`} {
		raw = json.RawMessage(`{"query":"q","case_sensitive":` + bad + `}`)
		if err := DecodeToolArguments(raw, &args); err == nil {
			t.Fatalf("bool spelling %s must stay rejected", bad)
		}
	}
	// A real JSON bool keeps working, and a string never coerces into a
	// non-bool field.
	raw = json.RawMessage(`{"query":"q","case_sensitive":true}`)
	if err := DecodeToolArguments(raw, &args); err != nil || !args.CaseSensitive {
		t.Fatalf("native bool decode failed: %v %+v", err, args)
	}
}

// TestToolErrorsHideHostPaths locks the model-visible error contract: a raw
// filesystem error names the workspace-relative path, never the host
// absolute workspace root, and the absolute-path rejection suggests a fixed
// neutral example instead of one derived from the model's own path.
func TestToolErrorsHideHostPaths(t *testing.T) {
	t.Parallel()
	root := t.TempDir()
	resolved, err := filepath.EvalSymlinks(root)
	if err != nil {
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

	_, err = read.Execute(context.Background(), json.RawMessage(`{"path":"logs/missing.log"}`))
	if err == nil {
		t.Fatal("read_file on a missing path succeeded")
	}
	if strings.Contains(err.Error(), resolved) || strings.Contains(err.Error(), root) {
		t.Fatalf("error leaks the host workspace root: %v", err)
	}
	if !strings.Contains(err.Error(), "logs/missing.log") {
		t.Fatalf("error lost the workspace-relative path: %v", err)
	}

	// A training-residue absolute path must not be replayed as the suggested
	// example; the rejection names a fixed neutral one.
	_, err = read.Execute(context.Background(), json.RawMessage(
		`{"path":"/home/node/.openclaw/workspace/state/missing.json"}`,
	))
	if err == nil {
		t.Fatal("read_file accepted a training-residue absolute path")
	}
	if !strings.Contains(err.Error(), `such as "notes/example.txt"`) {
		t.Fatalf("rejection lost the neutral example: %v", err)
	}
	if strings.Contains(err.Error(), `such as "home/node/.openclaw`) ||
		strings.Contains(err.Error(), `such as "state/missing.json"`) {
		t.Fatalf("rejection replays a path derived from the model input: %v", err)
	}
	if strings.Contains(err.Error(), resolved) || strings.Contains(err.Error(), root) {
		t.Fatalf("rejection leaks the host workspace root: %v", err)
	}

	// search_text takes its own stat/walk path; it must honor the same contract.
	var search Tool
	for _, tool := range tools {
		if tool.Spec().Name == "search_text" {
			search = tool
		}
	}
	_, err = search.Execute(context.Background(), json.RawMessage(
		`{"query":"travel policy","path":"travel_policy"}`,
	))
	if err == nil {
		t.Fatal("search_text on a missing path succeeded")
	}
	if strings.Contains(err.Error(), resolved) || strings.Contains(err.Error(), root) {
		t.Fatalf("search_text error leaks the host workspace root: %v", err)
	}
	if !strings.Contains(err.Error(), "travel_policy") {
		t.Fatalf("search_text error lost the workspace-relative path: %v", err)
	}
}
