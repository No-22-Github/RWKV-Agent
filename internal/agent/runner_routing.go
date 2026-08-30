package agent

import (
	"context"
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// tracePrompt captures a generation request. The prompt is recorded verbatim up
// to the configured budget so a greedy output change can be attributed to the
// exact input that produced it.
func (r *Runner) tracePrompt(
	request continuation.Request,
	assistantPrefix string,
	toolsOffered []string,
) *PromptTrace {
	budget := r.options.TracePromptBytes
	if budget == 0 {
		return nil
	}
	prompt := request.Prompt
	trace := &PromptTrace{
		Bytes:           len(prompt),
		AssistantPrefix: assistantPrefix,
		MaxOutputTokens: request.MaxOutputTokens,
		ToolsOffered:    toolsOffered,
	}
	if len(request.Stops) > 0 {
		trace.Stops = append([]string{}, request.Stops...)
	}
	if budget > 0 && len(prompt) > budget {
		// Keep the head and tail: the head carries the control prompt and tool
		// list, the tail carries the most recent observation and the prefix.
		head := budget / 2
		tail := budget - head
		prompt = prompt[:head] + "\n...[trace truncated]...\n" + prompt[len(prompt)-tail:]
		trace.Truncated = true
	}
	trace.Prompt = prompt
	return trace
}

// offeredToolNames lists the tools present in this run's registry. A change to
// the tool list changes every decision prompt, which under greedy decoding can
// move unrelated cases; recording it makes that attributable.
func offeredToolNames(specs []ToolSpec) []string {
	if len(specs) == 0 {
		return nil
	}
	names := make([]string, 0, len(specs))
	for _, spec := range specs {
		names = append(names, spec.Name)
	}
	sort.Strings(names)
	return names
}

func noWorkspaceEvidenceError() error {
	return fmt.Errorf(
		"%w: every tool call failed argument validation or was rejected; the turn was not committed",
		ErrNoWorkspaceEvidence,
	)
}

func (r *Runner) decideRoute(
	ctx context.Context,
	history []Message,
	task string,
	observer func(Event),
) (Route, []RouteStep, error) {
	r.observe(Event{Kind: EventRouteStart}, observer)
	messages := []Message{{Role: RoleSystem, Content: r.router.Instructions()}}
	messages = append(messages, routingHistory(history)...)
	messages = append(messages, Message{Role: RoleUser, Content: task})

	var steps []RouteStep
	for attempt := 0; attempt <= r.options.RouteRetries; attempt++ {
		rendered, err := r.routeRenderer.Render(messages)
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return "", steps, err
		}
		request := r.options.Generation
		request.Prompt, err = appendRequiredAssistantPrefix(r.routeRenderer, rendered, "<route>")
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return "", steps, err
		}
		request.Stops = r.router.Stops()
		request.MaxOutputTokens = r.options.RouteMaxOutputTokens
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(messages, nil, false, false, "<route>")
		}
		promptTrace := r.tracePrompt(request, "<route>", nil)
		started := time.Now()
		generated, _, _, err := r.generate(ctx, request, messages, nil, false, false, "<route>")
		if err != nil {
			steps = append(steps, RouteStep{
				Attempt:     attempt + 1,
				Request:     promptTrace,
				StartedAtMS: started.UnixMilli(),
				DurationMS:  time.Since(started).Milliseconds(),
			})
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return "", steps, err
		}
		candidate := strings.TrimSpace(generated.Text)
		if !strings.HasPrefix(candidate, "<route>") {
			candidate = "<route>" + candidate
		}
		route, parseErr := r.router.Parse(candidate, generated.FinishReason)
		current := RouteStep{
			Attempt:     attempt + 1,
			Request:     promptTrace,
			ModelOutput: generated.Text,
			StartedAtMS: started.UnixMilli(),
			DurationMS:  time.Since(started).Milliseconds(),
		}
		if parseErr == nil {
			current.Route = route
			steps = append(steps, current)
			r.observe(Event{Kind: EventRouteDone, Route: route}, observer)
			return route, steps, nil
		}
		current.ProtocolError = parseErr.Error()
		if attempt == r.options.RouteRetries {
			current.Route = RouteRespond
			current.FailedClosed = true
			steps = append(steps, current)
			r.observe(Event{
				Kind:  EventRouteDone,
				Route: RouteRespond,
				Err:   parseErr,
			}, observer)
			return RouteRespond, steps, nil
		}
		steps = append(steps, current)
		if echoed := retryEcho(candidate, parseErr); echoed != "" {
			messages = append(messages, Message{Role: RoleAssistant, Content: echoed})
		}
		messages = append(
			messages,
			Message{Role: RoleUser, Content: r.router.Correction(parseErr)},
		)
	}
	return RouteRespond, steps, nil
}

func (r *Runner) decideToolRoute(
	ctx context.Context,
	history []Message,
	task string,
	observer func(Event),
) (ToolRouteDecision, []RouteStep, error) {
	r.observe(Event{Kind: EventRouteStart}, observer)
	messages := []Message{{Role: RoleSystem, Content: r.toolRouter.Instructions(r.toolBundles)}}
	messages = append(messages, routingHistory(history)...)
	messages = append(messages, Message{Role: RoleUser, Content: task})

	var steps []RouteStep
	for attempt := 0; attempt <= r.options.RouteRetries; attempt++ {
		rendered, err := r.routeRenderer.Render(messages)
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return ToolRouteDecision{}, steps, err
		}
		request := r.options.Generation
		request.Prompt, err = appendRequiredAssistantPrefix(r.routeRenderer, rendered, "<route>")
		if err != nil {
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return ToolRouteDecision{}, steps, err
		}
		request.Stops = r.toolRouter.Stops()
		request.MaxOutputTokens = r.options.RouteMaxOutputTokens
		if r.toolCompleter != nil {
			request.Prompt = r.nativeTracePrompt(messages, nil, false, false, "<route>")
		}
		promptTrace := r.tracePrompt(request, "<route>", nil)
		started := time.Now()
		generated, _, _, err := r.generate(ctx, request, messages, nil, false, false, "<route>")
		if err != nil {
			steps = append(steps, RouteStep{
				Attempt:     attempt + 1,
				Request:     promptTrace,
				StartedAtMS: started.UnixMilli(),
				DurationMS:  time.Since(started).Milliseconds(),
			})
			r.observe(Event{Kind: EventRouteDone, Err: err}, observer)
			return ToolRouteDecision{}, steps, err
		}
		candidate := strings.TrimSpace(generated.Text)
		if !strings.HasPrefix(candidate, "<route>") {
			candidate = "<route>" + candidate
		}
		decision, parseErr := r.toolRouter.Parse(candidate, generated.FinishReason, r.toolBundles)
		current := RouteStep{
			Attempt:     attempt + 1,
			Request:     promptTrace,
			ModelOutput: generated.Text,
			StartedAtMS: started.UnixMilli(),
			DurationMS:  time.Since(started).Milliseconds(),
		}
		if parseErr == nil {
			current.Route = decision.Route
			current.Bundles = append([]string(nil), decision.Bundles...)
			steps = append(steps, current)
			r.observe(Event{Kind: EventRouteDone, Route: decision.Route, Bundles: decision.Bundles}, observer)
			return decision, steps, nil
		}
		current.ProtocolError = parseErr.Error()
		if attempt == r.options.RouteRetries {
			current.Route = RouteRespond
			current.FailedClosed = true
			steps = append(steps, current)
			r.observe(Event{Kind: EventRouteDone, Route: RouteRespond, Err: parseErr}, observer)
			return ToolRouteDecision{Route: RouteRespond}, steps, nil
		}
		steps = append(steps, current)
		if echoed := retryEcho(candidate, parseErr); echoed != "" {
			messages = append(messages, Message{Role: RoleAssistant, Content: echoed})
		}
		messages = append(messages, Message{
			Role:    RoleUser,
			Content: r.toolRouter.Correction(parseErr, r.toolBundles),
		})
	}
	return ToolRouteDecision{Route: RouteRespond}, steps, nil
}

// History returns a copy of the committed multi-turn transcript. The control
// prompt is intentionally excluded.
