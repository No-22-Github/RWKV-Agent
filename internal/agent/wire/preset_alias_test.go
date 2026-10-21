package wire

import "testing"

// The retired g1k names stay readable (old run.json, App configs, scripts) but
// are never written: names the model-facing configuration records come from
// MatchPreset, which only sees registered current names.

func TestRetiredNamesResolveToCurrentNames(t *testing.T) {
	cases := []struct{ retired, current string }{
		{"g1k", AgentWireV1},
		{"g1k-think", AgentWireThinkV1},
	}
	for _, testCase := range cases {
		retiredSpec, retiredName, err := Resolve(testCase.retired)
		if err != nil {
			t.Fatalf("Resolve(%q): %v", testCase.retired, err)
		}
		currentSpec, currentName, err := Resolve(testCase.current)
		if err != nil {
			t.Fatalf("Resolve(%q): %v", testCase.current, err)
		}
		if retiredName != testCase.current {
			t.Errorf("Resolve(%q) name = %q, want %q", testCase.retired, retiredName, testCase.current)
		}
		if currentName != testCase.current {
			t.Errorf("Resolve(%q) name = %q, want %q", testCase.current, currentName, testCase.current)
		}
		if retiredSpec.Canonical() != currentSpec.Canonical() {
			t.Errorf("Resolve(%q) canonical = %s, want %s", testCase.retired, retiredSpec.Canonical(), currentSpec.Canonical())
		}
	}

	withModifier, _, err := Resolve("g1k+think-full")
	if err != nil {
		t.Fatalf("Resolve(g1k+think-full): %v", err)
	}
	currentWithModifier, _, err := Resolve(AgentWireV1 + "+think-full")
	if err != nil {
		t.Fatalf("Resolve(%s+think-full): %v", AgentWireV1, err)
	}
	if withModifier.Canonical() != currentWithModifier.Canonical() {
		t.Fatalf("Resolve(g1k+think-full) = %s, want %s", withModifier.Canonical(), currentWithModifier.Canonical())
	}
}

func TestNamesAndMatchPresetUseCurrentNamesOnly(t *testing.T) {
	for _, name := range Names() {
		if name == "g1k" || name == "g1k-think" {
			t.Errorf("alias %q is listed as a registered preset", name)
		}
	}
	for _, alias := range []string{"g1k", "g1k-think"} {
		if _, canonical := presetAliases[alias]; !canonical {
			t.Errorf("%q is missing from the alias table", alias)
		}
	}
	spec, ok := Lookup(AgentWireV1)
	if !ok {
		t.Fatalf("%s is not registered", AgentWireV1)
	}
	if match, ok := spec.MatchPreset(); !ok || match != AgentWireV1 {
		t.Errorf("MatchPreset() = %q/%v, want %s", match, ok, AgentWireV1)
	}
}

// Clearing the alias table must break the retired spellings; otherwise the
// test above proves nothing about the alias path.
func TestAliasesAreWhatMakesRetiredNamesWork(t *testing.T) {
	saved := presetAliases
	presetAliases = map[string]string{}
	defer func() { presetAliases = saved }()

	for _, retired := range []string{"g1k", "g1k-think", "g1k+think-full"} {
		if _, _, err := Resolve(retired); err == nil {
			t.Errorf("Resolve(%q) succeeded with the alias table cleared", retired)
		}
	}
	// Current names keep working: they are registered, not aliased.
	if _, _, err := Resolve(AgentWireV1); err != nil {
		t.Errorf("Resolve(%q) with the alias table cleared: %v", AgentWireV1, err)
	}
}
