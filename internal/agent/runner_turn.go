package agent

import (
	"context"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

// G1IDecisionFakeThinkPrefix is the exact half-open prefix measured by the G1i
// abstention experiments. The final '>' and any answer bytes must come from the
// model. Whitespace is part of this protocol variable.
const G1IDecisionFakeThinkPrefix = "<think></think"

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
	forceAnswer             bool
	terminalToolCompleted   bool
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
		result:                  Result{Steps: make([]Step, 0, r.options.MaxSteps), Route: RouteInspect},
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
	turn.messages = make([]Message, 0, len(history)+2)
	turn.messages = append(turn.messages, Message{Role: RoleSystem, Content: control})
	turn.messages = append(turn.messages, history...)
	turn.messages = append(turn.messages, Message{Role: RoleUser, Content: turn.task})
	if r.options.ControlPrompt == ControlPromptInline {
		label := "Repository task:"
		if turn.result.Route == RouteRespond {
			label = "Current user message:"
		}
		turn.messages = append([]Message(nil), history...)
		turn.messages = append(turn.messages, Message{
			Role:    RoleUser,
			Content: control + "\n\n" + label + "\n" + turn.task,
		})
	}

	turn.terminalToolCompleted = r.terminalTool == "" || turn.result.Route == RouteRespond
	if (r.router != nil || r.toolRouter != nil) && turn.result.Route == RouteInspect {
		turn.assistantPrefix = r.protocol.ToolCallPrefix()
	}
	return nil
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
		!turn.terminalToolCompleted ||
		(step != turn.r.options.MaxSteps && !turn.forceAnswer) {
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
	if len(answerMessages) == 0 || strings.TrimSpace(prefix) == "" {
		return fmt.Errorf("%w: protocol did not prepare an answer stage", ErrProtocol)
	}
	turn.messages = answerMessages
	turn.assistantPrefix = prefix
	turn.stage = StageAnswer
	if turn.result.ForcedAnswerReason == "" {
		turn.result.ForcedAnswerReason = forcedAnswerStepBudget
	}
	return nil
}

func (turn *runnerTurn) generateModelStep(step int) (turnModelStep, error) {
	r := turn.r
	r.observe(Event{Kind: EventModelStart, Step: step}, turn.observer)
	rendered, err := r.renderer.Render(turn.messages)
	if err != nil {
		return turnModelStep{}, err
	}
	request := r.options.Generation
	request.Prompt = rendered
	request.Stops = r.protocol.Stops(turn.stage)
	if protocol, ok := r.protocol.(interface {
		stopsWithPrefix(GenerationStage, string) []string
	}); ok {
		request.Stops = protocol.stopsWithPrefix(turn.stage, turn.assistantPrefix)
	}
	if turn.stage == StageDecision &&
		turn.result.Route == RouteInspect &&
		turn.successfulToolCalls == 0 {
		request.MaxOutputTokens = r.options.DecisionMaxOutputTokens
	}
	requireNativeTool := r.toolCompleter != nil &&
		turn.stage == StageDecision &&
		turn.result.Route == RouteInspect &&
		turn.successfulToolCalls == 0
	injectedPrefix := false
	if turn.assistantPrefix == "" &&
		r.decisionFakeThink &&
		turn.stage == StageDecision &&
		turn.result.Route == RouteInspect {
		turn.assistantPrefix = G1IDecisionFakeThinkPrefix
	}
	if turn.assistantPrefix != "" && r.toolCompleter == nil {
		request.Prompt, injectedPrefix = appendAssistantPrefix(
			r.renderer,
			request.Prompt,
			turn.assistantPrefix,
		)
	}
	var offered []string
	if turn.stage == StageDecision {
		offered = offeredToolNames(turn.activeSpecs)
	}
	tracePrefix := ""
	if injectedPrefix {
		tracePrefix = turn.assistantPrefix
	}
	if r.toolCompleter != nil {
		request.Prompt = r.nativeTracePrompt(
			turn.messages,
			turn.activeSpecs,
			turn.stage == StageDecision && turn.result.Route == RouteInspect,
			requireNativeTool,
			turn.assistantPrefix,
		)
		tracePrefix = turn.assistantPrefix
	}
	promptTrace := r.tracePrompt(request, tracePrefix, offered)
	modelStarted := time.Now()
	generated, nativeCall, reasoningContent, err := r.generate(
		turn.ctx,
		request,
		turn.messages,
		turn.activeSpecs,
		turn.stage == StageDecision && turn.result.Route == RouteInspect,
		requireNativeTool,
		turn.assistantPrefix,
	)
	if err != nil {
		modelDuration := time.Since(modelStarted).Milliseconds()
		turn.result.Steps = append(turn.result.Steps, Step{
			Number: step, Stage: turn.stage, Request: promptTrace,
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
		Request:         promptTrace,
		ModelOutput:     generated.Text,
		FinishReason:    generated.FinishReason,
		Usage:           generated.Usage,
		ModelDurationMS: time.Since(modelStarted).Milliseconds(),
	}
	turn.result.Steps = append(turn.result.Steps, current)
	r.observe(
		Event{Kind: EventModelDone, Step: step, DurationMS: current.ModelDurationMS},
		turn.observer,
	)

	modelAction := generated.Text
	if renderer, ok := r.renderer.(interface{ reconstructOutput(string) string }); ok {
		modelAction = renderer.reconstructOutput(modelAction)
	}
	if injectedPrefix &&
		!strings.HasPrefix(strings.TrimSpace(modelAction), turn.assistantPrefix) {
		modelAction = turn.assistantPrefix + modelAction
	}
	if injectedPrefix && turn.assistantPrefix == G1IDecisionFakeThinkPrefix {
		completedPrefix := G1IDecisionFakeThinkPrefix + ">"
		if strings.HasPrefix(strings.TrimSpace(modelAction), completedPrefix) {
			modelAction = strings.TrimSpace(strings.TrimPrefix(strings.TrimSpace(modelAction), completedPrefix))
		}
	}
	return turnModelStep{
		generated:        generated,
		nativeCall:       nativeCall,
		reasoningContent: reasoningContent,
		modelAction:      modelAction,
	}, nil
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
	// Some G1i-compatible servers serialize a valid function call in the
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
	if err == nil && turn.stage == StageAnswer && stageActionType != "final" {
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
		turn.currentStep().ProtocolRepaired = action.ProtocolRepaired
		turn.currentStep().ProtocolFailure = action.OriginalProtocolFailure
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

func (turn *runnerTurn) retryProtocolAction(
	step int,
	modelStep turnModelStep,
	err error,
) error {
	current := turn.currentStep()
	current.ProtocolError = err.Error()
	current.ProtocolFailure = ProtocolFailureClassOf(err)
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
