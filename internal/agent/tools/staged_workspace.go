package tools

import (
	"bytes"
	"context"
	"crypto/rand"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/no22/RWKV-Agent/internal/agent"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"syscall"
	"time"
)

type FileSnapshot struct {
	Kind string `json:"kind"`
	Data string `json:"data,omitempty"`
	Mode uint32 `json:"mode,omitempty"`
}

// FileChange carries exact bytes (base64), including binary files and modes.
type FileChange struct {
	Path   string       `json:"path"`
	Before FileSnapshot `json:"before"`
	After  FileSnapshot `json:"after"`
}
type StagedWorkspace struct {
	execution        sync.Mutex
	mu               sync.Mutex
	root, binary, id string
	revision         int64
	closed           bool
}

func NewStagedWorkspace(root, binary string) (*StagedWorkspace, error) {
	root, e := filepath.EvalSymlinks(root)
	if e != nil {
		return nil, e
	}
	binary, e = ResolveBashSidecar(binary)
	if e != nil {
		return nil, e
	}
	var id [16]byte
	if _, e = rand.Read(id[:]); e != nil {
		return nil, e
	}
	w := &StagedWorkspace{root: root, binary: binary, id: hex.EncodeToString(id[:])}
	_, e = w.call(bashSidecarRequest{Op: "init"})
	return w, e
}
func (w *StagedWorkspace) call(r bashSidecarRequest) (bashSidecarResponse, error) {
	if w.closed {
		return bashSidecarResponse{}, fmt.Errorf("staged workspace is closed")
	}
	c, e := sharedBashSidecar(w.binary)
	if e != nil {
		return bashSidecarResponse{}, e
	}
	r.Root = w.root
	r.Session = w.id
	out, e := c.run(context.Background(), r, 30*time.Second)
	if e == nil && out.Error != "" {
		e = fmt.Errorf("workspace: %s", out.Error)
	}
	if e == nil {
		w.revision = out.Revision
	}
	return out, e
}
func (w *StagedWorkspace) relative(p string) (string, error) {
	rel, e := filepath.Rel(w.root, p)
	if e != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(filepath.Separator)) {
		return "", fmt.Errorf("path escapes workspace")
	}
	return filepath.ToSlash(rel), nil
}
func (w *StagedWorkspace) operation(op, p, data string) (bashSidecarResponse, error) {
	rel, e := w.relative(p)
	if e != nil {
		return bashSidecarResponse{}, e
	}
	w.mu.Lock()
	defer w.mu.Unlock()
	return w.call(bashSidecarRequest{Op: op, Path: rel, Data: data})
}
func (w *StagedWorkspace) Open(p string) (io.ReadCloser, error) {
	r, e := w.operation("read", p, "")
	if e != nil {
		return nil, e
	}
	b, e := base64.StdEncoding.DecodeString(r.Data)
	return io.NopCloser(bytes.NewReader(b)), e
}

type overlayStat struct {
	Directory bool      `json:"directory"`
	Symlink   bool      `json:"symlink"`
	SizeBytes int64     `json:"size"`
	FileMode  uint32    `json:"mode"`
	Mtime     time.Time `json:"mtime"`
	name      string
}

func (s overlayStat) Name() string { return s.name }
func (s overlayStat) Size() int64  { return s.SizeBytes }
func (s overlayStat) Mode() fs.FileMode {
	m := fs.FileMode(s.FileMode) & 0777
	if s.Directory {
		m |= fs.ModeDir
	}
	if s.Symlink {
		m |= fs.ModeSymlink
	}
	return m
}
func (s overlayStat) ModTime() time.Time { return s.Mtime }
func (s overlayStat) IsDir() bool        { return s.Directory }
func (s overlayStat) Sys() any           { return nil }
func (w *StagedWorkspace) Stat(p string) (fs.FileInfo, error) {
	r, e := w.operation("stat", p, "")
	r.Stat.name = filepath.Base(p)
	return r.Stat, e
}
func (w *StagedWorkspace) WalkDir(p string, visit fs.WalkDirFunc) error {
	info, e := w.Stat(p)
	if e != nil {
		return visit(p, nil, e)
	}
	var walk func(string, fs.FileInfo) error
	walk = func(p string, info fs.FileInfo) error {
		e := visit(p, fs.FileInfoToDirEntry(info), nil)
		if e == fs.SkipDir && info.IsDir() {
			return nil
		}
		if e != nil {
			return e
		}
		if !info.IsDir() {
			return nil
		}
		r, e := w.operation("list", p, "")
		if e != nil {
			return visit(p, fs.FileInfoToDirEntry(info), e)
		}
		sort.Strings(r.Names)
		for _, n := range r.Names {
			child := filepath.Join(p, n)
			i, e := w.Stat(child)
			if e != nil {
				e = visit(child, nil, e)
			} else {
				e = walk(child, i)
			}
			if e == fs.SkipDir {
				break
			}
			if e != nil {
				return e
			}
		}
		return nil
	}
	e = walk(p, info)
	if e == fs.SkipAll {
		return nil
	}
	return e
}
func (w *StagedWorkspace) WriteFile(p string, b []byte, _ fs.FileMode) error {
	_, e := w.operation("write", p, base64.StdEncoding.EncodeToString(b))
	return e
}
func (w *StagedWorkspace) MkdirAll(p string, _ fs.FileMode) error {
	_, e := w.operation("mkdir", p, "")
	return e
}
func (w *StagedWorkspace) AppendFile(p string, b []byte) error {
	_, e := w.operation("append", p, base64.StdEncoding.EncodeToString(b))
	return e
}
func (w *StagedWorkspace) Changes() ([]FileChange, error) {
	w.mu.Lock()
	defer w.mu.Unlock()
	r, e := w.call(bashSidecarRequest{Op: "changes"})
	if r.Changes == nil {
		r.Changes = []FileChange{}
	}
	return r.Changes, e
}
func (w *StagedWorkspace) Close() error {
	w.mu.Lock()
	defer w.mu.Unlock()
	if w.closed {
		return nil
	}
	_, e := w.call(bashSidecarRequest{Close: true})
	w.closed = true
	return e
}

// Resolve accepts exactly the reviewed revisions. A mismatch aborts before any
// disk operation. On I/O failure, already applied files are acknowledged and
// remaining files stay staged for retry. Directories are never recursively
// deleted on disk, so a newly created external file cannot be removed.
func (w *StagedWorkspace) Resolve(reviewed []FileChange, accept bool) ([]FileChange, error) {
	w.mu.Lock()
	defer w.mu.Unlock()
	r, e := w.call(bashSidecarRequest{Op: "changes"})
	if e != nil {
		return nil, e
	}
	current := map[string]FileChange{}
	for _, c := range r.Changes {
		current[c.Path] = c
	}
	selected := map[string]FileChange{}
	for _, c := range reviewed {
		actual, ok := current[c.Path]
		if !ok || actual != c {
			return nil, fmt.Errorf("%s changed since review; refresh the changes", c.Path)
		}
		selected[c.Path] = c
	}
	// Directory choices include their children; accepted files also create their
	// staged ancestor directories, as a single dependency group.
	for _, c := range reviewed {
		if c.Before.Kind == "directory" || c.After.Kind == "directory" {
			for p, child := range current {
				if strings.HasPrefix(p, c.Path+"/") {
					if _, ok := selected[p]; !ok {
						return nil, fmt.Errorf("%s requires reviewing child %s together", c.Path, child.Path)
					}
				}
			}
		}
		if accept {
			for parent := filepath.ToSlash(filepath.Dir(c.Path)); parent != "."; parent = filepath.ToSlash(filepath.Dir(parent)) {
				if a, ok := current[parent]; ok && a.Before.Kind == "missing" && a.After.Kind == "directory" {
					selected[parent] = a
				}
			}
		}
	}
	list := make([]FileChange, 0, len(selected))
	for _, c := range selected {
		list = append(list, c)
	}
	if accept {
		for _, c := range list {
			snap, e := w.diskSnapshot(c.Path)
			if e != nil {
				return nil, e
			}
			if snap != c.Before {
				return nil, fmt.Errorf("%s was modified outside the app; discard this staged change and edit again from the disk version", c.Path)
			}
		}
		sort.Slice(list, func(i, j int) bool {
			a, b := list[i], list[j]
			if (a.After.Kind == "missing") != (b.After.Kind == "missing") {
				return a.After.Kind == "missing"
			}
			if a.After.Kind == "missing" {
				return len(a.Path) > len(b.Path)
			}
			return len(a.Path) < len(b.Path)
		})
	}
	resolved := []string{}
	for _, c := range list {
		if accept {
			if e = w.apply(c); e != nil {
				break
			}
		}
		resolved = append(resolved, c.Path)
	}
	if len(resolved) > 0 {
		_, ackErr := w.call(bashSidecarRequest{Op: "forget", Paths: resolved})
		if ackErr != nil {
			return nil, fmt.Errorf("resolution acknowledgment failed: %w", ackErr)
		}
	}
	out, readErr := w.call(bashSidecarRequest{Op: "changes"})
	if e != nil {
		return out.Changes, e
	}
	return out.Changes, readErr
}
func (w *StagedWorkspace) diskSnapshot(rel string) (FileSnapshot, error) {
	if rel == "." || filepath.IsAbs(rel) || filepath.Clean(rel) != rel {
		return FileSnapshot{}, fmt.Errorf("invalid review path")
	}
	p := w.root
	for _, part := range strings.Split(filepath.ToSlash(rel), "/") {
		if part == ".." {
			return FileSnapshot{}, fmt.Errorf("path escapes workspace")
		}
		p = filepath.Join(p, part)
		i, e := os.Lstat(p)
		if os.IsNotExist(e) || errors.Is(e, syscall.ENOTDIR) {
			return FileSnapshot{Kind: "missing"}, nil
		}
		if e != nil {
			return FileSnapshot{}, e
		}
		if i.Mode()&os.ModeSymlink != 0 {
			return FileSnapshot{}, fmt.Errorf("%s: symlink changed outside app", rel)
		}
	}
	i, e := os.Lstat(p)
	if e != nil {
		return FileSnapshot{}, e
	}
	s := FileSnapshot{Kind: "directory", Mode: uint32(i.Mode().Perm())}
	if !i.IsDir() {
		if !i.Mode().IsRegular() {
			return s, fmt.Errorf("unsupported disk entry")
		}
		b, e := os.ReadFile(p)
		if e != nil {
			return s, e
		}
		s.Kind = "file"
		s.Data = base64.StdEncoding.EncodeToString(b)
	}
	return s, nil
}
func (w *StagedWorkspace) apply(c FileChange) error {
	// Recheck just before writing. os.Root contains operations even if a parent
	// is replaced with a symlink between validation and the write.
	s, e := w.diskSnapshot(c.Path)
	if e != nil {
		return e
	}
	if s != c.Before {
		return fmt.Errorf("%s changed while applying", c.Path)
	}
	root, e := os.OpenRoot(w.root)
	if e != nil {
		return e
	}
	defer root.Close()
	switch c.After.Kind {
	case "missing":
		if c.Before.Kind == "missing" {
			return nil
		}
		return root.Remove(c.Path)
	case "directory":
		if c.Before.Kind == "file" {
			if e = root.Remove(c.Path); e != nil {
				return e
			}
		}
		if e = root.MkdirAll(c.Path, fs.FileMode(c.After.Mode)); e != nil {
			return e
		}
		return root.Chmod(c.Path, fs.FileMode(c.After.Mode))
	case "file":
		b, e := base64.StdEncoding.DecodeString(c.After.Data)
		if e != nil {
			return e
		}
		if c.Before.Kind == "directory" {
			if e = root.Remove(c.Path); e != nil {
				return e
			}
		}
		// Atomic replacement in the same directory; preserve final permissions.
		var token [12]byte
		_, e = rand.Read(token[:])
		if e != nil {
			return e
		}
		tmp := filepath.Join(filepath.Dir(c.Path), ".rwkv-review-"+hex.EncodeToString(token[:]))
		f, e := root.OpenFile(tmp, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0600)
		if e != nil {
			return e
		}
		defer root.Remove(tmp)
		_, e = f.Write(b)
		if e == nil {
			e = f.Chmod(fs.FileMode(c.After.Mode))
		}
		if e == nil {
			e = f.Sync()
		}
		closeErr := f.Close()
		if e != nil {
			return e
		}
		if closeErr != nil {
			return closeErr
		}
		return root.Rename(tmp, c.Path)
	default:
		return fmt.Errorf("unsupported staged entry")
	}
}

// Serialize whole file tool calls, including native read-modify-write edits,
// across the parent and its children. Sidecar requests also serialize by id.
func (w *StagedWorkspace) WrapTools(tools []agent.Tool) []agent.Tool {
	result := make([]agent.Tool, len(tools))
	copy(result, tools)
	for i, t := range result {
		if t.Spec().Permission == agent.PermissionWorkspaceRead || t.Spec().Permission == agent.PermissionWorkspaceWrite {
			result[i] = stagedTool{Tool: t, workspace: w}
		}
	}
	return result
}

type stagedTool struct {
	agent.Tool
	workspace *StagedWorkspace
}

func (t stagedTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	t.workspace.execution.Lock()
	defer t.workspace.execution.Unlock()
	if e := ctx.Err(); e != nil {
		return nil, e
	}
	return t.Tool.Execute(ctx, raw)
}
