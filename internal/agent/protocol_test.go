package agent

import (
	"encoding/json"
	"errors"
	"strings"
	"testing"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestProtocolAndRendererHaveIndependentVersions(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	renderer := RWKVChatRenderer{}
	if protocol.ID() != G1EnvelopeProtocolV1 {
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
	// The model completes the withheld ">" itself; reconstructOutput restores the
	// prefix so the reasoning block parses as one unit.
	output := renderer.reconstructOutput(
		">reasoning</think>\n<tool_call>{\"name\":\"x\",\"arguments\":{}}</tool_call>",
	)
	action, err := (G1Protocol{}).Parse(output, continuation.FinishStop)
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
	output := renderer.reconstructOutput(
		"><tool_call>{\"name\":\"x\",\"arguments\":{}}</tool_call>",
	)
	action, err := (G1Protocol{}).Parse(output, continuation.FinishStop)
	if err != nil || action.Type != "tool" {
		t.Fatalf("fast thinking parse = %+v, %v", action, err)
	}
}

func TestG1ProtocolParsesVerifiedEnvelopes(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	action, err := protocol.Parse(
		`><tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
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

func TestG1ProtocolClassifiesToolExtractionFailures(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	tests := []struct {
		name  string
		value string
		want  error
	}{
		{
			name:  "missing envelope",
			value: `{"name":"read_file","arguments":{"path":"README.md"}}`,
			want:  ErrToolEnvelopeMissing,
		},
		{
			name:  "damaged JSON",
			value: `<tool_call>{"name":"read_file","arguments":`,
			want:  ErrToolJSONDecode,
		},
		{
			name:  "invalid shape",
			value: `<tool_call>{"name":"","arguments":[]}</tool_call>`,
			want:  ErrToolShapeInvalid,
		},
	}
	for _, testCase := range tests {
		t.Run(testCase.name, func(t *testing.T) {
			_, err := protocol.Parse(testCase.value, continuation.FinishStop)
			if !errors.Is(err, testCase.want) {
				t.Fatalf("parse error = %v, want %v", err, testCase.want)
			}
			if ProtocolFailureClassOf(err) == "" {
				t.Fatalf("parse error has no stable failure class: %v", err)
			}
		})
	}
}

func TestG1ProtocolRepairsLegacyXMLToolCall(t *testing.T) {
	t.Parallel()
	action, err := (G1Protocol{}).Parse(
		">\n<read_file file_path=\"/workspace/project-repo.git/README.md\" />",
		continuation.FinishStop,
	)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != "tool" || action.Name != "read_file" || !action.ProtocolRepaired ||
		action.OriginalProtocolFailure != ProtocolFailureToolEnvelopeMissing ||
		string(action.Arguments) != `{"path":"/workspace/project-repo.git/README.md"}` {
		t.Fatalf("legacy XML action = %+v", action)
	}
}

func TestG1ProtocolRepairsG1PluralToolCalls(t *testing.T) {
	t.Parallel()
	action, err := (G1Protocol{}).Parse(
		`><tool_calls>[{"type":"function","function":{"name":"read_file","arguments":"{\"path\":\"README.md\"}"}}]</tool_calls>`,
		continuation.FinishStop,
	)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != "tool" || action.Name != "read_file" || !action.ProtocolRepaired ||
		string(action.Arguments) != `{"path":"README.md"}` {
		t.Fatalf("plural tool action = %+v", action)
	}
}

func TestG1ProtocolRepairsReadFileAliases(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	for _, value := range []string{
		`<tool_call>{"name":"reader","arguments":{"path":"README.md"}}`,
		`<tool_call>{"path":"README.md","args":{}}`,
	} {
		action, err := protocol.Parse(value, continuation.FinishStop)
		if err != nil {
			t.Fatalf("parse %q: %v", value, err)
		}
		if action.Name != "read_file" || string(action.Arguments) != `{"path":"README.md"}` || !action.ProtocolRepaired {
			t.Fatalf("alias action = %+v", action)
		}
	}
}

func TestG1ProtocolClassifiesTruncationCauses(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	runaway := "<think>let me reconsider that once more"
	for _, testCase := range []struct {
		name   string
		value  string
		finish continuation.FinishReason
		want   error
	}{
		{
			name:   "unclosed think without a finish reason",
			value:  runaway,
			finish: continuation.FinishUnknown,
			want:   ErrUnclosedThink,
		},
		{
			name:   "unclosed think reported as length",
			value:  runaway,
			finish: continuation.FinishLength,
			want:   ErrUnclosedThink,
		},
		{
			name:   "plain answer truncated by the budget",
			value:  "the net outflow is",
			finish: continuation.FinishLength,
			want:   ErrOutputTokenLimit,
		},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			_, err := protocol.Parse(testCase.value, testCase.finish)
			if !errors.Is(err, testCase.want) {
				t.Fatalf("error = %v, want %v", err, testCase.want)
			}
			if !errors.Is(err, ErrProtocol) {
				t.Fatalf("error %v does not wrap ErrProtocol", err)
			}
		})
	}
}

func TestG1ProtocolCorrectionTargetsRunawayReasoning(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	unclosed := protocol.Correction(ErrUnclosedThink)
	if !strings.Contains(unclosed, "</think>") {
		t.Fatalf("unclosed think correction omits the closing tag: %q", unclosed)
	}
	if !strings.Contains(unclosed, "Do not restart") {
		t.Fatalf("unclosed think correction does not forbid restarting: %q", unclosed)
	}
	limit := protocol.Correction(ErrOutputTokenLimit)
	if !strings.Contains(limit, "concise") {
		t.Fatalf("token limit correction does not ask for brevity: %q", limit)
	}
	generic := protocol.Correction(errors.New("some other failure"))
	if strings.Contains(generic, "</think>") {
		t.Fatalf("generic correction leaked think guidance: %q", generic)
	}
	for _, correction := range []string{unclosed, limit, generic} {
		if !strings.Contains(correction, "<tool_call>") {
			t.Fatalf("correction omits the action contract: %q", correction)
		}
	}
}

func TestRetryEchoDropsRunawayReasoning(t *testing.T) {
	t.Parallel()
	runaway := "<think>" + strings.Repeat("wait, let me re-read the task. ", 400)
	if echo := retryEcho(runaway, ErrUnclosedThink); echo != "" {
		t.Fatalf("unclosed think was echoed back (%d chars)", len(echo))
	}
	if echo := retryEcho(strings.Repeat("x", 4000), ErrOutputTokenLimit); echo != "" {
		t.Fatalf("long truncated output was echoed back (%d chars)", len(echo))
	}
	short := `<tool_call>{"name":"read_file"}`
	if echo := retryEcho(short, errors.New("invalid tool call")); echo != short {
		t.Fatalf("short invalid action = %q, want it echoed verbatim", echo)
	}
	long := strings.Repeat("汉", 4000)
	echo := retryEcho(long, errors.New("invalid tool call"))
	if !strings.HasSuffix(echo, "[truncated]") {
		t.Fatalf("long echo was not marked truncated: %q", echo[:40])
	}
	if runes := []rune(echo); len(runes) > retryEchoBudget+len("\n[truncated]") {
		t.Fatalf("echo kept %d runes, want at most %d", len(runes), retryEchoBudget)
	}
	if !utf8.ValidString(echo) {
		t.Fatal("echo truncated a multibyte character")
	}
	if echo := retryEcho("   ", errors.New("empty")); echo != "" {
		t.Fatalf("blank action = %q, want empty", echo)
	}
}

func TestG1ProtocolUsesStageSpecificStops(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
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

func TestG1ProtocolAddsFewShotDecisionTrajectories(t *testing.T) {
	t.Parallel()
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read a file.",
		Arguments:   `{"path":"relative file path"}`,
	}}
	baseline := (G1Protocol{}).Instructions(specs, inference.ThinkingOff)
	fewShot := (G1Protocol{FewShot: true}).Instructions(specs, inference.ThinkingOff)
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
	if strings.Contains((G1Protocol{}).PostToolReminder(), "Decision patterns") ||
		!strings.Contains(
			(G1Protocol{FewShot: true}).PostToolReminder(),
			"Call one different tool only for a specific missing fact",
		) {
		t.Fatalf("post-tool reminders were not profile-specific")
	}
}

func TestG1ProtocolUsesThinkingModeAwareControl(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name     string
		mode     inference.ThinkingMode
		want     string
		unwanted string
	}{
		{
			name:     "off",
			mode:     inference.ThinkingOff,
			want:     "Do not emit <think>",
			unwanted: "Assistant prefix ends with",
		},
		{
			name:     "fast",
			mode:     inference.ThinkingFast,
			want:     "Output exactly one action.",
			unwanted: "Close your thinking",
		},
		{
			name:     "full",
			mode:     inference.ThinkingFull,
			want:     "Close your thinking with </think>",
			unwanted: "Do not emit <think>",
		},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			instructions := (G1Protocol{}).Instructions(nil, test.mode)
			if !strings.Contains(instructions, test.want) ||
				strings.Contains(instructions, test.unwanted) {
				t.Fatalf("instructions = %q", instructions)
			}
		})
	}
}

func TestG1ProtocolPreparesAnswerWithFullToolTranscript(t *testing.T) {
	t.Parallel()
	protocol := G1Protocol{}
	messages, prefix := protocol.PrepareAnswer([]Message{
		{Role: RoleSystem, Content: "tool instructions"},
		{Role: RoleUser, Content: "compare files"},
		{Role: RoleAssistant, Content: `<tool_call>{"name":"read_file","arguments":{"path":"a"}}</tool_call>`},
		{Role: RoleTool, Content: `<tool_result>{"result":"first"}</tool_result>`},
		{Role: RoleAssistant, Content: `<tool_call>{"name":"read_file","arguments":{"path":"b"}}</tool_call>`},
		{Role: RoleTool, Content: `<tool_result>{"result":"second"}</tool_result>`},
	}, nil, inference.ThinkingOff)
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

func TestG1ProtocolAddsFewShotOutputContractsToForcedAnswer(t *testing.T) {
	t.Parallel()
	baseline, _ := (G1Protocol{}).PrepareAnswer(nil, nil, inference.ThinkingOff)
	fewShot, _ := (G1Protocol{FewShot: true}).PrepareAnswer(nil, nil, inference.ThinkingOff)
	if strings.Contains(baseline[0].Content, "Output-contract examples") ||
		!strings.Contains(fewShot[0].Content, "Answer with only the flag") ||
		!strings.Contains(fewShot[0].Content, "SKU-17 1248.50") {
		t.Fatalf("answer profiles baseline=%q few-shot=%q", baseline[0].Content, fewShot[0].Content)
	}
}

func TestG1ProtocolUsesThinkingModeAwareForcedAnswerControl(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name     string
		mode     inference.ThinkingMode
		want     string
		unwanted string
	}{
		{
			name:     "off",
			mode:     inference.ThinkingOff,
			want:     "opening <answer> tag is already supplied",
			unwanted: "Assistant prefix ends with",
		},
		{
			name:     "fast",
			mode:     inference.ThinkingFast,
			want:     "Output only <answer>USER_VISIBLE_ANSWER</answer>.",
			unwanted: "opening <answer> tag is already supplied",
		},
		{
			name:     "full",
			mode:     inference.ThinkingFull,
			want:     "Close your thinking with </think>",
			unwanted: "Do not expose hidden reasoning",
		},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			messages, _ := (G1Protocol{}).PrepareAnswer(nil, nil, test.mode)
			control := messages[0].Content
			if !strings.Contains(control, test.want) || strings.Contains(control, test.unwanted) {
				t.Fatalf("control = %q", control)
			}
		})
	}
}

func TestG1ProtocolListsUnverifiedFactsInAnswerStage(t *testing.T) {
	t.Parallel()
	messages, _ := (G1Protocol{}).PrepareAnswer(
		nil,
		[]string{"fx_convert", "weather"},
		inference.ThinkingOff,
	)
	last := messages[len(messages)-1].Content
	for _, fragment := range []string{"- fx_convert", "- weather", "Do not invent a value"} {
		if !strings.Contains(last, fragment) {
			t.Fatalf("unverified reminder does not contain %q: %s", fragment, last)
		}
	}
}

func TestG1ProtocolCompactsToolResultsForContinuation(t *testing.T) {
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

// TestG1ProtocolSemanticNoTool pins the XML transcript's own no_tool action.
// Both product-facing profiles now offer the same abstention semantics, each in
// its own envelope, so the two can be compared on the same eval cases.
func TestG1ProtocolSemanticNoTool(t *testing.T) {
	t.Parallel()
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read one file.",
		Arguments:   `{"path":"relative file path"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"path":{"type":"string"}}}`),
	}}
	enabled := G1Protocol{SemanticNoTool: true}
	if control := enabled.Instructions(specs, inference.ThinkingOff); !strings.Contains(
		control, "- "+SemanticNoToolName+":",
	) {
		t.Fatalf("no_tool missing from the XML catalog:\n%s", control)
	}
	if control := (G1Protocol{}).Instructions(specs, inference.ThinkingOff); strings.Contains(
		control, SemanticNoToolName,
	) {
		t.Fatalf("no_tool leaked into the default XML catalog:\n%s", control)
	}
	call := `<tool_call>{"name":"no_tool","arguments":{"reason":"Nothing to inspect."}}</tool_call>`
	action, err := enabled.Parse(call, continuation.FinishStop)
	if err != nil {
		t.Fatalf("parse xml no_tool: %v", err)
	}
	if action.Type != ActionTypeNoTool || action.Name != SemanticNoToolName ||
		action.NoToolRationale != "Nothing to inspect." {
		t.Fatalf("xml no_tool action = %+v", action)
	}
	// With the switch off the same bytes stay an ordinary tool call, so the
	// Runner rejects it as an unknown tool instead of silently abstaining.
	action, err = (G1Protocol{}).Parse(call, continuation.FinishStop)
	if err != nil || action.Type != ActionTypeTool || action.Name != SemanticNoToolName {
		t.Fatalf("default xml action = %+v, err = %v", action, err)
	}
	// Argument validation is shared with the product profile: unknown fields
	// must fail closed rather than be treated as an abstention.
	if _, err := enabled.Parse(
		`<tool_call>{"name":"no_tool","arguments":{"unexpected":"x"}}</tool_call>`,
		continuation.FinishStop,
	); err == nil {
		t.Fatal("xml no_tool accepted an unknown argument")
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

func TestG1ProtocolAlignQwen36SwapsTagsAndCatalog(t *testing.T) {
	t.Parallel()
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read a file.",
		Arguments:   `{"path":"relative file path"}`,
	}}
	legacy := (G1Protocol{}).Instructions(specs, inference.ThinkingOff)
	aligned := (G1Protocol{AlignQwen36: true}).Instructions(specs, inference.ThinkingOff)
	alignedFewShot := (G1Protocol{AlignQwen36: true, FewShot: true}).Instructions(specs, inference.ThinkingOff)
	for _, fragment := range []string{"Available tools:", "- read_file:", "Tool: <tool_result>"} {
		if strings.Contains(aligned, fragment) {
			t.Fatalf("aligned instructions unexpectedly contain %q:\n%s", fragment, aligned)
		}
		if strings.Contains(alignedFewShot, fragment) {
			t.Fatalf("aligned few-shot instructions unexpectedly contain %q:\n%s", fragment, alignedFewShot)
		}
	}
	for _, fragment := range []string{
		`<tools>[`,
		`{"name":"read_file","description":"Read a file.","arguments":{"path":"relative file path"}}`,
		`]`,
		`</tools>`,
		`User: <tool_response>{"ok":true,"tool":"read_file","result":"1: # Example"}</tool_response>`,
	} {
		if !strings.Contains(aligned, fragment) {
			t.Fatalf("aligned instructions do not contain %q:\n%s", fragment, aligned)
		}
	}
	if strings.Count(alignedFewShot, "<tool_response>") != 6 {
		t.Fatalf("aligned few-shot tool results = %d, want 6 (1 example + 5 trajectory results):\n%s",
			strings.Count(alignedFewShot, "<tool_response>"), alignedFewShot)
	}
	// The legacy shape keeps its own bytes.
	for _, fragment := range []string{"Available tools:", "- read_file:", "Tool: <tool_result>"} {
		if !strings.Contains(legacy, fragment) {
			t.Fatalf("legacy instructions lost %q:\n%s", fragment, legacy)
		}
	}
	if got := (G1Protocol{AlignQwen36: true}).FormatToolResult("read_file", "call-1", "{}"); got != "<tool_response>{}</tool_response>" {
		t.Fatalf("aligned tool result = %q", got)
	}
	if got := (G1Protocol{}).FormatToolResult("read_file", "call-1", "{}"); got != "<tool_result>{}</tool_result>" {
		t.Fatalf("legacy tool result = %q", got)
	}
}

func TestG1ProtocolAcceptsResultEnvelopeEchoes(t *testing.T) {
	t.Parallel()
	for _, align := range []bool{true, false} {
		for _, open := range []string{"<tool_response>", "<tool_result>"} {
			output := open + `<tool_call>{"name":"read_file","arguments":{"path":"a.txt"}}</tool_call>` + "</" + open[1:]
			action, err := (G1Protocol{AlignQwen36: align}).Parse(output, continuation.FinishStop)
			if err != nil {
				t.Fatalf("parse %q: %v", output, err)
			}
			if action.Type != ActionTypeTool || action.Name != "read_file" {
				t.Fatalf("action = %+v", action)
			}
			if !action.ProtocolRepaired {
				t.Fatalf("echoed result envelope was not marked repaired")
			}
		}
	}
}

func TestG1ProtocolNoCallDemoAddsSubstantiveExample(t *testing.T) {
	t.Parallel()
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read a file.",
		Arguments:   `{"path":"relative file path"}`,
	}}
	base := (G1Protocol{AlignQwen36: true}).Instructions(specs, inference.ThinkingOff)
	probe := (G1Protocol{AlignQwen36: true, NoCallDemo: true}).Instructions(specs, inference.ThinkingOff)
	for _, fragment := range []string{
		"User: 底 10 高 5 的三角形面积是多少？",
		"Assistant: 25 平方米。",
	} {
		if strings.Contains(base, fragment) {
			t.Fatalf("base instructions unexpectedly contain %q", fragment)
		}
		if !strings.Contains(probe, fragment) {
			t.Fatalf("probe instructions do not contain %q:\n%s", fragment, probe)
		}
	}
	if !strings.Contains(probe, "User: What tools can you use?") ||
		strings.Index(probe, "Assistant: 25 平方米。") > strings.Index(probe, "User: What tools can you use?") {
		t.Fatalf("no-call demo is not placed with the base examples:\n%s", probe)
	}
}

func TestG1ProtocolAlignQwen36IncludesNoToolInToolsArray(t *testing.T) {
	t.Parallel()
	specs := []ToolSpec{{
		Name:        "read_file",
		Description: "Read a file.",
		Arguments:   `{"path":"relative file path"}`,
	}}
	aligned := (G1Protocol{AlignQwen36: true, SemanticNoTool: true}).Instructions(specs, inference.ThinkingOff)
	for _, fragment := range []string{
		`{"name":"no_tool","description":"Indicate that none of the offered tools is needed.`,
		`"arguments":{"reason":"brief complete user-facing response"}`,
	} {
		if !strings.Contains(aligned, fragment) {
			t.Fatalf("aligned no_tool entry missing %q:\n%s", fragment, aligned)
		}
	}
	if !strings.Contains(aligned, "<tools>[") || !strings.Contains(aligned, "</tools>") {
		t.Fatalf("aligned no_tool instructions lost the tools array:\n%s", aligned)
	}
}
