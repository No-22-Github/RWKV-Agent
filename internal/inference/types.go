package inference

import (
	"context"
	"io"
)

type BackendID string
type ModelID string
type ModelFormat string
type ByteSize uint64

const BackendAuto BackendID = "auto"

type Support struct {
	Available bool
	Emulated  bool
	Detail    string
}

type Capabilities struct {
	TextGeneration          Support
	StreamingText           Support
	Cancellation            Support
	StatefulSessions        Support
	StateExport             Support
	StateImport             Support
	StateFork               Support
	PrefixCache             Support
	TokenCounting           Support
	DeterministicSeed       Support
	SupportedBatchSizes     []int
	MaxConcurrentGeneration int
}

type DeviceInfo struct {
	ID   string
	Name string
	Kind string
}

type BackendInfo struct {
	ID                BackendID
	DisplayName       string
	Platform          string
	Device            DeviceInfo
	Formats           []ModelFormat
	Capabilities      Capabilities
	Available         bool
	UnavailableReason string
}

type ModelSource struct {
	Path          string
	TokenizerPath string
}

type ModelInfo struct {
	ID             ModelID
	Fingerprint    string
	Architecture   string
	Format         ModelFormat
	Precision      string
	Quantization   string
	VocabularySize int
	Backend        BackendID
}

type LoadRequest struct {
	Source         ModelSource
	Backend        BackendID
	MemoryBudget   ByteSize
	BackendOptions map[string]string
}

type Progress struct {
	Stage     string
	Completed int64
	Total     int64
}

type ProgressSink func(Progress) error

type Backend interface {
	Info() BackendInfo
	ProbeModel(context.Context, ModelSource) (ModelInfo, error)
	LoadModel(context.Context, LoadRequest, ProgressSink) (Model, error)
}

type Model interface {
	Info() ModelInfo
	Capabilities() Capabilities
	NewSession(context.Context, SessionOptions) (Session, error)
	Close() error
}

type SessionOptions struct{}

type Session interface {
	Generate(context.Context, GenerateRequest, EventSink) (GenerateResult, error)
	CountTokens(context.Context, TokenCountRequest) (int, error)
	Reset(context.Context) error
	StateInfo() SessionStateInfo
	ExportState(context.Context, io.Writer, ExportStateOptions) (StateDescriptor, error)
	ImportState(context.Context, io.Reader, ImportStateOptions) (StateDescriptor, error)
	Fork(context.Context) (Session, error)
	Stats() SessionStats
	Close() error
}

type Role string

const (
	RoleSystem    Role = "system"
	RoleUser      Role = "user"
	RoleAssistant Role = "assistant"
	RoleTool      Role = "tool"
)

type ContentKind string

const ContentText ContentKind = "text"

type ContentPart struct {
	Kind ContentKind
	Text string
}

type Message struct {
	Role       Role
	Name       string
	ToolCallID string
	Parts      []ContentPart
}

func TextMessage(role Role, text string) Message {
	return Message{
		Role:  role,
		Parts: []ContentPart{{Kind: ContentText, Text: text}},
	}
}

type RawInput struct {
	Text string
}

type PromptOptions struct {
	Reasoning bool
}

type SamplingOptions struct {
	Temperature      float32
	TopK             int
	TopP             float32
	PresencePenalty  float32
	FrequencyPenalty float32
	PenaltyDecay     float32
	Seed             *int64
}

type GenerationLimits struct {
	MaxOutputTokens int
}

type StopSequence struct {
	Text   string
	Tokens []int32
}

type CommitPolicy string

const (
	CommitOnSuccess CommitPolicy = "on_success"
	CommitPartial   CommitPolicy = "partial"
)

type GenerateRequest struct {
	Messages []Message
	Raw      *RawInput
	Prompt   PromptOptions
	Sampling SamplingOptions
	Limits   GenerationLimits
	Stops    []StopSequence
	Commit   CommitPolicy
}

type TokenCountRequest struct {
	Messages []Message
	Raw      *RawInput
	Prompt   PromptOptions
}

type EventKind string

const (
	EventStarted         EventKind = "started"
	EventPrefillProgress EventKind = "prefill_progress"
	EventOutputDelta     EventKind = "output_delta"
	EventWarning         EventKind = "warning"
)

type OutputChannel string

const (
	ChannelFinal     OutputChannel = "final"
	ChannelReasoning OutputChannel = "reasoning"
)

type OutputDelta struct {
	Channel OutputChannel
	Text    string
	Tokens  []int32
}

type GenerationEvent struct {
	Kind     EventKind
	Progress *Progress
	Delta    *OutputDelta
	Warning  string
}

type EventSink func(GenerationEvent) error

type FinishReason string

const (
	FinishStop      FinishReason = "stop"
	FinishLength    FinishReason = "length"
	FinishCancelled FinishReason = "cancelled"
	FinishError     FinishReason = "error"
	FinishUnknown   FinishReason = "unknown"
)

type Usage struct {
	PromptTokens     int
	CompletionTokens int
}

type Timings struct {
	PrefillTokensPerSecond float64
	DecodeTokensPerSecond  float64
}

type GenerateResult struct {
	Output        string
	OutputTokens  []int32
	FinishReason  FinishReason
	Usage         Usage
	Timings       Timings
	Committed     bool
	StateRevision string
}

type SessionStateInfo struct {
	Revision   string
	Status     string
	TokenCount int
}

type SessionStats struct {
	Generations uint64
	LastTimings Timings
}

type StateDescriptor struct {
	FormatVersion    int
	ModelFingerprint string
	StateRevision    string
}

type ExportStateOptions struct{}
type ImportStateOptions struct{}
