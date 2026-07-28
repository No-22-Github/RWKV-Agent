package inference_test

import (
	"context"
	"errors"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
)

func TestCoreAutoSelectsAvailableBackend(t *testing.T) {
	t.Parallel()

	core, err := inference.NewCore(mock.New(mock.Config{Output: "ok"}))
	if err != nil {
		t.Fatalf("NewCore: %v", err)
	}
	defer core.Close()

	progressCalls := 0
	model, err := core.LoadModel(context.Background(), inference.LoadRequest{
		Source:  inference.ModelSource{Path: "model.mock"},
		Backend: inference.BackendAuto,
	}, func(inference.Progress) error {
		progressCalls++
		if _, err := core.Backends(context.Background()); err != nil {
			t.Fatalf("Backends from progress callback: %v", err)
		}
		return nil
	})
	if err != nil {
		t.Fatalf("LoadModel: %v", err)
	}
	if model.Info().Backend != mock.BackendID {
		t.Fatalf("backend = %q, want %q", model.Info().Backend, mock.BackendID)
	}
	if progressCalls == 0 {
		t.Fatal("LoadModel emitted no progress")
	}
}

func TestCoreRejectsDuplicateBackend(t *testing.T) {
	t.Parallel()

	_, err := inference.NewCore(mock.New(mock.Config{}), mock.New(mock.Config{}))
	if !errors.Is(err, inference.ErrInvalidArgument) {
		t.Fatalf("NewCore error = %v, want ErrInvalidArgument", err)
	}
}

func TestCoreCloseIsIdempotent(t *testing.T) {
	t.Parallel()

	core, err := inference.NewCore(mock.New(mock.Config{}))
	if err != nil {
		t.Fatalf("NewCore: %v", err)
	}
	if err := core.Close(); err != nil {
		t.Fatalf("Close: %v", err)
	}
	if err := core.Close(); err != nil {
		t.Fatalf("second Close: %v", err)
	}
	if _, err := core.Backends(context.Background()); !errors.Is(err, inference.ErrClosed) {
		t.Fatalf("Backends after Close error = %v, want ErrClosed", err)
	}
}
