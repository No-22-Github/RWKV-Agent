package contracttest

import (
	"bytes"
	"context"
	"errors"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
)

type Suite struct {
	NewModel func(*testing.T) inference.Model
	Request  inference.GenerateRequest
}

func Run(t *testing.T, suite Suite) {
	t.Helper()
	if suite.NewModel == nil {
		t.Fatal("contract suite requires NewModel")
	}

	model := suite.NewModel(t)
	t.Cleanup(func() {
		if err := model.Close(); err != nil {
			t.Errorf("Model.Close: %v", err)
		}
	})

	t.Run("Metadata", func(t *testing.T) {
		info := model.Info()
		if info.ID == "" {
			t.Error("Model.Info ID is empty")
		}
		if info.Backend == "" {
			t.Error("Model.Info Backend is empty")
		}
		if !model.Capabilities().TextGeneration.Available {
			t.Error("TextGeneration capability is unavailable")
		}
	})

	t.Run("StreamMatchesResult", func(t *testing.T) {
		session := newSession(t, model)
		defer session.Close()

		var streamed strings.Builder
		result, err := session.Generate(context.Background(), suite.Request, func(event inference.GenerationEvent) error {
			if event.Kind == inference.EventOutputDelta {
				if event.Delta == nil {
					t.Fatal("output delta event has no delta")
				}
				streamed.WriteString(event.Delta.Text)
			}
			return nil
		})
		if err != nil {
			t.Fatalf("Generate: %v", err)
		}
		if result.Output == "" {
			t.Fatal("Generate returned empty output")
		}
		if got := streamed.String(); got != result.Output {
			t.Fatalf("streamed output = %q, result output = %q", got, result.Output)
		}
		if !result.Committed {
			t.Fatal("successful generation was not committed")
		}
		if result.StateRevision == "" {
			t.Fatal("successful generation has no StateRevision")
		}
		if got := session.Stats().Generations; got != 1 {
			t.Fatalf("Generations = %d, want 1", got)
		}
	})

	t.Run("CountResetClose", func(t *testing.T) {
		session := newSession(t, model)
		count, err := session.CountTokens(context.Background(), inference.TokenCountRequest{
			Messages: suite.Request.Messages,
			Raw:      suite.Request.Raw,
			Prompt:   suite.Request.Prompt,
		})
		if err != nil {
			t.Fatalf("CountTokens: %v", err)
		}
		if count <= 0 {
			t.Fatalf("CountTokens = %d, want positive", count)
		}
		if err := session.Reset(context.Background()); err != nil {
			t.Fatalf("Reset: %v", err)
		}
		if err := session.Close(); err != nil {
			t.Fatalf("Close: %v", err)
		}
		if err := session.Close(); err != nil {
			t.Fatalf("second Close: %v", err)
		}
		_, err = session.Generate(context.Background(), suite.Request, func(inference.GenerationEvent) error {
			return nil
		})
		if !errors.Is(err, inference.ErrClosed) {
			t.Fatalf("Generate after Close error = %v, want ErrClosed", err)
		}
	})

	t.Run("CancelledContext", func(t *testing.T) {
		session := newSession(t, model)
		defer session.Close()

		ctx, cancel := context.WithCancel(context.Background())
		cancel()
		result, err := session.Generate(ctx, suite.Request, func(inference.GenerationEvent) error {
			return nil
		})
		if !errors.Is(err, context.Canceled) {
			t.Fatalf("Generate error = %v, want context.Canceled", err)
		}
		if result.FinishReason != inference.FinishCancelled {
			t.Fatalf("FinishReason = %q, want %q", result.FinishReason, inference.FinishCancelled)
		}
	})

	t.Run("SinkError", func(t *testing.T) {
		session := newSession(t, model)
		defer session.Close()

		errSink := errors.New("sink failed")
		result, err := session.Generate(context.Background(), suite.Request, func(event inference.GenerationEvent) error {
			if event.Kind == inference.EventOutputDelta {
				return errSink
			}
			return nil
		})
		if !errors.Is(err, errSink) {
			t.Fatalf("Generate error = %v, want sink error", err)
		}
		if result.FinishReason != inference.FinishCancelled {
			t.Fatalf("FinishReason = %q, want %q", result.FinishReason, inference.FinishCancelled)
		}
	})

	t.Run("UnsupportedStateOperations", func(t *testing.T) {
		capabilities := model.Capabilities()
		if capabilities.StateExport.Available ||
			capabilities.StateImport.Available ||
			capabilities.StateFork.Available {
			t.Skip("backend advertises native State operations")
		}
		session := newSession(t, model)
		defer session.Close()

		if _, err := session.ExportState(
			context.Background(),
			&bytes.Buffer{},
			inference.ExportStateOptions{},
		); !errors.Is(err, inference.ErrUnsupported) {
			t.Fatalf("ExportState error = %v, want ErrUnsupported", err)
		}
		if _, err := session.ImportState(
			context.Background(),
			bytes.NewReader(nil),
			inference.ImportStateOptions{},
		); !errors.Is(err, inference.ErrUnsupported) {
			t.Fatalf("ImportState error = %v, want ErrUnsupported", err)
		}
		if _, err := session.Fork(context.Background()); !errors.Is(err, inference.ErrUnsupported) {
			t.Fatalf("Fork error = %v, want ErrUnsupported", err)
		}
	})
}

func newSession(t *testing.T, model inference.Model) inference.Session {
	t.Helper()
	session, err := model.NewSession(context.Background(), inference.SessionOptions{})
	if err != nil {
		t.Fatalf("NewSession: %v", err)
	}
	return session
}
