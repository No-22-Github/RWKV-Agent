package mock

import (
	"context"
	"io"
	"runtime"
	"strconv"
	"strings"
	"sync"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/inference"
)

const BackendID inference.BackendID = "mock"

type Config struct {
	Output    string
	ChunkSize int
	Started   chan<- struct{}
	Continue  <-chan struct{}
}

type Backend struct {
	config Config
}

func New(config Config) *Backend {
	if config.ChunkSize <= 0 {
		config.ChunkSize = 1
	}
	return &Backend{config: config}
}

func (b *Backend) Info() inference.BackendInfo {
	return inference.BackendInfo{
		ID:           BackendID,
		DisplayName:  "Deterministic mock",
		Platform:     runtime.GOOS + "/" + runtime.GOARCH,
		Formats:      []inference.ModelFormat{"mock"},
		Capabilities: capabilities(),
		Available:    true,
	}
}

func (b *Backend) ProbeModel(ctx context.Context, source inference.ModelSource) (inference.ModelInfo, error) {
	if err := ctx.Err(); err != nil {
		return inference.ModelInfo{}, err
	}
	return modelInfo(source), nil
}

func (b *Backend) LoadModel(
	ctx context.Context,
	request inference.LoadRequest,
	progress inference.ProgressSink,
) (inference.Model, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	if progress != nil {
		if err := progress(inference.Progress{Stage: "load", Completed: 1, Total: 1}); err != nil {
			return nil, err
		}
	}
	return &model{info: modelInfo(request.Source), config: b.config}, nil
}

func capabilities() inference.Capabilities {
	native := inference.Support{Available: true}
	return inference.Capabilities{
		TextGeneration:          native,
		StreamingText:           native,
		Cancellation:            native,
		StatefulSessions:        native,
		TokenCounting:           native,
		DeterministicSeed:       native,
		SupportedBatchSizes:     []int{1},
		MaxConcurrentGeneration: 1,
	}
}

func modelInfo(source inference.ModelSource) inference.ModelInfo {
	return inference.ModelInfo{
		ID:           inference.ModelID(source.Path),
		Fingerprint:  "mock:" + source.Path,
		Architecture: "mock",
		Format:       "mock",
		Backend:      BackendID,
	}
}

type model struct {
	mu       sync.Mutex
	info     inference.ModelInfo
	config   Config
	sessions map[*session]struct{}
	closed   bool
}

func (m *model) Info() inference.ModelInfo {
	return m.info
}

func (m *model) Capabilities() inference.Capabilities {
	return capabilities()
}

func (m *model) NewSession(ctx context.Context, _ inference.SessionOptions) (inference.Session, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.closed {
		return nil, &inference.Error{Op: "new session", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	if m.sessions == nil {
		m.sessions = make(map[*session]struct{})
	}
	s := &session{model: m, config: m.config, stateStatus: "clean"}
	m.sessions[s] = struct{}{}
	return s, nil
}

func (m *model) Close() error {
	m.mu.Lock()
	if m.closed {
		m.mu.Unlock()
		return nil
	}
	m.closed = true
	sessions := make([]*session, 0, len(m.sessions))
	for session := range m.sessions {
		sessions = append(sessions, session)
	}
	m.sessions = nil
	m.mu.Unlock()
	for _, session := range sessions {
		if err := session.Close(); err != nil {
			return err
		}
	}
	return nil
}

func (m *model) releaseSession(session *session) {
	m.mu.Lock()
	delete(m.sessions, session)
	m.mu.Unlock()
}

type session struct {
	mu           sync.Mutex
	model        *model
	config       Config
	closed       bool
	busy         bool
	cancel       context.CancelFunc
	done         chan struct{}
	generations  uint64
	revision     uint64
	stateStatus  string
	lastTimings  inference.Timings
	prefixTokens []int32
}

func (s *session) Generate(
	ctx context.Context,
	request inference.GenerateRequest,
	sink inference.EventSink,
) (inference.GenerateResult, error) {
	if sink == nil {
		return inference.GenerateResult{}, &inference.Error{
			Op: "generate", Code: inference.CodeInvalidArgument, Backend: BackendID, Err: inference.ErrInvalidArgument,
		}
	}
	if err := inference.ValidateGenerateRequest(request); err != nil {
		return inference.GenerateResult{}, err
	}
	if len(request.Stops) != 0 {
		return inference.GenerateResult{}, &inference.Error{
			Op: "generate", Code: inference.CodeUnsupported, Backend: BackendID, Err: inference.ErrUnsupported,
		}
	}

	runContext, err := s.begin(ctx)
	if err != nil {
		return inference.GenerateResult{}, err
	}
	defer s.end()

	if err := runContext.Err(); err != nil {
		return inference.GenerateResult{FinishReason: inference.FinishCancelled}, err
	}
	if err := sink(inference.GenerationEvent{Kind: inference.EventStarted}); err != nil {
		return inference.GenerateResult{FinishReason: inference.FinishCancelled}, err
	}
	if s.config.Started != nil {
		select {
		case s.config.Started <- struct{}{}:
		default:
		}
	}
	if s.config.Continue != nil {
		select {
		case <-runContext.Done():
			return inference.GenerateResult{FinishReason: inference.FinishCancelled}, runContext.Err()
		case <-s.config.Continue:
		}
	}

	output := s.config.Output
	if output == "" {
		prompt, err := inference.CompileGeneratePrompt(request)
		if err != nil {
			return inference.GenerateResult{FinishReason: inference.FinishError}, err
		}
		output = prompt
	}

	var emitted strings.Builder
	remaining := []rune(output)
	for len(remaining) > 0 {
		if err := runContext.Err(); err != nil {
			return inference.GenerateResult{
				Output: emitted.String(), FinishReason: inference.FinishCancelled,
			}, err
		}
		size := min(s.config.ChunkSize, len(remaining))
		chunk := string(remaining[:size])
		remaining = remaining[size:]
		emitted.WriteString(chunk)
		if err := sink(inference.GenerationEvent{
			Kind: inference.EventOutputDelta,
			Delta: &inference.OutputDelta{
				Channel: inference.ChannelFinal,
				Text:    chunk,
			},
		}); err != nil {
			return inference.GenerateResult{
				Output: emitted.String(), FinishReason: inference.FinishCancelled,
			}, err
		}
	}

	s.mu.Lock()
	s.generations++
	s.revision++
	revision := strconv.FormatUint(s.revision, 10)
	s.mu.Unlock()

	return inference.GenerateResult{
		Output:        emitted.String(),
		FinishReason:  inference.FinishStop,
		Usage:         inference.Usage{CompletionTokens: utf8.RuneCountInString(emitted.String())},
		Committed:     true,
		StateRevision: revision,
	}, nil
}

func (s *session) CountTokens(ctx context.Context, request inference.TokenCountRequest) (int, error) {
	if err := ctx.Err(); err != nil {
		return 0, err
	}
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return 0, &inference.Error{Op: "count tokens", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	if s.busy {
		s.mu.Unlock()
		return 0, &inference.Error{Op: "count tokens", Code: inference.CodeBusy, Backend: BackendID, Err: inference.ErrBusy}
	}
	s.mu.Unlock()
	s.model.mu.Lock()
	modelClosed := s.model.closed
	s.model.mu.Unlock()
	if modelClosed {
		return 0, &inference.Error{Op: "count tokens", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	prompt, err := inference.CompileTokenCountPrompt(request)
	if err != nil {
		return 0, err
	}
	return utf8.RuneCountInString(prompt), nil
}

func (s *session) Encode(ctx context.Context, text string) ([]int32, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	tokens := make([]int32, 0, utf8.RuneCountInString(text))
	for _, value := range text {
		tokens = append(tokens, int32(value))
	}
	return tokens, nil
}

func (s *session) Prefill(
	ctx context.Context,
	request inference.PrefillRequest,
	progress inference.ProgressSink,
) (inference.PrefillResult, error) {
	if err := ctx.Err(); err != nil {
		return inference.PrefillResult{}, err
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return inference.PrefillResult{}, &inference.Error{Op: "prefill", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	if s.busy {
		return inference.PrefillResult{}, &inference.Error{Op: "prefill", Code: inference.CodeBusy, Backend: BackendID, Err: inference.ErrBusy}
	}
	s.prefixTokens = append(s.prefixTokens[:0], request.Tokens...)
	if progress != nil {
		if err := progress(inference.Progress{Stage: "prefill", Completed: int64(len(request.Tokens)), Total: int64(len(request.Tokens))}); err != nil {
			return inference.PrefillResult{}, err
		}
	}
	return inference.PrefillResult{
		TokenCount:    len(request.Tokens),
		PrefixHash:    strconv.Itoa(len(request.Tokens)),
		StateRevision: strconv.FormatUint(s.revision, 10),
	}, nil
}

func (s *session) Reset(ctx context.Context) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return &inference.Error{Op: "reset", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	if s.busy {
		return &inference.Error{Op: "reset", Code: inference.CodeBusy, Backend: BackendID, Err: inference.ErrBusy}
	}
	s.revision++
	s.stateStatus = "clean"
	s.prefixTokens = nil
	return nil
}

func (s *session) StateInfo() inference.SessionStateInfo {
	s.mu.Lock()
	defer s.mu.Unlock()
	status := s.stateStatus
	if s.closed {
		status = "closed"
	} else if s.busy {
		status = "generating"
	}
	return inference.SessionStateInfo{
		Revision:                  strconv.FormatUint(s.revision, 10),
		Status:                    status,
		TokenCount:                len(s.prefixTokens),
		CommittedPrefixTokenCount: len(s.prefixTokens),
	}
}

func (s *session) ExportState(
	context.Context,
	io.Writer,
	inference.ExportStateOptions,
) (inference.StateDescriptor, error) {
	return inference.StateDescriptor{}, &inference.Error{
		Op: "export state", Code: inference.CodeUnsupported, Backend: BackendID, Err: inference.ErrUnsupported,
	}
}

func (s *session) ImportState(
	context.Context,
	io.Reader,
	inference.ImportStateOptions,
) (inference.StateDescriptor, error) {
	return inference.StateDescriptor{}, &inference.Error{
		Op: "import state", Code: inference.CodeUnsupported, Backend: BackendID, Err: inference.ErrUnsupported,
	}
}

func (s *session) Fork(context.Context) (inference.Session, error) {
	return nil, &inference.Error{
		Op: "fork session", Code: inference.CodeUnsupported, Backend: BackendID, Err: inference.ErrUnsupported,
	}
}

func (s *session) Stats() inference.SessionStats {
	s.mu.Lock()
	defer s.mu.Unlock()
	return inference.SessionStats{
		Generations: s.generations,
		LastTimings: s.lastTimings,
	}
}

func (s *session) Close() error {
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return nil
	}
	s.closed = true
	cancel := s.cancel
	done := s.done
	s.mu.Unlock()
	if cancel != nil {
		cancel()
	}
	if done != nil {
		<-done
	}
	s.model.releaseSession(s)
	return nil
}

func (s *session) begin(ctx context.Context) (context.Context, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
		return nil, &inference.Error{Op: "generate", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	s.model.mu.Lock()
	modelClosed := s.model.closed
	s.model.mu.Unlock()
	if modelClosed {
		return nil, &inference.Error{Op: "generate", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	if s.busy {
		return nil, &inference.Error{Op: "generate", Code: inference.CodeBusy, Backend: BackendID, Err: inference.ErrBusy}
	}
	runContext, cancel := context.WithCancel(ctx)
	s.busy = true
	s.cancel = cancel
	s.done = make(chan struct{})
	s.stateStatus = "generating"
	return runContext, nil
}

func (s *session) end() {
	s.mu.Lock()
	s.busy = false
	s.cancel = nil
	if s.done != nil {
		close(s.done)
		s.done = nil
	}
	if !s.closed {
		s.stateStatus = "clean"
	}
	s.mu.Unlock()
}

var _ inference.Backend = (*Backend)(nil)
var _ inference.Model = (*model)(nil)
var _ inference.Session = (*session)(nil)
var _ inference.Tokenizer = (*session)(nil)
