package agent

import (
	"path/filepath"
	"testing"
)

// goldenCell is one scripted trajectory whose compiled prompts are frozen to
// testdata/golden_prompt/wire/<name>.txt. The name is stable: renaming a cell
// renames its golden file, so a diff in this table is a diff in the covered
// wire matrix.
type goldenCell struct {
	Name    string
	Options Options
	Tools   []Tool
	Outputs []string
	History []Message
	Task    string
}

// wireGoldenCells covers the prefill matrix (A), the action space (B), and the
// loop fallbacks (C) from docs/refactor/wire-spec-p0-baseline.md §5.2. The
// seven hand-written fixtures in prompt_compile_golden_test.go stay untouched
// so their bytes remain the historical baseline; this table adds the cells the
// product profiles actually run (deep anchor, no_tool, router envelope, rescue,
// protocol retry).
func wireGoldenCells() []goldenCell {
	productBase := func(deepAnchor, fakeThink, closedThink bool) Options {
		return Options{
			MaxSteps: 3,
			Protocol: G1FunctionProtocol{
				Product:        true,
				SemanticNoTool: true,
				DeepToolAnchor: deepAnchor,
			},
			Renderer: G1FunctionRenderer{
				Product:           true,
				DecisionFakeThink: fakeThink,
				ClosedFakeThink:   closedThink,
			},
		}
	}
	xmlBase := func() Options {
		return Options{
			MaxSteps: 3,
			Protocol: G1Protocol{},
			Renderer: RWKVChatRenderer{},
		}
	}
	toolCall := `{"name":"echo","arguments":{"value":"ping"}}`
	// The deep anchor ends the prompt inside the object, so the model emits the
	// continuation of the call, not the whole object.
	deepToolCall := `echo","arguments":{"value":"ping"}}`
	return []goldenCell{
		{
			Name:    "product_md_deep_anchor",
			Options: productBase(true, false, false),
			Tools:   []Tool{echoTool{}},
			Outputs: []string{deepToolCall, "All done."},
			Task:    "Check the echo tool",
		},
		{
			Name:    "product_md_fake_think_half",
			Options: productBase(false, true, false),
			Tools:   []Tool{echoTool{}},
			// The model completes the withheld ">" first; the harness strips
			// the prefix it injected before parsing.
			Outputs: []string{">" + toolCall, ">All done."},
			Task:    "Check the echo tool",
		},
		{
			Name:    "product_md_fake_think_closed",
			Options: productBase(false, true, true),
			Tools:   []Tool{echoTool{}},
			Outputs: []string{
				G1DecisionClosedThinkPrefix + toolCall,
				G1DecisionClosedThinkPrefix + "All done.",
			},
			Task: "Check the echo tool",
		},
		{
			Name:    "product_md_no_tool_answer",
			Options: productBase(true, false, false),
			Tools:   []Tool{echoTool{}},
			// A non-empty reason becomes the final reply without another
			// generation.
			Outputs: []string{`no_tool","arguments":{"reason":"Nothing to look up."}}`},
			Task:    "Say hi",
		},
		{
			Name:    "product_md_no_tool_empty_to_answer_stage",
			Options: productBase(true, false, false),
			Tools:   []Tool{echoTool{}},
			// Empty arguments keep the compatibility path: the control prompt
			// switches to the direct-response control and the answer stage runs.
			Outputs: []string{`no_tool","arguments":{}}`, "All done."},
			Task:    "Say hi",
		},
		{
			Name: "product_md_gate_state_reject",
			Options: func() Options {
				options := productBase(true, false, false)
				options.MaxSteps = 4
				options.NoToolGate = "state"
				return options
			}(),
			Tools: []Tool{echoTool{}},
			// The state gate hides no_tool from the catalog until a tool call
			// succeeds; an early emission is rejected with a correction. The
			// rejection keeps the deep anchor armed, so the next decision is
			// still a call continuation; only the executed call clears it.
			Outputs: []string{
				`no_tool","arguments":{"reason":"Already done."}}`,
				`echo","arguments":{"value":"ping"}}`,
				"All done.",
			},
			Task: "Check the echo tool",
		},
		{
			Name: "product_md_rescue_same_tool",
			Options: func() Options {
				options := productBase(true, false, false)
				options.MaxSteps = 5
				options.SameToolRescueLimit = 2
				options.TerminalTool = "submit"
				options.EndOnTerminalTool = true
				return options
			}(),
			Tools: []Tool{echoTool{}, submitTestTool{}},
			// Two successful calls to the same tool trip the spiral rescue:
			// the catalog is rebuilt around submit and one rescue instruction
			// is injected. The terminal tool keeps the deep anchor armed on
			// every decision, so every output is a call continuation.
			Outputs: []string{
				`echo","arguments":{"value":"one"}}`,
				`echo","arguments":{"value":"two"}}`,
				`submit","arguments":{"answer":"All done."}}`,
			},
			Task: "Check the echo tool twice",
		},
		{
			Name: "xml_route_envelope",
			Options: func() Options {
				options := xmlBase()
				options.MaxSteps = 4
				options.Router = G1RouteProtocol{}
				options.RouteRenderer = RWKVChatRenderer{}
				options.RouteRetries = 1
				options.RouteMaxOutputTokens = 8
				return options
			}(),
			Tools: []Tool{echoTool{}},
			// The route stage is one generation; the inspect decision then
			// carries the <tool_call> envelope prefill, so the model continues
			// inside the envelope.
			Outputs: []string{
				"inspect</route>",
				`{"name":"echo","arguments":{"value":"ping"}}</tool_call>`,
				"All done.",
			},
			Task: "Check the echo tool",
		},
		{
			Name: "xml_route_answer_stage",
			Options: func() Options {
				options := xmlBase()
				options.MaxSteps = 3
				options.Router = G1RouteProtocol{}
				options.RouteRenderer = RWKVChatRenderer{}
				options.RouteRetries = 1
				options.RouteMaxOutputTokens = 8
				return options
			}(),
			Tools: []Tool{echoTool{}},
			// The envelope frame belongs to the decision stage only: the forced
			// answer stage must reconstruct its own <answer> opening and must
			// not let the stale decision frame touch the output. Two tool
			// calls keep the turn running until MaxSteps forces the stage.
			Outputs: []string{
				"inspect</route>",
				`{"name":"echo","arguments":{"value":"one"}}</tool_call>`,
				// After a completed tool step the envelope anchor stands down,
				// so this decision emits the whole envelope.
				`<tool_call>{"name":"echo","arguments":{"value":"two"}}</tool_call>`,
				"All done.",
			},
			Task: "Check the echo tool",
		},
		{
			Name: "xml_progressive_route",
			Options: func() Options {
				options := xmlBase()
				options.MaxSteps = 4
				options.ToolRouter = G1ProgressiveToolRouteProtocol{}
				options.RouteRenderer = RWKVChatRenderer{}
				options.ToolBundles = DefaultToolBundles()
				options.RouteRetries = 1
				options.RouteMaxOutputTokens = 8
				return options
			}(),
			Tools: []Tool{bundledEchoTool{name: "echo", bundle: ToolBundleWorkspace}},
			Outputs: []string{
				"inspect:workspace</route>",
				`{"name":"echo","arguments":{"value":"ping"}}</tool_call>`,
				"All done.",
			},
			Task: "Check the echo tool",
		},
		{
			Name: "xml_protocol_retry_unclosed_think",
			Options: func() Options {
				options := xmlBase()
				options.MaxSteps = 4
				options.ProtocolRetries = 1
				return options
			}(),
			Tools: []Tool{echoTool{}},
			// The unclosed think block is dropped from the echo (echoing a
			// runaway reason poisons the retry) and only the correction is
			// appended.
			Outputs: []string{
				"<think>I should check the echo tool",
				"<tool_call>" + toolCall + "</tool_call>",
				"All done.",
			},
			Task: "Check the echo tool",
		},
	}
}

func TestWireGoldenMatrix(t *testing.T) {
	t.Parallel()
	for _, cell := range wireGoldenCells() {
		t.Run(cell.Name, func(t *testing.T) {
			t.Parallel()
			task := cell.Task
			if task == "" {
				task = "Check the echo tool"
			}
			steps := runGoldenTurn(t, cell.Options, cell.Tools, cell.Outputs, cell.History, task)
			compareGoldenPrompt(
				t,
				filepath.Join("wire", cell.Name+".txt"),
				formatGolden(steps),
			)
		})
	}
}
