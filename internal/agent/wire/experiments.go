package wire

import "strings"

// Experiments groups opt-in axes used for the G1K wire replication study.
// Empty values preserve all existing product behavior and canonical hashes.
type Experiments struct {
	Recovery     string // none, salvage, json (cumulative parser recovery; empty means preamble, see RecoveryMode)
	Exit         string // no_tool, submit, final_answer, reply; all use answer payload
	History      string // preserve, think-fast (default records canonical action only)
	ThinkControl string // off (training export's instruction with fast prefill)
	Nudge        string // none, think, exit
	Duplicate    string // continue (reject duplicates without forcing answer stage)
	AnswerOpen   string // answer (restore just the answer prefill)
	ToolRole     string // tool (aligned tool results on a Tool: line instead of the user turn)
	GenPoint     string // space (negative control: a stray space after the bare "Assistant:" generation point)
}

// RecoveryMode is the parser recovery level in effect. Preamble recovery —
// executing a lone call that follows a sentence of commentary — is on by
// default since harness v25: every G1 checkpoint writes that shape, and
// rejecting it cost G1L +52 cases on the 2026-10-24 exam. "none" restores the
// strict pre-v25 parser for reproducing old runs.
func (e Experiments) RecoveryMode() string {
	switch e.Recovery {
	case "":
		return "preamble"
	case "none":
		return ""
	}
	return e.Recovery
}

func (e Experiments) entries() [][2]string {
	return [][2]string{{"recovery", e.Recovery}, {"exit", e.Exit}, {"history", e.History}, {"thinkcontrol", e.ThinkControl}, {"nudge", e.Nudge}, {"duplicate", e.Duplicate}, {"answeropen", e.AnswerOpen}, {"toolrole", e.ToolRole}, {"genpoint", e.GenPoint}}
}

func (e Experiments) canonical() string {
	var out strings.Builder
	for _, entry := range e.entries() {
		if entry[1] != "" {
			out.WriteString(";" + entry[0] + "=" + entry[1])
		}
	}
	return out.String()
}

func (s Spec) validateExperiments() error {
	if s.Experiments == (Experiments{}) {
		return nil
	}
	if s.Format != FormatXML || s.Transcript != TranscriptProduct || s.Transport != TransportText {
		return fail("experiment.unsupported", "wire experiments require product XML text transport", "")
	}
	allowed := map[string][]string{
		"recovery": {"", "none", "preamble", "salvage", "json"},
		"exit":     {"", "no_tool", "submit", "final_answer", "reply"},
		"history":  {"", "preserve", "think-fast"}, "nudge": {"", "none", "think", "exit"},
		"thinkcontrol": {"", "off"},
		"duplicate":    {"", "continue"}, "answeropen": {"", "answer"},
		"toolrole": {"", "tool"},
		"genpoint": {"", "space"},
	}
	for _, entry := range s.Experiments.entries() {
		if !known(allowed[entry[0]], entry[1]) {
			return fail("experiment.unknown", "unknown "+entry[0]+"="+entry[1], "")
		}
	}
	if s.Experiments.Exit != "" && (s.Abstain != AbstainNoTool || s.Align != AlignQwen36 || s.Terminal != TerminalNone) {
		return fail("experiment.exit", "exit requires no-tool abstention, aligned catalog and no terminal tool", "")
	}
	if s.Experiments.AnswerOpen != "" && s.Stages != StagesOne {
		return fail("experiment.answeropen", "answeropen requires stages=one", "")
	}
	if s.Experiments.History == "think-fast" && s.Thinking != ThinkingFast {
		return fail("experiment.history", "history=think-fast requires thinking=fast", "")
	}
	return nil
}
