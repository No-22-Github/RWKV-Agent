package geval

import (
	"regexp"
	"strings"
)

// The think-sft training format (bench/distill/think-sft/sample-format.md):
//
//	User: q1\n\nAssistant: <think></think>a1\n\nUser: q2\n\nAssistant: <think
//
// No System block; history answers carry an empty think block; the prompt
// stops at `<think` so the model writes the `>` itself; no block holds a
// blank line. Collapsing follows bench/distill/tools/think_sft/collapse_blank.py.

const (
	thinkSeed  = "<think"
	thinkOpen  = "<think>"
	thinkClose = "</think>"
	turnStop   = "\n\nUser:"
)

var (
	blankRun  = regexp.MustCompile(`\n[ \t\x{3000}]*(?:\n[ \t\x{3000}]*)+`)
	trailWS   = regexp.MustCompile(`[ \t\x{3000}]+\n`)
	userLabel = regexp.MustCompile(`\n\n(System|User|Assistant):`)
)

// collapseBlank removes blank lines (also lines holding only spaces) and
// trailing spaces, so a block never contains the `\n\n` turn separator.
func collapseBlank(text string) string {
	text = strings.ReplaceAll(text, "\r\n", "\n")
	text = blankRun.ReplaceAllString(text, "\n")
	text = trailWS.ReplaceAllString(text, "\n")
	return strings.TrimSpace(text)
}

// Exchange is one finished turn of history.
type Exchange struct {
	User   string
	Answer string
}

// renderPrompt builds the RWKV prompt for the next user turn.
func renderPrompt(history []Exchange, user string) string {
	var b strings.Builder
	for _, h := range history {
		b.WriteString("User: ")
		b.WriteString(collapseBlank(h.User))
		b.WriteString("\n\nAssistant: <think></think>")
		b.WriteString(collapseBlank(h.Answer))
		b.WriteString("\n\n")
	}
	b.WriteString("User: ")
	b.WriteString(collapseBlank(user))
	b.WriteString("\n\nAssistant: ")
	b.WriteString(thinkSeed)
	return b.String()
}

// Parsed is a generation split into thinking and the final answer.
type Parsed struct {
	Think string
	// Answer is the text after </think>, trimmed. Empty when the think
	// block never closed.
	Answer string
	// ThinkClosed reports a well-formed `<think>…</think>` block.
	ThinkClosed bool
	// EmptyThink is `<think></think>` with nothing (or only whitespace)
	// inside: the model skipped thinking.
	EmptyThink bool
}

// parseOutput splits raw output, the continuation after the `<think` seed
// with the seed put back in front.
func parseOutput(raw string) Parsed {
	if !strings.HasPrefix(raw, thinkOpen) {
		// The model did not complete the tag; nothing reliable to split.
		return Parsed{}
	}
	body := raw[len(thinkOpen):]
	end := strings.Index(body, thinkClose)
	if end < 0 {
		return Parsed{Think: strings.TrimSpace(body)}
	}
	think := strings.TrimSpace(body[:end])
	answer := body[end+len(thinkClose):]
	answer = strings.TrimSpace(cutRoleLabel(answer))
	return Parsed{Think: think, Answer: answer, ThinkClosed: true, EmptyThink: think == ""}
}

// cutRoleLabel drops a turn the model invented after its answer when the
// stop did not fire (a chat endpoint matching no stop, for one).
func cutRoleLabel(text string) string {
	if loc := userLabel.FindStringIndex(text); loc != nil {
		return text[:loc[0]]
	}
	return text
}
