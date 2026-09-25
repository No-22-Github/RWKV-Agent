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
	Turn        int    `json:"turn"`
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
	// Source names the dataset the row came from ("base700", "distill-b01"),
	// so rows from several batches can be told apart after they are packed.
	Source string `json:"source"`
	// SeededFromTest reports whether the case was derived from a test-bank
	// seed (records mode) . Cases written for distillation are never seeded.
	SeededFromTest bool `json:"seeded_from_test"`
	// CaseTags is the case's label block, normalised for records.
	CaseTags CaseTags `json:"case_tags"`
	// Traj describes what the trajectory actually did in this row's turn.
	Traj TrajStats `json:"traj"`
	// Kind is Traj's behaviour class (direct, local, web, write, script,
	// refuse, clarify, smalltalk), derived by docs/distill-workflow.md §4.4.2.
	Kind string `json:"kind"`
}

// CaseTags is the label block a training row carries. Cleaning, mixing and
// post-training analysis group by these fields, so a row never has to be
// joined back to its case to be classified.
type CaseTags struct {
	Scenario  string     `json:"scenario"`
	TaskType  string     `json:"task_type"`
	Traps     []string   `json:"traps"`
	Level     *string    `json:"level"`
	Family    string     `json:"family"`
	Behaviors []string   `json:"behaviors"`
	Origin    *TagOrigin `json:"origin,omitempty"`
}

// TagOrigin keeps the raw record labels normalised CaseTags were derived
// from, so a mapping decision can be re-audited without the source records.
type TagOrigin struct {
	ParentSeedID string   `json:"parent_seed_id"`
	Branch       string   `json:"branch"`
	Split        string   `json:"split"`
	BehaviorTags []string `json:"behavior_tags"`
}

// TrajStats is what the model did in one row's turn. Tool counts cover the
// turn's supervised outputs only; UnsupervisedOutputs counts the ones marked
// context-only (a recovery prefix), which are replayed but never trained.
type TrajStats struct {
	TurnsTotal          int      `json:"turns_total"`
	ToolCalls           int      `json:"tool_calls"`
	ToolSeq             []string `json:"tool_seq"`
	ZeroCall            bool     `json:"zero_call"`
	Web                 bool     `json:"web"`
	Local               bool     `json:"local"`
	Writes              bool     `json:"writes"`
	UnsupervisedOutputs int      `json:"unsupervised_outputs"`
	FinalKind           string   `json:"final_kind"`
	Tokens              int      `json:"tokens"`
}

// roleBoundaries end an assistant block inside a rendered transcript.
var roleBoundaries = []string{"\n\nUser:", "\n\nSystem:", "\n\nTool:"}

const toolCallClose = "</tool_call>"

// CorpusText is one case's assembled training text, or one turn's when the
// case has several.
type CorpusText struct {
	Text          string
	LossSpans     [][2]int
	Canonicalized int
	// Turn is the 1-based turn the text ends in; Generations and Supervised
	// count the script outputs it covers.
	Turn        int
	Generations int
	Supervised  int
	// FirstOutput is the index of the turn's first script output, so a caller
	// can recover the outputs (and their supervised flags) a row covers.
	FirstOutput int
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
	return buildSegment(calls, entry.Outputs, 0)
}

// BuildCorpusTurns is BuildCorpusText for multi-turn cases: turns[i] is the
// turn of calls[i]. Between turns the harness commits history without the
// per-step reminders, so the next turn's prompt is not an extension of the
// last one and a single row would show the model a transcript it never sees.
// Each turn becomes its own row whose text ends at that turn's last output;
// earlier turns appear only as the committed history the harness renders,
// and only the turn's own outputs get loss spans. Within a turn the
// append-only rule of BuildCorpusText still holds; across a boundary the next
// prompt must at least carry the previous turn's last output.
func BuildCorpusTurns(calls []ModelCallTrace, turns []int, entry ScriptEntry) ([]CorpusText, error) {
	if len(calls) != len(entry.Outputs) {
		return nil, fmt.Errorf(
			"harness made %d generations, script has %d outputs", len(calls), len(entry.Outputs),
		)
	}
	if len(turns) != len(calls) {
		return nil, fmt.Errorf("%d turn numbers for %d generations", len(turns), len(calls))
	}
	var texts []CorpusText
	for start := 0; start < len(calls); {
		end := start + 1
		for end < len(calls) && turns[end] == turns[start] {
			end++
		}
		if end < len(calls) {
			if turns[end] < turns[start] {
				return nil, fmt.Errorf("generation %d goes back from turn %d to %d", end+1, turns[start], turns[end])
			}
			answer := strings.TrimSpace(calls[end-1].Response.Text)
			if !strings.Contains(calls[end].Request.Prompt, answer) {
				return nil, fmt.Errorf("turn %d history does not carry turn %d's last output", turns[end], turns[start])
			}
		}
		text, err := buildSegment(calls[start:end], entry.Outputs[start:end], start)
		if err != nil {
			return nil, err
		}
		text.Turn = turns[start]
		text.FirstOutput = start
		texts = append(texts, text)
		start = end
	}
	return texts, nil
}

// buildSegment assembles the text of consecutive append-only generations;
// offset numbers them in error messages.
func buildSegment(calls []ModelCallTrace, outputs []ScriptOutput, offset int) (CorpusText, error) {
	var spans [][2]int
	canonicalized := 0
	for index, call := range calls {
		if call.Error != "" {
			return CorpusText{}, fmt.Errorf("generation %d failed: %s", offset+index+1, call.Error)
		}
		if call.Response.Text != outputs[index].Text {
			return CorpusText{}, fmt.Errorf("generation %d response differs from the script", offset+index+1)
		}
		if index == len(calls)-1 {
			break
		}
		prompt, next := call.Request.Prompt, calls[index+1].Request.Prompt
		if !strings.HasPrefix(next, prompt) {
			return CorpusText{}, fmt.Errorf("transcript is not append-only after generation %d", offset+index+1)
		}
		block := assistantBlock(next[len(prompt):])
		match := compareAction(block, call.Response.Text)
		if match == actionDiffers {
			return CorpusText{}, fmt.Errorf(
				"generation %d written back as %q, script output %q",
				offset+index+1, strings.TrimSpace(block), strings.TrimSpace(call.Response.Text),
			)
		}
		if match == actionCanonicalized {
			canonicalized++
		}
		if outputs[index].Supervised {
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
	if outputs[len(calls)-1].Supervised {
		spans = append(spans, [2]int{len(prompt) + len(separator), len(text)})
	}
	return CorpusText{
		Text: text, LossSpans: runeSpans(text, spans), Canonicalized: canonicalized,
		Generations: len(calls), Supervised: len(spans),
	}, nil
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
