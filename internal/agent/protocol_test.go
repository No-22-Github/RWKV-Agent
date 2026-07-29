package agent

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestProtocolAndRendererHaveIndependentVersions(t *testing.T) {
	t.Parallel()
	protocol := G1IProtocol{}
	renderer := RWKVChatRenderer{}
	if protocol.ID() != G1IActionProtocolV1 {
		t.Fatalf("protocol ID = %q", protocol.ID())
	}
	if renderer.ID() != RWKVPromptRendererV1 {
		t.Fatalf("renderer ID = %q", renderer.ID())
	}
}

func TestG1IProtocolParsesVerifiedEnvelopes(t *testing.T) {
	t.Parallel()
	protocol := G1IProtocol{}
	action, err := protocol.Parse(
		`<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
		continuation.FinishUnknown,
	)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != "tool" || action.Name != "read_file" {
		t.Fatalf("tool action = %+v", action)
	}
	action, err = protocol.Parse(
		"<think>inspect</think>\nRWKV Agent",
		continuation.FinishUnknown,
	)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != "final" || action.Content != "RWKV Agent" {
		t.Fatalf("answer action = %+v", action)
	}
	action, err = protocol.Parse(
		"The protocol uses `<tool_call>...</tool_call>` for tool control frames.",
		continuation.FinishUnknown,
	)
	if err != nil || action.Type != "final" {
		t.Fatalf("plain protocol explanation = %+v, error = %v", action, err)
	}
	for _, invalid := range []string{
		`{"name":"read_file","arguments":{"path":"README.md"}}`,
		`<tool_call>{"name":"read_file","arguments":{}}</tool_call> trailing`,
		`<answer></answer>`,
		`<think>unfinished<answer>no</answer>`,
	} {
		if _, err := protocol.Parse(invalid, continuation.FinishUnknown); err == nil {
			t.Fatalf("invalid envelope accepted: %q", invalid)
		}
	}
	action, err = protocol.Parse(
		`<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}`,
		continuation.FinishStop,
	)
	if err != nil || action.Type != "tool" {
		t.Fatalf("stopped tool action = %+v, error = %v", action, err)
	}
	if _, err := protocol.Parse("truncated answer", continuation.FinishLength); err == nil {
		t.Fatal("length-truncated plain answer was accepted")
	}
}

func TestG1IProtocolUsesStageSpecificStops(t *testing.T) {
	t.Parallel()
	protocol := G1IProtocol{}
	decision := strings.Join(protocol.Stops(StageDecision), "\x00")
	answer := strings.Join(protocol.Stops(StageAnswer), "\x00")
	if !strings.Contains(decision, "</tool_call>") ||
		strings.Contains(decision, "</answer>") {
		t.Fatalf("decision stops = %q", protocol.Stops(StageDecision))
	}
	if !strings.Contains(answer, "</answer>") ||
		strings.Contains(answer, "</tool_call>") {
		t.Fatalf("answer stops = %q", protocol.Stops(StageAnswer))
	}
}

func TestG1IProtocolCompactsToolResultsForContinuation(t *testing.T) {
	t.Parallel()
	longContent := "# Project\n" + strings.Repeat("irrelevant material ", 300) +
		"\nThe requested sentinel is ORANGE-42.\n" +
		strings.Repeat("trailing material ", 300)
	encoded, err := json.Marshal(toolResult{
		OK:   true,
		Tool: "read_file",
		Result: map[string]any{
			"path":    "README.md",
			"content": longContent,
		},
	})
	if err != nil {
		t.Fatal(err)
	}

	compacted := compactToolResult(
		"Find the requested sentinel in README.md.",
		"<tool_result>"+string(encoded)+"</tool_result>",
	)
	if !strings.Contains(compacted, "# Project") ||
		!strings.Contains(compacted, "ORANGE-42") ||
		!strings.Contains(compacted, "tool result compacted") {
		t.Fatalf("compacted tool result = %q", compacted)
	}
	if len([]rune(compacted)) >= len([]rune(longContent)) {
		t.Fatal("tool result was not compacted")
	}
}

func TestRWKVChatRendererBuildsRawContinuationPrompt(t *testing.T) {
	t.Parallel()
	prompt, err := (RWKVChatRenderer{Reasoning: true}).Render([]Message{
		{Role: RoleUser, Content: "task"},
		{Role: RoleAssistant, Content: `<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`},
		{Role: RoleTool, Content: `<tool_result>{"ok":true,"tool":"read_file","result":{"content":"text"}}</tool_result>`},
	})
	if err != nil {
		t.Fatal(err)
	}
	for _, fragment := range []string{
		"User: task",
		"Assistant: <tool_call>",
		"Tool: <tool_result>",
		"Assistant: <think>\n</think>",
	} {
		if !strings.Contains(prompt, fragment) {
			t.Fatalf("prompt does not contain %q:\n%s", fragment, prompt)
		}
	}
}
