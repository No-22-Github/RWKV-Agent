package agent

import (
	"bytes"
	"io"
	"io/fs"
)

// MaxTextFileBytes caps every work-v3 whole-file read (read_file, list_files
// line counts, replace_lines). work-v2 kept its 64 KiB caps unchanged.
const MaxTextFileBytes = 8 << 20

const listFilesLineCountBudget = 32 << 20

// WorkspaceToolsV3 returns work-v3's list_files and search_text: the work-v2
// tools with list_files line counts. read_file lives in the tools package (it shares read_lines'
// numbered form).
func WorkspaceToolsV3(root string, view WorkspaceFS) ([]Tool, error) {
	value, err := newWorkspaceV3(root, view)
	if err != nil {
		return nil, err
	}
	return []Tool{&listFilesTool{workspace: value}, &searchTextTool{workspace: value}}, nil
}

// NewWorkspaceResolverV3 is the resolver the work-v3 file tools share: the
// same containment policy with list_files line counts.
func NewWorkspaceResolverV3(root string, view WorkspaceFS) (*WorkspaceResolver, error) {
	value, err := newWorkspaceV3(root, view)
	if err != nil {
		return nil, err
	}
	return &WorkspaceResolver{workspace: value}, nil
}

func newWorkspaceV3(root string, view WorkspaceFS) (*workspace, error) {
	value, err := newWorkspace(root)
	if err != nil {
		return nil, err
	}
	value.filesystem = view
	value.lineCounts = true
	value.keepBuildDirs = true
	value.relaxed = true
	return value, nil
}

type lineCountBudget struct{ remaining int64 }

// lines counts a regular text file's lines for list_files (work-v3 §2.2). A
// file over MaxTextFileBytes, a binary file, or one past the per-call read
// budget gets no count.
func (b *lineCountBudget) lines(view WorkspaceFS, path string, info fs.FileInfo) *int {
	if !info.Mode().IsRegular() || info.Size() > MaxTextFileBytes || info.Size() > b.remaining {
		return nil
	}
	handle, err := view.Open(path)
	if err != nil {
		return nil
	}
	defer handle.Close()
	data, err := io.ReadAll(io.LimitReader(handle, MaxTextFileBytes+1))
	if err != nil || len(data) > MaxTextFileBytes || bytes.IndexByte(data, 0) >= 0 {
		return nil
	}
	b.remaining -= int64(len(data))
	count := CountLines(data)
	return &count
}

// CountLines counts text lines: a final line without a newline still counts,
// an empty file has none.
func CountLines(data []byte) int {
	if len(data) == 0 {
		return 0
	}
	count := bytes.Count(data, []byte{'\n'})
	if data[len(data)-1] != '\n' {
		count++
	}
	return count
}

// Relative is the workspace-relative display form of a resolved path.
func (r *WorkspaceResolver) Relative(target string) string { return r.workspace.relative(target) }
