package agent

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestExperimentalRecoveryBoundaries(t *testing.T) {
	call := `<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`
	for _, tc := range []struct {
		name, raw, mode string
		recovered       bool
	}{
		{"preamble", "<think>read</think>\nI'll read it.\n" + call, "preamble", true},
		{"off", "<think>read</think>\nI'll read it.\n" + call, "", false},
		{"salvage", "<think>I need the file.\n" + call, "salvage", true},
		{"no implicit salvage", "<think>I need the file.\n" + call, "preamble", false},
		{"inline quote", "Here is an example: " + call, "salvage", false},
		{"fenced quote", "Example:\n```xml\n" + call + "\n```", "salvage", false},
		{"multiple", "I'll read.\n" + call + "\n" + call, "salvage", false},
		{"extra brace", `<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}}</tool_call>`, "json", true},
		{"ambiguous quote", `<tool_call>{"name":"list_files","arguments":{"max_results":"100}}</tool_call>`, "json", false},
		{"schema placeholder", "<think>Example:\n<tool_call>{\"name\":\"TOOL_NAME\",\"arguments\":{}}", "salvage", false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			p := G1Protocol{Experiments: wire.Experiments{Recovery: tc.mode}}
			a, _ := p.Parse(tc.raw, continuation.FinishStop)
			if a.ProtocolRepaired != tc.recovered {
				t.Fatalf("action=%+v", a)
			}
			if tc.recovered && (a.Type != ActionTypeTool || a.Name == "") {
				t.Fatalf("bad recovered action=%+v", a)
			}
		})
	}
	p := G1Protocol{Experiments: wire.Experiments{Recovery: "salvage"}}
	if a, err := p.Parse("I'll read.\n"+call, continuation.FinishLength); err == nil || a.ProtocolRepaired {
		t.Fatal("token-limit generation was salvaged")
	}
}

func TestExperimentalExitAndNudge(t *testing.T) {
	for _, name := range []string{"no_tool", "submit", "final_answer", "reply"} {
		p := G1Protocol{SemanticNoTool: true, AlignQwen36: true, BareExamples: true, Experiments: wire.Experiments{Exit: name, Nudge: "exit"}}
		control := p.Instructions(nil, inference.ThinkingOff)
		if !strings.Contains(control, `"name":"`+name+`"`) || !strings.Contains(control, `"answer":"the final answer only"`) {
			t.Fatal(control)
		}
		a, err := p.Parse(`<tool_call>{"name":"`+name+`","arguments":{"answer":"950"}}</tool_call>`, continuation.FinishStop)
		if err != nil || a.Type != ActionTypeNoTool || a.NoToolAnswer != "950" {
			t.Fatalf("%+v %v", a, err)
		}
		if !strings.Contains(p.PostToolReminder(), "call "+name) {
			t.Fatal(p.PostToolReminder())
		}
	}
}
