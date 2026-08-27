package agent

import (
	"errors"
	"strings"

	"github.com/no22/RWKV-Agent/internal/inference"
)

// retryEchoBudget caps how many runes of a rejected response are echoed back to
// the model on a protocol retry.
const retryEchoBudget = 480

// retryEcho condenses a rejected response before it re-enters the transcript.
// Runaway reasoning is the common cause of a retry, and echoing thousands of
// characters of it verbatim poisons the context so the retry repeats the same
// failure. Unclosed thinking is dropped entirely; anything else is truncated.
func retryEcho(modelAction string, err error) string {
	trimmed := strings.TrimSpace(modelAction)
	if trimmed == "" {
		return ""
	}
	if errors.Is(err, ErrUnclosedThink) {
		return ""
	}
	runes := []rune(trimmed)
	if len(runes) <= retryEchoBudget {
		return trimmed
	}
	if errors.Is(err, ErrOutputTokenLimit) {
		return ""
	}
	return string(runes[:retryEchoBudget]) + "\n[truncated]"
}

func directResponseControl(mode inference.ThinkingMode) string {
	prompt := `You are a helpful conversational assistant.
Answer the current user message directly and naturally in the user's language.
Use the committed conversation and general knowledge.
Workspace tools are unavailable for this turn. Do not claim to have inspected files.
`
	switch mode {
	case inference.ThinkingFast:
		return prompt + "Answer directly. Do not open a <think> block, output tool calls, or emit role labels."
	case inference.ThinkingFull:
		return prompt + "Close your thinking with </think>, then answer directly. Do not output tool calls or emit role labels."
	default:
		return prompt + "Do not output tool calls, role labels, or hidden reasoning."
	}
}

const postToolDecisionReminder = `Use the Tool results above to continue the current task.
If the evidence is sufficient, answer now. Call another tool only for a specific missing fact.
Never repeat a successful tool call. Do not open a <think> block or repeat the Tool payload.`

const duplicateToolAnswerReminder = `That tool call was rejected because it repeats a successful call.
Answer the current task from the evidence already collected.`

const (
	answerContractFallbackEN = "I could not provide a reliable answer because the model output violated the answer contract. Please retry."
	answerContractFallbackZH = "模型输出不符合答案契约，因此无法可靠展示。请重试。"
)

const (
	maxConsecutiveToolFailures  = 2
	forcedAnswerStepBudget      = "step_budget_after_tool_attempt"
	forcedAnswerDuplicateCall   = "duplicate_tool_call"
	forcedAnswerProviderFailure = "provider_unavailable"
	rejectedUnknownTool         = "unknown_tool"
	rejectedDuplicateCall       = "duplicate_tool_call"
	rejectedFailureLimit        = "consecutive_tool_failures"
	rejectedProviderUnavailable = "provider_unavailable"
	rejectedRescueRestricted    = "rescue_submit_only"
)
