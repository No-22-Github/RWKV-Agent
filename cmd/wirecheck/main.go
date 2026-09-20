// Command wirecheck validates supervised assistant spans of corpus rows
// through the actual harness parser (agent.G1FunctionProtocol), asserting
// clean parses (0 repairs) and that each span decodes to the intended action.
//
// Input: a JSON file with {"spans":[{"kind":"tool_call|final|no_tool",
// "text":"...","name":...,"arguments":{...},"content":"...","reason":"..."}]}
// or a JSONL file of such objects (one per line). Prints one JSON verdict per
// span; exits nonzero when any span fails.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

type span struct {
	Kind      string          `json:"kind"`
	Text      string          `json:"text"`
	Name      string          `json:"name,omitempty"`
	Arguments json.RawMessage `json:"arguments,omitempty"`
	Content   string          `json:"content,omitempty"`
	Reason    string          `json:"reason,omitempty"`
}

type verdict struct {
	OK     bool     `json:"ok"`
	Kind   string   `json:"kind"`
	Errors []string `json:"errors,omitempty"`
}

func main() {
	fs := flag.NewFlagSet("wirecheck", flag.ContinueOnError)
	path := fs.String("in", "", "input json or jsonl file")
	if err := fs.Parse(os.Args[1:]); err != nil {
		os.Exit(2)
	}
	if *path == "" {
		fmt.Fprintln(os.Stderr, "wirecheck: --in is required")
		os.Exit(2)
	}
	data, err := os.ReadFile(*path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "wirecheck: %v\n", err)
		os.Exit(1)
	}
	spans := decodeSpans(data)
	protocol := agent.G1FunctionProtocol{Product: true, SemanticNoTool: true}
	failures := 0
	out := make([]verdict, 0, len(spans))
	for _, s := range spans {
		v := checkSpan(protocol, s)
		out = append(out, v)
		if !v.OK {
			failures++
		}
	}
	encoded, _ := json.Marshal(out)
	fmt.Println(string(encoded))
	if failures > 0 {
		fmt.Fprintf(os.Stderr, "wirecheck: %d/%d spans failed\n", failures, len(spans))
		os.Exit(1)
	}
}

func decodeSpans(data []byte) []span {
	text := strings.TrimSpace(string(data))
	if strings.HasPrefix(text, "[") {
		var spans []span
		if err := json.Unmarshal(data, &spans); err == nil {
			return spans
		}
	}
	var spans []span
	for _, line := range strings.Split(text, "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		var one span
		if err := json.Unmarshal([]byte(line), &one); err != nil {
			continue
		}
		spans = append(spans, one)
	}
	return spans
}

func checkSpan(protocol agent.G1FunctionProtocol, s span) verdict {
	v := verdict{Kind: s.Kind}
	// Structural strictness before the parser: the supervised span must be
	// exactly one envelope (calls) or plain text (finals) — no mixed
	// commentary, no repeated envelopes, no role labels, no think.
	trimmed := strings.TrimSpace(s.Text)
	switch s.Kind {
	case "tool_call", "no_tool":
		if !strings.HasPrefix(trimmed, "<tool_call>") || !strings.HasSuffix(trimmed, "</tool_call>") {
			v.Errors = append(v.Errors, "call span is not exactly one <tool_call> envelope")
		} else if strings.Count(trimmed, "<tool_call>") != 1 || strings.Count(trimmed, "</tool_call>") != 1 {
			v.Errors = append(v.Errors, "call span repeats the envelope")
		}
	case "final":
		for _, marker := range []string{"<tool_call>", "</tool_call>", "<tool_response>", "<tool_result>", "<answer>", "<think>", "</think>", "User:", "System:", "Assistant:"} {
			if strings.Contains(trimmed, marker) {
				v.Errors = append(v.Errors, "final span contains forbidden marker "+marker)
			}
		}
	}
	action, err := protocol.Parse(s.Text, continuation.FinishStop)
	if err != nil {
		v.Errors = append(v.Errors, "parse error: "+err.Error())
		v.OK = false
		return v
	}
	// The trained action form under xml-v1+align-qwen36+no-tool+bare+one-stage
	// carries the <tool_call> envelope (docs/corpus-g1k-wire-format.md §4/§7),
	// which the parser decodes via the envelope_recovered tolerance. That one
	// repair class is therefore expected on call spans; every other repair
	// (think strip, JSON surgery, key aliases, hoisting, legacy shapes) means
	// the supervised bytes are not the trained form and fails the check.
	allowed := map[wire.Repair]bool{}
	if s.Kind == "tool_call" || s.Kind == "no_tool" {
		allowed[wire.RepairEnvelopeRecovered] = true
	}
	for _, repair := range action.Repairs {
		if !allowed[repair] {
			v.Errors = append(v.Errors, fmt.Sprintf("unexpected repair: %v", repair))
		}
	}
	switch s.Kind {
	case "tool_call":
		if action.Type != agent.ActionTypeTool {
			v.Errors = append(v.Errors, "type = "+action.Type+", want tool")
			break
		}
		if action.Name != s.Name {
			v.Errors = append(v.Errors, fmt.Sprintf("name = %q, want %q", action.Name, s.Name))
		}
		if normalizedJSON(action.Arguments) != normalizedJSON(s.Arguments) {
			v.Errors = append(v.Errors, fmt.Sprintf(
				"arguments = %s, want %s", normalizedJSON(action.Arguments), normalizedJSON(s.Arguments)))
		}
	case "no_tool":
		if action.Type != agent.ActionTypeNoTool {
			v.Errors = append(v.Errors, "type = "+action.Type+", want no_tool")
			break
		}
		answer := action.NoToolAnswer
		if answer == "" {
			answer = action.NoToolRationale
		}
		if answer != s.Reason {
			v.Errors = append(v.Errors, fmt.Sprintf("reason = %q, want %q", answer, s.Reason))
		}
	case "final":
		if action.Type != agent.ActionTypeFinal {
			v.Errors = append(v.Errors, "type = "+action.Type+", want final")
			break
		}
		if strings.TrimSpace(action.Content) != strings.TrimSpace(s.Content) {
			v.Errors = append(v.Errors, fmt.Sprintf(
				"content = %q, want %q", action.Content, s.Content))
		}
	default:
		v.Errors = append(v.Errors, "unknown kind "+s.Kind)
	}
	v.OK = len(v.Errors) == 0
	return v
}

// normalizedJSON compares two JSON payloads semantically (decoded and
// re-encoded with sorted keys) so key order cannot mask a mismatch.
func normalizedJSON(raw json.RawMessage) string {
	if len(raw) == 0 {
		return ""
	}
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		return string(raw)
	}
	return string(remarshal(value))
}

func remarshal(value any) []byte {
	switch typed := value.(type) {
	case map[string]any:
		keys := make([]string, 0, len(typed))
		for k := range typed {
			keys = append(keys, k)
		}
		for i := 0; i < len(keys); i++ {
			for j := i + 1; j < len(keys); j++ {
				if keys[j] < keys[i] {
					keys[i], keys[j] = keys[j], keys[i]
				}
			}
		}
		out := []byte{'{'}
		for i, k := range keys {
			if i > 0 {
				out = append(out, ',')
			}
			key, _ := json.Marshal(k)
			out = append(out, key...)
			out = append(out, ':')
			out = append(out, remarshal(typed[k])...)
		}
		return append(out, '}')
	case []any:
		out := []byte{'['}
		for i, item := range typed {
			if i > 0 {
				out = append(out, ',')
			}
			out = append(out, remarshal(item)...)
		}
		return append(out, ']')
	default:
		encoded, _ := json.Marshal(typed)
		return encoded
	}
}
