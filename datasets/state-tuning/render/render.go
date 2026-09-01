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

// renderCase produces the training pair for one semantic case using the
// product's own G1I instructions and chat renderer, so the bytes are the ones
// the model meets at inference time.
func renderCase(
	entry semanticCase,
	schemas map[string]toolSchema,
	mode inference.ThinkingMode,
	shuffler *rand.Rand,
) (trainingRecord, error) {
	specs, order, err := buildSpecs(entry, schemas, shuffler)
	if err != nil {
		return trainingRecord{}, err
	}
	instructions := (agent.G1IProtocol{}).Instructions(specs, mode)
	messages := []agent.Message{
		{Role: agent.RoleSystem, Content: instructions},
		{Role: agent.RoleUser, Content: entry.User},
	}
	prompt, err := (agent.RWKVChatRenderer{ThinkingMode: mode}).Render(messages)
	if err != nil {
		return trainingRecord{}, err
	}
	completion, err := buildCompletion(entry, mode)
	if err != nil {
		return trainingRecord{}, err
	}
	sum := sha256.Sum256([]byte(prompt))
	return trainingRecord{
		ID:         entry.ID,
		Subtype:    entry.Subtype,
		Lang:       entry.Lang,
		Action:     entry.Action,
		Prompt:     prompt,
		Completion: completion,
		Text:       prompt + completion,
		ToolOrder:  order,
		PromptSHA:  hex.EncodeToString(sum[:]),
	}, nil
}

// buildSpecs resolves the case's tool subset into ToolSpecs and shuffles their
// order. Shuffling matters: the semantic layer tends to list the tool a positive
// case calls first, and a state trained on that ordering learns position rather
// than the tool. scarletwolf's formatter shuffles for the same reason.
func buildSpecs(
	entry semanticCase,
	schemas map[string]toolSchema,
	shuffler *rand.Rand,
) ([]agent.ToolSpec, []string, error) {
	if len(entry.Tools) == 0 {
		return nil, nil, fmt.Errorf("no tools listed")
	}
	names := append([]string(nil), entry.Tools...)
	shuffler.Shuffle(len(names), func(i, j int) { names[i], names[j] = names[j], names[i] })
	specs := make([]agent.ToolSpec, 0, len(names))
	for _, name := range names {
		schema, ok := schemas[name]
		if !ok {
			return nil, nil, fmt.Errorf("unknown tool %q", name)
		}
		if strings.TrimSpace(schema.Arguments) == "" {
			return nil, nil, fmt.Errorf("tool %q has no arguments_hint; re-run the exporter", name)
		}
		specs = append(specs, agent.ToolSpec{
			Name:        schema.Name,
			Description: schema.Description,
			Parameters:  schema.Parameters,
			Arguments:   schema.Arguments,
		})
	}
	return specs, names, nil
}

// buildCompletion assembles the assistant target. For a thinking mode the first
// byte is the ">" that Render withheld; omitting it would train a token
// boundary inference never produces.
func buildCompletion(entry semanticCase, mode inference.ThinkingMode) (string, error) {
	var body string
	switch entry.Action {
	case "call":
		if entry.Call == nil {
			return "", fmt.Errorf("action=call with no call")
		}
		var arguments any
		if err := json.Unmarshal(entry.Call.Arguments, &arguments); err != nil {
			return "", fmt.Errorf("arguments are not JSON: %w", err)
		}
		// Re-marshal so the trained bytes carry a canonical object rather than
		// whatever spacing the semantic layer happened to use, and so a
		// stringified arguments value could never reach the target.
		encoded, err := json.Marshal(map[string]any{
			"name":      entry.Call.Name,
			"arguments": arguments,
		})
		if err != nil {
			return "", err
		}
		body = "<tool_call>" + string(encoded) + "</tool_call>"
	case "abstain":
		if strings.TrimSpace(entry.Answer) == "" {
			return "", fmt.Errorf("action=abstain with empty answer")
		}
		body = entry.Answer
	default:
		return "", fmt.Errorf("unknown action %q", entry.Action)
	}
	switch mode {
	case inference.ThinkingFast, inference.ThinkingFull:
		// Render stopped mid-tag; the model completes it. See package doc.
		return ">" + body, nil
	default:
		return " " + body, nil
	}
}
