package api

import (
	"context"
	"errors"
	"fmt"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

type FileChange = assistanttools.FileChange

// NewStagedSession shares a copy-on-write workspace between every file tool
// and child Agent. Only ResolveFileChanges can write reviewed changes to disk.
func (s *Service) NewStagedSession(ctx context.Context) (*Session, error) {
	workspace := s.Status().Workspace
	if workspace == "" {
		return s.NewSession(ctx)
	}
	view, e := assistanttools.NewStagedWorkspace(workspace, "")
	if errors.Is(e, assistanttools.ErrBashSidecarMissing) {
		// The staged view runs on the just-bash sidecar. Without it the session
		// still opens, with read-only file tools and no bash, rather than failing.
		return s.NewSession(ctx)
	}
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
