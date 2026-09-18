package agent

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func hintToolSpecs(names ...string) []ToolSpec {
	specs := make([]ToolSpec, 0, len(names))
	for _, name := range names {
		specs = append(specs, ToolSpec{Name: name, Description: name, Arguments: "{}"})
	}
	return specs
}

// TestSourceHintSentence pins the exact sentence for the full workbank
// catalog and its degradation when the catalog lacks the web tools (the
// bfcl irrelevance subset) or the file tools entirely.
func TestSourceHintSentence(t *testing.T) {
	full := sourceHintSentence(hintToolSpecs("calculator", "list_files", "web_search", "read_file", "web_fetch", "search_text"))
	want := "The user's files are in the current workspace; use list_files, search_text and read_file for them. " +
		"Use web_search and web_fetch only for public information that is not in the workspace.\n"
	if full != want {
		t.Fatalf("full-catalog sentence:\nwant %q\n got %q", want, full)
	}
	localOnly := sourceHintSentence(hintToolSpecs("list_files", "read_file"))
	if localOnly != "The user's files are in the current workspace; use list_files and read_file for them.\n" {
		t.Fatalf("local-only sentence = %q", localOnly)
	}
	webOnly := sourceHintSentence(hintToolSpecs("web_search"))
	if webOnly != "Use web_search only for public information that is not in the workspace.\n" {
		t.Fatalf("web-only sentence = %q", webOnly)
	}
	if empty := sourceHintSentence(hintToolSpecs("calculator")); empty != "" {
		t.Fatalf("empty sentence = %q", empty)
	}
}

// TestSourceHintPromptInsertion locks the hint to one sentence after the
// opener line: everything else in the control prompt stays byte-identical.
func TestSourceHintPromptInsertion(t *testing.T) {
	specs := hintToolSpecs("list_files", "read_file", "search_text", "web_search", "web_fetch")
	base := G1Protocol{SemanticNoTool: true, AlignQwen36: true, BareExamples: true}
	hinted := base
	hinted.SourceHint = true
	without := base.Instructions(specs, inference.ThinkingOff)
	with := hinted.Instructions(specs, inference.ThinkingOff)
	cut := strings.Index(without, "\n\nChoose one action:")
	if cut < 0 {
		t.Fatal("control prompt lost the Choose one action block")
	}
	expected := without[:cut+1] + sourceHintSentence(specs) + without[cut+1:]
	if with != expected {
		t.Fatalf("hinted control prompt is not the base prompt plus one sentence:\nwant %q\n got %q", expected, with)
	}
}

// TestSourceHintProfileRoundTrip guards the exact profile the S1 run uses and
// the byte-identity of the S0 control prompt.
func TestSourceHintProfileRoundTrip(t *testing.T) {
	spec, _, err := wire.Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage+src-hint")
	if err != nil {
		t.Fatalf("Resolve(S1 profile): %v", err)
	}
	options, err := OptionsWithWire(Options{}, spec)
	if err != nil {
		t.Fatalf("OptionsWithWire: %v", err)
	}
	if options.SourceHint != "on" {
		t.Fatalf("options.SourceHint = %q", options.SourceHint)
	}
	protocol, ok := options.Protocol.(G1Protocol)
	if !ok || !protocol.SourceHint {
		t.Fatalf("protocol = %T, want G1Protocol with SourceHint set", options.Protocol)
	}
	control := protocol.Instructions(hintToolSpecs("list_files", "read_file", "search_text", "web_search", "web_fetch"), inference.ThinkingOff)
	if !strings.Contains(control, "The user's files are in the current workspace") {
		t.Fatal("S1 profile control prompt lacks the source hint sentence")
	}

	plainSpec, _, err := wire.Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage")
	if err != nil {
		t.Fatalf("Resolve(S0 profile): %v", err)
	}
	plainOptions, err := OptionsWithWire(Options{}, plainSpec)
	if err != nil {
		t.Fatalf("OptionsWithWire(S0): %v", err)
	}
	if plainOptions.SourceHint == "on" {
		t.Fatal("S0 profile turned the source hint on")
	}
	plainProtocol, ok := plainOptions.Protocol.(G1Protocol)
	if !ok {
		t.Fatalf("S0 protocol = %T, want G1Protocol", plainOptions.Protocol)
	}
	plainControl := plainProtocol.Instructions(hintToolSpecs("list_files", "read_file", "search_text", "web_search", "web_fetch"), inference.ThinkingOff)
	if strings.Contains(plainControl, "current workspace") {
		t.Fatal("S0 control prompt carries the source hint sentence")
	}

	derived, err := WireSpecOf(options)
	if err != nil {
		t.Fatalf("WireSpecOf(S1 options): %v", err)
	}
	if derived.SourceHint != wire.SourceHintOn {
		t.Fatalf("round-trip srchint = %q, want on", derived.SourceHint)
	}
}
