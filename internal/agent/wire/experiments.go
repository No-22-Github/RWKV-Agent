package wire

import "strings"

// Experiments groups opt-in axes used for the G1K wire replication study.
// Empty values preserve all existing product behavior and canonical hashes.
type Experiments struct {
	Recovery     string // preamble, salvage, json (cumulative parser recovery)
	Exit         string // no_tool, submit, final_answer, reply; all use answer payload
	History      string // preserve, think-fast (default records canonical action only)
	ThinkControl string // off (training export's instruction with fast prefill)
	Nudge        string // none, think, exit
	Duplicate    string // continue (reject duplicates without forcing answer stage)
	AnswerOpen   string // answer (restore just the answer prefill)
}

func (e Experiments) entries() [][2]string {
	return [][2]string{{"recovery", e.Recovery}, {"exit", e.Exit}, {"history", e.History}, {"thinkcontrol", e.ThinkControl}, {"nudge", e.Nudge}, {"duplicate", e.Duplicate}, {"answeropen", e.AnswerOpen}}
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
		"recovery": {"", "preamble", "salvage", "json"},
		"exit":     {"", "no_tool", "submit", "final_answer", "reply"},
		"history":  {"", "preserve", "think-fast"}, "nudge": {"", "none", "think", "exit"},
		"thinkcontrol": {"", "off"},
		"duplicate":    {"", "continue"}, "answeropen": {"", "answer"},
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
