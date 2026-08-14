package api

import (
	"context"
	"io"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestServiceSpawnAgentsUsesConcurrentChildSessions(t *testing.T) {
	t.Parallel()
	service, err := NewService(Options{Workspace: t.TempDir()})
	if err != nil {
		t.Fatal(err)
	}
	progressive := true
	source := &subagentTestSource{}
	service.source = source
	service.status = Status{State: ModelReady, Provider: ProviderRWKVLightning, Model: "scripted"}
	service.config = Config{
		Provider:               ProviderRWKVLightning,
		Model:                  "scripted",
		MaxSteps:               4,
		MaxTokens:              256,
		Temperature:            1,
		TopK:                   1,
		TopP:                   1,
		PenaltyDecay:           1,
		ProgressiveTools:       &progressive,
		EnableSubagents:        true,
		SubagentMaxParallel:    2,
		SubagentMaxSteps:       3,
		SubagentTimeoutSeconds: 5,
	}
	defer service.Close()

	session, err := service.NewSession(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	result, err := session.Run(context.Background(), "Compare two independent checks.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "combined" || len(result.Steps) != 2 || result.Steps[0].Tool != "spawn_agents" {
		t.Fatalf("result = %+v", result)
	}
	toolResult := result.Steps[0].ToolResult
	if !strings.Contains(toolResult, "child-2") || !strings.Contains(toolResult, "child-3") {
		t.Fatalf("spawn_agents result = %s", toolResult)
	}
	if source.maximum.Load() < 2 {
		t.Fatalf("maximum child concurrency = %d", source.maximum.Load())
	}
}

type subagentTestSource struct {
	created atomic.Int32
	active  atomic.Int32
	maximum atomic.Int32
	ready   atomic.Int32
}

func (s *subagentTestSource) newGenerator(context.Context) (continuation.Generator, io.Closer, error) {
	id := int(s.created.Add(1))
	return &subagentTestGenerator{source: s, id: id}, io.NopCloser(strings.NewReader("")), nil
}

func (*subagentTestSource) status() Status { return Status{State: ModelReady, Model: "scripted"} }
func (*subagentTestSource) close() error   { return nil }

type subagentTestGenerator struct {
	source *subagentTestSource
	id     int
	mu     sync.Mutex
	calls  int
}

func (g *subagentTestGenerator) Continue(
	ctx context.Context,
	_ continuation.Request,
	_ continuation.EventSink,
) (continuation.Result, error) {
	g.mu.Lock()
	g.calls++
	call := g.calls
	g.mu.Unlock()
	if g.id == 1 {
		outputs := []string{
			`inspect:delegate</route>`,
			`<tool_call>{"name":"spawn_agents","arguments":{"tasks":["official check","independent check"]}}</tool_call>`,
			`{"name":"submit","arguments":{"answer":"combined"}}`,
		}
		return continuation.Result{Text: outputs[call-1], FinishReason: continuation.FinishStop}, nil
	}
	if call == 1 {
		current := g.source.active.Add(1)
		defer g.source.active.Add(-1)
		for {
			maximum := g.source.maximum.Load()
			if current <= maximum || g.source.maximum.CompareAndSwap(maximum, current) {
				break
			}
		}
		g.source.ready.Add(1)
		deadline := time.NewTimer(time.Second)
		defer deadline.Stop()
		for g.source.ready.Load() < 2 {
			select {
			case <-ctx.Done():
				return continuation.Result{}, ctx.Err()
			case <-deadline.C:
				return continuation.Result{}, context.DeadlineExceeded
			default:
				time.Sleep(time.Millisecond)
			}
		}
		return continuation.Result{Text: `respond</route>`, FinishReason: continuation.FinishStop}, nil
	}
	return continuation.Result{
		Text:         "child-" + string(rune('0'+g.id)),
		FinishReason: continuation.FinishStop,
	}, nil
}
