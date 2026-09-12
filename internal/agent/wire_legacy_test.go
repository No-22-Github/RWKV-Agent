package agent

import (
	"context"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func legacyGeneration() continuation.Request {
	return continuation.Request{Model: "test-model", MaxOutputTokens: 1024}
}

// legacyProductOptions builds the Markdown product profile as the CLI does.
func legacyProductOptions(noTool, deepAnchor, fakeThink, closedThink bool) Options {
	return ProductHarnessOptions(ProductHarnessConfig{
		MaxSteps:                 6,
		DuplicateReplayLimit:     2,
		DuplicateRescueThreshold: 3,
		SameToolRescueLimit:      3,
		Generation:               legacyGeneration(),
		SemanticNoTool:           noTool,
		DeepToolAnchor:           deepAnchor,
		DecisionFakeThink:        fakeThink,
		ClosedFakeThink:          closedThink,
	})
}

// legacyXMLOptions builds the XML product profile as the CLI does.
func legacyXMLOptions(thinking inference.ThinkingMode, progressive bool) Options {
	return XMLHarnessOptions(XMLHarnessConfig{
		MaxSteps:                 6,
		DuplicateReplayLimit:     2,
		DuplicateRescueThreshold: 3,
		SameToolRescueLimit:      3,
		Generation:               legacyGeneration(),
		ProgressiveTools:         progressive,
		ToolBundles:              DefaultToolBundles(),
		ThinkingMode:             thinking,
	})
}

func TestWireSpecOfReachableCells(t *testing.T) {
	t.Parallel()
	cases := []struct {
		name    string
		options Options
		check   func(*testing.T, wire.Spec)
	}{
		{
			name:    "xml default",
			options: legacyXMLOptions(inference.ThinkingOff, false),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Format != wire.FormatXML || spec.Transcript != wire.TranscriptProduct {
					t.Fatalf("format/transcript = %s/%s", spec.Format, spec.Transcript)
				}
				if spec.Thinking != wire.ThinkingOff || spec.Prefill != wire.PrefillNone {
					t.Fatalf("thinking/prefill = %s/%s", spec.Thinking, spec.Prefill)
				}
				if spec.Abstain != wire.AbstainNone || spec.Route != wire.RouteNone || spec.Catalog != wire.CatalogFull {
					t.Fatalf("abstain/route/catalog = %s/%s/%s", spec.Abstain, spec.Route, spec.Catalog)
				}
			},
		},
		{
			name:    "xml thinking fast",
			options: legacyXMLOptions(inference.ThinkingFast, false),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Thinking != wire.ThinkingFast || spec.Prefill != wire.PrefillNone {
					t.Fatalf("thinking/prefill = %s/%s", spec.Thinking, spec.Prefill)
				}
			},
		},
		{
			name:    "xml progressive",
			options: legacyXMLOptions(inference.ThinkingOff, true),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Route != wire.RouteProgressive || spec.Catalog != wire.CatalogProgressive {
					t.Fatalf("route/catalog = %s/%s", spec.Route, spec.Catalog)
				}
				if spec.Prefill != wire.PrefillEnvelope {
					t.Fatalf("prefill = %s, want envelope", spec.Prefill)
				}
			},
		},
		{
			name: "xml respond-inspect router",
			options: func() Options {
				options := legacyXMLOptions(inference.ThinkingOff, false)
				options.Router = G1RouteProtocol{}
				options.RouteRenderer = RWKVChatRenderer{}
				options.RouteRetries = 1
				return options
			}(),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Route != wire.RouteRespondInspect || spec.Prefill != wire.PrefillEnvelope {
					t.Fatalf("route/prefill = %s/%s", spec.Route, spec.Prefill)
				}
			},
		},
		{
			name:    "md product deep anchor",
			options: legacyProductOptions(true, true, false, false),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Format != wire.FormatMDFence || spec.Transcript != wire.TranscriptProduct {
					t.Fatalf("format/transcript = %s/%s", spec.Format, spec.Transcript)
				}
				if spec.Prefill != wire.PrefillDeepFence || spec.Abstain != wire.AbstainNoTool {
					t.Fatalf("prefill/abstain = %s/%s", spec.Prefill, spec.Abstain)
				}
			},
		},
		{
			name:    "md product shallow fence",
			options: legacyProductOptions(true, false, false, false),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Prefill != wire.PrefillFence || spec.Abstain != wire.AbstainNoTool {
					t.Fatalf("prefill/abstain = %s/%s", spec.Prefill, spec.Abstain)
				}
			},
		},
		{
			name:    "md fake think beats the deep anchor",
			options: legacyProductOptions(true, true, true, false),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Prefill != wire.PrefillFakeThinkHalf {
					t.Fatalf("prefill = %s, want fake-think-half (fake-think owns the opening)", spec.Prefill)
				}
			},
		},
		{
			name:    "md fake think closed",
			options: legacyProductOptions(true, true, true, true),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Prefill != wire.PrefillFakeThinkClosed {
					t.Fatalf("prefill = %s, want fake-think-closed", spec.Prefill)
				}
			},
		},
		{
			name: "primitive upstream",
			options: Options{
				MaxSteps:          8,
				Protocol:          G1FunctionProtocol{AllowRepeatedCalls: true},
				Renderer:          G1FunctionRenderer{HasSubmit: true},
				TerminalTool:      "submit",
				EndOnTerminalTool: true,
				Generation:        legacyGeneration(),
			},
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Format != wire.FormatMDFence || spec.Transcript != wire.TranscriptBenchmark {
					t.Fatalf("format/transcript = %s/%s", spec.Format, spec.Transcript)
				}
				if spec.Prefill != wire.PrefillFence || spec.Terminal != wire.TerminalSubmit {
					t.Fatalf("prefill/terminal = %s/%s", spec.Prefill, spec.Terminal)
				}
				if !spec.Loop.AllowRepeatedCalls {
					t.Fatal("upstream primitive must allow repeated calls")
				}
			},
		},
		{
			name: "primitive go-native",
			options: Options{
				MaxSteps:   8,
				Protocol:   G1FunctionProtocol{},
				Renderer:   G1FunctionRenderer{},
				Generation: legacyGeneration(),
			},
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Transcript != wire.TranscriptBenchmark || spec.Terminal != wire.TerminalNone {
					t.Fatalf("transcript/terminal = %s/%s", spec.Transcript, spec.Terminal)
				}
				if spec.Loop.AllowRepeatedCalls {
					t.Fatal("go-native must reject repeated calls")
				}
			},
		},
		{
			name: "xml thinking plus router has no envelope prefill",
			options: func() Options {
				// The chat renderer refuses to inject a prefix while a think
				// block owns the opening, so the effective prefill is none.
				// Deriving it this way keeps the documented XML + thinking
				// combination valid instead of reporting a conflict.
				options := legacyXMLOptions(inference.ThinkingFast, false)
				options.Router = G1RouteProtocol{}
				options.RouteRenderer = RWKVChatRenderer{}
				options.RouteRetries = 1
				return options
			}(),
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Thinking != wire.ThinkingFast || spec.Prefill != wire.PrefillNone {
					t.Fatalf("thinking/prefill = %s/%s, want fast/none", spec.Thinking, spec.Prefill)
				}
				if spec.Route != wire.RouteRespondInspect {
					t.Fatalf("route = %s", spec.Route)
				}
			},
		},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			spec, err := WireSpecOf(testCase.options)
			if err != nil {
				t.Fatalf("WireSpecOf: %v", err)
			}
			testCase.check(t, spec)

			// Round trip: apply the spec and derive it back. This is what the
			// CLI/eval wiring will rely on, so drift here is a hard failure.
			applied, err := OptionsWithWire(
				Options{Generation: testCase.options.Generation},
				spec,
			)
			if err != nil {
				t.Fatalf("OptionsWithWire: %v", err)
			}
			applied.Wire = nil
			derived, err := WireSpecOf(applied)
			if err != nil {
				t.Fatalf("re-derive: %v", err)
			}
			if !derived.Equal(spec) {
				t.Fatalf("round trip drifted:\nwant %s\n got %s", spec.Canonical(), derived.Canonical())
			}
		})
	}
}

func TestWireSpecOfNativeTransport(t *testing.T) {
	t.Parallel()
	native, _, err := wire.Resolve("native-v1")
	if err != nil {
		t.Fatal(err)
	}
	options, err := OptionsWithWire(legacyXMLOptions(inference.ThinkingOff, false), native)
	if err != nil {
		t.Fatal(err)
	}
	spec, err := WireSpecOf(options)
	if err != nil {
		t.Fatal(err)
	}
	if spec.Transport != wire.TransportNative || spec.Prefill != wire.PrefillNone {
		t.Fatalf("transport/prefill = %s/%s", spec.Transport, spec.Prefill)
	}
}

func TestWireSpecOfSurfacesSilentConflicts(t *testing.T) {
	t.Parallel()
	cases := []struct {
		name    string
		options Options
		code    string
		check   func(*testing.T, wire.Spec)
	}{
		{
			name:    "deep anchor without an abstention exit",
			options: legacyProductOptions(false, true, false, false),
			code:    "prefill.requires-abstain",
			check: func(t *testing.T, spec wire.Spec) {
				t.Helper()
				if spec.Prefill != wire.PrefillDeepFence || spec.Abstain != wire.AbstainNone {
					t.Fatalf("prefill/abstain = %s/%s", spec.Prefill, spec.Abstain)
				}
			},
		},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			spec, err := WireSpecOf(testCase.options)
			if err == nil {
				t.Fatalf("WireSpecOf succeeded, want %s", testCase.code)
			}
			specErr, ok := err.(*wire.SpecError)
			if !ok {
				t.Fatalf("error type %T: %v", err, err)
			}
			if specErr.Code != testCase.code {
				t.Fatalf("code = %q, want %q: %v", specErr.Code, testCase.code, err)
			}
			// The spec is still returned so a manifest can record the invalid
			// legacy combination instead of losing it.
			testCase.check(t, spec)
		})
	}
}

func TestOptionsWithWireAppliesPreset(t *testing.T) {
	t.Parallel()
	spec, _, err := wire.Resolve("md-v1")
	if err != nil {
		t.Fatal(err)
	}
	spec.Loop = wire.Loop{
		MaxSteps:                 6,
		ProtocolRetries:          1,
		DecisionMaxOutputTokens:  96,
		AnswerMaxOutputTokens:    1024,
		RouteMaxOutputTokens:     48,
		DuplicateReplayLimit:     2,
		DuplicateRescueThreshold: 3,
		SameToolRescueLimit:      3,
	}
	options, err := OptionsWithWire(Options{Generation: legacyGeneration()}, spec)
	if err != nil {
		t.Fatal(err)
	}
	protocol, ok := options.Protocol.(G1FunctionProtocol)
	if !ok {
		t.Fatalf("protocol type %T", options.Protocol)
	}
	if !protocol.Product || !protocol.SemanticNoTool || !protocol.DeepToolAnchor {
		t.Fatalf("protocol = %+v", protocol)
	}
	renderer, ok := options.Renderer.(G1FunctionRenderer)
	if !ok || !renderer.Product {
		t.Fatalf("renderer = %#v", options.Renderer)
	}
	if options.MaxSteps != 6 || options.DecisionMaxOutputTokens != 96 ||
		options.DuplicateReplayLimit != 2 || options.SameToolRescueLimit != 3 {
		t.Fatalf("loop not applied: %+v", options)
	}
	if options.Wire == nil || !options.Wire.Equal(spec) {
		t.Fatal("Options.Wire must carry the applied spec")
	}
}

// TestNewRunnerRejectsInvalidWireSpec locks the P2 contract: a legacy option
// combination the canonical spec rejects fails at construction instead of
// silently changing what the model sees.
func TestNewRunnerRejectsInvalidWireSpec(t *testing.T) {
	t.Parallel()
	generator := continuation.GenerateFunc(func(
		context.Context,
		continuation.Request,
		continuation.EventSink,
	) (continuation.Result, error) {
		return continuation.Result{}, nil
	})
	_, err := NewRunner(generator, []Tool{echoTool{}}, Options{
		MaxSteps: 3,
		// A deep anchor removes every syntactic abstention exit; without
		// no_tool the model has no legal way to stop calling tools.
		Protocol: G1FunctionProtocol{Product: true, DeepToolAnchor: true},
		Renderer: G1FunctionRenderer{Product: true},
	})
	if err == nil || !strings.Contains(err.Error(), "prefill.requires-abstain") {
		t.Fatalf("NewRunner error = %v, want prefill.requires-abstain", err)
	}
	// The valid pairing still constructs.
	if _, err := NewRunner(generator, []Tool{echoTool{}}, legacyProductOptions(true, true, false, false)); err != nil {
		t.Fatalf("valid product profile rejected: %v", err)
	}
}
