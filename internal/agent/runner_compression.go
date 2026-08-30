package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
)

// Query-aware compression of long fetched pages.
//
// Evidence (test/probes/p5-compression, PREFERENCES.md P5-1..P5-3): with a
// full 5k-10k-token page fed back, the next decision collapses into re-fetch
// loops (1/20 carried the page's answer into the call); with a verbatim
// extraction produced by this same model under a half-open think prefill,
// 17/20 did. The extraction retains the answer 19/20 with the prefill vs 9/20
// without (P1-7: spontaneous <think> drift grows with context length), and
// shrinks ~5k/10k-token pages to ~110 chars.
//
// The raw tool result stays in the step trace (Step.ToolResult); only the
// transcript feedback uses the compressed copy (Step.ToolResultFeedback).

// FetchCompressionThresholdTokens is the estimated-token size above which a
// fetched page is compressed. P5 measured retrieval failure already at 5k
// tokens (full page 1/10 vs compressed 9/10), well below the P1-1 format
// degradation point (10k-20k), so the threshold sits under 5k.
const FetchCompressionThresholdTokens = 4096

// FetchCompressionMaxOutputTokens bounds the extraction call itself.
const FetchCompressionMaxOutputTokens = 256

// compressionFastThinkSuffix mirrors inference.ThinkBlockFast: a half-open
// empty think block prefilled after "Assistant:" suppresses the model's
// spontaneous think drift on raw continuations (P1-7, P5-1).
const compressionFastThinkSuffix = " <think></think"

// EstimateTokens approximates RWKV World tokenizer counts without a vocab:
// P1 bodies measured 3.85-5.42 ASCII chars/token (so 4.0 is near-exact for
// list-heavy text and overestimates prose by up to ~30%), and CJK is charged
// 1.1 tokens per rune. Overestimation only makes budgeting earlier.
func EstimateTokens(text string) int {
	tokens := 0.0
	for _, r := range text {
		if r < 128 {
			tokens += 0.25
		} else {
			tokens += 1.1
		}
	}
	return int(tokens)
}

// compressWebFetchFeedback compresses the pages of a web_fetch tool payload
// for transcript feedback. It reports the replacement payload and whether
// anything changed; failures fall back to the original payload.
func (turn *runnerTurn) compressWebFetchFeedback(
	ctx context.Context,
	payload string,
) (string, bool) {
	var parsed struct {
		OK     bool `json:"ok"`
		Result struct {
			Pages []struct {
				URL       string `json:"url"`
				Content   string `json:"content"`
				Truncated bool   `json:"truncated,omitempty"`
			} `json:"pages"`
		} `json:"result"`
	}
	if json.Unmarshal([]byte(payload), &parsed) != nil || !parsed.OK {
		return payload, false
	}
	if len(parsed.Result.Pages) == 0 {
		return payload, false
	}
	changed := false
	for index, page := range parsed.Result.Pages {
		if EstimateTokens(page.Content) <= FetchCompressionThresholdTokens {
			continue
		}
		compressed, err := turn.r.extractRelevantContent(ctx, turn.task, page.Content)
		if err != nil || strings.TrimSpace(compressed) == "" {
			// Fail open: an unusable extraction must not erase the page.
			continue
		}
		parsed.Result.Pages[index].Content = compressed
		parsed.Result.Pages[index].Truncated = true
		changed = true
	}
	if !changed {
		return payload, false
	}
	encoded, err := json.Marshal(parsed)
	if err != nil {
		return payload, false
	}
	return string(encoded), true
}

// extractRelevantContent runs one raw continuation that copies the
// task-relevant sentences of a page verbatim (P5-1: verbatim extraction with
// fast think retained the answer 19/20; abstractive summary 14/20).
func (r *Runner) extractRelevantContent(
	ctx context.Context,
	task string,
	content string,
) (string, error) {
	if r.generator == nil {
		return "", fmt.Errorf("compression requires the text-continuation path")
	}
	var prompt strings.Builder
	fmt.Fprintf(&prompt, "User: Subtask: %s\n\n", strings.TrimSpace(task))
	prompt.WriteString("A web page was fetched for this subtask. Copy every sentence of the page that is relevant to the subtask, verbatim and in the original order. Keep all numbers, names, dates, and URLs exactly as written. Output only the copied sentences.\n\n")
	prompt.WriteString("Page:\n")
	prompt.WriteString(content)
	prompt.WriteString("\n\nAssistant:")
	prompt.WriteString(compressionFastThinkSuffix)

	request := r.options.Generation
	request.Prompt = prompt.String()
	request.MaxOutputTokens = FetchCompressionMaxOutputTokens
	request.Stops = []string{"\n\nUser:", "\nUser:", "\nSystem:", "</s>"}
	result, err := r.generator.Continue(ctx, request, nil)
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(result.Text), nil
}
