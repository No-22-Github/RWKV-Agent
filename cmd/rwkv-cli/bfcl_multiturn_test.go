package main

import "testing"

func TestParseBFCLMultiTurnOptionsAcceptsEnhancedQwen(t *testing.T) {
	t.Parallel()
	options, err := parseBFCLMultiTurnOptions([]string{
		"--model", "Qwen/Qwen3-8B-FP8",
		"--api-url", "http://example.com/v1/chat/completions",
		"--transport", "chat-completions-wrapped",
		"--chat-template-thinking", "disabled",
		"--tier", "enhanced",
		"--split", "multi_turn_base",
		"--case", "multi_turn_base_0",
		"--output", "runs/bfcl-mt/qwen",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.tier != "enhanced" || options.transport != "chat-completions-wrapped" || options.maxSteps != 20 || options.maxPromptChars != 0 {
		t.Fatalf("options = %+v", options)
	}
}

func TestParseBFCLMultiTurnOptionsRejectsSplitCaseMismatch(t *testing.T) {
	t.Parallel()
	_, err := parseBFCLMultiTurnOptions([]string{
		"--model", "model",
		"--api-url", "https://example.com/v1/chat/completions",
		"--split", "multi_turn_base",
		"--case", "multi_turn_miss_func_0",
		"--output", "runs/bfcl-mt/mismatch",
	})
	if err == nil {
		t.Fatal("expected split/case mismatch error")
	}
}
