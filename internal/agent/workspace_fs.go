package agent

import (
	"io"
	"io/fs"
	"os"
	"path/filepath"
)

// WorkspaceFS is shared by all tools in a staged session. Paths are resolved
// absolute host presentation paths; implementations must enforce containment.
type WorkspaceFS interface {
	Open(string) (io.ReadCloser, error)
	Stat(string) (fs.FileInfo, error)
	WalkDir(string, fs.WalkDirFunc) error
	WriteFile(string, []byte, fs.FileMode) error
	MkdirAll(string, fs.FileMode) error
	AppendFile(string, []byte) error
}
type DiskWorkspaceFS struct{}

func (DiskWorkspaceFS) Open(p string) (io.ReadCloser, error)     { return os.Open(p) }
func (DiskWorkspaceFS) Stat(p string) (fs.FileInfo, error)       { return os.Stat(p) }
func (DiskWorkspaceFS) WalkDir(p string, f fs.WalkDirFunc) error { return filepath.WalkDir(p, f) }
func (DiskWorkspaceFS) WriteFile(p string, b []byte, m fs.FileMode) error {
	return os.WriteFile(p, b, m)
}
func (DiskWorkspaceFS) MkdirAll(p string, m fs.FileMode) error { return os.MkdirAll(p, m) }
func (DiskWorkspaceFS) AppendFile(p string, b []byte) error {
	f, e := os.OpenFile(p, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if e != nil {
		return e
	}
	defer f.Close()
	_, e = f.Write(b)
	return e
}
func (r *WorkspaceResolver) FS() WorkspaceFS {
	if r.workspace.filesystem != nil {
		return r.workspace.filesystem
	}
	return DiskWorkspaceFS{}
}
func NewWorkspaceResolverWithFS(root string, view WorkspaceFS) (*WorkspaceResolver, error) {
	r, e := NewWorkspaceResolver(root)
	if e == nil {
		r.workspace.filesystem = view
	}
	return r, e
}
func WorkspaceToolsWithFS(root string, view WorkspaceFS) ([]Tool, error) {
	ts, e := WorkspaceTools(root)
	if e != nil {
		return nil, e
	}
	for _, t := range ts {
		switch v := t.(type) {
		case *listFilesTool:
			v.workspace.filesystem = view
		case *readFileTool:
			v.workspace.filesystem = view
		case *searchTextTool:
			v.workspace.filesystem = view
		}
	}
	return ts, nil
}
func (w *workspace) fs() WorkspaceFS {
	if w.filesystem != nil {
		return w.filesystem
	}
	return DiskWorkspaceFS{}
}
