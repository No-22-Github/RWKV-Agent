package agent

import (
	"encoding/json"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func (p G1Protocol) exitName() string {
	if p.Experiments.Exit != "" {
		return p.Experiments.Exit
	}
	return SemanticNoToolName
}

// recoverExperimentalCall only accepts a single standalone call at the tail.
// It does not execute quoted examples, multiple calls, or truncated generations.
// Stop-consumed closing tags are allowed, matching the existing XML contract.
func (p G1Protocol) recoverExperimentalCall(value string, finish continuation.FinishReason) (Action, bool) {
	if finish == continuation.FinishLength {
		return Action{}, false
	}
	candidate := wire.StripLeadingThinkBlocks(strings.TrimSpace(value))
	candidate = wire.TrimWithheldOpening(candidate)
	unclosed := strings.HasPrefix(candidate, "<think>")
	if unclosed && p.Experiments.Recovery == "preamble" {
		return Action{}, false
	}
	if strings.Count(candidate, "<tool_call>") != 1 {
		return Action{}, false
	}
	index := strings.Index(candidate, "<tool_call>")
	if index < 0 {
		return Action{}, false
	}
	// Calls following a preamble must begin on a fresh line. This excludes
	// inline quotations such as: output exactly one "<tool_call>{...}".
	if index > 0 && candidate[index-1] != '\n' {
		return Action{}, false
	}
	if strings.Contains(candidate[:index], "```") {
		return Action{}, false
	}
	callText := candidate[index:]
	payload, _ := envelopeContent(callText, "<tool_call>", "</tool_call>")
	jsonRepair := false
	if !json.Valid([]byte(payload)) && p.Experiments.Recovery == "json" {
		fixed := repairExperimentalJSON(payload)
		if fixed != payload && json.Valid([]byte(fixed)) {
			payload = fixed
			callText = "<tool_call>" + fixed + "</tool_call>"
			jsonRepair = true
		}
	}
	var call struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}
	normalized, _ := normalizeG1CallPayload(payload)
	if json.Unmarshal([]byte(normalized), &call) != nil || call.Name == "" || call.Name == "TOOL_NAME" || !isJSONObject(call.Arguments) {
		return Action{}, false
	}
	if index == 0 && !jsonRepair {
		return Action{}, false
	}
	plain := p
	plain.Experiments.Recovery = ""
	action, err := plain.Parse(callText, finish)
	if err != nil || (action.Type != ActionTypeTool && action.Type != ActionTypeNoTool) {
		return Action{}, false
	}
	if unclosed {
		action.Repairs = append(action.Repairs, wire.Repair("think_salvaged"))
	} else if index > 0 {
		action.Repairs = append(action.Repairs, wire.Repair("preamble_stripped"))
	}
	if jsonRepair {
		action.Repairs = append(action.Repairs, wire.RepairJSONRepaired)
	}
	action.ProtocolRepaired = true
	action.OriginalProtocolFailure = ProtocolFailureToolShapeInvalid
	return action, true
}

// normalizeG1CallPayload accepts two near-misses G1L checkpoints emit inside
// a <tool_call> envelope: stray closing braces after a complete object, and
// the OpenAI {"type":"function","function":{…}} wrapper (harness v24).
func normalizeG1CallPayload(payload string) (string, []wire.Repair) {
	var repairs []wire.Repair
	if !json.Valid([]byte(payload)) {
		if fixed := repairExperimentalJSON(payload); fixed != payload {
			payload = fixed
			repairs = append(repairs, wire.RepairJSONRepaired)
		}
	}
	object, ok := rawJSONObject(json.RawMessage(payload))
	if !ok || object["name"] != nil {
		return payload, repairs
	}
	for key := range object {
		if key != "type" && key != "id" && key != "function" {
			return payload, repairs
		}
	}
	function, ok := rawJSONObject(object["function"])
	name := rawJSONString(function["name"])
	if !ok || name == "" {
		return payload, repairs
	}
	flattened, err := json.Marshal(struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}{name, firstRaw(function, "arguments")})
	if err != nil {
		return payload, repairs
	}
	return string(flattened), append(repairs, wire.RepairFunctionWrapper)
}

// Deliberately narrow: extra closing braces after a complete JSON object only.
// A missing quote may change argument meaning and is not guessed here.
func repairExperimentalJSON(value string) string {
	trimmed := strings.TrimSpace(value)
	for strings.HasSuffix(trimmed, "}") {
		trimmed = strings.TrimSpace(strings.TrimSuffix(trimmed, "}"))
		if json.Valid([]byte(trimmed)) {
			return trimmed
		}
	}
	return value
}
