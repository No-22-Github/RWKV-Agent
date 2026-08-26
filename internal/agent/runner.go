package agent

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"
	"sync"
	"time"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/inference"
)

var (
	ErrProtocol             = errors.New("agent protocol error")
	ErrMaxSteps             = errors.New("agent reached the step limit")
	ErrInvalidToolArguments = errors.New("invalid tool arguments")
	ErrProviderUnavailable  = errors.New("provider unavailable")
	ErrNoWorkspaceEvidence  = errors.New("agent could not obtain workspace evidence")
	ErrStageViolation       = fmt.Errorf("%w: action is not allowed in this generation stage", ErrProtocol)
)

// retryEchoBudget caps how many runes of a rejected response are echoed back to
// the model on a protocol retry.
const retryEchoBudget = 480

// retryEcho condenses a rejected response before it re-enters the transcript.
// Runaway reasoning is the common cause of a retry, and echoing thousands of
// characters of it verbatim poisons the context so the retry repeats the same
// failure. Unclosed thinking is dropped entirely; anything else is truncated.
func retryEcho(modelAction string, err error) string {
	trimmed := strings.TrimSpace(modelAction)
	if trimmed == "" {
		return ""
	}
	if errors.Is(err, ErrUnclosedThink) {
		return ""
	}
	runes := []rune(trimmed)
	if len(runes) <= retryEchoBudget {
		return trimmed
	}
	if errors.Is(err, ErrOutputTokenLimit) {
		return ""
	}
	return string(runes[:retryEchoBudget]) + "\n[truncated]"
}

func directResponseControl(mode inference.ThinkingMode) string {
	prompt := `You are a helpful conversational assistant.
Answer the current user message directly and naturally in the user's language.
Use the committed conversation and general knowledge.
Workspace tools are unavailable for this turn. Do not claim to have inspected files.
`
	switch mode {
	case inference.ThinkingFast:
		return prompt + "Answer directly. Do not open a <think> block, output tool calls, or emit role labels."
	case inference.ThinkingFull:
		return prompt + "Close your thinking with </think>, then answer directly. Do not output tool calls or emit role labels."
	default:
		return prompt + "Do not output tool calls, role labels, or hidden reasoning."
	}
}

const postToolDecisionReminder = `Use the Tool results above to continue the current task.
If the evidence is sufficient, answer now. Call another tool only for a specific missing fact.
Never repeat a successful tool call. Do not open a <think> block or repeat the Tool payload.`

const duplicateToolAnswerReminder = `That tool call was rejected because it repeats a successful call.
Answer the current task from the evidence already collected.`

const (
	answerContractFallbackEN = "I could not provide a reliable answer because the model output violated the answer contract. Please retry."
	answerContractFallbackZH = "模型输出不符合答案契约，因此无法可靠展示。请重试。"
)

const (
	maxConsecutiveToolFailures  = 2
	forcedAnswerStepBudget      = "step_budget_after_tool_attempt"
	forcedAnswerDuplicateCall   = "duplicate_tool_call"
	forcedAnswerProviderFailure = "provider_unavailable"
	rejectedUnknownTool         = "unknown_tool"
	rejectedDuplicateCall       = "duplicate_tool_call"
	rejectedFailureLimit        = "consecutive_tool_failures"
	rejectedProviderUnavailable = "provider_unavailable"
	rejectedRescueRestricted    = "rescue_submit_only"
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
	Number           int                       `json:"number"`
	Stage            GenerationStage           `json:"stage"`
	Request          *PromptTrace              `json:"request,omitempty"`
	ModelOutput      string                    `json:"model_output"`
	FinishReason     continuation.FinishReason `json:"finish_reason"`
	Usage            continuation.Usage        `json:"usage"`
	ModelDurationMS  int64                     `json:"model_duration_ms,omitempty"`
	ModelError       string                    `json:"model_error,omitempty"`
	ActionType       string                    `json:"action_type,omitempty"`
	Tool             string                    `json:"tool,omitempty"`
	ToolArguments    json.RawMessage           `json:"tool_arguments,omitempty"`
	ToolResult       json.RawMessage           `json:"tool_result,omitempty"`
	ToolExecuted     bool                      `json:"tool_executed,omitempty"`
	ToolEvidence     bool                      `json:"tool_evidence,omitempty"`
	ToolUnavailable  bool                      `json:"tool_unavailable,omitempty"`
	ToolRejected     string                    `json:"tool_rejected_reason,omitempty"`
	ToolError        string                    `json:"tool_error,omitempty"`
	ProtocolError    string                    `json:"protocol_error,omitempty"`
	ProtocolRepaired bool                      `json:"protocol_repaired,omitempty"`
	StageViolation   bool                      `json:"stage_violation,omitempty"`
	ToolRetries      []ToolRetryTrace          `json:"tool_retries,omitempty"`
	Subagents        []SubagentTrace           `json:"subagents,omitempty"`
	ToolDurationMS   int64                     `json:"tool_duration_ms,omitempty"`
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
	Index      int            `json:"index"`
	Task       string         `json:"task"`
	Status     string         `json:"status"`
	Error      string         `json:"error,omitempty"`
	Route      Route          `json:"route,omitempty"`
	Bundles    []string       `json:"bundles,omitempty"`
	DurationMS int64          `json:"duration_ms"`
	Output     string         `json:"output,omitempty"`
	Sources    []string       `json:"sources,omitempty"`
	Steps      []SubagentStep `json:"steps,omitempty"`
	StepCount  int            `json:"step_count,omitempty"`
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
	generator       continuation.Generator
	toolCompleter   toolchat.Completer
	tools           map[string]Tool
	toolSpecs       []ToolSpec
	options         Options
	protocol        ActionProtocol
	renderer        PromptRenderer
	control         string
	responseControl string
	terminalTool    string
	thinkingMode    inference.ThinkingMode
	router          RouteProtocol
	toolRouter      ToolRouteProtocol
	toolBundles     []ToolBundle
	routeRenderer   PromptRenderer

	runMu   sync.Mutex
	stateMu sync.RWMutex
	history []Message
}

func NewRunner(generator continuation.Generator, tools []Tool, options Options) (*Runner, error) {
	if generator == nil {
		return nil, fmt.Errorf("%w: continuation generator is required", continuation.ErrInvalidRequest)
	}
	if options.MaxSteps <= 0 {
		options.MaxSteps = 6
	}
	if options.MaxSteps < 2 {
		return nil, fmt.Errorf(
			"%w: at least two steps are required to reserve a final answer after tool use",
			continuation.ErrInvalidRequest,
		)
	}
	if options.ProtocolRetries < 0 {
		return nil, fmt.Errorf("%w: protocol retries cannot be negative", continuation.ErrInvalidRequest)
	}
	if options.RouteRetries < 0 {
		return nil, fmt.Errorf("%w: route retries cannot be negative", continuation.ErrInvalidRequest)
	}
	if options.DecisionMaxOutputTokens < 0 {
		return nil, fmt.Errorf(
			"%w: decision output token limit cannot be negative",
			continuation.ErrInvalidRequest,
		)
	}
	if options.ControlPrompt == "" {
		options.ControlPrompt = ControlPromptSystem
	}
	if options.ControlPrompt != ControlPromptSystem && options.ControlPrompt != ControlPromptInline {
		return nil, fmt.Errorf(
			"%w: invalid control prompt mode %q",
			continuation.ErrInvalidRequest,
			options.ControlPrompt,
		)
	}
	if options.Protocol == nil {
		options.Protocol = G1IProtocol{}
	}
	if options.Renderer == nil {
		options.Renderer = RWKVChatRenderer{}
	}
	if options.Router != nil && options.RouteRenderer == nil {
		options.RouteRenderer = RWKVChatRenderer{}
	}
	if options.ToolRouter != nil && options.RouteRenderer == nil {
		options.RouteRenderer = RWKVChatRenderer{}
	}
	if options.Router != nil && options.ToolRouter != nil {
		return nil, fmt.Errorf("%w: Router and ToolRouter are mutually exclusive", continuation.ErrInvalidRequest)
	}
	if options.Router != nil || options.ToolRouter != nil {
		routeThinkingMode := rendererThinkingMode(options.RouteRenderer)
		if routeThinkingMode != inference.ThinkingOff {
			return nil, fmt.Errorf(
				"%w: route renderer must use thinking mode %q; got %q",
				continuation.ErrInvalidRequest,
				inference.ThinkingOff,
				routeThinkingMode,
			)
		}
	}
	applyGenerationDefaults(&options.Generation)
	if options.DecisionMaxOutputTokens == 0 {
		options.DecisionMaxOutputTokens = 96
	}
	if options.DecisionMaxOutputTokens > options.Generation.MaxOutputTokens {
		options.DecisionMaxOutputTokens = options.Generation.MaxOutputTokens
	}
	if options.Router != nil || options.ToolRouter != nil {
		if options.RouteMaxOutputTokens == 0 {
			options.RouteMaxOutputTokens = 16
		}
		if options.RouteMaxOutputTokens < 1 {
			return nil, fmt.Errorf(
				"%w: route output token limit must be positive",
				continuation.ErrInvalidRequest,
			)
		}
		if options.RouteMaxOutputTokens > options.Generation.MaxOutputTokens {
			options.RouteMaxOutputTokens = options.Generation.MaxOutputTokens
		}
	}

	registered := make(map[string]Tool, len(tools))
	specs := make([]ToolSpec, 0, len(tools))
	for _, tool := range tools {
		if tool == nil {
			return nil, fmt.Errorf("%w: nil tool", continuation.ErrInvalidRequest)
		}
		spec := tool.Spec()
		if spec.Name == "" || spec.Description == "" || spec.Arguments == "" {
			return nil, fmt.Errorf("%w: incomplete tool specification", continuation.ErrInvalidRequest)
		}
		if _, exists := registered[spec.Name]; exists {
			return nil, fmt.Errorf("%w: duplicate tool %q", continuation.ErrInvalidRequest, spec.Name)
		}
		registered[spec.Name] = tool
		specs = append(specs, spec)
	}
	if options.ToolRouter != nil {
		loader, err := newLoadToolsTool(options.ToolBundles)
		if err != nil {
			return nil, err
		}
		if _, exists := registered[loader.Spec().Name]; exists {
			return nil, fmt.Errorf("%w: duplicate tool %q", continuation.ErrInvalidRequest, loader.Spec().Name)
		}
		registered[loader.Spec().Name] = loader
		specs = append(specs, loader.Spec())
	}
	if !preservesToolOrder(options.Protocol) {
		sort.Slice(specs, func(left, right int) bool {
			return specs[left].Name < specs[right].Name
		})
	}
	var toolCompleter toolchat.Completer
	if candidate, ok := generator.(toolchat.Completer); ok && candidate.NativeToolCalling() {
		for _, spec := range specs {
			if err := validateNativeToolSpec(spec); err != nil {
				return nil, err
			}
		}
		toolCompleter = candidate
	}
	thinkingMode := rendererThinkingMode(options.Renderer)
	responseControl := directResponseControl(thinkingMode)
	if len(specs) > 0 {
		var capabilities strings.Builder
		capabilities.WriteString(
			"\nOnly when the user asks about your capabilities, describe these read-only capabilities:\n",
		)
		for _, spec := range specs {
			fmt.Fprintf(&capabilities, "- %s: %s\n", spec.Name, spec.Description)
		}
		responseControl += strings.TrimRight(capabilities.String(), "\n")
	}
	control := toolControlPrompt(options.Protocol, specs, thinkingMode, toolCompleter != nil)
	if taskControl := strings.TrimSpace(options.TaskControl); taskControl != "" {
		control += "\n\nTask-specific contract:\n" + taskControl
	}
	terminalTool := ""
	if _, offered := registered[options.TerminalTool]; offered {
		terminalTool = options.TerminalTool
	}
	return &Runner{
		generator:       generator,
		toolCompleter:   toolCompleter,
		tools:           registered,
		toolSpecs:       append([]ToolSpec(nil), specs...),
		options:         options,
		protocol:        options.Protocol,
		renderer:        options.Renderer,
		control:         control,
		responseControl: responseControl,
		terminalTool:    terminalTool,
		thinkingMode:    thinkingMode,
		router:          options.Router,
		toolRouter:      options.ToolRouter,
		toolBundles:     append([]ToolBundle(nil), options.ToolBundles...),
		routeRenderer:   options.RouteRenderer,
	}, nil
}

func rendererThinkingMode(renderer PromptRenderer) inference.ThinkingMode {
	switch renderer := renderer.(type) {
	case RWKVChatRenderer:
		return renderer.thinkingMode()
	case *RWKVChatRenderer:
		return renderer.thinkingMode()
	default:
		return inference.ThinkingOff
	}
}

type assistantPrefixAppender interface {
	appendAssistantPrefix(string, string) (string, bool)
}

// appendAssistantPrefix is the single framing seam for continuation prefixes.
// A renderer may reject injection when its final bytes already open another
// protocol block (for example RWKV full/fast thinking). Renderers without an
// explicit seam retain the legacy space-separated continuation framing.
func appendAssistantPrefix(renderer PromptRenderer, prompt, prefix string) (string, bool) {
	if prefix == "" {
		return prompt, false
	}
	if appender, ok := renderer.(assistantPrefixAppender); ok {
		return appender.appendAssistantPrefix(prompt, prefix)
	}
	return prompt + " " + prefix, true
}

func appendRequiredAssistantPrefix(renderer PromptRenderer, prompt, prefix string) (string, error) {
	framed, injected := appendAssistantPrefix(renderer, prompt, prefix)
	if !injected {
		return "", fmt.Errorf(
			"%w: renderer %q cannot safely inject required assistant prefix %q",
			continuation.ErrInvalidRequest,
			renderer.ID(),
			prefix,
		)
	}
	return framed, nil
}

func applyGenerationDefaults(request *continuation.Request) {
	if request.MaxOutputTokens == 0 {
		request.MaxOutputTokens = 256
	}
	if request.Sampling.Temperature == 0 {
		request.Sampling.Temperature = 1
	}
	if request.Sampling.TopK == 0 {
		request.Sampling.TopK = 1
	}
	if request.Sampling.TopP == 0 {
		request.Sampling.TopP = 1
	}
	if request.Sampling.PenaltyDecay == 0 {
		if request.Sampling.PresencePenalty == 0 && request.Sampling.FrequencyPenalty == 0 {
			request.Sampling.PenaltyDecay = 1
		} else {
			request.Sampling.PenaltyDecay = 0.99
		}
	}
}

func (r *Runner) Run(ctx context.Context, prompt string) (Result, error) {
	return r.RunWithObserver(ctx, prompt, nil)
}

// RunWithObserver executes and transactionally commits one conversation turn.
// A cancelled or failed turn never changes History.
func (r *Runner) RunWithObserver(
	ctx context.Context,
	prompt string,
	observer func(Event),
) (Result, error) {
	if strings.TrimSpace(prompt) == "" {
		return Result{}, fmt.Errorf("%w: prompt is required", continuation.ErrInvalidRequest)
	}
	r.runMu.Lock()
	defer r.runMu.Unlock()

	task := strings.TrimSpace(prompt)
	history := r.History()
	result := Result{
		Steps: make([]Step, 0, r.options.MaxSteps),
		Route: RouteInspect,
	}
	activeSpecs := append([]ToolSpec(nil), r.toolSpecs...)
	activeTools := r.tools
	if r.toolRouter != nil {
		decision, routeSteps, routeErr := r.decideToolRoute(ctx, history, task, observer)
		result.RouteSteps = routeSteps
		if routeErr != nil {
			return result, routeErr
		}
		result.Route = decision.Route
		result.Bundles = append([]string(nil), decision.Bundles...)
		activeSpecs = toolSpecsForBundles(r.toolSpecs, result.Bundles)
		activeTools = toolsForSpecs(r.tools, activeSpecs)
	} else if r.router != nil {
		route, routeSteps, routeErr := r.decideRoute(ctx, history, task, observer)
		result.RouteSteps = routeSteps
		if routeErr != nil {
			return result, routeErr
		}
		result.Route = route
	}
	messages := make([]Message, 0, len(history)+2)
	control := r.controlForSpecs(activeSpecs)
	if result.Route == RouteRespond {
		control = r.responseControl
	}
	messages = append(messages, Message{Role: RoleSystem, Content: control})
	messages = append(messages, history...)
	messages = append(messages, Message{Role: RoleUser, Content: task})
	if r.options.ControlPrompt == ControlPromptInline {
		label := "Repository task:"
		if result.Route == RouteRespond {
			label = "Current user message:"
		}
		messages = append([]Message(nil), history...)
		messages = append(messages, Message{
			Role:    RoleUser,
			Content: control + "\n\n" + label + "\n" + task,
		})
	}

	turnMessages := []Message{{Role: RoleUser, Content: task}}
	retries := 0
	routeViolations := 0
	seenSuccessfulToolCalls := make(map[string]int)
	failedToolCallEpochs := make(map[string]int)
	unavailableTools := make(map[string]struct{})
	var unverified []string
	successfulToolCalls := 0
	toolAttempts := 0
	hasToolEvidence := false
	consecutiveFailedTool := ""
	consecutiveToolFailures := 0
	lastNativeCallKey := ""
	nativeRepeatStreak := 0
	sameCallStreak := 0
	lastSameCallKey := ""
	sameToolSuccessStreak := 0
	lastSameToolName := ""
	rescueMode := false
	workspaceRevision := 0
	stage := StageDecision
	assistantPrefix := ""
	forceAnswer := false
	terminalToolCompleted := r.terminalTool == "" || result.Route == RouteRespond
	if (r.router != nil || r.toolRouter != nil) && result.Route == RouteInspect {
		assistantPrefix = r.protocol.ToolCallPrefix()
	}
	for step := 1; step <= r.options.MaxSteps; step++ {
		if result.Route == RouteInspect &&
			toolAttempts > 0 &&
			terminalToolCompleted &&
			(step == r.options.MaxSteps || forceAnswer) {
			if !hasToolEvidence {
				return result, noWorkspaceEvidenceError()
			}
			answerMessages, prefix := r.protocol.PrepareAnswer(
				messages,
				unverified,
				r.thinkingMode,
			)
			if len(answerMessages) == 0 || strings.TrimSpace(prefix) == "" {
				return result, fmt.Errorf(
					"%w: protocol did not prepare an answer stage",
					ErrProtocol,
				)
			}
			messages = answerMessages
			assistantPrefix = prefix
			stage = StageAnswer
			if result.ForcedAnswerReason == "" {
				result.ForcedAnswerReason = forcedAnswerStepBudget
			}
		}
		r.observe(Event{Kind: EventModelStart, Step: step}, observer)
		rendered, err := r.renderer.Render(messages)
		if err != nil {
			return result, err
		}
		request := r.options.Generation
		request.Prompt = rendered
		request.Stops = r.protocol.Stops(stage)
		if protocol, ok := r.protocol.(interface {
			stopsWithPrefix(GenerationStage, string) []string
		}); ok {
			request.Stops = protocol.stopsWithPrefix(stage, assistantPrefix)
		}
		if stage == StageDecision &&
			result.Route == RouteInspect &&
			successfulToolCalls == 0 {
			request.MaxOutputTokens = r.options.DecisionMaxOutputTokens
		}
		requireNativeTool := r.toolCompleter != nil &&
			stage == StageDecision &&
			result.Route == RouteInspect &&
			successfulToolCalls == 0
		injectedPrefix := false
		if assistantPrefix != "" && r.toolCompleter == nil {
			request.Prompt, injectedPrefix = appendAssistantPrefix(
				r.renderer,
				request.Prompt,
				assistantPrefix,
			)
		}
		var offered []string
		if stage == StageDecision {
			offered = offeredToolNames(activeSpecs)
		}
		tracePrefix := ""
		if injectedPrefix {
			tracePrefix = assistantPrefix
		}
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(
				messages,
				activeSpecs,
				stage == StageDecision && result.Route == RouteInspect,
				requireNativeTool,
				assistantPrefix,
			)
			tracePrefix = assistantPrefix
		}
		promptTrace := r.tracePrompt(request, tracePrefix, offered)
		modelStarted := time.Now()
		generated, nativeCall, reasoningContent, err := r.generate(
			ctx,
			request,
			messages,
			activeSpecs,
			stage == StageDecision && result.Route == RouteInspect,
			requireNativeTool,
			assistantPrefix,
		)
		if err != nil {
			modelDuration := time.Since(modelStarted).Milliseconds()
			result.Steps = append(result.Steps, Step{
				Number: step, Stage: stage, Request: promptTrace,
				ModelDurationMS: modelDuration, ModelError: err.Error(),
			})
			r.observe(Event{Kind: EventModelDone, Step: step, DurationMS: modelDuration, Err: err}, observer)
			return result, err
		}
		current := Step{
			Number:          step,
			Stage:           stage,
			Request:         promptTrace,
			ModelOutput:     generated.Text,
			FinishReason:    generated.FinishReason,
			Usage:           generated.Usage,
			ModelDurationMS: time.Since(modelStarted).Milliseconds(),
		}
		result.Steps = append(result.Steps, current)
		r.observe(Event{Kind: EventModelDone, Step: step, DurationMS: current.ModelDurationMS}, observer)

		modelAction := generated.Text
		if renderer, ok := r.renderer.(interface{ reconstructOutput(string) string }); ok {
			modelAction = renderer.reconstructOutput(modelAction)
		}
		if injectedPrefix &&
			!strings.HasPrefix(strings.TrimSpace(modelAction), assistantPrefix) {
			modelAction = assistantPrefix + modelAction
		}
		action, err := r.protocol.Parse(modelAction, generated.FinishReason)
		// Some G1i-compatible servers serialize a valid function call in the
		// assistant content instead of the OpenAI tool_calls field. Preserve the
		// recovered call as a native transcript item so the following tool result
		// remains valid Chat Completions history.
		if err == nil && r.toolCompleter != nil && nativeCall == nil && action.Type == "tool" {
			nativeCall = &toolchat.ToolCall{
				ID:        fmt.Sprintf("call-content-%d", step),
				Name:      action.Name,
				Arguments: string(action.Arguments),
			}
		}
		stageActionType := action.Type
		if stage == StageAnswer && action.Type == "final" && answerContainsToolFrame(action.Content) {
			stageActionType = "tool"
		}
		if err == nil && stage == StageAnswer && stageActionType != "final" {
			err = fmt.Errorf(
				"%w: %s action is forbidden during %s",
				ErrStageViolation,
				stageActionType,
				stage,
			)
			result.Steps[len(result.Steps)-1].ActionType = stageActionType
			result.Steps[len(result.Steps)-1].StageViolation = true
		}
		if err != nil {
			result.Steps[len(result.Steps)-1].ProtocolError = err.Error()
			if retries >= r.options.ProtocolRetries {
				return result, err
			}
			retries++
			r.observe(Event{Kind: EventRetry, Step: step, Err: err}, observer)
			echoed := retryEcho(modelAction, err)
			if strings.TrimSpace(echoed) != "" {
				retryMessage := Message{
					Role:             RoleAssistant,
					Content:          echoed,
					ReasoningContent: reasoningContent,
				}
				if nativeCall != nil {
					retryMessage.ToolCalls = []toolchat.ToolCall{*nativeCall}
				}
				messages = append(messages, retryMessage)
			}
			correction := r.protocol.Correction(err)
			if errors.Is(err, ErrStageViolation) {
				correction = "Tools are unavailable in the final answer stage. Answer the original task now using existing Tool results. Do not output or request another tool call."
			}
			messages = append(messages, Message{
				Role:    RoleUser,
				Content: correction,
			})
			continue
		}
		retries = 0
		result.Steps[len(result.Steps)-1].ActionType = action.Type
		result.Steps[len(result.Steps)-1].ProtocolRepaired = action.ProtocolRepaired
		if action.Type == "final" {
			if !terminalToolCompleted {
				err = fmt.Errorf(
					"%w: successful %s call required before final answer",
					ErrProtocol,
					r.terminalTool,
				)
				result.Steps[len(result.Steps)-1].ProtocolError = err.Error()
				modelMessage := Message{Role: RoleAssistant, Content: action.Content}
				turnMessages = append(turnMessages, modelMessage)
				messages = append(
					messages,
					modelMessage,
					Message{
						Role: RoleUser,
						Content: fmt.Sprintf(
							"The task is not complete: call %s with the real final answer. Plain text is not scored.",
							r.terminalTool,
						),
					},
				)
				r.observe(Event{Kind: EventRetry, Step: step, Err: err}, observer)
				continue
			}
			if result.Route == RouteInspect && toolAttempts > 0 && !hasToolEvidence {
				return result, noWorkspaceEvidenceError()
			}
			result.OriginalOutput = action.Content
			violations := validateAnswer(action.Content)
			committedOutput := action.Content
			if len(violations) > 0 {
				result.AnswerContractRepaired = true
				result.AnswerViolations = make([]string, len(violations))
				for index, violation := range violations {
					result.AnswerViolations[index] = string(violation)
				}
				committedOutput = answerContractFallback(task)
			}
			result.Output = committedOutput
			turnMessages = append(turnMessages, Message{
				Role:    RoleAssistant,
				Content: committedOutput,
			})
			r.commit(turnMessages)
			return result, nil
		}
		if result.Route == RouteRespond {
			err = fmt.Errorf("%w: tools are unavailable on the respond route", ErrProtocol)
			result.Steps[len(result.Steps)-1].ProtocolError = err.Error()
			if routeViolations >= r.options.ProtocolRetries {
				return result, err
			}
			routeViolations++
			r.observe(Event{Kind: EventRetry, Step: step, Err: err}, observer)
			messages = append(
				messages,
				Message{Role: RoleAssistant, Content: modelAction},
				Message{
					Role: RoleUser,
					Content: "The route for this turn is respond. Answer directly using " +
						"the conversation and do not call workspace tools.",
				},
			)
			continue
		}

		toolAttempts++
		assistantPrefix = ""
		tool, ok := activeTools[action.Name]
		result.Steps[len(result.Steps)-1].Tool = action.Name
		result.Steps[len(result.Steps)-1].ToolArguments =
			append(json.RawMessage(nil), action.Arguments...)
		var value any
		toolContext := withToolEventObserver(ctx, func(event Event) {
			if event.Step == 0 {
				event.Step = step
			}
			if event.ParentStep == 0 && (event.Kind != EventToolRetry || event.SubagentIndex != 0) {
				event.ParentStep = step
			}
			if event.Kind == EventToolRetry && event.SubagentIndex == 0 {
				current := &result.Steps[len(result.Steps)-1]
				current.ToolRetries = append(current.ToolRetries, ToolRetryTrace{
					Attempt: event.Attempt, MaxAttempts: event.MaxAttempts,
					StatusCode: event.StatusCode, DelayMS: event.DelayMS,
				})
			}
			r.observe(event, observer)
		})
		toolStarted := time.Now()
		duplicate := false
		replayed := false
		recoveryBlocked := false
		executed := false
		callKey := canonicalToolCall(action)
		if callKey == lastSameCallKey {
			sameCallStreak++
		} else {
			lastSameCallKey = callKey
			sameCallStreak = 1
		}
		if preservesToolOrder(r.protocol) {
			if callKey == lastNativeCallKey {
				nativeRepeatStreak++
			} else {
				lastNativeCallKey = callKey
				nativeRepeatStreak = 0
			}
		}
		rescueRestricted := rescueMode && (r.terminalTool == "" || action.Name != r.terminalTool)
		if _, unavailable := unavailableTools[action.Name]; unavailable {
			result.Steps[len(result.Steps)-1].ToolRejected = rejectedProviderUnavailable
			result.Steps[len(result.Steps)-1].ToolUnavailable = true
			err = fmt.Errorf("%w: %s", ErrProviderUnavailable, action.Name)
		} else if rescueRestricted {
			result.Steps[len(result.Steps)-1].ToolRejected = rejectedRescueRestricted
			if r.terminalTool == "" {
				err = errors.New("tools are unavailable after repeated identical calls; answer directly")
			} else {
				err = fmt.Errorf(
					"only %s is available after repeated identical calls",
					r.terminalTool,
				)
			}
		} else if revision, exists := seenSuccessfulToolCalls[callKey]; exists &&
			revision == workspaceRevision && !allowsRepeatedToolCalls(r.protocol) {
			// A repeated successful call to a pure read can be re-executed
			// within the replay budget instead of rejected: re-running returns
			// the same result and keeps the transcript moving, which matters
			// under near-greedy decoding where a rejection otherwise drives
			// the model into emitting the identical call until the step
			// budget is exhausted.
			if ok && tool.Spec().Replayable &&
				r.options.DuplicateReplayLimit > 0 &&
				sameCallStreak <= r.options.DuplicateReplayLimit {
				replayed = true
				executed = true
				r.observe(Event{Kind: EventToolStart, Step: step, Tool: action.Name, Arguments: action.Arguments}, observer)
				value, err = tool.Execute(toolContext, action.Arguments)
			} else {
				duplicate = true
				result.Steps[len(result.Steps)-1].ToolRejected = rejectedDuplicateCall
				err = fmt.Errorf("duplicate tool call rejected")
			}
		} else if epoch, exists := failedToolCallEpochs[callKey]; exists &&
			epoch == successfulToolCalls && !allowsRepeatedToolCalls(r.protocol) {
			duplicate = true
			result.Steps[len(result.Steps)-1].ToolRejected = rejectedDuplicateCall
			err = fmt.Errorf("duplicate tool call rejected")
		} else {
			switch {
			case !ok:
				result.Steps[len(result.Steps)-1].ToolRejected = rejectedUnknownTool
				if hidden, exists := r.tools[action.Name]; exists && hidden.Spec().Bundle != "" {
					err = fmt.Errorf(
						"tool %q is not active; call load_tools with {\"bundle\":%q}, then retry %q",
						action.Name,
						hidden.Spec().Bundle,
						action.Name,
					)
				} else {
					err = fmt.Errorf("unknown tool %q", action.Name)
				}
			case !allowsRepeatedToolCalls(r.protocol) && action.Name == consecutiveFailedTool &&
				consecutiveToolFailures >= maxConsecutiveToolFailures:
				recoveryBlocked = true
				result.Steps[len(result.Steps)-1].ToolRejected = rejectedFailureLimit
				err = fmt.Errorf(
					"tool %q blocked after %d consecutive failures; choose a different tool or answer",
					action.Name,
					consecutiveToolFailures,
				)
			default:
				executed = true
				r.observe(Event{Kind: EventToolStart, Step: step, Tool: action.Name, Arguments: action.Arguments}, observer)
				value, err = tool.Execute(toolContext, action.Arguments)
			}
		}
		result.Steps[len(result.Steps)-1].ToolExecuted = executed
		if executed {
			result.Steps[len(result.Steps)-1].ToolDurationMS = time.Since(toolStarted).Milliseconds()
		}
		if executed {
			// An argument error is rejected before the tool reaches the
			// workspace, so it observed nothing and must not satisfy the
			// evidence gate. Every other executed outcome did reach the
			// workspace: a missing path or a runtime failure is a real
			// observation the model may report.
			toolEvidence := !errors.Is(err, ErrInvalidToolArguments) && !tool.Spec().Control
			result.Steps[len(result.Steps)-1].ToolEvidence = toolEvidence
			if toolEvidence {
				hasToolEvidence = true
			}
			if errors.Is(err, ErrProviderUnavailable) {
				failedToolCallEpochs[callKey] = successfulToolCalls
				unavailableTools[action.Name] = struct{}{}
				result.Steps[len(result.Steps)-1].ToolRejected = rejectedProviderUnavailable
				result.Steps[len(result.Steps)-1].ToolUnavailable = true
				unverified = appendUnique(unverified, action.Name)
				forceAnswer = true
			} else if errors.Is(err, ErrInvalidToolArguments) {
				failedToolCallEpochs[callKey] = successfulToolCalls
				// Schema repair attempts have not observed workspace state and
				// must not consume the runtime failure budget. A corrected call
				// to the same tool still needs a chance to execute.
			} else if err == nil {
				seenSuccessfulToolCalls[callKey] = workspaceRevision
				delete(failedToolCallEpochs, callKey)
				if tool.Spec().MutatesWorkspace && workspaceChanged(value) {
					workspaceRevision++
				}
				consecutiveFailedTool = ""
				consecutiveToolFailures = 0
			} else if action.Name == consecutiveFailedTool {
				failedToolCallEpochs[callKey] = successfulToolCalls
				consecutiveToolFailures++
			} else {
				failedToolCallEpochs[callKey] = successfulToolCalls
				consecutiveFailedTool = action.Name
				consecutiveToolFailures = 1
			}
		}
		if !executed && err != nil && !duplicate {
			failedToolCallEpochs[callKey] = successfulToolCalls
		}
		// Consecutive successful calls to one tool with no other tool or
		// failure in between. Unique argument sets escape the duplicate-key
		// streak, so a separate counter catches spirals that grind one tool
		// with fresh arguments on every step.
		if executed && err == nil {
			if action.Name == lastSameToolName {
				sameToolSuccessStreak++
			} else {
				lastSameToolName = action.Name
				sameToolSuccessStreak = 1
			}
		} else {
			sameToolSuccessStreak = 0
		}
		payload := toolResult{OK: err == nil, Tool: action.Name, Result: value}
		if err != nil {
			payload.Error = err.Error()
			result.Steps[len(result.Steps)-1].ToolError = err.Error()
		}
		if carrier, ok := value.(SubagentTraceCarrier); ok {
			result.Steps[len(result.Steps)-1].Subagents = cloneSubagentTraces(carrier.SubagentTraces())
		}
		encoded, marshalErr := json.Marshal(payload)
		if marshalErr != nil {
			return result, fmt.Errorf("encode tool result: %w", marshalErr)
		}
		result.Steps[len(result.Steps)-1].ToolResult =
			append(json.RawMessage(nil), encoded...)
		r.observe(Event{Kind: EventToolDone, Step: step, Tool: action.Name, Arguments: action.Arguments, Err: err}, observer)
		callID := fmt.Sprintf("call-%d", step)
		if nativeCall != nil {
			callID = nativeCall.ID
		}
		toolContent := r.protocol.FormatToolResult(
			action.Name,
			callID,
			string(encoded),
		)
		if preservesToolOrder(r.protocol) {
			switch {
			case replayed:
				toolContent += "\nNOTE: " + duplicateReplayNote(sameCallStreak, r.options.MaxSteps-step, r.terminalTool)
			case duplicate:
				toolContent += "\nRECOVERY: " + duplicateRejectionNote(sameCallStreak, r.options.MaxSteps-step, r.terminalTool)
			case err != nil:
				toolContent += "\nRECOVERY: " + toolFailureReminder(action.Name, err, recoveryBlocked, activeTools)
			}
		}
		if allowsRepeatedToolCalls(r.protocol) && nativeRepeatStreak >= 1 && action.Name != r.terminalTool {
			toolContent += "\nNOTE: identical tool call repeated. Do not call it again. Take the next step (other file, compute, run_tests, or submit)."
			if nativeRepeatStreak >= 2 {
				toolContent += "\nNOTE2: stop repeating. If you already have the answer, call submit now."
			}
		}
		// A hook after the terminal tool is pointless: the turn ends there and
		// nothing will ever read the reminder, so it would only pollute the
		// committed transcript.
		if err == nil && !replayed && action.Name != r.terminalTool && r.options.PostToolHook != nil {
			if hook := strings.TrimSpace(r.options.PostToolHook(action.Name, action.Arguments, value, nil)); hook != "" {
				toolContent += "\n" + hook
			}
		}
		toolContent = compactToolResult(task, toolContent)
		recordedAction := r.protocol.RecordAction(action, generated.Text)
		var recordedToolCalls []toolchat.ToolCall
		if nativeCall != nil {
			recordedToolCalls = []toolchat.ToolCall{*nativeCall}
		}
		turnMessages = append(
			turnMessages,
			Message{
				Role:             RoleAssistant,
				Content:          recordedAction,
				ReasoningContent: reasoningContent,
				ToolCalls:        recordedToolCalls,
			},
			Message{
				Role:       RoleTool,
				Name:       action.Name,
				ToolCallID: callID,
				Content:    toolContent,
			},
		)
		messages = append(
			messages,
			Message{
				Role:             RoleAssistant,
				Content:          recordedAction,
				ReasoningContent: reasoningContent,
				ToolCalls:        recordedToolCalls,
			},
			Message{
				Role:       RoleTool,
				Name:       action.Name,
				ToolCallID: callID,
				Content:    toolContent,
			},
		)
		if err == nil && rescueMode && action.Name == r.terminalTool {
			result.RescueSubmitted = true
		}
		if err == nil && action.Name == r.terminalTool && r.options.EndOnTerminalTool {
			output := terminalToolOutput(action, value)
			result.OriginalOutput = output
			result.Output = output
			r.commit(turnMessages)
			return result, nil
		}
		if err == nil {
			successfulToolCalls++
			if tool.Spec().Control {
				selection, selectionOK := value.(loadToolsResult)
				if selectionOK && !containsString(result.Bundles, selection.Bundle) {
					result.Bundles = append(result.Bundles, selection.Bundle)
					activeSpecs = toolSpecsForBundles(r.toolSpecs, result.Bundles)
					activeTools = toolsForSpecs(r.tools, activeSpecs)
					messages = replaceSystemControl(messages, r.controlForSpecs(activeSpecs))
				}
			}
			if action.Name == r.terminalTool {
				terminalToolCompleted = true
			}
			if reminder := strings.TrimSpace(r.postToolReminder(terminalToolCompleted)); reminder != "" {
				messages = append(messages, Message{
					Role:    RoleUser,
					Content: reminder,
				})
			}
		} else if duplicate {
			if terminalToolCompleted {
				forceAnswer = true
				result.ForcedAnswerReason = forcedAnswerDuplicateCall
			}
			if !preservesToolOrder(r.protocol) {
				messages = append(messages, Message{
					Role:    RoleUser,
					Content: r.duplicateToolReminder(successfulToolCalls > 0, terminalToolCompleted),
				})
			}
		} else {
			if !preservesToolOrder(r.protocol) {
				messages = append(messages, Message{
					Role:    RoleUser,
					Content: toolFailureReminder(action.Name, err, recoveryBlocked, activeTools),
				})
			}
		}
		if errors.Is(err, ErrProviderUnavailable) && !terminalToolCompleted &&
			r.terminalTool != "" && !rescueMode {
			rescueMode = true
			result.RescueAttempted = true
			result.ForcedAnswerReason = forcedAnswerProviderFailure
			messages = r.enterRescueMode(
				messages,
				fmt.Sprintf("the %s provider is unavailable", action.Name),
				r.options.MaxSteps-step,
			)
			activeSpecs = r.rescueToolSpecs()
			activeTools = toolsForSpecs(r.tools, activeSpecs)
		}
		loopStuck := r.options.DuplicateRescueThreshold > 0 &&
			sameCallStreak >= r.options.DuplicateRescueThreshold &&
			(duplicate || replayed || (err != nil && !executed))
		spiralStuck := r.options.SameToolRescueLimit > 0 &&
			sameToolSuccessStreak >= r.options.SameToolRescueLimit
		if !rescueMode && preservesToolOrder(r.protocol) && !allowsRepeatedToolCalls(r.protocol) &&
			(loopStuck || spiralStuck) {
			rescueMode = true
			result.RescueAttempted = true
			reason := fmt.Sprintf("the same call was repeated %d times", sameCallStreak)
			if spiralStuck {
				reason = fmt.Sprintf(
					"the same tool ran successfully %d times in a row with no other tool",
					sameToolSuccessStreak,
				)
			}
			messages = r.enterRescueMode(messages, reason, r.options.MaxSteps-step)
			activeSpecs = r.rescueToolSpecs()
			activeTools = toolsForSpecs(r.tools, activeSpecs)
		}
		if result.Route == RouteInspect && !terminalToolCompleted {
			assistantPrefix = r.protocol.ToolCallPrefix()
		}
	}
	return result, ErrMaxSteps
}

func (r *Runner) controlForSpecs(specs []ToolSpec) string {
	control := toolControlPrompt(r.protocol, specs, r.thinkingMode, r.toolCompleter != nil)
	if taskControl := strings.TrimSpace(r.options.TaskControl); taskControl != "" {
		control += "\n\nTask-specific contract:\n" + taskControl
	}
	return control
}

func replaceSystemControl(messages []Message, control string) []Message {
	result := append([]Message(nil), messages...)
	for index := range result {
		if result[index].Role == RoleSystem {
			result[index] = Message{Role: RoleSystem, Content: control}
			return result
		}
	}
	return append([]Message{{Role: RoleSystem, Content: control}}, result...)
}

func containsString(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

// terminalActionPhrase words the turn-ending suggestion in duplicate/rescue
// notes: through the terminal tool when one is offered, or with a direct
// answer otherwise (Markdown protocol has no submit gate).
func terminalActionPhrase(terminalTool, variant string) string {
	submit := terminalTool != ""
	switch variant {
	case "if_answer":
		if submit {
			return "submit if you have the answer"
		}
		return "answer directly if you have the answer"
	case "best_now":
		if submit {
			return "submit your best answer now"
		}
		return "answer directly now with your best answer"
	case "if_complete":
		if submit {
			return "submit if the task is complete"
		}
		return "answer directly if the task is complete"
	case "call_best":
		if submit {
			return "call submit with your best answer now"
		}
		return "answer directly now with your best answer"
	}
	return "answer directly"
}

// duplicateReplayNote accompanies a re-executed identical call to a Replayable
// tool. The first repeat keeps the gentle framing; further repeats escalate
// because the transcript has proven that the model is stuck in a loop.
func duplicateReplayNote(streak, stepsLeft int, terminalTool string) string {
	if streak <= 2 {
		return fmt.Sprintf(
			"identical tool call re-executed: this exact call has now run %d times in a row. The result is unchanged; do not call it again. Take the next step: different arguments, another tool, the next row, or %s.",
			streak,
			terminalActionPhrase(terminalTool, "if_answer"),
		)
	}
	return fmt.Sprintf(
		"STOP. This identical call has now run %d times in a row and the result will not change. You have %d steps left. Change the arguments, choose a different tool, or %s.",
		streak,
		stepsLeft,
		terminalActionPhrase(terminalTool, "best_now"),
	)
}

// duplicateRejectionNote replaces the fixed rejection text with an escalating
// one. The first rejection keeps the exact legacy wording so one-off repeats
// behave byte-for-byte like previous releases; further rejections add the
// streak count and the remaining budget.
func duplicateRejectionNote(streak, stepsLeft int, terminalTool string) string {
	if streak < 3 {
		return "This exact call is disabled. Do not repeat it. Use the existing result, change the arguments, choose a different tool, or " + terminalActionPhrase(terminalTool, "if_complete") + "."
	}
	return fmt.Sprintf(
		"STOP repeating. This identical call has now occurred %d times in a row and it will not be accepted again. You have %d steps left. Change the arguments, choose a different tool, or %s.",
		streak,
		stepsLeft,
		terminalActionPhrase(terminalTool, "call_best"),
	)
}

// enterRescueMode rebuilds the tool catalog so only the terminal tool remains
// and injects one explicit rescue instruction as a User turn. A User turn is
// more salient to the model than text appended after a Function output.
func (r *Runner) enterRescueMode(messages []Message, reason string, stepsLeft int) []Message {
	specs := r.rescueToolSpecs()
	control := toolControlPrompt(r.protocol, specs, r.thinkingMode, r.toolCompleter != nil)
	for index := range messages {
		if messages[index].Role == RoleSystem {
			messages[index] = Message{Role: RoleSystem, Content: control}
		}
	}
	return append(messages, Message{
		Role:    RoleUser,
		Content: rescueInstruction(r.terminalTool, reason, stepsLeft),
	})
}

func (r *Runner) rescueToolSpecs() []ToolSpec {
	if r.terminalTool == "" {
		return nil
	}
	for _, spec := range r.toolSpecs {
		if spec.Name == r.terminalTool {
			return []ToolSpec{spec}
		}
	}
	return nil
}

func rescueInstruction(terminalTool, reason string, stepsLeft int) string {
	if terminalTool == "" {
		return fmt.Sprintf(
			"The tools have been disabled because %s. You have %d steps left. Answer directly now with your best answer from the results you already have.",
			reason,
			stepsLeft,
		)
	}
	return fmt.Sprintf(
		"The other tools have been disabled because %s. You have %d steps left. Call %s now with your best answer in this exact shape: {\"name\":\"%s\",\"arguments\":{\"answer\":\"...\"}}",
		reason,
		stepsLeft,
		terminalTool,
		terminalTool,
	)
}

func workspaceChanged(value any) bool {
	result, ok := value.(WorkspaceMutationResult)
	return !ok || result.WorkspaceChanged()
}

func answerContainsToolFrame(content string) bool {
	lower := strings.ToLower(strings.TrimSpace(content))
	return strings.Contains(lower, "<tool_call") || looksLikeBareToolCall(content)
}

func terminalToolOutput(action Action, value any) string {
	var arguments struct {
		Answer string `json:"answer"`
	}
	if json.Unmarshal(action.Arguments, &arguments) == nil && strings.TrimSpace(arguments.Answer) != "" {
		return strings.TrimSpace(arguments.Answer)
	}
	if text, ok := value.(string); ok {
		return strings.TrimSpace(text)
	}
	encoded, err := json.Marshal(value)
	if err != nil {
		return ""
	}
	return string(encoded)
}

func (r *Runner) postToolReminder(terminalToolCompleted bool) string {
	if preservesToolOrder(r.protocol) {
		return r.protocol.PostToolReminder()
	}
	if !terminalToolCompleted {
		return fmt.Sprintf(
			"Use the Tool results above to continue the current task. Call another tool only for a specific missing fact. When the answer is ready, call %s with the real answer; do not answer in plain text. Never repeat a successful tool call.",
			r.terminalTool,
		)
	}
	return r.protocol.PostToolReminder()
}

func (r *Runner) duplicateToolReminder(hasEvidence, terminalToolCompleted bool) string {
	if !terminalToolCompleted {
		return fmt.Sprintf(
			"That tool call was rejected because the exact call already succeeded or failed without any intervening recovery. Do not call it again. If its earlier successful result answers the task, call %s now with that exact result; otherwise choose a different tool for one specific missing fact. Do not answer in plain text.",
			r.terminalTool,
		)
	}
	return duplicateToolReminder(hasEvidence)
}

func validateAnswer(output string) []answerViolation {
	trimmed := strings.TrimSpace(output)
	lower := strings.ToLower(trimmed)
	violations := make([]answerViolation, 0, 4)

	for _, tag := range []string{
		"<tool_call", "</tool_call", "<tool_result", "</tool_result",
		"<answer", "</answer", "<think", "</think",
	} {
		if strings.Contains(lower, tag) {
			violations = append(violations, violationProtocolTag)
			break
		}
	}

	for _, line := range strings.Split(trimmed, "\n") {
		line = strings.TrimSpace(strings.ToLower(line))
		for _, role := range []string{"assistant", "user", "system", "tool"} {
			if strings.HasPrefix(line, role+":") || strings.HasPrefix(line, role+"：") {
				violations = append(violations, violationRoleHeader)
				line = ""
				break
			}
		}
		if line == "" && len(violations) > 0 && violations[len(violations)-1] == violationRoleHeader {
			break
		}
	}

	var payload any
	if json.Unmarshal([]byte(trimmed), &payload) == nil {
		switch payload.(type) {
		case map[string]any, []any:
			violations = append(violations, violationJSONPayload)
		}
	}

	if strings.Contains(lower, `"ok"`) &&
		strings.Contains(lower, `"tool"`) &&
		(strings.Contains(lower, `"result"`) || strings.Contains(lower, `"error"`)) {
		violations = append(violations, violationToolEcho)
	}
	return violations
}

func answerContractFallback(task string) string {
	for _, value := range task {
		if unicode.Is(unicode.Han, value) {
			return answerContractFallbackZH
		}
	}
	return answerContractFallbackEN
}

func appendUnique(values []string, value string) []string {
	for _, existing := range values {
		if existing == value {
			return values
		}
	}
	return append(values, value)
}

func providerUnavailableReminder(name string) string {
	return fmt.Sprintf(
		"The provider for %s is unavailable. Do not call %s again in this turn. Continue only with verified Tool results and explicitly state that the %s fact could not be verified.",
		name,
		name,
		name,
	)
}

func duplicateToolReminder(hasEvidence bool) string {
	if hasEvidence {
		return duplicateToolAnswerReminder
	}
	return `That tool call was rejected because it repeats an earlier failed call.
Tools are now unavailable. Answer from the Tool results, and clearly state anything that could not be verified.`
}

func toolFailureReminder(
	name string,
	err error,
	recoveryBlocked bool,
	tools map[string]Tool,
) string {
	var prompt strings.Builder
	if errors.Is(err, ErrProviderUnavailable) {
		return providerUnavailableReminder(name)
	}
	if errors.Is(err, ErrInvalidToolArguments) {
		fmt.Fprintf(&prompt, "The %s arguments were rejected: %v. ", name, err)
		if tool, ok := tools[name]; ok {
			fmt.Fprintf(
				&prompt,
				"Retry %s using only the fields in this exact argument shape: %s. ",
				name,
				tool.Spec().Arguments,
			)
			if example := strings.TrimSpace(tool.Spec().Example); example != "" {
				fmt.Fprintf(
					&prompt,
					"A valid call uses literal values, never type descriptions: {\"name\":\"%s\",\"arguments\":%s}. ",
					name,
					example,
				)
			}
		}
		prompt.WriteString("Do not add optional limit, byte, offset, or pagination fields unless the schema lists them.")
		return prompt.String()
	}
	fmt.Fprintf(&prompt, "The tool call failed: %v. ", err)
	if recoveryBlocked {
		prompt.WriteString("Do not call the same tool again in this turn. ")
	} else {
		prompt.WriteString("Do not repeat the same call. ")
	}
	switch name {
	case "read_file":
		if _, hasList := tools["list_files"]; hasList {
			if _, hasSearch := tools["search_text"]; hasSearch {
				prompt.WriteString(
					"If the path is uncertain, use list_files or search_text before another read_file call. ",
				)
			}
		}
	case "list_files":
		if _, hasSearch := tools["search_text"]; hasSearch {
			prompt.WriteString(
				"Try an existing parent directory or workspace root, or use search_text for a known literal. ",
			)
		}
	}
	prompt.WriteString("Choose a different useful tool or answer with the limitation. Do not guess.")
	return prompt.String()
}

// tracePrompt captures a generation request. The prompt is recorded verbatim up
// to the configured budget so a greedy output change can be attributed to the
// exact input that produced it.
func (r *Runner) tracePrompt(
	request continuation.Request,
	assistantPrefix string,
	toolsOffered []string,
) *PromptTrace {
	budget := r.options.TracePromptBytes
	if budget == 0 {
		return nil
	}
	prompt := request.Prompt
	trace := &PromptTrace{
		Bytes:           len(prompt),
		AssistantPrefix: assistantPrefix,
		MaxOutputTokens: request.MaxOutputTokens,
		ToolsOffered:    toolsOffered,
	}
	if len(request.Stops) > 0 {
		trace.Stops = append([]string{}, request.Stops...)
	}
	if budget > 0 && len(prompt) > budget {
		// Keep the head and tail: the head carries the control prompt and tool
		// list, the tail carries the most recent observation and the prefix.
		head := budget / 2
		tail := budget - head
		prompt = prompt[:head] + "\n...[trace truncated]...\n" + prompt[len(prompt)-tail:]
		trace.Truncated = true
	}
	trace.Prompt = prompt
	return trace
}

// offeredToolNames lists the tools present in this run's registry. A change to
// the tool list changes every decision prompt, which under greedy decoding can
// move unrelated cases; recording it makes that attributable.
func offeredToolNames(specs []ToolSpec) []string {
	if len(specs) == 0 {
		return nil
	}
	names := make([]string, 0, len(specs))
	for _, spec := range specs {
		names = append(names, spec.Name)
	}
	sort.Strings(names)
	return names
}

func noWorkspaceEvidenceError() error {
	return fmt.Errorf(
		"%w: every tool call failed argument validation or was rejected; the turn was not committed",
		ErrNoWorkspaceEvidence,
	)
}

func (r *Runner) decideRoute(
	ctx context.Context,
	history []Message,
	task string,
	observer func(Event),
) (Route, []RouteStep, error) {
	r.observe(Event{Kind: EventRouteStart}, observer)
	messages := []Message{{Role: RoleSystem, Content: r.router.Instructions()}}
	messages = append(messages, routingHistory(history)...)
	messages = append(messages, Message{Role: RoleUser, Content: task})

	var steps []RouteStep
	for attempt := 0; attempt <= r.options.RouteRetries; attempt++ {
		rendered, err := r.routeRenderer.Render(messages)
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return "", steps, err
		}
		request := r.options.Generation
		request.Prompt, err = appendRequiredAssistantPrefix(r.routeRenderer, rendered, "<route>")
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return "", steps, err
		}
		request.Stops = r.router.Stops()
		request.MaxOutputTokens = r.options.RouteMaxOutputTokens
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(messages, nil, false, false, "<route>")
		}
		promptTrace := r.tracePrompt(request, "<route>", nil)
		started := time.Now()
		generated, _, _, err := r.generate(ctx, request, messages, nil, false, false, "<route>")
		if err != nil {
			steps = append(steps, RouteStep{
				Attempt:    attempt + 1,
				Request:    promptTrace,
				DurationMS: time.Since(started).Milliseconds(),
			})
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return "", steps, err
		}
		candidate := strings.TrimSpace(generated.Text)
		if !strings.HasPrefix(candidate, "<route>") {
			candidate = "<route>" + candidate
		}
		route, parseErr := r.router.Parse(candidate, generated.FinishReason)
		current := RouteStep{
			Attempt:     attempt + 1,
			Request:     promptTrace,
			ModelOutput: generated.Text,
			DurationMS:  time.Since(started).Milliseconds(),
		}
		if parseErr == nil {
			current.Route = route
			steps = append(steps, current)
			r.observe(Event{Kind: EventRouteDone, Route: route}, observer)
			return route, steps, nil
		}
		current.ProtocolError = parseErr.Error()
		if attempt == r.options.RouteRetries {
			current.Route = RouteRespond
			current.FailedClosed = true
			steps = append(steps, current)
			r.observe(Event{
				Kind:  EventRouteDone,
				Route: RouteRespond,
				Err:   parseErr,
			}, observer)
			return RouteRespond, steps, nil
		}
		steps = append(steps, current)
		if echoed := retryEcho(candidate, parseErr); echoed != "" {
			messages = append(messages, Message{Role: RoleAssistant, Content: echoed})
		}
		messages = append(
			messages,
			Message{Role: RoleUser, Content: r.router.Correction(parseErr)},
		)
	}
	return RouteRespond, steps, nil
}

func (r *Runner) decideToolRoute(
	ctx context.Context,
	history []Message,
	task string,
	observer func(Event),
) (ToolRouteDecision, []RouteStep, error) {
	r.observe(Event{Kind: EventRouteStart}, observer)
	messages := []Message{{Role: RoleSystem, Content: r.toolRouter.Instructions(r.toolBundles)}}
	messages = append(messages, routingHistory(history)...)
	messages = append(messages, Message{Role: RoleUser, Content: task})

	var steps []RouteStep
	for attempt := 0; attempt <= r.options.RouteRetries; attempt++ {
		rendered, err := r.routeRenderer.Render(messages)
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return ToolRouteDecision{}, steps, err
		}
		request := r.options.Generation
		request.Prompt, err = appendRequiredAssistantPrefix(r.routeRenderer, rendered, "<route>")
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return ToolRouteDecision{}, steps, err
		}
		request.Stops = r.toolRouter.Stops()
		request.MaxOutputTokens = r.options.RouteMaxOutputTokens
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(messages, nil, false, false, "<route>")
		}
		promptTrace := r.tracePrompt(request, "<route>", nil)
		started := time.Now()
		generated, _, _, err := r.generate(ctx, request, messages, nil, false, false, "<route>")
		if err != nil {
			steps = append(steps, RouteStep{
				Attempt:    attempt + 1,
				Request:    promptTrace,
				DurationMS: time.Since(started).Milliseconds(),
			})
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return ToolRouteDecision{}, steps, err
		}
		candidate := strings.TrimSpace(generated.Text)
		if !strings.HasPrefix(candidate, "<route>") {
			candidate = "<route>" + candidate
		}
		decision, parseErr := r.toolRouter.Parse(candidate, generated.FinishReason, r.toolBundles)
		current := RouteStep{
			Attempt:     attempt + 1,
			Request:     promptTrace,
			ModelOutput: generated.Text,
			DurationMS:  time.Since(started).Milliseconds(),
		}
		if parseErr == nil {
			current.Route = decision.Route
			current.Bundles = append([]string(nil), decision.Bundles...)
			steps = append(steps, current)
			r.observe(Event{Kind: EventRouteDone, Route: decision.Route, Bundles: decision.Bundles}, observer)
			return decision, steps, nil
		}
		current.ProtocolError = parseErr.Error()
		if attempt == r.options.RouteRetries {
			current.Route = RouteRespond
			current.FailedClosed = true
			steps = append(steps, current)
			r.observe(Event{Kind: EventRouteDone, Route: RouteRespond, Err: parseErr}, observer)
			return ToolRouteDecision{Route: RouteRespond}, steps, nil
		}
		steps = append(steps, current)
		if echoed := retryEcho(candidate, parseErr); echoed != "" {
			messages = append(messages, Message{Role: RoleAssistant, Content: echoed})
		}
		messages = append(messages, Message{
			Role:    RoleUser,
			Content: r.toolRouter.Correction(parseErr, r.toolBundles),
		})
	}
	return ToolRouteDecision{Route: RouteRespond}, steps, nil
}

// History returns a copy of the committed multi-turn transcript. The control
// prompt is intentionally excluded.
func (r *Runner) History() []Message {
	r.stateMu.RLock()
	defer r.stateMu.RUnlock()
	return cloneMessages(r.history)
}

// Reset clears committed conversation history. It does not change the tool
// registry or generation configuration.
func (r *Runner) Reset() {
	r.runMu.Lock()
	defer r.runMu.Unlock()
	r.stateMu.Lock()
	r.history = nil
	r.stateMu.Unlock()
}

// RestoreHistory replaces the committed transcript after validating that it
// contains only conversation roles. It is intended for application-level
// persistence; the control prompt and runtime tool registry are never stored.
func (r *Runner) RestoreHistory(messages []Message) error {
	for index, message := range messages {
		switch message.Role {
		case RoleUser, RoleAssistant, RoleTool:
		default:
			return fmt.Errorf("history message %d has unsupported role %q", index, message.Role)
		}
	}
	r.runMu.Lock()
	defer r.runMu.Unlock()
	r.stateMu.Lock()
	r.history = cloneMessages(messages)
	r.stateMu.Unlock()
	return nil
}

func (r *Runner) commit(messages []Message) {
	r.stateMu.Lock()
	r.history = append(r.history, cloneMessages(messages)...)
	r.stateMu.Unlock()
}

func cloneMessages(messages []Message) []Message {
	result := append([]Message(nil), messages...)
	for index := range result {
		result[index].ToolCalls = append([]toolchat.ToolCall(nil), result[index].ToolCalls...)
	}
	return result
}

func canonicalToolCall(action Action) string {
	var arguments bytes.Buffer
	if err := json.Compact(&arguments, action.Arguments); err != nil {
		arguments.Write(action.Arguments)
	}
	return action.Name + "\x00" + arguments.String()
}

func (r *Runner) observe(event Event, observer func(Event)) {
	if r.options.Observe != nil {
		r.options.Observe(event)
	}
	if observer != nil {
		observer(event)
	}
}

type toolEventObserverKey struct{}

func withToolEventObserver(ctx context.Context, observer func(Event)) context.Context {
	return context.WithValue(ctx, toolEventObserverKey{}, observer)
}

// EmitToolEvent forwards a nested tool event through the observer attached by
// Runner. Calls outside tool execution are harmless no-ops.
func EmitToolEvent(ctx context.Context, event Event) {
	observer, _ := ctx.Value(toolEventObserverKey{}).(func(Event))
	if observer != nil {
		observer(event)
	}
}

func cloneSubagentTraces(values []SubagentTrace) []SubagentTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]SubagentTrace, len(values))
	copy(result, values)
	for index := range result {
		result[index].Bundles = append([]string(nil), values[index].Bundles...)
		result[index].Sources = append([]string(nil), values[index].Sources...)
		result[index].Steps = append([]SubagentStep(nil), values[index].Steps...)
		for step := range result[index].Steps {
			result[index].Steps[step].Arguments = append(json.RawMessage(nil), values[index].Steps[step].Arguments...)
		}
	}
	return result
}

type toolResult struct {
	OK     bool   `json:"ok"`
	Tool   string `json:"tool"`
	Result any    `json:"result,omitempty"`
	Error  string `json:"error,omitempty"`
}
