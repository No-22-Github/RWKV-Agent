package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math/rand"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// The continuation prompts are read from the product rather than copied here.
// An earlier version of this file hand-copied them and relied on a test to
// notice drift; PostToolReminder() and PrepareAnswer() are the actual seams, so
// there is nothing left to drift.
const (
	answerOpen  = "<answer>"
	answerClose = "</answer>"
)

// postToolReminder is the runner's own between-steps reminder
// (internal/agent/runner_config.go, reached through the protocol).
func postToolReminder() string {
	return (agent.G1IProtocol{}).PostToolReminder()
}

// expandMultiStep turns one authored multi-step case into one training sample
// per step. Step k's prompt is the transcript through step k-1, so the samples
// share a growing prefix exactly as inference does.
func expandMultiStep(
	entry semanticCase,
	schemas map[string]toolSchema,
	mode inference.ThinkingMode,
	shuffler *rand.Rand,
) ([]trainingRecord, error) {
	if len(entry.Steps) == 0 {
		return nil, fmt.Errorf("multi_step case has no steps")
	}
	specs, order, err := buildSpecs(entry, schemas, shuffler)
	if err != nil {
		return nil, err
	}
	instructions := (agent.G1IProtocol{}).Instructions(specs, mode)

	// The transcript grows as steps are consumed. Roles follow the product's
	// chat template: Tool results arrive as a Tool message, and the runner's
	// reminder arrives as a User message.
	transcript := []agent.Message{
		{Role: agent.RoleSystem, Content: instructions},
		{Role: agent.RoleUser, Content: entry.User},
	}

	records := make([]trainingRecord, 0, len(entry.Steps))
	for index, step := range entry.Steps {
		last := index == len(entry.Steps)-1
		if !last && step.Action != "call" {
			return nil, fmt.Errorf("step %d: only the final step may be %q", index, step.Action)
		}

		record, err := renderStep(entry, step, transcript, order, mode, index, last)
		if err != nil {
			return nil, fmt.Errorf("step %d: %w", index, err)
		}
		records = append(records, record)

		if step.Action != "call" {
			break
		}
		assistant, err := envelopeFor(step)
		if err != nil {
			return nil, fmt.Errorf("step %d: %w", index, err)
		}
		payload, err := json.Marshal(step.Result)
		if err != nil {
			return nil, fmt.Errorf("step %d: encode result: %w", index, err)
		}
		transcript = append(transcript,
			agent.Message{Role: agent.RoleAssistant, Content: assistant},
			agent.Message{Role: agent.RoleTool,
				Content: "<tool_result>" + string(payload) + "</tool_result>"},
		)
		// Every consumed tool result is followed by the runner's post-tool
		// reminder. The answer stage's own reminder is NOT added here: the
		// product's PrepareAnswer appends it while rewriting the transcript, and
		// renderStep goes through PrepareAnswer so it cannot be added twice.
		transcript = append(transcript,
			agent.Message{Role: agent.RoleUser, Content: postToolReminder()})
	}
	return records, nil
}

// renderStep builds the (prompt, completion) pair for one step of a chain.
func renderStep(
	entry semanticCase,
	step semanticStep,
	transcript []agent.Message,
	order []string,
	mode inference.ThinkingMode,
	index int,
	last bool,
) (trainingRecord, error) {
	renderer := agent.RWKVChatRenderer{ThinkingMode: mode}
	prompt, err := renderer.Render(transcript)
	if err != nil {
		return trainingRecord{}, err
	}

	var completion string
	switch step.Action {
	case "call":
		envelope, err := envelopeFor(step)
		if err != nil {
			return trainingRecord{}, err
		}
		completion = withheldPrefix(mode) + envelope
	case "answer":
		if strings.TrimSpace(step.Answer) == "" {
			return trainingRecord{}, fmt.Errorf("answer step has empty answer")
		}
		// The answer stage is not the decision transcript plus a tag. The
		// product's PrepareAnswer DROPS the decision instructions, substitutes
		// its own answer-stage control, and appends the tools-exhausted
		// reminder itself, so going through it is the only way to get that
		// system block right.
		prepared, answerPrefix := (agent.G1IProtocol{}).PrepareAnswer(transcript, nil, mode)
		if len(prepared) == 0 || answerPrefix != answerOpen {
			return trainingRecord{}, fmt.Errorf(
				"PrepareAnswer returned %d messages and prefix %q, want the %q prefix",
				len(prepared), answerPrefix, answerOpen)
		}
		prompt, err = renderer.Render(prepared)
		if err != nil {
			return trainingRecord{}, err
		}
		// Prefix injection is soft (internal/agent/prompt_build.go:81) and
		// RWKVChatRenderer refuses it whenever its final bytes already open a
		// think block, so under fast/full the "<answer>" tag is never supplied
		// and the model must emit it. The answer-stage control says exactly
		// that per mode (protocol_g1i.go:394).
		if mode == inference.ThinkingOff {
			prompt += " " + answerOpen
			completion = step.Answer + answerClose
		} else {
			completion = withheldPrefix(mode) + answerOpen + step.Answer + answerClose
		}
	case "abstain":
		if strings.TrimSpace(step.Answer) == "" {
			return trainingRecord{}, fmt.Errorf("abstain step has empty answer")
		}
		completion = withheldPrefix(mode) + step.Answer
	default:
		return trainingRecord{}, fmt.Errorf("unknown step action %q", step.Action)
	}

	sum := sha256.Sum256([]byte(prompt))
	return trainingRecord{
		ID:         fmt.Sprintf("%s/step%d", entry.ID, index+1),
		Subtype:    entry.Subtype,
		Lang:       entry.Lang,
		Action:     step.Action,
		Prompt:     prompt,
		Completion: completion,
		Text:       prompt + completion,
		ToolOrder:  order,
		PromptSHA:  hex.EncodeToString(sum[:]),
		StepOf:     len(entry.Steps),
		StepIndex:  index + 1,
	}, nil
}

// envelopeFor canonicalises a step's call into the XML envelope through the
// product's RecordAction. See toolCallEnvelope for why the key order matters.
func envelopeFor(step semanticStep) (string, error) {
	if step.Call == nil {
		return "", fmt.Errorf("action=call with no call")
	}
	return toolCallEnvelope(step.Call.Name, step.Call.Arguments)
}

// withheldPrefix is the byte the model itself must emit to close the think tag
// Render left open. See the package doc for why it is withheld.
func withheldPrefix(mode inference.ThinkingMode) string {
	switch mode {
	case inference.ThinkingFast, inference.ThinkingFull:
		return ">"
	default:
		return " "
	}
}
