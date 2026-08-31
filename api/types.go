// Package api exposes the application-level model and agent API shared by
// command-line, TUI, desktop, and browser clients.
package api

import "time"

// Provider selects the continuation implementation used by a Service.
type Provider string

const (
	ProviderLocal           Provider = "local"
	ProviderChatCompletions Provider = "chat-completions"
	ProviderRWKVLightning   Provider = "rwkv-lightning"
)

// AgentProtocol selects the product-facing tool transcript. The zero value
// resolves to XML; Markdown remains an explicit option.
type AgentProtocol string

const (
	AgentProtocolMarkdown AgentProtocol = "markdown"
	AgentProtocolXML      AgentProtocol = "xml"
)

// ModelState describes the lifecycle state visible to clients.
type ModelState string

const (
	ModelIdle    ModelState = "idle"
	ModelLoading ModelState = "loading"
	ModelReady   ModelState = "ready"
	ModelError   ModelState = "error"
)

// Config configures one local or remote model provider. Secret fields are
// accepted as input but are never included in Status.
type Config struct {
	Provider       Provider          `json:"provider"`
	Model          string            `json:"model"`
	Endpoint       string            `json:"endpoint,omitempty"`
	APIKey         string            `json:"apiKey,omitempty"`
	Password       string            `json:"password,omitempty"`
	Headers        map[string]string `json:"headers,omitempty"`
	TokenizerPath  string            `json:"tokenizerPath,omitempty"`
	Backend        string            `json:"backend,omitempty"`
	NativeProvider string            `json:"nativeProvider,omitempty"`
	Thinking       string            `json:"thinking,omitempty"`
	AgentProtocol  AgentProtocol     `json:"agentProtocol,omitempty"`
	// TaskControl is the user's free-text contract appended verbatim after the
	// transcript's system prompt ("Task-specific contract:" block). It is the
	// supported personalization surface; the protocol-owned instructions stay
	// immutable so the measured transcript contract cannot be broken here.
	TaskControl       string  `json:"taskControl,omitempty"`
	SemanticNoTool    *bool   `json:"semanticNoTool,omitempty"`
	DecisionFakeThink bool    `json:"decisionFakeThink,omitempty"`
	DeepToolAnchor    *bool   `json:"deepToolAnchor,omitempty"`
	MaxSteps          int     `json:"maxSteps,omitempty"`
	MaxTokens         int     `json:"maxTokens,omitempty"`
	DecisionMaxTokens int     `json:"decisionMaxTokens,omitempty"`
	RouteMaxTokens    int     `json:"routeMaxTokens,omitempty"`
	TracePromptBytes  *int    `json:"tracePromptBytes,omitempty"`
	Temperature       float64 `json:"temperature,omitempty"`
	TopK              int     `json:"topK,omitempty"`
	TopP              float64 `json:"topP,omitempty"`
	PresencePenalty   float64 `json:"presencePenalty,omitempty"`
	FrequencyPenalty  float64 `json:"frequencyPenalty,omitempty"`
	PenaltyDecay      float64 `json:"penaltyDecay,omitempty"`
	ChatThinking      string  `json:"chatThinking,omitempty"`
	ChatPromptMode    string  `json:"chatPromptMode,omitempty"`
	ChatTokenLimit    string  `json:"chatTokenLimit,omitempty"`
	Stream            *bool   `json:"stream,omitempty"`
	RWKVStopTokens    string  `json:"rwkvStopTokens,omitempty"`
	// ProgressiveTools enables the optional capability Router. Nil defaults to
	// false so the XML decision stage owns tool selection directly.
	ProgressiveTools *bool  `json:"progressiveTools,omitempty"`
	EnableWeb        bool   `json:"enableWeb,omitempty"`
	BraveAPIKey      string `json:"braveApiKey,omitempty"`
	BraveEndpoint    string `json:"braveEndpoint,omitempty"`
	TavilyAPIKey     string `json:"tavilyApiKey,omitempty"`
	TavilyEndpoint   string `json:"tavilyEndpoint,omitempty"`
	EnableSubagents  bool   `json:"enableSubagents,omitempty"`
	// CompressFetch enables query-aware compression of long web_fetch results
	// before they enter the agent transcript (PREFERENCES.md P5-1..P5-3).
	CompressFetch          bool `json:"compressFetch,omitempty"`
	MaxActiveBatch         int  `json:"maxActiveBatch,omitempty"`
	RemoteBatchWaitMS      int  `json:"remoteBatchWaitMs,omitempty"`
	SubagentMaxParallel    int  `json:"subagentMaxParallel,omitempty"`
	SubagentMaxSteps       int  `json:"subagentMaxSteps,omitempty"`
	SubagentTimeoutSeconds int  `json:"subagentTimeoutSeconds,omitempty"`
}

// Status is the non-secret model state displayed by clients.
type Status struct {
	State        ModelState `json:"state"`
	Provider     Provider   `json:"provider,omitempty"`
	Model        string     `json:"model,omitempty"`
	Endpoint     string     `json:"endpoint,omitempty"`
	Backend      string     `json:"backend,omitempty"`
	Format       string     `json:"format,omitempty"`
	Architecture string     `json:"architecture,omitempty"`
	Workspace    string     `json:"workspace"`
	Message      string     `json:"message,omitempty"`
	HeaderNames  []string   `json:"headerNames,omitempty"`
	HasAPIKey    bool       `json:"hasApiKey"`
	UpdatedAt    time.Time  `json:"updatedAt"`
}

// EventKind identifies an observable Agent loop transition.
type EventKind string

const (
	EventModelStart    EventKind = "model_start"
	EventModelDone     EventKind = "model_done"
	EventRouteStart    EventKind = "route_start"
	EventRouteDone     EventKind = "route_done"
	EventRetry         EventKind = "protocol_retry"
	EventToolStart     EventKind = "tool_start"
	EventToolRetry     EventKind = "tool_retry"
	EventToolDone      EventKind = "tool_done"
	EventSubagentStart EventKind = "subagent_start"
	EventSubagentDone  EventKind = "subagent_done"
)

// Event is a transport-safe Agent loop event.
type Event struct {
	Kind          EventKind `json:"kind"`
	Step          int       `json:"step,omitempty"`
	ParentStep    int       `json:"parentStep,omitempty"`
	Tool          string    `json:"tool,omitempty"`
	Arguments     string    `json:"arguments,omitempty"`
	Route         string    `json:"route,omitempty"`
	Bundles       []string  `json:"bundles,omitempty"`
	SubagentIndex int       `json:"subagentIndex,omitempty"`
	SubagentTask  string    `json:"subagentTask,omitempty"`
	DurationMS    int64     `json:"durationMs,omitempty"`
	Attempt       int       `json:"attempt,omitempty"`
	MaxAttempts   int       `json:"maxAttempts,omitempty"`
	StatusCode    int       `json:"statusCode,omitempty"`
	DelayMS       int64     `json:"delayMs,omitempty"`
	Error         string    `json:"error,omitempty"`
}

type ToolRetryTrace struct {
	Attempt     int   `json:"attempt"`
	MaxAttempts int   `json:"maxAttempts"`
	StatusCode  int   `json:"statusCode,omitempty"`
	DelayMS     int64 `json:"delayMs"`
}

// PromptTrace is the bounded request snapshot that produced one model output.
// It can contain local conversation and workspace content and is intended for
// the local trajectory inspector, not telemetry.
type PromptTrace struct {
	Prompt          string   `json:"prompt"`
	Bytes           int      `json:"bytes"`
	Truncated       bool     `json:"truncated,omitempty"`
	AssistantPrefix string   `json:"assistantPrefix,omitempty"`
	Stops           []string `json:"stops,omitempty"`
	MaxOutputTokens int      `json:"maxOutputTokens,omitempty"`
	ToolsOffered    []string `json:"toolsOffered,omitempty"`
}

// Usage is the token accounting reported by the configured provider. The
// cache and reasoning breakdowns come from OpenAI-compatible usage details and
// stay zero for the local and RWKV continuation backends.
type Usage struct {
	PromptTokens     int `json:"promptTokens,omitempty"`
	CompletionTokens int `json:"completionTokens,omitempty"`
	CacheReadTokens  int `json:"cacheReadTokens,omitempty"`
	CacheWriteTokens int `json:"cacheWriteTokens,omitempty"`
	ReasoningTokens  int `json:"reasoningTokens,omitempty"`
}

// RouteStep records one routing generation, including correction retries.
type RouteStep struct {
	Attempt       int          `json:"attempt"`
	StartedAtMS   int64        `json:"startedAtMs,omitempty"`
	Request       *PromptTrace `json:"request,omitempty"`
	ModelOutput   string       `json:"modelOutput,omitempty"`
	Route         string       `json:"route,omitempty"`
	Bundles       []string     `json:"bundles,omitempty"`
	ProtocolError string       `json:"protocolError,omitempty"`
	FailedClosed  bool         `json:"failedClosed,omitempty"`
	DurationMS    int64        `json:"durationMs,omitempty"`
}

// SubagentStep is one compact child tool invocation. Tool result bodies are
// omitted so this trace is safe to retain in presentation storage.
type SubagentStep struct {
	Number    int              `json:"number"`
	Tool      string           `json:"tool"`
	Arguments string           `json:"arguments,omitempty"`
	Status    string           `json:"status"`
	Error     string           `json:"error,omitempty"`
	Retries   []ToolRetryTrace `json:"retries,omitempty"`
}

// SubagentTrace is one delegated Agent run attached to its parent tool step.
type SubagentTrace struct {
	Index       int            `json:"index"`
	Task        string         `json:"task"`
	Status      string         `json:"status"`
	Error       string         `json:"error,omitempty"`
	Route       string         `json:"route,omitempty"`
	Bundles     []string       `json:"bundles,omitempty"`
	StartedAtMS int64          `json:"startedAtMs,omitempty"`
	DurationMS  int64          `json:"durationMs"`
	Output      string         `json:"output,omitempty"`
	Sources     []string       `json:"sources,omitempty"`
	Steps       []SubagentStep `json:"steps,omitempty"`
}

// Step is the public trace summary for one model action.
type Step struct {
	Number           int              `json:"number"`
	Stage            string           `json:"stage"`
	Request          *PromptTrace     `json:"request,omitempty"`
	ModelOutput      string           `json:"modelOutput,omitempty"`
	FinishReason     string           `json:"finishReason,omitempty"`
	Usage            Usage            `json:"usage"`
	StartedAtMS      int64            `json:"startedAtMs,omitempty"`
	ModelDurationMS  int64            `json:"modelDurationMs,omitempty"`
	ModelError       string           `json:"modelError,omitempty"`
	ActionType       string           `json:"actionType,omitempty"`
	Tool             string           `json:"tool,omitempty"`
	ToolArguments    string           `json:"toolArguments,omitempty"`
	ToolResult       string           `json:"toolResult,omitempty"`
	ToolExecuted     bool             `json:"toolExecuted,omitempty"`
	ToolEvidence     bool             `json:"toolEvidence,omitempty"`
	ToolUnavailable  bool             `json:"toolUnavailable,omitempty"`
	ToolRejected     string           `json:"toolRejected,omitempty"`
	ToolError        string           `json:"toolError,omitempty"`
	ProtocolError    string           `json:"protocolError,omitempty"`
	ProtocolRepaired bool             `json:"protocolRepaired,omitempty"`
	StageViolation   bool             `json:"stageViolation,omitempty"`
	ToolRetries      []ToolRetryTrace `json:"toolRetries,omitempty"`
	Subagents        []SubagentTrace  `json:"subagents,omitempty"`
	ToolDurationMS   int64            `json:"toolDurationMs,omitempty"`
	ToolStartedAtMS  int64            `json:"toolStartedAtMs,omitempty"`
	NoToolRationale  string           `json:"noToolRationale,omitempty"`
	NoToolAnswer     string           `json:"noToolAnswer,omitempty"`
}

// Result is one committed Agent turn.
type Result struct {
	Output                 string        `json:"output"`
	Error                  string        `json:"error,omitempty"`
	OriginalOutput         string        `json:"originalOutput,omitempty"`
	StartedAtMS            int64         `json:"startedAtMs,omitempty"`
	RouteSteps             []RouteStep   `json:"routeSteps,omitempty"`
	Route                  string        `json:"route,omitempty"`
	Bundles                []string      `json:"bundles,omitempty"`
	Steps                  []Step        `json:"steps"`
	AnswerContractRepaired bool          `json:"answerContractRepaired,omitempty"`
	AnswerViolations       []string      `json:"answerViolations,omitempty"`
	ForcedAnswerReason     string        `json:"forcedAnswerReason,omitempty"`
	Duration               time.Duration `json:"duration"`
	DurationMS             int64         `json:"durationMs"`
}

// RemoteModel is one model returned by an OpenAI-compatible models endpoint.
type RemoteModel struct {
	ID string `json:"id"`
}

// ToolCall is one native tool invocation retained in a conversation transcript.
type ToolCall struct {
	ID        string `json:"id"`
	Name      string `json:"name"`
	Arguments string `json:"arguments"`
}

// ConversationMessage is one complete Harness transcript entry. Unlike the
// presentation-only chat messages, this also retains tool calls and results so
// a restored session has the same semantic context as the original session.
type ConversationMessage struct {
	Role             string     `json:"role"`
	Content          string     `json:"content,omitempty"`
	ReasoningContent string     `json:"reasoningContent,omitempty"`
	Name             string     `json:"name,omitempty"`
	ToolCallID       string     `json:"toolCallId,omitempty"`
	ToolCalls        []ToolCall `json:"toolCalls,omitempty"`
}

// Options configure a Service independently of a model.
type Options struct {
	Workspace string
}
