package mock_test

import (
	"context"
	"errors"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
	"github.com/no22/RWKV-Agent/internal/inference/contracttest"
)

func TestContract(t *testing.T) {
	t.Parallel()

	backend := mock.New(mock.Config{Output: "你好，RWKV。", ChunkSize: 2})
	contracttest.Run(t, contracttest.Suite{
		NewModel: func(t *testing.T) inference.Model {
			t.Helper()
			model, err := backend.LoadModel(
				context.Background(),
				inference.LoadRequest{Source: inference.ModelSource{Path: "contract.mock"}},
				nil,
			)
			if err != nil {
				t.Fatalf("LoadModel: %v", err)
			}
			return model
		},
		Request: testRequest(),
	})
}

func TestSessionRejectsConcurrentGeneration(t *testing.T) {
	t.Parallel()

	started := make(chan struct{}, 1)
	continueGeneration := make(chan struct{})
	backend := mock.New(mock.Config{
		Output:   "done",
		Started:  started,
		Continue: continueGeneration,
	})
	model, err := backend.LoadModel(
		context.Background(),
		inference.LoadRequest{Source: inference.ModelSource{Path: "busy.mock"}},
		nil,
	)
	if err != nil {
		t.Fatalf("LoadModel: %v", err)
	}
	defer model.Close()
	session, err := model.NewSession(context.Background(), inference.SessionOptions{})
	if err != nil {
		t.Fatalf("NewSession: %v", err)
	}
	defer session.Close()

	firstDone := make(chan error, 1)
	go func() {
		_, generateErr := session.Generate(context.Background(), testRequest(), func(inference.GenerationEvent) error {
			return nil
		})
		firstDone <- generateErr
	}()
	<-started

	_, err = session.Generate(context.Background(), testRequest(), func(inference.GenerationEvent) error {
		return nil
	})
	if !errors.Is(err, inference.ErrBusy) {
		t.Fatalf("concurrent Generate error = %v, want ErrBusy", err)
	}
	close(continueGeneration)
	if err := <-firstDone; err != nil {
		t.Fatalf("first Generate: %v", err)
	}
}

func TestSessionHonorsCancelledContext(t *testing.T) {
	t.Parallel()

	backend := mock.New(mock.Config{Output: "unused"})
	model, err := backend.LoadModel(
		context.Background(),
		inference.LoadRequest{Source: inference.ModelSource{Path: "cancel.mock"}},
		nil,
	)
	if err != nil {
		t.Fatalf("LoadModel: %v", err)
	}
	defer model.Close()
	session, err := model.NewSession(context.Background(), inference.SessionOptions{})
	if err != nil {
		t.Fatalf("NewSession: %v", err)
	}
	defer session.Close()

	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	result, err := session.Generate(ctx, testRequest(), func(inference.GenerationEvent) error {
		return nil
	})
	if !errors.Is(err, context.Canceled) {
		t.Fatalf("Generate error = %v, want context.Canceled", err)
	}
	if result.FinishReason != inference.FinishCancelled {
		t.Fatalf("FinishReason = %q, want %q", result.FinishReason, inference.FinishCancelled)
	}
}

func TestModelCloseCancelsGeneration(t *testing.T) {
	t.Parallel()

	started := make(chan struct{}, 1)
	backend := mock.New(mock.Config{
		Output:   "unused",
		Started:  started,
		Continue: make(chan struct{}),
	})
	model, err := backend.LoadModel(
		context.Background(),
		inference.LoadRequest{Source: inference.ModelSource{Path: "close.mock"}},
		nil,
	)
	if err != nil {
		t.Fatalf("LoadModel: %v", err)
	}
	session, err := model.NewSession(context.Background(), inference.SessionOptions{})
	if err != nil {
		t.Fatalf("NewSession: %v", err)
	}

	generateDone := make(chan error, 1)
	go func() {
		_, generateErr := session.Generate(context.Background(), testRequest(), func(inference.GenerationEvent) error {
			return nil
		})
		generateDone <- generateErr
	}()
	<-started

	if err := model.Close(); err != nil {
		t.Fatalf("Model.Close: %v", err)
	}
	if err := <-generateDone; !errors.Is(err, context.Canceled) {
		t.Fatalf("Generate error = %v, want context.Canceled", err)
	}
	if err := model.Close(); err != nil {
		t.Fatalf("second Model.Close: %v", err)
	}
}

func testRequest() inference.GenerateRequest {
	return inference.GenerateRequest{
		Messages: []inference.Message{inference.TextMessage(inference.RoleUser, "hello")},
		Sampling: inference.SamplingOptions{
			Temperature: 1,
			TopK:        1,
			TopP:        1,
		},
		Limits: inference.GenerationLimits{MaxOutputTokens: 8},
		Commit: inference.CommitOnSuccess,
	}
}
