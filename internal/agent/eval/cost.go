package eval

import (
	"context"
	"errors"
	"sort"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// Cost is the time and token spend of one turn or one whole case, so a run
// can be sorted by what held it up. It is derived from the turn's steps and
// never feeds scoring.
//
// Two clocks are kept apart on purpose. WallMS is elapsed time from start to
// end; under case parallelism it includes waiting for the shared endpoint.
// ModelMS and ToolMS are sums of the per-step durations, so a case that
// queued behind others shows a WallMS close to ModelMS (the model call itself
// waits in the server queue) while a slow tool shows in ToolMS.
//
// Token counts follow the per-step usage: PromptTokens and CompletionTokens are
// sums over the model steps (every step re-sends its whole context, so the
// prompt sum is the prefill work, not the context size), MaxPromptTokens is the
// largest single step context. TokenSource names where the counts came from
// ("server", "server_stream", "local_vocab", or several joined by "+");
// TokensMissingSteps counts model steps that carry no count at all.
type Cost struct {
	StartedAtMS int64 `json:"started_at_ms,omitempty"`
	EndedAtMS   int64 `json:"ended_at_ms,omitempty"`
	WallMS      int64 `json:"wall_ms"`
	ModelMS     int64 `json:"model_ms"`
	ToolMS      int64 `json:"tool_ms"`
	// WaitMS sums, over the model steps, the time from sending the request to
	// the first streamed token: batching window, server queue and prefill.
	// Under case parallelism it is mostly the shared endpoint's queue, so a
	// case whose ModelMS is high but WaitMS low spent its time generating.
	WaitMS             int64  `json:"wait_ms,omitempty"`
	Steps              int    `json:"steps"`
	MaxSteps           int    `json:"max_steps,omitempty"`
	PromptTokens       int    `json:"prompt_tokens"`
	CompletionTokens   int    `json:"completion_tokens"`
	MaxPromptTokens    int    `json:"max_prompt_tokens"`
	TokenSource        string `json:"token_source,omitempty"`
	TokensMissingSteps int    `json:"tokens_missing_steps,omitempty"`
	// LengthSteps counts steps that stopped on the output token budget: a
	// length finish, or (rwkv_lightning reports "stop" even at max_tokens) a
	// call whose generated count reached its budget, see atTokenBudget.
	LengthSteps  int  `json:"length_steps,omitempty"`
	HitMaxTokens bool `json:"hit_max_tokens,omitempty"`
	// HitMaxSteps is set when the turn ran out of steps: the runner gave up
	// at the step limit, or forced the answer stage because of the budget.
	HitMaxSteps bool `json:"hit_max_steps,omitempty"`
	// HitTimeout is set when the case timeout cut the turn off.
	HitTimeout bool `json:"hit_timeout,omitempty"`
}

// turnCost summarizes one turn. started and ended bracket the runner call.
func turnCost(
	result agent.Result,
	runErr error,
	maxSteps int,
	started time.Time,
	ended time.Time,
) *Cost {
	cost := &Cost{
		StartedAtMS: started.UnixMilli(),
		EndedAtMS:   ended.UnixMilli(),
		WallMS:      ended.Sub(started).Milliseconds(),
		MaxSteps:    maxSteps,
		Steps:       len(result.Steps),
	}
	sources := map[string]bool{}
	for _, route := range result.RouteSteps {
		cost.ModelMS += route.DurationMS
	}
	for _, step := range result.Steps {
		cost.ModelMS += step.ModelDurationMS
		cost.ToolMS += step.ToolDurationMS
		if step.StartedAtMS > 0 && step.FirstTokenAtMS >= step.StartedAtMS {
			cost.WaitMS += step.FirstTokenAtMS - step.StartedAtMS
		}
		usage := step.Usage
		cost.PromptTokens += usage.PromptTokens
		cost.CompletionTokens += usage.CompletionTokens
		if usage.PromptTokens > cost.MaxPromptTokens {
			cost.MaxPromptTokens = usage.PromptTokens
		}
		if usage.PromptTokens > 0 {
			sources[usageSource(usage.PromptSource)] = true
		}
		if usage.CompletionTokens > 0 {
			sources[usageSource(usage.CompletionSource)] = true
		}
		if step.ModelError == "" && usage.PromptTokens == 0 && usage.CompletionTokens == 0 {
			cost.TokensMissingSteps++
		}
		if step.FinishReason == continuation.FinishLength {
			cost.LengthSteps++
		}
	}
	cost.TokenSource = joinSources(sources)
	cost.HitMaxTokens = cost.LengthSteps > 0
	cost.HitMaxSteps = errors.Is(runErr, agent.ErrMaxSteps) ||
		result.ForcedAnswerReason == forcedAnswerStepBudget ||
		(maxSteps > 0 && len(result.Steps) >= maxSteps)
	cost.HitTimeout = errors.Is(runErr, context.DeadlineExceeded)
	return cost
}

// addBudgetHits raises LengthSteps to the number of model calls the recording
// generator saw reach their token budget, for backends whose finish reason
// does not say so. A step that both finished on length and was counted is
// counted once.
func (c *Cost) addBudgetHits(hits int) {
	if hits > c.LengthSteps {
		c.LengthSteps = hits
	}
	c.HitMaxTokens = c.LengthSteps > 0
}

// atTokenBudget reports whether a call generated up to its output budget.
// rwkv_lightning finishes such a call with "stop", so the count is the only
// sign. The count comes from stream chunks, which skip a token that decodes to
// no text yet (half of a multi-byte character), so it may fall a little short
// of the budget; 98% leaves room for that, and a call that ends on its own
// that close to the budget is rare enough to count as a hit too.
func atTokenBudget(completion int, budget int) bool {
	return budget > 0 && completion*50 >= budget*49
}

// forcedAnswerStepBudget mirrors the runner's forced-answer reason for a step
// budget that ran out after a tool attempt.
const forcedAnswerStepBudget = "step_budget_after_tool_attempt"

// caseCost adds up the turn costs; started and ended bracket the whole case,
// including workspace setup and the case-level expectation checks.
func caseCost(turns []TurnResult, started time.Time, ended time.Time, timedOut bool) *Cost {
	cost := &Cost{
		StartedAtMS: started.UnixMilli(),
		EndedAtMS:   ended.UnixMilli(),
		WallMS:      ended.Sub(started).Milliseconds(),
		HitTimeout:  timedOut,
	}
	sources := map[string]bool{}
	for _, turn := range turns {
		if turn.Cost == nil {
			continue
		}
		turnCost := turn.Cost
		cost.ModelMS += turnCost.ModelMS
		cost.ToolMS += turnCost.ToolMS
		cost.WaitMS += turnCost.WaitMS
		cost.Steps += turnCost.Steps
		if turnCost.MaxSteps > cost.MaxSteps {
			cost.MaxSteps = turnCost.MaxSteps
		}
		cost.PromptTokens += turnCost.PromptTokens
		cost.CompletionTokens += turnCost.CompletionTokens
		if turnCost.MaxPromptTokens > cost.MaxPromptTokens {
			cost.MaxPromptTokens = turnCost.MaxPromptTokens
		}
		for _, source := range strings.Split(turnCost.TokenSource, "+") {
			if source != "" {
				sources[source] = true
			}
		}
		cost.TokensMissingSteps += turnCost.TokensMissingSteps
		cost.LengthSteps += turnCost.LengthSteps
		cost.HitMaxTokens = cost.HitMaxTokens || turnCost.HitMaxTokens
		cost.HitMaxSteps = cost.HitMaxSteps || turnCost.HitMaxSteps
		cost.HitTimeout = cost.HitTimeout || turnCost.HitTimeout
	}
	cost.TokenSource = joinSources(sources)
	return cost
}

// usageSource names a count's source; a count recorded without one was
// reported by the backend.
func usageSource(source string) string {
	if source == "" {
		return continuation.UsageSourceServer
	}
	return source
}

func joinSources(sources map[string]bool) string {
	names := make([]string, 0, len(sources))
	for name := range sources {
		names = append(names, name)
	}
	sort.Strings(names)
	return strings.Join(names, "+")
}
