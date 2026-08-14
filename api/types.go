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

// AgentProtocol selects the product-facing tool transcript.
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
	Provider               Provider          `json:"provider"`
	Model                  string            `json:"model"`
	Endpoint               string            `json:"endpoint,omitempty"`
	APIKey                 string            `json:"apiKey,omitempty"`
	Password               string            `json:"password,omitempty"`
	Headers                map[string]string `json:"headers,omitempty"`
	TokenizerPath          string            `json:"tokenizerPath,omitempty"`
	Backend                string            `json:"backend,omitempty"`
	NativeProvider         string            `json:"nativeProvider,omitempty"`
	Thinking               string            `json:"thinking,omitempty"`
	AgentProtocol          AgentProtocol     `json:"agentProtocol,omitempty"`
	MaxSteps               int               `json:"maxSteps,omitempty"`
	MaxTokens              int               `json:"maxTokens,omitempty"`
	RouteMaxTokens         int               `json:"routeMaxTokens,omitempty"`
	Temperature            float64           `json:"temperature,omitempty"`
	TopK                   int               `json:"topK,omitempty"`
	TopP                   float64           `json:"topP,omitempty"`
	PresencePenalty        float64           `json:"presencePenalty,omitempty"`
	FrequencyPenalty       float64           `json:"frequencyPenalty,omitempty"`
	PenaltyDecay           float64           `json:"penaltyDecay,omitempty"`
	ChatThinking           string            `json:"chatThinking,omitempty"`
	ChatPromptMode         string            `json:"chatPromptMode,omitempty"`
	ChatTokenLimit         string            `json:"chatTokenLimit,omitempty"`
	Stream                 *bool             `json:"stream,omitempty"`
	RWKVStopTokens         string            `json:"rwkvStopTokens,omitempty"`
	ProgressiveTools       *bool             `json:"progressiveTools,omitempty"`
	EnableWeb              bool              `json:"enableWeb,omitempty"`
	BraveAPIKey            string            `json:"braveApiKey,omitempty"`
	BraveEndpoint          string            `json:"braveEndpoint,omitempty"`
	TavilyAPIKey           string            `json:"tavilyApiKey,omitempty"`
	TavilyEndpoint         string            `json:"tavilyEndpoint,omitempty"`
	EnableSubagents        bool              `json:"enableSubagents,omitempty"`
	MaxActiveBatch         int               `json:"maxActiveBatch,omitempty"`
	RemoteBatchWaitMS      int               `json:"remoteBatchWaitMs,omitempty"`
	SubagentMaxParallel    int               `json:"subagentMaxParallel,omitempty"`
	SubagentMaxSteps       int               `json:"subagentMaxSteps,omitempty"`
	SubagentTimeoutSeconds int               `json:"subagentTimeoutSeconds,omitempty"`
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
	EventModelStart EventKind = "model_start"
	EventRouteStart EventKind = "route_start"
	EventRouteDone  EventKind = "route_done"
	EventRetry      EventKind = "protocol_retry"
	EventToolStart  EventKind = "tool_start"
	EventToolDone   EventKind = "tool_done"
)

// Event is a transport-safe Agent loop event.
type Event struct {
	Kind    EventKind `json:"kind"`
	Step    int       `json:"step,omitempty"`
	Tool    string    `json:"tool,omitempty"`
	Route   string    `json:"route,omitempty"`
	Bundles []string  `json:"bundles,omitempty"`
	Error   string    `json:"error,omitempty"`
}

// Step is the public trace summary for one model action.
type Step struct {
	Number        int    `json:"number"`
	Stage         string `json:"stage"`
	ModelOutput   string `json:"modelOutput,omitempty"`
	FinishReason  string `json:"finishReason,omitempty"`
	ActionType    string `json:"actionType,omitempty"`
	Tool          string `json:"tool,omitempty"`
	ToolArguments string `json:"toolArguments,omitempty"`
	ToolResult    string `json:"toolResult,omitempty"`
	ToolExecuted  bool   `json:"toolExecuted,omitempty"`
	ToolError     string `json:"toolError,omitempty"`
}

// Result is one committed Agent turn.
type Result struct {
	Output     string        `json:"output"`
	Route      string        `json:"route,omitempty"`
	Bundles    []string      `json:"bundles,omitempty"`
	Steps      []Step        `json:"steps"`
	Duration   time.Duration `json:"duration"`
	DurationMS int64         `json:"durationMs"`
}

// RemoteModel is one model returned by an OpenAI-compatible models endpoint.
type RemoteModel struct {
	ID string `json:"id"`
}

// Options configure a Service independently of a model.
type Options struct {
	Workspace string
}
