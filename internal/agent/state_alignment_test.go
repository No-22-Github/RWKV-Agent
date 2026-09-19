package agent

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestStateFastHistoryMatchesTrainingTranscript(t *testing.T) {
	base, _, err := wire.Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage+think-fast")
	if err != nil {
		t.Fatal(err)
	}
	aligned, err := base.WithOverrides(map[string]string{"history": "think-fast"})
	if err != nil {
		t.Fatal(err)
	}
	options, err := OptionsWithWire(Options{}, aligned)
	if err != nil {
		t.Fatal(err)
	}
	p := options.Protocol.(G1Protocol)
	call := `<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`
	action, err := p.Parse(call, continuation.FinishStop)
	if err != nil {
		t.Fatal(err)
	}
	// Real actions are stored canonically without think. The next prompt must
	// restore the same assistant-history bytes as the supplied training corpus.
	messages := []Message{
		{Role: RoleUser, Content: "Read facts.txt"},
		{Role: RoleAssistant, Content: p.RecordAction(action, ">"+call)},
		{Role: RoleUser, Content: `<tool_response>{"ok":true,"tool":"read_file","result":"OK"}</tool_response>`},
	}
	got, err := options.Renderer.Render(messages)
	if err != nil {
		t.Fatal(err)
	}
	want := "User: Read facts.txt\n\nAssistant: <think></think>" + call +
		"\n\nUser: <tool_response>{\"ok\":true,\"tool\":\"read_file\",\"result\":\"OK\"}</tool_response>\n\nAssistant: <think></think"
	if got != want {
		t.Fatalf("aligned transcript mismatch\ngot: %q\nwant: %q", got, want)
	}
	legacy, err := OptionsWithWire(Options{}, base)
	if err != nil {
		t.Fatal(err)
	}
	old, err := legacy.Renderer.Render(messages)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(old, "Assistant: <think></think>"+call) || old == got {
		t.Fatal("alignment must be opt-in; legacy history changed")
	}
	// Re-rendering an already-prefixed history must not duplicate the prefix.
	messages[1].Content = "<think></think>" + call
	again, err := options.Renderer.Render(messages)
	if err != nil || again != want {
		t.Fatalf("duplicate prefix: %q, %v", again, err)
	}
	if aligned.Hash() == base.Hash() {
		t.Fatal("wire identity did not change")
	}
	if _, err := aligned.WithOverrides(map[string]string{"thinking": "off"}); err == nil {
		t.Fatal("fast history accepted with incompatible current opening")
	}
}

func TestStateFastControlMatchesTrainingExport(t *testing.T) {
	p := G1Protocol{AlignQwen36: true, SemanticNoTool: true, BareExamples: true, OneStage: true}
	none := p.Instructions(nil, inference.ThinkingOff)
	legacyFast := p.Instructions(nil, inference.ThinkingFast)
	p.Experiments.ThinkControl = "off"
	aligned := p.Instructions(nil, inference.ThinkingFast)
	if aligned != none || aligned == legacyFast {
		t.Fatal("training export uses the off-mode system text with fast prefill")
	}
	const trainingLine = "Never mix commentary with a tool call. Do not emit <think>, Markdown fences around tool JSON, or role labels."
	if !strings.Contains(aligned, trainingLine) {
		t.Fatal("training control bytes missing")
	}
	base, _, err := wire.Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage+think-fast")
	if err != nil {
		t.Fatal(err)
	}
	spec, err := base.WithOverrides(map[string]string{"history": "think-fast", "thinkcontrol": "off"})
	if err != nil {
		t.Fatal(err)
	}
	options, err := OptionsWithWire(Options{}, spec)
	if err != nil {
		t.Fatal(err)
	}
	if options.Protocol.Instructions(nil, inference.ThinkingFast) != aligned {
		t.Fatal("wire axis not applied")
	}
}
