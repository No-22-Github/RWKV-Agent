package agent

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"
	"time"

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
			result.Steps[len(result.Steps)-1].ProtocolFailure = ProtocolFailureClassOf(err)
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
		result.Steps[len(result.Steps)-1].ProtocolFailure = action.OriginalProtocolFailure
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
