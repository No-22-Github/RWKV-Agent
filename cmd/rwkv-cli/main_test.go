package main

import (
	"testing"

	"github.com/no22/RWKV-Agent/internal/terminal"
)

func TestOfficialG1ChatDefaults(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("run", []string{"--model", "model"})
	if err != nil {
		t.Fatal(err)
	}
	if options.reasoning {
		t.Fatal("reasoning must be opt-in for regular chat")
	}
	if options.reasoningExplicit {
		t.Fatal("omitted --reasoning must remain unspecified for Session inheritance")
	}
	if loadConversationOptions(options).Profile.TemplateID != "" {
		t.Fatal("Session load must inherit reasoning mode when the flag is omitted")
	}
	if options.temperature != 1 ||
		options.topP != 0.5 ||
		options.presencePenalty != 2 ||
		options.frequencyPenalty != 0.1 ||
		options.penaltyDecay != 0.99 {
		t.Fatalf("unexpected G1 chat defaults: %+v", options)
	}
}

func TestExplicitReasoningOverridesSessionInheritance(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions(
		"run",
		[]string{"--model", "model", "--reasoning=false"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if !options.reasoningExplicit {
		t.Fatal("--reasoning=false must count as an explicit mode selection")
	}
	if profile := loadConversationOptions(options).Profile; profile.TemplateID == "" ||
		profile.Reasoning {
		t.Fatalf("explicit profile = %+v", profile)
	}
}

func TestConcurrentUIOptions(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("concurrent", []string{"--model", "model"})
	if err != nil {
		t.Fatal(err)
	}
	if options.ui != string(terminal.UIAuto) {
		t.Fatalf("default UI = %q", options.ui)
	}
	if _, err := parseRunOptions("concurrent", []string{"--model", "model", "--ui", "invalid"}); err == nil {
		t.Fatal("invalid --ui accepted")
	}
}
