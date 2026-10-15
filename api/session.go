package api

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"regexp"
	"slices"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/product"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/terminal"
)

// Session is an isolated, multi-turn Agent conversation.
type Session struct {
	owner             *Service
	runner            *agent.Runner
	closer            io.Closer
	opMu              sync.Mutex
	mu                sync.RWMutex
	closed            bool
	overlay           *assistanttools.StagedWorkspace
	ownsOverlay       bool
	injectSessionTime bool
}

type webProviderSet struct {
	search assistanttools.WebSearchProvider
	fetch  assistanttools.WebFetchProvider
}

func newSession(
	owner *Service,
	generator continuation.Generator,
	closer io.Closer,
	workspace string,
	status Status,
) (*Session, error) {
	return newSessionAtDepth(owner, generator, closer, workspace, status, 0)
}

func newSessionAtDepth(
	owner *Service,
	generator continuation.Generator,
	closer io.Closer,
	workspace string,
	status Status,
	depth int,
	views ...*assistanttools.StagedWorkspace,
) (*Session, error) {
	var view *assistanttools.StagedWorkspace
	if len(views) > 0 {
		view = views[0]
	}
	ownsOverlay := false
	if view == nil && bashEnabled(ownerConfig(owner), workspace) {
		var err error
		view, err = assistanttools.NewStagedWorkspace(workspace, "")
		if err != nil {
			return nil, err
		}
		ownsOverlay = true
	}
	success := false
	defer func() {
		if !success && ownsOverlay {
			_ = view.Close()
		}
	}()
	tools, err := assembleSessionTools(ownerConfig(owner), owner, workspace, depth, view)
	if err != nil {
		return nil, err
	}
	config := ownerConfig(owner)
	if depth > 0 {
		config.MaxSteps = config.SubagentMaxSteps
	}
	markdownProtocol := config.AgentProtocol != AgentProtocolXML
	runnerOptions := sessionRunnerOptions(config, status, workspace, tools, markdownProtocol, view != nil)
	runnerOptions.SessionContext = sessionTimeContext(config.InjectSessionTime, time.Now())
	runner, err := agent.NewRunner(generator, tools, runnerOptions)
	if err != nil {
		return nil, err
	}
	success = true
	return &Session{owner: owner, runner: runner, closer: closer, overlay: view, ownsOverlay: ownsOverlay, injectSessionTime: config.InjectSessionTime}, nil
}

func sessionTimeContext(enabled bool, startedAt time.Time) string {
	if !enabled {
		return ""
	}
	return product.SessionTimeContext(startedAt)
}

// RestoreStartTime restores the persisted conversation's start time separately
// from the transcript. A zero timestamp leaves the creation-time context intact.
func (s *Session) RestoreStartTime(startedAt time.Time) {
	if startedAt.IsZero() {
		return
	}
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.runner.SetSessionContext(sessionTimeContext(s.injectSessionTime, startedAt))
}

// bashEnabled reports whether the bash tool belongs in a session: it needs the
// config switch, an open workspace and a usable just-bash sidecar. Without the
// sidecar the tool is left out instead of failing session creation.
func bashEnabled(config Config, workspace string) bool {
	if !config.EnableBash || strings.TrimSpace(workspace) == "" {
		return false
	}
	_, err := assistanttools.ResolveBashSidecar("")
	return err == nil
}

// assembleSessionTools builds the tool catalog for one session depth through
// the shared product assembly (the same one the product evaluation uses): file
// reading is always offered, editing only into a staged view (or for previews),
// and web, weather, bash and delegation follow their config switches;
// delegation is only wired at depth 0. The delegation closure compacts each
// child result into a presentation-safe summary. The config is passed
// explicitly so prompts can be previewed for a draft; owner may be nil for such
// previews, in which case nothing executes.
func assembleSessionTools(config Config, owner *Service, workspace string, depth int, views ...*assistanttools.StagedWorkspace) ([]agent.Tool, error) {
	var view *assistanttools.StagedWorkspace
	if len(views) > 0 {
		view = views[0]
	}
	set := product.ToolSet{
		Files: true,
		// Editing is only safe into a staged view; previews list it as well.
		Edit:      view != nil || (owner == nil && workspace != ""),
		Web:       config.EnableWeb,
		Weather:   strings.TrimSpace(config.WeatherBackend) != "",
		Bash:      bashEnabled(config, workspace),
		Subagents: config.EnableSubagents && depth == 0,
	}
	backends := product.Backends{
		Workspace: workspace,
		View:      view,
		Web:       product.WebBackend{TokenCount: product.TokenCounter(config.TokenizerPath)},
		Bash:      product.BashBackend{CatalogOnly: owner == nil},
		Delegation: product.DelegationBackend{
			MaxParallel: config.SubagentMaxParallel,
			Timeout:     time.Duration(config.SubagentTimeoutSeconds) * time.Second,
			Run:         delegateToChildSession(owner, depth+1, view),
		},
	}
	if set.Web {
		web, err := webProvidersFor(owner, config)
		if err != nil {
			return nil, err
		}
		backends.Web.Search, backends.Web.Fetch = web.search, web.fetch
	}
	if backend := strings.TrimSpace(config.WeatherBackend); backend != "" {
		weather, err := assistanttools.NewWeatherProvider(backend)
		if err != nil {
			return nil, err
		}
		backends.Weather = weather
	}
	return product.Tools(set, backends)
}

// delegateToChildSession runs one delegated task on a child session and converts
// the full child trace into the compact per-step summary the parent sees.
func delegateToChildSession(owner *Service, depth int, views ...*assistanttools.StagedWorkspace) func(context.Context, string, func(agent.Event)) (assistanttools.AgentTaskResult, error) {
	return func(ctx context.Context, task string, observer func(agent.Event)) (assistanttools.AgentTaskResult, error) {
		if owner == nil {
			// Preview assemblies wire the catalog without a live service.
			return assistanttools.AgentTaskResult{}, fmt.Errorf("delegation is not available in this context")
		}
		var view *assistanttools.StagedWorkspace
		if len(views) > 0 {
			view = views[0]
		}
		child, childErr := owner.newSessionWithView(ctx, depth, view)
		if childErr != nil {
			return assistanttools.AgentTaskResult{}, childErr
		}
		defer child.Close()
		result, runErr := child.runWithAgentObserver(ctx, task, observer)
		steps := make([]agent.SubagentStep, 0, len(result.Steps))
		for _, step := range result.Steps {
			if strings.TrimSpace(step.Tool) == "" {
				continue
			}
			status := "completed"
			if step.ToolError != "" {
				status = "failed"
			}
			steps = append(steps, agent.SubagentStep{
				Number: step.Number, Tool: step.Tool,
				Arguments: json.RawMessage(step.ToolArguments), Status: status, Error: step.ToolError,
				Retries: internalToolRetries(step.ToolRetries),
			})
		}
		return assistanttools.AgentTaskResult{
			Output:    result.Output,
			Sources:   resultSourceURLs(result),
			Route:     agent.Route(result.Route),
			Bundles:   append([]string(nil), result.Bundles...),
			Steps:     steps,
			StepCount: len(result.Steps),
		}, runErr
	}
}

// sessionRunnerOptions assembles the harness Options for one session through
// the shared product constructor: the Markdown protocol uses the product
// profile with its post-tool reminders, the XML profile carries the thinking
// mode instead. staged says the session writes through a staged workspace.
func sessionRunnerOptions(
	config Config,
	status Status,
	workspace string,
	tools []agent.Tool,
	markdownProtocol bool,
	staged bool,
) agent.Options {
	return product.HarnessOptions(harnessConfig(config, status, workspace, tools, markdownProtocol, staged))
}

// textWireProfile returns value (a wire profile or override) for providers
// that continue raw text, and "" for chat-completions providers: those apply
// their own chat template and call tools natively, so the text-continuation
// wire presets (g1k's no_tool exit, fake-think prefills) do not apply and the
// runner would reject them.
func textWireProfile(config Config, value string) string {
	if config.Provider == ProviderChatCompletions {
		return ""
	}
	return value
}

// harnessConfig converts the App configuration into the api-independent shape
// the shared assembly takes.
func harnessConfig(
	config Config,
	status Status,
	workspace string,
	tools []agent.Tool,
	markdownProtocol bool,
	staged bool,
) product.HarnessConfig {
	return product.HarnessConfig{
		Markdown:          markdownProtocol,
		Profile:           textWireProfile(config, config.Profile),
		Wire:              textWireProfile(config, config.Wire),
		Thinking:          config.Thinking,
		Model:             status.Model,
		StateID:           config.StateID,
		MaxSteps:          config.MaxSteps,
		MaxTokens:         config.MaxTokens,
		DecisionMaxTokens: config.DecisionMaxTokens,
		RouteMaxTokens:    config.RouteMaxTokens,
		TracePromptBytes:  config.TracePromptBytes,
		Sampling: continuation.Sampling{
			Temperature:      float32(config.Temperature),
			TopK:             config.TopK,
			TopP:             float32(config.TopP),
			PresencePenalty:  float32(config.PresencePenalty),
			FrequencyPenalty: float32(config.FrequencyPenalty),
			PenaltyDecay:     float32(config.PenaltyDecay),
		},
		ProgressiveTools:  config.ProgressiveTools,
		SemanticNoTool:    config.SemanticNoTool,
		DeepToolAnchor:    config.DeepToolAnchor,
		DecisionFakeThink: config.DecisionFakeThink,
		CompressFetch:     config.CompressFetch,
		WorkspaceOpen:     workspace != "",
		Staged:            staged,
		UserTaskControl:   config.TaskControl,
		TokenizerPath:     config.TokenizerPath,
		Tools:             tools,
	}
}

func progressiveToolsEnabled(value *bool) bool { return product.ProgressiveEnabled(value) }

func productSwitchEnabled(value *bool) bool { return product.SwitchEnabled(value) }

var resultURLPattern = regexp.MustCompile(`https?://[^\s"\\]+`)

func resultSourceURLs(result Result) []string {
	var sources []string
	for _, step := range result.Steps {
		if step.Tool != "web_search" && step.Tool != "web_fetch" {
			continue
		}
		for _, value := range resultURLPattern.FindAllString(step.ToolResult, -1) {
			value = strings.TrimRight(value, ",.;:)]}")
			if !slices.Contains(sources, value) {
				sources = append(sources, value)
			}
		}
	}
	return sources
}

// Run executes and commits one Agent turn.
func (s *Session) Run(ctx context.Context, prompt string) (Result, error) {
	return s.RunWithObserver(ctx, prompt, nil)
}

// RunWithObserver executes one Agent turn and reports tool-loop progress.
func (s *Session) RunWithObserver(ctx context.Context, prompt string, observer func(Event)) (Result, error) {
	return s.runWithAgentObserver(ctx, prompt, func(event agent.Event) {
		if observer != nil {
			observer(publicEvent(event))
		}
	})
}

func (s *Session) runWithAgentObserver(ctx context.Context, prompt string, observer func(agent.Event)) (Result, error) {
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.mu.RLock()
	closed := s.closed
	s.mu.RUnlock()
	if closed {
		return Result{}, fmt.Errorf("session is closed")
	}
	started := time.Now()
	value, err := s.runner.RunWithObserver(ctx, prompt, observer)
	result := publicResult(value, time.Since(started))
	return result, err
}

// Reset clears committed conversation history.
func (s *Session) Reset() {
	if s == nil || s.runner == nil {
		return
	}
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.mu.RLock()
	closed := s.closed
	s.mu.RUnlock()
	if closed {
		return
	}
	s.runner.Reset()
	s.runner.SetSessionContext(sessionTimeContext(s.injectSessionTime, time.Now()))
}

// History returns a transport-safe copy of the complete committed Harness
// transcript, including native tool calls and tool results.
func (s *Session) History() []ConversationMessage {
	if s == nil || s.runner == nil {
		return nil
	}
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.mu.RLock()
	closed := s.closed
	s.mu.RUnlock()
	if closed {
		return nil
	}
	return publicConversationMessages(s.runner.History())
}

// RestoreHistory replaces the committed transcript of a newly-created
// session. The model provider and workspace remain unchanged.
func (s *Session) RestoreHistory(messages []ConversationMessage) error {
	if s == nil || s.runner == nil {
		return fmt.Errorf("session is not initialized")
	}
	converted, err := internalConversationMessages(messages)
	if err != nil {
		return err
	}
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.mu.RLock()
	closed := s.closed
	s.mu.RUnlock()
	if closed {
		return fmt.Errorf("session is closed")
	}
	return s.runner.RestoreHistory(converted)
}

// Close releases the continuation session.
func (s *Session) Close() error {
	if s == nil {
		return nil
	}
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.mu.Lock()
	if s.closed {
		s.mu.Unlock()
		return nil
	}
	s.closed = true
	s.mu.Unlock()
	if s.owner != nil {
		s.owner.removeSession(s)
	}
	if s.ownsOverlay && s.overlay != nil {
		_ = s.overlay.Close()
	}
	if s.closer != nil {
		return s.closer.Close()
	}
	return nil
}

func publicEvent(event agent.Event) Event {
	value := Event{
		Kind:          EventKind(event.Kind),
		Step:          event.Step,
		ParentStep:    event.ParentStep,
		Tool:          event.Tool,
		Arguments:     string(event.Arguments),
		Route:         string(event.Route),
		Bundles:       append([]string(nil), event.Bundles...),
		SubagentIndex: event.SubagentIndex,
		SubagentTask:  event.SubagentTask,
		DurationMS:    event.DurationMS,
		Attempt:       event.Attempt,
		MaxAttempts:   event.MaxAttempts,
		StatusCode:    event.StatusCode,
		DelayMS:       event.DelayMS,
		Text:          terminal.SanitizeModelText(event.Text),
	}
	if event.Err != nil {
		value.Error = event.Err.Error()
	}
	return value
}

func publicResult(value agent.Result, duration time.Duration) Result {
	result := Result{
		Output:                 terminal.SanitizeModelText(value.Output),
		OriginalOutput:         value.OriginalOutput,
		Route:                  string(value.Route),
		Bundles:                append([]string(nil), value.Bundles...),
		Steps:                  make([]Step, 0, len(value.Steps)),
		AnswerContractRepaired: value.AnswerContractRepaired,
		AnswerViolations:       append([]string(nil), value.AnswerViolations...),
		ForcedAnswerReason:     value.ForcedAnswerReason,
		StartedAtMS:            value.StartedAtMS,
		Duration:               duration,
		DurationMS:             duration.Milliseconds(),
	}
	for _, routeStep := range value.RouteSteps {
		result.RouteSteps = append(result.RouteSteps, RouteStep{
			Attempt:       routeStep.Attempt,
			Request:       publicPromptTrace(routeStep.Request),
			ModelOutput:   routeStep.ModelOutput,
			Route:         string(routeStep.Route),
			Bundles:       append([]string(nil), routeStep.Bundles...),
			ProtocolError: routeStep.ProtocolError,
			FailedClosed:  routeStep.FailedClosed,
			StartedAtMS:   routeStep.StartedAtMS,
			DurationMS:    routeStep.DurationMS,
		})
	}
	for _, step := range value.Steps {
		converted := Step{
			Number:       step.Number,
			Stage:        string(step.Stage),
			Request:      publicPromptTrace(step.Request),
			ModelOutput:  step.ModelOutput,
			FinishReason: string(step.FinishReason),
			Usage: Usage{
				PromptTokens:     step.Usage.PromptTokens,
				CompletionTokens: step.Usage.CompletionTokens,
				CacheReadTokens:  step.Usage.PromptCacheReadTokens,
				CacheWriteTokens: step.Usage.PromptCacheWriteTokens,
				ReasoningTokens:  step.Usage.ReasoningTokens,
			},
			StartedAtMS:      step.StartedAtMS,
			ModelDurationMS:  step.ModelDurationMS,
			FirstTokenAtMS:   step.FirstTokenAtMS,
			ModelError:       step.ModelError,
			ActionType:       step.ActionType,
			Tool:             step.Tool,
			ToolArguments:    string(step.ToolArguments),
			ToolResult:       string(step.ToolResult),
			ToolExecuted:     step.ToolExecuted,
			ToolEvidence:     step.ToolEvidence,
			ToolUnavailable:  step.ToolUnavailable,
			ToolRejected:     step.ToolRejected,
			ToolError:        step.ToolError,
			ProtocolError:    step.ProtocolError,
			ProtocolRepaired: step.ProtocolRepaired,
			StageViolation:   step.StageViolation,
			ToolRetries:      publicToolRetries(step.ToolRetries),
			ToolDurationMS:   step.ToolDurationMS,
			NoToolRationale:  step.NoToolRationale,
			NoToolAnswer:     step.NoToolAnswer,
		}
		for _, subagent := range step.Subagents {
			child := SubagentTrace{
				Index: subagent.Index, Task: subagent.Task, Status: subagent.Status,
				Error: subagent.Error, Route: string(subagent.Route),
				Bundles: append([]string(nil), subagent.Bundles...), StartedAtMS: subagent.StartedAtMS,
				DurationMS: subagent.DurationMS,
				Output:     subagent.Output, Sources: append([]string(nil), subagent.Sources...),
			}
			for _, childStep := range subagent.Steps {
				child.Steps = append(child.Steps, SubagentStep{
					Number: childStep.Number, Tool: childStep.Tool,
					Arguments: string(childStep.Arguments), Status: childStep.Status, Error: childStep.Error,
					Retries: publicToolRetries(childStep.Retries),
				})
			}
			converted.Subagents = append(converted.Subagents, child)
		}
		result.Steps = append(result.Steps, converted)
	}
	return result
}

func publicPromptTrace(value *agent.PromptTrace) *PromptTrace {
	if value == nil {
		return nil
	}
	return &PromptTrace{
		Prompt:          value.Prompt,
		Bytes:           value.Bytes,
		Truncated:       value.Truncated,
		AssistantPrefix: value.AssistantPrefix,
		Stops:           append([]string(nil), value.Stops...),
		MaxOutputTokens: value.MaxOutputTokens,
		ToolsOffered:    append([]string(nil), value.ToolsOffered...),
	}
}

func publicToolRetries(values []agent.ToolRetryTrace) []ToolRetryTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]ToolRetryTrace, 0, len(values))
	for _, value := range values {
		result = append(result, ToolRetryTrace{
			Attempt: value.Attempt, MaxAttempts: value.MaxAttempts,
			StatusCode: value.StatusCode, DelayMS: value.DelayMS,
		})
	}
	return result
}

func internalToolRetries(values []ToolRetryTrace) []agent.ToolRetryTrace {
	if len(values) == 0 {
		return nil
	}
	result := make([]agent.ToolRetryTrace, 0, len(values))
	for _, value := range values {
		result = append(result, agent.ToolRetryTrace{
			Attempt: value.Attempt, MaxAttempts: value.MaxAttempts,
			StatusCode: value.StatusCode, DelayMS: value.DelayMS,
		})
	}
	return result
}

func publicConversationMessages(messages []agent.Message) []ConversationMessage {
	result := make([]ConversationMessage, 0, len(messages))
	for _, message := range messages {
		converted := ConversationMessage{
			Role:             string(message.Role),
			Content:          message.Content,
			ReasoningContent: message.ReasoningContent,
			Name:             message.Name,
			ToolCallID:       message.ToolCallID,
			ToolCalls:        make([]ToolCall, 0, len(message.ToolCalls)),
		}
		for _, call := range message.ToolCalls {
			converted.ToolCalls = append(converted.ToolCalls, ToolCall{
				ID: call.ID, Name: call.Name, Arguments: call.Arguments,
			})
		}
		result = append(result, converted)
	}
	return result
}

func internalConversationMessages(messages []ConversationMessage) ([]agent.Message, error) {
	result := make([]agent.Message, 0, len(messages))
	for index, message := range messages {
		role := agent.MessageRole(message.Role)
		switch role {
		case agent.RoleUser, agent.RoleAssistant, agent.RoleTool:
		default:
			return nil, fmt.Errorf("conversation message %d has unsupported role %q", index, message.Role)
		}
		converted := agent.Message{
			Role:             role,
			Content:          message.Content,
			ReasoningContent: message.ReasoningContent,
			Name:             message.Name,
			ToolCallID:       message.ToolCallID,
			ToolCalls:        make([]toolchat.ToolCall, 0, len(message.ToolCalls)),
		}
		for _, call := range message.ToolCalls {
			converted.ToolCalls = append(converted.ToolCalls, toolchat.ToolCall{
				ID: call.ID, Name: call.Name, Arguments: call.Arguments,
			})
		}
		result = append(result, converted)
	}
	return result, nil
}

// ownerConfig returns the configuration snapshot captured by Configure. It is
// kept in the source status today; defaults preserve the CLI Agent behavior.
func ownerConfig(owner *Service) Config {
	owner.mu.RLock()
	defer owner.mu.RUnlock()
	if owner.config.MaxSteps > 0 {
		return owner.config
	}
	return Config{
		MaxSteps: 6, MaxTokens: 1024, Temperature: 1, TopK: 1, TopP: 1,
		PenaltyDecay: 1, Thinking: "off",
	}
}

func ownerWebProviders(owner *Service, config Config) (*webProviderSet, error) {
	owner.mu.Lock()
	defer owner.mu.Unlock()
	if owner.web != nil {
		return owner.web, nil
	}
	web, err := newWebProviders(config)
	if err != nil {
		return nil, err
	}
	owner.web = web
	return web, nil
}

// webProvidersFor returns the cached provider set for live sessions and a
// fresh uncached set for previews (nil owner): a preview must never write its
// draft credentials into the runtime cache.
func webProvidersFor(owner *Service, config Config) (*webProviderSet, error) {
	if owner != nil {
		return ownerWebProviders(owner, config)
	}
	return newWebProviders(config)
}

// newWebProviders builds the search and fetch providers. A missing key is not
// an error: the tool stays in the catalog and answers with a "not configured"
// message when called, so a connection without keys still opens.
func newWebProviders(config Config) (*webProviderSet, error) {
	set := &webProviderSet{search: product.MissingWebSearch(), fetch: product.MissingWebFetch()}
	if strings.TrimSpace(config.BraveAPIKey) != "" {
		brave, err := assistanttools.NewBraveSearchProvider(assistanttools.BraveConfig{
			APIKey: config.BraveAPIKey, Endpoint: config.BraveEndpoint,
		})
		if err != nil {
			return nil, fmt.Errorf("initialize Brave search: %w", err)
		}
		set.search = brave
	}
	if strings.TrimSpace(config.TavilyAPIKey) != "" {
		tavily, err := assistanttools.NewTavilyFetchProvider(assistanttools.TavilyConfig{
			APIKey: config.TavilyAPIKey, Endpoint: config.TavilyEndpoint,
		})
		if err != nil {
			return nil, fmt.Errorf("initialize Tavily fetch: %w", err)
		}
		set.fetch = tavily
	}
	return set, nil
}
