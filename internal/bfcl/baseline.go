package bfcl

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

type BaselineRunnerOptions struct {
	Generator       continuation.Generator
	Model           string
	Transport       Transport
	Concurrency     int
	MaxOutputTokens int
	MaxPromptChars  int
	Temperature     float32
	CaseTimeout     time.Duration
}

func RunBaseline(ctx context.Context, cases []Case, options BaselineRunnerOptions) (RunResult, error) {
	if options.Generator == nil {
		return RunResult{}, fmt.Errorf("BFCL continuation generator is required")
	}
	if options.Transport != TransportRWKVContinuation && options.Transport != TransportChatCompletionsWrapped {
		return RunResult{}, fmt.Errorf("BFCL baseline transport is required")
	}
	if options.Concurrency <= 0 {
		return RunResult{}, fmt.Errorf("BFCL concurrency must be positive")
	}
	if options.MaxOutputTokens <= 0 || options.Temperature <= 0 {
		return RunResult{}, fmt.Errorf("BFCL sampling limits must be positive")
	}
	if options.CaseTimeout <= 0 {
		return RunResult{}, fmt.Errorf("BFCL case timeout must be positive")
	}

	type job struct {
		index int
		entry Case
	}
	jobs := make(chan job)
	trace := make([]TraceEntry, len(cases))
	started := time.Now()
	var wait sync.WaitGroup
	workerCount := min(options.Concurrency, len(cases))
	for range workerCount {
		wait.Add(1)
		go func() {
			defer wait.Done()
			for current := range jobs {
				trace[current.index] = runBaselineCase(ctx, current.entry, options)
			}
		}()
	}
	for index, entry := range cases {
		select {
		case jobs <- job{index: index, entry: entry}:
		case <-ctx.Done():
			close(jobs)
			wait.Wait()
			return RunResult{}, ctx.Err()
		}
	}
	close(jobs)
	wait.Wait()

	result := RunResult{Trace: trace, Elapsed: time.Since(started)}
	result.Entries = make([]ResultEntry, 0, len(trace))
	for _, entry := range trace {
		result.Entries = append(result.Entries, entry.ResultEntry)
		result.Usage.PromptTokens += entry.InputTokens
		result.Usage.CompletionTokens += entry.OutputTokens
		if entry.Skipped {
			result.Skipped++
		} else if entry.Error != "" {
			result.Failed++
		} else if entry.ParseError != "" {
			result.ParseFailed++
		}
	}
	return result, nil
}

func runBaselineCase(parent context.Context, entry Case, options BaselineRunnerOptions) TraceEntry {
	resultEntry := ResultEntry{ID: entry.ID, Category: entry.Category}
	trace := TraceEntry{ResultEntry: resultEntry}
	prompt, err := RenderPrompt(entry, TierBaseline, options.Transport)
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	trace.PromptBytes = len(prompt)
	if options.MaxPromptChars > 0 && len(prompt) > options.MaxPromptChars {
		trace.Skipped = true
		trace.Error = fmt.Sprintf("prompt size %d exceeds max_prompt_chars %d", len(prompt), options.MaxPromptChars)
		return trace
	}

	ctx, cancel := context.WithTimeout(parent, options.CaseTimeout)
	defer cancel()
	trace.ModelCalls = 1
	started := time.Now()
	completion, err := options.Generator.Continue(ctx, continuation.Request{
		Model:           options.Model,
		Prompt:          prompt,
		MaxOutputTokens: options.MaxOutputTokens,
		Stops:           baselineStops(options.Transport),
		Sampling: continuation.Sampling{
			Temperature:      options.Temperature,
			TopK:             1,
			TopP:             1,
			PresencePenalty:  0,
			FrequencyPenalty: 0,
			PenaltyDecay:     1,
		},
	}, nil)
	trace.Latency = time.Since(started).Seconds()
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	trace.Content = completion.Text
	trace.FinishReason = string(completion.FinishReason)
	trace.InputTokens = completion.Usage.PromptTokens
	trace.OutputTokens = completion.Usage.CompletionTokens
	calls, err := ParseMarkdownCalls(completion.Text)
	if err != nil {
		trace.ParseError = err.Error()
		return trace
	}
	trace.ToolCalls = calls
	trace.Result, err = ToResultString(calls, nil, LanguagePython)
	if err != nil {
		trace.ParseError = err.Error()
	}
	return trace
}

func baselineStops(transport Transport) []string {
	if transport == TransportChatCompletionsWrapped {
		return []string{"```", "\n\nUser:", "\nSystem:", "</s>"}
	}
	return []string{"```", "\n\nUser:", "\nUser:", "\nSystem:", "</s>"}
}
