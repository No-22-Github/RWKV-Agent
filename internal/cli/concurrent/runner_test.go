package concurrent

import (
	"bytes"
	"context"
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
)

func TestRunnerUsesIdenticalPromptWithoutSessionLabels(t *testing.T) {
	t.Parallel()

	model := loadMockModel(t, mock.Config{ChunkSize: 1})
	runner := newTestRunner(t, model, "same prompt", 4)
	summary, err := runner.Run(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if summary.Sessions != 4 {
		t.Fatalf("sessions = %d, want 4", summary.Sessions)
	}
	snapshot := runner.Snapshot()
	first := snapshot.Sessions[0].Output
	for _, session := range snapshot.Sessions {
		if session.Phase != PhaseDone {
			t.Fatalf("session %d phase = %q", session.Index, session.Phase)
		}
		if session.Output != first {
			t.Fatalf("session %d received a different prompt", session.Index)
		}
		if strings.Contains(session.Output, "["+string(rune('0'+session.Index))+"]") {
			t.Fatalf("session label leaked into prompt: %q", session.Output)
		}
		if !strings.Contains(session.Output, "same prompt") {
			t.Fatalf("prompt missing from output: %q", session.Output)
		}
	}
}

func TestRunnerCancellationMarksEverySessionAndRollsBack(t *testing.T) {
	t.Parallel()

	started := make(chan struct{}, 4)
	model := loadMockModel(t, mock.Config{
		Output:   "never committed",
		Started:  started,
		Continue: make(chan struct{}),
	})
	runner := newTestRunner(t, model, "cancel me", 4)
	ctx, cancel := context.WithCancel(context.Background())
	result := make(chan error, 1)
	go func() {
		_, err := runner.Run(ctx)
		result <- err
	}()
	select {
	case <-started:
	case <-time.After(2 * time.Second):
		t.Fatal("generation did not start")
	}
	cancel()
	select {
	case err := <-result:
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("Run error = %v, want context.Canceled", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("cancelled run did not stop")
	}
	for _, session := range runner.Snapshot().Sessions {
		if session.Phase != PhaseCancelled {
			t.Fatalf("session %d phase = %q, want cancelled", session.Index, session.Phase)
		}
	}
}

func TestRunnerSnapshotAndSlowConsumerNeverLoseOutput(t *testing.T) {
	t.Parallel()

	const output = "你好🙂 RWKV\n" + "token-stream-"
	model := loadMockModel(t, mock.Config{Output: output, ChunkSize: 1})
	runner := newTestRunner(t, model, "stream", 4)
	done := make(chan error, 1)
	go func() {
		_, err := runner.Run(context.Background())
		done <- err
	}()
	for {
		select {
		case err := <-done:
			if err != nil {
				t.Fatal(err)
			}
			for _, session := range runner.Snapshot().Sessions {
				if session.Output != output {
					t.Fatalf("session %d output = %q, want %q", session.Index, session.Output, output)
				}
			}
			return
		case <-time.After(5 * time.Millisecond):
			_ = runner.Snapshot()
			time.Sleep(10 * time.Millisecond)
		}
	}
}

func TestPlainRendererStripsTerminalControlSequences(t *testing.T) {
	t.Parallel()

	model := loadMockModel(t, mock.Config{Output: "safe\033[2J\rtext", ChunkSize: 2})
	runner := newTestRunner(t, model, "plain", 1)
	var output bytes.Buffer
	var status bytes.Buffer
	_, err := (PlainRenderer{Out: &output, Status: &status}).Run(context.Background(), runner)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(output.String(), "\033") || strings.Contains(output.String(), "\r") {
		t.Fatalf("plain output contains terminal controls: %q", output.String())
	}
	if got := status.String(); !strings.Contains(got, "Concurrent batch complete: sessions=1") {
		t.Fatalf("stable summary missing: %q", got)
	}
}

func TestRunnerSupportsEightSessions(t *testing.T) {
	t.Parallel()

	model := loadMockModel(t, mock.Config{Output: "ok", ChunkSize: 1})
	runner := newTestRunner(t, model, "eight", 8)
	t.Cleanup(func() { _ = runner.Close() })
	summary, err := runner.Run(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if summary.Sessions != 8 || len(runner.Snapshot().Sessions) != 8 {
		t.Fatalf("summary = %+v", summary)
	}
}

func TestFollowUpKeepsSelectedConversationAndCancelledTurnRollsBack(t *testing.T) {
	t.Parallel()

	continueGeneration := make(chan struct{}, 1)
	continueGeneration <- struct{}{}
	model := loadMockModel(t, mock.Config{
		ChunkSize: 1,
		Continue:  continueGeneration,
	})
	runner := newTestRunner(t, model, "initial question", 1)
	t.Cleanup(func() { _ = runner.Close() })
	if _, err := runner.Run(context.Background()); err != nil {
		t.Fatal(err)
	}

	ctx, cancel := context.WithCancel(context.Background())
	cancelled := make(chan error, 1)
	go func() {
		_, err := runner.FollowUp(ctx, 1, "cancelled question")
		cancelled <- err
	}()
	time.Sleep(20 * time.Millisecond)
	cancel()
	select {
	case err := <-cancelled:
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("cancelled FollowUp error = %v", err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("cancelled FollowUp did not stop")
	}

	continueGeneration <- struct{}{}
	result, err := runner.FollowUp(context.Background(), 1, "committed question")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(result.Output, "initial question") ||
		!strings.Contains(result.Output, "committed question") {
		t.Fatalf("follow-up did not retain selected conversation: %q", result.Output)
	}
	if strings.Contains(result.Output, "cancelled question") {
		t.Fatalf("cancelled turn was committed: %q", result.Output)
	}
	snapshot := runner.Snapshot()
	if snapshot.Phase != RunCompleted || !snapshot.Done ||
		snapshot.Sessions[0].Phase != PhaseDone {
		t.Fatalf("snapshot = %+v", snapshot)
	}
}

func newTestRunner(t *testing.T, model inference.Model, prompt string, count int) *Runner {
	t.Helper()
	runner, err := NewRunner(model, Options{
		Conversation: conversation.Options{
			Profile:     inference.DefaultPromptProfile(false),
			NativeState: "off",
		},
		Turn: conversation.TurnOptions{
			Sampling: inference.SamplingOptions{
				Temperature: 1,
				TopK:        1,
				TopP:        1,
			},
			Limits: inference.GenerationLimits{MaxOutputTokens: 128},
		},
		Prompt:      prompt,
		Concurrency: count,
		BaseSeed:    42,
	})
	if err != nil {
		t.Fatal(err)
	}
	return runner
}

func loadMockModel(t *testing.T, config mock.Config) inference.Model {
	t.Helper()
	model, err := mock.New(config).LoadModel(
		context.Background(),
		inference.LoadRequest{Source: inference.ModelSource{Path: "concurrent.mock"}},
		nil,
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = model.Close() })
	return model
}
