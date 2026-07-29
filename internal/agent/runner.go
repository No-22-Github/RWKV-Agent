package agent

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

var (
	ErrProtocol = errors.New("agent protocol error")
	ErrMaxSteps = errors.New("agent reached the step limit")
)

type ToolSpec struct {
	Name        string
	Description string
	Arguments   string
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
}

type ControlPromptMode string

const (
	ControlPromptSystem ControlPromptMode = "system"
	ControlPromptInline ControlPromptMode = "inline"
)

type EventKind string

const (
	EventModelStart EventKind = "model_start"
	EventRetry      EventKind = "protocol_retry"
	EventToolStart  EventKind = "tool_start"
	EventToolDone   EventKind = "tool_done"
)

type Event struct {
	Kind EventKind
	Step int
	Tool string
	Err  error
}

type Step struct {
	Number      int
	ModelOutput string
	Tool        string
	ToolError   string
}

type Result struct {
	Output string
	Steps  []Step
}

type Runner struct {
	generator continuation.Generator
	tools     map[string]Tool
	options   Options
	protocol  ActionProtocol
	renderer  PromptRenderer
	control   string
}

func NewRunner(generator continuation.Generator, tools []Tool, options Options) (*Runner, error) {
	if generator == nil {
		return nil, fmt.Errorf("%w: continuation generator is required", continuation.ErrInvalidRequest)
	}
	if options.MaxSteps <= 0 {
		options.MaxSteps = 6
	}
	if options.ProtocolRetries < 0 {
		return nil, fmt.Errorf("%w: protocol retries cannot be negative", continuation.ErrInvalidRequest)
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
	applyGenerationDefaults(&options.Generation)
	if options.DecisionMaxOutputTokens == 0 {
		options.DecisionMaxOutputTokens = 256
	}
	if options.DecisionMaxOutputTokens > options.Generation.MaxOutputTokens {
		options.DecisionMaxOutputTokens = options.Generation.MaxOutputTokens
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
	return &Runner{
		generator: generator,
		tools:     registered,
		options:   options,
		protocol:  options.Protocol,
		renderer:  options.Renderer,
		control:   options.Protocol.Instructions(specs),
	}, nil
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
	if strings.TrimSpace(prompt) == "" {
		return Result{}, fmt.Errorf("%w: prompt is required", continuation.ErrInvalidRequest)
	}
	task := strings.TrimSpace(prompt)
	messages := []Message{
		{Role: RoleSystem, Content: r.control},
		{Role: RoleUser, Content: task},
	}
	if r.options.ControlPrompt == ControlPromptInline {
		messages = []Message{{
			Role:    RoleUser,
			Content: r.control + "\n\nRepository task:\n" + task,
		}}
	}

	result := Result{Steps: make([]Step, 0, r.options.MaxSteps)}
	retries := 0
	seenToolCalls := make(map[string]struct{})
	stage := StageDecision
	assistantPrefix := ""
	for step := 1; step <= r.options.MaxSteps; step++ {
		r.observe(Event{Kind: EventModelStart, Step: step})
		rendered, err := r.renderer.Render(messages)
		if err != nil {
			return result, err
		}
		request := r.options.Generation
		request.Prompt = rendered
		request.Stops = r.protocol.Stops(stage)
		if stage == StageDecision {
			request.MaxOutputTokens = r.options.DecisionMaxOutputTokens
		}
		if assistantPrefix != "" {
			request.Prompt += " " + assistantPrefix
		}
		generated, err := r.generator.Continue(ctx, request, nil)
		if err != nil {
			return result, err
		}
		current := Step{Number: step, ModelOutput: generated.Text}
		result.Steps = append(result.Steps, current)

		modelAction := generated.Text
		if assistantPrefix != "" &&
			!strings.HasPrefix(strings.TrimSpace(modelAction), assistantPrefix) {
			modelAction = assistantPrefix + modelAction
		}
		action, err := r.protocol.Parse(modelAction, generated.FinishReason)
		if err != nil {
			if retries >= r.options.ProtocolRetries {
				return result, err
			}
			retries++
			r.observe(Event{Kind: EventRetry, Step: step, Err: err})
			if strings.TrimSpace(modelAction) != "" {
				messages = append(messages, Message{Role: RoleAssistant, Content: modelAction})
			}
			messages = append(messages, Message{
				Role:    RoleUser,
				Content: r.protocol.Correction(err),
			})
			continue
		}
		retries = 0
		if action.Type == "final" {
			result.Output = action.Content
			return result, nil
		}

		tool, ok := r.tools[action.Name]
		if !ok {
			err = fmt.Errorf("unknown tool %q", action.Name)
		} else {
			r.observe(Event{Kind: EventToolStart, Step: step, Tool: action.Name})
		}
		var value any
		if err == nil {
			callKey := canonicalToolCall(action)
			if _, duplicate := seenToolCalls[callKey]; duplicate {
				err = fmt.Errorf("duplicate tool call rejected")
			} else {
				seenToolCalls[callKey] = struct{}{}
				value, err = tool.Execute(ctx, action.Arguments)
			}
		}
		result.Steps[len(result.Steps)-1].Tool = action.Name
		payload := toolResult{OK: err == nil, Tool: action.Name, Result: value}
		if err != nil {
			payload.Error = err.Error()
			result.Steps[len(result.Steps)-1].ToolError = err.Error()
		}
		encoded, marshalErr := json.Marshal(payload)
		if marshalErr != nil {
			return result, fmt.Errorf("encode tool result: %w", marshalErr)
		}
		r.observe(Event{Kind: EventToolDone, Step: step, Tool: action.Name, Err: err})
		toolContent := r.protocol.FormatToolResult(
			action.Name,
			fmt.Sprintf("call-%d", step),
			string(encoded),
		)
		toolContent = compactToolResult(task, toolContent)
		messages = append(
			messages,
			Message{
				Role:    RoleAssistant,
				Content: r.protocol.RecordAction(action, generated.Text),
			},
			Message{
				Role:       RoleTool,
				Name:       action.Name,
				ToolCallID: fmt.Sprintf("call-%d", step),
				Content:    toolContent,
			},
		)
		if err == nil {
			answerMessages, prefix := r.protocol.PrepareAnswer(task, toolContent)
			if len(answerMessages) == 0 || strings.TrimSpace(prefix) == "" {
				return result, fmt.Errorf("%w: protocol did not prepare an answer stage", ErrProtocol)
			}
			messages = answerMessages
			assistantPrefix = prefix
			stage = StageAnswer
		} else {
			messages = append(messages, Message{
				Role: RoleUser,
				Content: "The tool call failed: " + err.Error() + ". " +
					r.protocol.Correction(err),
			})
			assistantPrefix = ""
			stage = StageDecision
		}
	}
	return result, ErrMaxSteps
}

func canonicalToolCall(action Action) string {
	var arguments bytes.Buffer
	if err := json.Compact(&arguments, action.Arguments); err != nil {
		arguments.Write(action.Arguments)
	}
	return action.Name + "\x00" + arguments.String()
}

func (r *Runner) observe(event Event) {
	if r.options.Observe != nil {
		r.options.Observe(event)
	}
}

type toolResult struct {
	OK     bool   `json:"ok"`
	Tool   string `json:"tool"`
	Result any    `json:"result,omitempty"`
	Error  string `json:"error,omitempty"`
}
