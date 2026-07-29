package agent

import (
	"context"
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
