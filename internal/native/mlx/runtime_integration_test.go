//go:build darwin && arm64 && cgo && mlx

package mlx

import (
	"context"
	"os"
	"strings"
	"testing"
)

func TestNativeMLXGeneration(t *testing.T) {
	model := os.Getenv("RWKV_TEST_MODEL")
	tokenizer := os.Getenv("RWKV_TEST_TOKENIZER")
	if model == "" || tokenizer == "" {
		t.Skip("set RWKV_TEST_MODEL and RWKV_TEST_TOKENIZER to run native inference")
	}

	runtime, err := Open(model, tokenizer)
	if err != nil {
		t.Fatalf("Open: %v", err)
	}
	defer runtime.Close()

	var output strings.Builder
	err = runtime.Generate(
		context.Background(),
		"<|bos|>User: 你好\n\nAssistant: <think>\n</think>",
		GenerateOptions{MaxTokens: 8, Temperature: 1, TopK: 1, TopP: 1},
		func(text string) error {
			_, writeErr := output.WriteString(text)
			return writeErr
		},
	)
	if err != nil {
		t.Fatalf("Generate: %v", err)
	}
	if output.Len() == 0 {
		t.Fatal("Generate returned no text")
	}
}
