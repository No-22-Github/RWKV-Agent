//go:build darwin && arm64 && cgo && mlx

package mlxbackend_test

import (
	"context"
	"os"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
	mlxbackend "github.com/no22/RWKV-Agent/internal/inference/backend/mlx"
	"github.com/no22/RWKV-Agent/internal/inference/contracttest"
)

func TestMLXBackendContract(t *testing.T) {
	modelPath := os.Getenv("RWKV_TEST_MODEL")
	tokenizerPath := os.Getenv("RWKV_TEST_TOKENIZER")
	if modelPath == "" || tokenizerPath == "" {
		t.Skip("set RWKV_TEST_MODEL and RWKV_TEST_TOKENIZER to run native inference")
	}

	backend := mlxbackend.New()
	contracttest.Run(t, contracttest.Suite{
		NewModel: func(t *testing.T) inference.Model {
			t.Helper()
			model, err := backend.LoadModel(
				context.Background(),
				inference.LoadRequest{
					Source: inference.ModelSource{
						Path:          modelPath,
						TokenizerPath: tokenizerPath,
					},
					Backend: mlxbackend.BackendID,
				},
				nil,
			)
			if err != nil {
				t.Fatalf("LoadModel: %v", err)
			}
			return model
		},
		Request: inference.GenerateRequest{
			Messages: []inference.Message{
				inference.TextMessage(inference.RoleUser, "你好"),
			},
			Sampling: inference.SamplingOptions{
				Temperature: 1,
				TopK:        1,
				TopP:        1,
			},
			Limits: inference.GenerationLimits{MaxOutputTokens: 8},
			Commit: inference.CommitOnSuccess,
		},
	})
}
