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
		return prompt + "The Assistant prefix ends with <think></think and leaves its final > for you. Generate > first, then answer directly. Do not open another <think> block, output tool calls, or emit role labels."
	case inference.ThinkingFull:
		return prompt + "The Assistant prefix ends with <think and leaves its final > for you. Generate > first, think inside the current block, close it with </think>, then answer directly. Do not open another <think> block, output tool calls, or emit role labels."
	default:
		return prompt + "Do not output tool calls, role labels, or hidden reasoning."
	}
}

const postToolDecisionReminder = `Use the Tool results above to continue the current task.
If the evidence is sufficient, answer now. Call another tool only for a specific missing fact.
Never repeat a successful tool call.`

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
	rejectedUnknownTool         = "unknown_tool"
	rejectedDuplicateCall       = "duplicate_tool_call"
	rejectedFailureLimit        = "consecutive_tool_failures"
	rejectedProviderUnavailable = "provider_unavailable"
)

type ToolSpec struct {
	Name        string
	Description string
	Arguments   string
	Parameters  json.RawMessage
	Strict      bool
}

type Tool interface {
	Spec() ToolSpec
	Execute(context.Context, json.RawMessage) (any, error)
}

type Options struct {
	MaxSteps                int
	ProtocolRetries         int
	DecisionMaxOutputTokens int
	ControlPrompt           ControlPromptMode
	Protocol                ActionProtocol
	Renderer                PromptRenderer
	Generation              continuation.Request
	Observe                 func(Event)
	Router                  RouteProtocol
	RouteRenderer           PromptRenderer
	RouteRetries            int
	RouteMaxOutputTokens    int
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
	EventModelStart EventKind = "model_start"
	EventRouteStart EventKind = "route_start"
	EventRouteDone  EventKind = "route_done"
	EventRetry      EventKind = "protocol_retry"
	EventToolStart  EventKind = "tool_start"
	EventToolDone   EventKind = "tool_done"
)

type Event struct {
	Kind  EventKind
	Step  int
	Tool  string
	Route Route
	Err   error
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
	ActionType      string                    `json:"action_type,omitempty"`
	Tool            string                    `json:"tool,omitempty"`
	ToolArguments   json.RawMessage           `json:"tool_arguments,omitempty"`
	ToolResult      json.RawMessage           `json:"tool_result,omitempty"`
	ToolExecuted    bool                      `json:"tool_executed,omitempty"`
	ToolEvidence    bool                      `json:"tool_evidence,omitempty"`
	ToolUnavailable bool                      `json:"tool_unavailable,omitempty"`
	ToolRejected    string                    `json:"tool_rejected_reason,omitempty"`
	ToolError       string                    `json:"tool_error,omitempty"`
	ProtocolError   string                    `json:"protocol_error,omitempty"`
}

// RouteStep records one routing attempt, including the retry a correction
// triggers. The route prompt was previously invisible, so a route change could
// not be traced to the history or instructions that caused it.
type RouteStep struct {
	Attempt       int          `json:"attempt"`
	Request       *PromptTrace `json:"request,omitempty"`
	ModelOutput   string       `json:"model_output"`
	Route         Route        `json:"route,omitempty"`
	ProtocolError string       `json:"protocol_error,omitempty"`
	FailedClosed  bool         `json:"failed_closed,omitempty"`
}

type Result struct {
	Output                 string      `json:"output"`
	OriginalOutput         string      `json:"original_output"`
	RouteSteps             []RouteStep `json:"route_steps,omitempty"`
	AnswerContractRepaired bool        `json:"answer_contract_repaired,omitempty"`
	AnswerViolations       []string    `json:"answer_violations,omitempty"`
	Steps                  []Step      `json:"steps"`
	Route                  Route       `json:"route"`
	ForcedAnswerReason     string      `json:"forced_answer_reason,omitempty"`
	Plan                   *PlanTrace  `json:"plan,omitempty"`
	PlanRejections         int         `json:"plan_rejections,omitempty"`
	PlanFallbacks          int         `json:"plan_fallbacks,omitempty"`
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
	thinkingMode    inference.ThinkingMode
	router          RouteProtocol
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
	applyGenerationDefaults(&options.Generation)
	if options.DecisionMaxOutputTokens == 0 {
		options.DecisionMaxOutputTokens = 96
	}
	if options.DecisionMaxOutputTokens > options.Generation.MaxOutputTokens {
		options.DecisionMaxOutputTokens = options.Generation.MaxOutputTokens
	}
	if options.Router != nil {
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
	sort.Slice(specs, func(left, right int) bool {
		return specs[left].Name < specs[right].Name
	})
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
	return &Runner{
		generator:       generator,
		toolCompleter:   toolCompleter,
		tools:           registered,
		toolSpecs:       append([]ToolSpec(nil), specs...),
		options:         options,
		protocol:        options.Protocol,
		renderer:        options.Renderer,
		control:         toolControlPrompt(options.Protocol, specs, thinkingMode, toolCompleter != nil),
		responseControl: responseControl,
		thinkingMode:    thinkingMode,
		router:          options.Router,
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
	if r.router != nil {
		route, routeSteps, routeErr := r.decideRoute(ctx, history, task, observer)
		result.RouteSteps = routeSteps
		if routeErr != nil {
			return result, routeErr
		}
		result.Route = route
	}
	messages := make([]Message, 0, len(history)+2)
	control := r.control
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
	seenToolCalls := make(map[string]struct{})
	unavailableTools := make(map[string]struct{})
	var unverified []string
	successfulToolCalls := 0
	toolAttempts := 0
	hasToolEvidence := false
	consecutiveFailedTool := ""
	consecutiveToolFailures := 0
	stage := StageDecision
	assistantPrefix := ""
	forceAnswer := false
	if r.router != nil && result.Route == RouteInspect {
		assistantPrefix = r.protocol.ToolCallPrefix()
	}
	for step := 1; step <= r.options.MaxSteps; step++ {
		if result.Route == RouteInspect &&
			toolAttempts > 0 &&
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
			if renderer, ok := r.renderer.(interface {
				appendAssistantPrefix(string, string) (string, bool)
			}); ok {
				request.Prompt, injectedPrefix = renderer.appendAssistantPrefix(
					request.Prompt,
					assistantPrefix,
				)
			} else {
				request.Prompt += " " + assistantPrefix
				injectedPrefix = true
			}
		}
		var offered []string
		if stage == StageDecision {
			offered = r.offeredToolNames()
		}
		tracePrefix := ""
		if injectedPrefix {
			tracePrefix = assistantPrefix
		}
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(
				messages,
				stage == StageDecision && result.Route == RouteInspect,
				requireNativeTool,
				assistantPrefix,
			)
			tracePrefix = assistantPrefix
		}
		promptTrace := r.tracePrompt(request, tracePrefix, offered)
		generated, nativeCall, reasoningContent, err := r.generate(
			ctx,
			request,
			messages,
			stage == StageDecision && result.Route == RouteInspect,
			requireNativeTool,
			assistantPrefix,
		)
		if err != nil {
			return result, err
		}
		current := Step{
			Number:       step,
			Stage:        stage,
			Request:      promptTrace,
			ModelOutput:  generated.Text,
			FinishReason: generated.FinishReason,
			Usage:        generated.Usage,
		}
		result.Steps = append(result.Steps, current)

		modelAction := generated.Text
		if renderer, ok := r.renderer.(interface{ reconstructOutput(string) string }); ok {
			modelAction = renderer.reconstructOutput(modelAction)
		}
		if injectedPrefix &&
			!strings.HasPrefix(strings.TrimSpace(modelAction), assistantPrefix) {
			modelAction = assistantPrefix + modelAction
		}
		action, err := r.protocol.Parse(modelAction, generated.FinishReason)
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
			messages = append(messages, Message{
				Role:    RoleUser,
				Content: r.protocol.Correction(err),
			})
			continue
		}
		retries = 0
		result.Steps[len(result.Steps)-1].ActionType = action.Type
		if action.Type == "final" {
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
		tool, ok := r.tools[action.Name]
		result.Steps[len(result.Steps)-1].Tool = action.Name
		result.Steps[len(result.Steps)-1].ToolArguments =
			append(json.RawMessage(nil), action.Arguments...)
		var value any
		duplicate := false
		recoveryBlocked := false
		executed := false
		callKey := canonicalToolCall(action)
		if _, unavailable := unavailableTools[action.Name]; unavailable {
			result.Steps[len(result.Steps)-1].ToolRejected = rejectedProviderUnavailable
			result.Steps[len(result.Steps)-1].ToolUnavailable = true
			err = fmt.Errorf("%w: %s", ErrProviderUnavailable, action.Name)
		} else if _, exists := seenToolCalls[callKey]; exists {
			duplicate = true
			result.Steps[len(result.Steps)-1].ToolRejected = rejectedDuplicateCall
			err = fmt.Errorf("duplicate tool call rejected")
		} else {
			seenToolCalls[callKey] = struct{}{}
			switch {
			case !ok:
				result.Steps[len(result.Steps)-1].ToolRejected = rejectedUnknownTool
				err = fmt.Errorf("unknown tool %q", action.Name)
			case action.Name == consecutiveFailedTool &&
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
				r.observe(Event{Kind: EventToolStart, Step: step, Tool: action.Name}, observer)
				value, err = tool.Execute(ctx, action.Arguments)
			}
		}
		result.Steps[len(result.Steps)-1].ToolExecuted = executed
		if executed {
			// An argument error is rejected before the tool reaches the
			// workspace, so it observed nothing and must not satisfy the
			// evidence gate. Every other executed outcome did reach the
			// workspace: a missing path or a runtime failure is a real
			// observation the model may report.
			toolEvidence := !errors.Is(err, ErrInvalidToolArguments)
			result.Steps[len(result.Steps)-1].ToolEvidence = toolEvidence
			if toolEvidence {
				hasToolEvidence = true
			}
			if errors.Is(err, ErrProviderUnavailable) {
				unavailableTools[action.Name] = struct{}{}
				result.Steps[len(result.Steps)-1].ToolRejected = rejectedProviderUnavailable
				result.Steps[len(result.Steps)-1].ToolUnavailable = true
				unverified = appendUnique(unverified, action.Name)
				forceAnswer = true
			} else if errors.Is(err, ErrInvalidToolArguments) {
				// Schema repair attempts have not observed workspace state and
				// must not consume the runtime failure budget. A corrected call
				// to the same tool still needs a chance to execute.
			} else if err == nil {
				consecutiveFailedTool = ""
				consecutiveToolFailures = 0
			} else if action.Name == consecutiveFailedTool {
				consecutiveToolFailures++
			} else {
				consecutiveFailedTool = action.Name
				consecutiveToolFailures = 1
			}
		}
		payload := toolResult{OK: err == nil, Tool: action.Name, Result: value}
		if err != nil {
			payload.Error = err.Error()
			result.Steps[len(result.Steps)-1].ToolError = err.Error()
		}
		encoded, marshalErr := json.Marshal(payload)
		if marshalErr != nil {
			return result, fmt.Errorf("encode tool result: %w", marshalErr)
		}
		result.Steps[len(result.Steps)-1].ToolResult =
			append(json.RawMessage(nil), encoded...)
		r.observe(Event{Kind: EventToolDone, Step: step, Tool: action.Name, Err: err}, observer)
		callID := fmt.Sprintf("call-%d", step)
		if nativeCall != nil {
			callID = nativeCall.ID
		}
		toolContent := r.protocol.FormatToolResult(
			action.Name,
			callID,
			string(encoded),
		)
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
		if err == nil {
			successfulToolCalls++
			messages = append(messages, Message{
				Role:    RoleUser,
				Content: r.protocol.PostToolReminder(),
			})
		} else if duplicate {
			forceAnswer = true
			result.ForcedAnswerReason = forcedAnswerDuplicateCall
			messages = append(messages, Message{
				Role:    RoleUser,
				Content: duplicateToolReminder(successfulToolCalls > 0),
			})
		} else {
			messages = append(messages, Message{
				Role:    RoleUser,
				Content: toolFailureReminder(action.Name, err, recoveryBlocked, r.tools),
			})
		}
	}
	return result, ErrMaxSteps
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
func (r *Runner) offeredToolNames() []string {
	if len(r.tools) == 0 {
		return nil
	}
	names := make([]string, 0, len(r.tools))
	for name := range r.tools {
		names = append(names, name)
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
		request.Prompt = rendered + " <route>"
		request.Stops = r.router.Stops()
		request.MaxOutputTokens = r.options.RouteMaxOutputTokens
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(messages, false, false, "<route>")
		}
		promptTrace := r.tracePrompt(request, "<route>", nil)
		generated, _, _, err := r.generate(ctx, request, messages, false, false, "<route>")
		if err != nil {
			steps = append(steps, RouteStep{
				Attempt: attempt + 1,
				Request: promptTrace,
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

type toolResult struct {
	OK     bool   `json:"ok"`
	Tool   string `json:"tool"`
	Result any    `json:"result,omitempty"`
	Error  string `json:"error,omitempty"`
}
