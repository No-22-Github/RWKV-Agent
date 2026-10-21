package samplingpreset

import "testing"

// TestPresetValuesArePinned locks the measured numbers: a changed value is a
// new measurement and must update the sweep report, not slip in silently.
func TestPresetValuesArePinned(t *testing.T) {
	t.Parallel()
	want := map[string]Preset{
		Greedy:       {Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1},
		AgentDefault: {Temperature: 0.3, TopK: 65536, TopP: 0.5, PenaltyDecay: 1},
		AgentFast:    {Temperature: 0.3, TopK: 65536, TopP: 0.5, PresencePenalty: 0.5, FrequencyPenalty: 0.1, PenaltyDecay: 0.996},
		AgentStable:  {Temperature: 1, TopK: 20, TopP: 0.3, PenaltyDecay: 1},
		Backend:      {Temperature: 1, TopK: 20, TopP: 0.3, PresencePenalty: 2, FrequencyPenalty: 0.2, PenaltyDecay: 0.996},
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
		if got.TopK == 1 && name != Greedy {
			t.Fatalf("%s sets top_k 1, which silently disables its temperature", name)
		}
	}
}

func TestMatchRecognisesPresetsAndRejectsOverrides(t *testing.T) {
	t.Parallel()
	if got := Match(0.3, 65536, 0.5, 0, 0, 1); got != AgentDefault {
		t.Fatalf("agent-default values matched %q", got)
	}
	if got := Match(0.5, 65536, 0.5, 0, 0, 1); got != "" {
		t.Fatalf("overridden temperature still matched %q", got)
	}
	// An API provider drops top_k and penalty_decay; the rest still identifies the preset.
	if got := Match(0.3, 0, 0.5, 0.5, 0.1, 0, "top_k", "penalty_decay"); got != AgentFast {
		t.Fatalf("API-side agent-fast matched %q", got)
	}
}

// The retired names stay readable — old run.json files and saved commands use
// them — but never listed, so Match keeps returning one name per value set.
func TestRetiredNamesResolveButAreNotListed(t *testing.T) {
	t.Parallel()
	for retired, current := range map[string]string{
		"g1k-agent":      AgentDefault,
		"g1k-agent-fast": AgentFast,
		"g1k-stable":     AgentStable,
	} {
		if CanonicalName(retired) != current {
			t.Errorf("CanonicalName(%q) = %q, want %q", retired, CanonicalName(retired), current)
		}
		preset, ok := Lookup(retired)
		if !ok || preset.Name != current {
			t.Errorf("Lookup(%q) = %q/%v, want %q", retired, preset.Name, ok, current)
		}
	}
	for _, name := range Names() {
		if name == "g1k-agent" || name == "g1k-agent-fast" || name == "g1k-stable" {
			t.Errorf("alias %q is listed as a preset", name)
		}
	}
	if got := Match(0.3, 65536, 0.5, 0, 0, 1); got != AgentDefault {
		t.Errorf("Match returned the retired name %q", got)
	}
}
