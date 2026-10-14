package eval

import (
	"context"
	"errors"
	"io"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestCountUsageFillsEmptyCountsFromTheLocalVocabulary(t *testing.T) {
	count := func(text string) int { return len(text) }
	filled := countUsage(continuation.Usage{}, "prompt", "out</tool_call>", count)
	if filled.PromptTokens != 6 || filled.PromptSource != continuation.UsageSourceLocalVocab {
		t.Fatalf("prompt = %d/%q", filled.PromptTokens, filled.PromptSource)
	}
	if filled.CompletionTokens != 15 || filled.CompletionSource != continuation.UsageSourceLocalVocab {
		t.Fatalf("completion = %d/%q", filled.CompletionTokens, filled.CompletionSource)
	}

	// A count the backend reported wins and is labeled; only the empty one
	// is counted locally.
	reported := countUsage(continuation.Usage{CompletionTokens: 9}, "prompt", "out", count)
	if reported.CompletionTokens != 9 || reported.CompletionSource != continuation.UsageSourceServer {
		t.Fatalf("reported completion = %d/%q", reported.CompletionTokens, reported.CompletionSource)
	}
	if reported.PromptSource != continuation.UsageSourceLocalVocab {
		t.Fatalf("prompt source = %q", reported.PromptSource)
	}

	// A stream count keeps its label.
	stream := countUsage(continuation.Usage{
		CompletionTokens: 4, CompletionSource: continuation.UsageSourceServerStream,
	}, "", "out", count)
	if stream.CompletionSource != continuation.UsageSourceServerStream || stream.CompletionTokens != 4 {
		t.Fatalf("stream completion = %d/%q", stream.CompletionTokens, stream.CompletionSource)
	}

	// No counter: nothing is invented.
	if empty := countUsage(continuation.Usage{}, "prompt", "out", nil); empty != (continuation.Usage{}) {
		t.Fatalf("usage without a counter = %+v", empty)
	}
}

func TestTurnCostSumsStepsAndFlagsLimits(t *testing.T) {
	started := time.UnixMilli(1_000)
	result := agent.Result{
		RouteSteps: []agent.RouteStep{{DurationMS: 5}},
		Steps: []agent.Step{
			{
				ModelDurationMS: 100, ToolDurationMS: 7,
				FinishReason: continuation.FinishStop,
				Usage: continuation.Usage{
					PromptTokens: 300, CompletionTokens: 20,
					PromptSource:     continuation.UsageSourceLocalVocab,
					CompletionSource: continuation.UsageSourceServerStream,
				},
			},
			{
				ModelDurationMS: 200,
				FinishReason:    continuation.FinishLength,
				Usage: continuation.Usage{
					PromptTokens: 500, CompletionTokens: 2048,
					PromptSource:     continuation.UsageSourceLocalVocab,
					CompletionSource: continuation.UsageSourceServerStream,
				},
			},
			{ModelDurationMS: 3, ModelError: "boom"},
			{ModelDurationMS: 4, FinishReason: continuation.FinishStop},
		},
	}
	cost := turnCost(result, agent.ErrMaxSteps, 4, started, started.Add(900*time.Millisecond))
	if cost.WallMS != 900 || cost.StartedAtMS != 1_000 || cost.EndedAtMS != 1_900 {
		t.Fatalf("wall = %+v", cost)
	}
	if cost.ModelMS != 312 || cost.ToolMS != 7 || cost.Steps != 4 || cost.MaxSteps != 4 {
		t.Fatalf("time = %+v", cost)
	}
	if cost.PromptTokens != 800 || cost.CompletionTokens != 2068 || cost.MaxPromptTokens != 500 {
		t.Fatalf("tokens = %+v", cost)
	}
	if cost.TokenSource != "local_vocab+server_stream" || cost.TokensMissingSteps != 1 {
		t.Fatalf("source = %q missing = %d", cost.TokenSource, cost.TokensMissingSteps)
	}
	if !cost.HitMaxTokens || cost.LengthSteps != 1 || !cost.HitMaxSteps || cost.HitTimeout {
		t.Fatalf("limits = %+v", cost)
	}

	timedOut := turnCost(agent.Result{}, context.DeadlineExceeded, 16, started, started)
	if !timedOut.HitTimeout || timedOut.HitMaxSteps || timedOut.HitMaxTokens {
		t.Fatalf("timeout limits = %+v", timedOut)
	}
	forced := turnCost(agent.Result{ForcedAnswerReason: forcedAnswerStepBudget}, nil, 16, started, started)
	if !forced.HitMaxSteps {
		t.Fatal("a forced answer on the step budget did not count as hitting max steps")
	}
}

func TestCaseCostAddsTurnsAndKeepsTheWallClockSeparate(t *testing.T) {
	started := time.UnixMilli(10_000)
	turns := []TurnResult{
		{Cost: &Cost{
			WallMS: 400, ModelMS: 300, ToolMS: 50, Steps: 3, MaxSteps: 16,
			PromptTokens: 900, CompletionTokens: 90, MaxPromptTokens: 400,
			TokenSource: "local_vocab+server_stream", LengthSteps: 1, HitMaxTokens: true,
		}},
		{Cost: &Cost{
			WallMS: 200, ModelMS: 150, ToolMS: 0, Steps: 1, MaxSteps: 16,
			PromptTokens: 700, CompletionTokens: 10, MaxPromptTokens: 700,
			TokenSource: "server",
		}},
		{},
	}
	cost := caseCost(turns, started, started.Add(time.Second), false)
	if cost.WallMS != 1000 || cost.ModelMS != 450 || cost.ToolMS != 50 || cost.Steps != 4 {
		t.Fatalf("time = %+v", cost)
	}
	if cost.PromptTokens != 1600 || cost.CompletionTokens != 100 || cost.MaxPromptTokens != 700 {
		t.Fatalf("tokens = %+v", cost)
	}
	if cost.TokenSource != "local_vocab+server+server_stream" {
		t.Fatalf("source = %q", cost.TokenSource)
	}
	if !cost.HitMaxTokens || cost.HitMaxSteps || cost.LengthSteps != 1 || cost.MaxSteps != 16 {
		t.Fatalf("limits = %+v", cost)
	}
}

// A backend that reports no usage (rwkv_lightning) gets every step counted
// with the local vocabulary, and the turn and case carry their cost.
func TestRunRecordsCostAndLocalTokenCounts(t *testing.T) {
	answer := "The code is TRACE-2048."
	script := []continuation.Result{
		{Text: `<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`,
			FinishReason: continuation.FinishStop},
		{Text: answer, FinishReason: continuation.FinishStop},
	}
	loop := continuation.Result{
		Text:         `<tool_call>{"name":"list_files","arguments":{"path":"."}}</tool_call>`,
		FinishReason: continuation.FinishStop,
	}
	count := func(text string) int { return len([]rune(text)) }
	report, err := Run(context.Background(), Config{
		Cases: []Case{
			{
				ID:          "answers",
				Description: "Answers after one read.",
				Files:       map[string]string{"facts.txt": "TRACE-2048\n"},
				Turns: []Turn{{
					Prompt: "Read facts.txt and report its code.",
					Expect: Expectation{Route: agent.RouteInspect, Tools: []string{"read_file"}, OutputContains: []string{"TRACE-2048"}},
				}},
			},
			{
				ID:          "loops",
				Description: "Never stops calling tools.",
				Files:       map[string]string{"facts.txt": "TRACE-2048\n"},
				Turns: []Turn{{
					Prompt: "List the files.",
					Expect: Expectation{Route: agent.RouteInspect, Tools: []string{"list_files"}},
				}},
			},
		},
		Suite: "custom",
		Runner: agent.Options{
			MaxSteps:                3,
			DecisionMaxOutputTokens: 64,
			DuplicateReplayLimit:    100,
			Generation:              continuation.Request{MaxOutputTokens: 64},
		},
		TokenCount: count,
		GeneratorFactory: func(ctx context.Context) (continuation.Generator, io.Closer, error) {
			index := 0
			caseID, _ := CaseIDFromContext(ctx)
			loops := caseID == "loops"
			return continuation.GenerateFunc(func(
				context.Context, continuation.Request, continuation.EventSink,
			) (continuation.Result, error) {
				if loops {
					return loop, nil
				}
				if index >= len(script) {
					return continuation.Result{}, errors.New("script exhausted")
				}
				result := script[index]
				index++
				return result, nil
			}), nil, nil
		},
		CaseTimeout: 10 * time.Second,
		TempDir:     t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}

	answered := report.Summary.Cases[0]
	if !answered.Passed {
		t.Fatalf("case failed: %+v", answered)
	}
	turn := answered.Turns[0]
	if turn.Cost == nil || answered.Cost == nil {
		t.Fatalf("missing cost: turn %+v case %+v", turn.Cost, answered.Cost)
	}
	sumPrompt, sumCompletion, maxPrompt := 0, 0, 0
	for _, step := range turn.Result.Steps {
		usage := step.Usage
		if usage.PromptSource != continuation.UsageSourceLocalVocab ||
			usage.CompletionSource != continuation.UsageSourceLocalVocab {
			t.Fatalf("step %d usage sources = %+v", step.Number, usage)
		}
		if usage.PromptTokens == 0 || usage.CompletionTokens == 0 {
			t.Fatalf("step %d usage = %+v", step.Number, usage)
		}
		sumPrompt += usage.PromptTokens
		sumCompletion += usage.CompletionTokens
		maxPrompt = max(maxPrompt, usage.PromptTokens)
	}
	if turn.Cost.PromptTokens != sumPrompt || turn.Cost.CompletionTokens != sumCompletion ||
		turn.Cost.MaxPromptTokens != maxPrompt || turn.Cost.Steps != len(turn.Result.Steps) {
		t.Fatalf("turn cost = %+v, steps sum %d/%d max %d", turn.Cost, sumPrompt, sumCompletion, maxPrompt)
	}
	if turn.Cost.TokenSource != continuation.UsageSourceLocalVocab || turn.Cost.HitMaxSteps {
		t.Fatalf("turn cost = %+v", turn.Cost)
	}
	if answered.Cost.CompletionTokens != turn.Cost.CompletionTokens ||
		answered.Cost.MaxPromptTokens != turn.Cost.MaxPromptTokens ||
		answered.Cost.WallMS < turn.Cost.WallMS ||
		answered.Cost.StartedAtMS > turn.Cost.StartedAtMS ||
		answered.Cost.EndedAtMS < turn.Cost.EndedAtMS {
		t.Fatalf("case cost = %+v, turn cost = %+v", answered.Cost, turn.Cost)
	}

	looped := report.Summary.Cases[1].Cost
	if looped == nil || !looped.HitMaxSteps || looped.MaxSteps != 3 {
		t.Fatalf("looping case cost = %+v", looped)
	}

	// The trace carries the same labeled counts, so the run totals add up.
	tracePrompt := 0
	for _, record := range report.Trace {
		if record.ModelCall == nil {
			continue
		}
		if record.ModelCall.Response.Usage.PromptSource != continuation.UsageSourceLocalVocab {
			t.Fatalf("trace usage = %+v", record.ModelCall.Response.Usage)
		}
		tracePrompt += record.ModelCall.Response.Usage.PromptTokens
	}
	if report.Summary.Metrics.PromptTokens != tracePrompt || tracePrompt == 0 {
		t.Fatalf("metrics prompt tokens = %d, trace %d", report.Summary.Metrics.PromptTokens, tracePrompt)
	}
}

func TestBudgetHitsFlagAStopThatRanToTheBudget(t *testing.T) {
	for _, tc := range []struct {
		completion, budget int
		want               bool
	}{{4096, 4096, true}, {4020, 4096, true}, {3900, 4096, false}, {10, 0, false}} {
		if got := atTokenBudget(tc.completion, tc.budget); got != tc.want {
			t.Fatalf("atTokenBudget(%d, %d) = %v", tc.completion, tc.budget, got)
		}
	}
	cost := &Cost{}
	cost.addBudgetHits(0)
	if cost.HitMaxTokens {
		t.Fatal("no hits flagged max tokens")
	}
	cost.addBudgetHits(2)
	if cost.LengthSteps != 2 || !cost.HitMaxTokens {
		t.Fatalf("hits = %+v", cost)
	}
	counted := &Cost{LengthSteps: 1, HitMaxTokens: true}
	counted.addBudgetHits(1)
	if counted.LengthSteps != 1 {
		t.Fatalf("a length finish was counted twice: %+v", counted)
	}
}

func TestTurnCostSumsTimeToFirstToken(t *testing.T) {
	result := agent.Result{Steps: []agent.Step{
		{StartedAtMS: 1_000, FirstTokenAtMS: 1_400, ModelDurationMS: 900},
		{StartedAtMS: 2_000, FirstTokenAtMS: 2_100, ModelDurationMS: 300},
		{StartedAtMS: 3_000, ModelDurationMS: 50},
	}}
	started := time.UnixMilli(1_000)
	if cost := turnCost(result, nil, 16, started, started); cost.WaitMS != 500 {
		t.Fatalf("wait = %d", cost.WaitMS)
	}
}
