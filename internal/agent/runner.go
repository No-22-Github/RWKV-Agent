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
	if err := applyRunnerDefaults(&options); err != nil {
		return nil, err
	}
	registered, specs, err := registerTools(tools, options)
	if err != nil {
		return nil, err
	}
	toolCompleter, err := nativeCompleterFor(generator, specs)
	if err != nil {
		return nil, err
	}
	thinkingMode := rendererThinkingMode(options.Renderer)
	profile := OptionsProductProfile(options)
	// no_tool is implemented by both product-facing transcripts, so it is not
	// gated on the product pair; the fence prefill experiments still are.
	semanticNoTool := semanticNoToolEnabled(options.Protocol)
	decisionFakeThink := profile.DecisionFakeThink
	closedFakeThink := rendererClosedFakeThink(options.Renderer)
	if semanticNoTool || profile.Experimental() {
		if toolCompleter != nil {
			return nil, fmt.Errorf(
				"%w: semantic no_tool and decision fake-think are text-continuation experiments and cannot be used with native tool calling",
				continuation.ErrInvalidRequest,
			)
		}
		if profile.Experimental() && !profile.Complete() {
			return nil, fmt.Errorf(
				"%w: the fence prefill experiments require the product G1i function protocol and renderer",
				continuation.ErrInvalidRequest,
			)
		}
	}
	responseControl := responseControlPrompt(specs, thinkingMode)
	terminalTool := ""
	if _, offered := registered[options.TerminalTool]; offered {
		terminalTool = options.TerminalTool
	}
	return &Runner{
		generator:         generator,
		toolCompleter:     toolCompleter,
		tools:             registered,
		toolSpecs:         append([]ToolSpec(nil), specs...),
		options:           options,
		protocol:          options.Protocol,
		renderer:          options.Renderer,
		responseControl:   responseControl,
		terminalTool:      terminalTool,
		thinkingMode:      thinkingMode,
		semanticNoTool:    semanticNoTool,
		decisionFakeThink: decisionFakeThink,
		closedFakeThink:   closedFakeThink,
		router:            options.Router,
		toolRouter:        options.ToolRouter,
		toolBundles:       append([]ToolBundle(nil), options.ToolBundles...),
		routeRenderer:     options.RouteRenderer,
	}, nil
}

// applyRunnerDefaults fills the unset knobs and validates the value domains and
// cross-constraints (step budget, control-prompt mode, router exclusivity, and
// output token budgets). It mutates options in place.
func applyRunnerDefaults(options *Options) error {
	if options.MaxSteps <= 0 {
		options.MaxSteps = 6
	}
	if options.MaxSteps < 2 {
		return fmt.Errorf(
			"%w: at least two steps are required to reserve a final answer after tool use",
			continuation.ErrInvalidRequest,
		)
	}
	if options.ProtocolRetries < 0 {
		return fmt.Errorf("%w: protocol retries cannot be negative", continuation.ErrInvalidRequest)
	}
	if options.RouteRetries < 0 {
		return fmt.Errorf("%w: route retries cannot be negative", continuation.ErrInvalidRequest)
	}
	if options.DecisionMaxOutputTokens < 0 {
		return fmt.Errorf(
			"%w: decision output token limit cannot be negative",
			continuation.ErrInvalidRequest,
		)
	}
	if options.ControlPrompt == "" {
		options.ControlPrompt = ControlPromptSystem
	}
	if options.ControlPrompt != ControlPromptSystem && options.ControlPrompt != ControlPromptInline {
		return fmt.Errorf(
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
	if (options.Router != nil || options.ToolRouter != nil) && options.RouteRenderer == nil {
		options.RouteRenderer = RWKVChatRenderer{}
	}
	if options.Router != nil && options.ToolRouter != nil {
		return fmt.Errorf("%w: Router and ToolRouter are mutually exclusive", continuation.ErrInvalidRequest)
	}
	if options.Router != nil || options.ToolRouter != nil {
		routeThinkingMode := rendererThinkingMode(options.RouteRenderer)
		if routeThinkingMode != inference.ThinkingOff {
			return fmt.Errorf(
				"%w: route renderer must use thinking mode %q; got %q",
				continuation.ErrInvalidRequest,
				inference.ThinkingOff,
				routeThinkingMode,
			)
		}
	}
	applyGenerationDefaults(&options.Generation)
	if options.DecisionMaxOutputTokens == 0 {
		options.DecisionMaxOutputTokens = defaultDecisionMaxOutputTokens(options.Protocol)
	}
	if options.DecisionMaxOutputTokens > options.Generation.MaxOutputTokens {
		options.DecisionMaxOutputTokens = options.Generation.MaxOutputTokens
	}
	if options.Router != nil || options.ToolRouter != nil {
		if options.RouteMaxOutputTokens == 0 {
			options.RouteMaxOutputTokens = 16
		}
		if options.RouteMaxOutputTokens < 1 {
			return fmt.Errorf(
				"%w: route output token limit must be positive",
				continuation.ErrInvalidRequest,
			)
		}
		if options.RouteMaxOutputTokens > options.Generation.MaxOutputTokens {
			options.RouteMaxOutputTokens = options.Generation.MaxOutputTokens
		}
	}
	return nil
}

// registerTools validates the tool catalog and builds the registry. When the
// progressive bundle router is configured, the load_tools control tool joins
// the catalog. Specs keep catalog order for order-preserving protocols and are
// sorted by name otherwise.
func registerTools(tools []Tool, options Options) (map[string]Tool, []ToolSpec, error) {
	registered := make(map[string]Tool, len(tools))
	specs := make([]ToolSpec, 0, len(tools))
	for _, tool := range tools {
		if tool == nil {
			return nil, nil, fmt.Errorf("%w: nil tool", continuation.ErrInvalidRequest)
		}
		spec := tool.Spec()
		if spec.Name == "" || spec.Description == "" || spec.Arguments == "" {
			return nil, nil, fmt.Errorf("%w: incomplete tool specification", continuation.ErrInvalidRequest)
		}
		if _, exists := registered[spec.Name]; exists {
			return nil, nil, fmt.Errorf("%w: duplicate tool %q", continuation.ErrInvalidRequest, spec.Name)
		}
		registered[spec.Name] = tool
		specs = append(specs, spec)
	}
	if options.ToolRouter != nil {
		loader, err := newLoadToolsTool(options.ToolBundles)
		if err != nil {
			return nil, nil, err
		}
		if _, exists := registered[loader.Spec().Name]; exists {
			return nil, nil, fmt.Errorf("%w: duplicate tool %q", continuation.ErrInvalidRequest, loader.Spec().Name)
		}
		registered[loader.Spec().Name] = loader
		specs = append(specs, loader.Spec())
	}
	if !preservesToolOrder(options.Protocol) {
		sort.Slice(specs, func(left, right int) bool {
			return specs[left].Name < specs[right].Name
		})
	}
	return registered, specs, nil
}

// nativeCompleterFor adopts the generator's native tool-calling surface when it
// has one and every spec satisfies the native schema contract.
func nativeCompleterFor(generator continuation.Generator, specs []ToolSpec) (toolchat.Completer, error) {
	candidate, ok := generator.(toolchat.Completer)
	if !ok || !candidate.NativeToolCalling() {
		return nil, nil
	}
	for _, spec := range specs {
		if err := validateNativeToolSpec(spec); err != nil {
			return nil, err
		}
	}
	return candidate, nil
}

// responseControlPrompt renders the direct-response control used on the
// respond route and after an accepted abstention. It advertises the read-only
// capabilities so capability questions stay answerable without tools.
func responseControlPrompt(specs []ToolSpec, thinkingMode inference.ThinkingMode) string {
	responseControl := directResponseControl(thinkingMode)
	if len(specs) == 0 {
		return responseControl
	}
	var capabilities strings.Builder
	capabilities.WriteString(
		"\nOnly when the user asks about your capabilities, describe these read-only capabilities:\n",
	)
	for _, spec := range specs {
		fmt.Fprintf(&capabilities, "- %s: %s\n", spec.Name, spec.Description)
	}
	return responseControl + strings.TrimRight(capabilities.String(), "\n")
}

// ProductProfile describes which product text-continuation profile an Options
// value selects, and which of its default-off model-preference experiments are
// enabled. Both the Runner's own configuration validation and eval manifest
// recording read the profile through here, so the two cannot disagree about
// what counts as a product run.
type ProductProfile struct {
	// Protocol and Renderer report whether each half of the pair is the product
	// variant. The experiments below require both.
	Protocol bool
	Renderer bool
	// SemanticNoTool, DecisionFakeThink and DeepToolAnchor are only ever true on
	// a product profile; a benchmark protocol carrying the same field reports
	// false.
	SemanticNoTool    bool
	DecisionFakeThink bool
	DeepToolAnchor    bool
}

// Complete reports whether both halves of the product pair are present.
func (profile ProductProfile) Complete() bool {
	return profile.Protocol && profile.Renderer
}

// Experimental reports whether any default-off model-preference experiment is
// enabled for this run.
func (profile ProductProfile) Experimental() bool {
	return profile.SemanticNoTool || profile.DecisionFakeThink || profile.DeepToolAnchor
}

// ProductProfileOf inspects a protocol and renderer pair. Callers holding an
// Options value should use OptionsProductProfile instead.
func ProductProfileOf(protocol ActionProtocol, renderer PromptRenderer) ProductProfile {
	functionProtocol, _ := protocol.(G1IFunctionProtocol)
	functionRenderer, _ := renderer.(G1IFunctionRenderer)
	profile := ProductProfile{
		Protocol: functionProtocol.Product,
		Renderer: functionRenderer.Product,
	}
	profile.SemanticNoTool = profile.Protocol && functionProtocol.SemanticNoTool
	profile.DecisionFakeThink = profile.Renderer && functionRenderer.DecisionFakeThink
	profile.DeepToolAnchor = profile.Protocol && functionProtocol.DeepToolAnchor
	return profile
}

// Decision-stage output budgets. The right value is a property of the
// transcript, not of the model: the fenced-JSON profile prefills an anchor that
// drops the model straight into a call object, so it needs very little room,
// while the XML envelope lets the model reason before it commits to an action.
//
// Measured on the 60-case product suite (7B, no router): raising the XML budget
// from 96 to 512 moved task success 24/60 -> 33/60 (+9/-0, p=0.0039) and
// protocol validity 82% -> 97%, because at 96 the think block was cut off
// mid-sentence and scored as a malformed envelope. The same change on the
// fenced profile moved it 24/60 -> 22/60, i.e. nothing outside noise. 1024 was
// indistinguishable from 512 (+0/-0), so 512 is the knee.
const (
	DefaultDecisionMaxOutputTokens    = 96
	DefaultXMLDecisionMaxOutputTokens = 512
)

// defaultDecisionMaxOutputTokens picks the decision budget for a protocol when
// the caller did not set one.
func defaultDecisionMaxOutputTokens(protocol ActionProtocol) int {
	if _, ok := protocol.(G1IProtocol); ok {
		return DefaultXMLDecisionMaxOutputTokens
	}
	return DefaultDecisionMaxOutputTokens
}

// semanticNoToolEnabled reports whether the protocol offers the text-only
// no_tool abstention action. Both product-facing transcripts implement it, each
// in its own envelope, so this is deliberately not gated on the product pair.
func semanticNoToolEnabled(protocol ActionProtocol) bool {
	switch typed := protocol.(type) {
	case G1IFunctionProtocol:
		return typed.Product && typed.SemanticNoTool
	case G1IProtocol:
		return typed.SemanticNoTool
	default:
		return false
	}
}

// OptionsProductProfile reports the product profile an Options value selects.
func OptionsProductProfile(options Options) ProductProfile {
	return ProductProfileOf(options.Protocol, options.Renderer)
}

// rendererClosedFakeThink selects the fully closed think prefill. It only
// matters when DecisionFakeThink is also on.
func rendererClosedFakeThink(renderer PromptRenderer) bool {
	typed, ok := renderer.(G1IFunctionRenderer)
	return ok && typed.Product && typed.DecisionFakeThink && typed.ClosedFakeThink
}

func rendererThinkingMode(renderer PromptRenderer) inference.ThinkingMode {
	if chat, ok := renderer.(RWKVChatRenderer); ok {
		return chat.thinkingMode()
	}
	return inference.ThinkingOff
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
