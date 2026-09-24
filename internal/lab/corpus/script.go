package corpus

import (
	"fmt"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// The replay script format lives in internal/agent/eval/script.go; this file
// only adds the "<id>--p<n>" path numbering the corpus tools use.
const PathSeparator = "--p"

// PathID names the n-th distilled path of a case.
func PathID(caseID string, number int) string {
	return fmt.Sprintf("%s%s%d", caseID, PathSeparator, number)
}

// BaseCaseID is the bank case a script entry replays: "<id>--p<n>" -> "<id>".
// Python's rsplit(sep, 1)[0] splits at the last occurrence.
func BaseCaseID(scriptCaseID string) string {
	if idx := strings.LastIndex(scriptCaseID, PathSeparator); idx != -1 {
		return scriptCaseID[:idx]
	}
	return scriptCaseID
}

// Entry builds one script line. The outputs are marked supervised unless the
// caller says otherwise.
func Entry(caseID string, texts []string, supervised []bool) eval.ScriptEntry {
	outputs := make([]eval.ScriptOutput, len(texts))
	for i, text := range texts {
		flag := true
		if supervised != nil {
			flag = supervised[i]
		}
		outputs[i] = eval.ScriptOutput{Text: text, Supervised: flag}
	}
	return eval.ScriptEntry{CaseID: caseID, Outputs: outputs}
}
