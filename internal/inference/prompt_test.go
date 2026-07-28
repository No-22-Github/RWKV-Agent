package inference

import (
	"errors"
	"testing"
)

func TestCompileGeneratePrompt(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name    string
		request GenerateRequest
		want    string
	}{
		{
			name: "reasoning chat",
			request: GenerateRequest{
				Messages: []Message{TextMessage(RoleUser, "你好")},
				Prompt:   PromptOptions{Reasoning: true},
			},
			want: "<|bos|>User: 你好\n\nAssistant: <think>\n</think>",
		},
		{
			name: "plain chat",
			request: GenerateRequest{
				Messages: []Message{TextMessage(RoleUser, "hello")},
			},
			want: "User: hello\n\nAssistant:",
		},
		{
			name: "raw",
			request: GenerateRequest{
				Raw:    &RawInput{Text: "raw input"},
				Prompt: PromptOptions{Reasoning: true},
			},
			want: "raw input",
		},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			got, err := CompileGeneratePrompt(test.request)
			if err != nil {
				t.Fatalf("CompileGeneratePrompt: %v", err)
			}
			if got != test.want {
				t.Fatalf("prompt = %q, want %q", got, test.want)
			}
		})
	}
}

func TestCompileGeneratePromptRejectsAmbiguousInput(t *testing.T) {
	t.Parallel()

	_, err := CompileGeneratePrompt(GenerateRequest{
		Messages: []Message{TextMessage(RoleUser, "hello")},
		Raw:      &RawInput{Text: "raw"},
	})
	if !errors.Is(err, ErrInvalidArgument) {
		t.Fatalf("error = %v, want ErrInvalidArgument", err)
	}
}
