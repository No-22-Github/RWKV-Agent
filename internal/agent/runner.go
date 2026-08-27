package agent

import (
	"context"
	"errors"
	"fmt"
	"sort"
	"strings"

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

	turn := newRunnerTurn(r, ctx, strings.TrimSpace(prompt), observer)
	if err := turn.initialize(); err != nil {
		return turn.result, err
	}
	return turn.run()
}
