package local

import (
	"context"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
)

func TestGeneratorAdaptsInferenceSession(t *testing.T) {
	t.Parallel()
	core, err := inference.NewCore(mock.New(mock.Config{
		Output:    `{"type":"final","content":"done"}`,
		ChunkSize: 5,
	}))
	if err != nil {
		t.Fatal(err)
	}
	defer core.Close()
	model, err := core.LoadModel(context.Background(), inference.LoadRequest{
		Source:  inference.ModelSource{Path: "mock"},
		Backend: mock.BackendID,
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	session, err := model.NewSession(context.Background(), inference.SessionOptions{})
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	generator, err := New(session)
	if err != nil {
		t.Fatal(err)
	}
	var streamed string
	result, err := generator.Continue(
		context.Background(),
		continuation.Request{
			Prompt:          "User: task\n\nAssistant:",
			MaxOutputTokens: 64,
			Sampling: continuation.Sampling{
				Temperature:  1,
				TopK:         1,
				TopP:         1,
				PenaltyDecay: 0.99,
			},
		},
		func(event continuation.Event) error {
			streamed += event.Text
			return nil
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != `{"type":"final","content":"done"}` || streamed != result.Text {
		t.Fatalf("result = %+v, streamed = %q", result, streamed)
	}
}
