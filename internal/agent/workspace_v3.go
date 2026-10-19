package agent

import (
	"bytes"
	"io"
	"io/fs"
	"path/filepath"
	"strings"
)

// WebScratchDir is the work-v3 web-page archive: web_fetch saves long pages
// under it, the read tools read them back (docs/design/work-v3-tools.md §2.7).
const WebScratchDir = ".web"

// MaxTextFileBytes caps every work-v3 whole-file read (read_file, list_files
// line counts, replace_lines). work-v2 kept its 64 KiB caps unchanged.
const MaxTextFileBytes = 8 << 20

const listFilesLineCountBudget = 32 << 20

// WorkspaceV3Options are the work-v3 additions to the workspace read tools.
type WorkspaceV3Options struct {
	// ScratchDir, when set, is a host directory whose WebScratchDir subtree
	// answers every ".web/..." path instead of the workspace. Used when pages
	// cannot be staged in the workspace view (no workspace, or no staged view).
	ScratchDir string
}

// WorkspaceToolsV3 returns work-v3's list_files and search_text: the work-v2
// tools with the .web archive hidden from workspace-wide calls and list_files
// line counts. read_file lives in the tools package (it shares read_lines'
// numbered form).
func WorkspaceToolsV3(root string, view WorkspaceFS, options WorkspaceV3Options) ([]Tool, error) {
	value, err := newWorkspaceV3(root, view, options)
	if err != nil {
		return nil, err
	}
	return []Tool{&listFilesTool{workspace: value}, &searchTextTool{workspace: value}}, nil
}

// NewWorkspaceResolverV3 is the resolver the work-v3 file tools share: the
// same containment policy plus the scratch mapping and hidden archive.
func NewWorkspaceResolverV3(root string, view WorkspaceFS, options WorkspaceV3Options) (*WorkspaceResolver, error) {
	value, err := newWorkspaceV3(root, view, options)
	if err != nil {
		return nil, err
	}
	return &WorkspaceResolver{workspace: value}, nil
}

func newWorkspaceV3(root string, view WorkspaceFS, options WorkspaceV3Options) (*workspace, error) {
	value, err := newWorkspace(root)
	if err != nil {
		return nil, err
	}
	value.filesystem = view
	value.hidden = WebScratchDir
	value.lineCounts = true
	if options.ScratchDir != "" {
		scratch, err := filepath.Abs(options.ScratchDir)
		if err != nil {
			return nil, err
		}
		value.scratch = scratch
	}
	return value, nil
}

// IsScratchPath reports whether a model-supplied path names the web archive.
func IsScratchPath(path string) bool {
	clean := filepath.ToSlash(filepath.Clean(strings.TrimPrefix(filepath.ToSlash(path), "/workspace/")))
	return clean == WebScratchDir || strings.HasPrefix(clean, WebScratchDir+"/")
}

// resolveScratch maps ".web/..." onto the scratch directory when one is set.
// Those paths are read on the host disk, not through the workspace view.
func (w *workspace) resolveScratch(path string) (string, bool) {
	if w == nil || w.scratch == "" || !IsScratchPath(path) {
		return "", false
	}
	clean := filepath.Clean(strings.TrimPrefix(filepath.ToSlash(path), "/workspace/"))
	return filepath.Join(w.scratch, clean), true
}

// fsFor is the filesystem behind one resolved path: scratch paths always live
// on the host disk.
func (w *workspace) fsFor(target string) WorkspaceFS {
	if w.scratch != "" && (target == w.scratch || strings.HasPrefix(target, w.scratch+string(filepath.Separator))) {
		return DiskWorkspaceFS{}
	}
	return w.fs()
}

// skipHidden reports whether a directory visited by a walk rooted at target is
// the hidden archive and the call did not ask for it.
func (w *workspace) skipHidden(target, path string) bool {
	if w.hidden == "" || filepath.Base(path) != w.hidden {
		return false
	}
	if w.relative(target) != "." {
		return false
	}
	return w.relative(path) == w.hidden
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

// Relative is the workspace-relative display form of a resolved path; scratch
// paths display as ".web/...".
func (r *WorkspaceResolver) Relative(target string) string { return r.workspace.relative(target) }

// FSFor is the filesystem that holds one resolved path.
func (r *WorkspaceResolver) FSFor(target string) WorkspaceFS { return r.workspace.fsFor(target) }
