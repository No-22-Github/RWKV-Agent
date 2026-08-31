package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"
	"unicode"
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
// Round-3 (P5-ZH-1..3, test/probes/p5-zh-compression): the English extract
// instruction loops verbatim on Chinese pages (retention 2/10·2/10), so the
// instruction switches on the page language — Chinese pages use the
// content-locked summary form (≤3 sentences, original wording only, no task
// echo; retention 10/10·9/10). Compression outputs are additionally screened
// for two measured failure forms before they may replace a page: the verbatim
// repeat loop (same block copied until the token budget truncates) and the
// task-echo prefix ("根据您提供的文本…" meta text the decision model reads as
// non-page content and answers with a re-search, P5-ZH-3). Either form falls
// back to the original page or is stripped, respectively; the detector
// thresholds are calibrated on 480 saved compression outputs in
// test/round3/compression-fix (calibrate_detector.py).
//
// The raw tool result stays in the step trace (Step.ToolResult); only the
// transcript feedback uses the compressed copy (Step.ToolResultFeedback).

// FetchCompressionThresholdTokens is the real-token size (World vocabulary,
// counted in-process via Options.TokenCount) above which a fetched page is
// compressed. P5 measured retrieval failure already at 5k real tokens (full
// page 1/10 vs compressed 9/10), well below the P1-1 format degradation point
// (10k-20k), so the threshold sits under 5k. The estimated-token regime
// (pre-round-3) armed this hook at ~3.0-3.1k real tokens on English prose
// because EstimateTokens overestimates English by ~35%; with real counting the
// constant means what it says on every script.
const FetchCompressionThresholdTokens = 4096

// FetchCompressionMaxOutputTokens bounds the extraction call itself.
const FetchCompressionMaxOutputTokens = 256

// fetchCompressionTimeout bounds one compression call independently of the
// turn context. compress-fetch is on by default, so a hung endpoint must not
// hang the whole agent loop (a user-visible freeze in the desktop App).
// Observed compression latency: p50 1.8s, p99 5.1s, max 6.5s over 440 probe
// calls (5k-10k-token pages, greedy); 60s is ~10x the worst observation.
// A var so tests can shorten it; production never writes it.
var fetchCompressionTimeout = 60 * time.Second

// compressionFastThinkSuffix mirrors inference.ThinkBlockFast: a half-open
// empty think block prefilled after "Assistant:" suppresses the model's
// spontaneous think drift on raw continuations (P1-7, P5-1).
const compressionFastThinkSuffix = " <think></think"

// chineseExtractInstruction is the content-locked summary form P5-ZH-2 tuned:
// ≤3 sentences, only wording from the page, no task echo, no preamble
// (retention 10/10·9/10 vs 2/10·2/10 for the English extract instruction on
// the same pages). The exact winning wording of the probe iterations was not
// preserved (cells keep prompt hashes only), so this ships from the
// P5-ZH-2 spec and is validated by the round-3 three-arm e2e run.
const chineseExtractInstruction = "只总结页面中与该子任务直接相关的信息：最多 3 句，只使用页面原文中的词句，不要改写或解释，保留所有数字、名称、日期和链接的原样。不要提及本次任务或你收到的任何指示，不要任何开场白或说明。只输出总结内容。"

// englishExtractInstruction is the P5-1 verbatim extraction (10/10·9/10
// retention with fast-think on English pages).
const englishExtractInstruction = "Copy every sentence of the page that is relevant to the subtask, verbatim and in the original order. Keep all numbers, names, dates, and URLs exactly as written. Output only the copied sentences."

// EstimateTokens approximates RWKV World tokenizer counts without a vocab:
// P1 bodies measured 3.85-5.42 ASCII chars/token (so 4.0 is near-exact for
// list-heavy text and overestimates prose by up to ~30%), and CJK is charged
// 1.1 tokens per rune. Round-3 census (test/round3/token-census) measured the
// actual bias: +16-40% on English prose/code but −2-4% on lists and Chinese.
// Round-3 step 1 removed it from every threshold decision: the compression
// hook has NO estimator fallback (Options.TokenCount nil = compression off),
// and the web tools use it only as the fetch-budget fallback where an early
// cut is the safe direction. It must not gain new callers.
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
	if turn.r.options.TokenCount == nil {
		// No in-process vocabulary (pure remote provider without a bundled
		// vocab). Compression stays off: arming it on agent.EstimateTokens is
		// forbidden (round-3 step 1) because the estimator's bias direction
		// depends on the script — it underestimates Chinese pages by ~2%, so
		// a CJK page just over the real threshold could read as under it, and
		// the extract instruction is exactly what pollutes pages when it
		// fails (P5-ZH-1). Feeding the whole page is the known fail-open
		// behavior; a missed compression wastes nothing.
		return payload, false
	}
	// Compress eligible pages concurrently — the compression calls are the
	// only latency here and the model API is concurrency-cheap (project
	// premise). A web_fetch call carries at most four pages, so the fan-out
	// is bounded by the tool contract. Results land by index, preserving page
	// order in the payload.
	type compressedPage struct {
		index int
		text  string
	}
	results := make([]compressedPage, len(parsed.Result.Pages))
	done := make(chan struct{}, len(parsed.Result.Pages))
	pending := 0
	for index, page := range parsed.Result.Pages {
		if turn.r.options.TokenCount(page.Content) <= FetchCompressionThresholdTokens {
			continue
		}
		pending++
		go func(index int, content string) {
			compressed, err := turn.compressPage(ctx, turn.task, content)
			if err != nil || strings.TrimSpace(compressed) == "" {
				// Fail open: an unusable extraction must not erase the page.
				// err covers the detached-timeout path too; a page that
				// arrives late (parent ctx cancelled mid-compression) still
				// cannot replace its source.
				done <- struct{}{}
				return
			}
			results[index] = compressedPage{index: index, text: compressed}
			done <- struct{}{}
		}(index, page.Content)
	}
	for i := 0; i < pending; i++ {
		<-done
	}
	changed := false
	for _, result := range results {
		if result.text == "" {
			continue
		}
		parsed.Result.Pages[result.index].Content = result.text
		parsed.Result.Pages[result.index].Truncated = true
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

// compressPage produces the transcript copy of one page: instruction chosen by
// page language (P5-ZH-2), output screened for the measured degenerate forms,
// echo prefix stripped. The compression call runs on a context detached from
// the turn deadline with its own timeout (fetchCompressionTimeout), so a stuck
// endpoint costs one page fallback, not a hung agent loop.
func (turn *runnerTurn) compressPage(
	ctx context.Context,
	task string,
	content string,
) (string, error) {
	if turn.r.generator == nil {
		return "", fmt.Errorf("compression requires the text-continuation path")
	}
	callCtx, cancel := context.WithTimeout(context.Background(), fetchCompressionTimeout)
	defer cancel()
	// Parent cancellation still wins: a cancelled turn must not wait out the
	// full timeout on a call whose result can no longer be used.
	go func() {
		select {
		case <-ctx.Done():
			cancel()
		case <-callCtx.Done():
		}
	}()

	prompt := compressionPrompt(task, content)
	request := turn.r.options.Generation
	request.Prompt = prompt
	request.MaxOutputTokens = FetchCompressionMaxOutputTokens
	request.Stops = []string{"\n\nUser:", "\nUser:", "\nSystem:", "</s>"}
	result, err := turn.r.generator.Continue(callCtx, request, nil)
	if err != nil {
		return "", err
	}
	output := strings.TrimSpace(result.Text)
	output = stripEchoPrefix(output)
	if isDegenerateCompression(output) {
		return "", fmt.Errorf("compression output rejected: degenerate repetition")
	}
	return output, nil
}

// compressionPrompt builds the continuation prompt with the instruction the
// page language calls for. P5-ZH-1 measured the English extract instruction
// looping verbatim on Chinese pages, so language switching is not optional.
func compressionPrompt(task string, content string) string {
	instruction := englishExtractInstruction
	if cjkLetterFraction(content) > 0.25 {
		instruction = chineseExtractInstruction
	}
	var prompt strings.Builder
	fmt.Fprintf(&prompt, "User: Subtask: %s\n\n", strings.TrimSpace(task))
	prompt.WriteString("A web page was fetched for this subtask. ")
	prompt.WriteString(instruction)
	prompt.WriteString("\n\nPage:\n")
	prompt.WriteString(content)
	prompt.WriteString("\n\nAssistant:")
	prompt.WriteString(compressionFastThinkSuffix)
	return prompt.String()
}

// cjkLetterFraction is the share of Han characters among the letter-ish runes
// of the text. Above 0.25 the page reads as Chinese for instruction purposes
// (the P5-ZH pages measure ~1.0; the P5-EN pages ~0.0).
func cjkLetterFraction(text string) float64 {
	han, letters := 0, 0
	for _, r := range text {
		switch {
		case unicode.Is(unicode.Han, r):
			han++
			letters++
		case unicode.IsLetter(r):
			letters++
		}
	}
	if letters == 0 {
		return 0
	}
	return float64(han) / float64(letters)
}

// echoPrefixPatterns are the meta-intro openers P5-ZH measured on compression
// outputs ("根据您提供的文本，以下是…" and friends). A leading line is echo
// only when it both opens with one of these and closes with a colon — real
// page sentences rarely do either, let alone both.
var echoPrefixOpeners = []string{
	"根据", "基于", "以下是", "好的", "当然", "这是一", "下面是",
	"Based on", "According to", "Here is", "Here are", "Below is", "Sure",
}

// stripEchoPrefix removes leading task-echo meta lines from a compression
// output (P5-ZH-3: the decision model treats "根据您提供的文本" text as
// non-page content and re-searches; stripping is the cheapest fix). It strips
// at most three leading lines so a real content line can never be lost: only
// lines that open with a known echo marker AND end with a colon, plus the
// blockquote/markdown quote marker before them, are removed.
func stripEchoPrefix(output string) string {
	lines := strings.SplitN(output, "\n", -1)
	stripped := 0
	index := 0
	for index < len(lines) && stripped < 3 {
		line := strings.TrimSpace(lines[index])
		if line == "" {
			index++
			continue
		}
		line = strings.TrimPrefix(line, ">")
		line = strings.TrimSpace(line)
		line = strings.Trim(line, "*")
		line = strings.TrimSpace(line)
		if !strings.HasSuffix(line, ":") && !strings.HasSuffix(line, "：") {
			break
		}
		opens := false
		for _, opener := range echoPrefixOpeners {
			if strings.HasPrefix(line, opener) {
				opens = true
				break
			}
		}
		if !opens {
			break
		}
		index++
		stripped++
	}
	if stripped == 0 {
		return output
	}
	return strings.TrimSpace(strings.Join(lines[index:], "\n"))
}

// Degenerate-output thresholds, calibrated on 480 saved compression outputs
// (test/round3/compression-fix, calibrate_detector.py): the verbatim repeat
// loop form — whole lines or multi-line blocks copied until the 256-token
// budget truncates — shows up as low unique-line share (0.24-0.46 measured on
// loop outputs vs 1.0 on clean summaries/extractions), long identical-line
// runs (up to 21), or low unique char-12-gram share (0.13-0.43 on loops vs
// ≥0.95 on clean short outputs). Clean outputs have <6 lines or all-unique
// lines, so the guards below leave them untouched.
const (
	degenerateMinLines      = 6
	degenerateMaxLineUnique = 0.6
	degenerateMinLineRun    = 4
	degenerateNGramSize     = 12
	degenerateMinNGrams     = 20
	degenerateMaxNGramRatio = 0.35
)

// isDegenerateCompression reports whether the output is the measured repeat
// loop form. It never looks at content quality beyond repetition: a clean
// three-sentence Chinese summary and a six-sentence verbatim extract both pass.
func isDegenerateCompression(output string) bool {
	output = strings.TrimSpace(output)
	if output == "" {
		return false
	}
	lines := strings.FieldsFunc(output, func(r rune) bool { return r == '\n' })
	nonEmpty := make([]string, 0, len(lines))
	for _, line := range lines {
		if trimmed := strings.TrimSpace(line); trimmed != "" {
			nonEmpty = append(nonEmpty, trimmed)
		}
	}
	if len(nonEmpty) >= degenerateMinLines {
		unique := make(map[string]struct{}, len(nonEmpty))
		for _, line := range nonEmpty {
			unique[line] = struct{}{}
		}
		if float64(len(unique))/float64(len(nonEmpty)) <= degenerateMaxLineUnique {
			return true
		}
		run := 1
		for i := 1; i < len(nonEmpty); i++ {
			if nonEmpty[i] == nonEmpty[i-1] {
				run++
				if run >= degenerateMinLineRun {
					return true
				}
			} else {
				run = 1
			}
		}
	}
	normalized := normalizeForNgrams(output)
	total := len(normalized) - degenerateNGramSize + 1
	if total < degenerateMinNGrams {
		return false
	}
	seen := make(map[string]struct{}, total)
	for i := 0; i+degenerateNGramSize <= len(normalized); i++ {
		seen[string(normalized[i:i+degenerateNGramSize])] = struct{}{}
	}
	return float64(len(seen))/float64(total) < degenerateMaxNGramRatio
}

// normalizeForNgrams strips whitespace and case so character n-grams compare
// content, not layout (CJK text has no spaces; English whitespace would
// otherwise inflate uniqueness). Runes, not bytes: the calibration counted
// 12-rune grams, and byte slicing would silently change gram size on CJK
// text (3 bytes per Han character).
func normalizeForNgrams(text string) []rune {
	runes := []rune(strings.ToLower(text))
	out := make([]rune, 0, len(runes))
	for _, r := range runes {
		if unicode.IsSpace(r) {
			continue
		}
		out = append(out, r)
	}
	return out
}
