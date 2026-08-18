package main

import "testing"

func TestParseBFCLEvalOptionsAcceptsM2Baseline(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLEvalOptions([]string{
		"--model", "rwkv7-g1i-7.2b",
		"--api-url", "https://example.com/v1/batch/completions",
		"--tier", "baseline",
		"--split", "simple_python",
		"--output", "runs/bfcl/m2",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.tier != "baseline" || len(options.splits) != 1 || options.splits[0] != "simple_python" {
		t.Fatalf("options = %+v", options)
	}
}

func TestParseBFCLEvalOptionsAcceptsWrappedQwenBaseline(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLEvalOptions([]string{
		"--model", "Qwen/Qwen3-8B-FP8",
		"--api-url", "http://example.com/v1/chat/completions",
		"--tier", "baseline",
		"--transport", "chat-completions-wrapped",
		"--chat-template-thinking", "disabled",
		"--split", "simple_python",
		"--output", "runs/bfcl/qwen",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.transport != "chat-completions-wrapped" || options.chatTemplateThinking != "disabled" {
		t.Fatalf("options = %+v", options)
	}
}

func TestParseBFCLEvalOptionsRestrictsM2Split(t *testing.T) {
	t.Parallel()
	_, err := parseBFCLEvalOptions([]string{
		"--model", "rwkv7-g1i-7.2b",
		"--api-url", "https://example.com/v1/batch/completions",
		"--tier", "baseline",
		"--split", "multiple",
		"--output", "runs/bfcl/m2",
	})
	if err == nil {
		t.Fatal("expected M2 split validation error")
	}
}
