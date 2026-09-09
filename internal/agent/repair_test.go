package agent

import (
	"slices"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// TestParserReportsRepairIDs locks the machine-readable half of the tolerant
// parsers: every recovery stage names itself, so a prompt change that silently
// moves work into the parser is visible in trace/manifest instead of hiding
// behind one boolean.
func TestParserReportsRepairIDs(t *testing.T) {
	t.Parallel()
	cases := []struct {
		name     string
		protocol ActionProtocol
		value    string
		want     []wire.Repair
	}{
		{
			name:     "fenced parser strips a leading think block",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `<think>let me check</think>{"name":"echo","arguments":{"value":"x"}}`,
			want:     []wire.Repair{wire.RepairThinkStripped},
		},
		{
			name:     "fenced parser recovers the xml envelope",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `<tool_call>{"name":"echo","arguments":{"value":"x"}}</tool_call>`,
			want:     []wire.Repair{wire.RepairEnvelopeRecovered},
		},
		{
			name:     "fenced parser accepts the tool_calls array",
			protocol: G1IFunctionProtocol{},
			value:    `<tool_calls>[{"name":"echo","arguments":{"value":"x"}}]</tool_calls>`,
			want:     []wire.Repair{wire.RepairArrayEnvelope},
		},
		{
			name:     "fenced parser flattens the function wrapper",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `{"function":{"name":"echo","arguments":{"value":"x"}}}`,
			want:     []wire.Repair{wire.RepairFunctionWrapper},
		},
		{
			name:     "fenced parser accepts key aliases",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `{"command":"echo","args":{"value":"x"}}`,
			want:     []wire.Repair{wire.RepairKeyAlias},
		},
		{
			name:     "fenced parser hoists unknown keys",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `{"name":"echo","value":"x"}`,
			want:     []wire.Repair{wire.RepairArgumentsHoisted},
		},
		{
			name:     "fenced parser parses stringified arguments",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `{"name":"echo","arguments":"{\"value\":\"x\"}"}`,
			want:     []wire.Repair{wire.RepairStringifiedArguments},
		},
		{
			name:     "fenced parser infers a missing tool name",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `{"path":"notes/a.txt"}`,
			want:     []wire.Repair{wire.RepairArgumentsHoisted, wire.RepairNameInferred},
		},
		{
			name:     "xml parser recovers a bare path payload",
			protocol: G1IProtocol{},
			value:    `<tool_call>{"path":"notes/a.txt"}</tool_call>`,
			want:     []wire.Repair{wire.RepairPathArgument},
		},
		{
			name:     "xml parser renames a legacy tool",
			protocol: G1IProtocol{},
			value:    `<tool_call>{"name":"reader","arguments":{"path":"notes/a.txt"}}</tool_call>`,
			want:     []wire.Repair{wire.RepairToolRenamed},
		},
		{
			name:     "xml parser accepts the legacy self-closing call",
			protocol: G1IProtocol{},
			value:    `<read_file file_path="notes/a.txt"/>`,
			want:     []wire.Repair{wire.RepairLegacyXMLCall, wire.RepairXMLPathAlias},
		},
		{
			name:     "clean call records no repair",
			protocol: G1IFunctionProtocol{Product: true},
			value:    `{"name":"echo","arguments":{"value":"x"}}`,
			want:     nil,
		},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			action, err := testCase.protocol.Parse(testCase.value, continuation.FinishStop)
			if err != nil {
				t.Fatalf("Parse: %v", err)
			}
			if action.Type != ActionTypeTool {
				t.Fatalf("action type = %q, want tool", action.Type)
			}
			if !slices.Equal(action.Repairs, testCase.want) {
				t.Fatalf("repairs = %v, want %v", action.Repairs, testCase.want)
			}
			if action.ProtocolRepaired != (len(testCase.want) > 0) {
				t.Fatalf("ProtocolRepaired = %v for repairs %v", action.ProtocolRepaired, action.Repairs)
			}
			// Every emitted ID must be inside the transcript's declared
			// recovery vocabulary.
			spec := wire.Default()
			if _, ok := testCase.protocol.(G1IFunctionProtocol); ok {
				spec.Format = wire.FormatMDFence
			}
			for _, repair := range action.Repairs {
				if !spec.AllowsRepair(repair) {
					t.Fatalf("repair %q is not declared for %s", repair, spec.Format)
				}
			}
		})
	}
}

// TestRepairIDsAreStable guards the manifest contract: the strings go into
// run.json verbatim, so a rename breaks comparability with archived runs.
func TestRepairIDsAreStable(t *testing.T) {
	t.Parallel()
	ids := wire.RepairIDs()
	if len(ids) != 14 {
		t.Fatalf("repair ID count = %d, want 14", len(ids))
	}
	seen := make(map[string]struct{}, len(ids))
	for _, id := range ids {
		if id == "" {
			t.Fatal("empty repair ID")
		}
		if _, duplicate := seen[id]; duplicate {
			t.Fatalf("duplicate repair ID %q", id)
		}
		seen[id] = struct{}{}
	}
}
