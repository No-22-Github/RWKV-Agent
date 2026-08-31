package tools

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// File-editing tools for the 7B harness. Design constraints come from the
// model's measured weak spots: no byte-exact str_replace (old_str mismatches
// drive retry spirals), numbered paged reads, flat argument objects, and few
// tools. Two shapes exist for the E6 A/B (results land in the docs report):
//
//	lines ("A"): read_lines + write_file + replace_lines + append_file
//	whole ("B"): read_lines + write_file  (edits = read + full rewrite)
//
// Both share the workspace containment policy and per-call caps.
type FileEditForm string

const (
	FileEditLines FileEditForm = "lines"
	FileEditWhole FileEditForm = "whole"
)

const (
	fileEditMaxLines    = 200
	fileEditMaxReadByte = 64 * 1024
	fileEditMaxWrite    = 256 * 1024
)

// FileEditTools returns the editing toolset for the requested form. The
// workspace resolver is shared with the read-only workspace tools.
func FileEditTools(root string, form FileEditForm) ([]agent.Tool, error) {
	value, err := agent.NewWorkspaceResolver(root)
	if err != nil {
		return nil, err
	}
	switch form {
	case FileEditLines:
		return []agent.Tool{
			&readLinesTool{workspace: value},
			&writeFileTool{workspace: value},
			&replaceLinesTool{workspace: value},
			&appendFileTool{workspace: value},
		}, nil
	case FileEditWhole:
		return []agent.Tool{
			&readLinesTool{workspace: value},
			&writeFileTool{workspace: value},
		}, nil
	default:
		return nil, fmt.Errorf("unknown file-edit form %q", form)
	}
}

type readLinesTool struct{ workspace *agent.WorkspaceResolver }

func (t *readLinesTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "read_lines",
		Description: "Read lines start..end (1-based, inclusive) of a workspace text file. Output lines are numbered; at most 200 lines per call. Omit the lines to read the whole file.",
		Arguments:   `{"path":"relative file path","start_line":"optional integer >= 1","end_line":"optional integer >= start_line"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"path":{"type":"string","description":"Workspace-relative file path."},
				"start_line":{"type":["integer","null"],"minimum":1,"description":"Optional first line, default 1."},
				"end_line":{"type":["integer","null"],"minimum":1,"description":"Optional last line, default start_line+199."}
			},
			"required":["path","start_line","end_line"],
			"additionalProperties":false
		}`),
		Strict:     true,
		Bundle:     agent.ToolBundleWorkspace,
		Permission: agent.PermissionWorkspaceRead,
	}
}

type readLinesArgs struct {
	Path      string          `json:"path"`
	StartLine json.RawMessage `json:"start_line"`
	EndLine   json.RawMessage `json:"end_line"`
}

// readLinesRange decodes the nullable line range. The model habitually sends
// null for optional integers (list_files style), so nulls become defaults:
// start 1, end start+199.
func readLinesRange(args readLinesArgs) (int, int, error) {
	start, end := 1, 0
	if len(args.StartLine) > 0 && string(args.StartLine) != "null" {
		if err := json.Unmarshal(args.StartLine, &start); err != nil {
			return 0, 0, fmt.Errorf("%w: start_line: %v", agent.ErrInvalidToolArguments, err)
		}
	}
	if len(args.EndLine) > 0 && string(args.EndLine) != "null" {
		if err := json.Unmarshal(args.EndLine, &end); err != nil {
			return 0, 0, fmt.Errorf("%w: end_line: %v", agent.ErrInvalidToolArguments, err)
		}
	} else {
		end = start + fileEditMaxLines - 1
	}
	if start < 1 || end < start {
		return 0, 0, fmt.Errorf("%w: need 1 <= start_line <= end_line", agent.ErrInvalidToolArguments)
	}
	if end-start >= fileEditMaxLines {
		return 0, 0, fmt.Errorf("%w: at most %d lines per call", agent.ErrInvalidToolArguments, fileEditMaxLines)
	}
	return start, end, nil
}

type readLinesResult struct {
	Path       string `json:"path"`
	StartLine  int    `json:"start_line"`
	EndLine    int    `json:"end_line"`
	TotalLines int    `json:"total_lines"`
	Content    string `json:"content"`
}

func (t *readLinesTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args readLinesArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Path == "" {
		return nil, fmt.Errorf("%w: path is required", agent.ErrInvalidToolArguments)
	}
	start, end, err := readLinesRange(args)
	if err != nil {
		return nil, err
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, err
	}
	lines, err := readFileLines(target, fileEditMaxReadByte)
	if err != nil {
		return nil, err
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if end > len(lines) {
		end = len(lines)
	}
	if start > len(lines) {
		return readLinesResult{
			Path: args.Path, StartLine: start,
			EndLine: start - 1, TotalLines: len(lines),
			Content: "",
		}, nil
	}
	var numbered strings.Builder
	for index := start; index <= end; index++ {
		fmt.Fprintf(&numbered, "%d: %s\n", index, lines[index-1])
	}
	return readLinesResult{
		Path: args.Path, StartLine: start,
		EndLine: end, TotalLines: len(lines), Content: numbered.String(),
	}, nil
}

func readFileLines(target string, limit int64) ([]string, error) {
	handle, err := os.Open(target)
	if err != nil {
		return nil, err
	}
	defer handle.Close()
	data, err := io.ReadAll(io.LimitReader(handle, limit+1))
	if err != nil {
		return nil, err
	}
	if bytes.IndexByte(data, 0) >= 0 {
		return nil, fmt.Errorf("binary files are not supported")
	}
	if !utf8.Valid(data) {
		return nil, fmt.Errorf("file is not valid UTF-8 text")
	}
	text := strings.TrimSuffix(string(data), "\n")
	if text == "" {
		return []string{}, nil
	}
	return strings.Split(text, "\n"), nil
}

func writeFileLines(target string, lines []string) error {
	return os.WriteFile(target, []byte(strings.Join(lines, "\n")+"\n"), 0o644)
}

type writeFileTool struct{ workspace *agent.WorkspaceResolver }

func (t *writeFileTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "write_file",
		Description: "Create or overwrite a workspace text file with the given content. The content becomes the whole file.",
		Arguments:   `{"path":"relative file path","content":"full file content"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"path":{"type":"string","description":"Workspace-relative file path."},
				"content":{"type":"string","description":"Complete new file content."}
			},
			"required":["path","content"],
			"additionalProperties":false
		}`),
		Strict:           true,
		Bundle:           agent.ToolBundleWorkspace,
		Permission:       agent.PermissionWorkspaceWrite,
		MutatesWorkspace: true,
	}
}

type writeFileArgs struct {
	Path    string `json:"path"`
	Content string `json:"content"`
}

func (t *writeFileTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args writeFileArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Path == "" {
		return nil, fmt.Errorf("%w: path is required", agent.ErrInvalidToolArguments)
	}
	if len(args.Content) > fileEditMaxWrite {
		return nil, fmt.Errorf("%w: content exceeds %d bytes", agent.ErrInvalidToolArguments, fileEditMaxWrite)
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, err
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
		return nil, err
	}
	if err := os.WriteFile(target, []byte(args.Content), 0o644); err != nil {
		return nil, err
	}
	return map[string]any{"path": args.Path, "bytes": len(args.Content)}, nil
}

type replaceLinesTool struct{ workspace *agent.WorkspaceResolver }

func (t *replaceLinesTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "replace_lines",
		Description: "Replace lines start..end (1-based, inclusive) of a workspace text file with the given content lines. Other lines stay unchanged.",
		Arguments:   `{"path":"relative file path","start_line":"integer >= 1","end_line":"integer >= start_line","content":"replacement lines"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"path":{"type":"string","description":"Workspace-relative file path."},
				"start_line":{"type":"integer","minimum":1},
				"end_line":{"type":"integer","minimum":1},
				"content":{"type":"string","description":"Replacement text; may be empty to delete the range."}
			},
			"required":["path","start_line","end_line","content"],
			"additionalProperties":false
		}`),
		Strict:           true,
		Bundle:           agent.ToolBundleWorkspace,
		Permission:       agent.PermissionWorkspaceWrite,
		MutatesWorkspace: true,
	}
}

type replaceLinesArgs struct {
	Path      string `json:"path"`
	StartLine int    `json:"start_line"`
	EndLine   int    `json:"end_line"`
	Content   string `json:"content"`
}

func (t *replaceLinesTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args replaceLinesArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Path == "" {
		return nil, fmt.Errorf("%w: path is required", agent.ErrInvalidToolArguments)
	}
	if args.StartLine < 1 || args.EndLine < args.StartLine {
		return nil, fmt.Errorf("%w: need 1 <= start_line <= end_line", agent.ErrInvalidToolArguments)
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, err
	}
	lines, err := readFileLines(target, fileEditMaxReadByte)
	if err != nil {
		return nil, err
	}
	if args.EndLine > len(lines) {
		return nil, fmt.Errorf("%w: end_line %d beyond last line %d", agent.ErrInvalidToolArguments, args.EndLine, len(lines))
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	replacement := []string{}
	if args.Content != "" {
		replacement = strings.Split(strings.TrimSuffix(args.Content, "\n"), "\n")
	}
	updated := append(append([]string{}, lines[:args.StartLine-1]...), replacement...)
	updated = append(updated, lines[args.EndLine:]...)
	if err := writeFileLines(target, updated); err != nil {
		return nil, err
	}
	return map[string]any{
		"path": args.Path, "replaced_from": args.StartLine,
		"replaced_to": args.EndLine, "total_lines": len(updated),
	}, nil
}

type appendFileTool struct{ workspace *agent.WorkspaceResolver }

func (t *appendFileTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "append_file",
		Description: "Append the given lines to the end of a workspace text file. Creates the file when it does not exist.",
		Arguments:   `{"path":"relative file path","content":"lines to append"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"path":{"type":"string","description":"Workspace-relative file path."},
				"content":{"type":"string","description":"Text to append."}
			},
			"required":["path","content"],
			"additionalProperties":false
		}`),
		Strict:           true,
		Bundle:           agent.ToolBundleWorkspace,
		Permission:       agent.PermissionWorkspaceWrite,
		MutatesWorkspace: true,
	}
}

type appendFileArgs struct {
	Path    string `json:"path"`
	Content string `json:"content"`
}

func (t *appendFileTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args appendFileArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Path == "" {
		return nil, fmt.Errorf("%w: path is required", agent.ErrInvalidToolArguments)
	}
	if len(args.Content) > fileEditMaxWrite {
		return nil, fmt.Errorf("%w: content exceeds %d bytes", agent.ErrInvalidToolArguments, fileEditMaxWrite)
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, err
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	handle, err := os.OpenFile(target, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0o644)
	if err != nil {
		return nil, err
	}
	defer handle.Close()
	if _, err := handle.WriteString(args.Content); err != nil {
		return nil, err
	}
	return map[string]any{"path": args.Path, "appended_bytes": len(args.Content)}, nil
}
