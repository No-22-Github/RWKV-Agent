package eval

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// checkpointCases answer "ok" on even indexes and fail on odd ones, so the
// merged summary mixes passes and failures.
func checkpointCases() []Case {
	answer := "ok"
	cases := make([]Case, 6)
	for index := range cases {
		cases[index] = Case{
			ID:          fmt.Sprintf("resume-%d", index),
			Description: "resume case",
			Turns: []Turn{{
				Prompt: fmt.Sprintf("answer case %d", index),
				Expect: Expectation{Route: agent.RouteInspect, Tools: []string{}, OutputEquals: &answer},
			}},
		}
	}
	return cases
}

type fakeBackend struct {
	mu    sync.Mutex
	calls map[string]int
	// before runs ahead of each generation; a non-nil error replaces it.
	before func(ctx context.Context, caseID string) error
}

func (b *fakeBackend) factory(caseContext context.Context) (continuation.Generator, io.Closer, error) {
	caseID, _ := CaseIDFromContext(caseContext)
	return continuation.GenerateFunc(func(ctx context.Context, _ continuation.Request, _ continuation.EventSink) (continuation.Result, error) {
		b.mu.Lock()
		if b.calls == nil {
			b.calls = map[string]int{}
		}
		b.calls[caseID]++
		b.mu.Unlock()
		if b.before != nil {
			if err := b.before(ctx, caseID); err != nil {
				return continuation.Result{}, err
			}
		}
		text := "ok"
		var index int
		fmt.Sscanf(caseID, "resume-%d", &index)
		if index%2 == 1 {
			text = "wrong"
		}
		return continuation.Result{Text: text, FinishReason: continuation.FinishStop}, nil
	}), nil, nil
}

func (b *fakeBackend) called(caseID string) int {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.calls[caseID]
}

func checkpointConfig(t *testing.T, backend *fakeBackend) Config {
	return Config{
		Cases:           checkpointCases(),
		Suite:           "custom",
		CaseParallelism: 1,
		Runner: agent.Options{
			MaxSteps:   2,
			Generation: continuation.Request{MaxOutputTokens: 32},
		},
		GeneratorFactory: backend.factory,
		TempDir:          t.TempDir(),
		AdapterID:        "miss-v2",
	}
}

// volatileKeys are wall-clock and run-identity fields that legitimately
// differ between two executions of the same cases.
var volatileKeys = map[string]bool{
	"run_id": true, "timestamp": true, "started_at_ms": true, "ended_at_ms": true,
	"wall_ms": true, "model_ms": true, "tool_ms": true, "wait_ms": true,
	"wall_time_millis": true, "latency_ms": true, "duration_ms": true,
}

func normalizedJSON(t *testing.T, value any) any {
	t.Helper()
	data, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	var decoded any
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatal(err)
	}
	var strip func(any) any
	strip = func(node any) any {
		switch typed := node.(type) {
		case map[string]any:
			for key, child := range typed {
				if volatileKeys[key] || strings.HasSuffix(key, "_ms") || strings.HasSuffix(key, "_millis") {
					delete(typed, key)
					continue
				}
				typed[key] = strip(child)
			}
		case []any:
			for index, child := range typed {
				typed[index] = strip(child)
			}
		}
		return node
	}
	return strip(decoded)
}

func TestCheckpointResumeMatchesUninterruptedRun(t *testing.T) {
	t.Parallel()
	output := filepath.Join(t.TempDir(), "run")

	// Attempt 1: resume-1 hits an upstream break (invalid), and the run is
	// cancelled while resume-3 is generating.
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	first := &fakeBackend{before: func(ctx context.Context, caseID string) error {
		switch caseID {
		case "resume-1":
			return fmt.Errorf("%w: 502 bad gateway", continuation.ErrUpstream)
		case "resume-3":
			cancel()
			<-ctx.Done()
			return ctx.Err()
		}
		return nil
	}}
	config := checkpointConfig(t, first)
	checkpoint, err := OpenCheckpoint(output, config, false, io.Discard)
	if err != nil {
		t.Fatal(err)
	}
	config.Checkpoint = checkpoint
	if _, err := Run(ctx, config); err == nil {
		t.Fatal("interrupted run returned nil error")
	}
	if err := checkpoint.Close(); err != nil {
		t.Fatal(err)
	}
	progress := checkpoint.Progress()
	if progress.Done != 3 || progress.Pass != 2 || progress.Invalid != 1 || progress.Total != 6 {
		t.Fatalf("progress after interruption = %+v", progress)
	}
	if first.called("resume-4") != 0 {
		t.Fatal("cases after the cancellation started")
	}

	// A plain rerun must not silently reuse or clobber the partial.
	if _, err := OpenCheckpoint(output, checkpointConfig(t, &fakeBackend{}), false, io.Discard); err == nil ||
		!strings.Contains(err.Error(), "--resume") {
		t.Fatalf("open without resume over a partial = %v", err)
	}

	// Attempt 2: resume with a healthy backend and a lower parallelism.
	second := &fakeBackend{}
	config = checkpointConfig(t, second)
	config.CaseParallelism = 3
	var log strings.Builder
	checkpoint, err = OpenCheckpoint(output, config, true, &log)
	if err != nil {
		t.Fatal(err)
	}
	config.Checkpoint = checkpoint
	resumed, err := Run(context.Background(), config)
	if err != nil {
		t.Fatal(err)
	}
	if err := checkpoint.Close(); err != nil {
		t.Fatal(err)
	}
	for _, id := range []string{"resume-0", "resume-2"} {
		if second.called(id) != 0 {
			t.Fatalf("finished case %s ran again", id)
		}
	}
	for _, id := range []string{"resume-1", "resume-3", "resume-4", "resume-5"} {
		if second.called(id) == 0 {
			t.Fatalf("case %s was not run on resume", id)
		}
	}
	if !strings.Contains(log.String(), "resume: 2/6 cases carried over") ||
		!strings.Contains(log.String(), "[6/6] ") {
		t.Fatalf("resume log = %q", log.String())
	}
	if resumed.Manifest.RunID != checkpoint.runID {
		t.Fatalf("resumed run id %q, checkpoint %q", resumed.Manifest.RunID, checkpoint.runID)
	}

	// Baseline: the same cases in one uninterrupted run.
	baselineConfig := checkpointConfig(t, &fakeBackend{})
	baselineConfig.CaseParallelism = 3
	baseline, err := Run(context.Background(), baselineConfig)
	if err != nil {
		t.Fatal(err)
	}
	if got, want := normalizedJSON(t, resumed.Summary), normalizedJSON(t, baseline.Summary); !reflect.DeepEqual(got, want) {
		gotJSON, _ := json.MarshalIndent(got, "", " ")
		wantJSON, _ := json.MarshalIndent(want, "", " ")
		t.Fatalf("resumed summary differs from baseline\nresumed: %s\nbaseline: %s", gotJSON, wantJSON)
	}
	if got, want := normalizedJSON(t, resumed.Trace), normalizedJSON(t, baseline.Trace); !reflect.DeepEqual(got, want) {
		t.Fatal("resumed trace differs from baseline")
	}
	if resumed.Summary.Metrics.TaskSuccess.Correct != 3 || resumed.Summary.Metrics.InvalidCases != 0 {
		t.Fatalf("resumed metrics = %+v", resumed.Summary.Metrics.TaskSuccess)
	}

	// The merged report still writes the unchanged artifact layout.
	paths, err := WriteArtifacts(output, resumed)
	if err != nil {
		t.Fatal(err)
	}
	for _, path := range []string{paths.Run, paths.Trace, paths.Summary} {
		if _, err := os.Stat(path); err != nil {
			t.Fatal(err)
		}
	}
	if err := checkpoint.Remove(); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(PartialDir(output)); !os.IsNotExist(err) {
		t.Fatalf("partial dir after Remove: %v", err)
	}
}

func TestCheckpointRefusesResumeWithDifferentConfiguration(t *testing.T) {
	t.Parallel()
	output := filepath.Join(t.TempDir(), "run")
	config := checkpointConfig(t, &fakeBackend{})
	checkpoint, err := OpenCheckpoint(output, config, false, io.Discard)
	if err != nil {
		t.Fatal(err)
	}
	if err := checkpoint.Close(); err != nil {
		t.Fatal(err)
	}

	changed := checkpointConfig(t, &fakeBackend{})
	changed.AdapterID = "miss-v1"
	changed.Runner.Generation.Sampling.Temperature = 0.7
	changed.Cases[2].Turns[0].Prompt = "edited prompt"
	_, err = OpenCheckpoint(output, changed, true, io.Discard)
	if err == nil {
		t.Fatal("resume with a different configuration was accepted")
	}
	for _, want := range []string{"resume refused", "harness.adapter_id", "sampling.temperature", "cases:"} {
		if !strings.Contains(err.Error(), want) {
			t.Fatalf("error %q does not name %q", err, want)
		}
	}
	if strings.Contains(err.Error(), "case_parallelism") {
		t.Fatalf("case parallelism must not be part of the signature: %v", err)
	}

	// Parallelism alone may change.
	same := checkpointConfig(t, &fakeBackend{})
	same.CaseParallelism = 4
	reopened, err := OpenCheckpoint(output, same, true, io.Discard)
	if err != nil {
		t.Fatalf("resume with only a parallelism change: %v", err)
	}
	_ = reopened.Close()
}

func TestCheckpointDropsTornFinalLine(t *testing.T) {
	t.Parallel()
	output := filepath.Join(t.TempDir(), "run")
	config := checkpointConfig(t, &fakeBackend{})
	checkpoint, err := OpenCheckpoint(output, config, false, io.Discard)
	if err != nil {
		t.Fatal(err)
	}
	checkpoint.record(0, CaseResult{ID: "resume-0", Passed: true}, nil, 0)
	if err := checkpoint.Close(); err != nil {
		t.Fatal(err)
	}
	casesPath := filepath.Join(PartialDir(output), checkpointCasesFile)
	file, err := os.OpenFile(casesPath, os.O_WRONLY|os.O_APPEND, 0o600)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := file.WriteString(`{"index":1,"case_id":"resume-1","sta`); err != nil {
		t.Fatal(err)
	}
	_ = file.Close()

	checkpoint, err = OpenCheckpoint(output, config, true, io.Discard)
	if err != nil {
		t.Fatal(err)
	}
	if _, ok := checkpoint.reusable("resume-0"); !ok {
		t.Fatal("whole record before the torn line was lost")
	}
	checkpoint.record(1, CaseResult{ID: "resume-1"}, nil, 0)
	_ = checkpoint.Close()
	records, _, err := readCaseCheckpoints(casesPath)
	if err != nil {
		t.Fatal(err)
	}
	if len(records) != 2 || records[1].CaseID != "resume-1" || records[1].Status != CaseStatusFail {
		t.Fatalf("records after repair = %+v", records)
	}
}

func TestEstimateETA(t *testing.T) {
	t.Parallel()
	if _, ok := estimateETA(etaMinSamples-1, 10, time.Minute); ok {
		t.Fatal("ETA shown before enough cases finished")
	}
	// 10 cases in 20 minutes, 30 left: 60 minutes.
	if eta, ok := estimateETA(10, 30, 20*time.Minute); !ok || eta != time.Hour {
		t.Fatalf("eta = %v, %v", eta, ok)
	}
	if eta, ok := estimateETA(0, 0, 0); !ok || eta != 0 {
		t.Fatalf("finished run eta = %v, %v", eta, ok)
	}
	for eta, want := range map[time.Duration]string{
		90 * time.Second:                "1m30s",
		41*time.Minute + 20*time.Second: "41m",
		72 * time.Minute:                "1h12m",
	} {
		if got := formatETA(eta); got != want {
			t.Fatalf("formatETA(%v) = %q, want %q", eta, got, want)
		}
	}
}

func TestCheckpointProgressReportsETA(t *testing.T) {
	t.Parallel()
	clock := time.Date(2026, 10, 15, 8, 0, 0, 0, time.UTC)
	var mu sync.Mutex
	config := checkpointConfig(t, &fakeBackend{})
	config.Now = func() time.Time {
		mu.Lock()
		defer mu.Unlock()
		return clock
	}
	var log strings.Builder
	checkpoint, err := OpenCheckpoint(filepath.Join(t.TempDir(), "run"), config, false, &log)
	if err != nil {
		t.Fatal(err)
	}
	defer checkpoint.Close()
	for index := range etaMinSamples {
		mu.Lock()
		clock = clock.Add(time.Minute)
		mu.Unlock()
		checkpoint.record(index, CaseResult{ID: fmt.Sprintf("resume-%d", index), Passed: true}, nil, time.Minute)
	}
	// 5 of 6 cases in 5 minutes: one minute left.
	progress := checkpoint.Progress()
	if progress.ETASeconds == nil || *progress.ETASeconds != 60 {
		t.Fatalf("eta_seconds = %v", progress.ETASeconds)
	}
	lines := strings.Split(strings.TrimSpace(log.String()), "\n")
	if lines[0] != "[1/6] resume-0 pass 1m0s eta ?" || lines[4] != "[5/6] resume-4 pass 1m0s eta 1m0s" {
		t.Fatalf("progress lines = %q", lines)
	}
}
