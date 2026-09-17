package agent

import (
	"path/filepath"
	"strings"
	"testing"
)

// The user-merge variants (V1 merged, V2 no-nudge, V3 rewrite) pin the exact
// rendered prompt bytes of one scripted trajectory: a successful read_file,
// the same call repeated and rejected as a duplicate, a successful submit,
// then the forced answer stage. G1K was trained on strictly alternating
// User/Assistant turns, so every generation of the merge variants must show
// at most one consecutive User block before the trailing Assistant opening.

// userMergeTrajectory is the shared scripted sequence: a read_file success,
// the identical call rejected as a duplicate (no forceAnswer while the
// terminal tool is incomplete), a submit success, then the forced answer.
func userMergeTrajectory() ([]Tool, []string) {
	return []Tool{bundledEchoTool{name: "read_file"}, submitTestTool{}},
		[]string{
			`<tool_call>{"name":"read_file","arguments":{"path":"a.txt"}}</tool_call>`,
			`<tool_call>{"name":"read_file","arguments":{"path":"a.txt"}}</tool_call>`,
			`<tool_call>{"name":"submit","arguments":{"answer":"draft"}}</tool_call>`,
			"All done.",
		}
}

func runUserMergeGolden(t *testing.T, mode string) []goldenStep {
	t.Helper()
	tools, outputs := userMergeTrajectory()
	steps := runGoldenTurn(
		t,
		Options{
			MaxSteps:     4,
			Protocol:     G1Protocol{OneStage: true, AlignQwen36: true, SemanticNoTool: true},
			Renderer:     RWKVChatRenderer{},
			TerminalTool: "submit",
			UserMerge:    mode,
		},
		tools,
		outputs,
		nil,
		"Read a.txt and answer.",
	)
	for index, step := range steps {
		if got := countTrailingUserBlocks(step.Prompt); got > 1 {
			t.Fatalf(
				"usermsg=%s generation %d has %d consecutive User blocks before the trailing Assistant:, want at most 1",
				mode, index+1, got,
			)
		}
	}
	return steps
}

// countTrailingUserBlocks counts the consecutive User: blocks immediately
// before the trailing Assistant: opening of a rendered prompt. Blocks split
// on blank lines; a block with no role label continues the message below it.
// It returns -1 when the prompt does not end with an Assistant opening.
func countTrailingUserBlocks(prompt string) int {
	blocks := strings.Split(prompt, "\n\n")
	if len(blocks) == 0 || !strings.HasPrefix(blocks[len(blocks)-1], "Assistant:") {
		return -1
	}
	count := 0
	for index := len(blocks) - 2; index >= 0; index-- {
		block := blocks[index]
		switch {
		case strings.HasPrefix(block, "User:"):
			count++
		case strings.HasPrefix(block, "Assistant:") ||
			strings.HasPrefix(block, "System:") ||
			strings.HasPrefix(block, "Tool:"):
			return count
		}
	}
	return count
}

// TestUserMergeV1Golden locks the merged variant: the per-step nudge rides in
// the same User message right after </tool_response>, and the answer-stage
// instruction folds into the trailing User message. (The in-memory blank-line
// join renders as a single newline: inference.CleanChatText collapses blank
// lines inside User messages.)
func TestUserMergeV1Golden(t *testing.T) {
	t.Parallel()
	steps := runUserMergeGolden(t, "merged")
	compareGoldenPrompt(t, filepath.Join("wire", "user_merge_v1_merged.txt"), formatGolden(steps))
	postTool := steps[1].Prompt
	if !strings.Contains(postTool, "</tool_response>\nUse the Tool results above to continue the current task.") {
		t.Fatal("V1 post-tool prompt does not merge the nudge into the tool-response User message")
	}
	answer := steps[3].Prompt
	if !strings.Contains(answer, "</tool_response>\nUse the Tool results above to continue the current task.") ||
		!strings.Contains(answer, "Tool execution is complete and tools are now unavailable.") {
		t.Fatal("V1 answer prompt does not merge the tool response, nudge and answer instruction")
	}
}

// TestUserMergeV2Golden locks the no-nudge variant: the per-step
// successful-tool nudge never renders, while duplicate-rejection reminders
// and the answer instruction still merge.
func TestUserMergeV2Golden(t *testing.T) {
	t.Parallel()
	steps := runUserMergeGolden(t, "no-nudge")
	compareGoldenPrompt(t, filepath.Join("wire", "user_merge_v2_no_nudge.txt"), formatGolden(steps))
	for index, step := range steps {
		if strings.Contains(step.Prompt, "Use the Tool results above to continue the current task.") {
			t.Fatalf("V2 generation %d still carries the per-step nudge", index+1)
		}
	}
	postRejection := steps[2].Prompt
	if !strings.Contains(postRejection, "</tool_response>\nThat tool call was rejected") {
		t.Fatal("V2 post-rejection prompt does not merge the duplicate reminder into the tool-response User message")
	}
}

// TestUserMergeV3Golden locks the rewrite variant: at answer-stage entry the
// rejected duplicate call and its receipts roll back out of the transcript,
// the system control carries no tool catalog, and exactly one closing User
// instruction remains.
func TestUserMergeV3Golden(t *testing.T) {
	t.Parallel()
	steps := runUserMergeGolden(t, "rewrite")
	compareGoldenPrompt(t, filepath.Join("wire", "user_merge_v3_rewrite.txt"), formatGolden(steps))
	answer := steps[3].Prompt
	if strings.Contains(answer, "<tools>") {
		t.Fatal("V3 answer control still carries the tool catalog")
	}
	if !strings.Contains(answer, "Answer in ordinary text.") {
		t.Fatal("V3 answer control lost the plain-text sentence")
	}
	if strings.Contains(answer, "duplicate tool call rejected") ||
		strings.Contains(answer, "That tool call was rejected") {
		t.Fatal("V3 answer transcript still carries the rejected duplicate or its receipts")
	}
	if count := strings.Count(answer, `{"name":"read_file","arguments":{"path":"a.txt"}}`); count != 1 {
		t.Fatalf("V3 answer transcript carries %d copies of the repeated call, want 1", count)
	}
	if strings.Contains(answer, "Use the Tool results above to continue the current task.") {
		t.Fatal("V3 answer transcript still carries the per-step nudge")
	}
	if !strings.Contains(answer, "Tool execution is complete and tools are now unavailable.") {
		t.Fatal("V3 answer transcript lost the closing instruction")
	}
	// The successful exchanges (read_file, submit) stay.
	if !strings.Contains(answer, `{"name":"submit","arguments":{"answer":"draft"}}`) {
		t.Fatal("V3 answer transcript dropped the successful submit exchange")
	}
}
