package bfcl

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

const RetryPromptVersion = "bfcl-markdown-retry-v1"

type BaselineRunnerOptions struct {
	Generator       continuation.Generator
	Model           string
	Tier            Tier
	Transport       Transport
	Concurrency     int
	MaxOutputTokens int
	MaxPromptChars  int
	Temperature     float32
	CaseTimeout     time.Duration
	Progress        func(completed, total int)
}

func RunBaseline(ctx context.Context, cases []Case, options BaselineRunnerOptions) (RunResult, error) {
	if options.Generator == nil {
		return RunResult{}, fmt.Errorf("BFCL continuation generator is required")
	}
	if options.Tier == "" {
		options.Tier = TierBaseline
	}
	if options.Tier != TierBaseline && options.Tier != TierEnhanced && options.Tier != TierFinishTaskProbe && options.Tier != TierXMLBaseline && options.Tier != TierXMLAnchor {
		return RunResult{}, fmt.Errorf("unsupported BFCL tier %q", options.Tier)
	}
	if options.Tier == TierXMLBaseline || options.Tier == TierXMLAnchor {
		if options.Transport != TransportRWKVContinuation {
			return RunResult{}, fmt.Errorf("BFCL XML tier requires the %s transport", TransportRWKVContinuation)
		}
	} else if options.Transport != TransportRWKVContinuation && options.Transport != TransportChatCompletionsWrapped {
		return RunResult{}, fmt.Errorf("BFCL Markdown transport is required")
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
				trace[current.index] = runBaselineCase(ctx, current.entry, options)
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

	result := RunResult{
		Trace:           trace,
		Elapsed:         time.Since(started),
		RepairCounts:    make(map[string]int),
		ProbeSelections: make(map[string]int),
	}
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
		if len(entry.Repairs) > 0 {
			result.Repaired++
			for _, repair := range entry.Repairs {
				result.RepairCounts[repair]++
			}
		}
		if entry.ModelCalls > 1 {
			result.Retried++
			if entry.Error == "" && entry.ParseError == "" {
				result.RetryParsed++
			}
		}
		if entry.ProbeSelection != "" {
			result.ProbeSelections[entry.ProbeSelection]++
		}
	}
	return result, nil
}

func runBaselineCase(parent context.Context, entry Case, options BaselineRunnerOptions) TraceEntry {
	if options.Tier == TierXMLBaseline || options.Tier == TierXMLAnchor {
		return runXMLCase(parent, entry, options)
	}
	resultEntry := ResultEntry{ID: entry.ID, Category: entry.Category}
	trace := TraceEntry{ResultEntry: resultEntry}
	rendered, err := RenderPromptWithAnchor(entry, options.Tier, options.Transport)
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	trace.PromptBytes = len(rendered.Prompt)
	trace.PrefillAnchor = rendered.Anchor
	trace.PromptSHA256 = promptSHA256(rendered.Prompt)
	if options.MaxPromptChars > 0 && len(rendered.Prompt) > options.MaxPromptChars {
		trace.Skipped = true
		trace.Error = fmt.Sprintf("prompt size %d exceeds max_prompt_chars %d", len(rendered.Prompt), options.MaxPromptChars)
		return trace
	}

	ctx, cancel := context.WithTimeout(parent, options.CaseTimeout)
	defer cancel()
	first, err := runMarkdownAttempt(ctx, rendered.Prompt, rendered.Anchor, 1, options)
	trace.Attempts = append(trace.Attempts, first)
	trace.ModelCalls = 1
	accumulateAttempt(&trace, first)
	if err != nil {
		trace.Error = err.Error()
		return trace
	}

	outcome, parseErr := parseAttempt(entry, &trace.Attempts[0], options.Tier)
	if parseErr == nil {
		adoptAttempt(&trace, trace.Attempts[0], outcome, options.Tier == TierFinishTaskProbe)
		return trace
	}
	if options.Tier == TierBaseline || options.Tier == TierFinishTaskProbe {
		adoptFailedAttempt(&trace, trace.Attempts[0], parseErr)
		return trace
	}

	retryPrompt := correctedPrompt(rendered, first.Content, trace.Attempts[0].StrictErrorCode)
	if options.MaxPromptChars > 0 && len(retryPrompt) > options.MaxPromptChars {
		adoptFailedAttempt(
			&trace,
			trace.Attempts[0],
			fmt.Errorf("retry prompt size %d exceeds max_prompt_chars %d", len(retryPrompt), options.MaxPromptChars),
		)
		return trace
	}
	retry, err := runMarkdownAttempt(ctx, retryPrompt, rendered.Anchor, 2, options)
	trace.Attempts = append(trace.Attempts, retry)
	trace.ModelCalls = 2
	accumulateAttempt(&trace, retry)
	if err != nil {
		trace.Error = err.Error()
		trace.Content = retry.Content
		trace.GeneratedContent = retry.GeneratedContent
		trace.FinishReason = retry.FinishReason
		return trace
	}
	outcome, parseErr = parseAttempt(entry, &trace.Attempts[1], options.Tier)
	if parseErr != nil {
		adoptFailedAttempt(&trace, trace.Attempts[1], parseErr)
		return trace
	}
	adoptAttempt(&trace, trace.Attempts[1], outcome, false)
	return trace
}

func runMarkdownAttempt(
	ctx context.Context,
	prompt string,
	anchor string,
	attemptNumber int,
	options BaselineRunnerOptions,
) (AttemptTrace, error) {
	attempt := AttemptTrace{
		Attempt:       attemptNumber,
		PromptSHA256:  promptSHA256(prompt),
		PrefillAnchor: anchor,
	}
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
	attempt.Latency = time.Since(started).Seconds()
	if err != nil {
		return attempt, err
	}
	attempt.GeneratedContent = completion.Text
	attempt.Content, attempt.AssemblyMode = assembleMarkdownContent(anchor, completion.Text)
	attempt.FinishReason = string(completion.FinishReason)
	attempt.InputTokens = completion.Usage.PromptTokens
	attempt.OutputTokens = completion.Usage.CompletionTokens
	return attempt, nil
}

func parseAttempt(entry Case, attempt *AttemptTrace, tier Tier) (ParseOutcome, error) {
	calls, strictErr := ParseMarkdownCalls(attempt.Content)
	if strictErr == nil {
		attempt.Adopted = true
		return ParseOutcome{Calls: calls}, nil
	}
	attempt.StrictErrorCode = parseErrorCode(strictErr)
	if isIrrelevance(entry.Category) {
		attempt.NoCall = true
		attempt.Adopted = true
		return ParseOutcome{}, nil
	}
	if tier == TierBaseline {
		attempt.ParseError = strictErr.Error()
		return ParseOutcome{}, strictErr
	}
	// The strict attempt above already ran, so go straight to the compat
	// rewrite instead of re-running ParseMarkdownCalls inside WithMode.
	outcome, compatErr := parseRWKVWireCompatV1(attempt.Content, entry.Functions)
	if compatErr != nil {
		attempt.ParseError = compatErr.Error()
		return ParseOutcome{}, compatErr
	}
	attempt.Repairs = append([]string(nil), outcome.Repairs...)
	attempt.Adopted = true
	return outcome, nil
}

func adoptAttempt(trace *TraceEntry, attempt AttemptTrace, outcome ParseOutcome, finishTaskProbe bool) {
	trace.Content = attempt.Content
	trace.GeneratedContent = attempt.GeneratedContent
	trace.AssemblyMode = attempt.AssemblyMode
	trace.FinishReason = attempt.FinishReason
	trace.ToolCalls = outcome.Calls
	trace.Repairs = append([]string(nil), outcome.Repairs...)
	if finishTaskProbe && len(outcome.Calls) == 0 {
		trace.ProbeSelection = "no_call"
	}
	if attempt.NoCall {
		return
	}
	if finishTaskProbe {
		realCalls := make([]toolchat.ToolCall, 0, len(outcome.Calls))
		finishCalls := 0
		for _, call := range outcome.Calls {
			if call.Name == FinishTaskName {
				finishCalls++
				continue
			}
			realCalls = append(realCalls, call)
		}
		switch {
		case finishCalls > 0 && len(realCalls) == 0:
			trace.ProbeSelection = "finish_task"
			return
		case finishCalls > 0:
			trace.ProbeSelection = "mixed"
		case len(realCalls) > 0:
			trace.ProbeSelection = "real_tool"
		}
		outcome.Calls = realCalls
	}
	result, err := ToResultString(outcome.Calls, nil, resultLanguage(trace.Category))
	if err != nil {
		trace.ParseError = err.Error()
		return
	}
	trace.Result = result
}

func adoptFailedAttempt(trace *TraceEntry, attempt AttemptTrace, err error) {
	trace.Content = attempt.Content
	trace.GeneratedContent = attempt.GeneratedContent
	trace.AssemblyMode = attempt.AssemblyMode
	trace.FinishReason = attempt.FinishReason
	trace.ParseError = err.Error()
}

func accumulateAttempt(trace *TraceEntry, attempt AttemptTrace) {
	trace.Latency += attempt.Latency
	trace.InputTokens += attempt.InputTokens
	trace.OutputTokens += attempt.OutputTokens
}

func assembleMarkdownContent(anchor, generated string) (string, string) {
	candidate := strings.TrimSpace(generated)
	if anchor == `[{"name":"` {
		switch {
		case strings.HasPrefix(candidate, `[`):
			return candidate, "self_contained"
		case strings.HasPrefix(candidate, `{"name":"`):
			return "[" + candidate, "array_elements"
		}
	} else if strings.HasPrefix(candidate, `{"name":"`) {
		return candidate, "self_contained"
	}
	return anchor + generated, "prefill_continuation"
}

func correctedPrompt(rendered RenderedPrompt, content, errorCode string) string {
	promptWithoutAnchor := strings.TrimSuffix(rendered.Prompt, rendered.Anchor)
	return promptWithoutAnchor + content + "\n```\n\nSystem: The previous answer was not a valid " +
		"function-call JSON value (error: " + errorCode + "). Return one corrected function call " +
		"using the same tools and user request. Use the required JSON shape and output no explanation.\n\n" +
		"Assistant: ```json\n" + rendered.Anchor
}

func parseErrorCode(err error) string {
	message := err.Error()
	switch {
	case strings.Contains(message, "empty function call"):
		return "empty"
	case strings.Contains(message, "unterminated JSON fence"):
		return "unterminated_fence"
	case strings.Contains(message, "trailing"):
		return "trailing_content"
	case strings.Contains(message, "arguments must be an object"):
		return "arguments_not_object"
	case strings.Contains(message, "exactly name and arguments"),
		strings.Contains(message, "name is required"),
		strings.Contains(message, "arguments are required"):
		return "wrong_envelope"
	case strings.Contains(message, "decode"):
		return "json_syntax"
	default:
		return "invalid_function_call"
	}
}

func promptSHA256(prompt string) string {
	digest := sha256.Sum256([]byte(prompt))
	return hex.EncodeToString(digest[:])
}

func isIrrelevance(category string) bool {
	return category == "irrelevance" || category == "live_irrelevance"
}

func resultLanguage(category string) Language {
	switch category {
	case "simple_java":
		return LanguageJava
	case "simple_javascript":
		return LanguageJavaScript
	default:
		return LanguagePython
	}
}

func baselineStops(transport Transport) []string {
	if transport == TransportChatCompletionsWrapped {
		return []string{"```", "\n\nUser:", "\nSystem:", "</s>"}
	}
	return []string{"```", "\n\nUser:", "\nUser:", "\nSystem:", "</s>"}
}
