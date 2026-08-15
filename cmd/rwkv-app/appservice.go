package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"sync"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
	"github.com/wailsapp/wails/v3/pkg/application"
)

// DisplayMessage is one presentation-level message retained for the desktop
// UI. The complete Harness transcript is stored separately and never trimmed
// down to this view.
type DisplayMessage struct {
	ID         string           `json:"id"`
	Role       string           `json:"role"`
	Content    string           `json:"content"`
	Meta       string           `json:"meta,omitempty"`
	Trajectory []ToolTrace      `json:"trajectory,omitempty"`
	Trace      *agentapi.Result `json:"trace,omitempty"`
	CreatedAt  time.Time        `json:"createdAt,omitempty"`
}

type ToolTrace struct {
	Step      int              `json:"step"`
	Tool      string           `json:"tool"`
	Arguments string           `json:"arguments,omitempty"`
	Status    string           `json:"status"`
	Error     string           `json:"error,omitempty"`
	Retries   []ToolRetryTrace `json:"retries,omitempty"`
	Subagents []SubagentTrace  `json:"subagents,omitempty"`
}

type ToolRetryTrace struct {
	Attempt     int   `json:"attempt"`
	MaxAttempts int   `json:"maxAttempts"`
	StatusCode  int   `json:"statusCode,omitempty"`
	DelayMS     int64 `json:"delayMs"`
}

type SubagentStep struct {
	Step      int              `json:"step"`
	Tool      string           `json:"tool"`
	Arguments string           `json:"arguments,omitempty"`
	Status    string           `json:"status"`
	Error     string           `json:"error,omitempty"`
	Retries   []ToolRetryTrace `json:"retries,omitempty"`
}

type SubagentTrace struct {
	Index      int            `json:"index"`
	Task       string         `json:"task"`
	Status     string         `json:"status"`
	Error      string         `json:"error,omitempty"`
	Route      string         `json:"route,omitempty"`
	Bundles    []string       `json:"bundles,omitempty"`
	DurationMS int64          `json:"durationMs"`
	Output     string         `json:"output,omitempty"`
	Sources    []string       `json:"sources,omitempty"`
	Steps      []SubagentStep `json:"steps,omitempty"`
}

type ConversationSummary struct {
	ID        string    `json:"id"`
	Title     string    `json:"title"`
	UpdatedAt time.Time `json:"updatedAt"`
}

type ConversationView struct {
	ID        string           `json:"id"`
	Title     string           `json:"title"`
	Messages  []DisplayMessage `json:"messages"`
	CreatedAt time.Time        `json:"createdAt"`
	UpdatedAt time.Time        `json:"updatedAt"`
}

type WorkspaceItem struct {
	Path      string `json:"path"`
	Name      string `json:"name"`
	Available bool   `json:"available"`
	Active    bool   `json:"active"`
}

type StoragePaths struct {
	ConfigFile     string `json:"configFile"`
	DataDirectory  string `json:"dataDirectory"`
	StateFile      string `json:"stateFile"`
	CacheDirectory string `json:"cacheDirectory"`
}

type AppBootstrap struct {
	Status        agentapi.Status       `json:"status"`
	Config        agentapi.Config       `json:"config"`
	HasConfig     bool                  `json:"hasConfig"`
	Conversations []ConversationSummary `json:"conversations"`
	Conversation  *ConversationView     `json:"conversation,omitempty"`
	Workspaces    []WorkspaceItem       `json:"workspaces"`
	Paths         StoragePaths          `json:"paths"`
	Warning       string                `json:"warning,omitempty"`
}

// AppService binds durable application state to the public Agent API.
type AppService struct {
	operation sync.Mutex
	mu        sync.Mutex
	service   *agentapi.Service
	storage   *appstorage.Store
	session   *agentapi.Session
	active    *appstorage.Conversation
	config    agentapi.Config
	hasConfig bool
	app       *application.App
	warning   string
	closed    bool
}

func newAppService(service *agentapi.Service, storage *appstorage.Store) *AppService {
	backend := &AppService{service: service, storage: storage}
	if err := storage.Prepare(); err != nil {
		backend.warning = fmt.Sprintf("准备应用存储目录失败：%v", err)
	}
	if settings, err := storage.LoadSettings(); err != nil {
		backend.warning = joinWarning(backend.warning, fmt.Sprintf("读取设置失败：%v", err))
	} else if strings.TrimSpace(settings.Provider.Model) != "" {
		backend.config = settings.Provider
		backend.hasConfig = true
	}
	// 不要在这里持久化工作区：启动时的工作区可能是默认值（用户主目录），
	// 只有用户通过“打开工作区”主动选择后才应该被记住。
	backend.loadActiveConversation()
	return backend
}

func (s *AppService) setApplication(app *application.App) {
	s.mu.Lock()
	s.app = app
	s.mu.Unlock()
}

// Bootstrap returns all durable state needed to hydrate the frontend.
func (s *AppService) Bootstrap() (AppBootstrap, error) {
	s.operation.Lock()
	defer s.operation.Unlock()
	return s.bootstrap()
}

// Status returns the current non-secret model state.
func (s *AppService) Status() agentapi.Status {
	s.mu.Lock()
	service := s.service
	s.mu.Unlock()
	return service.Status()
}

// Configure replaces the active provider and persists the complete settings,
// including credentials, in the XDG configuration file.
func (s *AppService) Configure(ctx context.Context, config agentapi.Config) (agentapi.Status, error) {
	s.operation.Lock()
	defer s.operation.Unlock()
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return agentapi.Status{}, fmt.Errorf("application service is closed")
	}
	service := s.service
	old := s.session
	s.session = nil
	s.mu.Unlock()
	if old != nil {
		_ = old.Close()
	}
	status, err := service.Configure(ctx, config, func(value agentapi.Status) {
		s.emit("model:status", value)
	})
	s.emit("model:status", status)
	if err != nil {
		return status, err
	}
	if err := s.storage.SaveSettings(config); err != nil {
		return status, fmt.Errorf("模型已配置，但保存设置失败: %w", err)
	}
	s.mu.Lock()
	s.config = config
	s.hasConfig = true
	s.mu.Unlock()
	return status, nil
}

// ListRemoteModels verifies remote connectivity and returns model identifiers.
func (s *AppService) ListRemoteModels(ctx context.Context, config agentapi.Config) ([]agentapi.RemoteModel, error) {
	s.mu.Lock()
	service := s.service
	s.mu.Unlock()
	return service.ListRemoteModels(ctx, config)
}

// Chat runs and durably commits one Agent turn in the active conversation.
func (s *AppService) Chat(ctx context.Context, prompt string) (agentapi.Result, error) {
	if strings.TrimSpace(prompt) == "" {
		return agentapi.Result{}, fmt.Errorf("message is required")
	}
	s.operation.Lock()
	defer s.operation.Unlock()
	session, err := s.ensureSession(ctx)
	if err != nil {
		return agentapi.Result{}, err
	}
	turnStarted := time.Now().UTC()
	result, err := session.RunWithObserver(ctx, prompt, func(event agentapi.Event) {
		s.emit("agent:event", event)
	})
	role := "assistant"
	content := result.Output
	if err != nil {
		result.Error = err.Error()
		role = "error"
		content = err.Error()
		s.emit("agent:error", err.Error())
	}
	if persistErr := s.persistTurn(session, prompt, role, content, result, turnStarted); persistErr != nil {
		if err != nil {
			return result, errors.Join(err, persistErr)
		}
		return result, persistErr
	}
	return result, err
}
func (s *AppService) persistTurn(session *agentapi.Session, prompt, role, content string, result agentapi.Result, turnStarted time.Time) error {
	s.mu.Lock()
	active := s.active
	workspace := s.service.Status().Workspace
	s.mu.Unlock()
	if active == nil {
		created, createErr := appstorage.NewConversation(workspace, prompt)
		if createErr != nil {
			return createErr
		}
		active = &created
	}
	active.Messages = append(active.Messages,
		appstorage.DisplayMessage{
			ID: messageID(active.ID, len(active.Messages)), Role: "user",
			Content: strings.TrimSpace(prompt), CreatedAt: turnStarted,
		},
		appstorage.DisplayMessage{
			ID: messageID(active.ID, len(active.Messages)+1), Role: role, Content: content,
			Meta:       fmt.Sprintf("%d 步 · %.1f 秒", len(result.Steps), float64(result.DurationMS)/1000),
			Trajectory: storedToolTrace(result),
			Trace:      &result,
			CreatedAt:  time.Now().UTC(),
		},
	)
	active.Transcript = session.History()
	if err := s.storage.SaveConversation(*active); err != nil {
		return fmt.Errorf("保存对话失败: %w", err)
	}
	saved, err := s.loadSavedConversation(active.ID)
	if err != nil {
		return fmt.Errorf("重新读取已保存对话失败: %w", err)
	}
	active = saved
	if err := s.storage.SetActiveConversation(workspace, active.ID); err != nil {
		return fmt.Errorf("保存当前对话失败: %w", err)
	}
	s.mu.Lock()
	s.active = active
	s.mu.Unlock()
	s.emit("conversation:saved", conversationView(*active))
	return nil
}

// NewConversation starts a blank durable conversation while preserving the
// configured provider.
func (s *AppService) NewConversation() error {
	s.operation.Lock()
	defer s.operation.Unlock()
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return fmt.Errorf("application service is closed")
	}
	old := s.session
	s.session = nil
	s.active = nil
	workspace := s.service.Status().Workspace
	s.mu.Unlock()
	if old != nil {
		_ = old.Close()
	}
	if err := s.storage.SetActiveConversation(workspace, ""); err != nil {
		return err
	}
	s.emit("conversation:reset")
	return nil
}

// OpenConversation selects an existing conversation for display and semantic
// continuation. Its Harness transcript is restored lazily when the next turn
// runs.
func (s *AppService) OpenConversation(id string) (ConversationView, error) {
	s.operation.Lock()
	defer s.operation.Unlock()
	value, err := s.storage.LoadConversation(id)
	if err != nil {
		return ConversationView{}, err
	}
	s.mu.Lock()
	workspace := s.service.Status().Workspace
	if !sameWorkspace(value.Workspace, workspace) {
		s.mu.Unlock()
		return ConversationView{}, fmt.Errorf("conversation belongs to another workspace")
	}
	old := s.session
	s.session = nil
	s.active = &value
	s.mu.Unlock()
	if old != nil {
		_ = old.Close()
	}
	if err := s.storage.SetActiveConversation(workspace, id); err != nil {
		return ConversationView{}, err
	}
	return conversationView(value), nil
}

// DeleteConversation removes one saved conversation.
func (s *AppService) DeleteConversation(id string) error {
	s.operation.Lock()
	defer s.operation.Unlock()
	s.mu.Lock()
	active := s.active != nil && s.active.ID == id
	workspace := s.service.Status().Workspace
	var old *agentapi.Session
	if active {
		old = s.session
		s.session = nil
		s.active = nil
	}
	s.mu.Unlock()
	if old != nil {
		_ = old.Close()
	}
	if err := s.storage.DeleteConversation(id); err != nil {
		return err
	}
	if active {
		return s.storage.SetActiveConversation(workspace, "")
	}
	return nil
}

// ChooseWorkspace opens the platform-native directory picker. Server builds
// return the Wails "file dialogs not available" error.
func (s *AppService) ChooseWorkspace() (AppBootstrap, error) {
	s.mu.Lock()
	app := s.app
	s.mu.Unlock()
	if app == nil {
		return AppBootstrap{}, fmt.Errorf("application is not ready")
	}
	selected, err := app.Dialog.OpenFile().
		CanChooseFiles(false).
		CanChooseDirectories(true).
		SetTitle("选择工作区").
		PromptForSingleSelection()
	if err != nil {
		return AppBootstrap{}, err
	}
	if strings.TrimSpace(selected) == "" {
		return s.Bootstrap()
	}
	return s.OpenWorkspace(selected)
}

// OpenWorkspace switches to an existing directory and unloads the current
// provider. Persisted model settings remain available for reconnection.
func (s *AppService) OpenWorkspace(path string) (AppBootstrap, error) {
	s.operation.Lock()
	defer s.operation.Unlock()
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return AppBootstrap{}, fmt.Errorf("application service is closed")
	}
	s.mu.Unlock()
	service, err := agentapi.NewService(agentapi.Options{Workspace: path})
	if err != nil {
		return AppBootstrap{}, err
	}
	if _, err := s.storage.RememberWorkspace(service.Status().Workspace); err != nil {
		_ = service.Close()
		return AppBootstrap{}, err
	}
	s.mu.Lock()
	oldService := s.service
	oldSession := s.session
	s.service = service
	s.session = nil
	s.active = nil
	s.mu.Unlock()
	if oldSession != nil {
		_ = oldSession.Close()
	}
	if oldService != nil {
		_ = oldService.Close()
	}
	s.loadActiveConversation()
	s.emit("model:status", service.Status())
	return s.bootstrap()
}

// ExportTrajectory shows a native save dialog and writes the given JSONL
// content to the chosen path. Returns the written path, or "" when the user
// cancels the dialog.
func (s *AppService) ExportTrajectory(content string) (string, error) {
	app := s.app
	if app == nil || app.Dialog == nil {
		return "", errors.New("桌面窗口不可用")
	}
	dialog := app.Dialog.SaveFile()
	dialog.SetOptions(&application.SaveFileDialogOptions{
		Title:    "导出轨迹",
		Filename: "rwkv-agent-trajectory.jsonl",
		Message:  "将当前可见的轨迹保存为 JSONL",
	})
	dialog.AddFilter("JSONL", "*.jsonl")
	dialog.AddFilter("所有文件", "*")
	path, err := dialog.PromptForSingleSelection()
	if err != nil {
		return "", err
	}
	if path == "" {
		return "", nil // 用户取消
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		return "", fmt.Errorf("写入轨迹文件失败: %w", err)
	}
	return path, nil
}

// Close releases the current conversation and model provider.
func (s *AppService) Close() error {
	s.operation.Lock()
	defer s.operation.Unlock()
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return nil
	}
	s.closed = true
	session := s.session
	service := s.service
	s.session = nil
	s.mu.Unlock()
	if session != nil {
		_ = session.Close()
	}
	return service.Close()
}

func (s *AppService) ensureSession(ctx context.Context) (*agentapi.Session, error) {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return nil, fmt.Errorf("application service is closed")
	}
	if s.session != nil {
		result := s.session
		s.mu.Unlock()
		return result, nil
	}
	service := s.service
	active := s.active
	s.mu.Unlock()
	created, err := service.NewSession(ctx)
	if err != nil {
		return nil, err
	}
	if active != nil && len(active.Transcript) > 0 {
		if err := created.RestoreHistory(active.Transcript); err != nil {
			_ = created.Close()
			return nil, fmt.Errorf("恢复对话失败: %w", err)
		}
	}
	s.mu.Lock()
	if s.closed || s.service != service {
		s.mu.Unlock()
		_ = created.Close()
		return nil, fmt.Errorf("workspace changed while creating conversation")
	}
	s.session = created
	s.mu.Unlock()
	return created, nil
}

func (s *AppService) bootstrap() (AppBootstrap, error) {
	s.mu.Lock()
	service := s.service
	config := s.config
	hasConfig := s.hasConfig
	active := s.active
	warning := s.warning
	s.mu.Unlock()
	status := service.Status()
	summaries, err := s.storage.ListConversations(status.Workspace)
	if err != nil {
		return AppBootstrap{}, err
	}
	state, err := s.storage.LoadState()
	if err != nil {
		return AppBootstrap{}, err
	}
	paths := s.storage.Paths()
	result := AppBootstrap{
		Status: status, Config: config, HasConfig: hasConfig,
		Conversations: conversationSummaries(summaries),
		Workspaces:    workspaceItems(state.RecentWorkspaces, status.Workspace),
		Paths: StoragePaths{
			ConfigFile: paths.ConfigFile, DataDirectory: paths.DataDirectory,
			StateFile: paths.StateFile, CacheDirectory: paths.CacheDirectory,
		},
		Warning: warning,
	}
	if active != nil {
		view := conversationView(*active)
		result.Conversation = &view
	}
	return result, nil
}

func (s *AppService) loadActiveConversation() {
	s.mu.Lock()
	workspace := s.service.Status().Workspace
	s.mu.Unlock()
	id, err := s.storage.ActiveConversation(workspace)
	if err != nil {
		s.mu.Lock()
		s.warning = joinWarning(s.warning, fmt.Sprintf("读取应用状态失败：%v", err))
		s.mu.Unlock()
		return
	}
	if id == "" {
		return
	}
	value, err := s.storage.LoadConversation(id)
	if err != nil || !sameWorkspace(value.Workspace, workspace) {
		return
	}
	s.mu.Lock()
	s.active = &value
	s.mu.Unlock()
}

func (s *AppService) loadSavedConversation(id string) (*appstorage.Conversation, error) {
	value, err := s.storage.LoadConversation(id)
	if err != nil {
		return nil, err
	}
	return &value, nil
}

func (s *AppService) emit(name string, data ...any) {
	s.mu.Lock()
	app := s.app
	s.mu.Unlock()
	if app != nil {
		app.Event.Emit(name, data...)
	}
}

func conversationSummaries(values []appstorage.Summary) []ConversationSummary {
	result := make([]ConversationSummary, 0, len(values))
	for _, value := range values {
		result = append(result, ConversationSummary{ID: value.ID, Title: value.Title, UpdatedAt: value.UpdatedAt})
	}
	return result
}

func conversationView(value appstorage.Conversation) ConversationView {
	messages := make([]DisplayMessage, 0, len(value.Messages))
	for _, message := range value.Messages {
		messages = append(messages, DisplayMessage{
			ID: message.ID, Role: message.Role, Content: message.Content, Meta: message.Meta,
			Trajectory: displayToolTrace(message.Trajectory), Trace: message.Trace, CreatedAt: message.CreatedAt,
		})
	}
	return ConversationView{
		ID: value.ID, Title: value.Title, Messages: messages,
		CreatedAt: value.CreatedAt, UpdatedAt: value.UpdatedAt,
	}
}

func storedToolTrace(result agentapi.Result) []appstorage.ToolTrace {
	trace := make([]appstorage.ToolTrace, 0, len(result.Steps))
	for _, step := range result.Steps {
		if strings.TrimSpace(step.Tool) == "" {
			continue
		}
		status := "completed"
		if step.ToolError != "" {
			status = "failed"
		}
		trace = append(trace, appstorage.ToolTrace{
			Step: step.Number, Tool: step.Tool, Arguments: step.ToolArguments,
			Status: status, Error: step.ToolError, Retries: storedToolRetries(step.ToolRetries),
			Subagents: storedSubagentTrace(step.Subagents),
		})
	}
	return trace
}

func displayToolTrace(values []appstorage.ToolTrace) []ToolTrace {
	if len(values) == 0 {
		return nil
	}
	trace := make([]ToolTrace, 0, len(values))
	for _, value := range values {
		trace = append(trace, ToolTrace{
			Step: value.Step, Tool: value.Tool, Arguments: value.Arguments,
			Status: value.Status, Error: value.Error, Retries: displayToolRetries(value.Retries),
			Subagents: displaySubagentTrace(value.Subagents),
		})
	}
	return trace
}

func storedSubagentTrace(values []agentapi.SubagentTrace) []appstorage.SubagentTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]appstorage.SubagentTrace, 0, len(values))
	for _, value := range values {
		child := appstorage.SubagentTrace{
			Index: value.Index, Task: value.Task, Status: value.Status, Error: value.Error,
			Route: value.Route, Bundles: append([]string(nil), value.Bundles...),
			DurationMS: value.DurationMS, Output: value.Output,
			Sources: append([]string(nil), value.Sources...),
		}
		for _, step := range value.Steps {
			child.Steps = append(child.Steps, appstorage.SubagentStep{
				Step: step.Number, Tool: step.Tool, Arguments: step.Arguments,
				Status: step.Status, Error: step.Error, Retries: storedToolRetries(step.Retries),
			})
		}
		result = append(result, child)
	}
	return result
}

func displaySubagentTrace(values []appstorage.SubagentTrace) []SubagentTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]SubagentTrace, 0, len(values))
	for _, value := range values {
		child := SubagentTrace{
			Index: value.Index, Task: value.Task, Status: value.Status, Error: value.Error,
			Route: value.Route, Bundles: append([]string(nil), value.Bundles...),
			DurationMS: value.DurationMS, Output: value.Output,
			Sources: append([]string(nil), value.Sources...),
		}
		for _, step := range value.Steps {
			child.Steps = append(child.Steps, SubagentStep{
				Step: step.Step, Tool: step.Tool, Arguments: step.Arguments,
				Status: step.Status, Error: step.Error, Retries: displayToolRetries(step.Retries),
			})
		}
		result = append(result, child)
	}
	return result
}

func storedToolRetries(values []agentapi.ToolRetryTrace) []appstorage.ToolRetryTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]appstorage.ToolRetryTrace, 0, len(values))
	for _, value := range values {
		result = append(result, appstorage.ToolRetryTrace{
			Attempt: value.Attempt, MaxAttempts: value.MaxAttempts,
			StatusCode: value.StatusCode, DelayMS: value.DelayMS,
		})
	}
	return result
}

func displayToolRetries(values []appstorage.ToolRetryTrace) []ToolRetryTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]ToolRetryTrace, 0, len(values))
	for _, value := range values {
		result = append(result, ToolRetryTrace{
			Attempt: value.Attempt, MaxAttempts: value.MaxAttempts,
			StatusCode: value.StatusCode, DelayMS: value.DelayMS,
		})
	}
	return result
}

func workspaceItems(paths []string, active string) []WorkspaceItem {
	result := make([]WorkspaceItem, 0, len(paths))
	for _, path := range paths {
		info, err := os.Stat(path)
		result = append(result, WorkspaceItem{
			Path: path, Name: filepath.Base(path), Available: err == nil && info.IsDir(), Active: sameWorkspace(path, active),
		})
	}
	return result
}

func sameWorkspace(left, right string) bool {
	left = filepath.Clean(left)
	right = filepath.Clean(right)
	if runtime.GOOS == "windows" {
		return strings.EqualFold(left, right)
	}
	return left == right
}

func messageID(conversationID string, index int) string {
	return fmt.Sprintf("%s-%d", conversationID, index+1)
}

func joinWarning(left, right string) string {
	if left == "" {
		return right
	}
	return left + "；" + right
}
