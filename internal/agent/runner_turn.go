package agent

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"slices"
	"strings"
	"time"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// G1DecisionFakeThinkPrefix is the exact half-open prefix measured by the G1
// abstention experiments. The final '>' and any answer bytes must come from the
// model. Whitespace is part of this protocol variable.
//
// Half-open is not an accident. Measured on this tokenizer: ">" is one token
// and ">{" is also one token, so withholding the ">" lets the model emit it
// merged with the byte that opens a structured payload. Closing the tag here
// removes that merged path and forces a fresh token instead.
//
// The bytes live in the wire package next to the prefill axis that selects
// them; this alias keeps the historical exported name for callers and tests.
const G1DecisionFakeThinkPrefix = wire.FakeThinkHalfPrefix

// G1DecisionClosedThinkPrefix closes the block in the prompt, so the model
// cannot open one at all. It costs the merged ">{" continuation above, and it
// is newline-sensitive: the abstention lab measured that appending "\n\n" makes
// 10/80 completions resume thinking, so nothing may follow these bytes.
const G1DecisionClosedThinkPrefix = wire.FakeThinkClosedPrefix

type runnerTurn struct {
	r        *Runner
	ctx      context.Context
	task     string
	observer func(Event)

	result       Result
	activeSpecs  []ToolSpec
	activeTools  map[string]Tool
	messages     []Message
	turnMessages []Message

	retries                 int
	routeViolations         int
	seenSuccessfulToolCalls map[string]int
	failedToolCallEpochs    map[string]int
	unavailableTools        map[string]struct{}
	unverified              []string
	successfulToolCalls     int
	toolAttempts            int
	hasToolEvidence         bool
	consecutiveFailedTool   string
	consecutiveToolFailures int
	lastNativeCallKey       string
	nativeRepeatStreak      int
	sameCallStreak          int
	lastSameCallKey         string
	sameToolSuccessStreak   int
	lastSameToolName        string
	rescueMode              bool
	workspaceRevision       int
	stage                   GenerationStage
	assistantPrefix         string
	// frame is the prefill resolved for the current decision generation; the
	// output post-processing strips exactly these bytes back off.
	frame                 wire.Frame
	forceAnswer           bool
	terminalToolCompleted bool
	answerViolations      int
}

type turnModelStep struct {
	generated        continuation.Result
	nativeCall       *toolchat.ToolCall
	reasoningContent string
	modelAction      string
}

func newRunnerTurn(
	r *Runner,
	ctx context.Context,
	task string,
	observer func(Event),
) *runnerTurn {
	return &runnerTurn{
		r:                       r,
		ctx:                     ctx,
		task:                    task,
		observer:                observer,
		result:                  Result{StartedAtMS: time.Now().UnixMilli(), Steps: make([]Step, 0, r.options.MaxSteps), Route: RouteInspect},
		activeSpecs:             append([]ToolSpec(nil), r.toolSpecs...),
		activeTools:             r.tools,
		turnMessages:            []Message{{Role: RoleUser, Content: task}},
		seenSuccessfulToolCalls: make(map[string]int),
		failedToolCallEpochs:    make(map[string]int),
		unavailableTools:        make(map[string]struct{}),
		stage:                   StageDecision,
	}
}

func (turn *runnerTurn) initialize() error {
	r := turn.r
	history := r.History()
	if r.toolRouter != nil {
		decision, routeSteps, err := r.decideToolRoute(
			turn.ctx,
			history,
			turn.task,
			turn.observer,
		)
		turn.result.RouteSteps = routeSteps
		if err != nil {
			return err
		}
		turn.result.Route = decision.Route
		turn.result.Bundles = append([]string(nil), decision.Bundles...)
		turn.activeSpecs = toolSpecsForBundles(r.toolSpecs, turn.result.Bundles)
		turn.activeTools = toolsForSpecs(r.tools, turn.activeSpecs)
	} else if r.router != nil {
		route, routeSteps, err := r.decideRoute(
			turn.ctx,
			history,
			turn.task,
			turn.observer,
		)
		turn.result.RouteSteps = routeSteps
		if err != nil {
			return err
		}
		turn.result.Route = route
	}

	control := r.controlForSpecs(turn.activeSpecs)
	if turn.result.Route == RouteRespond {
		control = r.responseControl
	}
	if r.options.NoToolGate == "state" && turn.successfulToolCalls == 0 {
		// State gate: the exit must not exist before any tool evidence; a
		// no_tool emitted here could only be a fabricated completion.
		turn.activeSpecs = dropNoToolSpec(turn.activeSpecs)
		control = r.controlForSpecs(turn.activeSpecs)
	}
	turn.assembleTurnMessages(history, control)

	turn.terminalToolCompleted = r.terminalTool == "" || turn.result.Route == RouteRespond
	// The decision prefill is not armed here. Every decision generation calls
	// resolveFrame, which asks the wire spec for the opening of the current
	// state, so the policy lives in exactly one place instead of being
	// re-derived at each tool/retry transition.
	return nil
}

// assembleTurnMessages expands the committed history plus the new task into
// the first decision transcript under the active control prompt. The control
// prompt is framing, not conversation data, so it never enters History.
func (turn *runnerTurn) assembleTurnMessages(history []Message, control string) {
	if turn.r.options.ControlPrompt == ControlPromptInline {
		label := "Repository task:"
		if turn.result.Route == RouteRespond {
			label = "Current user message:"
		}
		turn.messages = append([]Message(nil), history...)
		turn.messages = append(turn.messages, Message{
			Role:    RoleUser,
			Content: control + "\n\n" + label + "\n" + turn.task,
		})
		return
	}
	turn.messages = make([]Message, 0, len(history)+2)
	turn.messages = append(turn.messages, Message{Role: RoleSystem, Content: control})
	turn.messages = append(turn.messages, history...)
	turn.messages = append(turn.messages, Message{Role: RoleUser, Content: turn.task})
}

func (turn *runnerTurn) run() (Result, error) {
	for step := 1; step <= turn.r.options.MaxSteps; step++ {
		if err := turn.prepareAnswerStage(step); err != nil {
			return turn.result, err
		}
		modelStep, err := turn.generateModelStep(step)
		if err != nil {
			return turn.result, err
		}
		action, err := turn.parseModelAction(step, &modelStep)
		if err != nil {
			if retryErr := turn.retryProtocolAction(step, modelStep, err); retryErr != nil {
				return turn.result, retryErr
			}
			continue
		}
		if action.Type == ActionTypeFinal {
			done, finalErr := turn.finishFinalAction(step, action)
			if finalErr != nil {
				return turn.result, finalErr
			}
			if done {
				return turn.result, nil
			}
			continue
		}
		if action.Type == ActionTypeNoTool {
			if turn.stage == StageAnswer {
				// Entering the answer stage already required tool evidence, so
				// the no_tool gate does not apply here: the reason is the final
				// answer. parseModelAction rejected an empty payload.
				current := turn.currentStep()
				current.NoToolRationale = action.NoToolRationale
				current.NoToolAnswer = action.NoToolAnswer
				turn.commitFinalText(firstNonEmpty(action.NoToolAnswer, action.NoToolRationale))
				return turn.result, nil
			}
			if turn.r.options.NoToolGate != "" && turn.noToolGateRejects(action) {
				turn.rejectNoTool(step, action, modelStep)
				continue
			}
			if turn.result.Route == RouteRespond {
				if err := turn.retryRespondRoute(step, modelStep.modelAction); err != nil {
					return turn.result, err
				}
				continue
			}
			if turn.acceptSemanticNoTool(action, modelStep) {
				return turn.result, nil
			}
			continue
		}
		if turn.result.Route == RouteRespond {
			if err := turn.retryRespondRoute(step, modelStep.modelAction); err != nil {
				return turn.result, err
			}
			continue
		}
		done, err := turn.runToolAction(step, action, modelStep)
		if err != nil {
			return turn.result, err
		}
		if done {
			return turn.result, nil
		}
	}
	return turn.result, ErrMaxSteps
}

func (turn *runnerTurn) prepareAnswerStage(step int) error {
	if turn.result.Route != RouteInspect ||
		turn.toolAttempts == 0 ||
		!turn.terminalToolCompleted {
		return nil
	}
	// Round-1 forced the answer only at MaxSteps, so with ProtocolRetries=1 a
	// model that still emitted a tool call there died on its first violation.
	// AnswerStageLead starts the stage earlier to leave room for one re-ask.
	forcedAtStep := step == turn.r.options.MaxSteps
	if lead := turn.r.options.AnswerStageLead; lead > 0 && step == turn.r.options.MaxSteps-lead {
		forcedAtStep = true
	}
	if !forcedAtStep && !turn.forceAnswer {
		return nil
	}
	if !turn.hasToolEvidence {
		return noWorkspaceEvidenceError()
	}
	answerMessages, prefix := turn.r.protocol.PrepareAnswer(
		turn.messages,
		turn.unverified,
		turn.r.thinkingMode,
	)
	if len(answerMessages) == 0 {
		return fmt.Errorf("%w: protocol did not prepare an answer stage", ErrProtocol)
	}
	// The merged one-stage contract keeps the transcript intact and returns an
	// empty prefix: no <answer> envelope is prefilled, the model answers in
	// ordinary text. The two-stage contract must own an envelope prefix.
	if prefix == "" && turn.r.wire.Stages != wire.StagesOne {
		return fmt.Errorf("%w: protocol did not prepare an answer stage", ErrProtocol)
	}
	turn.messages = answerMessages
	turn.assistantPrefix = prefix
	// The answer stage owns its own opening; no decision-stage frame applies.
	turn.frame = wire.Frame{}
	turn.stage = StageAnswer
	if turn.result.ForcedAnswerReason == "" {
		turn.result.ForcedAnswerReason = forcedAnswerStepBudget
	}
	return nil
}

func (turn *runnerTurn) generateModelStep(step int) (turnModelStep, error) {
	r := turn.r
	r.observe(Event{Kind: EventModelStart, Step: step}, turn.observer)
	turn.resolveFrame()
	compiled, err := r.compileStep(turn.stepPromptInput())
	if err != nil {
		return turnModelStep{}, err
	}
	modelStarted := time.Now()
	generated, nativeCall, reasoningContent, err := r.generate(
		turn.ctx,
		compiled,
		turn.messages,
		turn.activeSpecs,
	)
	channel := ChannelText
	if r.toolCompleter != nil {
		channel = ChannelNative
	}
	if err != nil {
		modelDuration := time.Since(modelStarted).Milliseconds()
		turn.result.Steps = append(turn.result.Steps, Step{
			Number: step, Stage: turn.stage, Channel: channel, Request: compiled.Trace,
			StartedAtMS:     modelStarted.UnixMilli(),
			ModelDurationMS: modelDuration, ModelError: err.Error(),
		})
		r.observe(
			Event{Kind: EventModelDone, Step: step, DurationMS: modelDuration, Err: err},
			turn.observer,
		)
		return turnModelStep{}, err
	}
	current := Step{
		Number:          step,
		Stage:           turn.stage,
		Channel:         channel,
		Request:         compiled.Trace,
		ModelOutput:     generated.Text,
		FinishReason:    generated.FinishReason,
		Usage:           generated.Usage,
		StartedAtMS:     modelStarted.UnixMilli(),
		ModelDurationMS: time.Since(modelStarted).Milliseconds(),
	}
	turn.result.Steps = append(turn.result.Steps, current)
	r.observe(
		Event{Kind: EventModelDone, Step: step, DurationMS: current.ModelDurationMS},
		turn.observer,
	)

	modelAction := turn.postProcessModelOutput(generated.Text, compiled.InjectedPrefix)
	return turnModelStep{
		generated:        generated,
		nativeCall:       nativeCall,
		reasoningContent: reasoningContent,
		modelAction:      modelAction,
	}, nil
}

// stepPromptInput translates the turn state into the compiler input: the
// decision budget and the native tool switches apply to a first decision step
// on the inspect route, and the offered catalog follows the active specs.
func (turn *runnerTurn) stepPromptInput() stepPromptInput {
	r := turn.r
	decision := turn.stage == StageDecision && turn.result.Route == RouteInspect
	return stepPromptInput{
		messages:       turn.messages,
		stage:          turn.stage,
		prefix:         turn.assistantPrefix,
		decisionBudget: decision && turn.successfulToolCalls == 0,
		specs:          turn.activeSpecs,
		offerNative:    decision,
		requireNative: decision && r.toolCompleter != nil && turn.successfulToolCalls == 0 &&
			r.options.NativeFirstCall != "auto",
	}
}

// resolveFrame computes the decision-stage assistant opening from the wire
// spec and the current turn state. It is the single owner of the prefill for a
// decision generation: initialize, tool transitions, rejections and retries no
// longer mutate the prefix, they only change the state the frame reads.
func (turn *runnerTurn) resolveFrame() {
	if turn.stage != StageDecision {
		return
	}
	turn.frame = turn.r.wire.DecisionFrame(wire.DecisionState{
		Inspect:          turn.result.Route == RouteInspect,
		AfterTool:        turn.toolAttempts > 0,
		TerminalComplete: turn.terminalToolCompleted,
	})
	turn.assistantPrefix = turn.frame.Text
}

// postProcessModelOutput restores withheld framing and strips the prefill the
// harness injected, so the parser never records a repair for bytes we supplied
// ourselves. The half-open fake-think form is closed by the model's own ">";
// the closed form is already whole in the prompt and is echoed back verbatim,
// if at all. Format anchors (envelope, fence) are left in place: the protocol
// parser owns their framing.
func (turn *runnerTurn) postProcessModelOutput(modelAction string, injectedPrefix bool) string {
	r := turn.r
	if renderer, ok := r.renderer.(interface{ reconstructOutput(string) string }); ok {
		modelAction = renderer.reconstructOutput(modelAction)
	}
	if !injectedPrefix || turn.assistantPrefix == "" {
		return modelAction
	}
	// The injected prefix is reconstructed for every stage: the decision frame
	// (envelope/fence/fake-think) and the answer-stage opening (<answer>, or
	// "Assistant:" where the renderer accepts it) both rely on it.
	if !strings.HasPrefix(strings.TrimSpace(modelAction), turn.assistantPrefix) {
		modelAction = turn.assistantPrefix + modelAction
	}
	// Only the decision frame owns bytes the harness must strip again. The
	// guard on Text keeps a stale frame from a previous decision step from
	// touching answer-stage output.
	if turn.frame.Strip == "" || turn.frame.Text != turn.assistantPrefix {
		return modelAction
	}
	if trimmed := strings.TrimSpace(modelAction); strings.HasPrefix(trimmed, turn.frame.Strip) {
		modelAction = strings.TrimSpace(strings.TrimPrefix(trimmed, turn.frame.Strip))
	}
	return modelAction
}

func (turn *runnerTurn) parseModelAction(
	step int,
	modelStep *turnModelStep,
) (Action, error) {
	action, err := turn.r.protocol.Parse(
		modelStep.modelAction,
		modelStep.generated.FinishReason,
	)
	if err == nil && action.Type == ActionTypeNoTool && !turn.r.semanticNoTool {
		err = fmt.Errorf("%w: semantic no_tool is disabled", ErrProtocol)
	}
	// Some G1-compatible servers serialize a valid function call in the
	// assistant content instead of the OpenAI tool_calls field. Preserve the
	// recovered call as a native transcript item so the following tool result
	// remains valid Chat Completions history.
	if err == nil &&
		turn.r.toolCompleter != nil &&
		modelStep.nativeCall == nil &&
		action.Type == ActionTypeTool {
		modelStep.nativeCall = &toolchat.ToolCall{
			ID:        fmt.Sprintf("call-content-%d", step),
			Name:      action.Name,
			Arguments: string(action.Arguments),
		}
	}
	stageActionType := action.Type
	if turn.stage == StageAnswer &&
		action.Type == ActionTypeFinal &&
		answerContainsToolFrame(action.Content) {
		stageActionType = ActionTypeTool
	}
	if err == nil && turn.stage == StageAnswer &&
		action.Type == ActionTypeNoTool &&
		firstNonEmpty(action.NoToolAnswer, action.NoToolRationale) == "" {
		// An empty no_tool carries no answer; it takes the protocol retry path
		// instead of committing an empty final.
		err = fmt.Errorf("%w: no_tool in the answer stage must carry a reason or answer", ErrProtocol)
	}
	if err == nil && turn.stage == StageAnswer &&
		stageActionType != ActionTypeFinal && stageActionType != ActionTypeNoTool {
		err = fmt.Errorf(
			"%w: %s action is forbidden during %s",
			ErrStageViolation,
			stageActionType,
			turn.stage,
		)
		turn.currentStep().ActionType = stageActionType
		turn.currentStep().StageViolation = true
	}
	if err == nil {
		turn.retries = 0
		turn.currentStep().ActionType = action.Type
		if turn.currentStep().Channel != ChannelNative {
			// Tolerant-recovery markers describe the text wire only. On the
			// native channel the provider produces structured calls and the
			// harness synthesizes the envelope itself, so counting its
			// recovery as a model protocol violation would mislabel the run.
			turn.currentStep().ProtocolRepaired = action.ProtocolRepaired
			turn.currentStep().ProtocolFailure = action.OriginalProtocolFailure
			turn.currentStep().ProtocolRepairs = append([]wire.Repair(nil), action.Repairs...)
		}
	}
	return action, err
}

func (turn *runnerTurn) acceptSemanticNoTool(action Action, modelStep turnModelStep) bool {
	current := turn.currentStep()
	current.NoToolRationale = action.NoToolRationale
	current.NoToolAnswer = action.NoToolAnswer
	if output := firstNonEmpty(action.NoToolAnswer, action.NoToolRationale); output != "" {
		turn.commitFinalText(output)
		return true
	}
	recorded := turn.r.protocol.RecordAction(action, modelStep.generated.Text)
	// The decision protocol and its no_tool catalog must not leak into the
	// following answer generation. Keep the accepted action in transcript for
	// audit, but replace the system control with the same direct-response
	// control used by an explicit respond route.
	turn.messages = replaceSystemControl(turn.messages, turn.r.responseControl)
	turn.messages = append(
		turn.messages,
		Message{
			Role:             RoleAssistant,
			Content:          recorded,
			ReasoningContent: modelStep.reasoningContent,
		},
		Message{
			Role: RoleUser,
			Content: "The no_tool decision with empty arguments was accepted. No tool will be executed. " +
				"No user-facing reason or answer was provided, and no tool evidence exists. " +
				"Answer the original current task directly in ordinary Markdown now. " +
				"Do not output another function call or repeat the no_tool action.",
		},
	)
	turn.assistantPrefix = "Assistant:"
	turn.frame = wire.Frame{}
	turn.stage = StageAnswer
	return false
}

func firstNonEmpty(values ...string) string {
	for _, value := range values {
		if value = strings.TrimSpace(value); value != "" {
			return value
		}
	}
	return ""
}

// dropNoToolSpec removes the semantic no_tool action from a spec list so the
// catalog (and its instructions) stop offering the exit.
func dropNoToolSpec(specs []ToolSpec) []ToolSpec {
	return slices.DeleteFunc(append([]ToolSpec(nil), specs...), func(spec ToolSpec) bool {
		return spec.Name == SemanticNoToolName
	})
}

// noToolGateRejects reports whether the harness must refuse this no_tool
// action under the configured gate. Rejection is policy, not parsing: the
// action itself is protocol-valid.
func (turn *runnerTurn) noToolGateRejects(action Action) bool {
	switch turn.r.options.NoToolGate {
	case "state":
		return turn.successfulToolCalls == 0
	case "evidence":
		return !turn.reasonCitesEvidence(action)
	default:
		return false
	}
}

// rejectNoTool records the refusal and re-asks with the gate-specific
// correction. It does not consume the protocol retry budget: the emission is
// valid protocol shape, and the step budget bounds repetition.
func (turn *runnerTurn) rejectNoTool(step int, action Action, modelStep turnModelStep) {
	current := turn.currentStep()
	current.ToolRejected = "no_tool_gate"
	if echoed := retryEcho(modelStep.modelAction, nil); strings.TrimSpace(echoed) != "" {
		turn.messages = append(turn.messages, Message{
			Role:             RoleAssistant,
			Content:          echoed,
			ReasoningContent: modelStep.reasoningContent,
		})
	}
	turn.messages = append(turn.messages, Message{
		Role:    RoleUser,
		Content: noToolGateRejectionNote(turn.r.options.NoToolGate),
	})
	turn.r.observe(Event{Kind: EventRetry, Step: step, Err: errors.New("no_tool rejected by " + turn.r.options.NoToolGate + " gate")}, turn.observer)
}

// noToolGateRejectionNote words the harness refusal for each gate mode.
func noToolGateRejectionNote(gate string) string {
	if gate == "state" {
		return ("no_tool was rejected: no tool has run successfully in this task yet, " +
			"so there is no evidence to report. Call a suitable tool first; " +
			"no_tool becomes available only after a tool call succeeds.")
	}
	return ("no_tool was rejected: the reason does not cite any actual Function output of this task. " +
		"Call a tool to obtain evidence first, or cite the Function output verbatim in the reason.")
}

// noToolEvidenceShingle is the normalized-citation length the evidence gate
// requires: 10 consecutive letters/digits/CJK runes copied from a Function
// output. Shorter matches fire on boilerplate; the model's cited values,
// names, and phrases reach it easily.
const noToolEvidenceShingle = 10

// normalizeEvidence keeps only lowercase ASCII letters, digits, and CJK
// runes, so JSON escaping, whitespace, punctuation, and case differences
// between the reason and the raw payload cannot hide a citation.
func normalizeEvidence(text string) string {
	var builder strings.Builder
	for _, r := range strings.ToLower(text) {
		switch {
		case r >= 'a' && r <= 'z', r >= '0' && r <= '9', unicode.Is(unicode.Han, r):
			builder.WriteRune(r)
		}
	}
	return builder.String()
}

// reasonCitesEvidence checks the no_tool reason against every raw tool
// payload of this turn: the reason must reproduce at least one shingle of
// actual Function output content (compressed feedback is a subset of the raw
// payload, so citations of either match).
func (turn *runnerTurn) reasonCitesEvidence(action Action) bool {
	reason := normalizeEvidence(firstNonEmpty(action.NoToolAnswer, action.NoToolRationale))
	runes := []rune(reason)
	if len(runes) < noToolEvidenceShingle {
		return false
	}
	var corpus strings.Builder
	for _, step := range turn.result.Steps {
		if len(step.ToolResult) == 0 {
			continue
		}
		var decoded any
		if json.Unmarshal(step.ToolResult, &decoded) == nil {
			corpus.WriteString(normalizeEvidence(fmt.Sprint(decoded)))
		} else {
			corpus.WriteString(normalizeEvidence(string(step.ToolResult)))
		}
	}
	hay := corpus.String()
	for start := 0; start+noToolEvidenceShingle <= len(runes); start++ {
		if strings.Contains(hay, string(runes[start:start+noToolEvidenceShingle])) {
			return true
		}
	}
	return false
}

// revealNoTool restores the semantic no_tool action (hidden at turn start by
// the state gate) once a tool call has succeeded, and re-renders the control
// so the catalog and instructions carry the exit again.
func (turn *runnerTurn) revealNoTool() {
	r := turn.r
	if len(turn.result.Bundles) > 0 {
		turn.activeSpecs = toolSpecsForBundles(r.toolSpecs, turn.result.Bundles)
	} else {
		turn.activeSpecs = append([]ToolSpec(nil), r.toolSpecs...)
	}
	turn.messages = replaceSystemControl(turn.messages, r.controlForSpecs(turn.activeSpecs))
}

func (turn *runnerTurn) retryProtocolAction(
	step int,
	modelStep turnModelStep,
	err error,
) error {
	current := turn.currentStep()
	current.ProtocolError = err.Error()
	current.ProtocolFailure = ProtocolFailureClassOf(err)
	// AnswerStageLead gives answer-stage tool violations one dedicated re-ask
	// that does not consume the protocol retry budget: the forced answer is
	// the harness's own termination device, so the model gets a strict second
	// chance instead of dying on its first violation (round-1's answer 0-12.5%
	// at step exhaustion).
	if errors.Is(err, ErrStageViolation) && turn.stage == StageAnswer &&
		turn.r.options.AnswerStageLead > 0 && turn.answerViolations == 0 {
		turn.answerViolations++
		turn.r.observe(Event{Kind: EventRetry, Step: step, Err: errors.New("answer-stage violation re-ask")}, turn.observer)
		if echoed := retryEcho(modelStep.modelAction, err); strings.TrimSpace(echoed) != "" {
			turn.messages = append(turn.messages, Message{
				Role:             RoleAssistant,
				Content:          echoed,
				ReasoningContent: modelStep.reasoningContent,
			})
		}
		turn.messages = append(turn.messages, Message{
			Role: RoleUser,
			Content: "Answer the original current task in ordinary Markdown NOW using the Function outputs above. " +
				"This is your final answer; tool calls are forbidden.",
		})
		turn.assistantPrefix = "Assistant:"
		return nil
	}
	if turn.retries >= turn.r.options.ProtocolRetries {
		return err
	}
	turn.retries++
	turn.r.observe(Event{Kind: EventRetry, Step: step, Err: err}, turn.observer)
	echoed := retryEcho(modelStep.modelAction, err)
	if strings.TrimSpace(echoed) != "" {
		retryMessage := Message{
			Role:             RoleAssistant,
			Content:          echoed,
			ReasoningContent: modelStep.reasoningContent,
		}
		if modelStep.nativeCall != nil {
			retryMessage.ToolCalls = []toolchat.ToolCall{*modelStep.nativeCall}
		}
		turn.messages = append(turn.messages, retryMessage)
	}
	correction := turn.r.protocol.Correction(err)
	if errors.Is(err, ErrStageViolation) {
		correction = "Tools are unavailable in the final answer stage. Answer the original task now using existing Tool results. Do not output or request another tool call."
	}
	turn.messages = append(turn.messages, Message{Role: RoleUser, Content: correction})
	return nil
}

func (turn *runnerTurn) finishFinalAction(step int, action Action) (bool, error) {
	if !turn.terminalToolCompleted {
		err := fmt.Errorf(
			"%w: successful %s call required before final answer",
			ErrProtocol,
			turn.r.terminalTool,
		)
		turn.currentStep().ProtocolError = err.Error()
		modelMessage := Message{Role: RoleAssistant, Content: action.Content}
		turn.turnMessages = append(turn.turnMessages, modelMessage)
		turn.messages = append(
			turn.messages,
			modelMessage,
			Message{
				Role: RoleUser,
				Content: fmt.Sprintf(
					"The task is not complete: call %s with the real final answer. Plain text is not scored.",
					turn.r.terminalTool,
				),
			},
		)
		turn.r.observe(Event{Kind: EventRetry, Step: step, Err: err}, turn.observer)
		return false, nil
	}
	if turn.result.Route == RouteInspect && turn.toolAttempts > 0 && !turn.hasToolEvidence {
		return false, noWorkspaceEvidenceError()
	}
	turn.commitFinalText(action.Content)
	return true, nil
}

func (turn *runnerTurn) commitFinalText(content string) {
	turn.result.OriginalOutput = content
	violations := validateAnswer(content)
	committedOutput := content
	if len(violations) > 0 {
		turn.result.AnswerContractRepaired = true
		turn.result.AnswerViolations = make([]string, len(violations))
		for index, violation := range violations {
			turn.result.AnswerViolations[index] = string(violation)
		}
		committedOutput = answerContractFallback(turn.task)
	}
	turn.result.Output = committedOutput
	turn.turnMessages = append(turn.turnMessages, Message{
		Role:    RoleAssistant,
		Content: committedOutput,
	})
	turn.r.commit(turn.turnMessages)
}

func (turn *runnerTurn) retryRespondRoute(step int, modelAction string) error {
	err := fmt.Errorf("%w: tools are unavailable on the respond route", ErrProtocol)
	turn.currentStep().ProtocolError = err.Error()
	if turn.routeViolations >= turn.r.options.ProtocolRetries {
		return err
	}
	turn.routeViolations++
	turn.r.observe(Event{Kind: EventRetry, Step: step, Err: err}, turn.observer)
	turn.messages = append(
		turn.messages,
		Message{Role: RoleAssistant, Content: modelAction},
		Message{
			Role: RoleUser,
			Content: "The route for this turn is respond. Answer directly using " +
				"the conversation and do not call workspace tools.",
		},
	)
	return nil
}

func (turn *runnerTurn) currentStep() *Step {
	return &turn.result.Steps[len(turn.result.Steps)-1]
}
