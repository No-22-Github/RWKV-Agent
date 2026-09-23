package samplingpreset

import "testing"

// TestPresetValuesArePinned locks the measured numbers: a changed value is a
// new measurement and must update the sweep report, not slip in silently.
func TestPresetValuesArePinned(t *testing.T) {
	t.Parallel()
	want := map[string]Preset{
		"greedy":         {Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1},
		"g1k-agent":      {Temperature: 0.3, TopK: 65536, TopP: 0.5, PenaltyDecay: 1},
		"g1k-agent-fast": {Temperature: 0.3, TopK: 65536, TopP: 0.5, PresencePenalty: 0.5, FrequencyPenalty: 0.1, PenaltyDecay: 0.996},
		"g1k-stable":     {Temperature: 1, TopK: 20, TopP: 0.3, PenaltyDecay: 1},
		"backend":        {Temperature: 1, TopK: 20, TopP: 0.3, PresencePenalty: 2, FrequencyPenalty: 0.2, PenaltyDecay: 0.996},
	}
	if len(Names()) != len(want) {
		t.Fatalf("presets = %v", Names())
	}
	for name, w := range want {
		got, ok := Lookup(name)
		if !ok {
			t.Fatalf("missing preset %q", name)
		}
		if got.Temperature != w.Temperature || got.TopK != w.TopK || got.TopP != w.TopP ||
			got.PresencePenalty != w.PresencePenalty || got.FrequencyPenalty != w.FrequencyPenalty ||
			got.PenaltyDecay != w.PenaltyDecay || got.Use == "" {
			t.Fatalf("%s = %+v", name, got)
		}
		// top_k 1 makes temperature and top_p inert; only greedy may use it.
		if got.TopK == 1 && name != "greedy" {
			t.Fatalf("%s sets top_k 1, which silently disables its temperature", name)
		}
	}
}

func TestMatchRecognisesPresetsAndRejectsOverrides(t *testing.T) {
	t.Parallel()
	if got := Match(0.3, 65536, 0.5, 0, 0, 1); got != "g1k-agent" {
		t.Fatalf("g1k-agent values matched %q", got)
	}
	if got := Match(0.5, 65536, 0.5, 0, 0, 1); got != "" {
		t.Fatalf("overridden temperature still matched %q", got)
	}
	// An API provider drops top_k and penalty_decay; the rest still identifies the preset.
	if got := Match(0.3, 0, 0.5, 0.5, 0.1, 0, "top_k", "penalty_decay"); got != "g1k-agent-fast" {
		t.Fatalf("API-side g1k-agent-fast matched %q", got)
	}
}
