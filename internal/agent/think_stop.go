package agent

import (
	"context"
	"encoding/json"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// maxThinkStopResumes bounds how often one generation is resumed after a
// quoted </tool_call> stop fired inside an open think block.
const maxThinkStopResumes = 4

// continueThroughThinkStops runs one text continuation and resumes it when the
// </tool_call> stop fired on a quotation inside a still-open think block.
//
// Thinking checkpoints quote the action contract while reasoning
// (`…output exactly one <tool_call>{"name":"...","arguments":{...}}`), and the
// client stop then cut the reasoning mid-sentence, so the step ended as an
// unclosed think and was retried. The matched stop goes back into the text and
// generation continues, as if no stop had been configured inside the think.
//
// A complete, real call inside the open think is NOT resumed. In the
// 2026-10-10 think-full retest that shape was ~90% of the cuts (the model
// acts without writing </think>), and resuming it failed 18 of 19 times: the
// model either ends the turn or emits another call. Accepting such a call is a
// parser decision with its own wire experiment (recover-salvage), not a
// transport fix. Role-label stops ("\nUser:") always end the generation, and
// providers that match stops server-side leave Result.Stop empty.
func (r *Runner) continueThroughThinkStops(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	combined, err := r.generator.Continue(ctx, request, sink)
	if err != nil {
		return combined, err
	}
	// Only the current Assistant turn decides whether a think is open; the
	// prompt may end with a withheld "<think" prefix.
	turnPrefix := request.Prompt
	if index := strings.LastIndex(turnPrefix, "Assistant:"); index >= 0 {
		turnPrefix = turnPrefix[index:]
	}
	for resumes := 0; resumes < maxThinkStopResumes; resumes++ {
		if combined.FinishReason != continuation.FinishStop ||
			combined.Stop != "</tool_call>" ||
			!thinkOpen(turnPrefix+combined.Text) ||
			endsWithCompleteCall(combined.Text) {
			break
		}
		stop := combined.Stop
		combined.Text += stop
		combined.Stop = ""
		if sink != nil {
			if err := sink(continuation.Event{Kind: continuation.EventTextDelta, Text: stop}); err != nil {
				combined.FinishReason = continuation.FinishCancelled
				return combined, err
			}
		}
		remaining := request.MaxOutputTokens - spentTokens(combined)
		if remaining <= 0 {
			combined.FinishReason = continuation.FinishLength
			break
		}
		next := request
		next.Prompt = request.Prompt + combined.Text
		next.MaxOutputTokens = remaining
		result, err := r.generator.Continue(ctx, next, sink)
		combined.Text += result.Text
		combined.FinishReason = result.FinishReason
		combined.Stop = result.Stop
		combined.Usage.PromptTokens += result.Usage.PromptTokens
		combined.Usage.CompletionTokens += result.Usage.CompletionTokens
		if err != nil {
			return combined, err
		}
	}
	return combined, nil
}

// thinkOpen reports whether text has opened more think blocks than it closed.
func thinkOpen(text string) bool {
	return strings.Count(text, "<think") > strings.Count(text, "</think>")
}

// endsWithCompleteCall reports whether the text after the last <tool_call> is
// a real call object rather than a quoted template such as
// {"name":"TOOL_NAME","arguments":{...}}.
func endsWithCompleteCall(text string) bool {
	index := strings.LastIndex(text, "<tool_call>")
	if index < 0 {
		return false
	}
	var call struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}
	payload := strings.TrimSpace(text[index+len("<tool_call>"):])
	if json.Unmarshal([]byte(payload), &call) != nil {
		return false
	}
	return call.Name != "" && call.Name != "TOOL_NAME" && call.Name != "..." && isJSONObject(call.Arguments)
}

// spentTokens is the generation's token count, estimated from the text when
// the provider reports no usage (rwkv_lightning cuda streams report none).
// Three bytes per token overestimates both English and Chinese RWKV output, so
// a resume never runs past the original budget.
func spentTokens(result continuation.Result) int {
	if result.Usage.CompletionTokens > 0 {
		return result.Usage.CompletionTokens
	}
	return len(result.Text)/3 + 1
}
