// Package corpus ports the scripts/corpus tools: turning teacher agent-eval
// runs into a replay script (paths), replaying that script through the real
// eval harness (render), cutting training rows out of the trace (rows), and
// gating distillation candidates against the test bank (decontam).
//
// The port keeps the Python originals' bytes (§4.3 of
// docs/go-tooling-migration.md). That matters most here: script.jsonl and
// rows.jsonl feed training corpora, and rows.jsonl is compared byte for byte
// against the baseline because it is the exact byte stream the model saw.
package corpus

import (
	"github.com/no22/RWKV-Agent/internal/lab"
)

// Assistant action bytes as a replay script carries them.
//
// A script holds each generation's raw text; the student's wire (System block,
// receipts, reminders) comes from the harness at render time. The only wire
// knowledge this side needs is how an action is spelled. This matches the
// work-v1 corpus renderer and the harness write-back: name first, compact
// JSON, non-ASCII kept.
const (
	ToolCallOpen  = "<tool_call>"
	ToolCallClose = "</tool_call>"
)

// ToolCall renders one assistant action.
//
// The arguments are an OrderedMap, not a map[string]any: Go sorts map keys
// when marshalling and Python preserves the teacher's order, so a decoded map
// would silently reorder the payload and change the training corpus (P1).
func ToolCall(name string, arguments *lab.OrderedMap) (string, error) {
	payload := lab.NewOrderedMap()
	payload.Set("name", name)
	payload.Set("arguments", arguments)
	data, err := lab.EncodeOrderedJSON(payload, lab.EncodeOptions{})
	if err != nil {
		return "", err
	}
	return ToolCallOpen + string(data) + ToolCallClose, nil
}
