package wire

import (
	"strings"
	"testing"
)

func TestRegisteredPresetsValidateAndRoundTrip(t *testing.T) {
	t.Parallel()
	for _, name := range Names() {
		spec, ok := Lookup(name)
		if !ok {
			t.Fatalf("preset %q missing after Names()", name)
		}
		if err := spec.Validate(); err != nil {
			t.Fatalf("preset %q invalid: %v", name, err)
		}
		resolved, resolvedName, err := Resolve(name)
		if err != nil {
			t.Fatalf("Resolve(%q): %v", name, err)
		}
		if resolvedName != name {
			t.Fatalf("Resolve(%q) name = %q, want %q", name, resolvedName, name)
		}
		if !resolved.Equal(spec) {
			t.Fatalf("Resolve(%q) drifted:\nwant %s\n got %s", name, spec.Canonical(), resolved.Canonical())
		}
		parsed, _, err := Resolve(spec.Canonical())
		if err != nil {
			t.Fatalf("Resolve(canonical of %q): %v", name, err)
		}
		if !parsed.Equal(spec) {
			t.Fatalf("canonical round trip of %q drifted:\nwant %s\n got %s", name, spec.Canonical(), parsed.Canonical())
		}
	}
}

func TestResolveModifiersCompose(t *testing.T) {
	t.Parallel()
	cases := []struct {
		value      string
		check      func(Spec) bool
		wantPreset string
	}{
		{
			value:      "md-v1+anchor+gate-state",
			wantPreset: "",
			check: func(s Spec) bool {
				return s.Prefill == PrefillDeepFence && s.Abstain == AbstainNoToolGateState
			},
		},
		{
			value:      "md-v1+fence",
			wantPreset: "",
			check:      func(s Spec) bool { return s.Prefill == PrefillFence && s.Abstain == AbstainNoTool },
		},
		{
			value:      "md-v1+fake-think",
			wantPreset: "",
			check:      func(s Spec) bool { return s.Prefill == PrefillFakeThinkHalf },
		},
		{
			value:      "xml-v1+envelope",
			wantPreset: "",
			check: func(s Spec) bool {
				return s.Prefill == PrefillEnvelope && s.Route == RouteRespondInspect
			},
		},
		{
			value:      "xml-v1+progressive",
			wantPreset: "",
			check: func(s Spec) bool {
				return s.Route == RouteProgressive && s.Catalog == CatalogProgressive && s.Prefill == PrefillEnvelope
			},
		},
		{
			value:      "bfcl-md-v1+gate-evidence",
			wantPreset: "",
			check:      func(s Spec) bool { return s.Abstain == AbstainNoToolGateEvidence && s.Route == RouteProgressive },
		},
		{
			value:      "md-v1",
			wantPreset: "md-v1",
			check:      func(s Spec) bool { return s.Format == FormatMDFence },
		},
	}
	for _, testCase := range cases {
		spec, name, err := Resolve(testCase.value)
		if err != nil {
			t.Fatalf("Resolve(%q): %v", testCase.value, err)
		}
		if name != testCase.wantPreset {
			t.Fatalf("Resolve(%q) name = %q, want %q", testCase.value, name, testCase.wantPreset)
		}
		if !testCase.check(spec) {
			t.Fatalf("Resolve(%q) = %s", testCase.value, spec.Canonical())
		}
	}
}

func TestResolveRejectsUnknown(t *testing.T) {
	t.Parallel()
	cases := []struct {
		value string
		code  string
	}{
		{"", "resolve.empty"},
		{"nope-v1", "resolve.unknown-preset"},
		{"md-v1+nope", "resolve.unknown-modifier"},
		{"format=xml", "resolve.canonical-fields"},
	}
	for _, testCase := range cases {
		_, _, err := Resolve(testCase.value)
		if err == nil {
			t.Fatalf("Resolve(%q) succeeded, want %s", testCase.value, testCase.code)
		}
		specErr, ok := err.(*SpecError)
		if !ok || specErr.Code != testCase.code {
			t.Fatalf("Resolve(%q) error = %v, want code %s", testCase.value, err, testCase.code)
		}
	}
}

func TestValidateCrossAxisTable(t *testing.T) {
	t.Parallel()
	with := func(mutate func(*Spec)) Spec {
		spec := Default()
		mutate(&spec)
		return spec
	}
	cases := []struct {
		name string
		spec Spec
		code string
	}{
		{
			name: "half-open thinking owns the opening",
			spec: with(func(s *Spec) { s.Thinking = ThinkingFast; s.Prefill = PrefillFence }),
			code: "prefill.conflict",
		},
		{
			name: "md-fence has no think slot",
			spec: with(func(s *Spec) { s.Format = FormatMDFence; s.Thinking = ThinkingFast }),
			code: "thinking.unsupported",
		},
		{
			name: "deep anchor needs an abstention exit",
			spec: with(func(s *Spec) { s.Format = FormatMDFence; s.Prefill = PrefillDeepFence }),
			code: "prefill.requires-abstain",
		},
		{
			name: "envelope needs a router",
			spec: with(func(s *Spec) { s.Prefill = PrefillEnvelope }),
			code: "prefill.not-wired",
		},
		{
			name: "envelope is xml only",
			spec: with(func(s *Spec) {
				s.Format = FormatMDFence
				s.Prefill = PrefillEnvelope
				s.Route = RouteRespondInspect
				s.Abstain = AbstainNoTool
			}),
			code: "prefill.unsupported",
		},
		{
			name: "deep anchor is md only",
			spec: with(func(s *Spec) { s.Prefill = PrefillDeepFence; s.Abstain = AbstainNoTool }),
			code: "prefill.unsupported",
		},
		{
			name: "fake think is md only",
			spec: with(func(s *Spec) { s.Prefill = PrefillFakeThinkHalf; s.Abstain = AbstainNoTool }),
			code: "prefill.unsupported",
		},
		{
			name: "progressive route and catalog travel together",
			spec: with(func(s *Spec) { s.Route = RouteProgressive }),
			code: "route.catalog-mismatch",
		},
		{
			name: "native transport has no prefill",
			spec: with(func(s *Spec) {
				s.Format = FormatMDFence
				s.Prefill = PrefillDeepFence
				s.Abstain = AbstainNoTool
				s.Transport = TransportNative
			}),
			code: "transport.prefill",
		},
		{
			name: "few-shot is xml only",
			spec: with(func(s *Spec) { s.Format = FormatMDFence; s.Control = ControlFewShot }),
			code: "control.unsupported",
		},
		{
			name: "benchmark has no no_tool",
			spec: with(func(s *Spec) {
				s.Format = FormatMDFence
				s.Transcript = TranscriptBenchmark
				s.Prefill = PrefillFence
				s.Abstain = AbstainNoTool
			}),
			code: "abstain.unsupported",
		},
		{
			name: "repeated calls are benchmark only",
			spec: with(func(s *Spec) {
				s.Format = FormatMDFence
				s.Prefill = PrefillFence
				s.Loop.AllowRepeatedCalls = true
			}),
			code: "loop.allow-repeated",
		},
		{
			name: "benchmark is md only",
			spec: with(func(s *Spec) { s.Transcript = TranscriptBenchmark }),
			code: "transcript.unsupported",
		},
		{
			name: "negative loop field",
			spec: with(func(s *Spec) { s.Loop.MaxSteps = -1 }),
			code: "loop.negative",
		},
		{
			name: "unknown format",
			spec: with(func(s *Spec) { s.Format = "yaml" }),
			code: "format.unknown",
		},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			err := testCase.spec.Validate()
			if err == nil {
				t.Fatalf("Validate succeeded, want %s:\n%s", testCase.code, testCase.spec.Canonical())
			}
			specErr, ok := err.(*SpecError)
			if !ok {
				t.Fatalf("error type %T, want *SpecError", err)
			}
			if specErr.Code != testCase.code {
				t.Fatalf("error code = %q, want %q: %v", specErr.Code, testCase.code, err)
			}
		})
	}
}

func TestCanonicalAndHashAreContentIdentity(t *testing.T) {
	t.Parallel()
	base := Default()
	base.Loop = Loop{MaxSteps: 6, AnswerMaxOutputTokens: 1024}
	same := base
	if !base.Equal(same) || base.Hash() != same.Hash() {
		t.Fatal("identical specs must share canonical and hash")
	}
	changed := base
	changed.Prefill = PrefillFence
	changed.Format = FormatMDFence
	if base.Hash() == changed.Hash() {
		t.Fatal("hash must change when an axis changes")
	}
	if !strings.Contains(base.Canonical(), "format=xml") {
		t.Fatalf("canonical = %s", base.Canonical())
	}
}

func TestShortListsOnlyDeviations(t *testing.T) {
	t.Parallel()
	if got := Default().Short(); got != "default" {
		t.Fatalf("default short = %q", got)
	}
	spec, _, err := Resolve("md-v1")
	if err != nil {
		t.Fatal(err)
	}
	short := spec.Short()
	for _, want := range []string{"md-fence", "deep-fence", "no-tool"} {
		if !strings.Contains(short, want) {
			t.Fatalf("short = %q, missing %q", short, want)
		}
	}
}
