//go:build darwin && arm64 && cgo && mlx

package rwkvmobile_test

import (
	"context"
	"errors"
	"os"
	"sync"
	"testing"
	"time"

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

func TestEightSessionGreedyBatchPreservesEveryStateSlot(t *testing.T) {
	modelPath := os.Getenv("RWKV_TEST_MODEL")
	tokenizerPath := os.Getenv("RWKV_TEST_TOKENIZER")
	if modelPath == "" || tokenizerPath == "" {
		t.Skip("RWKV_TEST_MODEL and RWKV_TEST_TOKENIZER are not set")
	}
	value := backend.New(backend.Options{Provider: "mlx", MaxActiveBatch: 8})
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

	const count = 8
	sessions := make([]inference.Session, count)
	for index := range sessions {
		sessions[index], err = model.NewSession(context.Background(), inference.SessionOptions{})
		if err != nil {
			t.Fatal(err)
		}
		defer sessions[index].Close()
	}
	results := make([]inference.GenerateResult, count)
	errs := make([]error, count)
	firstToken := make(chan struct{}, 2)
	request := inference.GenerateRequest{
		Messages: []inference.Message{
			inference.TextMessage(inference.RoleUser, "从一到一百逐个列出数字，不要省略。"),
		},
		Sampling: inference.SamplingOptions{
			Temperature: 1,
			TopK:        1,
			TopP:        0.5,
		},
		Limits: inference.GenerationLimits{MaxOutputTokens: 64},
		Commit: inference.CommitOnSuccess,
	}

	var wait sync.WaitGroup
	startSession := func(index int) {
		wait.Add(1)
		go func() {
			defer wait.Done()
			notified := false
			results[index], errs[index] = sessions[index].Generate(
				context.Background(),
				request,
				func(event inference.GenerationEvent) error {
					if index < 2 && !notified && event.Kind == inference.EventOutputDelta {
						notified = true
						firstToken <- struct{}{}
					}
					return nil
				},
			)
		}()
	}
	startSession(0)
	startSession(1)
	for range 2 {
		select {
		case <-firstToken:
		case <-time.After(10 * time.Second):
			t.Fatal("initial batch did not begin decoding")
		}
	}
	for index := 2; index < count; index++ {
		startSession(index)
	}
	wait.Wait()

	for index := range sessions {
		if errs[index] != nil {
			t.Fatalf("session %d failed: %v", index+1, errs[index])
		}
		if !results[index].Committed {
			t.Fatalf("session %d was not committed", index+1)
		}
		if results[index].Output != results[0].Output {
			t.Fatalf(
				"session %d diverged under greedy decoding\nfirst: %q\nactual: %q",
				index+1,
				results[0].Output,
				results[index].Output,
			)
		}
	}
	if observed := model.Capabilities().MaxObservedBatch; observed != 8 {
		t.Fatalf("max observed native batch = %d, want 8", observed)
	}
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
