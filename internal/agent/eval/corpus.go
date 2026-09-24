package eval

import (
	"encoding/json"
	"fmt"
	"reflect"
	"strings"
	"unicode/utf8"
)

// CorpusRow is one training row rendered from a scripted eval run: the final
// transcript text plus the character spans of the supervised assistant
// outputs. Spans are Unicode code point offsets, the unit the Python corpus
// renderer (tooling/workv1_wire.py) emits.
type CorpusRow struct {
	Text      string     `json:"text"`
	LossSpans [][2]int   `json:"loss_spans"`
	Meta      CorpusMeta `json:"meta"`
}

type CorpusMeta struct {
	CaseID      string `json:"case_id"`
	Passed      bool   `json:"passed"`
	Generations int    `json:"generations"`
	Supervised  int    `json:"supervised"`
	// Canonicalized counts tool calls the harness wrote back with different
	// bytes but the same JSON (Go escapes <, > and & as \u003c...); the row
	// carries the harness bytes, which are what the model sees in history.
	Canonicalized  int    `json:"canonicalized"`
	WireCanonical  string `json:"wire_canonical,omitempty"`
	WireHash       string `json:"wire_hash,omitempty"`
	HarnessVersion string `json:"harness_version,omitempty"`
}

// roleBoundaries end an assistant block inside a rendered transcript.
var roleBoundaries = []string{"\n\nUser:", "\n\nSystem:", "\n\nTool:"}

const toolCallClose = "</tool_call>"

// CorpusText is one case's assembled training text.
type CorpusText struct {
	Text          string
	LossSpans     [][2]int
	Canonicalized int
}

// BuildCorpusText assembles one case's training text from the generations
// the harness made while replaying entry. calls must be the case's model
// calls in order. It fails instead of guessing whenever the harness diverged
// from the script: a different number of generations, a generation error, a
// transcript that is not append-only, or an assistant turn written back with
// different content than the teacher output.
func BuildCorpusText(calls []ModelCallTrace, entry ScriptEntry) (CorpusText, error) {
	if len(calls) != len(entry.Outputs) {
		return CorpusText{}, fmt.Errorf(
			"harness made %d generations, script has %d outputs", len(calls), len(entry.Outputs),
		)
	}
	var spans [][2]int
	canonicalized := 0
	for index, call := range calls {
		if call.Error != "" {
			return CorpusText{}, fmt.Errorf("generation %d failed: %s", index+1, call.Error)
		}
		if call.Response.Text != entry.Outputs[index].Text {
			return CorpusText{}, fmt.Errorf("generation %d response differs from the script", index+1)
		}
		if index == len(calls)-1 {
			break
		}
		prompt, next := call.Request.Prompt, calls[index+1].Request.Prompt
		if !strings.HasPrefix(next, prompt) {
			return CorpusText{}, fmt.Errorf("transcript is not append-only after generation %d", index+1)
		}
		block := assistantBlock(next[len(prompt):])
		match := compareAction(block, call.Response.Text)
		if match == actionDiffers {
			return CorpusText{}, fmt.Errorf(
				"generation %d written back as %q, script output %q",
				index+1, strings.TrimSpace(block), strings.TrimSpace(call.Response.Text),
			)
		}
		if match == actionCanonicalized {
			canonicalized++
		}
		if entry.Outputs[index].Supervised {
			spans = append(spans, trimmedSpan(prompt, block))
		}
	}
	last := calls[len(calls)-1]
	final := strings.TrimSpace(last.Response.Text)
	if strings.Contains(final, "<tool_call>") && !strings.HasSuffix(final, toolCallClose) {
		// The stop sequence consumed the closing tag; the harness restores it
		// when it writes the call back, so the trained text carries it too.
		final += toolCallClose
	}
	prompt := last.Request.Prompt
	separator := ""
	if strings.HasSuffix(prompt, ":") {
		separator = " "
	}
	text := prompt + separator + final
	if entry.Outputs[len(calls)-1].Supervised {
		spans = append(spans, [2]int{len(prompt) + len(separator), len(text)})
	}
	return CorpusText{Text: text, LossSpans: runeSpans(text, spans), Canonicalized: canonicalized}, nil
}

// assistantBlock returns the assistant content at the head of rest: up to
// the next role label, or all of rest when none follows.
func assistantBlock(rest string) string {
	end := len(rest)
	for _, boundary := range roleBoundaries {
		if position := strings.Index(rest, boundary); position >= 0 && position < end {
			end = position
		}
	}
	return rest[:end]
}

type actionMatch int

const (
	actionIdentical actionMatch = iota
	actionCanonicalized
	actionDiffers
)

// compareAction compares a written-back assistant block with the raw output.
// Identical allows only surrounding whitespace and a closing tag the stop
// sequence consumed; canonicalized means both are tool calls whose JSON
// payloads decode to the same value (the harness re-marshals calls).
func compareAction(block, output string) actionMatch {
	written := strings.TrimSpace(block)
	raw := strings.TrimSpace(output)
	if written == raw || (strings.Contains(raw, "<tool_call>") && written == raw+toolCallClose) {
		return actionIdentical
	}
	left, leftOK := toolCallPayload(written)
	right, rightOK := toolCallPayload(raw)
	if leftOK && rightOK && reflect.DeepEqual(left, right) {
		return actionCanonicalized
	}
	return actionDiffers
}

func toolCallPayload(text string) (any, bool) {
	body, ok := strings.CutPrefix(text, "<tool_call>")
	if !ok {
		return nil, false
	}
	body = strings.TrimSuffix(body, toolCallClose)
	var value any
	if err := json.Unmarshal([]byte(body), &value); err != nil {
		return nil, false
	}
	return value, true
}

// trimmedSpan is the byte span of block (appended right after prompt)
// without its surrounding whitespace.
func trimmedSpan(prompt, block string) [2]int {
	start := len(prompt) + len(block) - len(strings.TrimLeft(block, " \t\r\n"))
	end := len(prompt) + len(strings.TrimRight(block, " \t\r\n"))
	return [2]int{start, end}
}

func runeSpans(text string, spans [][2]int) [][2]int {
	converted := make([][2]int, len(spans))
	for index, span := range spans {
		converted[index] = [2]int{
			utf8.RuneCountInString(text[:span[0]]),
			utf8.RuneCountInString(text[:span[1]]),
		}
	}
	return converted
}
