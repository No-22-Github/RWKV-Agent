package agent

import (
	"regexp"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// answerPreview turns the raw deltas of one model step into a best-effort live
// preview of the final answer for an interactive observer. It never decides
// anything: the parser still owns the step once generation finishes, and the
// committed Result.Output replaces the preview. A step that turns out to be a
// tool call or a rejected output is retracted with EventAnswerReset.
//
// The preview is conservative. Output that could still become a tool envelope,
// a fenced call or an unclosed think block is held back, so a viewer may see
// an answer late but never sees call JSON flash by as prose.
type answerPreview struct {
	turn     *runnerTurn
	step     int
	injected bool
	raw      strings.Builder
	sent     string
}

func (turn *runnerTurn) newAnswerPreview(step int, injected bool) *answerPreview {
	if turn.observer == nil && turn.r.options.Observe == nil {
		return nil
	}
	return &answerPreview{turn: turn, step: step, injected: injected}
}

func (preview *answerPreview) sink() continuation.EventSink {
	if preview == nil {
		return nil
	}
	return func(event continuation.Event) error {
		if event.Kind != continuation.EventTextDelta || event.Text == "" {
			return nil
		}
		preview.raw.WriteString(event.Text)
		visible, ok := previewAnswerText(preview.turn.postProcessModelOutput(preview.raw.String(), preview.injected))
		if !ok || visible == preview.sent {
			return nil
		}
		if !strings.HasPrefix(visible, preview.sent) {
			preview.emit(Event{Kind: EventAnswerReset, Step: preview.step})
			preview.sent = ""
		}
		preview.emit(Event{Kind: EventAnswerDelta, Step: preview.step, Text: visible[len(preview.sent):]})
		preview.sent = visible
		return nil
	}
}

// retract withdraws a preview whose step did not end as the final answer.
func (preview *answerPreview) retract() {
	if preview == nil || preview.sent == "" {
		return
	}
	preview.emit(Event{Kind: EventAnswerReset, Step: preview.step})
	preview.sent = ""
}

func (preview *answerPreview) emit(event Event) {
	preview.turn.r.observe(event, preview.turn.observer)
}

// callFence matches the start of a fenced tool-call envelope: a fence whose
// body opens a JSON object. Fences around ordinary code stay answer content.
var callFence = regexp.MustCompile("```(?:json)?\\s*\\{")

// previewAnswerText extracts the displayable answer from a partial model
// output, or reports false while the output could still be something else.
func previewAnswerText(output string) (string, bool) {
	candidate := strings.TrimSpace(output)
	if strings.HasPrefix(candidate, "<think>") {
		stripped := wire.StripLeadingThinkBlocks(candidate)
		if strings.HasPrefix(stripped, "<think>") {
			return "", false
		}
		candidate = stripped
	}
	candidate = wire.TrimWithheldOpening(candidate)
	if rest, ok := strings.CutPrefix(candidate, "<answer>"); ok {
		candidate = strings.TrimLeft(rest, " \t\r\n")
		if end := strings.Index(candidate, "</answer>"); end >= 0 {
			candidate = candidate[:end]
		}
		return strings.TrimRight(holdPartialTag(candidate), " \t\r\n"), true
	}
	if candidate == "" || strings.ContainsAny(candidate[:1], "<`{[") {
		// A tool envelope, a fenced call, bare call JSON or a not-yet-complete
		// "<answer>" all start this way; wait for the committed output.
		return "", false
	}
	if index := strings.Index(candidate, "<tool_call"); index >= 0 {
		candidate = candidate[:index]
	}
	if match := callFence.FindStringIndex(candidate); match != nil {
		candidate = candidate[:match[0]]
	} else if index := strings.LastIndex(candidate, "```"); index >= 0 &&
		strings.Count(candidate, "```")%2 == 1 && len(candidate)-index < len("```json\n{") {
		// A fence that has only just opened may still turn into a call; a
		// closing fence is plain answer content.
		candidate = candidate[:index]
	}
	return strings.TrimRight(holdPartialTag(candidate), " \t\r\n"), true
}

// holdPartialTag drops a trailing "<..." that has not closed yet, so a tag
// split across deltas ("</ans", "<tool_") is never shown half-written.
func holdPartialTag(text string) string {
	index := strings.LastIndex(text, "<")
	if index < 0 || strings.Contains(text[index:], ">") || len(text)-index > len("</tool_calls>") {
		return text
	}
	return text[:index]
}
