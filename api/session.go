package api

import (
	"context"
	"fmt"
	"io"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
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

func newSession(
	owner *Service,
	generator continuation.Generator,
	closer io.Closer,
	workspace string,
	status Status,
) (*Session, error) {
	tools, err := agent.WorkspaceTools(workspace)
	if err != nil {
		return nil, fmt.Errorf("initialize workspace tools: %w", err)
	}
	localTools, err := assistanttools.LocalTools(assistanttools.Options{Workspace: workspace})
	if err != nil {
		return nil, fmt.Errorf("initialize local tools: %w", err)
	}
	tools = append(tools, localTools...)
	config := ownerConfig(owner)
	runner, err := agent.NewRunner(generator, tools, agent.Options{
		MaxSteps:                config.MaxSteps,
		ProtocolRetries:         1,
		DecisionMaxOutputTokens: min(96, config.MaxTokens),
		ControlPrompt:           agent.ControlPromptSystem,
		Protocol:                agent.G1IProtocol{},
		Renderer: agent.RWKVChatRenderer{
			ThinkingMode: inference.ThinkingMode(config.Thinking),
		},
		DuplicateReplayLimit:     2,
		DuplicateRescueThreshold: 3,
		SameToolRescueLimit:      8,
		TracePromptBytes:         agent.DefaultTracePromptBytes,
		Generation: continuation.Request{
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
		},
	})
	if err != nil {
		return nil, err
	}
	return &Session{owner: owner, runner: runner, closer: closer}, nil
}

// Run executes and commits one Agent turn.
func (s *Session) Run(ctx context.Context, prompt string) (Result, error) {
	return s.RunWithObserver(ctx, prompt, nil)
}

// RunWithObserver executes one Agent turn and reports tool-loop progress.
func (s *Session) RunWithObserver(ctx context.Context, prompt string, observer func(Event)) (Result, error) {
	s.opMu.Lock()
	defer s.opMu.Unlock()
	s.mu.RLock()
	closed := s.closed
	s.mu.RUnlock()
	if closed {
		return Result{}, fmt.Errorf("session is closed")
	}
	started := time.Now()
	value, err := s.runner.RunWithObserver(ctx, prompt, func(event agent.Event) {
		if observer != nil {
			observer(publicEvent(event))
		}
	})
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
		Kind:  EventKind(event.Kind),
		Step:  event.Step,
		Tool:  event.Tool,
		Route: string(event.Route),
	}
	if event.Err != nil {
		value.Error = event.Err.Error()
	}
	return value
}

func publicResult(value agent.Result, duration time.Duration) Result {
	result := Result{
		Output:     terminal.SanitizeModelText(value.Output),
		Route:      string(value.Route),
		Steps:      make([]Step, 0, len(value.Steps)),
		Duration:   duration,
		DurationMS: duration.Milliseconds(),
	}
	for _, step := range value.Steps {
		result.Steps = append(result.Steps, Step{
			Number:        step.Number,
			Stage:         string(step.Stage),
			ModelOutput:   step.ModelOutput,
			FinishReason:  string(step.FinishReason),
			ActionType:    step.ActionType,
			Tool:          step.Tool,
			ToolArguments: string(step.ToolArguments),
			ToolResult:    string(step.ToolResult),
			ToolExecuted:  step.ToolExecuted,
			ToolError:     step.ToolError,
		})
	}
	return result
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
