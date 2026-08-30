package agent

import (
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// routeAssistantPrefix is the framing prefix every route generation is
// anchored on: the route protocol parses only output that opens with it.
const routeAssistantPrefix = "<route>"

// CompiledPrompt is the finished model input for one generation: the framed
// continuation request plus the framing metadata the prompt trace, the output
// post-processing, and the native Chat Completions path still need. Every
// model call in the Runner goes through a compiler so the transcript framing
// is decided in one place instead of being re-assembled at each call site.
type CompiledPrompt struct {
	// Request is the exact continuation request for this call. On the native
	// tool path Prompt holds the JSON request trace only; the real input
	// travels as Chat Completions messages.
	Request continuation.Request
	// Trace records the framed request for the run transcript.
	Trace *PromptTrace
	// ToolsOffered records the active tool catalog for the prompt trace.
	ToolsOffered []string
	// Prefix is the effective assistant prefix of this call. On the text path
	// an injected prefix is already part of Request.Prompt; on the native path
	// it travels inside the Chat Completions request instead.
	Prefix string
	// InjectedPrefix reports whether the prefix became part of Request.Prompt,
	// so the output post-processing knows which framing bytes to strip again.
	InjectedPrefix bool
	// OfferNative and RequireNative are the native tool-calling switches of
	// this call; they are always false on the text-continuation path.
	OfferNative   bool
	RequireNative bool
}

// stepPromptInput collects the per-step state the decision/answer compiler
// needs beyond the immutable run profile. The turn owns the policy of when a
// decision budget or a native tool call applies; the compiler turns that
// policy into the exact request bytes.
type stepPromptInput struct {
	messages []Message
	stage    GenerationStage
	// prefix is the resolved assistant prefix; empty frames no prefix.
	prefix string
	// decisionBudget applies the protocol's decision output budget.
	decisionBudget bool
	specs          []ToolSpec
	// offerNative and requireNative mirror the native tool-calling switches.
	offerNative   bool
	requireNative bool
}

// compileStep frames one decision or answer generation: rendering, stop
// sequences, output budget, prefix injection, and the native request trace.
func (r *Runner) compileStep(input stepPromptInput) (CompiledPrompt, error) {
	rendered, err := r.renderer.Render(input.messages)
	if err != nil {
		return CompiledPrompt{}, err
	}
	request := r.options.Generation
	request.Prompt = rendered
	request.Stops = r.protocol.Stops(input.stage)
	if typed, ok := r.protocol.(interface {
		stopsWithPrefix(GenerationStage, string) []string
	}); ok {
		request.Stops = typed.stopsWithPrefix(input.stage, input.prefix)
	}
	if input.decisionBudget {
		request.MaxOutputTokens = r.options.DecisionMaxOutputTokens
	}
	compiled := CompiledPrompt{
		Prefix:        input.prefix,
		OfferNative:   input.offerNative,
		RequireNative: input.requireNative,
	}
	if input.stage == StageDecision {
		compiled.ToolsOffered = offeredToolNames(input.specs)
	}
	if input.prefix != "" && r.toolCompleter == nil {
		request.Prompt, compiled.InjectedPrefix = appendAssistantPrefix(
			r.renderer,
			request.Prompt,
			input.prefix,
		)
	}
	tracePrefix := ""
	if compiled.InjectedPrefix {
		tracePrefix = input.prefix
	}
	if r.toolCompleter != nil {
		request.Prompt = r.nativeTracePrompt(
			input.messages,
			input.specs,
			input.offerNative,
			input.requireNative,
			input.prefix,
		)
		tracePrefix = input.prefix
	}
	compiled.Request = request
	compiled.Trace = r.tracePrompt(request, tracePrefix, compiled.ToolsOffered)
	return compiled, nil
}

// compileRoute frames one route generation. The route stage requires its
// prefix: a renderer that cannot inject it fails the call instead of sending
// an unanchored route prompt.
func (r *Runner) compileRoute(messages []Message, stops []string) (CompiledPrompt, error) {
	rendered, err := r.routeRenderer.Render(messages)
	if err != nil {
		return CompiledPrompt{}, err
	}
	request := r.options.Generation
	request.Prompt, err = appendRequiredAssistantPrefix(
		r.routeRenderer,
		rendered,
		routeAssistantPrefix,
	)
	if err != nil {
		return CompiledPrompt{}, err
	}
	request.Stops = append([]string(nil), stops...)
	request.MaxOutputTokens = r.options.RouteMaxOutputTokens
	compiled := CompiledPrompt{Prefix: routeAssistantPrefix}
	if r.toolCompleter != nil {
		request.Prompt = r.nativeTracePrompt(messages, nil, false, false, routeAssistantPrefix)
	}
	compiled.Request = request
	compiled.Trace = r.tracePrompt(request, routeAssistantPrefix, nil)
	return compiled, nil
}
