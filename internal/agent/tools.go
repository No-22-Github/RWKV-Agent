package agent

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"reflect"
	"strconv"
	"strings"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/inference"
)

const (
	maxReadBytes       = 64 * 1024
	maxSearchFileBytes = 2 * 1024 * 1024
)

type workspace struct {
	root        string
	unavailable bool
}

// WorkspaceResolver exposes the existing workspace containment policy to
// tool packages without exposing the workspace root itself.
type WorkspaceResolver struct {
	workspace *workspace
}

func NewWorkspaceResolver(root string) (*WorkspaceResolver, error) {
	value, err := newWorkspace(root)
	if err != nil {
		return nil, err
	}
	return &WorkspaceResolver{workspace: value}, nil
}

func (r *WorkspaceResolver) Resolve(path string) (string, error) {
	if r == nil || r.workspace == nil {
		return "", fmt.Errorf("workspace resolver is not initialized")
	}
	return r.workspace.resolve(path)
}

func WorkspaceTools(root string) ([]Tool, error) {
	value, err := newWorkspace(root)
	if err != nil {
		return nil, err
	}
	return []Tool{
		&listFilesTool{workspace: value},
		&readFileTool{workspace: value},
		&searchTextTool{workspace: value},
	}, nil
}

func newWorkspace(root string) (*workspace, error) {
	if root == "" {
		// 未打开工作区：解析器保持不可用状态，任何解析都会返回明确错误，
		// 绝不回退到当前工作目录（.app 经 LaunchServices 启动时 CWD 是 /，
		// 回退会让文件工具绑定到整个磁盘根）。
		return &workspace{unavailable: true}, nil
	}
	absolute, err := filepath.Abs(root)
	if err != nil {
		return nil, fmt.Errorf("resolve workspace: %w", err)
	}
	resolved, err := filepath.EvalSymlinks(absolute)
	if err != nil {
		return nil, fmt.Errorf("resolve workspace symlinks: %w", err)
	}
	info, err := os.Stat(resolved)
	if err != nil {
		return nil, fmt.Errorf("stat workspace: %w", err)
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("%w: workspace is not a directory", inference.ErrInvalidArgument)
	}
	return &workspace{root: filepath.Clean(resolved)}, nil
}

// absoluteCandidates maps a model-supplied absolute path onto the relative
// paths it plausibly meant. The model never sees the real workspace root, so it
// commonly anchors paths at a notional "/workspace". Candidates are ordered
// most literal first; resolve only accepts one that both stays inside the
// workspace and actually exists, so a genuine escape such as "/etc/hosts" still
// fails.
func (w *workspace) absoluteCandidates(path string) []string {
	trimmed := filepath.ToSlash(path)
	if volume := filepath.VolumeName(path); volume != "" {
		trimmed = strings.TrimPrefix(trimmed, filepath.ToSlash(volume))
	}
	if root := filepath.ToSlash(w.root); strings.HasPrefix(trimmed, root+"/") {
		trimmed = strings.TrimPrefix(trimmed, root+"/")
	}
	trimmed = strings.TrimLeft(trimmed, "/")
	if trimmed == "" {
		return []string{"."}
	}
	candidates := []string{trimmed}
	for _, notional := range []string{"workspace", filepath.Base(w.root)} {
		for {
			if trimmed == notional {
				trimmed = "."
			} else if strings.HasPrefix(trimmed, notional+"/") {
				trimmed = strings.TrimPrefix(trimmed, notional+"/")
			} else {
				break
			}
			candidates = append(candidates, trimmed)
			if trimmed == "." {
				break
			}
		}
	}
	// Harnesses commonly mount a checkout below a virtual /workspace/*.git
	// directory. Resolve that presentation path back onto this configured root;
	// resolveRelative still enforces containment and existence.
	if slash := strings.IndexByte(trimmed, '/'); slash > 0 && strings.HasSuffix(trimmed[:slash], ".git") {
		candidates = append(candidates, trimmed[slash+1:])
	}
	return candidates
}

func (w *workspace) resolve(path string) (string, error) {
	if w == nil || w.unavailable {
		return "", fmt.Errorf("没有打开工作区：本地文件工具需要先打开一个工作区才能使用。请停止调用文件工具，直接告诉用户先在应用中打开一个工作区（“打开工作区”按钮）")
	}
	if path == "" {
		path = "."
	}
	if filepath.IsAbs(path) || filepath.VolumeName(path) != "" {
		// An absolute path that already points inside the workspace is accepted
		// after the same containment check as any relative path. Symlinks are
		// evaluated first so a link form of the root (macOS /var) still matches.
		if resolved, err := filepath.EvalSymlinks(path); err == nil {
			if relative, err := filepath.Rel(w.root, resolved); err == nil &&
				relative != ".." &&
				!strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
				return resolved, nil
			}
		}
		candidates := w.absoluteCandidates(path)
		for _, candidate := range candidates {
			resolved, err := w.resolveRelative(candidate)
			if err != nil {
				continue
			}
			if _, err := os.Lstat(resolved); err != nil {
				continue
			}
			return resolved, nil
		}
		// A malformed path argument is rejected before the tool reads anything,
		// so it must be classified as an argument error: it observed no
		// workspace state and cannot ground an answer. Escapes stay a plain
		// error because a refusal is itself a reportable observation.
		return "", fmt.Errorf(
			"%w: path must be workspace-relative, such as %q; got absolute path %q",
			ErrInvalidToolArguments,
			candidates[len(candidates)-1],
			path,
		)
	}
	return w.resolveRelative(path)
}

func (w *workspace) resolveRelative(path string) (string, error) {
	if path == "" {
		path = "."
	}
	clean := filepath.Clean(path)
	if clean == ".." || strings.HasPrefix(clean, ".."+string(filepath.Separator)) {
		return "", fmt.Errorf("path escapes the workspace")
	}
	target, err := filepath.EvalSymlinks(filepath.Join(w.root, clean))
	if err != nil {
		return "", err
	}
	relative, err := filepath.Rel(w.root, target)
	if err != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
		return "", fmt.Errorf("path escapes the workspace")
	}
	return target, nil
}

func (w *workspace) relative(path string) string {
	value, err := filepath.Rel(w.root, path)
	if err != nil || value == "." {
		return value
	}
	return filepath.ToSlash(value)
}

type listFilesTool struct {
	workspace *workspace
}

func (t *listFilesTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "list_files",
		Description: "List files and directories below a workspace-relative path. Generated and VCS directories are skipped.",
		Arguments:   `{"path":"optional relative directory","max_depth":"integer 1..8","max_results":"integer 1..500"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"path":{"type":["string","null"],"description":"Optional workspace-relative directory."},
				"max_depth":{"type":["integer","null"],"minimum":1,"maximum":8},
				"max_results":{"type":["integer","null"],"minimum":1,"maximum":500}
			},
			"required":["path","max_depth","max_results"],
			"additionalProperties":false
		}`),
		Strict:     true,
		Bundle:     ToolBundleWorkspace,
		Permission: PermissionWorkspaceRead,
	}
}

type listFilesArgs struct {
	Path       string `json:"path"`
	MaxDepth   int    `json:"max_depth"`
	MaxResults int    `json:"max_results"`
}

type fileEntry struct {
	Path string `json:"path"`
	Type string `json:"type"`
	Size int64  `json:"size,omitempty"`
}

type listFilesResult struct {
	Entries   []fileEntry `json:"entries"`
	Truncated bool        `json:"truncated"`
}

func (t *listFilesTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args listFilesArgs
	if err := DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.MaxDepth == 0 {
		args.MaxDepth = 3
	}
	if args.MaxResults == 0 {
		args.MaxResults = 200
	}
	if args.MaxDepth < 1 || args.MaxDepth > 8 {
		return nil, fmt.Errorf("%w: max_depth must be between 1 and 8", ErrInvalidToolArguments)
	}
	if args.MaxResults < 1 || args.MaxResults > 500 {
		return nil, fmt.Errorf("%w: max_results must be between 1 and 500", ErrInvalidToolArguments)
	}
	target, err := t.workspace.resolve(args.Path)
	if err != nil {
		return nil, err
	}
	info, err := os.Stat(target)
	if err != nil {
		return nil, err
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("path is not a directory")
	}
	baseDepth := pathDepth(t.workspace.relative(target))
	result := listFilesResult{Entries: make([]fileEntry, 0, args.MaxResults)}
	err = filepath.WalkDir(target, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if err := ctx.Err(); err != nil {
			return err
		}
		if path == target {
			return nil
		}
		relative := t.workspace.relative(path)
		if entry.IsDir() && shouldSkipDirectory(entry.Name()) {
			return filepath.SkipDir
		}
		if pathDepth(relative)-baseDepth > args.MaxDepth {
			if entry.IsDir() {
				return filepath.SkipDir
			}
			return nil
		}
		if len(result.Entries) >= args.MaxResults {
			result.Truncated = true
			return fs.SkipAll
		}
		item := fileEntry{Path: relative, Type: "file"}
		if entry.IsDir() {
			item.Type = "directory"
		} else if entry.Type()&os.ModeSymlink != 0 {
			item.Type = "symlink"
		} else if value, statErr := entry.Info(); statErr == nil {
			item.Size = value.Size()
		}
		result.Entries = append(result.Entries, item)
		return nil
	})
	return result, err
}

type readFileTool struct {
	workspace *workspace
}

func (t *readFileTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "read_file",
		Description: "Read one UTF-8 text file inside the workspace, up to 64 KiB.",
		Arguments:   `{"path":"relative file path"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{"path":{"type":"string","description":"Workspace-relative file path."}},
			"required":["path"],
			"additionalProperties":false
		}`),
		Strict:     true,
		Bundle:     ToolBundleWorkspace,
		Permission: PermissionWorkspaceRead,
	}
}

type readFileArgs struct {
	Path string `json:"path"`
}

type readFileResult struct {
	Path      string `json:"path"`
	Content   string `json:"content"`
	Truncated bool   `json:"truncated"`
}

func (t *readFileTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args readFileArgs
	if err := DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Path == "" {
		return nil, fmt.Errorf("%w: path is required", ErrInvalidToolArguments)
	}
	target, err := t.workspace.resolve(args.Path)
	if err != nil {
		return nil, err
	}
	info, err := os.Stat(target)
	if err != nil {
		return nil, err
	}
	if !info.Mode().IsRegular() {
		return nil, fmt.Errorf("path is not a regular file")
	}
	handle, err := os.Open(target)
	if err != nil {
		return nil, err
	}
	defer handle.Close()
	data, err := io.ReadAll(io.LimitReader(handle, maxReadBytes+1))
	if err != nil {
		return nil, err
	}
	if bytes.IndexByte(data, 0) >= 0 {
		return nil, fmt.Errorf("binary files are not supported")
	}
	if !utf8.Valid(data) {
		return nil, fmt.Errorf("file is not valid UTF-8 text")
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	truncated := len(data) > maxReadBytes
	if truncated {
		data = data[:maxReadBytes]
	}
	return readFileResult{
		Path:      t.workspace.relative(target),
		Content:   string(data),
		Truncated: truncated,
	}, nil
}

type searchTextTool struct {
	workspace *workspace
}

func (t *searchTextTool) Spec() ToolSpec {
	return ToolSpec{
		Name:        "search_text",
		Description: "Search literal text in workspace files. Generated and VCS directories are skipped.",
		Arguments:   `{"query":"literal text","path":"optional relative path","case_sensitive":"boolean","max_results":"integer 1..200"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"query":{"type":"string","description":"Literal text to search for."},
				"path":{"type":["string","null"],"description":"Optional workspace-relative file or directory."},
				"case_sensitive":{"type":["boolean","null"]},
				"max_results":{"type":["integer","null"],"minimum":1,"maximum":200}
			},
			"required":["query","path","case_sensitive","max_results"],
			"additionalProperties":false
		}`),
		Strict:     true,
		Bundle:     ToolBundleWorkspace,
		Permission: PermissionWorkspaceRead,
	}
}

type searchTextArgs struct {
	Query         string `json:"query"`
	Path          string `json:"path"`
	CaseSensitive bool   `json:"case_sensitive"`
	MaxResults    int    `json:"max_results"`
}

type searchMatch struct {
	Path string `json:"path"`
	Line int    `json:"line"`
	Text string `json:"text"`
}

type searchTextResult struct {
	Matches   []searchMatch `json:"matches"`
	Truncated bool          `json:"truncated"`
}

func (t *searchTextTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args searchTextArgs
	if err := DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Query == "" {
		return nil, fmt.Errorf("%w: query is required", ErrInvalidToolArguments)
	}
	if args.MaxResults == 0 {
		args.MaxResults = 50
	}
	if args.MaxResults < 1 || args.MaxResults > 200 {
		return nil, fmt.Errorf("%w: max_results must be between 1 and 200", ErrInvalidToolArguments)
	}
	target, err := t.workspace.resolve(args.Path)
	if err != nil {
		return nil, err
	}
	info, err := os.Stat(target)
	if err != nil {
		return nil, err
	}
	result := searchTextResult{Matches: make([]searchMatch, 0, args.MaxResults)}
	visit := func(path string, entry fs.DirEntry) error {
		if err := ctx.Err(); err != nil {
			return err
		}
		if entry.IsDir() {
			if path != target && shouldSkipDirectory(entry.Name()) {
				return filepath.SkipDir
			}
			return nil
		}
		if entry.Type()&os.ModeSymlink != 0 {
			return nil
		}
		value, err := entry.Info()
		if err != nil || !value.Mode().IsRegular() || value.Size() > maxSearchFileBytes {
			return nil
		}
		matches, binary, err := searchFile(path, args.Query, args.CaseSensitive, args.MaxResults-len(result.Matches))
		if err != nil || binary {
			return err
		}
		for _, match := range matches {
			match.Path = t.workspace.relative(path)
			result.Matches = append(result.Matches, match)
		}
		if len(result.Matches) >= args.MaxResults {
			result.Truncated = true
			return fs.SkipAll
		}
		return nil
	}
	if !info.IsDir() {
		entry := fs.FileInfoToDirEntry(info)
		err = visit(target, entry)
	} else {
		err = filepath.WalkDir(target, func(path string, entry fs.DirEntry, walkErr error) error {
			if walkErr != nil {
				return walkErr
			}
			return visit(path, entry)
		})
	}
	return result, err
}

func searchFile(path, query string, caseSensitive bool, limit int) ([]searchMatch, bool, error) {
	handle, err := os.Open(path)
	if err != nil {
		return nil, false, err
	}
	defer handle.Close()
	needle := query
	if !caseSensitive {
		needle = strings.ToLower(needle)
	}
	scanner := bufio.NewScanner(handle)
	scanner.Buffer(make([]byte, 64*1024), maxSearchFileBytes)
	var matches []searchMatch
	for lineNumber := 1; scanner.Scan(); lineNumber++ {
		line := scanner.Text()
		if strings.IndexByte(line, 0) >= 0 {
			return nil, true, nil
		}
		haystack := line
		if !caseSensitive {
			haystack = strings.ToLower(haystack)
		}
		if strings.Contains(haystack, needle) {
			matches = append(matches, searchMatch{
				Line: lineNumber,
				Text: truncateText(strings.TrimSpace(line), 300),
			})
			if len(matches) >= limit {
				break
			}
		}
	}
	return matches, false, scanner.Err()
}

// DecodeToolArguments decodes a tool arguments payload strictly: unknown
// fields and trailing data are rejected so a malformed call surfaces as an
// argument error rather than a silently ignored one. UseNumber keeps numeric
// literals exact until the tool validates them.
//
// One deliberate leniency: a numeric target field accepts a JSON string that
// parses exactly as a number ("10" for an integer). Measured in the round-3
// zh e2e: once the catalog renders max_results as a flat "integer 1..10"
// placeholder, the model reliably emits "10" as a string, and rejecting it
// costs the whole step budget to a duplicate-call loop (the strict path was
// added for malformed STRUCTURE, not for scalar spelling).
func DecodeToolArguments(raw json.RawMessage, target any) error {
	if coerced, changed := coerceNumericArgumentStrings(raw, target); changed {
		raw = coerced
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	decoder.UseNumber()
	if err := decoder.Decode(target); err != nil {
		return fmt.Errorf("%w: %v", ErrInvalidToolArguments, err)
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return fmt.Errorf("%w: trailing data", ErrInvalidToolArguments)
	}
	return nil
}

// coerceNumericArgumentStrings rewrites top-level string values to numeric
// literals when the matching target field is numeric and the string parses
// exactly as one. Non-numeric strings, unknown fields, and nested values are
// left untouched so the strict decoder still judges them.
func coerceNumericArgumentStrings(raw json.RawMessage, target any) (json.RawMessage, bool) {
	var fields map[string]json.RawMessage
	if json.Unmarshal(raw, &fields) != nil {
		return raw, false
	}
	targetType := reflect.TypeOf(target)
	if targetType == nil || targetType.Kind() != reflect.Pointer || targetType.Elem().Kind() != reflect.Struct {
		return raw, false
	}
	structType := targetType.Elem()
	numericKinds := map[reflect.Kind]bool{
		reflect.Int: true, reflect.Int8: true, reflect.Int16: true,
		reflect.Int32: true, reflect.Int64: true,
		reflect.Uint: true, reflect.Uint8: true, reflect.Uint16: true,
		reflect.Uint32: true, reflect.Uint64: true,
		reflect.Float32: true, reflect.Float64: true,
	}
	numericFields := map[string]reflect.StructField{}
	for i := 0; i < structType.NumField(); i++ {
		field := structType.Field(i)
		jsonName := strings.Split(field.Tag.Get("json"), ",")[0]
		if jsonName == "" {
			jsonName = field.Name
		}
		if numericKinds[field.Type.Kind()] {
			numericFields[jsonName] = field
		}
	}
	changed := false
	for name, value := range fields {
		if _, ok := numericFields[name]; !ok {
			continue
		}
		var text string
		if json.Unmarshal(value, &text) != nil {
			continue
		}
		if _, err := strconv.ParseInt(text, 10, 64); err != nil {
			if _, floatErr := strconv.ParseFloat(text, 64); floatErr != nil {
				continue
			}
		}
		fields[name] = json.RawMessage(text)
		changed = true
	}
	if !changed {
		return raw, false
	}
	encoded, err := json.Marshal(fields)
	if err != nil {
		return raw, false
	}
	return encoded, true
}

func shouldSkipDirectory(name string) bool {
	switch name {
	case ".git", "build", "dist", "node_modules":
		return true
	default:
		return false
	}
}

func pathDepth(path string) int {
	if path == "" || path == "." {
		return 0
	}
	return strings.Count(filepath.ToSlash(filepath.Clean(path)), "/") + 1
}

func truncateText(value string, limit int) string {
	runes := []rune(value)
	if len(runes) <= limit {
		return value
	}
	return string(runes[:limit])
}
