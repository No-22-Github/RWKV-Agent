package main

import (
	"context"
	"fmt"
	"strings"
	"sync"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/wailsapp/wails/v3/pkg/application"
)

// AppService is the thin Wails binding over the public application API.
type AppService struct {
	service *agentapi.Service

	mu      sync.Mutex
	session *agentapi.Session
	app     *application.App
	closed  bool
}

func newAppService(service *agentapi.Service) *AppService {
	return &AppService{service: service}
}

func (s *AppService) setApplication(app *application.App) {
	s.mu.Lock()
	s.app = app
	s.mu.Unlock()
}

// Status returns the current non-secret model state.
func (s *AppService) Status() agentapi.Status {
	return s.service.Status()
}

// Configure replaces the active local or remote model provider.
func (s *AppService) Configure(ctx context.Context, config agentapi.Config) (agentapi.Status, error) {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return agentapi.Status{}, fmt.Errorf("application service is closed")
	}
	old := s.session
	s.session = nil
	s.mu.Unlock()
	if old != nil {
		_ = old.Close()
	}
	status, err := s.service.Configure(ctx, config, func(value agentapi.Status) {
		s.emit("model:status", value)
	})
	s.emit("model:status", status)
	return status, err
}

// ListRemoteModels verifies remote connectivity and returns model identifiers.
func (s *AppService) ListRemoteModels(ctx context.Context, config agentapi.Config) ([]agentapi.RemoteModel, error) {
	return s.service.ListRemoteModels(ctx, config)
}

// Chat runs one committed Agent turn in the active conversation.
func (s *AppService) Chat(ctx context.Context, prompt string) (agentapi.Result, error) {
	if strings.TrimSpace(prompt) == "" {
		return agentapi.Result{}, fmt.Errorf("message is required")
	}
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return agentapi.Result{}, fmt.Errorf("application service is closed")
	}
	if s.session == nil {
		created, err := s.service.NewSession(ctx)
		if err != nil {
			s.mu.Unlock()
			return agentapi.Result{}, err
		}
		s.session = created
	}
	session := s.session
	s.mu.Unlock()
	result, err := session.RunWithObserver(ctx, prompt, func(event agentapi.Event) {
		s.emit("agent:event", event)
	})
	if err != nil {
		s.emit("agent:error", err.Error())
	}
	return result, err
}

// NewConversation clears the current transcript while preserving the model.
func (s *AppService) NewConversation() error {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return fmt.Errorf("application service is closed")
	}
	if s.session != nil {
		s.session.Reset()
	}
	s.mu.Unlock()
	s.emit("conversation:reset")
	return nil
}

// Close releases the current conversation and model provider.
func (s *AppService) Close() error {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return nil
	}
	s.closed = true
	session := s.session
	s.session = nil
	s.mu.Unlock()
	if session != nil {
		_ = session.Close()
	}
	return s.service.Close()
}

func (s *AppService) emit(name string, data ...any) {
	s.mu.Lock()
	app := s.app
	s.mu.Unlock()
	if app != nil {
		app.Event.Emit(name, data...)
	}
}
