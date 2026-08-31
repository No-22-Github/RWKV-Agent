package bfcl

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// TierXMLBaseline runs the frozen BFCL cases through the product XML envelope
// protocol instead of the wrapped markdown anchor. The transcript mirrors the
// App default: the G1I control prompt with the case's function catalog as tool
// specs, fast-thinking prefill, and no answer-stage or router seam.
const TierXMLBaseline Tier = "xml-baseline"

const RenderProtocolG1IXMLV1 = "bfcl-g1i-xml-v1"

// TierXMLAnchor is TierXMLBaseline plus a deep prefill anchor: the prompt ends
// with a closed fast-think block and `<tool_call>{"name":"`, so the model must
// continue into a well-formed first envelope. It is the XML analog of the
// markdown `{"name":"` anchor and shares its cost: a no-call exit no longer
// exists, so no-call-expected cases are forced into a call.
const TierXMLAnchor Tier = "xml-anchor"

const RenderProtocolG1IXMLAnchorV1 = "bfcl-g1i-xml-anchor-v1"

// XMLAnchor is the envelope prefill appended after the closed think block. The
// model continues with the tool name; parallel cases close the first envelope
// and open further ones.
const XMLAnchor = `<tool_call>{"name":"`

// BFCL single-turn parallel splits expect every call inside one response, so
// parallel categories replace the product "exactly one tool call" contract
// with a multi-envelope one. This mirrors the markdown renderer, which swaps
// in its own array instruction for the same splits.
const xmlParallelContract = "Parallel contract: when several calls are needed, output one <tool_call> block per call in the same response, with no text between blocks."

// Same pattern as agent.protocol_core.go leadingThinkBlocks; kept local because
// the agent regex is unexported. Update both together.
var xmlLeadingThinkBlocks = regexp.MustCompile(`(?s)\A\s*(?:<think>.*?</think>\s*)+`)

// RenderPromptXML builds the product XML transcript for one BFCL case. The
// anchor records the withheld think-prefix so traces show what the model must
// complete first.
func RenderPromptXML(entry Case, thinkingMode inference.ThinkingMode) (RenderedPrompt, error) {
	if thinkingMode == "" {
		thinkingMode = inference.ThinkingFast
	}
	if thinkingMode != inference.ThinkingFast && thinkingMode != inference.ThinkingFull {
		return RenderedPrompt{}, fmt.Errorf("BFCL XML transcript requires fast or full thinking, got %q", thinkingMode)
	}
	if len(entry.Messages) == 0 {
		return RenderedPrompt{}, fmt.Errorf("BFCL case %q requires messages", entry.ID)
	}
	specs := make([]agent.ToolSpec, 0, len(entry.Functions))
	for index, function := range entry.Functions {
		if len(function) == 0 || !json.Valid(function) {
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q function %d is invalid JSON", entry.ID, index)
		}
		var definition struct {
			Name        string          `json:"name"`
			Description string          `json:"description"`
			Parameters  json.RawMessage `json:"parameters"`
		}
		if err := json.Unmarshal(function, &definition); err != nil {
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q function %d: %w", entry.ID, index, err)
		}
		if strings.TrimSpace(definition.Name) == "" {
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q function %d has no name", entry.ID, index)
		}
		specs = append(specs, agent.ToolSpec{
			Name:        definition.Name,
			Description: definition.Description,
			Arguments:   strings.TrimSpace(string(definition.Parameters)),
		})
	}
	instructions := (agent.G1IProtocol{}).Instructions(specs, thinkingMode)
	if strings.Contains(entry.Category, "parallel") {
		instructions += "\n" + xmlParallelContract
	}
	messages := []agent.Message{{Role: agent.RoleSystem, Content: instructions}}
	for index, message := range entry.Messages {
		if strings.TrimSpace(message.Content) == "" {
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q message %d is empty", entry.ID, index)
		}
		switch message.Role {
		case "system":
			messages = append(messages, agent.Message{Role: agent.RoleSystem, Content: message.Content})
		case "user":
			messages = append(messages, agent.Message{Role: agent.RoleUser, Content: message.Content})
		case "assistant":
			messages = append(messages, agent.Message{Role: agent.RoleAssistant, Content: message.Content})
		default:
			return RenderedPrompt{}, fmt.Errorf("BFCL case %q message %d has unsupported role %q", entry.ID, index, message.Role)
		}
	}
	prompt, err := (agent.RWKVChatRenderer{ThinkingMode: thinkingMode}).Render(messages)
	if err != nil {
		return RenderedPrompt{}, err
	}
	anchor := inference.ThinkBlockFast
	if thinkingMode == inference.ThinkingFull {
		anchor = inference.ThinkBlockFull
	}
	return RenderedPrompt{Prompt: prompt, Anchor: anchor}, nil
}

// ParseXMLCalls collects the tool calls from one XML completion. It follows
// the product parser's semantics: leading think blocks and the withheld ">"
// are framing, an output that does not open with <tool_call> is a direct
// answer (zero calls, not an error), and a final envelope truncated by a stop
// token is accepted while a length truncation is a parse failure.
func ParseXMLCalls(value string, finish continuation.FinishReason) ([]toolchat.ToolCall, error) {
	candidate := strings.TrimSpace(value)
	if match := xmlLeadingThinkBlocks.FindStringIndex(candidate); match != nil && match[0] == 0 {
		candidate = strings.TrimSpace(candidate[match[1]:])
	}
	if strings.HasPrefix(candidate, ">") {
		remainder := strings.TrimSpace(strings.TrimPrefix(candidate, ">"))
		if strings.HasPrefix(remainder, "<tool_call") {
			candidate = remainder
		}
	}
	if strings.HasPrefix(candidate, "<think>") {
		return nil, fmt.Errorf("unclosed think block")
	}
	if candidate == "" {
		return nil, nil
	}
	const (
		toolOpen  = "<tool_call>"
		toolClose = "</tool_call>"
	)
	if !strings.HasPrefix(candidate, toolOpen) {
		return nil, nil
	}
	calls := make([]toolchat.ToolCall, 0, 2)
	remaining := candidate
	for {
		rest := strings.TrimPrefix(remaining, toolOpen)
		if len(rest) == len(remaining) {
			break
		}
		end := strings.Index(rest, toolClose)
		if end < 0 {
			if finish != continuation.FinishStop {
				return nil, fmt.Errorf("unterminated G1I tool call envelope")
			}
			object, err := decodeXMLCallPayload(strings.TrimSpace(rest))
			if err != nil {
				return nil, err
			}
			parsed, err := parseStrictCallObject(object)
			if err != nil {
				return nil, err
			}
			calls = append(calls, parsed...)
			break
		}
		object, err := decodeXMLCallPayload(strings.TrimSpace(rest[:end]))
		if err != nil {
			return nil, err
		}
		parsed, err := parseStrictCallObject(object)
		if err != nil {
			return nil, err
		}
		calls = append(calls, parsed...)
		remaining = strings.TrimLeft(rest[end+len(toolClose):], " \t\r\n")
		if !strings.HasPrefix(remaining, toolOpen) {
			break
		}
	}
	return calls, nil
}

func decodeXMLCallPayload(payload string) (map[string]json.RawMessage, error) {
	if payload == "" {
		return nil, fmt.Errorf("empty G1I tool call envelope")
	}
	var object map[string]json.RawMessage
	if err := json.Unmarshal([]byte(payload), &object); err != nil {
		return nil, fmt.Errorf("decode G1I tool call: %w", err)
	}
	return object, nil
}

// reconstructXMLThink restores the withheld think prefix so the parser sees a
// well-formed block; it mirrors agent.RWKVChatRenderer.reconstructOutput for
// the fast prefill the XML baseline uses.
func reconstructXMLThink(output string) string {
	if strings.HasPrefix(strings.TrimSpace(output), "<think>") {
		return output
	}
	return inference.ThinkBlockFast + output
}

func xmlRenderPromptAnchored(entry Case, thinkingMode inference.ThinkingMode) (RenderedPrompt, error) {
	rendered, err := RenderPromptXML(entry, thinkingMode)
	if err != nil {
		return RenderedPrompt{}, err
	}
	// RenderPromptXML ends on the withheld fast-think prefix; close it and
	// prefill the first envelope opener so the model continues with the tool
	// name, mirroring the markdown `{"name":"` anchor mechanics.
	rendered.Prompt += ">" + XMLAnchor
	rendered.Anchor = XMLAnchor
	return rendered, nil
}

// xmlClosedThinkPrefix wraps anchored bodies so the parser strips the think
// block with its usual leading-think rule.
const xmlClosedThinkPrefix = "<think></think>"

// assembleXMLAnchoredContent mirrors assembleMarkdownContent: the anchor lives
// in the prompt, so the parser only sees it if the completion is glued back.
// Completions that ignore the prefill and emit an envelope or call object on
// their own are adopted as-is.
func assembleXMLAnchoredContent(anchor, generated string) (string, string) {
	candidate := strings.TrimSpace(generated)
	candidate = strings.TrimSpace(strings.TrimPrefix(candidate, ">"))
	switch {
	case strings.HasPrefix(candidate, "<tool_call>"):
		return candidate, "self_contained"
	case strings.HasPrefix(candidate, `{"name":"`):
		return "<tool_call>" + candidate, "envelope_self_contained"
	}
	return anchor + candidate, "prefill_continuation"
}

func runXMLCase(parent context.Context, entry Case, options BaselineRunnerOptions) TraceEntry {
	resultEntry := ResultEntry{ID: entry.ID, Category: entry.Category}
	trace := TraceEntry{ResultEntry: resultEntry}
	anchored := options.Tier == TierXMLAnchor
	var rendered RenderedPrompt
	var err error
	if anchored {
		rendered, err = xmlRenderPromptAnchored(entry, inference.ThinkingFast)
	} else {
		rendered, err = RenderPromptXML(entry, inference.ThinkingFast)
	}
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	trace.PromptBytes = len(rendered.Prompt)
	trace.PrefillAnchor = rendered.Anchor
	trace.PromptSHA256 = promptSHA256(rendered.Prompt)
	if options.MaxPromptChars > 0 && len(rendered.Prompt) > options.MaxPromptChars {
		trace.Skipped = true
		trace.Error = fmt.Sprintf("prompt size %d exceeds max_prompt_chars %d", len(rendered.Prompt), options.MaxPromptChars)
		return trace
	}

	ctx, cancel := context.WithTimeout(parent, options.CaseTimeout)
	defer cancel()
	attempt, err := runXMLAttempt(ctx, rendered.Prompt, rendered.Anchor, options, anchored)
	trace.Attempts = append(trace.Attempts, attempt)
	trace.ModelCalls = 1
	accumulateAttempt(&trace, attempt)
	if err != nil {
		trace.Error = err.Error()
		return trace
	}
	outcome, parseErr := parseXMLAttempt(entry, &trace.Attempts[0])
	if parseErr != nil {
		adoptFailedAttempt(&trace, trace.Attempts[0], parseErr)
		return trace
	}
	adoptAttempt(&trace, trace.Attempts[0], outcome, false)
	return trace
}

func runXMLAttempt(ctx context.Context, prompt string, anchor string, options BaselineRunnerOptions, anchored bool) (AttemptTrace, error) {
	attempt := AttemptTrace{
		Attempt:       1,
		PromptSHA256:  promptSHA256(prompt),
		PrefillAnchor: anchor,
	}
	started := time.Now()
	completion, err := options.Generator.Continue(ctx, continuation.Request{
		Model:           options.Model,
		Prompt:          prompt,
		MaxOutputTokens: options.MaxOutputTokens,
		Stops:           baselineStops(options.Transport),
		Sampling: continuation.Sampling{
			Temperature:      options.Temperature,
			TopK:             1,
			TopP:             1,
			PresencePenalty:  0,
			FrequencyPenalty: 0,
			PenaltyDecay:     1,
		},
	}, nil)
	attempt.Latency = time.Since(started).Seconds()
	if err != nil {
		return attempt, err
	}
	attempt.GeneratedContent = completion.Text
	if anchored {
		attempt.Content, attempt.AssemblyMode = assembleXMLAnchoredContent(anchor, completion.Text)
		attempt.Content = xmlClosedThinkPrefix + attempt.Content
	} else {
		attempt.Content = reconstructXMLThink(completion.Text)
	}
	attempt.FinishReason = string(completion.FinishReason)
	attempt.InputTokens = completion.Usage.PromptTokens
	attempt.OutputTokens = completion.Usage.CompletionTokens
	return attempt, nil
}

func parseXMLAttempt(entry Case, attempt *AttemptTrace) (ParseOutcome, error) {
	finish := continuation.FinishReason(attempt.FinishReason)
	calls, err := ParseXMLCalls(attempt.Content, finish)
	if err == nil {
		attempt.Adopted = true
		return ParseOutcome{Calls: calls}, nil
	}
	// Mirror the markdown pipeline: a malformed output on a no-call-expected
	// case is adopted as no-call rather than a protocol failure.
	if isIrrelevance(entry.Category) {
		attempt.NoCall = true
		attempt.Adopted = true
		return ParseOutcome{}, nil
	}
	attempt.ParseError = err.Error()
	return ParseOutcome{}, err
}
