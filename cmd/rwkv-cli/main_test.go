package main

import "testing"

func TestRenderPrompt(t *testing.T) {
	t.Parallel()

	if got, want := renderPrompt("你好", false, true), "<|bos|>User: 你好\n\nAssistant: <think>\n</think>"; got != want {
		t.Fatalf("reasoning prompt = %q, want %q", got, want)
	}
	if got, want := renderPrompt("hello", false, false), "User: hello\n\nAssistant:"; got != want {
		t.Fatalf("plain chat prompt = %q, want %q", got, want)
	}
	if got, want := renderPrompt("raw input", true, true), "raw input"; got != want {
		t.Fatalf("raw prompt = %q, want %q", got, want)
	}
}
