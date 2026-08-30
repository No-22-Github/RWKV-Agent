package agent

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type toolExecution struct {
	tool            Tool
	value           any
	err             error
	duplicate       bool
	replayed        bool
	recoveryBlocked bool
	executed        bool
	callKey         string
}

func (turn *runnerTurn) runToolAction(
	step int,
	action Action,
	modelStep turnModelStep,
) (bool, error) {
	turn.toolAttempts++
	turn.assistantPrefix = ""
	current := turn.currentStep()
	current.Tool = action.Name
	current.ToolArguments = append(json.RawMessage(nil), action.Arguments...)

	execution, err := turn.executeTool(step, action)
	if err != nil {
		return false, err
	}
	turn.appendToolTranscript(step, action, modelStep, execution)
	return turn.advanceAfterTool(step, action, execution), nil
}

// toolEventContext attaches the per-step event observer: nested tool events
// gain this step number, retry traces are recorded on the step, and everything
// forwards to the runner observer.
func (turn *runnerTurn) toolEventContext(step int, current *Step) context.Context {
	r := turn.r
	return withToolEventObserver(turn.ctx, func(event Event) {
		if event.Step == 0 {
			event.Step = step
		}
		if event.ParentStep == 0 && (event.Kind != EventToolRetry || event.SubagentIndex != 0) {
			event.ParentStep = step
		}
		if event.Kind == EventToolRetry && event.SubagentIndex == 0 {
			current.ToolRetries = append(current.ToolRetries, ToolRetryTrace{
				Attempt: event.Attempt, MaxAttempts: event.MaxAttempts,
				StatusCode: event.StatusCode, DelayMS: event.DelayMS,
			})
		}
		r.observe(event, turn.observer)
	})
}

// recordCallStreaks advances the identical-call counters the duplicate gates
// and recovery notes read: one streak per protocol family, since the fenced
// transcript counts every repeat while the native path counts resets.
func (turn *runnerTurn) recordCallStreaks(action Action, execution *toolExecution) {
	r := turn.r
	if execution.callKey == turn.lastSameCallKey {
		turn.sameCallStreak++
	} else {
		turn.lastSameCallKey = execution.callKey
		turn.sameCallStreak = 1
	}
	if preservesToolOrder(r.protocol) {
		if execution.callKey == turn.lastNativeCallKey {
			turn.nativeRepeatStreak++
		} else {
			turn.lastNativeCallKey = execution.callKey
			turn.nativeRepeatStreak = 0
		}
	}
}

func (turn *runnerTurn) executeTool(step int, action Action) (toolExecution, error) {
	current := turn.currentStep()
	tool, known := turn.activeTools[action.Name]
	execution := toolExecution{
		tool:    tool,
		callKey: canonicalToolCall(action),
	}
	toolContext := turn.toolEventContext(step, current)
	toolStarted := time.Now()
	turn.recordCallStreaks(action, &execution)
	turn.applyToolGates(step, action, &execution, current, toolContext, known)

	current.ToolExecuted = execution.executed
	if execution.executed {
		current.ToolStartedAtMS = toolStarted.UnixMilli()
		current.ToolDurationMS = time.Since(toolStarted).Milliseconds()
		turn.recordExecutedToolOutcome(action, execution)
	}
	if !execution.executed && execution.err != nil && !execution.duplicate {
		turn.failedToolCallEpochs[execution.callKey] = turn.successfulToolCalls
	}
	turn.recordToolStreak(action, execution)

	if err := turn.recordToolResult(step, action, execution, current); err != nil {
		return execution, err
	}
	return execution, nil
}

// applyToolGates decides the fate of one requested call: provider and rescue
// availability, duplicate protection (with replayable re-execution), the
// consecutive-failure block, and finally execution itself. It returns with
// execution.executed or execution.err set.
func (turn *runnerTurn) applyToolGates(
	step int,
	action Action,
	execution *toolExecution,
	current *Step,
	toolContext context.Context,
	known bool,
) {
	r := turn.r
	tool := execution.tool

	rescueRestricted := turn.rescueMode &&
		(r.terminalTool == "" || action.Name != r.terminalTool)
	if _, unavailable := turn.unavailableTools[action.Name]; unavailable {
		current.ToolRejected = rejectedProviderUnavailable
		current.ToolUnavailable = true
		execution.err = fmt.Errorf("%w: %s", ErrProviderUnavailable, action.Name)
	} else if rescueRestricted {
		current.ToolRejected = rejectedRescueRestricted
		if r.terminalTool == "" {
			execution.err = errors.New(
				"tools are unavailable after repeated identical calls; answer directly",
			)
		} else {
			execution.err = fmt.Errorf(
				"only %s is available after repeated identical calls",
				r.terminalTool,
			)
		}
	} else if revision, exists := turn.seenSuccessfulToolCalls[execution.callKey]; exists &&
		revision == turn.workspaceRevision &&
		!allowsRepeatedToolCalls(r.protocol) {
		// Re-executing a replayable pure read keeps near-greedy decoding moving
		// without weakening duplicate protection for stateful tools.
		if known &&
			tool.Spec().Replayable &&
			r.options.DuplicateReplayLimit > 0 &&
			turn.sameCallStreak <= r.options.DuplicateReplayLimit {
			execution.replayed = true
			execution.executed = true
			r.observe(
				Event{
					Kind: EventToolStart, Step: step, Tool: action.Name,
					Arguments: action.Arguments,
				},
				turn.observer,
			)
			execution.value, execution.err = tool.Execute(toolContext, action.Arguments)
		} else {
			execution.duplicate = true
			current.ToolRejected = rejectedDuplicateCall
			execution.err = errors.New("duplicate tool call rejected")
		}
	} else if epoch, exists := turn.failedToolCallEpochs[execution.callKey]; exists &&
		epoch == turn.successfulToolCalls &&
		!allowsRepeatedToolCalls(r.protocol) {
		execution.duplicate = true
		current.ToolRejected = rejectedDuplicateCall
		execution.err = errors.New("duplicate tool call rejected")
	} else {
		switch {
		case !known:
			current.ToolRejected = rejectedUnknownTool
			if hidden, exists := r.tools[action.Name]; exists && hidden.Spec().Bundle != "" {
				execution.err = fmt.Errorf(
					"tool %q is not active; call load_tools with {\"bundle\":%q}, then retry %q",
					action.Name,
					hidden.Spec().Bundle,
					action.Name,
				)
			} else {
				execution.err = fmt.Errorf("unknown tool %q", action.Name)
			}
		case !allowsRepeatedToolCalls(r.protocol) &&
			action.Name == turn.consecutiveFailedTool &&
			turn.consecutiveToolFailures >= maxConsecutiveToolFailures:
			execution.recoveryBlocked = true
			current.ToolRejected = rejectedFailureLimit
			execution.err = fmt.Errorf(
				"tool %q blocked after %d consecutive failures; choose a different tool or answer",
				action.Name,
				turn.consecutiveToolFailures,
			)
		default:
			execution.executed = true
			r.observe(
				Event{
					Kind: EventToolStart, Step: step, Tool: action.Name,
					Arguments: action.Arguments,
				},
				turn.observer,
			)
			execution.value, execution.err = tool.Execute(toolContext, action.Arguments)
		}
	}
}

// recordToolResult marshals the tool outcome into the step trace and emits the
// tool_done event.
func (turn *runnerTurn) recordToolResult(
	step int,
	action Action,
	execution toolExecution,
	current *Step,
) error {
	payload := toolResult{
		OK:     execution.err == nil,
		Tool:   action.Name,
		Result: execution.value,
	}
	if execution.err != nil {
		payload.Error = execution.err.Error()
		current.ToolError = execution.err.Error()
	}
	if carrier, ok := execution.value.(SubagentTraceCarrier); ok {
		current.Subagents = cloneSubagentTraces(carrier.SubagentTraces())
	}
	encoded, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("encode tool result: %w", err)
	}
	current.ToolResult = append(json.RawMessage(nil), encoded...)
	turn.r.observe(
		Event{
			Kind: EventToolDone, Step: step, Tool: action.Name,
			Arguments: action.Arguments, Err: execution.err,
		},
		turn.observer,
	)
	return nil
}

func (turn *runnerTurn) recordExecutedToolOutcome(
	action Action,
	execution toolExecution,
) {
	current := turn.currentStep()
	toolEvidence := !errors.Is(execution.err, ErrInvalidToolArguments) &&
		!execution.tool.Spec().Control
	current.ToolEvidence = toolEvidence
	if toolEvidence {
		turn.hasToolEvidence = true
	}
	switch {
	case errors.Is(execution.err, ErrProviderUnavailable):
		turn.failedToolCallEpochs[execution.callKey] = turn.successfulToolCalls
		turn.unavailableTools[action.Name] = struct{}{}
		current.ToolRejected = rejectedProviderUnavailable
		current.ToolUnavailable = true
		turn.unverified = appendUnique(turn.unverified, action.Name)
		turn.forceAnswer = true
	case errors.Is(execution.err, ErrInvalidToolArguments):
		turn.failedToolCallEpochs[execution.callKey] = turn.successfulToolCalls
	case execution.err == nil:
		turn.seenSuccessfulToolCalls[execution.callKey] = turn.workspaceRevision
		delete(turn.failedToolCallEpochs, execution.callKey)
		if execution.tool.Spec().MutatesWorkspace && workspaceChanged(execution.value) {
			turn.workspaceRevision++
		}
		turn.consecutiveFailedTool = ""
		turn.consecutiveToolFailures = 0
	case action.Name == turn.consecutiveFailedTool:
		turn.failedToolCallEpochs[execution.callKey] = turn.successfulToolCalls
		turn.consecutiveToolFailures++
	default:
		turn.failedToolCallEpochs[execution.callKey] = turn.successfulToolCalls
		turn.consecutiveFailedTool = action.Name
		turn.consecutiveToolFailures = 1
	}
}

func (turn *runnerTurn) recordToolStreak(action Action, execution toolExecution) {
	if execution.executed && execution.err == nil {
		if action.Name == turn.lastSameToolName {
			turn.sameToolSuccessStreak++
		} else {
			turn.lastSameToolName = action.Name
			turn.sameToolSuccessStreak = 1
		}
		return
	}
	turn.sameToolSuccessStreak = 0
}

func (turn *runnerTurn) appendToolTranscript(
	step int,
	action Action,
	modelStep turnModelStep,
	execution toolExecution,
) {
	r := turn.r
	callID := fmt.Sprintf("call-%d", step)
	if modelStep.nativeCall != nil {
		callID = modelStep.nativeCall.ID
	}
	toolContent := r.protocol.FormatToolResult(
		action.Name,
		callID,
		string(turn.currentStep().ToolResult),
	)
	if preservesToolOrder(r.protocol) {
		switch {
		case execution.replayed:
			toolContent += "\nNOTE: " + duplicateReplayNote(
				turn.sameCallStreak,
				r.options.MaxSteps-step,
				r.terminalTool,
			)
		case execution.duplicate:
			toolContent += "\nRECOVERY: " + duplicateRejectionNote(
				turn.sameCallStreak,
				r.options.MaxSteps-step,
				r.terminalTool,
			)
		case execution.err != nil:
			toolContent += "\nRECOVERY: " + toolFailureReminder(
				action.Name,
				execution.err,
				execution.recoveryBlocked,
				turn.activeTools,
			)
		}
	}
	if allowsRepeatedToolCalls(r.protocol) &&
		turn.nativeRepeatStreak >= 1 &&
		action.Name != r.terminalTool {
		toolContent += "\nNOTE: identical tool call repeated. Do not call it again. Take the next step (other file, compute, run_tests, or submit)."
		if turn.nativeRepeatStreak >= 2 {
			toolContent += "\nNOTE2: stop repeating. If you already have the answer, call submit now."
		}
	}
	if execution.err == nil &&
		!execution.replayed &&
		action.Name != r.terminalTool &&
		r.options.PostToolHook != nil {
		hook := r.options.PostToolHook(
			action.Name,
			action.Arguments,
			execution.value,
			nil,
		)
		if hook = strings.TrimSpace(hook); hook != "" {
			toolContent += "\n" + hook
		}
	}
	toolContent = compactToolResult(turn.task, toolContent)
	recordedAction := r.protocol.RecordAction(action, modelStep.generated.Text)
	var recordedToolCalls []toolchat.ToolCall
	if modelStep.nativeCall != nil {
		recordedToolCalls = []toolchat.ToolCall{*modelStep.nativeCall}
	}
	assistantMessage := Message{
		Role:             RoleAssistant,
		Content:          recordedAction,
		ReasoningContent: modelStep.reasoningContent,
		ToolCalls:        recordedToolCalls,
	}
	toolMessage := Message{
		Role:       RoleTool,
		Name:       action.Name,
		ToolCallID: callID,
		Content:    toolContent,
	}
	turn.turnMessages = append(turn.turnMessages, assistantMessage, toolMessage)
	turn.messages = append(turn.messages, assistantMessage, toolMessage)
}

func (turn *runnerTurn) advanceAfterTool(
	step int,
	action Action,
	execution toolExecution,
) bool {
	r := turn.r
	if execution.err == nil && turn.rescueMode && action.Name == r.terminalTool {
		turn.result.RescueSubmitted = true
	}
	if execution.err == nil &&
		action.Name == r.terminalTool &&
		r.options.EndOnTerminalTool {
		output := terminalToolOutput(action, execution.value)
		turn.result.OriginalOutput = output
		turn.result.Output = output
		r.commit(turn.turnMessages)
		return true
	}
	if execution.err == nil {
		turn.successfulToolCalls++
		if execution.tool.Spec().Control {
			selection, ok := execution.value.(loadToolsResult)
			if ok && !containsString(turn.result.Bundles, selection.Bundle) {
				turn.result.Bundles = append(turn.result.Bundles, selection.Bundle)
				turn.activeSpecs = toolSpecsForBundles(r.toolSpecs, turn.result.Bundles)
				turn.activeTools = toolsForSpecs(r.tools, turn.activeSpecs)
				turn.messages = replaceSystemControl(
					turn.messages,
					r.controlForSpecs(turn.activeSpecs),
				)
			}
		}
		if action.Name == r.terminalTool {
			turn.terminalToolCompleted = true
		}
		if reminder := strings.TrimSpace(
			r.postToolReminder(turn.terminalToolCompleted),
		); reminder != "" {
			turn.messages = append(
				turn.messages,
				Message{Role: RoleUser, Content: reminder},
			)
		}
	} else if execution.duplicate {
		if turn.terminalToolCompleted {
			turn.forceAnswer = true
			turn.result.ForcedAnswerReason = forcedAnswerDuplicateCall
		}
		if !preservesToolOrder(r.protocol) {
			turn.messages = append(turn.messages, Message{
				Role: RoleUser,
				Content: r.duplicateToolReminder(
					turn.successfulToolCalls > 0,
					turn.terminalToolCompleted,
				),
			})
		}
	} else if !preservesToolOrder(r.protocol) {
		turn.messages = append(turn.messages, Message{
			Role: RoleUser,
			Content: toolFailureReminder(
				action.Name,
				execution.err,
				execution.recoveryBlocked,
				turn.activeTools,
			),
		})
	}

	if errors.Is(execution.err, ErrProviderUnavailable) &&
		!turn.terminalToolCompleted &&
		r.terminalTool != "" &&
		!turn.rescueMode {
		turn.rescueMode = true
		turn.result.RescueAttempted = true
		turn.result.ForcedAnswerReason = forcedAnswerProviderFailure
		turn.messages = r.enterRescueMode(
			turn.messages,
			fmt.Sprintf("the %s provider is unavailable", action.Name),
			r.options.MaxSteps-step,
		)
		turn.activeSpecs = r.rescueToolSpecs()
		turn.activeTools = toolsForSpecs(r.tools, turn.activeSpecs)
	}
	loopStuck := r.options.DuplicateRescueThreshold > 0 &&
		turn.sameCallStreak >= r.options.DuplicateRescueThreshold &&
		(execution.duplicate ||
			execution.replayed ||
			(execution.err != nil && !execution.executed))
	spiralStuck := r.options.SameToolRescueLimit > 0 &&
		turn.sameToolSuccessStreak >= r.options.SameToolRescueLimit
	if !turn.rescueMode &&
		preservesToolOrder(r.protocol) &&
		!allowsRepeatedToolCalls(r.protocol) &&
		(loopStuck || spiralStuck) {
		turn.rescueMode = true
		turn.result.RescueAttempted = true
		reason := fmt.Sprintf(
			"the same call was repeated %d times",
			turn.sameCallStreak,
		)
		if spiralStuck {
			reason = fmt.Sprintf(
				"the same tool ran successfully %d times in a row with no other tool",
				turn.sameToolSuccessStreak,
			)
		}
		turn.messages = r.enterRescueMode(
			turn.messages,
			reason,
			r.options.MaxSteps-step,
		)
		turn.activeSpecs = r.rescueToolSpecs()
		turn.activeTools = toolsForSpecs(r.tools, turn.activeSpecs)
	}
	if turn.result.Route == RouteInspect && !turn.terminalToolCompleted {
		turn.assistantPrefix = r.protocol.ToolCallPrefix()
	}
	return false
}
