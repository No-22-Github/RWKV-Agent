package agent

import (
	"context"
	"encoding/json"
	"sync"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/inference"
)

type ToolSpec struct {
	Name        string
	Description string
	Arguments   string
	Parameters  json.RawMessage
	Strict      bool
	Bundle      string
	Permission  ToolPermission
	Control     bool
	// MutatesWorkspace allows successful reads or tests to be repeated after a
	// real workspace change while retaining duplicate protection within one
	// revision.
	MutatesWorkspace bool
	// Replayable marks a pure read with no observable side effects (calculator,
	// search, file listing, reads). When a model repeats the identical call, the
	// runner may re-execute it up to Options.DuplicateReplayLimit times instead
	// of rejecting it outright, keeping the transcript moving under near-greedy
	// decoding. Stateful tools (writes, tests, program runs) must stay false.
	Replayable bool
	// Example is a rendered JSON example of one valid arguments payload, shown
	// in the invalid-argument recovery text. Small models copy the schema shape
	// verbatim ("expression":{"type":"string"}) when the recovery echoes the
	// schema; a concrete literal example breaks that loop.
	Example string
}

type Tool interface {
	Spec() ToolSpec
	Execute(context.Context, json.RawMessage) (any, error)
}

// WorkspaceMutationResult lets a mutating tool report a successful no-op.
// Tools marked MutatesWorkspace default to changed when they do not implement
// this interface.
type WorkspaceMutationResult interface {
	WorkspaceChanged() bool
}

type Options struct {
	MaxSteps                int
	ProtocolRetries         int
	DecisionMaxOutputTokens int
	ControlPrompt           ControlPromptMode
	// TaskControl adds a suite- or task-specific contract after the generic
	// tool protocol. It is recorded by eval manifests for reproducibility.
	TaskControl string
	// TerminalTool requires this tool to succeed before a plain-text final is
	// accepted. If the tool is not offered for a particular Runner, the option
	// is ignored (for example the Primitive arithmetic case has no submit tool).
	TerminalTool string
	// EndOnTerminalTool ends the turn as soon as TerminalTool succeeds. This
	// matches benchmark protocols where submit is itself the scored final action
	// and avoids spending an extra model turn on a redundant plain-text answer.
	EndOnTerminalTool bool
	// DuplicateReplayLimit re-executes identical calls to Replayable tools
	// instead of rejecting them, up to this many consecutive identical calls.
	// Zero keeps the strict rejection behavior. Only the G1i function protocol
	// with repeated-call rejection honors this knob; other protocols are
	// unaffected.
	DuplicateReplayLimit int
	// DuplicateRescueThreshold switches the run into submit-only rescue mode
	// after this many consecutive identical calls (replayed or rejected): the
	// tool catalog is rebuilt to offer only the terminal tool and one explicit
	// rescue instruction is injected. Zero disables the rescue switch.
	DuplicateRescueThreshold int
	// SameToolRescueLimit switches the run into submit-only rescue mode after
	// this many consecutive successful calls to the same tool with no other
	// tool or failure in between. It catches spirals where every call carries
	// fresh arguments (a new duplicate key each step) so the duplicate-based
	// rescue never fires; the transcript shows the model grinding the same
	// tool without progress. Zero disables this check.
	SameToolRescueLimit int
	// PostToolHook optionally augments the transcript after a successful tool
	// execution that was not a duplicate replay. The returned text is appended
	// right next to the tool result, so a scenario-specific reminder reaches
	// the model exactly when the evidence it references is fresh. Eval suites
	// register task-specific hooks here; the generic runner stays
	// scenario-agnostic.
	PostToolHook         func(name string, arguments json.RawMessage, result any, err error) string
	Protocol             ActionProtocol
	Renderer             PromptRenderer
	Generation           continuation.Request
	Observe              func(Event)
	Router               RouteProtocol
	RouteRenderer        PromptRenderer
	RouteRetries         int
	RouteMaxOutputTokens int
	ToolRouter           ToolRouteProtocol
	ToolBundles          []ToolBundle
	// TracePromptBytes caps how much of each rendered prompt is recorded.
	// Zero disables prompt recording entirely; a negative value records the
	// full prompt with no cap.
	TracePromptBytes int
	// CompressFetch enables query-aware compression of long web_fetch results
	// before they enter the transcript (PREFERENCES.md P5-1..P5-3). The raw
	// tool result stays in the step trace; only the feedback copy shrinks.
	CompressFetch bool
	// TokenCount counts tokens with the real RWKV World vocabulary in-process
	// (round-3 step 1; agent.EstimateTokens is no longer allowed to decide
	// thresholds — its bias is +16-40% on English prose/code but −2-4% on
	// lists and Chinese, measured by the round-3 token census). It gates the
	// fetch-compression threshold. Nil means no local vocabulary is available:
	// the compression hook then stays OFF entirely (arming compression on the
	// estimator would drag pages that should stay whole into an extract call
	// whose failure mode is page pollution), while the web tools fall back to
	// the estimator for budget slicing only, where an early cut is the safe
	// direction.
	TokenCount func(string) int
	// NoToolGate applies harness-level enforcement to the semantic no_tool
	// exit (round-2, step 4; round-1 measured the two-sided failure: without
	// an exit the model loops to step exhaustion, with one it claims
	// completion without evidence — E6-2/E6-3). "" keeps the model-only
	// decision. "state" accepts no_tool only after at least one successful
	// tool call in the turn (the catalog hides no_tool until then and late
	// emissions are rejected). "evidence" additionally requires the reason
	// to cite content that appears in an actual Function output of this turn
	// (10-char normalized shingle match); otherwise the exit is rejected and
	// the model must retry.
	NoToolGate string
	// AnswerStageLead forces the answer stage this many steps before the step
	// budget is exhausted (0 = only at MaxSteps, as before) and gives
	// answer-stage tool violations one dedicated re-ask that does not consume
	// the protocol retry budget. With lead=1 and MaxSteps=6 the model gets a
	// real answer-stage attempt at step 5 and a strict re-ask at step 6,
	// instead of one attempt at step 6 that dies on its first violation.
	AnswerStageLead int
}

// DefaultTracePromptBytes keeps a full boundary-sized prompt while bounding a
// pathological workspace file from dominating the trace.
const DefaultTracePromptBytes = 128 * 1024

type ControlPromptMode string

const (
	ControlPromptSystem ControlPromptMode = "system"
	ControlPromptInline ControlPromptMode = "inline"
)

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

type Event struct {
	Kind          EventKind
	Step          int
	ParentStep    int
	Tool          string
	Arguments     json.RawMessage
	Route         Route
	Bundles       []string
	SubagentIndex int
	SubagentTask  string
	DurationMS    int64
	Attempt       int
	MaxAttempts   int
	StatusCode    int
	DelayMS       int64
	Err           error
}

// ToolRetryTrace is a presentation-only record of one transport retry. It is
// retained with the Step but never rendered into the model transcript.
type ToolRetryTrace struct {
	Attempt     int   `json:"attempt"`
	MaxAttempts int   `json:"max_attempts"`
	StatusCode  int   `json:"status_code,omitempty"`
	DelayMS     int64 `json:"delay_ms"`
}

// PromptTrace records exactly what was sent to the model for one generation.
// Greedy decoding makes the prompt the only input that can explain an output
// change, so a run without it cannot attribute a score move to a specific
// harness change. Truncated is set when Bytes exceeded the recording budget.
type PromptTrace struct {
	Prompt          string   `json:"prompt"`
	Bytes           int      `json:"bytes"`
	Truncated       bool     `json:"truncated,omitempty"`
	AssistantPrefix string   `json:"assistant_prefix,omitempty"`
	Stops           []string `json:"stops,omitempty"`
	MaxOutputTokens int      `json:"max_output_tokens,omitempty"`
	ToolsOffered    []string `json:"tools_offered,omitempty"`
}

type Step struct {
	Number          int                       `json:"number"`
	Stage           GenerationStage           `json:"stage"`
	Request         *PromptTrace              `json:"request,omitempty"`
	ModelOutput     string                    `json:"model_output"`
	FinishReason    continuation.FinishReason `json:"finish_reason"`
	Usage           continuation.Usage        `json:"usage"`
	StartedAtMS     int64                     `json:"model_started_at_ms,omitempty"`
	ModelDurationMS int64                     `json:"model_duration_ms,omitempty"`
	ModelError      string                    `json:"model_error,omitempty"`
	ActionType      string                    `json:"action_type,omitempty"`
	Tool            string                    `json:"tool,omitempty"`
	ToolArguments   json.RawMessage           `json:"tool_arguments,omitempty"`
	ToolResult      json.RawMessage           `json:"tool_result,omitempty"`
	// ToolResultFeedback holds the transcript copy of the tool result when
	// query-aware compression replaced it (PREFERENCES.md P5-1..P5-3).
	ToolResultFeedback json.RawMessage      `json:"tool_result_feedback,omitempty"`
	ToolExecuted       bool                 `json:"tool_executed,omitempty"`
	ToolEvidence       bool                 `json:"tool_evidence,omitempty"`
	ToolUnavailable    bool                 `json:"tool_unavailable,omitempty"`
	ToolRejected       string               `json:"tool_rejected_reason,omitempty"`
	ToolError          string               `json:"tool_error,omitempty"`
	ProtocolError      string               `json:"protocol_error,omitempty"`
	ProtocolFailure    ProtocolFailureClass `json:"protocol_failure,omitempty"`
	ProtocolRepaired   bool                 `json:"protocol_repaired,omitempty"`
	StageViolation     bool                 `json:"stage_violation,omitempty"`
	ToolRetries        []ToolRetryTrace     `json:"tool_retries,omitempty"`
	Subagents          []SubagentTrace      `json:"subagents,omitempty"`
	ToolDurationMS     int64                `json:"tool_duration_ms,omitempty"`
	ToolStartedAtMS    int64                `json:"tool_started_at_ms,omitempty"`
	// NoToolRationale and NoToolAnswer retain model-authored abstention text for
	// presentation and audit. They are never tool evidence.
	NoToolRationale string `json:"no_tool_rationale,omitempty"`
	NoToolAnswer    string `json:"no_tool_answer,omitempty"`
}

// SubagentStep is the compact, presentation-safe trace of one child tool call.
// Tool result bodies are deliberately excluded.
type SubagentStep struct {
	Number    int              `json:"number"`
	Tool      string           `json:"tool"`
	Arguments json.RawMessage  `json:"arguments,omitempty"`
	Status    string           `json:"status"`
	Error     string           `json:"error,omitempty"`
	Retries   []ToolRetryTrace `json:"retries,omitempty"`
}

// SubagentTrace records one delegated run without copying large child payloads.
type SubagentTrace struct {
	Index       int            `json:"index"`
	Task        string         `json:"task"`
	Status      string         `json:"status"`
	Error       string         `json:"error,omitempty"`
	Route       Route          `json:"route,omitempty"`
	Bundles     []string       `json:"bundles,omitempty"`
	StartedAtMS int64          `json:"started_at_ms,omitempty"`
	DurationMS  int64          `json:"duration_ms"`
	Output      string         `json:"output,omitempty"`
	Sources     []string       `json:"sources,omitempty"`
	Steps       []SubagentStep `json:"steps,omitempty"`
	StepCount   int            `json:"step_count,omitempty"`
}

// SubagentTraceCarrier lets delegation tools expose typed presentation traces
// to the runner without coupling the runner to a concrete tool package.
type SubagentTraceCarrier interface {
	SubagentTraces() []SubagentTrace
}

// RouteStep records one routing attempt, including the retry a correction
// triggers. The route prompt was previously invisible, so a route change could
// not be traced to the history or instructions that caused it.
type RouteStep struct {
	Attempt       int          `json:"attempt"`
	StartedAtMS   int64        `json:"started_at_ms,omitempty"`
	Request       *PromptTrace `json:"request,omitempty"`
	ModelOutput   string       `json:"model_output"`
	Route         Route        `json:"route,omitempty"`
	Bundles       []string     `json:"bundles,omitempty"`
	ProtocolError string       `json:"protocol_error,omitempty"`
	FailedClosed  bool         `json:"failed_closed,omitempty"`
	DurationMS    int64        `json:"duration_ms,omitempty"`
}

type Result struct {
	Output                 string      `json:"output"`
	OriginalOutput         string      `json:"original_output"`
	StartedAtMS            int64       `json:"started_at_ms,omitempty"`
	RouteSteps             []RouteStep `json:"route_steps,omitempty"`
	AnswerContractRepaired bool        `json:"answer_contract_repaired,omitempty"`
	AnswerViolations       []string    `json:"answer_violations,omitempty"`
	Steps                  []Step      `json:"steps"`
	Route                  Route       `json:"route"`
	Bundles                []string    `json:"bundles,omitempty"`
	ForcedAnswerReason     string      `json:"forced_answer_reason,omitempty"`
	Plan                   *PlanTrace  `json:"plan,omitempty"`
	PlanRejections         int         `json:"plan_rejections,omitempty"`
	PlanFallbacks          int         `json:"plan_fallbacks,omitempty"`
	RescueAttempted        bool        `json:"rescue_attempted,omitempty"`
	RescueSubmitted        bool        `json:"rescue_submitted,omitempty"`
}

type answerViolation string

const (
	violationProtocolTag answerViolation = "protocol_tag"
	violationRoleHeader  answerViolation = "role_header"
	violationJSONPayload answerViolation = "json_payload"
	violationToolEcho    answerViolation = "tool_payload_echo"
)

type PlanTrace struct {
	Subtasks []PlanSubtaskTrace `json:"subtasks"`
	Waves    [][]int            `json:"waves"`
}

type PlanSubtaskTrace struct {
	ID        int             `json:"id"`
	Tool      string          `json:"tool"`
	Arguments json.RawMessage `json:"arguments"`
}

type Runner struct {
	generator         continuation.Generator
	toolCompleter     toolchat.Completer
	tools             map[string]Tool
	toolSpecs         []ToolSpec
	options           Options
	protocol          ActionProtocol
	renderer          PromptRenderer
	responseControl   string
	terminalTool      string
	thinkingMode      inference.ThinkingMode
	semanticNoTool    bool
	decisionFakeThink bool
	closedFakeThink   bool
	router            RouteProtocol
	toolRouter        ToolRouteProtocol
	toolBundles       []ToolBundle
	routeRenderer     PromptRenderer

	runMu   sync.Mutex
	stateMu sync.RWMutex
	history []Message
}
