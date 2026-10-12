package main

import (
	"fmt"
	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
)

// FileChanges returns pending changes for the active conversation, including
// changes left by interrupted or failed turns.
func (s *AppService) FileChanges() ([]agentapi.FileChange, error) {
	s.operation.Lock()
	defer s.operation.Unlock()
	return s.fileChanges()
}
func (s *AppService) fileChanges() ([]agentapi.FileChange, error) {
	s.mu.Lock()
	session := s.session
	s.mu.Unlock()
	if session == nil {
		return []agentapi.FileChange{}, nil
	}
	return session.FileChanges()
}
func (s *AppService) ResolveFileChanges(reviewed []agentapi.FileChange, accept bool) ([]agentapi.FileChange, error) {
	s.operation.Lock()
	defer s.operation.Unlock()
	s.mu.Lock()
	session := s.session
	s.mu.Unlock()
	if session == nil {
		return nil, fmt.Errorf("当前对话没有待确认改动")
	}
	before, _ := session.FileChanges()
	changes, e := session.ResolveFileChanges(reviewed, accept)
	// A failed apply can still have saved some files. Record only proposals
	// removed from the pending view, and leave unresolved decisions untouched.
	if current, readErr := session.FileChanges(); readErr == nil {
		remaining := map[string]agentapi.FileChange{}
		for _, c := range current {
			remaining[c.Path] = c
		}
		resolved := map[string]agentapi.FileChange{}
		for _, c := range before {
			if _, ok := remaining[c.Path]; !ok {
				resolved[c.Path] = c
			}
		}
		s.mu.Lock()
		active := s.active
		s.mu.Unlock()
		if active != nil && len(resolved) > 0 {
			status := "discarded"
			if accept {
				status = "saved"
			}
			for i := range active.Messages {
				for j := range active.Messages[i].Files {
					file := &active.Messages[i].Files[j]
					if c, ok := resolved[file.Change.Path]; ok && file.Status == "pending" && file.Change == c {
						file.Status = status
					}
				}
			}
			if saveErr := s.storage.SaveConversation(*active); saveErr != nil && e == nil {
				e = fmt.Errorf("文件已处理，但保存展示记录失败: %w", saveErr)
			}
		}
	}
	s.emit("workspace:changes", changes)
	return changes, e
}
func (s *AppService) requireResolvedChanges() error {
	changes, e := s.fileChanges()
	if e != nil {
		return e
	}
	if len(changes) > 0 {
		return fmt.Errorf("当前对话还有 %d 项文件改动未确认，请先在文件改动面板中保存或丢弃", len(changes))
	}
	return nil
}

func turnFileArtifacts(before, after []agentapi.FileChange) []appstorage.FileArtifact {
	previous := map[string]agentapi.FileChange{}
	for _, c := range before {
		previous[c.Path] = c
	}
	var files []appstorage.FileArtifact
	for _, c := range after {
		if old, ok := previous[c.Path]; !ok || old != c {
			files = append(files, appstorage.FileArtifact{Change: c, Status: "pending"})
		}
	}
	return files
}
