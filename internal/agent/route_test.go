package agent

import (
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestG1IRouteProtocolParsesOnlyKnownRoutes(t *testing.T) {
	t.Parallel()

	protocol := G1IRouteProtocol{}
	for input, want := range map[string]Route{
		"<route>respond</route>": RouteRespond,
		"<route>inspect</route>": RouteInspect,
	} {
		got, err := protocol.Parse(input, continuation.FinishUnknown)
		if err != nil || got != want {
			t.Fatalf("Parse(%q) = %q, %v", input, got, err)
		}
	}
	if got, err := protocol.Parse("<route>respond", continuation.FinishStop); err != nil ||
		got != RouteRespond {
		t.Fatalf("stopped route = %q, %v", got, err)
	}
	for _, input := range []string{
		"respond",
		"<route>tool</route>",
		"<route>respond</route> trailing",
	} {
		if _, err := protocol.Parse(input, continuation.FinishUnknown); err == nil {
			t.Fatalf("invalid route accepted: %q", input)
		}
	}
	if _, err := protocol.Parse(
		"<route>inspect",
		continuation.FinishLength,
	); err == nil {
		t.Fatal("length-truncated route accepted")
	}
}

func TestProgressiveToolRouteSelectsAtMostTwoKnownBundles(t *testing.T) {
	t.Parallel()
	protocol := G1IProgressiveToolRouteProtocol{}
	bundles := DefaultToolBundles()
	decision, err := protocol.Parse(
		"<route>inspect:workspace+compute</route>",
		continuation.FinishStop,
		bundles,
	)
	if err != nil || decision.Route != RouteInspect ||
		len(decision.Bundles) != 2 || decision.Bundles[0] != ToolBundleWorkspace {
		t.Fatalf("decision = %+v, %v", decision, err)
	}
	for _, value := range []string{
		"<route>inspect:unknown</route>",
		"<route>inspect:workspace+compute+web</route>",
		"<route>inspect:web+web</route>",
	} {
		if _, err := protocol.Parse(value, continuation.FinishStop, bundles); err == nil {
			t.Fatalf("accepted progressive route %q", value)
		}
	}
}

func TestProgressiveToolRouteInstructionsUseConcreteRoutes(t *testing.T) {
	t.Parallel()
	protocol := G1IProgressiveToolRouteProtocol{}
	bundles := DefaultToolBundles()[:2]
	for name, value := range map[string]string{
		"instructions": protocol.Instructions(bundles),
		"correction":   protocol.Correction(errors.New("invalid"), bundles),
	} {
		if strings.Contains(value, "BUNDLE") || strings.Contains(value, "NAME") {
			t.Fatalf("%s contains a placeholder: %q", name, value)
		}
		for _, expected := range []string{"<route>respond</route>", "<route>inspect:workspace</route>", "<route>inspect:compute</route>"} {
			if !strings.Contains(value, expected) {
				t.Fatalf("%s omits %q: %q", name, expected, value)
			}
		}
	}
}

func TestG1IRouteProtocolClassifiesRunawayReasoning(t *testing.T) {
	t.Parallel()

	protocol := G1IRouteProtocol{}
	runaway := "<think>the user is asking about files, but wait, let me reconsider"
	for _, testCase := range []struct {
		name   string
		value  string
		finish continuation.FinishReason
		want   error
	}{
		{
			name:   "unclosed think without a finish reason",
			value:  runaway,
			finish: continuation.FinishUnknown,
			want:   ErrUnclosedThink,
		},
		{
			name:   "unclosed think reported as length",
			value:  runaway,
			finish: continuation.FinishLength,
			want:   ErrUnclosedThink,
		},
		{
			name:   "envelope truncated by the route budget",
			value:  "respond",
			finish: continuation.FinishLength,
			want:   ErrRouteTokenLimit,
		},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			_, err := protocol.Parse(testCase.value, testCase.finish)
			if !errors.Is(err, testCase.want) {
				t.Fatalf("error = %v, want %v", err, testCase.want)
			}
			if !errors.Is(err, ErrProtocol) {
				t.Fatalf("error %v does not wrap ErrProtocol", err)
			}
		})
	}
	unclosed := protocol.Correction(ErrUnclosedThink)
	if !strings.Contains(unclosed, "</think>") {
		t.Fatalf("unclosed think correction omits the closing tag: %q", unclosed)
	}
	for _, correction := range []string{
		unclosed,
		protocol.Correction(ErrRouteTokenLimit),
		protocol.Correction(errors.New("other")),
	} {
		if !strings.Contains(correction, "<route>respond</route>") {
			t.Fatalf("route correction omits the contract: %q", correction)
		}
	}
}

func TestRoutingHistoryExcludesToolPayloadsAndBoundsTurns(t *testing.T) {
	t.Parallel()

	history := []Message{
		{Role: RoleUser, Content: "old question"},
		{Role: RoleAssistant, Content: "old answer"},
		{Role: RoleAssistant, Content: `<tool_call>{"name":"read_file","arguments":{}}</tool_call>`},
		{Role: RoleTool, Content: "untrusted tool payload"},
	}
	for index := 0; index < 10; index++ {
		history = append(
			history,
			Message{Role: RoleUser, Content: "question"},
			Message{Role: RoleAssistant, Content: "answer"},
		)
	}
	filtered := routingHistory(history)
	if len(filtered) != maxRoutingHistoryMessages {
		t.Fatalf("routing history length = %d", len(filtered))
	}
	for _, message := range filtered {
		if message.Role == RoleTool ||
			strings.Contains(message.Content, "tool_call") ||
			strings.Contains(message.Content, "untrusted") {
			t.Fatalf("routing history leaked a tool trace: %+v", filtered)
		}
	}
}

func TestInvalidRouteFallsBackToRespondWithoutTools(t *testing.T) {
	t.Parallel()

	outputs := []continuation.Result{
		{Text: "maybe", FinishReason: continuation.FinishStop},
		{Text: "still-maybe", FinishReason: continuation.FinishStop},
		{Text: "I cannot inspect files on this route.", FinishReason: continuation.FinishStop},
	}
	calls := 0
	runner, err := NewRunner(
		continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			result := outputs[calls]
			calls++
			return result, nil
		}),
		[]Tool{echoTool{}},
		Options{
			Router:       G1IRouteProtocol{},
			RouteRetries: 1,
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "ambiguous request")
	if err != nil {
		t.Fatal(err)
	}
	if result.Route != RouteRespond ||
		result.Output != "I cannot inspect files on this route." ||
		calls != 3 {
		t.Fatalf("fallback result=%+v calls=%d", result, calls)
	}
}
