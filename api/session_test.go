package api

import (
	"context"
	"io"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestUnifiedSessionReadsREADMEAndReturnsFirstLine(t *testing.T) {
	t.Parallel()
	workspace := t.TempDir()
	const firstLine = "# RWKV Agent acceptance fixture"
	if err := os.WriteFile(filepath.Join(workspace, "README.md"), []byte(firstLine+"\nsecond line\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	service, err := NewService(Options{Workspace: workspace})
	if err != nil {
		t.Fatal(err)
	}
	service.config = Config{
		Provider: ProviderChatCompletions, Model: "scripted", MaxSteps: 4,
		MaxTokens: 256, Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1,
		Thinking: "off",
	}
	outputs := []string{
		`<tool_call>{"name":"read_file","arguments":{"path":"README.md"}}</tool_call>`,
		firstLine,
	}
	var mu sync.Mutex
	generator := continuation.GenerateFunc(func(
		_ context.Context,
		request continuation.Request,
		_ continuation.EventSink,
	) (continuation.Result, error) {
		mu.Lock()
		defer mu.Unlock()
		if len(outputs) == 0 {
			t.Fatalf("unexpected extra generation; prompt=%q", request.Prompt)
		}
		output := outputs[0]
		outputs = outputs[1:]
		return continuation.Result{Text: output, FinishReason: continuation.FinishStop}, nil
	})
	session, err := newSession(service, generator, io.NopCloser(strings.NewReader("")), workspace, Status{Model: "scripted"})
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	var events []Event
	result, err := session.RunWithObserver(context.Background(), "读取 README 并只输出第一行。", func(event Event) {
		events = append(events, event)
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != firstLine {
		t.Fatalf("output = %q", result.Output)
	}
	if len(result.Steps) != 2 || result.Steps[0].Tool != "read_file" || !result.Steps[0].ToolExecuted {
		t.Fatalf("steps = %+v", result.Steps)
	}
	if len(events) < 4 || events[1].Kind != EventToolStart {
		t.Fatalf("events = %+v", events)
	}
}
