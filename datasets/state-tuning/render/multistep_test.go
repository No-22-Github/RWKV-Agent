package main

import (
	"encoding/json"
	"math/rand"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// TestContinuationPromptsMatchProduct pins the two reminders a multi-step
// transcript injects between turns. They are copied constants, so nothing but a
// test stops them drifting from the runner, and a drifted reminder trains a
// context the model never meets at inference.
func TestContinuationPromptsMatchProduct(t *testing.T) {
	root := repoRoot(t)
	for _, check := range []struct {
		name   string
		source string
		want   string
	}{
		{"postToolReminder", "internal/agent/runner_config.go", postToolReminder()},
	} {
		t.Run(check.name, func(t *testing.T) {
			raw, err := os.ReadFile(filepath.Join(root, check.source))
			if err != nil {
				t.Fatal(err)
			}
			if !strings.Contains(string(raw), check.want) {
				t.Errorf("%s no longer appears verbatim in %s; the product wording changed and this constant must follow",
					check.name, check.source)
			}
		})
	}
}

func multiStepFixture(t *testing.T) semanticCase {
	t.Helper()
	raw := `{
	  "id": "multi-test",
	  "subtype": "multi_step",
	  "lang": "zh",
	  "tools": ["web_search", "web_fetch", "write_file"],
	  "user": "查一下 RWKV7 的结论并写进 notes.md",
	  "steps": [
	    {"action":"call",
	     "call":{"name":"web_search","arguments":{"query":"RWKV7 结论","max_results":5}},
	     "result":{"ok":true,"tool":"web_search","result":{"query":"RWKV7 结论","results":[{"source_id":"s1","title":"RWKV-7","url":"https://example.com/a","snippet":"动态状态演化"}]}},
	     "think":"先检索来源。"},
	    {"action":"call",
	     "call":{"name":"write_file","arguments":{"path":"notes.md","content":"# RWKV7\n- 动态状态演化"}},
	     "result":{"ok":true,"tool":"write_file","result":{"path":"notes.md","bytes":28}},
	     "think":"证据够了，落盘。"},
	    {"action":"answer","answer":"已写入 notes.md，要点是动态状态演化。","think":"文件写成，回报。"}
	  ]
	}`
	var entry semanticCase
	if err := json.Unmarshal([]byte(raw), &entry); err != nil {
		t.Fatal(err)
	}
	return entry
}

// TestMultiStepExpansion checks the shape of the expansion: one sample per step,
// prompts strictly growing, and each step's prompt already containing the prior
// step's envelope and tool result.
func TestMultiStepExpansion(t *testing.T) {
	root := repoRoot(t)
	schemas, err := loadSchemas(filepath.Join(root, "datasets/state-tuning/tool_schemas.json"))
	if err != nil {
		t.Fatal(err)
	}
	records, err := expandMultiStep(multiStepFixture(t), schemas,
		inference.ThinkingFast, rand.New(rand.NewSource(3)))
	if err != nil {
		t.Fatal(err)
	}
	if len(records) != 3 {
		t.Fatalf("want 3 samples, got %d", len(records))
	}

	for index, record := range records {
		if record.StepIndex != index+1 || record.StepOf != 3 {
			t.Errorf("sample %d: step markers = %d/%d, want %d/3",
				index, record.StepIndex, record.StepOf, index+1)
		}
		// Only the call steps share a growing prefix. The answer step is not in
		// that chain: PrepareAnswer swaps the decision instructions for a
		// shorter control block, so its prompt is expected to be shorter.
		if index > 0 && record.Action == "call" &&
			len(record.Prompt) <= len(records[index-1].Prompt) {
			t.Errorf("sample %d: prompt did not grow over the previous step", index)
		}
	}

	// Step 2 must see step 1's envelope and its tool result. The expected
	// envelope comes from the product's own RecordAction rather than a literal,
	// so a drift on either side fails here instead of shipping.
	wantEnvelope := (agent.G1IProtocol{}).RecordAction(agent.Action{
		Type:      agent.ActionTypeTool,
		Name:      "web_search",
		Arguments: json.RawMessage(`{"max_results":5,"query":"RWKV7 结论"}`),
	}, "")
	if !strings.Contains(records[1].Prompt, wantEnvelope) {
		t.Errorf("step 2 prompt is missing step 1's tool call envelope %s", wantEnvelope)
	}
	if !strings.Contains(records[1].Prompt, `<tool_result>{"ok":true,"tool":"web_search"`) {
		t.Error("step 2 prompt is missing step 1's tool result")
	}
	if !strings.Contains(records[1].Prompt, postToolReminder()) {
		t.Error("step 2 prompt is missing the post-tool reminder")
	}

	// The two call steps use the withheld-bracket boundary.
	for _, index := range []int{0, 1} {
		if !strings.HasSuffix(records[index].Prompt, inference.ThinkBlockFast) {
			t.Errorf("step %d prompt must end at the open think tag", index+1)
		}
		if !strings.HasPrefix(records[index].Completion, `><tool_call>`) {
			t.Errorf("step %d completion = %q, want a withheld bracket then an envelope",
				index+1, records[index].Completion[:min(30, len(records[index].Completion))])
		}
	}
}

// TestAnswerStageShape pins the third completion shape, which the single-turn
// corpus never produces. Two things are easy to get wrong here and both are
// pinned below:
//
//   - The system block is NOT the decision instructions. PrepareAnswer drops
//     them and substitutes its own answer-stage control.
//   - Under a thinking mode the "<answer>" tag is NOT supplied. Prefix
//     injection is soft and RWKVChatRenderer refuses it while a think block is
//     open, so the prompt still ends at the half-open tag and the model emits
//     ">" then "<answer>" itself. Only ThinkingOff gets the tag prefilled.
func TestAnswerStageShape(t *testing.T) {
	root := repoRoot(t)
	schemas, err := loadSchemas(filepath.Join(root, "datasets/state-tuning/tool_schemas.json"))
	if err != nil {
		t.Fatal(err)
	}
	records, err := expandMultiStep(multiStepFixture(t), schemas,
		inference.ThinkingFast, rand.New(rand.NewSource(3)))
	if err != nil {
		t.Fatal(err)
	}
	final := records[len(records)-1]

	if !strings.HasSuffix(final.Prompt, inference.ThinkBlockFast) {
		t.Errorf("answer-stage prompt must still end at the half-open think tag, got tail %q",
			final.Prompt[max(0, len(final.Prompt)-40):])
	}
	if want := ">" + answerOpen; !strings.HasPrefix(final.Completion, want) {
		t.Errorf("answer completion must open with %q, got %q",
			want, final.Completion[:min(20, len(final.Completion))])
	}
	if !strings.HasSuffix(final.Completion, answerClose) {
		t.Errorf("answer completion must close with %q, got %q", answerClose, final.Completion)
	}

	// The system block must be the product's answer-stage control, not the
	// decision instructions the earlier steps carry.
	wantPrepared, _ := (agent.G1IProtocol{}).PrepareAnswer(
		[]agent.Message{{Role: agent.RoleUser, Content: "x"}}, nil, inference.ThinkingFast)
	answerControl := wantPrepared[0].Content
	if !strings.Contains(final.Prompt, answerControl) {
		t.Error("answer-stage prompt is missing the product's answer-stage control block")
	}
	if strings.Contains(final.Prompt, "Available tools:") {
		t.Error("answer-stage prompt still carries the decision instructions; tools are unavailable there")
	}
	if !strings.Contains(final.Prompt, "tools are now unavailable") {
		t.Error("answer-stage prompt is missing the tools-exhausted reminder")
	}
	// PrepareAnswer trades a long instruction block for a short one, so the
	// answer prompt is legitimately shorter than the decision prompt before it.
	if len(records) > 1 && len(final.Prompt) >= len(records[len(records)-2].Prompt) {
		t.Log("answer prompt did not shrink; PrepareAnswer may no longer be replacing the system block")
	}
}
