package eval

import (
	"context"
	"errors"
	"strings"
	"testing"
	"time"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestScriptRunRendersCorpusRowsThroughTheHarness(t *testing.T) {
	entries := map[string]ScriptEntry{
		"alpha": {CaseID: "alpha", Outputs: []ScriptOutput{
			{Text: `<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`, Supervised: true},
			{Text: "ALPHA-7", Supervised: true},
		}},
		"beta": {CaseID: "beta", Outputs: []ScriptOutput{
			// A context-only prefix: the failed read stays in the transcript
			// but gets no loss span.
			{Text: `<tool_call>{"name":"read_file","arguments":{"path":"missing.txt"}}</tool_call>`, Supervised: false},
			{Text: `<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`, Supervised: true},
			{Text: "BETA-9", Supervised: true},
		}},
	}
	cases := []Case{
		{ID: "alpha", Description: "a", Files: map[string]string{"facts.txt": "ALPHA-7\n"},
			Turns: []Turn{{Prompt: "Report the code in facts.txt.", Expect: Expectation{OutputContains: []string{"ALPHA-7"}}}}},
		{ID: "beta", Description: "b", Files: map[string]string{"facts.txt": "BETA-9\n"},
			Turns: []Turn{{Prompt: "Report the code in facts.txt.", Expect: Expectation{OutputContains: []string{"BETA-9"}}}}},
	}
	report, err := Run(context.Background(), Config{
		Cases:           cases,
		Suite:           "custom",
		CaseParallelism: 2,
		Runner: agent.Options{
			MaxSteps:                6,
			DecisionMaxOutputTokens: 64,
			Protocol:                agent.G1Protocol{OneStage: true, AlignQwen36: true, SemanticNoTool: true},
			Renderer:                agent.RWKVChatRenderer{},
			Generation:              continuation.Request{MaxOutputTokens: 64},
		},
		GeneratorFactory: ScriptGeneratorFactory(entries),
		CaseTimeout:      10 * time.Second,
		TempDir:          t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	calls := map[string][]ModelCallTrace{}
	for _, record := range report.Trace {
		if record.Kind == "model_call" {
			calls[record.CaseID] = append(calls[record.CaseID], *record.ModelCall)
		}
	}
	for _, result := range report.Summary.Cases {
		if !result.Passed {
			t.Fatalf("case %s failed under its own script: %+v", result.ID, result)
		}
	}

	alpha, err := BuildCorpusText(calls["alpha"], entries["alpha"])
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasSuffix(alpha.Text, "\n\nAssistant: ALPHA-7") {
		t.Fatalf("alpha row does not end with the final answer: %q", tail(alpha.Text))
	}
	if !strings.Contains(alpha.Text, "Use the Tool results above to continue the current task.") {
		t.Fatalf("alpha row lacks the harness post-tool reminder the model sees at eval time")
	}
	assertSpans(t, alpha, []string{
		`<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`,
		"ALPHA-7",
	})

	beta, err := BuildCorpusText(calls["beta"], entries["beta"])
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(beta.Text, `"path":"missing.txt"`) {
		t.Fatalf("beta row dropped its context-only prefix")
	}
	assertSpans(t, beta, []string{
		`<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`,
		"BETA-9",
	})
}

func TestScriptGeneratorFailsPastTheEndOfTheScript(t *testing.T) {
	factory := ScriptGeneratorFactory(map[string]ScriptEntry{
		"only": {CaseID: "only", Outputs: []ScriptOutput{{Text: "done"}}},
	})
	if _, _, err := factory(context.Background()); err == nil {
		t.Fatal("factory accepted a context without a case ID")
	}
	if _, _, err := factory(WithCaseID(context.Background(), "other")); err == nil {
		t.Fatal("factory accepted a case without a script entry")
	}
	generator, _, err := factory(WithCaseID(context.Background(), "only"))
	if err != nil {
		t.Fatal(err)
	}
	result, err := generator.Continue(context.Background(), continuation.Request{}, nil)
	if err != nil || result.Text != "done" {
		t.Fatalf("first generation = %q, %v", result.Text, err)
	}
	if _, err := generator.Continue(context.Background(), continuation.Request{}, nil); !errors.Is(err, ErrScriptExhausted) {
		t.Fatalf("second generation error = %v, want ErrScriptExhausted", err)
	}
}

func TestDecodeScriptRejectsMalformedEntries(t *testing.T) {
	for name, input := range map[string]string{
		"duplicate":     `{"case_id":"a","outputs":[{"text":"x"}]}` + "\n" + `{"case_id":"a","outputs":[{"text":"y"}]}`,
		"empty id":      `{"case_id":"","outputs":[{"text":"x"}]}`,
		"no outputs":    `{"case_id":"a","outputs":[]}`,
		"unknown field": `{"case_id":"a","outputs":[{"text":"x"}],"extra":1}`,
	} {
		if _, err := decodeScript(strings.NewReader(input)); err == nil {
			t.Errorf("%s: decodeScript accepted %q", name, input)
		}
	}
}

func TestBuildCorpusTextRejectsHarnessDivergence(t *testing.T) {
	call := `<tool_call>{"name":"read_file","arguments":{"path":"a"}}</tool_call>`
	first := "System: s\n\nUser: q\n\nAssistant:"
	second := first + " " + call + "\n\nUser: <tool_response>{}</tool_response>\n\nAssistant:"
	entry := ScriptEntry{CaseID: "c", Outputs: []ScriptOutput{{Text: call, Supervised: true}, {Text: "ok", Supervised: true}}}
	trace := func(prompts ...string) []ModelCallTrace {
		out := make([]ModelCallTrace, len(prompts))
		for index, prompt := range prompts {
			out[index] = ModelCallTrace{
				Request:  RequestSnapshot{Prompt: prompt},
				Response: ResponseSnapshot{Text: entry.Outputs[index].Text},
			}
		}
		return out
	}
	if _, err := BuildCorpusText(trace(first, second), entry); err != nil {
		t.Fatalf("faithful trace rejected: %v", err)
	}
	if _, err := BuildCorpusText(trace(first), entry); err == nil {
		t.Error("accepted fewer generations than the script")
	}
	if _, err := BuildCorpusText(trace(first, "System: rewritten\n\nAssistant:"), entry); err == nil {
		t.Error("accepted a transcript that is not append-only")
	}
	rewritten := first + ` <tool_call>{"name":"read_file","arguments":{"path":"b"}}</tool_call>` + "\n\nAssistant:"
	if _, err := BuildCorpusText(trace(first, rewritten), entry); err == nil {
		t.Error("accepted a tool call written back with different arguments")
	}
	failed := trace(first, second)
	failed[0].Error = "upstream down"
	if _, err := BuildCorpusText(failed, entry); err == nil {
		t.Error("accepted a failed generation")
	}
}

func TestBuildCorpusTextKeepsHarnessBytesForCanonicalizedCalls(t *testing.T) {
	raw := `<tool_call>{"name":"search_text","arguments":{"query":"a<b"}}</tool_call>`
	// Go marshals "<" as the six bytes \ u 0 0 3 c.
	escaped := strings.Replace(raw, "a<b", "a"+`\`+"u003cb", 1)
	first := "User: 查询\n\nAssistant:"
	second := first + " " + escaped + "\n\nUser: <tool_response>{}</tool_response>\n\nAssistant:"
	entry := ScriptEntry{CaseID: "c", Outputs: []ScriptOutput{{Text: raw, Supervised: true}, {Text: "完成", Supervised: true}}}
	built, err := BuildCorpusText([]ModelCallTrace{
		{Request: RequestSnapshot{Prompt: first}, Response: ResponseSnapshot{Text: raw}},
		{Request: RequestSnapshot{Prompt: second}, Response: ResponseSnapshot{Text: "完成"}},
	}, entry)
	if err != nil {
		t.Fatal(err)
	}
	if built.Canonicalized != 1 {
		t.Fatalf("canonicalized = %d, want 1", built.Canonicalized)
	}
	// Code point spans over non-ASCII text: the harness bytes, then the answer.
	assertSpans(t, built, []string{escaped, "完成"})
}

// assertSpans checks the row's code point spans cut out exactly want.
func assertSpans(t *testing.T, built CorpusText, want []string) {
	t.Helper()
	if len(built.LossSpans) != len(want) {
		t.Fatalf("spans = %v, want %d spans", built.LossSpans, len(want))
	}
	runes := []rune(built.Text)
	if utf8.RuneCountInString(built.Text) != len(runes) {
		t.Fatal("text is not valid UTF-8")
	}
	for index, span := range built.LossSpans {
		if got := string(runes[span[0]:span[1]]); got != want[index] {
			t.Errorf("span %d = %q, want %q", index, got, want[index])
		}
	}
}

func tail(text string) string {
	if len(text) > 120 {
		return text[len(text)-120:]
	}
	return text
}
