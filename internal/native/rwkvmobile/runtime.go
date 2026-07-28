package rwkvmobile

import (
	"context"
	"errors"
	"fmt"
	"io"
)

var ErrUnavailable = errors.New("RWKV Agent native runtime is unavailable in this build")

type Status int

const (
	StatusOK                Status = 0
	StatusInvalidArgument   Status = 1
	StatusUnavailable       Status = 2
	StatusUnsupported       Status = 3
	StatusBusy              Status = 4
	StatusCancelled         Status = 5
	StatusIncompatibleState Status = 6
	StatusCorruptState      Status = 7
	StatusBackendFailure    Status = 8
	StatusClosed            Status = 9
	StatusCapacity          Status = 10
)

type Error struct {
	Status  Status
	Message string
}

func (e *Error) Error() string {
	if e.Message == "" {
		return fmt.Sprintf("native runtime status %d", e.Status)
	}
	return e.Message
}

type Options struct {
	MaxActiveBatch int
	QueueCapacity  int
}

type ModelOptions struct {
	Path          string
	TokenizerPath string
	Provider      string
	IndexPath     string
}

type Capabilities struct {
	NativeState      bool
	ContinuousBatch  bool
	ExactTokens      bool
	Cancellation     bool
	MaxStateSlots    int
	AvailableSlots   int
	MaxActiveBatch   int
	QueueCapacity    int
	MaxObservedBatch int
}

type GenerateOptions struct {
	RequestID        uint64
	InputTokens      []int32
	MaxOutputTokens  int
	Temperature      float32
	TopK             int
	TopP             float32
	PresencePenalty  float32
	FrequencyPenalty float32
	PenaltyDecay     float32
	Seed             *uint64
}

type StreamEvent struct {
	RequestID uint64
	TokenID   int32
	Text      string
	Finish    bool
	Warning   bool
}

type GenerateResult struct {
	FinishReason           string
	StateClean             bool
	PrefillTokens          int
	DecodeTokens           int
	PrefillTokensPerSecond float64
	DecodeTokensPerSecond  float64
	PrefixHash             uint64
}

type SessionInfo struct {
	Status           string
	PrefixTokenCount int
	PrefixHash       uint64
	ActiveRequestID  uint64
	DirtyReason      string
}

type StateDescriptor struct {
	FormatVersion    int
	PrefixTokenCount int
	PrefixHash       uint64
	CodecID          string
	CodecVersion     int
}

type runtimeImpl interface {
	loadModel(ModelOptions) (modelImpl, error)
	close() error
}

type modelImpl interface {
	encode(string) ([]int32, error)
	capabilities() (Capabilities, error)
	newSession() (sessionImpl, error)
	close() error
}

type sessionImpl interface {
	syncPrefix(context.Context, []int32, func(completed, total int) error) error
	generate(context.Context, GenerateOptions, func(StreamEvent) error) (GenerateResult, error)
	cancel(uint64) error
	reset() error
	info() (SessionInfo, error)
	exportState(io.Writer) (StateDescriptor, error)
	importState(io.Reader, StateDescriptor) error
	close() error
}

type Runtime struct{ impl runtimeImpl }
type Model struct{ impl modelImpl }
type Session struct{ impl sessionImpl }

func Available() bool { return platformAvailable() }

func Open(options Options) (*Runtime, error) {
	impl, err := platformOpen(options)
	if err != nil {
		return nil, err
	}
	return &Runtime{impl: impl}, nil
}

func (r *Runtime) LoadModel(options ModelOptions) (*Model, error) {
	if r == nil || r.impl == nil {
		return nil, &Error{Status: StatusClosed, Message: "native runtime is closed"}
	}
	impl, err := r.impl.loadModel(options)
	if err != nil {
		return nil, err
	}
	return &Model{impl: impl}, nil
}

func (r *Runtime) Close() error {
	if r == nil || r.impl == nil {
		return nil
	}
	err := r.impl.close()
	r.impl = nil
	return err
}

func (m *Model) Encode(text string) ([]int32, error) {
	if m == nil || m.impl == nil {
		return nil, &Error{Status: StatusClosed, Message: "native model is closed"}
	}
	return m.impl.encode(text)
}

func (m *Model) Capabilities() (Capabilities, error) {
	if m == nil || m.impl == nil {
		return Capabilities{}, &Error{Status: StatusClosed, Message: "native model is closed"}
	}
	return m.impl.capabilities()
}

func (m *Model) NewSession() (*Session, error) {
	if m == nil || m.impl == nil {
		return nil, &Error{Status: StatusClosed, Message: "native model is closed"}
	}
	impl, err := m.impl.newSession()
	if err != nil {
		return nil, err
	}
	return &Session{impl: impl}, nil
}

func (m *Model) Close() error {
	if m == nil || m.impl == nil {
		return nil
	}
	err := m.impl.close()
	m.impl = nil
	return err
}

func (s *Session) SyncPrefix(
	ctx context.Context,
	tokens []int32,
	progress func(completed, total int) error,
) error {
	if s == nil || s.impl == nil {
		return &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.syncPrefix(ctx, tokens, progress)
}

func (s *Session) Generate(
	ctx context.Context,
	options GenerateOptions,
	callback func(StreamEvent) error,
) (GenerateResult, error) {
	if s == nil || s.impl == nil {
		return GenerateResult{}, &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.generate(ctx, options, callback)
}

func (s *Session) Cancel(requestID uint64) error {
	if s == nil || s.impl == nil {
		return &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.cancel(requestID)
}

func (s *Session) Reset() error {
	if s == nil || s.impl == nil {
		return &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.reset()
}

func (s *Session) Info() (SessionInfo, error) {
	if s == nil || s.impl == nil {
		return SessionInfo{}, &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.info()
}

func (s *Session) ExportState(writer io.Writer) (StateDescriptor, error) {
	if s == nil || s.impl == nil {
		return StateDescriptor{}, &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.exportState(writer)
}

func (s *Session) ImportState(reader io.Reader, descriptor StateDescriptor) error {
	if s == nil || s.impl == nil {
		return &Error{Status: StatusClosed, Message: "native session is closed"}
	}
	return s.impl.importState(reader, descriptor)
}

func (s *Session) Close() error {
	if s == nil || s.impl == nil {
		return nil
	}
	err := s.impl.close()
	s.impl = nil
	return err
}
