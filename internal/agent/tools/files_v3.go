package tools

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"regexp"
	"strconv"
	"strings"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// work-v3 file tools (docs/design/work-v3-tools.md §2.1–§2.4). The work-v2
// tools above stay byte-identical; nothing here is shared with them except
// write_file/append_file, which v3 wraps without touching.
const (
	readFileV3Lines       = 200
	readFileV3Bytes       = 12 * 1024
	readFileV3LineRunes   = 2000
	replaceLinesV3Context = 3
)

const (
	readFileV3Description     = `Read a UTF-8 text file in the workspace. Lines come numbered as "N: text". Without start_line/end_line it returns the first screen (up to 200 lines); the result says how many lines the file has.`
	replaceLinesV3Description = `Replace lines start..end (1-based, inclusive) of a workspace text file with the given content lines. Use the line numbers shown by read_file; do not include the "N: " prefixes in content. An end_line past the last line means through the last line.`
)

const (
	readFileV3MoreNote   = "只显示了第 %d–%d 行，文件共 %d 行。往后读用 start_line=%d；要查找或统计，用 search_text，或用 bash 的 grep、wc、awk 处理整个文件。"
	readFileV3PastNote   = "文件只有 %d 行，没有第 %d 行。"
	readFileV3TooBig     = "文件超过 8MB，用 bash 的 head、grep、wc 处理。"
	numberedContentError = `content 里每一行都带着 "N: " 行号前缀，这是 read_file 显示用的，不属于文件内容。去掉前缀后再写。`
)

// FileToolsV3 returns work-v3's read_file plus the three writing tools, all on
// one resolver (same containment and view as list_files and search_text from
// agent.WorkspaceToolsV3).
func FileToolsV3(root string, view agent.WorkspaceFS) (read agent.Tool, edits []agent.Tool, err error) {
	resolver, err := agent.NewWorkspaceResolverV3(root, view)
	if err != nil {
		return nil, nil, err
	}
	return &readFileV3Tool{workspace: resolver}, []agent.Tool{
		&writeFileV3Tool{inner: &writeFileTool{workspace: resolver}},
		&replaceLinesV3Tool{workspace: resolver},
		&appendFileV3Tool{inner: &appendFileTool{workspace: resolver}},
	}, nil
}

type readFileV3Tool struct{ workspace *agent.WorkspaceResolver }

func (t *readFileV3Tool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "read_file",
		Description: readFileV3Description,
		Arguments:   `{"path":"relative file path","start_line":"optional integer >= 1","end_line":"optional integer >= start_line"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"path":{"type":"string","description":"Workspace-relative file path."},"start_line":{"type":["integer","null"],"minimum":1},"end_line":{"type":["integer","null"],"minimum":1}},"required":["path","start_line","end_line"],"additionalProperties":false}`),
		Strict:      true,
		Bundle:      agent.ToolBundleWorkspace,
		Permission:  agent.PermissionWorkspaceRead,
	}
}

type readFileV3Result struct {
	Path       string `json:"path"`
	StartLine  int    `json:"start_line"`
	EndLine    int    `json:"end_line"`
	TotalLines int    `json:"total_lines"`
	Content    string `json:"content"`
	Note       string `json:"note,omitempty"`
}

func (t *readFileV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args readLinesArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Path == "" {
		return nil, fmt.Errorf("%w: path is required", agent.ErrInvalidToolArguments)
	}
	start, end, err := optionalRange(args)
	if err != nil {
		return nil, err
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, err
	}
	lines, err := readTextLinesV3(t.workspace.FS(), target)
	if err != nil {
		return nil, t.workspace.RelativizeError(err)
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	result := readFileV3Result{Path: t.workspace.Relative(target), StartLine: start, TotalLines: len(lines)}
	if start > len(lines) {
		result.EndLine = start - 1
		if len(lines) > 0 || start > 1 {
			result.Note = fmt.Sprintf(readFileV3PastNote, len(lines), start)
		}
		return result, nil
	}
	last := len(lines)
	if end > 0 && end < last {
		last = end
	}
	if last-start+1 > readFileV3Lines {
		last = start + readFileV3Lines - 1
	}
	var content strings.Builder
	size := 0
	shown := start - 1
	for index := start; index <= last; index++ {
		line := capLine(lines[index-1])
		if index > start && size+len(line)+1 > readFileV3Bytes {
			break
		}
		size += len(line) + 1
		content.WriteString(strconv.Itoa(index))
		content.WriteString(": ")
		content.WriteString(line)
		content.WriteByte('\n')
		shown = index
	}
	result.EndLine = shown
	result.Content = content.String()
	if shown < len(lines) {
		result.Note = fmt.Sprintf(readFileV3MoreNote, start, shown, len(lines), shown+1)
	}
	return result, nil
}

// optionalRange decodes read_file's nullable range; 0 end means "one screen".
func optionalRange(args readLinesArgs) (int, int, error) {
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
		if end < start {
			return 0, 0, fmt.Errorf("%w: need 1 <= start_line <= end_line", agent.ErrInvalidToolArguments)
		}
	}
	if start < 1 {
		return 0, 0, fmt.Errorf("%w: need 1 <= start_line <= end_line", agent.ErrInvalidToolArguments)
	}
	return start, end, nil
}

func capLine(line string) string {
	if utf8.RuneCountInString(line) <= readFileV3LineRunes {
		return line
	}
	runes := []rune(line)
	return string(runes[:readFileV3LineRunes]) + fmt.Sprintf(" …[本行共 %d 字符]", len(runes))
}

// readTextLinesV3 reads a whole text file (up to agent.MaxTextFileBytes) into
// lines. Unlike work-v2's readFileLinesWithFS it never silently stops at a
// byte cap: a larger file is an error.
func readTextLinesV3(view agent.WorkspaceFS, target string) ([]string, error) {
	info, err := view.Stat(target)
	if err != nil {
		return nil, err
	}
	if !info.Mode().IsRegular() {
		return nil, fmt.Errorf("path is not a regular file")
	}
	if info.Size() > agent.MaxTextFileBytes {
		return nil, errors.New(readFileV3TooBig)
	}
	handle, err := view.Open(target)
	if err != nil {
		return nil, err
	}
	defer handle.Close()
	data, err := io.ReadAll(io.LimitReader(handle, agent.MaxTextFileBytes+1))
	if err != nil {
		return nil, err
	}
	if len(data) > agent.MaxTextFileBytes {
		return nil, errors.New(readFileV3TooBig)
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

var numberedLine = regexp.MustCompile(`^(\d+): `)

// looksNumbered reports content copied from read_file with its "N: " prefixes:
// at least two non-empty lines, every one prefixed, numbers consecutive.
func looksNumbered(content string) bool {
	previous, seen := -1, 0
	for _, line := range strings.Split(content, "\n") {
		if strings.TrimSpace(line) == "" {
			continue
		}
		match := numberedLine.FindStringSubmatch(line)
		if match == nil {
			return false
		}
		value, err := strconv.Atoi(match[1])
		if err != nil || (previous >= 0 && value != previous+1) {
			return false
		}
		previous = value
		seen++
	}
	return seen >= 2
}

// guardWrite is the shared work-v3 check before any write.
func guardWrite(path, content string) error {
	if looksNumbered(content) {
		return fmt.Errorf("%w: %s", agent.ErrInvalidToolArguments, numberedContentError)
	}
	return nil
}

type writeFileV3Tool struct{ inner *writeFileTool }

func (t *writeFileV3Tool) Spec() agent.ToolSpec { return t.inner.Spec() }

func (t *writeFileV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args writeFileArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if err := guardWrite(args.Path, args.Content); err != nil {
		return nil, err
	}
	return t.inner.Execute(ctx, raw)
}

type appendFileV3Tool struct{ inner *appendFileTool }

func (t *appendFileV3Tool) Spec() agent.ToolSpec { return t.inner.Spec() }

func (t *appendFileV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args appendFileArgs
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if err := guardWrite(args.Path, args.Content); err != nil {
		return nil, err
	}
	return t.inner.Execute(ctx, raw)
}

type replaceLinesV3Tool struct{ workspace *agent.WorkspaceResolver }

func (t *replaceLinesV3Tool) Spec() agent.ToolSpec {
	spec := (&replaceLinesTool{}).Spec()
	spec.Description = replaceLinesV3Description
	return spec
}

func (t *replaceLinesV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
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
	if err := guardWrite(args.Path, args.Content); err != nil {
		return nil, err
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, err
	}
	lines, err := readTextLinesV3(t.workspace.FS(), target)
	if err != nil {
		return nil, t.workspace.RelativizeError(err)
	}
	total := len(lines)
	if args.StartLine > total+1 {
		return nil, fmt.Errorf("%w: 文件只有 %d 行，start_line 最大是 %d（在末尾追加）。", agent.ErrInvalidToolArguments, total, total+1)
	}
	clamped := false
	end := args.EndLine
	if end > total {
		end, clamped = total, true
	}
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	replacement := []string{}
	if args.Content != "" {
		replacement = strings.Split(strings.TrimSuffix(args.Content, "\n"), "\n")
	}
	updated := append(append([]string{}, lines[:args.StartLine-1]...), replacement...)
	if end >= args.StartLine {
		updated = append(updated, lines[end:]...)
	} else {
		updated = append(updated, lines[args.StartLine-1:]...)
	}
	if err := t.workspace.FS().WriteFile(target, []byte(strings.Join(updated, "\n")+"\n"), 0o644); err != nil {
		return nil, t.workspace.RelativizeError(err)
	}
	result := map[string]any{
		"path": args.Path, "replaced_from": args.StartLine,
		"replaced_to": end, "total_lines": len(updated),
		"around": numberedWindow(updated, args.StartLine-replaceLinesV3Context, args.StartLine+len(replacement)-1+replaceLinesV3Context),
	}
	if clamped {
		result["end_line_clamped"] = true
	}
	return result, nil
}

func numberedWindow(lines []string, from, to int) string {
	if from < 1 {
		from = 1
	}
	if to > len(lines) {
		to = len(lines)
	}
	var out strings.Builder
	for index := from; index <= to; index++ {
		fmt.Fprintf(&out, "%d: %s\n", index, capLine(lines[index-1]))
	}
	return out.String()
}
