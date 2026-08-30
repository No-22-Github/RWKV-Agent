package agent

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/inference"
)

// controlPromptFor assembles the decision-stage control prompt: the protocol
// instructions followed by an optional task contract. The Runner and the
// settings preview share it, so a preview can never drift from enforcement.
func controlPromptFor(
	protocol ActionProtocol,
	specs []ToolSpec,
	thinkingMode inference.ThinkingMode,
	native bool,
	taskControl string,
) string {
	control := toolControlPrompt(protocol, specs, thinkingMode, native)
	if task := strings.TrimSpace(taskControl); task != "" {
		control += "\n\nTask-specific contract:\n" + task
	}
	return control
}

func (r *Runner) controlForSpecs(specs []ToolSpec) string {
	return controlPromptFor(r.protocol, specs, r.thinkingMode, r.toolCompleter != nil, r.options.TaskControl)
}

func replaceSystemControl(messages []Message, control string) []Message {
	result := append([]Message(nil), messages...)
	for index := range result {
		if result[index].Role == RoleSystem {
			result[index] = Message{Role: RoleSystem, Content: control}
			return result
		}
	}
	return append([]Message{{Role: RoleSystem, Content: control}}, result...)
}

func containsString(values []string, target string) bool {
	for _, value := range values {
		if value == target {
			return true
		}
	}
	return false
}

// terminalActionPhrase words the turn-ending suggestion in duplicate/rescue
// notes: through the terminal tool when one is offered, or with a direct
// answer otherwise (Markdown protocol has no submit gate).
func terminalActionPhrase(terminalTool, variant string) string {
	submit := terminalTool != ""
	switch variant {
	case "if_answer":
		if submit {
			return "submit if you have the answer"
		}
		return "answer directly if you have the answer"
	case "best_now":
		if submit {
			return "submit your best answer now"
		}
		return "answer directly now with your best answer"
	case "if_complete":
		if submit {
			return "submit if the task is complete"
		}
		return "answer directly if the task is complete"
	case "call_best":
		if submit {
			return "call submit with your best answer now"
		}
		return "answer directly now with your best answer"
	}
	return "answer directly"
}

// duplicateReplayNote accompanies a re-executed identical call to a Replayable
// tool. The first repeat keeps the gentle framing; further repeats escalate
// because the transcript has proven that the model is stuck in a loop.
func duplicateReplayNote(streak, stepsLeft int, terminalTool string) string {
	if streak <= 2 {
		return fmt.Sprintf(
			"identical tool call re-executed: this exact call has now run %d times in a row. The result is unchanged; do not call it again. Take the next step: different arguments, another tool, the next row, or %s.",
			streak,
			terminalActionPhrase(terminalTool, "if_answer"),
		)
	}
	return fmt.Sprintf(
		"STOP. This identical call has now run %d times in a row and the result will not change. You have %d steps left. Change the arguments, choose a different tool, or %s.",
		streak,
		stepsLeft,
		terminalActionPhrase(terminalTool, "best_now"),
	)
}

// duplicateRejectionNote replaces the fixed rejection text with an escalating
// one. The first rejection keeps the exact legacy wording so one-off repeats
// behave byte-for-byte like previous releases; further rejections add the
// streak count and the remaining budget.
func duplicateRejectionNote(streak, stepsLeft int, terminalTool string) string {
	if streak < 3 {
		return "This exact call is disabled. Do not repeat it. Use the existing result, change the arguments, choose a different tool, or " + terminalActionPhrase(terminalTool, "if_complete") + "."
	}
	return fmt.Sprintf(
		"STOP repeating. This identical call has now occurred %d times in a row and it will not be accepted again. You have %d steps left. Change the arguments, choose a different tool, or %s.",
		streak,
		stepsLeft,
		terminalActionPhrase(terminalTool, "call_best"),
	)
}

// enterRescueMode rebuilds the tool catalog so only the terminal tool remains
// and injects one explicit rescue instruction as a User turn. A User turn is
// more salient to the model than text appended after a Function output.
func (r *Runner) enterRescueMode(messages []Message, reason string, stepsLeft int) []Message {
	specs := r.rescueToolSpecs()
	control := toolControlPrompt(r.protocol, specs, r.thinkingMode, r.toolCompleter != nil)
	for index := range messages {
		if messages[index].Role == RoleSystem {
			messages[index] = Message{Role: RoleSystem, Content: control}
		}
	}
	return append(messages, Message{
		Role:    RoleUser,
		Content: rescueInstruction(r.terminalTool, reason, stepsLeft),
	})
}

func (r *Runner) rescueToolSpecs() []ToolSpec {
	if r.terminalTool == "" {
		return nil
	}
	for _, spec := range r.toolSpecs {
		if spec.Name == r.terminalTool {
			return []ToolSpec{spec}
		}
	}
	return nil
}

func rescueInstruction(terminalTool, reason string, stepsLeft int) string {
	if terminalTool == "" {
		return fmt.Sprintf(
			"The tools have been disabled because %s. You have %d steps left. Answer directly now with your best answer from the results you already have.",
			reason,
			stepsLeft,
		)
	}
	return fmt.Sprintf(
		"The other tools have been disabled because %s. You have %d steps left. Call %s now with your best answer in this exact shape: {\"name\":\"%s\",\"arguments\":{\"answer\":\"...\"}}",
		reason,
		stepsLeft,
		terminalTool,
		terminalTool,
	)
}

func workspaceChanged(value any) bool {
	result, ok := value.(WorkspaceMutationResult)
	return !ok || result.WorkspaceChanged()
}

func answerContainsToolFrame(content string) bool {
	lower := strings.ToLower(strings.TrimSpace(content))
	return strings.Contains(lower, "<tool_call") || looksLikeBareToolCall(content)
}

func terminalToolOutput(action Action, value any) string {
	var arguments struct {
		Answer string `json:"answer"`
	}
	if json.Unmarshal(action.Arguments, &arguments) == nil && strings.TrimSpace(arguments.Answer) != "" {
		return strings.TrimSpace(arguments.Answer)
	}
	if text, ok := value.(string); ok {
		return strings.TrimSpace(text)
	}
	encoded, err := json.Marshal(value)
	if err != nil {
		return ""
	}
	return string(encoded)
}

func (r *Runner) postToolReminder(terminalToolCompleted bool) string {
	if preservesToolOrder(r.protocol) {
		return r.protocol.PostToolReminder()
	}
	if !terminalToolCompleted {
		return fmt.Sprintf(
			"Use the Tool results above to continue the current task. Call another tool only for a specific missing fact. When the answer is ready, call %s with the real answer; do not answer in plain text. Never repeat a successful tool call.",
			r.terminalTool,
		)
	}
	return r.protocol.PostToolReminder()
}

func (r *Runner) duplicateToolReminder(hasEvidence, terminalToolCompleted bool) string {
	if !terminalToolCompleted {
		return fmt.Sprintf(
			"That tool call was rejected because the exact call already succeeded or failed without any intervening recovery. Do not call it again. If its earlier successful result answers the task, call %s now with that exact result; otherwise choose a different tool for one specific missing fact. Do not answer in plain text.",
			r.terminalTool,
		)
	}
	return duplicateToolReminder(hasEvidence)
}

func validateAnswer(output string) []answerViolation {
	trimmed := strings.TrimSpace(output)
	lower := strings.ToLower(trimmed)
	violations := make([]answerViolation, 0, 4)

	for _, tag := range []string{
		"<tool_call", "</tool_call", "<tool_result", "</tool_result",
		"<answer", "</answer", "<think", "</think",
	} {
		if strings.Contains(lower, tag) {
			violations = append(violations, violationProtocolTag)
			break
		}
	}

	for _, line := range strings.Split(trimmed, "\n") {
		line = strings.TrimSpace(strings.ToLower(line))
		for _, role := range []string{"assistant", "user", "system", "tool"} {
			if strings.HasPrefix(line, role+":") || strings.HasPrefix(line, role+"：") {
				violations = append(violations, violationRoleHeader)
				line = ""
				break
			}
		}
		if line == "" && len(violations) > 0 && violations[len(violations)-1] == violationRoleHeader {
			break
		}
	}

	var payload any
	if json.Unmarshal([]byte(trimmed), &payload) == nil {
		switch payload.(type) {
		case map[string]any, []any:
			violations = append(violations, violationJSONPayload)
		}
	}

	if strings.Contains(lower, `"ok"`) &&
		strings.Contains(lower, `"tool"`) &&
		(strings.Contains(lower, `"result"`) || strings.Contains(lower, `"error"`)) {
		violations = append(violations, violationToolEcho)
	}
	return violations
}

func answerContractFallback(task string) string {
	for _, value := range task {
		if unicode.Is(unicode.Han, value) {
			return answerContractFallbackZH
		}
	}
	return answerContractFallbackEN
}

func appendUnique(values []string, value string) []string {
	for _, existing := range values {
		if existing == value {
			return values
		}
	}
	return append(values, value)
}

func providerUnavailableReminder(name string) string {
	return fmt.Sprintf(
		"The provider for %s is unavailable. Do not call %s again in this turn. Continue only with verified Tool results and explicitly state that the %s fact could not be verified.",
		name,
		name,
		name,
	)
}

func duplicateToolReminder(hasEvidence bool) string {
	if hasEvidence {
		return duplicateToolAnswerReminder
	}
	return `That tool call was rejected because it repeats an earlier failed call.
Tools are now unavailable. Answer from the Tool results, and clearly state anything that could not be verified.`
}

func toolFailureReminder(
	name string,
	err error,
	recoveryBlocked bool,
	tools map[string]Tool,
) string {
	var prompt strings.Builder
	if errors.Is(err, ErrProviderUnavailable) {
		return providerUnavailableReminder(name)
	}
	if errors.Is(err, ErrInvalidToolArguments) {
		fmt.Fprintf(&prompt, "The %s arguments were rejected: %v. ", name, err)
		if tool, ok := tools[name]; ok {
			fmt.Fprintf(
				&prompt,
				"Retry %s using only the fields in this exact argument shape: %s. ",
				name,
				tool.Spec().Arguments,
			)
			if example := strings.TrimSpace(tool.Spec().Example); example != "" {
				fmt.Fprintf(
					&prompt,
					"A valid call uses literal values, never type descriptions: {\"name\":\"%s\",\"arguments\":%s}. ",
					name,
					example,
				)
			}
		}
		prompt.WriteString("Do not add optional limit, byte, offset, or pagination fields unless the schema lists them.")
		return prompt.String()
	}
	fmt.Fprintf(&prompt, "The tool call failed: %v. ", err)
	if recoveryBlocked {
		prompt.WriteString("Do not call the same tool again in this turn. ")
	} else {
		prompt.WriteString("Do not repeat the same call. ")
	}
	if hint := toolFailureHint(name, tools); hint != "" {
		prompt.WriteString(hint)
	}
	prompt.WriteString("Choose a different useful tool or answer with the limitation. Do not guess.")
	return prompt.String()
}

// toolFailureHint is the per-tool recovery guidance appended when a listed
// companion tool is offered. The texts are byte-stable transcript contract, so
// new entries belong in this table rather than in ad-hoc branches.
var toolFailureHints = map[string]struct {
	companions []string
	hint       string
}{
	"read_file": {
		companions: []string{"list_files", "search_text"},
		hint:       "If the path is uncertain, use list_files or search_text before another read_file call. ",
	},
	"list_files": {
		companions: []string{"search_text"},
		hint:       "Try an existing parent directory or workspace root, or use search_text for a known literal. ",
	},
}

func toolFailureHint(name string, tools map[string]Tool) string {
	entry, ok := toolFailureHints[name]
	if !ok {
		return ""
	}
	for _, companion := range entry.companions {
		if _, offered := tools[companion]; !offered {
			return ""
		}
	}
	return entry.hint
}

// tracePrompt captures a generation request. The prompt is recorded verbatim up
// to the configured budget so a greedy output change can be attributed to the
// exact input that produced it.
