package bfcl

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// MultiTurnRenderProtocolV2 drops the stale initial_config block and supports a
// prefill anchor. The retired v1 re-rendered initial_config into every step even
// after tool calls had changed the simulator state, so the block contradicted
// the Tool lines above it; official never shows state to the model at all.
const MultiTurnRenderProtocolV2 = "bfcl-multi-turn-json-v2"

// MultiTurnRenderProtocolFinishV1 adds the turn-end control tool. Reuses E3's
// tool name so the single-turn abstention probe and this share one identifier,
// but the description asks about turn completion rather than tool relevance --
// a judgement made after acting, with execution results in hand.
const MultiTurnRenderProtocolFinishV1 = "bfcl-multi-turn-json-finish-v1"

var multiTurnFinishFunction = json.RawMessage(`{"name":"finish_task","description":"Call this with empty arguments when the current turn's request is already satisfied by the results so far and no further tool call is needed.","parameters":{"type":"dict","properties":{},"required":[]}}`)

// multiTurnFinishReminder restates the exit immediately before the decision.
// Diagnosis: with the rule only in the system preamble the model called again
// even under the free fence anchor; restated here it ends the turn correctly.
const multiTurnFinishClass = "__control__"

const multiTurnFinishReminder = "If the current turn's request is already satisfied by the results above, call finish_task with empty arguments. Otherwise issue the next call."

// MultiTurnAnchor selects the prefill anchor. Anchors that force a JSON object
// make an empty turn-ending response unreachable, so the choice is measured by
// the E7b probe rather than inferred. See bfcl-v4-anchor-position-20260820.md.
type MultiTurnAnchor string

const (
	// There is deliberately no "none" tier. A bare `Assistant: ` is what E7
	// already ran, and C1's shallowest measured tier is the fence — which also
	// carries a cross-experiment anchor value (simple_python 28.75%), so it is
	// the meaningful lower bound. A no-anchor tier would only re-run E7.
	MultiTurnAnchorFence  MultiTurnAnchor = "fence"
	MultiTurnAnchorArray  MultiTurnAnchor = "array"
	MultiTurnAnchorObject MultiTurnAnchor = "object"
)

func (anchor MultiTurnAnchor) Prefill() string {
	switch anchor {
	case MultiTurnAnchorArray:
		return "```json\n["
	case MultiTurnAnchorObject:
		return "```json\n{\"name\":\""
	case MultiTurnAnchorFence:
		return "```json\n"
	default:
		return "```json\n"
	}
}

// EmptyReachable reports whether the model can still end a turn by emitting an
// empty call list under this anchor.
func (anchor MultiTurnAnchor) EmptyReachable() bool {
	return anchor != MultiTurnAnchorObject
}

func ValidMultiTurnAnchor(value string) bool {
	switch MultiTurnAnchor(value) {
	case MultiTurnAnchorFence, MultiTurnAnchorArray, MultiTurnAnchorObject:
		return true
	}
	return false
}

type MultiTurnExecutor interface {
	Execute(context.Context, string, []string) ([]string, error)
}

type MultiTurnRunnerOptions struct {
	Generator continuation.Generator
	// Completer drives the native chat-completions tool path. It is set (and used
	// instead of Generator) only when Transport is TransportChatCompletionsNativeFC.
	// The RWKV backend has no native FC, so it always runs through Generator.
	Completer toolchat.Completer
	Executor  MultiTurnExecutor
	SessionID string
	Model     string
	Tier      Tier
	Transport Transport
	Anchor    MultiTurnAnchor
	// FinishTool injects the E3 control tool and a per-step restatement of the
	// turn-end rule. Official ends a turn when the model emits no call, which for
	// a chat model means prose; the anchor forbids prose, so without an explicit
	// exit no turn ever ends on its own (0 of 207 turns across both anchors).
	FinishTool          bool
	RenderInitialConfig bool
	MaxOutputTokens     int
	RouteMaxTokens      int
	MaxPromptChars      int
	MaxPromptTokens     int
	TokenCounter        func(string) (int, error)
	MaxSteps            int
	// MaxTurns truncates the case after N turns. Probe-only: a truncated result
	// is shorter than the GT turn list, which the official evaluator reports as
	// multi_turn:force_terminated, so such runs must never enter a score table.
	MaxTurns                 int
	RouteRetries             int
	DuplicateReplayLimit     int
	DuplicateRescueThreshold int
	SameToolRescueLimit      int
	Temperature              float32
	CaseTimeout              time.Duration
}

// errPromptBudget marks a prompt-size abort. It must not be treated as a parse
// error: feeding a correction back only makes the next prompt longer.
type promptBudgetError struct{ message string }

func (err *promptBudgetError) Error() string { return err.message }

// errInfrastructure marks a failure of the harness or its dependencies rather
// than of the model, so E8 can keep those cases out of the scored denominator.
type infrastructureError struct{ err error }

func (err *infrastructureError) Error() string { return err.err.Error() }
func (err *infrastructureError) Unwrap() error { return err.err }

type MultiTurnEvent struct {
	Kind           string   `json:"kind"`
	Turn           int      `json:"turn"`
	Step           int      `json:"step,omitempty"`
	Reason         string   `json:"reason,omitempty"`
	Route          string   `json:"route,omitempty"`
	Bundles        []string `json:"bundles,omitempty"`
	BeforeTools    []string `json:"before_tools,omitempty"`
	AfterTools     []string `json:"after_tools,omitempty"`
	Signature      string   `json:"signature,omitempty"`
	Retry          int      `json:"retry,omitempty"`
	ExecutionError string   `json:"execution_error,omitempty"`
	Generated      string   `json:"generated_content,omitempty"`
}

type MultiTurnStepTrace struct {
	Step             int    `json:"step"`
	PromptSHA256     string `json:"prompt_sha256"`
	PromptBytes      int    `json:"prompt_bytes"`
	PromptTokens     int    `json:"prompt_tokens,omitempty"`
	PrefillAnchor    string `json:"prefill_anchor,omitempty"`
	AssemblyMode     string `json:"assembly_mode,omitempty"`
	GeneratedContent string `json:"generated_content"`
	Content          string `json:"content,omitempty"`
	// FinishReason is the provider stop reason (native path). "length" with no
	// tool_calls means the model ran out of budget mid-response -- a runaway
	// reasoning block under thinking -- which counts as a model failure, not an
	// exclusion. Scan for it to tell an inadequate --max-tokens from genuine
	// non-convergence.
	FinishReason     string              `json:"finish_reason,omitempty"`
	ToolCalls        []toolchat.ToolCall `json:"tool_calls,omitempty"`
	ExecutionCalls   []string            `json:"execution_calls,omitempty"`
	ExecutionResults []string            `json:"execution_results,omitempty"`
	ParseError       string              `json:"parse_error,omitempty"`
	ProbeSelection   string              `json:"probe_selection,omitempty"`
	Repairs          []string            `json:"repairs,omitempty"`
	InputTokens      int                 `json:"input_tokens,omitempty"`
	OutputTokens     int                 `json:"output_tokens,omitempty"`
	Latency          float64             `json:"latency,omitempty"`
}

type MultiTurnTurnTrace struct {
	Turn          int                  `json:"turn"`
	Messages      []Message            `json:"messages"`
	Catalog       []string             `json:"catalog"`
	RouteCalls    int                  `json:"route_calls,omitempty"`
	RouteDecision string               `json:"route_decision,omitempty"`
	Steps         []MultiTurnStepTrace `json:"steps"`
	EndedBy       string               `json:"ended_by"`
}

// MultiTurnFailureKind separates harness/dependency failures from model
// failures. Both used to surface as a short result list, which the official
// evaluator reports as multi_turn:force_terminated either way.
type MultiTurnFailureKind string

const (
	MultiTurnFailureNone           MultiTurnFailureKind = ""
	MultiTurnFailureModel          MultiTurnFailureKind = "model"
	MultiTurnFailureInfrastructure MultiTurnFailureKind = "infrastructure"
)

type MultiTurnTrace struct {
	ID              string               `json:"id"`
	Category        string               `json:"category"`
	Tier            string               `json:"tier"`
	Result          [][][]string         `json:"result"`
	Turns           []MultiTurnTurnTrace `json:"turns"`
	Events          []MultiTurnEvent     `json:"events,omitempty"`
	PathDiagnostic  []string             `json:"path_diagnostic,omitempty"`
	ModelCalls      int                  `json:"model_calls"`
	RouteCalls      int                  `json:"route_calls,omitempty"`
	InputTokens     int                  `json:"input_tokens,omitempty"`
	OutputTokens    int                  `json:"output_tokens,omitempty"`
	Latency         float64              `json:"latency,omitempty"`
	MaxPromptBytes  int                  `json:"max_prompt_bytes"`
	MaxPromptTokens int                  `json:"max_prompt_tokens,omitempty"`
	TurnExits       map[string]int       `json:"turn_exits,omitempty"`
	// Truncated marks a probe run stopped by MaxTurns. Such a result is not a
	// valid scoring artifact.
	Truncated   bool                 `json:"truncated_by_max_turns,omitempty"`
	Error       string               `json:"error,omitempty"`
	FailureKind MultiTurnFailureKind `json:"failure_kind,omitempty"`
}

// fail records a terminal error and whether it is attributable to the model.
func (trace *MultiTurnTrace) fail(err error) {
	trace.Error = err.Error()
	var infra *infrastructureError
	if errors.As(err, &infra) {
		trace.FailureKind = MultiTurnFailureInfrastructure
		return
	}
	trace.FailureKind = MultiTurnFailureModel
}

type multiTurnTranscript struct {
	Role    string
	Content any
	// ToolCalls and CallIDs are native-only and additive: the wrapped renderer
	// (RenderMultiTurnPrompt) reads only Role and Content, so populating these
	// leaves every wrapped prompt byte-identical. The native stepper reconstructs
	// structured assistant tool_calls and tool_call_id-linked results from them.
	ToolCalls []toolchat.ToolCall
	CallIDs   []string
}

// turnStepper runs one model decision and normalizes it to tool calls,
// regardless of wire protocol. noCall reports an empty call list, which is the
// turn-end signal (for native FC an empty tool_calls response is exactly the
// official "model emitted no call" termination). Everything the main loop does
// above this seam -- finish_task selection, dedup, loop-rescue, execution,
// result accumulation -- already operates on []toolchat.ToolCall and is shared.
type turnStepper interface {
	Step(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, names map[string]string, turn, step int, options MultiTurnRunnerOptions) (MultiTurnStepTrace, []toolchat.ToolCall, bool, error)
}

// wrappedStepper is the continuation/markdown protocol: render a flat transcript
// with a prefill anchor, call Generator.Continue, reassemble, and parse the
// generated text into calls. It delegates to the frozen runMultiTurnStep so the
// wrapped render path stays byte-for-byte what E1/E2/E8 recorded.
type wrappedStepper struct{}

func (wrappedStepper) Step(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, _ map[string]string, turn, step int, options MultiTurnRunnerOptions) (MultiTurnStepTrace, []toolchat.ToolCall, bool, error) {
	return runMultiTurnStep(ctx, transcript, entry, functions, turn, step, options)
}

func RunMultiTurnCase(parent context.Context, entry MultiTurnCase, catalog MultiTurnCatalog, options MultiTurnRunnerOptions) MultiTurnTrace {
	trace := MultiTurnTrace{ID: entry.ID, Category: entry.Category, Tier: string(options.Tier), PathDiagnostic: append([]string(nil), entry.Path...)}
	if options.Generator == nil || options.Executor == nil || options.SessionID == "" {
		trace.Error = "BFCL multi-turn generator, executor, and session are required"
		return trace
	}
	if options.Tier != TierBaseline && options.Tier != TierEnhanced {
		trace.Error = fmt.Sprintf("unsupported BFCL multi-turn tier %q", options.Tier)
		return trace
	}
	if options.MaxSteps <= 0 {
		options.MaxSteps = 20
	}
	if options.RouteMaxTokens <= 0 {
		options.RouteMaxTokens = 48
	}
	if options.MaxOutputTokens <= 0 {
		options.MaxOutputTokens = 1024
	}
	if options.CaseTimeout <= 0 {
		options.CaseTimeout = 2 * time.Minute
	}
	if options.Anchor == "" {
		options.Anchor = MultiTurnAnchorFence
	}
	// Pick the wire protocol once. Native FC (Qwen's own tool-calling, the
	// official-comparable path) speaks structured tool_calls and needs a global
	// sanitized->original name map to un-sanitize before the simulator; wrapped
	// leaves names nil and behaves exactly as the frozen runs did.
	native := options.Transport == TransportChatCompletionsNativeFC
	var stepper turnStepper = wrappedStepper{}
	var names map[string]string
	if native {
		if options.Completer == nil {
			trace.Error = "BFCL multi-turn native FC transport requires a completer"
			return trace
		}
		if options.Tier != TierBaseline {
			trace.Error = "BFCL multi-turn native FC currently supports only the baseline tier"
			return trace
		}
		built, err := multiTurnNativeNames(catalog.Functions)
		if err != nil {
			trace.Error = err.Error()
			return trace
		}
		names = built
		stepper = nativeStepper{completer: options.Completer}
	}
	ctx, cancel := context.WithTimeout(parent, options.CaseTimeout)
	defer cancel()
	var transcript []multiTurnTranscript
	trace.Result = make([][][]string, 0, len(entry.Turns))
	trace.TurnExits = make(map[string]int, len(entry.Turns))
	for turnIndex, originalMessages := range entry.Turns {
		if options.MaxTurns > 0 && turnIndex >= options.MaxTurns {
			trace.Truncated = true
			break
		}
		messages := append([]Message(nil), originalMessages...)
		if len(messages) == 0 {
			messages = []Message{{Role: "user", Content: AdditionalFunctionPrompt}}
			trace.Events = append(trace.Events, MultiTurnEvent{Kind: "holdout_released", Turn: turnIndex})
		}
		for _, message := range messages {
			transcript = append(transcript, multiTurnTranscript{Role: multiTurnRole(message.Role), Content: message.Content})
		}
		available := catalog.ForTurn(turnIndex, nil)
		turnTrace := MultiTurnTurnTrace{Turn: turnIndex, Messages: messages, Steps: []MultiTurnStepTrace{}}
		if options.Tier == TierEnhanced {
			selected, decision, calls, events, err := routeMultiTurn(ctx, transcript, entry, available, turnIndex, options)
			turnTrace.RouteCalls = calls
			trace.RouteCalls += calls
			trace.ModelCalls += calls
			trace.Events = append(trace.Events, events...)
			turnTrace.RouteDecision = decision
			if err != nil {
				// Product semantics degrade an exhausted route to respond
				// rather than killing the case (agent/runner.go:1769).
				var infra *infrastructureError
				if errors.As(err, &infra) {
					trace.fail(err)
					turnTrace.EndedBy = "route_infrastructure_error"
					trace.TurnExits[turnTrace.EndedBy]++
					trace.Turns = append(trace.Turns, turnTrace)
					return trace
				}
				decision = string(agent.RouteRespond)
				turnTrace.RouteDecision = "respond_degraded"
				trace.Events = append(trace.Events, MultiTurnEvent{Kind: "route_degraded", Turn: turnIndex, Reason: err.Error(), Route: decision})
			}
			if decision == string(agent.RouteRespond) {
				if turnTrace.EndedBy == "" {
					turnTrace.EndedBy = "route_respond"
				}
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: "[]"})
				// Must stay an empty slice: a nil turn marshals to JSON null and
				// the official evaluator raises TypeError for the whole split
				// (eval_runner.py:222, no per-entry guard).
				trace.Result = append(trace.Result, [][]string{})
				trace.TurnExits[turnTrace.EndedBy]++
				trace.Turns = append(trace.Turns, turnTrace)
				continue
			}
			// Record which involved classes narrowing dropped. GT is never
			// consulted here; correlating dropped classes with GT is an
			// offline analysis step.
			if dropped := droppedClasses(entry.InvolvedClasses, selected); len(dropped) > 0 {
				trace.Events = append(trace.Events, MultiTurnEvent{Kind: "narrowing_dropped_class", Turn: turnIndex, Bundles: dropped, AfterTools: MultiTurnFunctionNames(selected)})
			}
			available = selected
		}
		if options.FinishTool {
			available = append(append([]MultiTurnFunction(nil), available...),
				MultiTurnFunction{Name: FinishTaskName, Class: multiTurnFinishClass, Raw: multiTurnFinishFunction})
		}
		turnTrace.Catalog = MultiTurnFunctionNames(available)
		turnResult := make([][]string, 0)
		// Real loops alternate (cd document / cd workspace), so comparing only
		// against the previous signature never fires. Count per turn instead.
		signatureCounts := make(map[string]int)
		lastTool := ""
		sameToolStreak := 0
		parseRetries := 0
		for step := 0; step < options.MaxSteps; step++ {
			stepTrace, calls, noCall, err := stepper.Step(ctx, transcript, entry, available, names, turnIndex, step, options)
			turnTrace.Steps = append(turnTrace.Steps, stepTrace)
			trace.ModelCalls++
			trace.InputTokens += stepTrace.InputTokens
			trace.OutputTokens += stepTrace.OutputTokens
			trace.Latency += stepTrace.Latency
			trace.MaxPromptBytes = max(trace.MaxPromptBytes, stepTrace.PromptBytes)
			trace.MaxPromptTokens = max(trace.MaxPromptTokens, stepTrace.PromptTokens)
			if err != nil {
				var budget *promptBudgetError
				if errors.As(err, &budget) {
					trace.fail(err)
					turnTrace.EndedBy = "prompt_budget_exceeded"
					trace.TurnExits[turnTrace.EndedBy]++
					trace.Turns = append(trace.Turns, turnTrace)
					return trace
				}
				var infra *infrastructureError
				if errors.As(err, &infra) {
					trace.fail(err)
					turnTrace.EndedBy = "generator_error"
					trace.TurnExits[turnTrace.EndedBy]++
					trace.Turns = append(trace.Turns, turnTrace)
					return trace
				}
				if options.Tier == TierEnhanced && stepTrace.ParseError != "" && parseRetries < options.RouteRetries {
					parseRetries++
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "correction_retry", Turn: turnIndex, Step: step, Reason: stepTrace.ParseError, Retry: parseRetries})
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)}, multiTurnTranscript{Role: "User", Content: "The previous output was invalid. Return only one JSON function-call object, a JSON array of calls, or [] when complete."})
					continue
				}
				if transcriptContent(stepTrace) != "" {
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)})
				}
				turnTrace.EndedBy = "parse_error"
				break
			}
			if noCall {
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)})
				turnTrace.EndedBy = "empty_response"
				break
			}
			// The control tool is a turn-end signal, not an executable call: it
			// must never reach the simulator or the official result. Following
			// E3, only a pure finish_task counts -- mixing it with real calls
			// cannot be used to hide those calls.
			if options.FinishTool {
				real := make([]toolchat.ToolCall, 0, len(calls))
				finishes := 0
				for _, call := range calls {
					if call.Name == FinishTaskName {
						finishes++
						continue
					}
					real = append(real, call)
				}
				if finishes > 0 && len(real) == 0 {
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "finish_task_selected", Turn: turnIndex, Step: step})
					turnTrace.Steps[len(turnTrace.Steps)-1].ProbeSelection = "finish_task"
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)})
					turnTrace.EndedBy = "finish_task"
					break
				}
				if finishes > 0 {
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "finish_task_mixed", Turn: turnIndex, Step: step})
					turnTrace.Steps[len(turnTrace.Steps)-1].ProbeSelection = "mixed"
					calls = real
				}
			}
			parseRetries = 0
			executionCalls, encodeErr := multiTurnExecutionCalls(calls, names)
			if encodeErr != nil {
				turnTrace.Steps[len(turnTrace.Steps)-1].ParseError = encodeErr.Error()
				turnTrace.EndedBy = "result_encoding_error"
				break
			}
			signature := multiTurnCallSignature(calls)
			signatureCounts[signature]++
			repeats := signatureCounts[signature]
			toolName := calls[0].Name
			if toolName == lastTool {
				sameToolStreak++
			} else {
				sameToolStreak = 1
			}
			lastTool = toolName
			if options.Tier == TierEnhanced && options.DuplicateReplayLimit > 0 && repeats > options.DuplicateReplayLimit {
				trace.Events = append(trace.Events, MultiTurnEvent{Kind: "duplicate_rejected", Turn: turnIndex, Step: step, Signature: signature, Retry: repeats})
				if options.DuplicateRescueThreshold > 0 && repeats >= options.DuplicateRescueThreshold {
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "loop_rescue", Turn: turnIndex, Step: step, Reason: "repeated_call", Signature: signature})
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)})
					turnTrace.EndedBy = "loop_rescue"
					break
				}
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)}, multiTurnTranscript{Role: "Tool", Content: []string{"This exact call is disabled. Use the existing result or choose another tool."}})
				continue
			}
			if options.Tier == TierEnhanced && options.SameToolRescueLimit > 0 && sameToolStreak >= options.SameToolRescueLimit {
				trace.Events = append(trace.Events, MultiTurnEvent{Kind: "loop_rescue", Turn: turnIndex, Step: step, Reason: "same_tool_spiral", Signature: signature})
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace)})
				turnTrace.EndedBy = "loop_rescue"
				break
			}
			results, executeErr := options.Executor.Execute(ctx, options.SessionID, executionCalls)
			if executeErr != nil {
				trace.fail(&infrastructureError{err: executeErr})
				turnTrace.EndedBy = "sidecar_error"
				trace.TurnExits[turnTrace.EndedBy]++
				trace.Turns = append(trace.Turns, turnTrace)
				return trace
			}
			turnResult = append(turnResult, executionCalls)
			turnTrace.Steps[len(turnTrace.Steps)-1].ExecutionCalls = executionCalls
			turnTrace.Steps[len(turnTrace.Steps)-1].ExecutionResults = results
			// ToolCalls/CallIDs are additive and native-only: they let the native
			// stepper rebuild the assistant tool_calls and match each tool result to
			// its call id on the next step. The wrapped renderer ignores them.
			transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: transcriptContent(stepTrace), ToolCalls: calls}, multiTurnTranscript{Role: "Tool", Content: results, CallIDs: toolCallIDs(calls)})
			for _, result := range results {
				if strings.HasPrefix(result, "Error during execution:") {
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "execution_error_feedback", Turn: turnIndex, Step: step, ExecutionError: result})
				}
			}
		}
		if turnTrace.EndedBy == "" {
			turnTrace.EndedBy = "step_limit"
		}
		trace.TurnExits[turnTrace.EndedBy]++
		trace.Result = append(trace.Result, turnResult)
		trace.Turns = append(trace.Turns, turnTrace)
	}
	return trace
}

// droppedClasses lists involved classes that narrowing removed from this turn's
// catalog. It reads only the test entry and the router's own decision.
func droppedClasses(involved []string, selected []MultiTurnFunction) []string {
	kept := make(map[string]struct{}, len(selected))
	for _, function := range selected {
		kept[function.Class] = struct{}{}
	}
	dropped := make([]string, 0, len(involved))
	for _, className := range involved {
		if _, ok := kept[className]; !ok {
			dropped = append(dropped, className)
		}
	}
	return dropped
}

func runMultiTurnStep(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, turn, step int, options MultiTurnRunnerOptions) (MultiTurnStepTrace, []toolchat.ToolCall, bool, error) {
	anchor := options.Anchor.Prefill()
	prompt, err := RenderMultiTurnPrompt(entry, functions, transcript, options.Anchor, options.RenderInitialConfig, options.FinishTool)
	trace := MultiTurnStepTrace{Step: step, PromptBytes: len(prompt), PromptSHA256: promptSHA256(prompt), PrefillAnchor: anchor}
	if err != nil {
		return trace, nil, false, err
	}
	if options.TokenCounter != nil {
		// A silent 0 here would disable the guard, so a counting failure is an
		// infrastructure abort rather than an unguarded step.
		tokens, countErr := options.TokenCounter(prompt)
		if countErr != nil {
			return trace, nil, false, &infrastructureError{err: fmt.Errorf("count prompt tokens: %w", countErr)}
		}
		trace.PromptTokens = tokens
	}
	// Prompt-budget aborts are terminal, never a parse error: a correction retry
	// would only append more transcript and overflow again.
	if options.MaxPromptTokens > 0 && trace.PromptTokens > options.MaxPromptTokens {
		return trace, nil, false, &promptBudgetError{message: fmt.Sprintf("multi-turn prompt %d tokens exceeds max_prompt_tokens %d", trace.PromptTokens, options.MaxPromptTokens)}
	}
	if options.MaxPromptChars > 0 && len(prompt) > options.MaxPromptChars {
		return trace, nil, false, &promptBudgetError{message: fmt.Sprintf("multi-turn prompt %d bytes exceeds max_prompt_chars %d", len(prompt), options.MaxPromptChars)}
	}
	started := time.Now()
	completion, err := options.Generator.Continue(ctx, continuation.Request{Model: options.Model, Prompt: prompt, MaxOutputTokens: options.MaxOutputTokens, Stops: multiTurnStops(options.Transport), Sampling: continuation.Sampling{Temperature: options.Temperature, TopK: 1, TopP: 1, PenaltyDecay: 1}}, nil)
	trace.Latency = time.Since(started).Seconds()
	if err != nil {
		return trace, nil, false, &infrastructureError{err: err}
	}
	trace.GeneratedContent = strings.TrimSpace(completion.Text)
	trace.InputTokens = completion.Usage.PromptTokens
	trace.OutputTokens = completion.Usage.CompletionTokens
	trace.Content, trace.AssemblyMode = assembleMultiTurnContent(anchor, completion.Text)
	calls, parseErr := ParseMarkdownCalls(trace.Content)
	if parseErr != nil && options.Tier == TierEnhanced {
		rawFunctions := make([]json.RawMessage, 0, len(functions))
		for _, function := range functions {
			rawFunctions = append(rawFunctions, function.Raw)
		}
		outcome, compatErr := ParseMarkdownCallsWithMode(trace.Content, rawFunctions, ParserRWKVWireCompatV1)
		if compatErr == nil {
			calls = outcome.Calls
			trace.Repairs = outcome.Repairs
			parseErr = nil
		}
	}
	if parseErr != nil {
		trace.ParseError = parseErr.Error()
		return trace, nil, false, parseErr
	}
	trace.ToolCalls = calls
	return trace, calls, len(calls) == 0, nil
}

// multiTurnStops adds the Tool role to the single-turn stop set. Without it the
// model can continue past its own call and write fabricated tool results, which
// then parse as part of the same step. baselineStops is left untouched so the
// frozen E1/E2 single-turn renders stay byte-identical.
func multiTurnStops(transport Transport) []string {
	stops := baselineStops(transport)
	if transport == TransportChatCompletionsWrapped {
		// Chat Completions accepts at most four stop sequences. The wrapped
		// baseline already uses all four slots, so replace the redundant EOS
		// marker with the multi-turn Tool role guard. The provider terminates at
		// EOS itself; stopping before a fabricated Tool turn is specific to this
		// protocol and cannot be recovered after generation.
		stops = stops[:len(stops)-1]
	}
	return append(stops, "\nTool:")
}

// transcriptContent prefers the anchor-assembled content so the recorded
// assistant turn is valid JSON and the anchor is not duplicated when the next
// step re-prefills it.
func transcriptContent(step MultiTurnStepTrace) string {
	if step.Content != "" {
		return step.Content
	}
	return step.GeneratedContent
}

// closeAnchorArray closes the bracket the array anchor itself opened.
//
// With the bare "[" anchor the model writes one complete call object and stops,
// because from its side the object is the whole answer; the array terminator is
// scaffold the harness introduced. Probe A measured 13/20 Qwen cases failing on
// exactly this missing "]" while the call itself was correct.
//
// It is deliberately conservative: it only appends the terminator when the
// content is otherwise well formed. Unbalanced braces or an unterminated string
// mean the model was truncated, which is a genuine failure and must stay one.
// trimAnchorFence drops a closing fence that matches the opening one the anchor
// left in the prompt. Because assembly reinstates only the JSON body, the
// decoder never sees the opener and would read the closer as trailing garbage.
// The "```" stop keeps this from firing on either current transport, so it is
// defensive: no recorded run contains a trailing fence.
func trimAnchorFence(content string) string {
	trimmed := strings.TrimRight(content, " \t\n")
	if !strings.HasSuffix(trimmed, "```") {
		return content
	}
	return strings.TrimRight(strings.TrimSuffix(trimmed, "```"), " \t\n")
}

func closeAnchorArray(content string) (string, bool) {
	brackets, braces := 0, 0
	inString, escaped := false, false
	for _, symbol := range content {
		switch {
		case escaped:
			escaped = false
		case symbol == '\\' && inString:
			escaped = true
		case symbol == '"':
			inString = !inString
		case inString:
		case symbol == '[':
			brackets++
		case symbol == ']':
			brackets--
		case symbol == '{':
			braces++
		case symbol == '}':
			braces--
		}
	}
	if inString || escaped || braces != 0 || brackets <= 0 {
		return content, false
	}
	return content + strings.Repeat("]", brackets), true
}

// assembleMultiTurnContent mirrors assembleMarkdownContent: wrapped transports
// sometimes echo the anchor, so a self-contained answer must not be re-prefixed.
func assembleMultiTurnContent(anchor, generated string) (string, string) {
	candidate := strings.TrimSpace(generated)
	if anchor == "" {
		return candidate, "no_anchor"
	}
	body := strings.TrimPrefix(anchor, "```json\n")
	if body != "" {
		// The opener stayed in the prompt, so a closer here is scaffold too.
		candidate = trimAnchorFence(candidate)
		generated = trimAnchorFence(generated)
	}
	switch {
	case body == "" && (strings.HasPrefix(candidate, "{") || strings.HasPrefix(candidate, "[")):
		return candidate, "self_contained"
	case body == "[" && strings.HasPrefix(candidate, "["):
		if closed, ok := closeAnchorArray(candidate); ok {
			return closed, "self_contained_closed"
		}
		return candidate, "self_contained"
	case body == "[" && strings.HasPrefix(candidate, `{"name":"`):
		if closed, ok := closeAnchorArray("[" + candidate); ok {
			return closed, "array_elements_closed"
		}
		return "[" + candidate, "array_elements"
	case body == `{"name":"` && strings.HasPrefix(candidate, `{"name":"`):
		return candidate, "self_contained"
	}
	continued := body + generated
	if body == "[" {
		// RWKV usually writes its own "]" here, in which case the scan is
		// balanced and this is a no-op; it only fires when the terminator is
		// missing.
		if closed, ok := closeAnchorArray(continued); ok {
			return closed, "prefill_continuation_closed"
		}
	}
	return continued, "prefill_continuation"
}

func RenderMultiTurnPrompt(entry MultiTurnCase, functions []MultiTurnFunction, transcript []multiTurnTranscript, anchor MultiTurnAnchor, renderInitialConfig, finishTool bool) (string, error) {
	initial, err := json.Marshal(entry.InitialConfig)
	if err != nil {
		return "", err
	}
	var prompt strings.Builder
	prompt.WriteString(`System: You are a BFCL multi-turn tool agent. Use only the listed tools.
Return one JSON function-call object in exactly this shape: {"name":"TOOL_NAME","arguments":{"ARGUMENT":"VALUE"}}.
For parallel calls return a JSON array of those objects. The key is always "arguments", never "parameters" or "response". Do not predict tool results. Return [] when the current turn is complete. Output JSON only and no prose. Tool errors are evidence: correct the call instead of repeating it.
Tools:
[`)
	for index, function := range functions {
		if index > 0 {
			prompt.WriteString(",\n")
		}
		prompt.Write(function.Raw)
	}
	prompt.WriteString("\n]\n")
	// V1 rendered initial_config into every step. After the first executed call
	// the block is stale and contradicts the Tool lines above it; official keeps
	// state out of the model input entirely (base_handler.go state_log). State is
	// discoverable through pwd/ls, and response_checker asserts GT subset of the
	// model's returns, so read-only exploration cannot cost correctness.
	if renderInitialConfig {
		prompt.WriteString("Initial state:\n")
		prompt.Write(initial)
		prompt.WriteByte('\n')
	}
	for _, message := range transcript {
		fmt.Fprintf(&prompt, "%s: ", message.Role)
		switch value := message.Content.(type) {
		case string:
			prompt.WriteString(value)
		default:
			encoded, err := json.Marshal(value)
			if err != nil {
				return "", err
			}
			prompt.Write(encoded)
		}
		prompt.WriteByte('\n')
	}
	if finishTool {
		fmt.Fprintf(&prompt, "User: %s\n", multiTurnFinishReminder)
	}
	prompt.WriteString("Assistant: ")
	prompt.WriteString(anchor.Prefill())
	return prompt.String(), nil
}

func MultiTurnExecutionCalls(calls []toolchat.ToolCall) ([]string, error) {
	return multiTurnExecutionCalls(calls, nil)
}

// multiTurnExecutionCalls renders calls to executable Python strings for the
// simulator. names maps sanitized native tool names back to their originals
// (dot-bearing BFCL names get `.`->`_` for the OpenAI tools array); it is nil on
// the wrapped path, where the model already emits original names.
func multiTurnExecutionCalls(calls []toolchat.ToolCall, names map[string]string) ([]string, error) {
	result := make([]string, 0, len(calls))
	for _, call := range calls {
		encoded, err := ToResultString([]toolchat.ToolCall{call}, names, LanguagePython)
		if err != nil {
			return nil, err
		}
		result = append(result, strings.TrimSuffix(strings.TrimPrefix(encoded, "["), "]"))
	}
	return result, nil
}

// toolCallIDs extracts the provider-assigned call ids so native tool-result
// messages can reference them. Wrapped calls carry no ids and ignore the result.
func toolCallIDs(calls []toolchat.ToolCall) []string {
	ids := make([]string, len(calls))
	for index, call := range calls {
		ids[index] = call.ID
	}
	return ids
}

func multiTurnCallSignature(calls []toolchat.ToolCall) string {
	var parts []string
	for _, call := range calls {
		parts = append(parts, call.Name+"\x00"+call.Arguments)
	}
	return strings.Join(parts, "\x01")
}

func multiTurnRole(role string) string {
	switch strings.ToLower(strings.TrimSpace(role)) {
	case "system":
		return "System"
	case "assistant":
		return "Assistant"
	default:
		return "User"
	}
}

func routeMultiTurn(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, turn int, options MultiTurnRunnerOptions) ([]MultiTurnFunction, string, int, []MultiTurnEvent, error) {
	bundles := make([]agent.ToolBundle, 0, len(entry.InvolvedClasses))
	for _, className := range entry.InvolvedClasses {
		bundles = append(bundles, agent.ToolBundle{Name: className, Description: "BFCL functions provided by " + className + "."})
	}
	protocol := agent.G1IProgressiveToolRouteProtocol{}
	prompt := "System: " + protocol.Instructions(bundles) + "\n"
	for _, message := range transcript {
		content, ok := message.Content.(string)
		if !ok {
			encoded, _ := json.Marshal(message.Content)
			content = string(encoded)
		}
		prompt += message.Role + ": " + content + "\n"
	}
	prompt += "Assistant: "
	var events []MultiTurnEvent
	for attempt := 0; attempt <= options.RouteRetries; attempt++ {
		completion, err := options.Generator.Continue(ctx, continuation.Request{Model: options.Model, Prompt: prompt, MaxOutputTokens: options.RouteMaxTokens, Stops: protocol.Stops(), Sampling: continuation.Sampling{Temperature: options.Temperature, TopK: 1, TopP: 1, PenaltyDecay: 1}}, nil)
		if err != nil {
			return nil, "", attempt + 1, events, &infrastructureError{err: err}
		}
		decision, parseErr := protocol.Parse(completion.Text, completion.FinishReason, bundles)
		if parseErr == nil {
			before := MultiTurnFunctionNames(functions)
			if decision.Route == agent.RouteRespond {
				events = append(events, MultiTurnEvent{Kind: "route_decision", Turn: turn, Route: string(decision.Route), BeforeTools: before, Generated: strings.TrimSpace(completion.Text)})
				return nil, string(decision.Route), attempt + 1, events, nil
			}
			selected := make(map[string]struct{}, len(decision.Bundles))
			for _, className := range decision.Bundles {
				selected[className] = struct{}{}
			}
			var narrowed []MultiTurnFunction
			for _, function := range functions {
				if _, ok := selected[function.Class]; ok {
					narrowed = append(narrowed, function)
				}
			}
			events = append(events, MultiTurnEvent{Kind: "route_decision", Turn: turn, Route: string(decision.Route), Bundles: decision.Bundles, BeforeTools: before, AfterTools: MultiTurnFunctionNames(narrowed), Generated: strings.TrimSpace(completion.Text)})
			return narrowed, string(decision.Route), attempt + 1, events, nil
		}
		events = append(events, MultiTurnEvent{Kind: "route_retry", Turn: turn, Reason: parseErr.Error(), Retry: attempt + 1, Generated: strings.TrimSpace(completion.Text)})
		prompt += completion.Text + "\nUser: " + protocol.Correction(parseErr, bundles) + "\nAssistant: "
	}
	return nil, "", options.RouteRetries + 1, events, fmt.Errorf("BFCL multi-turn route retries exhausted")
}
