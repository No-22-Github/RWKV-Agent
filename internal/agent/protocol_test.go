package agent

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestProtocolAndRendererHaveIndependentVersions(t *testing.T) {
	t.Parallel()
	protocol := G1IProtocol{}
	renderer := RWKVChatRenderer{}
	if protocol.ID() != G1IActionProtocolV1 {
		t.Fatalf("protocol ID = %q", protocol.ID())
	}
	if protocol.ToolCallPrefix() != "<tool_call>" {
		t.Fatalf("tool call prefix = %q", protocol.ToolCallPrefix())
	}
	if renderer.ID() != RWKVPromptRendererV2 {
		t.Fatalf("renderer ID = %q", renderer.ID())
	}
}

func TestFullThinkingRendererFramesOutputWithoutToolPrefixInjection(t *testing.T) {
	t.Parallel()
	renderer := RWKVChatRenderer{ThinkingMode: inference.ThinkingFull}
	prompt, err := renderer.Render([]Message{{Role: RoleUser, Content: "task"}})
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasSuffix(prompt, "Assistant: <think") {
		t.Fatalf("full thinking prompt = %q", prompt)
	}
	framed, injected := renderer.appendAssistantPrefix(prompt, "<tool_call>")
	if injected || framed != prompt {
		t.Fatalf("full thinking prefix framing = %q, injected=%v", framed, injected)
	}
	output := renderer.reconstructOutput(">inspect</think>\n<tool_call>{\"name\":\"x\",\"arguments\":{}}</tool_call>")
	action, err := (G1IProtocol{}).Parse(output, continuation.FinishStop)
	if err != nil || action.Type != "tool" {
		t.Fatalf("full thinking parse = %+v, %v", action, err)
	}
}

func TestFastThinkingRendererUsesExactTokenBoundary(t *testing.T) {
	t.Parallel()
	renderer := RWKVChatRenderer{ThinkingMode: inference.ThinkingFast}
	prompt, err := renderer.Render([]Message{{Role: RoleUser, Content: "task"}})
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasSuffix(prompt, "Assistant: <think></think") {
		t.Fatalf("fast thinking prompt = %q", prompt)
	}
	framed, injected := renderer.appendAssistantPrefix(prompt, "<tool_call>")
	if injected || framed != prompt {
		t.Fatalf("fast thinking prefix framing = %q, injected=%v", framed, injected)
	}
	output := renderer.reconstructOutput("><tool_call>{\"name\":\"x\",\"arguments\":{}}</tool_call>")
	action, err := (G1IProtocol{}).Parse(output, continuation.FinishStop)
	if err != nil || action.Type != "tool" {
		t.Fatalf("fast thinking parse = %+v, %v", action, err)
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

func TestG1IProtocolAddsFewShotDecisionTrajectories(t *testing.T) {
	t.Parallel()
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read a file.",
		Arguments:   `{"path":"relative file path"}`,
	}}
	baseline := (G1IProtocol{}).Instructions(specs)
	fewShot := (G1IProtocol{FewShot: true}).Instructions(specs)
	if strings.Contains(baseline, "Additional complete decision trajectories") {
		t.Fatalf("baseline unexpectedly contains few-shot trajectories: %q", baseline)
	}
	for _, fragment := range []string{
		"Additional complete decision trajectories",
		"Assistant: Project Aurora",
		`Assistant: <tool_call>{"name":"read_file","arguments":{"path":"docs/migrate.md"}}</tool_call>`,
		`"max_bytes":64`,
		"Assistant: VALUE=cedar",
	} {
		if !strings.Contains(fewShot, fragment) {
			t.Fatalf("few-shot instructions do not contain %q:\n%s", fragment, fewShot)
		}
	}
	if strings.Contains((G1IProtocol{}).PostToolReminder(), "Decision patterns") ||
		!strings.Contains(
			(G1IProtocol{FewShot: true}).PostToolReminder(),
			"Call one different tool only for a specific missing fact",
		) {
		t.Fatalf("post-tool reminders were not profile-specific")
	}
}

func TestG1IProtocolPreparesAnswerWithFullToolTranscript(t *testing.T) {
	t.Parallel()
	protocol := G1IProtocol{}
	messages, prefix := protocol.PrepareAnswer([]Message{
		{Role: RoleSystem, Content: "tool instructions"},
		{Role: RoleUser, Content: "compare files"},
		{Role: RoleAssistant, Content: `<tool_call>{"name":"read_file","arguments":{"path":"a"}}</tool_call>`},
		{Role: RoleTool, Content: `<tool_result>{"result":"first"}</tool_result>`},
		{Role: RoleAssistant, Content: `<tool_call>{"name":"read_file","arguments":{"path":"b"}}</tool_call>`},
		{Role: RoleTool, Content: `<tool_result>{"result":"second"}</tool_result>`},
	}, nil)
	if prefix != "<answer>" || len(messages) != 7 {
		t.Fatalf("prepared messages=%+v prefix=%q", messages, prefix)
	}
	if messages[0].Role != RoleSystem ||
		!strings.Contains(messages[0].Content, "Tools are unavailable") ||
		strings.Contains(messages[0].Content, "tool instructions") {
		t.Fatalf("answer control = %+v", messages[0])
	}
	for _, fragment := range []string{"compare files", `"result":"first"`, `"result":"second"`} {
		found := false
		for _, message := range messages {
			found = found || strings.Contains(message.Content, fragment)
		}
		if !found {
			t.Fatalf("prepared transcript does not contain %q: %+v", fragment, messages)
		}
	}
	if messages[len(messages)-1].Role != RoleUser ||
		!strings.Contains(messages[len(messages)-1].Content, "tools are now unavailable") {
		t.Fatalf("final answer reminder = %+v", messages[len(messages)-1])
	}
}

func TestG1IProtocolAddsFewShotOutputContractsToForcedAnswer(t *testing.T) {
	t.Parallel()
	baseline, _ := (G1IProtocol{}).PrepareAnswer(nil, nil)
	fewShot, _ := (G1IProtocol{FewShot: true}).PrepareAnswer(nil, nil)
	if strings.Contains(baseline[0].Content, "Output-contract examples") ||
		!strings.Contains(fewShot[0].Content, "Answer with only the flag") ||
		!strings.Contains(fewShot[0].Content, "SKU-17 1248.50") {
		t.Fatalf("answer profiles baseline=%q few-shot=%q", baseline[0].Content, fewShot[0].Content)
	}
}

func TestG1IProtocolListsUnverifiedFactsInAnswerStage(t *testing.T) {
	t.Parallel()
	messages, _ := (G1IProtocol{}).PrepareAnswer(nil, []string{"fx_convert", "weather"})
	last := messages[len(messages)-1].Content
	for _, fragment := range []string{"- fx_convert", "- weather", "Do not invent a value"} {
		if !strings.Contains(last, fragment) {
			t.Fatalf("unverified reminder does not contain %q: %s", fragment, last)
		}
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
		"Assistant: <think></think",
	} {
		if !strings.Contains(prompt, fragment) {
			t.Fatalf("prompt does not contain %q:\n%s", fragment, prompt)
		}
	}
}
