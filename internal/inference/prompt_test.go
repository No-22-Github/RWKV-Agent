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
			want: "User: 你好\n\nAssistant: <think>\n</think>",
		},
		{
			name: "plain chat",
			request: GenerateRequest{
				Messages: []Message{TextMessage(RoleUser, "hello")},
			},
			want: "User: hello\n\nAssistant:",
		},
		{
			name: "official input cleanup",
			request: GenerateRequest{
				Messages: []Message{
					TextMessage(RoleSystem, " concise\r\n\r\nplease "),
					TextMessage(RoleUser, " first\n\n\nsecond "),
				},
			},
			want: "System: concise\nplease\n\nUser: first\nsecond\n\nAssistant:",
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

func TestCompileCommittedPromptGolden(t *testing.T) {
	t.Parallel()
	messages := []Message{
		TextMessage(RoleSystem, "be concise"),
		TextMessage(RoleUser, "hello"),
		TextMessage(RoleAssistant, "hi"),
		TextMessage(RoleUser, "again"),
	}
	got, err := CompileCommittedPrompt(messages, PromptOptions{Reasoning: true})
	if err != nil {
		t.Fatal(err)
	}
	want := "System: be concise\n\nUser: hello\n\nAssistant: hi\n\nUser: again\n\n"
	if got != want {
		t.Fatalf("committed prompt = %q, want %q", got, want)
	}
	profile := DefaultPromptProfile(true)
	if profile.TemplateID != PromptTemplateID ||
		profile.TemplateVersion != PromptTemplateVersion ||
		profile.ProfileHash == "" {
		t.Fatalf("invalid prompt profile: %+v", profile)
	}
}
