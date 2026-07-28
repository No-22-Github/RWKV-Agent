//go:build darwin && arm64 && cgo && mlx

package rwkvmobile_test

import (
	"context"
	"errors"
	"os"
	"sync"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
	backend "github.com/no22/RWKV-Agent/internal/inference/backend/rwkvmobile"
	"github.com/no22/RWKV-Agent/internal/inference/contracttest"
)

func TestRWKVMobileBackendContract(t *testing.T) {
	modelPath := os.Getenv("RWKV_TEST_MODEL")
	tokenizerPath := os.Getenv("RWKV_TEST_TOKENIZER")
	if modelPath == "" || tokenizerPath == "" {
		t.Skip("RWKV_TEST_MODEL and RWKV_TEST_TOKENIZER are not set")
	}
	contracttest.Run(t, contracttest.Suite{
		NewModel: func(t *testing.T) inference.Model {
			value := backend.New(backend.Options{Provider: "mlx", MaxActiveBatch: 4})
			model, err := value.LoadModel(context.Background(), inference.LoadRequest{
				Source: inference.ModelSource{
					Path:          modelPath,
					TokenizerPath: tokenizerPath,
				},
			}, nil)
			if err != nil {
				t.Fatal(err)
			}
			return model
		},
		Request: inference.GenerateRequest{
			Messages: []inference.Message{
				inference.TextMessage(inference.RoleUser, "只回答 OK。"),
			},
			Sampling: inference.SamplingOptions{
				Temperature: 1,
				TopK:        32,
				TopP:        0.8,
			},
			Limits: inference.GenerationLimits{MaxOutputTokens: 8},
			Commit: inference.CommitOnSuccess,
		},
	})
}

func TestFourSessionContinuousBatchAndIndependentCancel(t *testing.T) {
	modelPath := os.Getenv("RWKV_TEST_MODEL")
	tokenizerPath := os.Getenv("RWKV_TEST_TOKENIZER")
	if modelPath == "" || tokenizerPath == "" {
		t.Skip("RWKV_TEST_MODEL and RWKV_TEST_TOKENIZER are not set")
	}
	value := backend.New(backend.Options{Provider: "mlx", MaxActiveBatch: 4})
	model, err := value.LoadModel(context.Background(), inference.LoadRequest{
		Source: inference.ModelSource{
			Path:          modelPath,
			TokenizerPath: tokenizerPath,
		},
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	defer model.Close()

	sessions := make([]inference.Session, 4)
	for index := range sessions {
		sessions[index], err = model.NewSession(context.Background(), inference.SessionOptions{})
		if err != nil {
			t.Fatal(err)
		}
		defer sessions[index].Close()
	}

	start := make(chan struct{})
	results := make([]inference.GenerateResult, len(sessions))
	errs := make([]error, len(sessions))
	var wait sync.WaitGroup
	for index, session := range sessions {
		wait.Add(1)
		go func(index int, session inference.Session) {
			defer wait.Done()
			ctx := context.Background()
			cancel := func() {}
			if index == 0 {
				ctx, cancel = context.WithCancel(ctx)
			}
			defer cancel()
			<-start
			results[index], errs[index] = session.Generate(
				ctx,
				inference.GenerateRequest{
					Messages: []inference.Message{
						inference.TextMessage(inference.RoleUser, "用一句话回答并发测试。"),
					},
					Prompt: inference.PromptOptions{Reasoning: false},
					Sampling: inference.SamplingOptions{
						Temperature: 1,
						TopK:        32,
						TopP:        0.8,
					},
					Limits: inference.GenerationLimits{MaxOutputTokens: 12},
					Commit: inference.CommitOnSuccess,
				},
				func(event inference.GenerationEvent) error {
					if index == 0 && event.Kind == inference.EventOutputDelta {
						cancel()
					}
					return nil
				},
			)
		}(index, session)
	}
	close(start)
	wait.Wait()

	if !errors.Is(errs[0], context.Canceled) {
		t.Fatalf("cancelled session error = %v, want context.Canceled", errs[0])
	}
	if results[0].Committed {
		t.Fatal("cancelled session was committed")
	}
	for index := 1; index < len(sessions); index++ {
		if errs[index] != nil {
			t.Fatalf("session %d failed: %v", index, errs[index])
		}
		if results[index].Output == "" || !results[index].Committed {
			t.Fatalf("session %d result is not isolated and committed: %+v", index, results[index])
		}
	}
	if observed := model.Capabilities().MaxObservedBatch; observed != 4 {
		t.Fatalf("max observed native batch = %d, want 4", observed)
	}
	if state := sessions[0].StateInfo(); state.Status != "dirty" {
		t.Fatalf("cancelled session status = %q, want dirty", state.Status)
	}
	for index := 1; index < len(sessions); index++ {
		if state := sessions[index].StateInfo(); state.Status != "clean" {
			t.Fatalf("session %d status = %q, want clean", index, state.Status)
		}
	}
}
