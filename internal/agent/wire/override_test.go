package wire

import (
	"strings"
	"testing"
)

func TestParseOverrides(t *testing.T) {
	t.Parallel()
	overrides, err := ParseOverrides(" format=md-fence , prefill=fence ,thinking=off")
	if err != nil {
		t.Fatal(err)
	}
	want := map[string]string{"format": "md-fence", "prefill": "fence", "thinking": "off"}
	for key, value := range want {
		if overrides[key] != value {
			t.Fatalf("overrides = %+v", overrides)
		}
	}
	cases := []struct {
		value string
		code  string
	}{
		{"", "override.empty"},
		{"format", "override.shape"},
		{"=xml", "override.shape"},
		{"format=", "override.shape"},
		{"format=xml,format=md-fence", "override.duplicate"},
		{"nope=xml", "override.unknown"},
	}
	for _, testCase := range cases {
		_, err := ParseOverrides(testCase.value)
		if err == nil {
			t.Fatalf("ParseOverrides(%q) succeeded, want %s", testCase.value, testCase.code)
		}
		specErr, ok := err.(*SpecError)
		if !ok || specErr.Code != testCase.code {
			t.Fatalf("ParseOverrides(%q) = %v, want code %s", testCase.value, err, testCase.code)
		}
	}
}

func TestWithOverridesComposesOnBase(t *testing.T) {
	t.Parallel()
	base, _, err := Resolve("md-v1")
	if err != nil {
		t.Fatal(err)
	}
	// Only the named axes change: the base keeps its no-tool exit and loop.
	overridden, err := base.WithOverrides(map[string]string{
		"prefill":  "fence",
		"thinking": "off",
	})
	if err != nil {
		t.Fatal(err)
	}
	if overridden.Prefill != PrefillFence || overridden.Abstain != AbstainNoTool ||
		overridden.Format != FormatMDFence {
		t.Fatalf("overridden = %s", overridden.Canonical())
	}
	// Free composition the preset space did not cover: XML thinking + envelope.
	xmlSpec := Default()
	composed, err := xmlSpec.WithOverrides(map[string]string{
		"thinking": "full",
		"route":    "respond-inspect",
		"prefill":  "envelope",
	})
	if err == nil {
		t.Fatalf("thinking=full with prefill=envelope accepted: %s", composed.Canonical())
	}
	if !strings.Contains(err.Error(), "prefill.conflict") {
		t.Fatalf("error = %v, want prefill.conflict", err)
	}
	// The valid half-open composition.
	composed, err = xmlSpec.WithOverrides(map[string]string{
		"thinking": "fast",
		"route":    "respond-inspect",
	})
	if err != nil {
		t.Fatal(err)
	}
	if composed.Thinking != ThinkingFast || composed.Prefill != PrefillNone {
		t.Fatalf("composed = %s", composed.Canonical())
	}
	// An override that breaks a cross-axis rule fails validation.
	if _, err := base.WithOverrides(map[string]string{"abstain": "none"}); err == nil {
		t.Fatal("deep-fence without abstain accepted")
	}
}
