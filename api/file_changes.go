package api

import (
	"context"
	"fmt"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

const stagedFileControl = "本会话的 bash 和所有文件工具共享同一暂存文件系统。新增、修改和删除都只暂存在内存，读回、列目录和搜索会看到暂存后的内容。只有用户在文件改动面板确认后才会写入真实磁盘。回答中应说明文件改动已暂存待确认，不要声称已保存到磁盘。"

type FileChange = assistanttools.FileChange

// NewStagedSession shares a copy-on-write workspace between every file tool
// and child Agent. Only ResolveFileChanges can write reviewed changes to disk.
func (s *Service) NewStagedSession(ctx context.Context) (*Session, error) {
	workspace := s.Status().Workspace
	if workspace == "" {
		return s.NewSession(ctx)
	}
	view, e := assistanttools.NewStagedWorkspace(workspace, "")
	if e != nil {
		return nil, e
	}
	session, e := s.newSessionWithView(ctx, 0, view)
	if e != nil {
		_ = view.Close()
		return nil, e
	}
	session.ownsOverlay = true
	return session, nil
}
func (s *Session) FileChanges() ([]FileChange, error) {
	s.opMu.Lock()
	defer s.opMu.Unlock()
	if s.closed {
		return nil, fmt.Errorf("session is closed")
	}
	if s.overlay == nil {
		return []FileChange{}, nil
	}
	return s.overlay.Changes()
}
func (s *Session) ResolveFileChanges(reviewed []FileChange, accept bool) ([]FileChange, error) {
	s.opMu.Lock()
	defer s.opMu.Unlock()
	if s.closed {
		return nil, fmt.Errorf("session is closed")
	}
	if s.overlay == nil {
		return nil, fmt.Errorf("session has no staged workspace")
	}
	return s.overlay.Resolve(reviewed, accept)
}
