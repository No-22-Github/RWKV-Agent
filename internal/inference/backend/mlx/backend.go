package mlxbackend

import (
	"context"
	"crypto/sha256"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"sync"

	"github.com/no22/RWKV-Agent/internal/inference"
	nativemlx "github.com/no22/RWKV-Agent/internal/native/mlx"
)

const BackendID inference.BackendID = "mlx"

type Backend struct{}

func New() *Backend {
	return &Backend{}
}

func (b *Backend) Info() inference.BackendInfo {
	available := nativemlx.Available()
	reason := ""
	if !available {
		reason = "MLX requires an Apple Silicon build with cgo and the mlx build tag"
	}
	return inference.BackendInfo{
		ID:          BackendID,
		DisplayName: "RWKV Mobile MLX",
		Platform:    runtime.GOOS + "/" + runtime.GOARCH,
		Device: inference.DeviceInfo{
			ID:   "apple-silicon",
			Name: "Apple Silicon",
			Kind: "gpu",
		},
		Formats:           []inference.ModelFormat{"mlx-safetensors"},
		Capabilities:      capabilities(),
		Available:         available,
		UnavailableReason: reason,
	}
}

func (b *Backend) ProbeModel(ctx context.Context, source inference.ModelSource) (inference.ModelInfo, error) {
	if err := ctx.Err(); err != nil {
		return inference.ModelInfo{}, err
	}
	if err := validateSource(source); err != nil {
		return inference.ModelInfo{}, &inference.Error{
			Op: "probe model", Code: inference.CodeInvalidArgument, Backend: BackendID, Err: err,
		}
	}
	fingerprint, err := modelFingerprint(source.Path)
	if err != nil {
		return inference.ModelInfo{}, &inference.Error{
			Op: "fingerprint model", Code: inference.CodeBackendFailure, Backend: BackendID, Err: err,
		}
	}
	return inference.ModelInfo{
		ID:           inference.ModelID(filepath.Base(source.Path)),
		Fingerprint:  fingerprint,
		Architecture: "rwkv",
		Format:       "mlx-safetensors",
		Backend:      BackendID,
	}, nil
}

func (b *Backend) LoadModel(
	ctx context.Context,
	request inference.LoadRequest,
	progress inference.ProgressSink,
) (inference.Model, error) {
	if !nativemlx.Available() {
		return nil, &inference.Error{
			Op: "load model", Code: inference.CodeUnavailable, Backend: BackendID, Err: inference.ErrUnavailable,
		}
	}
	info, err := b.ProbeModel(ctx, request.Source)
	if err != nil {
		return nil, err
	}
	if progress != nil {
		if err := progress(inference.Progress{Stage: "load_model", Completed: 0, Total: 1}); err != nil {
			return nil, err
		}
	}
	nativeRuntime, err := nativemlx.Open(request.Source.Path, tokenizerPath(request.Source))
	if err != nil {
		return nil, &inference.Error{
			Op: "load model", Code: inference.CodeBackendFailure, Backend: BackendID, Err: err,
		}
	}
	if progress != nil {
		if err := progress(inference.Progress{Stage: "load_model", Completed: 1, Total: 1}); err != nil {
			_ = nativeRuntime.Close()
			return nil, err
		}
	}
	return &model{
		info:   info,
		native: nativeRuntime,
	}, nil
}

func capabilities() inference.Capabilities {
	native := inference.Support{Available: true}
	return inference.Capabilities{
		TextGeneration:          native,
		StreamingText:           native,
		Cancellation:            native,
		StatefulSessions:        native,
		TokenCounting:           native,
		PrefixCache:             native,
		SupportedBatchSizes:     []int{1},
		MaxConcurrentGeneration: 1,
	}
}

func tokenizerPath(source inference.ModelSource) string {
	if source.TokenizerPath != "" {
		return source.TokenizerPath
	}
	return filepath.Join(source.Path, "rwkv_vocab_v20230424.txt")
}

func validateSource(source inference.ModelSource) error {
	info, err := os.Stat(source.Path)
	if err != nil {
		return fmt.Errorf("model directory: %w", err)
	}
	if !info.IsDir() {
		return fmt.Errorf("%w: model path %q is not a directory", inference.ErrInvalidArgument, source.Path)
	}
	if _, err := os.Stat(filepath.Join(source.Path, "config.json")); err != nil {
		return fmt.Errorf("model config: %w", err)
	}
	weights, err := filepath.Glob(filepath.Join(source.Path, "*.safetensors"))
	if err != nil {
		return fmt.Errorf("model weights: %w", err)
	}
	if len(weights) == 0 {
		return fmt.Errorf("%w: model directory contains no safetensors weights", inference.ErrInvalidArgument)
	}
	if _, err := os.Stat(tokenizerPath(source)); err != nil {
		return fmt.Errorf("tokenizer: %w", err)
	}
	return nil
}

func modelFingerprint(path string) (string, error) {
	absolute, err := filepath.Abs(path)
	if err != nil {
		return "", err
	}
	files, err := filepath.Glob(filepath.Join(absolute, "*.safetensors"))
	if err != nil {
		return "", err
	}
	files = append(files, filepath.Join(absolute, "config.json"))
	digest := sha256.New()
	for _, file := range files {
		info, err := os.Stat(file)
		if err != nil {
			return "", err
		}
		fmt.Fprintf(digest, "%s\x00%d\x00", filepath.Base(file), info.Size())
		handle, err := os.Open(file)
		if err != nil {
			return "", err
		}
		_, copyErr := io.Copy(digest, handle)
		closeErr := handle.Close()
		if copyErr != nil {
			return "", copyErr
		}
		if closeErr != nil {
			return "", closeErr
		}
	}
	return fmt.Sprintf("mlx:%x", digest.Sum(nil)), nil
}

type model struct {
	mu       sync.Mutex
	nativeMu sync.RWMutex
	info     inference.ModelInfo
	native   *nativemlx.Runtime
	active   *session
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
	if m.active != nil {
		return nil, &inference.Error{Op: "new session", Code: inference.CodeBusy, Backend: BackendID, Err: inference.ErrBusy}
	}
	m.nativeMu.RLock()
	if err := m.native.ClearState(); err != nil {
		m.nativeMu.RUnlock()
		return nil, &inference.Error{Op: "reset session", Code: inference.CodeBackendFailure, Backend: BackendID, Err: err}
	}
	m.nativeMu.RUnlock()
	s := &session{model: m, stateStatus: "clean"}
	m.active = s
	return s, nil
}

func (m *model) Close() error {
	m.mu.Lock()
	if m.closed {
		m.mu.Unlock()
		return nil
	}
	m.closed = true
	active := m.active
	m.active = nil
	m.mu.Unlock()

	if active != nil {
		active.stopAndWait()
	}
	m.nativeMu.Lock()
	defer m.nativeMu.Unlock()
	return m.native.Close()
}

func (m *model) releaseSession(session *session) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.active == session {
		m.active = nil
	}
	if m.closed {
		return nil
	}
	m.nativeMu.RLock()
	defer m.nativeMu.RUnlock()
	if err := m.native.ClearState(); err != nil {
		return &inference.Error{Op: "reset session", Code: inference.CodeBackendFailure, Backend: BackendID, Err: err}
	}
	return nil
}

type session struct {
	mu          sync.Mutex
	model       *model
	closed      bool
	busy        bool
	cancel      context.CancelFunc
	done        chan struct{}
	generations uint64
	revision    uint64
	stateStatus string
	lastTimings inference.Timings
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
	if err := unsupportedOptions(request); err != nil {
		return inference.GenerateResult{}, err
	}
	prompt, err := inference.CompileGeneratePrompt(request)
	if err != nil {
		return inference.GenerateResult{}, err
	}

	runContext, err := s.begin(ctx)
	if err != nil {
		return inference.GenerateResult{}, err
	}
	defer s.end()

	if err := sink(inference.GenerationEvent{Kind: inference.EventStarted}); err != nil {
		s.cancelRun()
		return inference.GenerateResult{FinishReason: inference.FinishCancelled}, err
	}

	var output strings.Builder
	var sinkErr error
	s.model.mu.Lock()
	modelClosed := s.model.closed
	s.model.mu.Unlock()
	if modelClosed {
		return inference.GenerateResult{FinishReason: inference.FinishError}, &inference.Error{
			Op: "generate", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed,
		}
	}
	s.model.nativeMu.RLock()
	err = s.model.native.Generate(
		runContext,
		prompt,
		nativemlx.GenerateOptions{
			MaxTokens:   request.Limits.MaxOutputTokens,
			Temperature: request.Sampling.Temperature,
			TopK:        request.Sampling.TopK,
			TopP:        request.Sampling.TopP,
		},
		func(text string) error {
			output.WriteString(text)
			eventErr := sink(inference.GenerationEvent{
				Kind: inference.EventOutputDelta,
				Delta: &inference.OutputDelta{
					Channel: inference.ChannelFinal,
					Text:    text,
				},
			})
			if eventErr != nil {
				sinkErr = eventErr
				s.cancelRun()
			}
			return eventErr
		},
	)
	stats := s.model.native.Stats()
	s.model.nativeMu.RUnlock()

	result := inference.GenerateResult{
		Output: output.String(),
		Timings: inference.Timings{
			PrefillTokensPerSecond: stats.PrefillTokensPerSecond,
			DecodeTokensPerSecond:  stats.DecodeTokensPerSecond,
		},
	}
	if sinkErr != nil {
		result.FinishReason = inference.FinishCancelled
		s.resetAfterFailure()
		return result, sinkErr
	}
	if err != nil {
		result.FinishReason = inference.FinishError
		if errors.Is(err, context.Canceled) || errors.Is(err, context.DeadlineExceeded) {
			result.FinishReason = inference.FinishCancelled
		}
		s.resetAfterFailure()
		return result, err
	}

	s.mu.Lock()
	s.generations++
	s.revision++
	s.lastTimings = result.Timings
	result.StateRevision = strconv.FormatUint(s.revision, 10)
	s.mu.Unlock()
	result.FinishReason = inference.FinishUnknown
	result.Committed = true
	return result, nil
}

func (s *session) CountTokens(ctx context.Context, request inference.TokenCountRequest) (int, error) {
	if err := ctx.Err(); err != nil {
		return 0, err
	}
	prompt, err := inference.CompileTokenCountPrompt(request)
	if err != nil {
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
	s.model.nativeMu.RLock()
	defer s.model.nativeMu.RUnlock()
	count, err := s.model.native.CountTokens(prompt)
	if err != nil {
		return 0, &inference.Error{Op: "count tokens", Code: inference.CodeBackendFailure, Backend: BackendID, Err: err}
	}
	return count, nil
}

func (s *session) Reset(ctx context.Context) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return &inference.Error{Op: "reset", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	if s.busy {
		s.mu.Unlock()
		return &inference.Error{Op: "reset", Code: inference.CodeBusy, Backend: BackendID, Err: inference.ErrBusy}
	}
	s.mu.Unlock()

	s.model.mu.Lock()
	modelClosed := s.model.closed
	s.model.mu.Unlock()
	if modelClosed {
		return &inference.Error{Op: "reset", Code: inference.CodeClosed, Backend: BackendID, Err: inference.ErrClosed}
	}
	s.model.nativeMu.RLock()
	defer s.model.nativeMu.RUnlock()
	if err := s.model.native.ClearState(); err != nil {
		return &inference.Error{Op: "reset", Code: inference.CodeBackendFailure, Backend: BackendID, Err: err}
	}
	s.mu.Lock()
	s.revision++
	s.stateStatus = "clean"
	s.mu.Unlock()
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
		Revision: strconv.FormatUint(s.revision, 10),
		Status:   status,
	}
}

func (s *session) ExportState(
	context.Context,
	io.Writer,
	inference.ExportStateOptions,
) (inference.StateDescriptor, error) {
	return inference.StateDescriptor{}, unsupported("export state")
}

func (s *session) ImportState(
	context.Context,
	io.Reader,
	inference.ImportStateOptions,
) (inference.StateDescriptor, error) {
	return inference.StateDescriptor{}, unsupported("import state")
}

func (s *session) Fork(context.Context) (inference.Session, error) {
	return nil, unsupported("fork session")
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
	return s.model.releaseSession(s)
}

func (s *session) begin(ctx context.Context) (context.Context, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.closed {
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

func (s *session) cancelRun() {
	s.mu.Lock()
	cancel := s.cancel
	s.mu.Unlock()
	if cancel != nil {
		cancel()
	}
}

func (s *session) stopAndWait() {
	s.mu.Lock()
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
}

func (s *session) resetAfterFailure() {
	s.model.mu.Lock()
	modelClosed := s.model.closed
	s.model.mu.Unlock()
	if modelClosed {
		return
	}
	s.model.nativeMu.RLock()
	defer s.model.nativeMu.RUnlock()
	_ = s.model.native.ClearState()
}

func unsupportedOptions(request inference.GenerateRequest) error {
	if len(request.Stops) != 0 ||
		request.Sampling.Seed != nil ||
		request.Sampling.PresencePenalty != 0 ||
		request.Sampling.FrequencyPenalty != 0 ||
		request.Sampling.PenaltyDecay != 0 ||
		request.Commit == inference.CommitPartial {
		return unsupported("generate options")
	}
	return nil
}

func unsupported(op string) error {
	return &inference.Error{Op: op, Code: inference.CodeUnsupported, Backend: BackendID, Err: inference.ErrUnsupported}
}

var _ inference.Backend = (*Backend)(nil)
var _ inference.Model = (*model)(nil)
var _ inference.Session = (*session)(nil)
