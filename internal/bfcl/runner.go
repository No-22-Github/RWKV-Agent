package bfcl

import (
	"context"
	"encoding/json"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type RunnerOptions struct {
	Completer       toolchat.Completer
	Model           string
	Concurrency     int
	MaxOutputTokens int
	MaxPromptChars  int
	Temperature     float32
	CaseTimeout     time.Duration
	Progress        func(completed, total int)
}

type TraceEntry struct {
	ResultEntry
	Content          string              `json:"content,omitempty"`
	ReasoningContent string              `json:"reasoning_content,omitempty"`
	ToolCalls        []toolchat.ToolCall `json:"tool_calls,omitempty"`
	PromptBytes      int                 `json:"prompt_bytes,omitempty"`
	FinishReason     string              `json:"finish_reason,omitempty"`
	Repairs          []string            `json:"repairs,omitempty"`
	ParseError       string              `json:"parse_error,omitempty"`
	Error            string              `json:"error,omitempty"`
	Skipped          bool                `json:"skipped,omitempty"`
}

type RunResult struct {
	Entries      []ResultEntry
	Trace        []TraceEntry
	Failed       int
	ParseFailed  int
	Repaired     int
	Skipped      int
	Usage        continuation.Usage
	RepairCounts map[string]int
	Elapsed      time.Duration
}

func RunNative(ctx context.Context, cases []Case, options RunnerOptions) (RunResult, error) {
	if options.Completer == nil {
		return RunResult{}, fmt.Errorf("BFCL completer is required")
	}
	if !options.Completer.NativeToolCalling() {
		return RunResult{}, fmt.Errorf("BFCL adapter health requires native tool calling")
	}
	if options.Concurrency <= 0 {
		return RunResult{}, fmt.Errorf("BFCL concurrency must be positive")
	}
	if options.MaxOutputTokens <= 0 || options.Temperature < 0 {
		return RunResult{}, fmt.Errorf("BFCL sampling limits must be non-negative")
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
	var completed atomic.Int64
	for range workerCount {
		wait.Add(1)
		go func() {
			defer wait.Done()
			for current := range jobs {
				trace[current.index] = runNativeCase(ctx, current.entry, options)
				if options.Progress != nil {
					options.Progress(int(completed.Add(1)), len(cases))
				}
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
		}
	}
	return result, nil
}

func runNativeCase(parent context.Context, entry Case, options RunnerOptions) TraceEntry {
	resultEntry := ResultEntry{ID: entry.ID, Category: entry.Category}
	trace := TraceEntry{ResultEntry: resultEntry}
	tools, names, err := NativeTools(entry)
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	messages := NativeMessages(entry)
	if options.MaxPromptChars > 0 {
		encoded, marshalErr := json.Marshal(struct {
			Messages []toolchat.Message `json:"messages"`
			Tools    []toolchat.Tool    `json:"tools"`
		}{Messages: messages, Tools: tools})
		if marshalErr != nil {
			trace.Error = marshalErr.Error()
			return trace
		}
		if len(encoded) > options.MaxPromptChars {
			trace.ModelCalls = 0
			trace.Skipped = true
			trace.Error = fmt.Sprintf("request size %d exceeds max_prompt_chars %d", len(encoded), options.MaxPromptChars)
			return trace
		}
	}

	ctx, cancel := context.WithTimeout(parent, options.CaseTimeout)
	defer cancel()
	trace.ModelCalls = 1
	toolChoice := toolchat.ToolChoiceAuto
	parallelToolCalls := true
	if len(tools) == 0 {
		toolChoice = toolchat.ToolChoiceNone
		parallelToolCalls = false
	}
	started := time.Now()
	completion, err := options.Completer.Complete(ctx, toolchat.Request{
		Model:           options.Model,
		Messages:        messages,
		Tools:           tools,
		ToolChoice:      toolChoice,
		MaxOutputTokens: options.MaxOutputTokens,
		Sampling: continuation.Sampling{
			Temperature:      options.Temperature,
			TopK:             1,
			TopP:             1,
			PresencePenalty:  0,
			FrequencyPenalty: 0,
			PenaltyDecay:     1,
		},
		ParallelToolCalls: parallelToolCalls,
	}, nil)
	trace.Latency = time.Since(started).Seconds()
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	trace.Content = completion.Content
	trace.ReasoningContent = completion.ReasoningContent
	trace.ToolCalls = completion.ToolCalls
	trace.FinishReason = string(completion.FinishReason)
	trace.InputTokens = completion.Usage.PromptTokens
	trace.OutputTokens = completion.Usage.CompletionTokens
	language := LanguagePython
	if entry.Category == "simple_java" {
		language = LanguageJava
	} else if entry.Category == "simple_javascript" {
		language = LanguageJavaScript
	}
	trace.Result, err = ToResultString(completion.ToolCalls, names, language)
	if err != nil {
		trace.Error = err.Error()
	}
	return trace
}
