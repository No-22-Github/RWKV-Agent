package api

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"regexp"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/terminal"
)

// Session is an isolated, multi-turn Agent conversation.
type Session struct {
	owner  *Service
	runner *agent.Runner
	closer io.Closer
	opMu   sync.Mutex
	mu     sync.RWMutex
	closed bool
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
) (*Session, error) {
	tools, err := assembleSessionTools(ownerConfig(owner), owner, workspace, depth)
	if err != nil {
		return nil, err
	}
	config := ownerConfig(owner)
	if depth > 0 {
		config.MaxSteps = config.SubagentMaxSteps
	}
	markdownProtocol := config.AgentProtocol != AgentProtocolXML
	runnerOptions := sessionRunnerOptions(config, status, workspace, tools, markdownProtocol)
	runner, err := agent.NewRunner(generator, tools, runnerOptions)
	if err != nil {
		return nil, err
	}
	return &Session{owner: owner, runner: runner, closer: closer}, nil
}

// assembleSessionTools builds the tool catalog for one session depth: workspace
// and local tools are always offered, web and delegation tools follow their
// config switches, and delegation is only wired at depth 0. The delegation
// closure compacts each child result into a presentation-safe summary. The
// config is passed explicitly so prompts can be previewed for a draft; owner
// may be nil for such previews, in which case nothing executes.
func assembleSessionTools(config Config, owner *Service, workspace string, depth int) ([]agent.Tool, error) {
	// 文件工具始终在目录里（模型能感知该能力）；未打开工作区时它们由
	// 不可用解析器支撑，调用会返回"请先打开工作区"的明确提示。
	workspaceTools, err := agent.WorkspaceTools(workspace)
	if err != nil {
		return nil, fmt.Errorf("initialize workspace tools: %w", err)
	}
	tools := workspaceTools
	localTools, err := assistanttools.LocalTools(assistanttools.Options{Workspace: workspace})
	if err != nil {
		return nil, fmt.Errorf("initialize local tools: %w", err)
	}
	tools = append(tools, localTools...)
	if config.EnableWeb {
		web, providerErr := webProvidersFor(owner, config)
		if providerErr != nil {
			return nil, providerErr
		}
		tools = append(tools, assistanttools.WebTools(assistanttools.WebOptions{
			Search: web.search, Fetch: web.fetch,
		})...)
	}
	if config.EnableSubagents && depth == 0 {
		tools = append(tools, assistanttools.DelegationTools(assistanttools.DelegationOptions{
			MaxParallel: config.SubagentMaxParallel,
			Timeout:     time.Duration(config.SubagentTimeoutSeconds) * time.Second,
			Run:         delegateToChildSession(owner, depth+1),
		})...)
	}
	return tools, nil
}

// delegateToChildSession runs one delegated task on a child session and converts
// the full child trace into the compact per-step summary the parent sees.
func delegateToChildSession(owner *Service, depth int) func(context.Context, string, func(agent.Event)) (assistanttools.AgentTaskResult, error) {
	return func(ctx context.Context, task string, observer func(agent.Event)) (assistanttools.AgentTaskResult, error) {
		if owner == nil {
			// Preview assemblies wire the catalog without a live service.
			return assistanttools.AgentTaskResult{}, fmt.Errorf("delegation is not available in this context")
		}
		child, childErr := owner.newSession(ctx, depth)
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

// sessionRunnerOptions assembles the harness Options for one session: the
// Markdown protocol uses the product profile with its post-tool reminders, the
// XML profile carries the thinking mode instead.
func sessionRunnerOptions(
	config Config,
	status Status,
	workspace string,
	tools []agent.Tool,
	markdownProtocol bool,
) agent.Options {
	var postToolHook func(string, json.RawMessage, any, error) string
	if markdownProtocol {
		// The Markdown protocol answers directly (plain Markdown or fenced
		// code) once it has enough evidence; there is no submit gate, so the
		// model never has to pack the user-visible answer into a JSON tool
		// argument (which is where Markdown fences get lost).
		postToolHook = func(name string, _ json.RawMessage, _ any, _ error) string {
			switch name {
			case "web_fetch":
				return "NEXT: Use the fetched page content above and answer the user directly now. Do not call web_search or web_fetch again."
			case "spawn_agents":
				return "NEXT: Synthesize the ordered child results above and answer the user directly now. Do not spawn another batch."
			default:
				return ""
			}
		}
	}
	toolBundles := agent.EnabledToolBundles(tools, agent.DefaultToolBundles())
	taskControl := ""
	if workspace == "" {
		taskControl = "工作区未打开：本地文件工具（list_files/read_file/search_text）需要先打开一个工作区才能使用。如果用户需要读取或搜索本地文件，请直接告诉用户先在应用中打开一个工作区（例如“打开工作区”按钮），不要尝试调用任何文件工具，也不要假装读取了文件。"
	}
	// The user's personal contract rides in the same Task-specific block,
	// after any system hint, and reaches the prompt verbatim.
	if user := strings.TrimSpace(config.TaskControl); user != "" {
		if taskControl != "" {
			taskControl += "\n\n"
		}
		taskControl += user
	}
	generation := continuation.Request{
		Model:           status.Model,
		MaxOutputTokens: config.MaxTokens,
		Sampling: continuation.Sampling{
			Temperature:      float32(config.Temperature),
			TopK:             config.TopK,
			TopP:             float32(config.TopP),
			PresencePenalty:  float32(config.PresencePenalty),
			FrequencyPenalty: float32(config.FrequencyPenalty),
			PenaltyDecay:     float32(config.PenaltyDecay),
		},
	}
	tracePromptBytes := agent.DefaultTracePromptBytes
	if config.TracePromptBytes != nil {
		tracePromptBytes = *config.TracePromptBytes
	}
	if markdownProtocol {
		return agent.ProductHarnessOptions(agent.ProductHarnessConfig{
			MaxSteps:                 config.MaxSteps,
			DecisionMaxOutputTokens:  min(config.DecisionMaxTokens, config.MaxTokens),
			RouteMaxOutputTokens:     min(config.RouteMaxTokens, config.MaxTokens),
			TracePromptBytes:         tracePromptBytes,
			DuplicateReplayLimit:     agent.ProductDuplicateReplayLimit,
			DuplicateRescueThreshold: agent.ProductDuplicateRescueThreshold,
			SameToolRescueLimit:      agent.ProductSameToolRescueLimit,
			Generation:               generation,
			ProgressiveTools:         progressiveToolsEnabled(config.ProgressiveTools),
			ToolBundles:              toolBundles,
			SemanticNoTool:           productSwitchEnabled(config.SemanticNoTool),
			DecisionFakeThink:        config.DecisionFakeThink,
			DeepToolAnchor:           productSwitchEnabled(config.DeepToolAnchor),
			TaskControl:              taskControl,
			PostToolHook:             postToolHook,
		})
	}
	return agent.XMLHarnessOptions(agent.XMLHarnessConfig{
		MaxSteps:                 config.MaxSteps,
		DecisionMaxOutputTokens:  min(config.DecisionMaxTokens, config.MaxTokens),
		RouteMaxOutputTokens:     min(config.RouteMaxTokens, config.MaxTokens),
		TracePromptBytes:         tracePromptBytes,
		DuplicateReplayLimit:     agent.ProductDuplicateReplayLimit,
		DuplicateRescueThreshold: agent.ProductDuplicateRescueThreshold,
		SameToolRescueLimit:      agent.ProductSameToolRescueLimit,
		Generation:               generation,
		ProgressiveTools:         progressiveToolsEnabled(config.ProgressiveTools),
		ToolBundles:              toolBundles,
		TaskControl:              taskControl,
		ThinkingMode:             inference.ThinkingMode(config.Thinking),
	})
}

func progressiveToolsEnabled(value *bool) bool {
	return value != nil && *value
}

// productSwitchEnabled resolves a tri-state Markdown-profile switch. Unset is
// on for semantic no_tool and the deep anchor; XML normalization supplies false.
func productSwitchEnabled(value *bool) bool {
	return value == nil || *value
}

var resultURLPattern = regexp.MustCompile(`https?://[^\s"\\]+`)

func resultSourceURLs(result Result) []string {
	var sources []string
	for _, step := range result.Steps {
		if step.Tool != "web_search" && step.Tool != "web_fetch" {
			continue
		}
		for _, value := range resultURLPattern.FindAllString(step.ToolResult, -1) {
			value = strings.TrimRight(value, ",.;:)]}")
			if !containsSource(sources, value) {
				sources = append(sources, value)
			}
		}
	}
	return sources
}

func containsSource(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
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

func newWebProviders(config Config) (*webProviderSet, error) {
	brave, err := assistanttools.NewBraveSearchProvider(assistanttools.BraveConfig{
		APIKey: config.BraveAPIKey, Endpoint: config.BraveEndpoint,
	})
	if err != nil {
		return nil, fmt.Errorf("initialize Brave search: %w", err)
	}
	tavily, err := assistanttools.NewTavilyFetchProvider(assistanttools.TavilyConfig{
		APIKey: config.TavilyAPIKey, Endpoint: config.TavilyEndpoint,
	})
	if err != nil {
		return nil, fmt.Errorf("initialize Tavily fetch: %w", err)
	}
	return &webProviderSet{search: brave, fetch: tavily}, nil
}
