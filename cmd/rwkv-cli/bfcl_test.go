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

func TestParseBFCLEvalOptionsAcceptsFrozenSampleAcrossSplits(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLEvalOptions([]string{
		"--model", "Qwen/Qwen3-8B-FP8",
		"--api-url", "http://example.com/v1/chat/completions",
		"--tier", "baseline",
		"--transport", "chat-completions-wrapped",
		"--split", "simple_python,multiple",
		"--sample-manifest", "configs/bfcl-sample-v1.json",
		"--output", "runs/bfcl/sample",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.sampleManifest != "configs/bfcl-sample-v1.json" || len(options.splits) != 2 {
		t.Fatalf("options = %+v", options)
	}
}

func TestParseBFCLEvalOptionsAcceptsFullBaseline(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLEvalOptions([]string{
		"--model", "Qwen/Qwen3-8B-FP8",
		"--api-url", "http://example.com/v1/chat/completions",
		"--tier", "baseline",
		"--transport", "chat-completions-wrapped",
		"--split", "simple_python,parallel",
		"--full",
		"--output", "runs/bfcl/full",
	})
	if err != nil {
		t.Fatal(err)
	}
	if !options.full || len(options.splits) != 2 {
		t.Fatalf("options = %+v", options)
	}
}

func TestParseBFCLEvalOptionsAllowsNativeFCTemplateThinking(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLEvalOptions([]string{
		"--model", "Qwen/Qwen3-8B-FP8",
		"--api-url", "http://example.com/v1/chat/completions",
		"--tier", "adapter-health",
		"--transport", "chat-completions-native-fc",
		"--chat-template-thinking", "disabled",
		"--split", "simple_python",
		"--full",
		"--output", "runs/bfcl/native-nothink",
	})
	if err != nil {
		t.Fatal(err)
	}
	enableThinking := options.chatTemplateEnableThinking()
	if enableThinking == nil || *enableThinking {
		t.Fatalf("enable_thinking = %v, want pointer to false", enableThinking)
	}
}

func TestBFCLEvalTemplateThinkingAutoLeavesServerDefault(t *testing.T) {
	t.Parallel()
	options := bfclEvalOptions{chatTemplateThinking: "auto"}
	if got := options.chatTemplateEnableThinking(); got != nil {
		t.Fatalf("enable_thinking = %v, want nil so the server default is untouched", *got)
	}
	options.chatTemplateThinking = "enabled"
	if got := options.chatTemplateEnableThinking(); got == nil || !*got {
		t.Fatalf("enable_thinking = %v, want pointer to true", got)
	}
}

func TestParseBFCLEvalOptionsRejectsTemplateThinkingOnRWKVContinuation(t *testing.T) {
	t.Parallel()
	_, err := parseBFCLEvalOptions([]string{
		"--model", "rwkv7-g1i-7.2b",
		"--api-url", "https://example.com/v1/batch/completions",
		"--tier", "baseline",
		"--transport", "rwkv-continuation",
		"--chat-template-thinking", "disabled",
		"--split", "simple_python",
		"--output", "runs/bfcl/rwkv-nothink",
	})
	if err == nil {
		t.Fatal("expected --chat-template-thinking to be rejected for rwkv-continuation")
	}
}

func TestParseBFCLReparseOptions(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLReparseOptions([]string{
		"--source", "runs/bfcl/m2",
		"--output", "runs/bfcl/m2.5",
		"--parser", "rwkv-wire-compat-v1",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.source != "runs/bfcl/m2" || options.output != "runs/bfcl/m2.5" ||
		options.parser != "rwkv-wire-compat-v1" {
		t.Fatalf("options = %+v", options)
	}
}
