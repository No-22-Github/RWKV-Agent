package api

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"time"
)

// Service owns the configured provider and creates isolated Agent sessions.
type Service struct {
	mu        sync.RWMutex
	workspace string
	status    Status
	config    Config
	source    generatorSource
	web       *webProviderSet
	sessions  map[*Session]struct{}
	closed    bool
}

// NewService creates an idle application service. An empty workspace is a
// valid "no project open" state: the agent is created without file tools and
// must ask the user to open a workspace before touching local files.
func NewService(options Options) (*Service, error) {
	workspace := strings.TrimSpace(options.Workspace)
	if workspace != "" {
		absolute, err := filepath.Abs(workspace)
		if err != nil {
			return nil, fmt.Errorf("resolve workspace: %w", err)
		}
		resolved, err := filepath.EvalSymlinks(absolute)
		if err != nil {
			return nil, fmt.Errorf("resolve workspace symlinks: %w", err)
		}
		workspace = resolved
	}
	service := &Service{
		workspace: workspace,
		sessions:  make(map[*Session]struct{}),
	}
	service.status = Status{
		State:     ModelIdle,
		Workspace: workspace,
		Message:   "Choose a local model or configure a remote API",
		UpdatedAt: time.Now(),
	}
	return service, nil
}

// Status returns a snapshot that never contains secret values.
func (s *Service) Status() Status {
	s.mu.RLock()
	defer s.mu.RUnlock()
	return cloneStatus(s.status)
}

// Configure validates and atomically replaces the active provider.
func (s *Service) Configure(ctx context.Context, config Config, progress func(Status)) (Status, error) {
	normalized, err := normalizeConfig(config)
	if err != nil {
		return s.setFailure(config, err), err
	}
	s.setStatus(Status{
		State:     ModelLoading,
		Provider:  normalized.Provider,
		Model:     normalized.Model,
		Endpoint:  publicEndpoint(normalized),
		Workspace: s.workspace,
		Message:   "Preparing model provider",
		UpdatedAt: time.Now(),
	}, progress)

	candidate, err := buildSource(ctx, normalized, func(value Status) {
		value.Workspace = s.workspace
		value.UpdatedAt = time.Now()
		s.setStatus(value, progress)
	})
	if err != nil {
		return s.setFailure(normalized, err), err
	}

	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		_ = candidate.close()
		return Status{}, fmt.Errorf("service is closed")
	}
	oldSource := s.source
	oldSessions := make([]*Session, 0, len(s.sessions))
	for session := range s.sessions {
		oldSessions = append(oldSessions, session)
	}
	s.sessions = make(map[*Session]struct{})
	s.source = candidate
	s.config = normalized
	s.web = nil
	status := candidate.status()
	status.Workspace = s.workspace
	status.UpdatedAt = time.Now()
	s.status = status
	s.mu.Unlock()

	for _, session := range oldSessions {
		_ = session.Close()
	}
	if oldSource != nil {
		_ = oldSource.close()
	}
	if progress != nil {
		progress(cloneStatus(status))
	}
	return cloneStatus(status), nil
}

// NewSession creates one isolated multi-turn Agent loop.
func (s *Service) NewSession(ctx context.Context) (*Session, error) {
	return s.newSession(ctx, 0)
}

func (s *Service) newSession(ctx context.Context, depth int) (*Session, error) {
	s.mu.RLock()
	if s.closed {
		s.mu.RUnlock()
		return nil, fmt.Errorf("service is closed")
	}
	source := s.source
	workspace := s.workspace
	status := s.status
	s.mu.RUnlock()
	if source == nil || status.State != ModelReady {
		return nil, fmt.Errorf("model provider is not ready")
	}
	generator, closer, err := source.newGenerator(ctx)
	if err != nil {
		return nil, err
	}
	configured, err := newSessionAtDepth(s, generator, closer, workspace, status, depth)
	if err != nil {
		_ = closer.Close()
		return nil, err
	}
	s.mu.Lock()
	if s.closed || s.source != source {
		s.mu.Unlock()
		_ = configured.Close()
		return nil, fmt.Errorf("model provider changed while creating session")
	}
	s.sessions[configured] = struct{}{}
	s.mu.Unlock()
	return configured, nil
}

func (s *Service) removeSession(session *Session) {
	s.mu.Lock()
	delete(s.sessions, session)
	s.mu.Unlock()
}

// ListRemoteModels tests a remote /v1/models endpoint with the same bearer
// token and custom headers used for inference requests.
func (s *Service) ListRemoteModels(ctx context.Context, config Config) ([]RemoteModel, error) {
	if config.Provider == "" {
		config.Provider = ProviderChatCompletions
	}
	if config.Provider != ProviderChatCompletions && config.Provider != ProviderRWKVLightning {
		return nil, fmt.Errorf("model discovery requires a remote provider")
	}
	endpoint := normalizeModelsEndpoint(config.Endpoint)
	parsed, err := url.Parse(endpoint)
	if err != nil || parsed.Scheme == "" || parsed.Host == "" ||
		(parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.User != nil {
		return nil, fmt.Errorf("endpoint must be an absolute HTTP(S) URL without credentials")
	}
	headers, _, err := validatedHeaders(config.Headers)
	if err != nil {
		return nil, err
	}
	request, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint, nil)
	if err != nil {
		return nil, err
	}
	request.Header = headers
	if apiKey := strings.TrimSpace(config.APIKey); apiKey != "" {
		request.Header.Set("Authorization", "Bearer "+apiKey)
	}
	response, err := (&http.Client{Timeout: 30 * time.Second}).Do(request)
	if err != nil {
		return nil, fmt.Errorf("request remote models: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		_, _ = io.Copy(io.Discard, io.LimitReader(response.Body, 4096))
		return nil, fmt.Errorf("remote models returned HTTP %s", response.Status)
	}
	var payload struct {
		Data   []RemoteModel `json:"data"`
		Models []RemoteModel `json:"models"`
	}
	decoder := json.NewDecoder(io.LimitReader(response.Body, 4*1024*1024))
	if err := decoder.Decode(&payload); err != nil {
		return nil, fmt.Errorf("decode remote models: %w", err)
	}
	models := payload.Data
	if len(models) == 0 {
		models = payload.Models
	}
	models = append([]RemoteModel(nil), models...)
	sort.Slice(models, func(left, right int) bool { return models[left].ID < models[right].ID })
	return models, nil
}

// Close closes every session and unloads the active provider.
func (s *Service) Close() error {
	if s == nil {
		return nil
	}
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return nil
	}
	s.closed = true
	source := s.source
	s.source = nil
	s.config = Config{}
	sessions := make([]*Session, 0, len(s.sessions))
	for session := range s.sessions {
		sessions = append(sessions, session)
	}
	s.sessions = nil
	s.status = Status{State: ModelIdle, Workspace: s.workspace, Message: "Service closed", UpdatedAt: time.Now()}
	s.mu.Unlock()
	var first error
	for _, session := range sessions {
		if err := session.Close(); err != nil && first == nil {
			first = err
		}
	}
	if source != nil {
		if err := source.close(); err != nil && first == nil {
			first = err
		}
	}
	return first
}

func (s *Service) setStatus(status Status, progress func(Status)) {
	s.mu.Lock()
	if !s.closed {
		s.status = cloneStatus(status)
	}
	s.mu.Unlock()
	if progress != nil {
		progress(cloneStatus(status))
	}
}

func (s *Service) setFailure(config Config, err error) Status {
	status := Status{
		State:     ModelError,
		Provider:  config.Provider,
		Model:     config.Model,
		Endpoint:  publicEndpoint(config),
		Workspace: s.workspace,
		Message:   err.Error(),
		UpdatedAt: time.Now(),
	}
	s.setStatus(status, nil)
	return status
}

func normalizeConfig(config Config) (Config, error) {
	if config.Provider == "" {
		config.Provider = ProviderLocal
	}
	config.Model = strings.TrimSpace(config.Model)
	if config.Model == "" {
		return Config{}, fmt.Errorf("model is required")
	}
	if config.MaxSteps == 0 {
		config.MaxSteps = 6
	}
	if config.MaxSteps < 2 {
		return Config{}, fmt.Errorf("maxSteps must be at least 2")
	}
	if config.MaxTokens == 0 {
		config.MaxTokens = 1024
	}
	if config.MaxTokens < 1 {
		return Config{}, fmt.Errorf("maxTokens must be positive")
	}
	if config.RouteMaxTokens == 0 {
		config.RouteMaxTokens = 48
	}
	if config.RouteMaxTokens < 1 {
		return Config{}, fmt.Errorf("routeMaxTokens must be positive")
	}
	if config.MaxActiveBatch == 0 {
		config.MaxActiveBatch = 4
	}
	if config.MaxActiveBatch < 1 || config.MaxActiveBatch > 8 {
		return Config{}, fmt.Errorf("maxActiveBatch must be between 1 and 8")
	}
	if config.RemoteBatchWaitMS < 0 || config.RemoteBatchWaitMS > 1000 {
		return Config{}, fmt.Errorf("remoteBatchWaitMs must be between 0 and 1000")
	}
	if config.EnableSubagents && config.RemoteBatchWaitMS == 0 {
		config.RemoteBatchWaitMS = 10
	}
	if config.SubagentMaxParallel == 0 {
		config.SubagentMaxParallel = 4
	}
	if config.SubagentMaxParallel < 2 || config.SubagentMaxParallel > 8 {
		return Config{}, fmt.Errorf("subagentMaxParallel must be between 2 and 8")
	}
	if config.SubagentMaxSteps == 0 {
		config.SubagentMaxSteps = 4
	}
	if config.SubagentMaxSteps < 2 || config.SubagentMaxSteps > 32 {
		return Config{}, fmt.Errorf("subagentMaxSteps must be between 2 and 32")
	}
	if config.SubagentTimeoutSeconds == 0 {
		config.SubagentTimeoutSeconds = 120
	}
	if config.SubagentTimeoutSeconds < 1 || config.SubagentTimeoutSeconds > 3600 {
		return Config{}, fmt.Errorf("subagentTimeoutSeconds must be between 1 and 3600")
	}
	if config.EnableWeb && (strings.TrimSpace(config.BraveAPIKey) == "" || strings.TrimSpace(config.TavilyAPIKey) == "") {
		return Config{}, fmt.Errorf("enableWeb requires Brave and Tavily API keys")
	}
	if config.Temperature == 0 {
		config.Temperature = 1
	}
	if config.TopK == 0 {
		config.TopK = 1
	}
	if config.TopP == 0 {
		config.TopP = 1
	}
	if config.PenaltyDecay == 0 {
		config.PenaltyDecay = 1
	}
	if config.Thinking == "" {
		config.Thinking = "off"
	}
	if config.AgentProtocol == "" {
		config.AgentProtocol = AgentProtocolMarkdown
	}
	if config.AgentProtocol != AgentProtocolMarkdown && config.AgentProtocol != AgentProtocolXML {
		return Config{}, fmt.Errorf("unsupported agentProtocol %q", config.AgentProtocol)
	}
	if config.Backend == "" {
		config.Backend = "auto"
	}
	if config.NativeProvider == "" {
		config.NativeProvider = "auto"
	}
	if config.ChatThinking == "" {
		config.ChatThinking = "auto"
	}
	if config.ChatPromptMode == "" {
		config.ChatPromptMode = "native-chat"
	}
	if config.ChatTokenLimit == "" {
		config.ChatTokenLimit = "max-completion-tokens"
	}
	if config.RWKVStopTokens == "" {
		// Keep stop handling under Harness control. The client still truncates
		// decoded text locally, while omitting server-specific stop token forms.
		config.RWKVStopTokens = "none"
	}
	if config.Temperature <= 0 || config.TopK <= 0 || config.TopP <= 0 || config.TopP > 1 ||
		config.PresencePenalty < 0 || config.FrequencyPenalty < 0 ||
		config.PenaltyDecay <= 0 || config.PenaltyDecay > 1 {
		return Config{}, fmt.Errorf("invalid sampling options")
	}
	switch config.Provider {
	case ProviderLocal:
		absolute, err := filepath.Abs(config.Model)
		if err != nil {
			return Config{}, fmt.Errorf("resolve model path: %w", err)
		}
		config.Model = absolute
		config.TokenizerPath, err = ResolveTokenizer(config.Model, config.TokenizerPath)
		if err != nil {
			return Config{}, err
		}
	case ProviderChatCompletions, ProviderRWKVLightning:
		parsed, err := url.Parse(config.Endpoint)
		if err != nil || parsed.Scheme == "" || parsed.Host == "" ||
			(parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.User != nil {
			return Config{}, fmt.Errorf("endpoint must be an absolute HTTP(S) URL without credentials")
		}
		if _, _, err := validatedHeaders(config.Headers); err != nil {
			return Config{}, err
		}
	default:
		return Config{}, fmt.Errorf("unsupported provider %q", config.Provider)
	}
	return config, nil
}

func publicEndpoint(config Config) string {
	if config.Provider == ProviderChatCompletions && strings.TrimSpace(config.Endpoint) != "" {
		return normalizeChatEndpoint(config.Endpoint)
	}
	if config.Provider == ProviderRWKVLightning && strings.TrimSpace(config.Endpoint) != "" {
		return normalizeRWKVEndpoint(config.Endpoint)
	}
	return strings.TrimSpace(config.Endpoint)
}

func cloneStatus(status Status) Status {
	status.HeaderNames = append([]string(nil), status.HeaderNames...)
	return status
}
