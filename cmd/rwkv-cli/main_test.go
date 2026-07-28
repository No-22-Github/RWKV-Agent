package main

import "testing"

func TestOfficialG1ChatDefaults(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("run", []string{"--model", "model"})
	if err != nil {
		t.Fatal(err)
	}
	if options.reasoning {
		t.Fatal("reasoning must be opt-in for regular chat")
	}
	if options.temperature != 1 ||
		options.topP != 0.5 ||
		options.presencePenalty != 2 ||
		options.frequencyPenalty != 0.1 ||
		options.penaltyDecay != 0.99 {
		t.Fatalf("unexpected G1 chat defaults: %+v", options)
	}
}
