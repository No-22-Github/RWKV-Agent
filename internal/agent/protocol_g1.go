package agent

import (
	"encoding/json"
	"encoding/xml"
	"errors"
	"fmt"
	"io"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

type G1Protocol struct {
	Experiments wire.Experiments

	FewShot bool
	// SemanticNoTool offers the same text-only abstention action the product
	// profile uses, expressed in this transcript's envelope. It is a protocol
	// pseudo-action: the Runner never executes it and never records evidence.
	SemanticNoTool bool
	// AlignQwen36 switches the transcript tags to the aligned shape: tool
	// results ride in the user turn wrapped in <tool_response> and the catalog
	// is a JSON array inside <tools>. The action envelope (<tool_call>) and
	// every instruction sentence are unchanged.
	AlignQwen36 bool
	// NoCallDemo adds one substantive no-call demonstration to the examples: a
	// real question the tools cannot improve on, answered directly. It
	// is the R1.5 probe for whether the abstention behavior is evocable in
	// context at all (the two base examples are trivia).
	NoCallDemo bool
	// GreetingExamples reduces the example block to the greeting no-call pair
	// only (R3 intermediate state).
	GreetingExamples bool
	// BareExamples removes the example block entirely (R3 full cut). It wins
	// over GreetingExamples; the control axis keeps the two from combining
	// with the few-shot trajectory block.
	BareExamples bool
	// OneStage merges the answer stage into the decision transcript: the
	// forced-answer preparation appends only the plain-text nudge user turn —
	// no answer-control system block, no <answer> prefill. The runner still
	// marks the generation as StageAnswer so the answer-now contract is
	// enforced harness-side.
	OneStage bool
	// SourceHint adds the fixed information-source sentence after the opener
	// line: where the user's files live and what the web tools are for. The
	// sentence names only tools the catalog offers, so a bank with a fixed
	// catalog sees the same bytes in every case.
	SourceHint bool
}

func (G1Protocol) ID() string {
	return G1EnvelopeProtocolV1
}

// sourceHintSentence is the S1 information-source locator: one fixed sentence
// naming the workspace-file tools and the web tools, degraded to whichever of
// the two groups the catalog actually offers. Catalogs without any of those
// tools get no sentence at all.
func sourceHintSentence(specs []ToolSpec) string {
	var files, web []string
	for _, name := range []string{"list_files", "search_text", "read_file"} {
		if hasToolSpec(specs, name) {
			files = append(files, name)
		}
	}
	for _, name := range []string{"web_search", "web_fetch"} {
		if hasToolSpec(specs, name) {
			web = append(web, name)
		}
	}
	sentence := ""
	if len(files) > 0 {
		sentence = "The user's files are in the current workspace; use " + joinToolNames(files) + " for them."
	}
	if len(web) > 0 {
		clause := "Use " + joinToolNames(web) + " only for public information that is not in the workspace."
		if sentence == "" {
			sentence = clause
		} else {
			sentence += " " + clause
		}
	}
	if sentence == "" {
		return ""
	}
	return sentence + "\n"
}

// joinToolNames renders a comma list with "and" before the final name.
func joinToolNames(names []string) string {
	switch len(names) {
	case 0:
		return ""
	case 1:
		return names[0]
	default:
		return strings.Join(names[:len(names)-1], ", ") + " and " + names[len(names)-1]
	}
}

func (protocol G1Protocol) Instructions(
	specs []ToolSpec,
	thinkingMode inference.ThinkingMode,
) string {
	var prompt strings.Builder
	prompt.WriteString("You are a local-first assistant with " + toolAccessDescription(specs) + ". " + PolicyUntrustedData + "\n")
	if protocol.SourceHint {
		prompt.WriteString(sourceHintSentence(specs))
	}
	prompt.WriteString(`
Choose one action:
- If new tool evidence is needed, output exactly one tool call and nothing else:
  <tool_call>{"name":"TOOL_NAME","arguments":{...}}</tool_call>
- Otherwise, answer the user directly in ordinary text without an envelope.
Greetings, thanks, casual conversation, and questions that do not need new tool evidence must be answered directly. Never invoke tools merely because they are available.
After a Tool result, make the same choice again: call one tool if more evidence is needed, or answer directly.
`)
	controlMode := thinkingMode
	if protocol.Experiments.ThinkControl == "off" {
		controlMode = inference.ThinkingOff
	}
	prompt.WriteString(thinkingControl(controlMode))
	prompt.WriteString("\n" + PolicyNoInvention + "\n")
	if protocol.AlignQwen36 {
		prompt.WriteString("<tools>" + protocol.renderToolsJSON(specs) + "</tools>\n")
	} else {
		prompt.WriteString("Available tools:\n")
		for _, spec := range specs {
			fmt.Fprintf(&prompt, "- %s: %s Arguments: %s\n", spec.Name, spec.Description, spec.Arguments)
		}
		if protocol.SemanticNoTool {
			fmt.Fprintf(
				&prompt,
				"- %s: Indicate that none of the offered tools is needed. "+
					"Put a brief, complete user-facing response in reason; it becomes the final reply. "+
					`Arguments: {"reason":"brief complete user-facing response"}`+"\n",
				SemanticNoToolName,
			)
		}
	}
	if protocol.BareExamples {
		// R3 full cut: no example block at all.
		return strings.TrimSpace(prompt.String())
	}
	prompt.WriteString(`
Examples:
User: 你好
Assistant: 你好！有什么我可以帮你的吗？`)
	if protocol.NoCallDemo {
		prompt.WriteString(`
User: 底 10 高 5 的三角形面积是多少？
Assistant: 25 平方米。`)
	}
	if protocol.GreetingExamples {
		return strings.TrimSpace(prompt.String())
	}
	prompt.WriteString(`
User: What tools can you use?
Assistant: Describe only the tools listed above.`)
	if hasToolSpec(specs, "list_files") {
		prompt.WriteString(`
User: Find files under docs.
Assistant: <tool_call>{"name":"list_files","arguments":{"path":"docs"}}</tool_call>`)
	}
	if hasToolSpec(specs, "read_file") {
		result := `{"ok":true,"tool":"read_file","result":"1: # Example"}`
		if protocol.AlignQwen36 {
			prompt.WriteString(`
User: Read README.md and report its title.
Assistant: <tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>
User: ` + protocol.toolResponseEnvelope(result) + `
Assistant: Example`)
		} else {
			prompt.WriteString(`
User: Read README.md and report its title.
Assistant: <tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>
Tool: <tool_result>` + result + `</tool_result>
Assistant: Example`)
		}
	}
	if protocol.FewShot {
		resultLine := func(payload string) string {
			if protocol.AlignQwen36 {
				return "User: " + protocol.toolResponseEnvelope(payload)
			}
			return "Tool: <tool_result>" + payload + "</tool_result>"
		}
		prompt.WriteString(`

Additional complete decision trajectories follow. Learn when to stop or continue, but never copy their paths or facts.

User: Read notes/title.txt and output only its first line.
Assistant: <tool_call>{"name":"read_file","arguments":{"path":"notes/title.txt"}}</tool_call>
` + resultLine(`{"ok":true,"tool":"read_file","result":{"path":"notes/title.txt","content":"Project Aurora\nOwner: Example"}}`) + `
Assistant: Project Aurora

User: Find the migration flag for version 3.1.
Assistant: <tool_call>{"name":"search_text","arguments":{"query":"3.1","path":"docs","case_sensitive":false,"max_results":20}}</tool_call>
` + resultLine(`{"ok":true,"tool":"search_text","result":{"matches":[{"path":"docs/migrate.md","line":8,"text":"Version 3.1 migration"}]}}`) + `
Assistant: <tool_call>{"name":"read_file","arguments":{"path":"docs/migrate.md"}}</tool_call>
` + resultLine(`{"ok":true,"tool":"read_file","result":{"path":"docs/migrate.md","content":"For version 3.1 use --sample-v3."}}`) + `
Assistant: --sample-v3

User: Read config/app.txt and report its value.
Assistant: <tool_call>{"name":"read_file","arguments":{"path":"config/app.txt","max_bytes":64}}</tool_call>
` + resultLine(`{"ok":false,"tool":"read_file","error":"invalid tool arguments: unknown field max_bytes; exact shape is {path}"}`) + `
Assistant: <tool_call>{"name":"read_file","arguments":{"path":"config/app.txt"}}</tool_call>
` + resultLine(`{"ok":true,"tool":"read_file","result":{"path":"config/app.txt","content":"VALUE=cedar"}}`) + `
Assistant: VALUE=cedar`)
	}
	return strings.TrimSpace(prompt.String())
}

func hasToolSpec(specs []ToolSpec, name string) bool {
	for _, spec := range specs {
		if spec.Name == name {
			return true
		}
	}
	return false
}

func toolAccessDescription(specs []ToolSpec) string {
	for _, spec := range specs {
		switch spec.Name {
		case "write_file", "chmod", "run_file", "run_tests":
			return "isolated tools, including the explicitly listed mutation tools"
		}
	}
	return "read-only tools"
}

// toolResponseEnvelope wraps a tool-result payload in the aligned tag. The
// legacy tag lives inline in FormatToolResult and the example strings.
func (protocol G1Protocol) toolResponseEnvelope(payload string) string {
	return "<tool_response>" + payload + "</tool_response>"
}

// renderToolsJSON renders the catalog as the JSON array the markdown training
// transcript uses, one compact entry per line. Entries keep the product
// catalog's own description and flat arguments string, so only the container
// changes relative to the legacy markdown list.
func (protocol G1Protocol) renderToolsJSON(specs []ToolSpec) string {
	type catalogEntry struct {
		Name        string          `json:"name"`
		Description string          `json:"description"`
		Arguments   json.RawMessage `json:"arguments"`
	}
	entries := make([]string, 0, len(specs)+1)
	appendEntry := func(name, description, arguments string) {
		encodedArguments := arguments
		if !json.Valid([]byte(arguments)) {
			encoded, err := json.Marshal(arguments)
			if err != nil {
				return
			}
			encodedArguments = string(encoded)
		}
		encoded, err := json.Marshal(catalogEntry{
			Name:        name,
			Description: description,
			Arguments:   json.RawMessage(encodedArguments),
		})
		if err != nil {
			return
		}
		entries = append(entries, string(encoded))
	}
	for _, spec := range specs {
		appendEntry(spec.Name, spec.Description, spec.Arguments)
	}
	if protocol.SemanticNoTool && protocol.Experiments.Exit == "" {
		appendEntry(
			SemanticNoToolName,
			"Indicate that none of the offered tools is needed. Put a brief, complete user-facing response in reason; it becomes the final reply.",
			`{"reason":"brief complete user-facing response"}`,
		)
	}
	if protocol.SemanticNoTool && protocol.Experiments.Exit != "" {
		appendEntry(protocol.exitName(), "Reply to the user and end the turn. Use it when no tool is needed, when the tool results already contain the answer, or when the task cannot be completed. Put only the final answer in answer.", `{"answer":"the final answer only"}`)
	}
	return "[\n" + strings.Join(entries, ",\n") + "\n]"
}

func thinkingControl(mode inference.ThinkingMode) string {
	switch mode {
	case inference.ThinkingFast:
		return "Never mix commentary with a tool call. Output exactly one action. Do not open a <think> block, use Markdown fences around tool JSON, or emit role labels."
	case inference.ThinkingFull:
		return "Never mix commentary with a tool call. Close your thinking with </think>, then output exactly one action. Do not use Markdown fences around tool JSON or emit role labels."
	default:
		return "Never mix commentary with a tool call. Do not emit <think>, Markdown fences around tool JSON, or role labels."
	}
}

func (protocol G1Protocol) Parse(value string, finish continuation.FinishReason) (Action, error) {
	if protocol.Experiments.Recovery != "" {
		if action, ok := protocol.recoverExperimentalCall(value, finish); ok {
			return action, nil
		}
	}
	candidate := wire.StripLeadingThinkBlocks(strings.TrimSpace(value))
	if finish == continuation.FinishLength {
		if strings.HasPrefix(candidate, "<think>") {
			return Action{}, ErrUnclosedThink
		}
		return Action{}, ErrOutputTokenLimit
	}
	if strings.HasPrefix(candidate, "<think>") {
		return Action{}, ErrUnclosedThink
	}
	// Some RWKV Chat Completions gateways retain the lone ">" that would
	// normally close a withheld thinking prefix. It is framing, not answer
	// content, when the remainder is an explicit tool envelope.
	candidate = wire.TrimWithheldOpening(candidate)
	const (
		toolOpen    = wire.EnvelopePrefix
		toolClose   = wire.EnvelopeClose
		answerOpen  = "<answer>"
		answerClose = "</answer>"
	)
	if strings.HasPrefix(candidate, toolOpen) {
		payload, closed := envelopeContent(candidate, toolOpen, toolClose)
		if !closed && finish != continuation.FinishStop {
			return Action{}, fmt.Errorf("%w: incomplete G1 tool call envelope", ErrToolJSONDecode)
		}
		var call struct {
			Name      string          `json:"name"`
			Arguments json.RawMessage `json:"arguments"`
		}
		repairs := &repairLog{}
		strictDecoded := true
		decoder := json.NewDecoder(strings.NewReader(payload))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&call); err != nil {
			strictDecoded = false
			var object map[string]json.RawMessage
			var path string
			if json.Unmarshal([]byte(payload), &object) != nil ||
				json.Unmarshal(object["path"], &path) != nil || strings.TrimSpace(path) == "" {
				return Action{}, fmt.Errorf("%w: decode G1 tool call: %v", ErrToolJSONDecode, err)
			}
			call.Name = "read_file"
			call.Arguments, _ = json.Marshal(map[string]string{"path": path})
			repairs.mark(wire.RepairPathArgument)
		}
		if call.Name == "reader" || call.Name == "file_reader" {
			call.Name = "read_file"
			repairs.mark(wire.RepairToolRenamed)
		}
		if (strictDecoded && decoder.Decode(&struct{}{}) != io.EOF) ||
			strings.TrimSpace(call.Name) == "" ||
			!isJSONObject(call.Arguments) {
			return Action{}, fmt.Errorf("%w: invalid G1 tool call", ErrToolShapeInvalid)
		}
		originalFailure := ProtocolFailureClass("")
		if repairs.any() {
			originalFailure = ProtocolFailureToolShapeInvalid
		}
		if protocol.SemanticNoTool && call.Name == protocol.exitName() {
			rationale, answer, err := parseSemanticNoToolArguments(call.Arguments)
			if err != nil {
				return Action{}, err
			}
			return Action{
				Type:                    ActionTypeNoTool,
				Name:                    call.Name,
				Arguments:               call.Arguments,
				NoToolRationale:         rationale,
				NoToolAnswer:            answer,
				ProtocolRepaired:        repairs.any(),
				OriginalProtocolFailure: originalFailure,
				Repairs:                 repairs.list(),
			}, nil
		}
		return Action{
			Type:                    ActionTypeTool,
			Name:                    call.Name,
			Arguments:               call.Arguments,
			ProtocolRepaired:        repairs.any(),
			OriginalProtocolFailure: originalFailure,
			Repairs:                 repairs.list(),
		}, nil
	}
	if strings.HasPrefix(candidate, answerOpen) {
		content, closed := envelopeContent(candidate, answerOpen, answerClose)
		if !closed && finish != continuation.FinishStop {
			return Action{}, fmt.Errorf("%w: incomplete G1 answer envelope", ErrProtocol)
		}
		if content == "" {
			return Action{}, fmt.Errorf("%w: empty G1 answer", ErrProtocol)
		}
		return Action{Type: ActionTypeFinal, Content: content}, nil
	}
	if candidate == "" {
		return Action{}, fmt.Errorf("%w: empty model response", ErrProtocol)
	}
	if strings.HasPrefix(candidate, toolClose) {
		return Action{}, fmt.Errorf("%w: unexpected G1 tool call closing tag", ErrToolShapeInvalid)
	}
	// The aligned transcript delivers tool results in the user turn, so the
	// model may echo that envelope around its own action. Accept both the
	// aligned and the legacy result tag, strip one envelope, and re-parse the
	// content so scoring stays comparable across the two shapes.
	if strings.HasPrefix(candidate, "<tool_response>") || strings.HasPrefix(candidate, "<tool_result>") {
		open := "<tool_response>"
		if strings.HasPrefix(candidate, "<tool_result>") {
			open = "<tool_result>"
		}
		inner, _ := envelopeContent(candidate, open, "</"+open[1:])
		if strings.TrimSpace(inner) != "" {
			action, err := protocol.Parse(inner, finish)
			if err == nil {
				action.ProtocolRepaired = true
				action.Repairs = append([]wire.Repair{wire.RepairEnvelopeRecovered}, action.Repairs...)
				if action.OriginalProtocolFailure == "" {
					action.OriginalProtocolFailure = ProtocolFailureToolEnvelopeMissing
				}
			}
			return action, err
		}
	}
	if strings.Contains(candidate, "<tool_calls>") {
		action, err := (G1FunctionProtocol{}).Parse(candidate, finish)
		if err != nil {
			return Action{}, err
		}
		action.ProtocolRepaired = true
		action.Repairs = append([]wire.Repair{wire.RepairEnvelopeRecovered}, action.Repairs...)
		if action.OriginalProtocolFailure == "" {
			action.OriginalProtocolFailure = ProtocolFailureToolEnvelopeMissing
		}
		return action, nil
	}
	if action, ok := parseLegacyXMLToolCall(candidate); ok {
		return action, nil
	}
	if looksLikeBareToolCall(candidate) {
		return Action{}, fmt.Errorf("%w: tool call JSON is missing its G1 envelope", ErrToolEnvelopeMissing)
	}
	return Action{Type: ActionTypeFinal, Content: candidate}, nil
}

// parseLegacyXMLToolCall recovers the compact self-closing function syntax
// emitted by some OpenAI-compatible RWKV checkpoints. Native tool_calls remain
// preferred; this only accepts one complete XML element and still relies on
// Runner validation to reject unknown tools or arguments.
func parseLegacyXMLToolCall(value string) (Action, bool) {
	candidate := strings.TrimSpace(value)
	if strings.HasPrefix(candidate, ">") {
		candidate = strings.TrimSpace(strings.TrimPrefix(candidate, ">"))
	}
	if !strings.HasPrefix(candidate, "<") || !strings.HasSuffix(candidate, "/>") {
		return Action{}, false
	}
	decoder := xml.NewDecoder(strings.NewReader(candidate))
	first, err := decoder.Token()
	if err != nil {
		return Action{}, false
	}
	start, ok := first.(xml.StartElement)
	if !ok || start.Name.Space != "" || !nativeToolNamePattern.MatchString(start.Name.Local) {
		return Action{}, false
	}
	arguments := make(map[string]string, len(start.Attr))
	for _, attribute := range start.Attr {
		if attribute.Name.Space != "" || !nativeToolNamePattern.MatchString(attribute.Name.Local) {
			return Action{}, false
		}
		if _, exists := arguments[attribute.Name.Local]; exists {
			return Action{}, false
		}
		arguments[attribute.Name.Local] = attribute.Value
	}
	end, err := decoder.Token()
	if err != nil {
		return Action{}, false
	}
	closed, ok := end.(xml.EndElement)
	if !ok || closed.Name != start.Name {
		return Action{}, false
	}
	if _, err := decoder.Token(); err != io.EOF {
		return Action{}, false
	}
	repairs := []wire.Repair{wire.RepairLegacyXMLCall}
	if start.Name.Local == "read_file" {
		if path, exists := arguments["file_path"]; exists {
			if _, duplicate := arguments["path"]; duplicate {
				return Action{}, false
			}
			arguments["path"] = path
			delete(arguments, "file_path")
			repairs = append(repairs, wire.RepairXMLPathAlias)
		}
	}
	encoded, err := json.Marshal(arguments)
	if err != nil {
		return Action{}, false
	}
	return Action{
		Type:                    "tool",
		Name:                    start.Name.Local,
		Arguments:               encoded,
		ProtocolRepaired:        true,
		OriginalProtocolFailure: ProtocolFailureToolEnvelopeMissing,
		Repairs:                 repairs,
	}, true
}

func envelopeContent(candidate string, open string, close string) (string, bool) {
	content := strings.TrimPrefix(candidate, open)
	if strings.HasSuffix(content, close) {
		return strings.TrimSpace(strings.TrimSuffix(content, close)), true
	}
	return strings.TrimSpace(content), false
}

func (G1Protocol) Correction(err error) string {
	const action = "Either answer directly in ordinary text, or output exactly one " +
		"<tool_call>{\"name\":\"...\",\"arguments\":{...}}</tool_call> and nothing else."
	switch {
	case errors.Is(err, ErrUnclosedThink):
		return "Your previous reasoning never finished and was cut off. Do not restart it. " +
			"Close the thinking block with </think> immediately, then " + action + " " +
			"Decide with the evidence you already have instead of reasoning further."
	case errors.Is(err, ErrOutputTokenLimit):
		return "Your previous response was cut off by the output limit. Be far more concise. " +
			"Skip preamble and restated reasoning, then " + action
	default:
		return "Your previous response was invalid. " + action
	}
}

func (protocol G1Protocol) RecordAction(action Action, raw string) string {
	if protocol.Experiments.History == "preserve" && action.Type == "tool" {
		return wire.StripLeadingThinkBlocks(strings.TrimSpace(raw))
	}
	if action.Type != "tool" {
		return raw
	}
	payload, err := json.Marshal(struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}{
		Name:      action.Name,
		Arguments: action.Arguments,
	})
	if err != nil {
		return raw
	}
	return "<tool_call>" + string(payload) + "</tool_call>"
}

func (protocol G1Protocol) FormatToolResult(_ string, _ string, payload string) string {
	if protocol.AlignQwen36 {
		return protocol.toolResponseEnvelope(payload)
	}
	return "<tool_result>" + payload + "</tool_result>"
}

// ToolCallPrefix returns the envelope bytes. The runner no longer calls it —
// wire.Spec.DecisionFrame owns the prefill policy — but the bytes stay
// single-sourced here for tests and callers that need the raw constant.
func (G1Protocol) ToolCallPrefix() string {
	return wire.EnvelopePrefix
}

func (protocol G1Protocol) PostToolReminder() string {
	switch protocol.Experiments.Nudge {
	case "none":
		return ""
	case "think":
		return strings.ReplaceAll(postToolDecisionReminder, "Do not open a <think> block or repeat the Tool payload.", "Do not repeat the Tool payload.")
	case "exit":
		return "Use the Tool results above to continue the current task. If the evidence is sufficient, call " + protocol.exitName() + ". Otherwise call another tool only for a specific missing fact. Never repeat a successful tool call."
	}
	if !protocol.FewShot {
		return postToolDecisionReminder
	}
	return `Use the actual Tool results above to continue the current task.
Follow these decision patterns:
- Sufficient: User asks for a code; Tool content contains CODE=EMBER-7; Assistant answers EMBER-7 with no more tool call.
- Insufficient: User asks for a value; Tool only identifies config/value.txt; Assistant calls read_file for config/value.txt.
Answer now if the requested facts are present. Call one different tool only for a specific missing fact. Never repeat a successful call.`
}

func (protocol G1Protocol) PrepareAnswer(
	messages []Message,
	unverified []string,
	thinkingMode inference.ThinkingMode,
) ([]Message, string) {
	if protocol.OneStage {
		// Merged stages: keep the whole transcript as-is (the control prompt
		// and catalog stay in place) and append only the plain-text nudge.
		// The empty prefix tells the runner not to prefill any envelope.
		prepared := append([]Message(nil), messages...)
		prepared = append(prepared, Message{
			Role:    RoleUser,
			Content: oneStageAnswerInstruction(unverified),
		})
		return prepared, ""
	}
	prepared := make([]Message, 0, len(messages)+1)
	answerControl := answerStageControlBase()
	switch thinkingMode {
	case inference.ThinkingFast:
		answerControl += `
Output only <answer>USER_VISIBLE_ANSWER</answer>. Do not open a <think> block.`
	case inference.ThinkingFull:
		answerControl += `
Close your thinking with </think>, then output only <answer>USER_VISIBLE_ANSWER</answer>.`
	default:
		answerControl += `
Do not expose hidden reasoning. The opening <answer> tag is already supplied. Output only the user-visible answer followed by </answer>.`
	}
	if protocol.FewShot {
		answerControl += `
Output-contract examples:
- "Answer with only the flag" -> --sample-flag
- "Answer exactly 'SKU amount'" -> SKU-17 1248.50
- "Answer with only the number rounded to 2 decimals" -> 42.00
Follow the current user's requested format exactly; do not add an introduction or explanation.`
	}
	prepared = append(prepared, Message{
		Role:    RoleSystem,
		Content: answerControl,
	})
	for _, message := range messages {
		if message.Role != RoleSystem {
			prepared = append(prepared, message)
		}
	}
	prepared = append(prepared, Message{
		Role: RoleUser,
		Content: `Tool execution is complete and tools are now unavailable.
Answer the original current task using the Tool results above. If they are insufficient, say what could not be verified.`,
	})
	if len(unverified) > 0 {
		prepared = append(prepared, Message{
			Role: RoleUser,
			Content: "The following requested facts could not be verified because their providers were unavailable:\n- " +
				strings.Join(unverified, "\n- ") +
				"\nState each limitation explicitly. Do not invent a value, quote, rate, time, or conversion for any listed item.",
		})
	}
	return prepared, "<answer>"
}

func (G1Protocol) Stops(stage GenerationStage) []string {
	stops := []string{"\nUser:", "\nSystem:", "\nTool:"}
	if stage == StageAnswer {
		return append([]string{"</answer>"}, stops...)
	}
	return append([]string{"</tool_call>"}, stops...)
}

// oneStageAnswerInstruction is the closing User instruction of the merged
// one-stage answer contract. G1Protocol.PrepareAnswer appends it as its own
// User message; the merge variants fold it into the trailing User message,
// and the rewrite variant keeps it as the single closing instruction.
func oneStageAnswerInstruction(unverified []string) string {
	instruction := `Tool execution is complete and tools are now unavailable.
Answer the original current task directly in ordinary text using the Tool results above. Do not call another tool or repeat the Tool results. If they are insufficient, say what could not be verified.`
	if len(unverified) > 0 {
		instruction += "\nThe following requested facts could not be verified because their providers were unavailable:\n- " +
			strings.Join(unverified, "\n- ") +
			"\nState each limitation explicitly. Do not invent a value, quote, rate, time, or conversion for any listed item."
	}
	return instruction
}

// answerStageControlBase is the no-tools answer control shared by the
// two-stage answer prompt and the rewrite variant. The two-stage branch
// appends its thinking/envelope sentence; the rewrite variant appends its own
// plain-text sentence instead.
func answerStageControlBase() string {
	return `You are the final local-assistant answer stage. Tools are unavailable.
Answer the current task directly in the user's language using the full supplied conversation and Tool results.
` + PolicyUntrustedData + ` ` + PolicyNoInventedFacts + `
If the Tool results do not establish the requested answer, state the limitation clearly.
Do not perform or output another tool call, repeat the Tool results, or emit role labels.
Unless the user explicitly asks for detail, keep the answer concise and use at most five bullets.`
}
