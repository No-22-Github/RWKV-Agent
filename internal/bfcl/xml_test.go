package bfcl

import (
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

var xmlTestEntry = Case{
	ID:       "xml_test_simple_python_0",
	Category: "simple_python",
	Functions: []json.RawMessage{
		json.RawMessage(`{"name":"multiply","description":"Multiply two integers","parameters":{"type":"dict","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"]}}`),
	},
	Messages: []Message{
		{Role: "system", Content: "You are a calculator service."},
		{Role: "user", Content: "Multiply 3 and 4."},
	},
}

func TestRenderPromptXMLMirrorsProductTranscript(t *testing.T) {
	rendered, err := RenderPromptXML(xmlTestEntry, inference.ThinkingFast)
	if err != nil {
		t.Fatalf("RenderPromptXML: %v", err)
	}
	for _, want := range []string{
		"You are a local-first assistant",
		"- multiply: Multiply two integers Arguments: {",
		"System: You are a calculator service.",
		"User: Multiply 3 and 4.",
		"Assistant: " + inference.ThinkBlockFast,
	} {
		if !strings.Contains(rendered.Prompt, want) {
			t.Fatalf("prompt missing %q:\n%s", want, rendered.Prompt)
		}
	}
	if rendered.Anchor != inference.ThinkBlockFast {
		t.Fatalf("anchor %q, want fast think prefix", rendered.Anchor)
	}
	if strings.HasSuffix(rendered.Prompt, ">") {
		t.Fatalf("prompt must withhold the think-closing >:\n%s", rendered.Prompt)
	}
}

func TestRenderPromptXMLParallelContractOnlyForParallelSplits(t *testing.T) {
	rendered, err := RenderPromptXML(xmlTestEntry, inference.ThinkingFast)
	if err != nil {
		t.Fatalf("RenderPromptXML: %v", err)
	}
	if strings.Contains(rendered.Prompt, xmlParallelContract) {
		t.Fatalf("non-parallel case must not carry the parallel contract")
	}
	parallel := xmlTestEntry
	parallel.Category = "parallel"
	rendered, err = RenderPromptXML(parallel, inference.ThinkingFast)
	if err != nil {
		t.Fatalf("RenderPromptXML parallel: %v", err)
	}
	if !strings.Contains(rendered.Prompt, xmlParallelContract) {
		t.Fatalf("parallel case must carry the multi-envelope contract")
	}
}

func TestRenderPromptXMLAnchored(t *testing.T) {
	rendered, err := xmlRenderPromptAnchored(xmlTestEntry, inference.ThinkingFast)
	if err != nil {
		t.Fatalf("xmlRenderPromptAnchored: %v", err)
	}
	suffix := inference.ThinkBlockFast + ">" + XMLAnchor
	if !strings.HasSuffix(rendered.Prompt, suffix) {
		t.Fatalf("anchored prompt must end with %q:\n%s", suffix, rendered.Prompt)
	}
	if rendered.Anchor != XMLAnchor {
		t.Fatalf("anchor %q, want %q", rendered.Anchor, XMLAnchor)
	}
}

func TestAssembleXMLAnchoredContent(t *testing.T) {
	generated := `calculate_triangle_area","arguments":{"base":10}} </tool_call>`
	content, mode := assembleXMLAnchoredContent(XMLAnchor, generated)
	if mode != "prefill_continuation" || content != XMLAnchor+generated {
		t.Fatalf("prefill_continuation: mode=%s content=%q", mode, content)
	}
	content, mode = assembleXMLAnchoredContent(XMLAnchor, "> <tool_call>{\"name\":\"f\",\"arguments\":{}}</tool_call>")
	if mode != "self_contained" || !strings.HasPrefix(content, "<tool_call>") {
		t.Fatalf("self_contained: mode=%s content=%q", mode, content)
	}
	content, mode = assembleXMLAnchoredContent(XMLAnchor, `{"name":"f","arguments":{}}`)
	if mode != "envelope_self_contained" || !strings.HasPrefix(content, "<tool_call>{\"name\":\"f\"") {
		t.Fatalf("envelope_self_contained: mode=%s content=%q", mode, content)
	}
}

func TestParseXMLAnchoredFlow(t *testing.T) {
	// Full anchored continuation: closed think prefix, prefilled anchor, model
	// completes the name, closes the envelope, and opens a second one.
	body := XMLAnchor + `f","arguments":{"a":1}} </tool_call>` + " <tool_call>{\"name\":\"g\",\"arguments\":{\"b\":\"x\"}}</tool_call>"
	calls, err := ParseXMLCalls(xmlClosedThinkPrefix+body, continuation.FinishStop)
	if err != nil {
		t.Fatalf("anchored parallel flow: %v", err)
	}
	if len(calls) != 2 || calls[0].Name != "f" || calls[1].Name != "g" {
		t.Fatalf("unexpected calls: %+v", calls)
	}

	// Self-contained adoption path also parses through the same prefix.
	content, _ := assembleXMLAnchoredContent(XMLAnchor, "> <tool_call>{\"name\":\"f\",\"arguments\":{}}</tool_call>")
	calls, err = ParseXMLCalls(xmlClosedThinkPrefix+content, continuation.FinishStop)
	if err != nil {
		t.Fatalf("anchored self-contained: %v", err)
	}
	if len(calls) != 1 || calls[0].Name != "f" {
		t.Fatalf("unexpected calls: %+v", calls)
	}
}

func TestParseXMLCallsSingleAndParallel(t *testing.T) {
	calls, err := ParseXMLCalls(
		inference.ThinkBlockFast+"><tool_call>{\"name\":\"multiply\",\"arguments\":{\"a\":3,\"b\":4}}</tool_call>",
		continuation.FinishStop,
	)
	if err != nil {
		t.Fatalf("single continuation output: %v", err)
	}
	if len(calls) != 1 || calls[0].Name != "multiply" || calls[0].Arguments != `{"a":3,"b":4}` {
		t.Fatalf("unexpected calls: %+v", calls)
	}

	parallel := "<tool_call>{\"name\":\"f\",\"arguments\":{\"a\":1}}</tool_call>\n" +
		"<tool_call>{\"name\":\"g\",\"arguments\":{\"b\":\"x\"}}</tool_call>"
	calls, err = ParseXMLCalls("<think></think>"+parallel, continuation.FinishStop)
	if err != nil {
		t.Fatalf("parallel output: %v", err)
	}
	if len(calls) != 2 || calls[0].Name != "f" || calls[1].Name != "g" {
		t.Fatalf("unexpected parallel calls: %+v", calls)
	}
}

func TestParseXMLCallsFramingAndNoCall(t *testing.T) {
	// Reconstructed fast prefill plus a lone > frame, mirroring what the
	// model receives and emits around the withheld think block.
	output := inference.ThinkBlockFast + "> " + "<tool_call>{\"name\":\"f\",\"arguments\":{}}</tool_call>"
	calls, err := ParseXMLCalls(output, continuation.FinishStop)
	if err != nil {
		t.Fatalf("framed output: %v", err)
	}
	if len(calls) != 1 || calls[0].Name != "f" {
		t.Fatalf("unexpected calls: %+v", calls)
	}

	for _, answer := range []string{
		"The area is 25 square meters.",
		"",
		">",
		inference.ThinkBlockFast + "> Done.",
	} {
		calls, err = ParseXMLCalls(answer, continuation.FinishStop)
		if err != nil {
			t.Fatalf("answer %q: unexpected error %v", answer, err)
		}
		if len(calls) != 0 {
			t.Fatalf("answer %q must parse as no call, got %+v", answer, calls)
		}
	}
}

func TestParseXMLCallsFailures(t *testing.T) {
	if _, err := ParseXMLCalls(inference.ThinkBlockFast+" without closing", continuation.FinishLength); err == nil {
		t.Fatalf("unclosed think block must fail")
	}
	if _, err := ParseXMLCalls("<tool_call>{\"name\":\"f\",\"arguments\":{\"a\":1}}", continuation.FinishLength); err == nil {
		t.Fatalf("unclosed envelope at length must fail")
	}
	if _, err := ParseXMLCalls("<tool_call>{\"name\":\"f\",\"arguments\":{}}", continuation.FinishStop); err != nil {
		t.Fatalf("unclosed envelope at stop must be accepted: %v", err)
	}
	if _, err := ParseXMLCalls("<tool_call>{\"name\":\"f\",\"arguments\":\"{}\"}</tool_call>", continuation.FinishStop); err == nil {
		t.Fatalf("stringified arguments must fail strict parsing")
	}
	if _, err := ParseXMLCalls("<tool_call>{\"name\":\"f\",\"arguments\":{},\"extra\":1}</tool_call>", continuation.FinishStop); err == nil {
		t.Fatalf("unknown envelope fields must fail strict parsing")
	}
}
