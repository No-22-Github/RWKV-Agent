package rwkvmobile

import (
	"context"
	"crypto/sha256"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"

	"github.com/no22/RWKV-Agent/internal/inference"
	native "github.com/no22/RWKV-Agent/internal/native/rwkvmobile"
)

const BackendID inference.BackendID = "rwkvmobile"

type Options struct {
	Provider       string
	MaxActiveBatch int
	QueueCapacity  int
}

type Backend struct{ options Options }

func New(options Options) *Backend {
	if options.Provider == "" || options.Provider == "auto" {
		options.Provider = "mlx"
	}
	if options.MaxActiveBatch <= 0 {
		options.MaxActiveBatch = 4
	}
	if options.QueueCapacity <= 0 {
		options.QueueCapacity = 64
	}
	return &Backend{options: options}
}

func (b *Backend) Info() inference.BackendInfo {
	available := native.Available()
	reason := ""
	if !available {
		reason = "RWKV Mobile MLX requires Apple Silicon macOS, cgo, and the mlx build tag"
	}
	return inference.BackendInfo{
		ID:          BackendID,
		DisplayName: "RWKV Agent Runtime / RWKV Mobile MLX",
		Platform:    runtime.GOOS + "/" + runtime.GOARCH,
		Device: inference.DeviceInfo{
			ID:   "apple-silicon",
			Name: "Apple Silicon",
			Kind: "gpu",
		},
		Formats:           []inference.ModelFormat{"mlx-safetensors"},
		Capabilities:      advertisedCapabilities(b.options.MaxActiveBatch),
		Available:         available,
		UnavailableReason: reason,
	}
}

func advertisedCapabilities(maxBatch int) inference.Capabilities {
	nativeSupport := inference.Support{Available: true}
	return inference.Capabilities{
		TextGeneration:          nativeSupport,
		StreamingText:           nativeSupport,
		Cancellation:            nativeSupport,
		StatefulSessions:        nativeSupport,
		StateExport:             nativeSupport,
		StateImport:             nativeSupport,
		PrefixCache:             nativeSupport,
		TokenCounting:           nativeSupport,
		DeterministicSeed:       nativeSupport,
		SupportedBatchSizes:     integerRange(1, maxBatch),
		MaxConcurrentGeneration: maxBatch,
	}
}

func integerRange(start, end int) []int {
	result := make([]int, 0, max(0, end-start+1))
	for value := start; value <= end; value++ {
		result = append(result, value)
	}
	return result
}

func (b *Backend) ProbeModel(ctx context.Context, source inference.ModelSource) (inference.ModelInfo, error) {
	if err := ctx.Err(); err != nil {
		return inference.ModelInfo{}, err
	}
	if err := validateSource(source); err != nil {
		return inference.ModelInfo{}, wrap("probe model", inference.CodeInvalidArgument, err)
	}
	modelFingerprint, err := fingerprintFiles(source.Path, "*.safetensors", "config.json")
	if err != nil {
		return inference.ModelInfo{}, wrap("fingerprint model", inference.CodeBackendFailure, err)
	}
	tokenizerFingerprint, err := fingerprintFile(tokenizerPath(source))
	if err != nil {
		return inference.ModelInfo{}, wrap("fingerprint tokenizer", inference.CodeBackendFailure, err)
	}
	return inference.ModelInfo{
		ID:                   inference.ModelID(filepath.Base(source.Path)),
		Fingerprint:          "sha256:" + modelFingerprint,
		TokenizerFingerprint: "sha256:" + tokenizerFingerprint,
		Architecture:         "rwkv-7",
		Format:               "mlx-safetensors",
		Backend:              BackendID,
	}, nil
}

func (b *Backend) LoadModel(
	ctx context.Context,
	request inference.LoadRequest,
	progress inference.ProgressSink,
) (inference.Model, error) {
	if !native.Available() {
		return nil, wrap("load model", inference.CodeUnavailable, inference.ErrUnavailable)
	}
	info, err := b.ProbeModel(ctx, request.Source)
	if err != nil {
		return nil, err
	}
	if progress != nil {
		if err := progress(inference.Progress{Stage: "load_model", Total: 1}); err != nil {
			return nil, err
		}
	}
	nativeRuntime, err := native.Open(native.Options{
		MaxActiveBatch: b.options.MaxActiveBatch,
		QueueCapacity:  b.options.QueueCapacity,
	})
	if err != nil {
		return nil, mapError("create runtime", err)
	}
	nativeModel, err := nativeRuntime.LoadModel(native.ModelOptions{
		Path:          request.Source.Path,
		TokenizerPath: tokenizerPath(request.Source),
		Provider:      b.options.Provider,
	})
	if err != nil {
		_ = nativeRuntime.Close()
		return nil, mapError("load model", err)
	}
	capability, err := nativeModel.Capabilities()
	if err != nil {
		_ = nativeModel.Close()
		_ = nativeRuntime.Close()
		return nil, mapError("model capabilities", err)
	}
	if progress != nil {
		if err := progress(inference.Progress{Stage: "load_model", Completed: 1, Total: 1}); err != nil {
			_ = nativeModel.Close()
			_ = nativeRuntime.Close()
			return nil, err
		}
	}
	return &model{
		info:         info,
		runtime:      nativeRuntime,
		native:       nativeModel,
		capabilities: capabilitiesFromNative(capability),
		sessions:     make(map[*session]struct{}),
	}, nil
}

func capabilitiesFromNative(value native.Capabilities) inference.Capabilities {
	result := advertisedCapabilities(value.MaxActiveBatch)
	result.StateExport.Available = value.NativeState
	result.StateImport.Available = value.NativeState
	result.Cancellation.Available = value.Cancellation
	result.MaxObservedBatch = value.MaxObservedBatch
	return result
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
		return fmt.Errorf("%w: model path is not a directory", inference.ErrInvalidArgument)
	}
	if _, err := os.Stat(filepath.Join(source.Path, "config.json")); err != nil {
		return fmt.Errorf("model config: %w", err)
	}
	weights, err := filepath.Glob(filepath.Join(source.Path, "*.safetensors"))
	if err != nil || len(weights) == 0 {
		return fmt.Errorf("%w: no safetensors weights", inference.ErrInvalidArgument)
	}
	if _, err := os.Stat(tokenizerPath(source)); err != nil {
		return fmt.Errorf("tokenizer: %w", err)
	}
	return nil
}

func fingerprintFiles(directory string, pattern string, required ...string) (string, error) {
	files, err := filepath.Glob(filepath.Join(directory, pattern))
	if err != nil {
		return "", err
	}
	for _, name := range required {
		files = append(files, filepath.Join(directory, name))
	}
	sort.Strings(files)
	digest := sha256.New()
	for _, path := range files {
		fileDigest, err := fingerprintFile(path)
		if err != nil {
			return "", err
		}
		fmt.Fprintf(digest, "%s\x00%s\x00", filepath.Base(path), fileDigest)
	}
	return fmt.Sprintf("%x", digest.Sum(nil)), nil
}

func fingerprintFile(path string) (string, error) {
	handle, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer handle.Close()
	digest := sha256.New()
	if _, err := io.Copy(digest, handle); err != nil {
		return "", err
	}
	return fmt.Sprintf("%x", digest.Sum(nil)), nil
}

type model struct {
	mu           sync.Mutex
	info         inference.ModelInfo
	runtime      *native.Runtime
	native       *native.Model
	capabilities inference.Capabilities
	sessions     map[*session]struct{}
	closed       bool
	requestID    atomic.Uint64
}

func (m *model) Info() inference.ModelInfo { return m.info }

func (m *model) Capabilities() inference.Capabilities {
	m.mu.Lock()
	defer m.mu.Unlock()
	if !m.closed {
		if value, err := m.native.Capabilities(); err == nil {
			m.capabilities = capabilitiesFromNative(value)
		}
	}
	return m.capabilities
}

func (m *model) NewSession(ctx context.Context, _ inference.SessionOptions) (inference.Session, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.closed {
		return nil, wrap("new session", inference.CodeClosed, inference.ErrClosed)
	}
	handle, err := m.native.NewSession()
	if err != nil {
		return nil, mapError("new session", err)
	}
	value := &session{model: m, native: handle}
	m.sessions[value] = struct{}{}
	return value, nil
}

func (m *model) Close() error {
	m.mu.Lock()
	if m.closed {
		m.mu.Unlock()
		return nil
	}
	m.closed = true
	sessions := make([]*session, 0, len(m.sessions))
	for value := range m.sessions {
		sessions = append(sessions, value)
	}
	m.mu.Unlock()
	var result []error
	for _, value := range sessions {
		if err := value.Close(); err != nil {
			result = append(result, err)
		}
	}
	if err := m.native.Close(); err != nil {
		result = append(result, mapError("close model", err))
	}
	if err := m.runtime.Close(); err != nil {
		result = append(result, mapError("close runtime", err))
	}
	return errors.Join(result...)
}

func (m *model) release(value *session) {
	m.mu.Lock()
	delete(m.sessions, value)
	m.mu.Unlock()
}

type session struct {
	mu          sync.Mutex
	model       *model
	native      *native.Session
	closed      bool
	generations uint64
	lastTimings inference.Timings
}

func (s *session) Encode(ctx context.Context, text string) ([]int32, error) {
	if err := ctx.Err(); err != nil {
		return nil, err
	}
	s.mu.Lock()
	closed := s.closed
	s.mu.Unlock()
	if closed {
		return nil, wrap("encode", inference.CodeClosed, inference.ErrClosed)
	}
	tokens, err := s.model.native.Encode(text)
	if err != nil {
		return nil, mapError("encode", err)
	}
	return tokens, nil
}

func (s *session) Generate(
	ctx context.Context,
	request inference.GenerateRequest,
	sink inference.EventSink,
) (inference.GenerateResult, error) {
	if err := ctx.Err(); err != nil {
		return inference.GenerateResult{FinishReason: inference.FinishCancelled}, err
	}
	if sink == nil {
		return inference.GenerateResult{}, wrap("generate", inference.CodeInvalidArgument, inference.ErrInvalidArgument)
	}
	if err := inference.ValidateGenerateRequest(request); err != nil {
		return inference.GenerateResult{}, err
	}
	if request.Commit == inference.CommitPartial {
		return inference.GenerateResult{}, wrap("generate", inference.CodeUnsupported, inference.ErrUnsupported)
	}
	prompt, err := inference.CompileGeneratePrompt(request)
	if err != nil {
		return inference.GenerateResult{}, err
	}
	tokens, err := s.Encode(ctx, prompt)
	if err != nil {
		if ctx.Err() != nil {
			return inference.GenerateResult{FinishReason: inference.FinishCancelled}, ctx.Err()
		}
		return inference.GenerateResult{}, err
	}
	if err := sink(inference.GenerationEvent{Kind: inference.EventStarted}); err != nil {
		return inference.GenerateResult{FinishReason: inference.FinishCancelled}, err
	}
	requestID := s.model.requestID.Add(1)
	var output strings.Builder
	var outputTokens []int32
	seed := (*uint64)(nil)
	if request.Sampling.Seed != nil {
		value := uint64(*request.Sampling.Seed)
		seed = &value
	}
	nativeResult, nativeErr := s.native.Generate(ctx, native.GenerateOptions{
		RequestID:        requestID,
		InputTokens:      tokens,
		MaxOutputTokens:  request.Limits.MaxOutputTokens,
		Temperature:      request.Sampling.Temperature,
		TopK:             request.Sampling.TopK,
		TopP:             request.Sampling.TopP,
		PresencePenalty:  request.Sampling.PresencePenalty,
		FrequencyPenalty: request.Sampling.FrequencyPenalty,
		PenaltyDecay:     request.Sampling.PenaltyDecay,
		Seed:             seed,
	}, func(event native.StreamEvent) error {
		if event.Finish || event.Warning {
			return nil
		}
		output.WriteString(event.Text)
		outputTokens = append(outputTokens, event.TokenID)
		return sink(inference.GenerationEvent{
			Kind: inference.EventOutputDelta,
			Delta: &inference.OutputDelta{
				Channel: inference.ChannelFinal,
				Text:    event.Text,
				Tokens:  []int32{event.TokenID},
			},
		})
	})
	result := inference.GenerateResult{
		Output:       output.String(),
		OutputTokens: outputTokens,
		FinishReason: finishReason(nativeResult.FinishReason),
		Usage: inference.Usage{
			PromptTokens:     nativeResult.PrefillTokens,
			CompletionTokens: nativeResult.DecodeTokens,
		},
		Timings: inference.Timings{
			PrefillTokensPerSecond: nativeResult.PrefillTokensPerSecond,
			DecodeTokensPerSecond:  nativeResult.DecodeTokensPerSecond,
		},
		Committed:     nativeResult.StateClean && nativeErr == nil,
		StateRevision: formatHash(nativeResult.PrefixHash),
	}
	if nativeErr != nil {
		if errors.Is(ctx.Err(), context.Canceled) || errors.Is(ctx.Err(), context.DeadlineExceeded) {
			return result, ctx.Err()
		}
		return result, mapError("generate", nativeErr)
	}
	s.mu.Lock()
	s.generations++
	s.lastTimings = result.Timings
	s.mu.Unlock()
	return result, nil
}

func finishReason(value string) inference.FinishReason {
	switch value {
	case "stop":
		return inference.FinishStop
	case "length":
		return inference.FinishLength
	case "cancelled":
		return inference.FinishCancelled
	default:
		return inference.FinishError
	}
}

func (s *session) Prefill(
	ctx context.Context,
	request inference.PrefillRequest,
	progress inference.ProgressSink,
) (inference.PrefillResult, error) {
	if request.ReplacePrefix {
		if err := s.native.Reset(); err != nil {
			return inference.PrefillResult{}, mapError("reset prefix", err)
		}
	}
	err := s.native.SyncPrefix(ctx, request.Tokens, func(completed, total int) error {
		if progress == nil {
			return nil
		}
		return progress(inference.Progress{
			Stage:     "prefill",
			Completed: int64(completed),
			Total:     int64(total),
		})
	})
	if err != nil {
		if ctx.Err() != nil {
			return inference.PrefillResult{}, ctx.Err()
		}
		return inference.PrefillResult{}, mapError("prefill", err)
	}
	info, err := s.native.Info()
	if err != nil {
		return inference.PrefillResult{}, mapError("prefill State", err)
	}
	return inference.PrefillResult{
		TokenCount:    info.PrefixTokenCount,
		PrefixHash:    formatHash(info.PrefixHash),
		StateRevision: formatHash(info.PrefixHash),
	}, nil
}

func (s *session) CountTokens(ctx context.Context, request inference.TokenCountRequest) (int, error) {
	prompt, err := inference.CompileTokenCountPrompt(request)
	if err != nil {
		return 0, err
	}
	tokens, err := s.Encode(ctx, prompt)
	return len(tokens), err
}

func (s *session) Reset(ctx context.Context) error {
	if err := ctx.Err(); err != nil {
		return err
	}
	if err := s.native.Reset(); err != nil {
		return mapError("reset", err)
	}
	return nil
}

func (s *session) StateInfo() inference.SessionStateInfo {
	info, err := s.native.Info()
	if err != nil {
		return inference.SessionStateInfo{Status: "closed", DirtyReason: err.Error()}
	}
	return inference.SessionStateInfo{
		Revision:                  formatHash(info.PrefixHash),
		NativeRevision:            formatHash(info.PrefixHash),
		Status:                    info.Status,
		TokenCount:                info.PrefixTokenCount,
		CommittedPrefixTokenCount: info.PrefixTokenCount,
		NativeSnapshot:            true,
		RecoveryMode:              "native-or-replay",
		DirtyReason:               info.DirtyReason,
		PrefixHash:                formatHash(info.PrefixHash),
	}
}

func (s *session) ExportState(
	ctx context.Context,
	writer io.Writer,
	_ inference.ExportStateOptions,
) (inference.StateDescriptor, error) {
	if err := ctx.Err(); err != nil {
		return inference.StateDescriptor{}, err
	}
	value, err := s.native.ExportState(writer)
	if err != nil {
		return inference.StateDescriptor{}, mapError("export State", err)
	}
	return inference.StateDescriptor{
		FormatVersion:    value.FormatVersion,
		ModelFingerprint: s.model.info.Fingerprint,
		StateRevision:    formatHash(value.PrefixHash),
		PrefixTokenCount: value.PrefixTokenCount,
		PrefixHash:       formatHash(value.PrefixHash),
		CodecID:          value.CodecID,
		CodecVersion:     value.CodecVersion,
	}, nil
}

func (s *session) ImportState(
	ctx context.Context,
	reader io.Reader,
	options inference.ImportStateOptions,
) (inference.StateDescriptor, error) {
	if err := ctx.Err(); err != nil {
		return inference.StateDescriptor{}, err
	}
	descriptor := options.Descriptor
	if descriptor.FormatVersion == 0 {
		return inference.StateDescriptor{}, wrap(
			"import State",
			inference.CodeInvalidArgument,
			fmt.Errorf("%w: State descriptor is required", inference.ErrInvalidArgument),
		)
	}
	value := native.StateDescriptor{
		FormatVersion:    descriptor.FormatVersion,
		PrefixTokenCount: descriptor.PrefixTokenCount,
		PrefixHash:       parseHash(descriptor.PrefixHash),
		CodecID:          descriptor.CodecID,
		CodecVersion:     descriptor.CodecVersion,
	}
	if err := s.native.ImportState(reader, value); err != nil {
		return inference.StateDescriptor{}, mapError("import State", err)
	}
	return descriptor, nil
}

func (s *session) Fork(context.Context) (inference.Session, error) {
	return nil, wrap("fork session", inference.CodeUnsupported, inference.ErrUnsupported)
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
	s.mu.Unlock()
	err := s.native.Close()
	s.model.release(s)
	if err != nil {
		return mapError("close session", err)
	}
	return nil
}

func formatHash(value uint64) string {
	return fmt.Sprintf("fnv64:%016x", value)
}

func parseHash(value string) uint64 {
	value = strings.TrimPrefix(value, "fnv64:")
	result, _ := strconv.ParseUint(value, 16, 64)
	return result
}

func wrap(op string, code inference.ErrorCode, err error) error {
	return &inference.Error{Op: op, Code: code, Backend: BackendID, Err: err}
}

func mapError(op string, err error) error {
	var nativeError *native.Error
	if !errors.As(err, &nativeError) {
		return wrap(op, inference.CodeBackendFailure, err)
	}
	code := inference.CodeBackendFailure
	sentinel := error(err)
	switch nativeError.Status {
	case native.StatusInvalidArgument:
		code, sentinel = inference.CodeInvalidArgument, errors.Join(inference.ErrInvalidArgument, err)
	case native.StatusUnavailable:
		code, sentinel = inference.CodeUnavailable, errors.Join(inference.ErrUnavailable, err)
	case native.StatusUnsupported:
		code, sentinel = inference.CodeUnsupported, errors.Join(inference.ErrUnsupported, err)
	case native.StatusBusy:
		code, sentinel = inference.CodeBusy, errors.Join(inference.ErrBusy, err)
	case native.StatusCancelled:
		code, sentinel = inference.CodeCancelled, errors.Join(inference.ErrCancelled, err)
	case native.StatusIncompatibleState:
		code, sentinel = inference.CodeIncompatibleState, errors.Join(inference.ErrIncompatibleState, err)
	case native.StatusCorruptState:
		code, sentinel = inference.CodeCorruptState, errors.Join(inference.ErrCorruptState, err)
	case native.StatusClosed:
		code, sentinel = inference.CodeClosed, errors.Join(inference.ErrClosed, err)
	case native.StatusCapacity:
		code, sentinel = inference.CodeCapacity, errors.Join(inference.ErrCapacity, err)
	}
	return &inference.Error{
		Op:         op,
		Code:       code,
		Backend:    BackendID,
		NativeCode: int(nativeError.Status),
		Retryable:  nativeError.Status == native.StatusBusy || nativeError.Status == native.StatusCapacity,
		Err:        sentinel,
	}
}

var _ inference.Backend = (*Backend)(nil)
var _ inference.Model = (*model)(nil)
var _ inference.Session = (*session)(nil)
var _ inference.Tokenizer = (*session)(nil)
