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

// TestFirstCallAxis locks the native first-step tool_choice axis: it rides the
// canonical string and hash like every other axis, resolves as a modifier,
// and round-trips through the canonical spelling.
func TestFirstCallAxis(t *testing.T) {
	t.Parallel()
	base := Default()
	if base.FirstCall != FirstCallRequired {
		t.Fatalf("default firstcall = %q, want required", base.FirstCall)
	}
	if !strings.HasSuffix(base.Canonical(), ";firstcall=required;usermsg=split;srchint=off") {
		t.Fatalf("canonical = %q, want the firstcall, usermsg and srchint axes last", base.Canonical())
	}
	auto := base
	auto.FirstCall = FirstCallAuto
	if auto.Hash() == base.Hash() {
		t.Fatal("hash must change when firstcall changes")
	}
	parsed, _, err := Resolve(auto.Canonical())
	if err != nil {
		t.Fatalf("Resolve(canonical with firstcall): %v", err)
	}
	if !parsed.Equal(auto) {
		t.Fatalf("canonical round trip drifted:\nwant %s\n got %s", auto.Canonical(), parsed.Canonical())
	}
	resolved, _, err := Resolve("xml-v1+first-auto")
	if err != nil {
		t.Fatalf("Resolve(xml-v1+first-auto): %v", err)
	}
	if resolved.FirstCall != FirstCallAuto {
		t.Fatalf("first-auto modifier firstcall = %q", resolved.FirstCall)
	}
	if short := auto.Short(); !strings.Contains(short, "first-auto") {
		t.Fatalf("short = %q, missing first-auto", short)
	}
	unknown := base
	unknown.FirstCall = "force"
	err = unknown.Validate()
	if err == nil {
		t.Fatal("unknown firstcall value accepted")
	}
	if specErr, ok := err.(*SpecError); !ok || specErr.Code != "firstcall.unknown" {
		t.Fatalf("Validate error = %v, want code firstcall.unknown", err)
	}
}

// TestSourceHintAxis locks the control-prompt information-source sentence:
// off by default (byte-identical control prompt), rides the canonical string
// and hash, and resolves through the src-hint modifier.
func TestSourceHintAxis(t *testing.T) {
	t.Parallel()
	base := Default()
	if base.SourceHint != SourceHintOff {
		t.Fatalf("default srchint = %q, want off", base.SourceHint)
	}
	if !strings.HasSuffix(base.Canonical(), ";firstcall=required;usermsg=split;srchint=off") {
		t.Fatalf("canonical = %q, want the srchint axis last", base.Canonical())
	}
	on := base
	on.SourceHint = SourceHintOn
	if on.Hash() == base.Hash() {
		t.Fatal("hash must change when srchint changes")
	}
	parsed, _, err := Resolve(on.Canonical())
	if err != nil {
		t.Fatalf("Resolve(canonical with srchint): %v", err)
	}
	if !parsed.Equal(on) {
		t.Fatalf("canonical round trip drifted:\nwant %s\n got %s", on.Canonical(), parsed.Canonical())
	}
	resolved, _, err := Resolve("xml-v1+src-hint")
	if err != nil {
		t.Fatalf("Resolve(xml-v1+src-hint): %v", err)
	}
	if resolved.SourceHint != SourceHintOn {
		t.Fatalf("src-hint modifier srchint = %q", resolved.SourceHint)
	}
	if short := on.Short(); !strings.Contains(short, "src-hint") {
		t.Fatalf("short = %q, missing src-hint", short)
	}
	unknown := base
	unknown.SourceHint = "sometimes"
	err = unknown.Validate()
	if err == nil {
		t.Fatal("unknown srchint value accepted")
	}
	if specErr, ok := err.(*SpecError); !ok || specErr.Code != "srchint.unknown" {
		t.Fatalf("Validate error = %v, want code srchint.unknown", err)
	}
}

// TestUserMergeAxis locks the transcript-structure variants: they ride the
// canonical string and hash, resolve as modifiers, and are gated to the
// qwen36 product XML transcript (rewrite additionally to the one-stage
// contract) because the merge semantics are defined for tool results riding
// in user turns.
func TestUserMergeAxis(t *testing.T) {
	t.Parallel()
	base := Default()
	if base.UserMerge != UserMergeSplit {
		t.Fatalf("default usermsg = %q, want split", base.UserMerge)
	}
	g1k, _, err := Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage")
	if err != nil {
		t.Fatal(err)
	}
	for _, testCase := range []struct {
		modifier string
		want     UserMerge
	}{
		{"merge-users", UserMergeMerged},
		{"merge-users-no-nudge", UserMergeNoNudge},
		{"merge-users-rewrite", UserMergeRewrite},
	} {
		spec, _, err := Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage+" + testCase.modifier)
		if err != nil {
			t.Fatalf("Resolve(%s): %v", testCase.modifier, err)
		}
		if spec.UserMerge != testCase.want {
			t.Fatalf("%s usermsg = %q, want %q", testCase.modifier, spec.UserMerge, testCase.want)
		}
		parsed, _, err := Resolve(spec.Canonical())
		if err != nil {
			t.Fatalf("Resolve(canonical of %s): %v", testCase.modifier, err)
		}
		if !parsed.Equal(spec) {
			t.Fatalf("canonical round trip of %s drifted:\nwant %s\n got %s",
				testCase.modifier, spec.Canonical(), parsed.Canonical())
		}
	}
	if g1k.Hash() == Default().Hash() {
		t.Fatal("hash must change when an axis changes")
	}
	merged := g1k
	merged.UserMerge = UserMergeMerged
	if merged.Hash() == g1k.Hash() {
		t.Fatal("hash must change when usermsg changes")
	}
	if short := merged.Short(); !strings.Contains(short, "merge-users") {
		t.Fatalf("short = %q, missing merge-users", short)
	}

	// Cross-axis gates.
	noAlign := g1k
	noAlign.Align = AlignLegacy
	noAlign.UserMerge = UserMergeMerged
	assertSpecError(t, noAlign, "usermsg.unsupported")
	md := g1k
	md.Format = FormatMDFence
	md.UserMerge = UserMergeMerged
	assertSpecError(t, md, "usermsg.unsupported")
	benchmark := g1k
	benchmark.Transcript = TranscriptBenchmark
	benchmark.UserMerge = UserMergeMerged
	assertSpecError(t, benchmark, "usermsg.unsupported")
	twoStage := g1k
	twoStage.Stages = StagesTwo
	twoStage.UserMerge = UserMergeRewrite
	assertSpecError(t, twoStage, "usermsg.unsupported")
	unknown := g1k
	unknown.UserMerge = "smush"
	assertSpecError(t, unknown, "usermsg.unknown")
}

func assertSpecError(t *testing.T, spec Spec, code string) {
	t.Helper()
	err := spec.Validate()
	if err == nil {
		t.Fatalf("Validate succeeded, want %s:\n%s", code, spec.Canonical())
	}
	specErr, ok := err.(*SpecError)
	if !ok || specErr.Code != code {
		t.Fatalf("Validate error = %v, want code %s", err, code)
	}
}

// TestG1KPresetIsTheLockedLonghand pins the short name to the longhand the
// 2026-09-15 ablation selected, so the two spellings stay one wire and a run
// started from the longhand still reports itself as g1k.
func TestG1KPresetIsTheLockedLonghand(t *testing.T) {
	t.Parallel()
	preset, name, err := Resolve("g1k")
	if err != nil || name != "g1k" {
		t.Fatalf("Resolve(g1k) = %q, %v", name, err)
	}
	longhand, _, err := Resolve("xml-v1+align-qwen36+no-tool+bare+one-stage")
	if err != nil {
		t.Fatal(err)
	}
	if !preset.Equal(longhand) {
		t.Fatalf("g1k = %s\nlonghand = %s", preset.Canonical(), longhand.Canonical())
	}
	if match, ok := longhand.MatchPreset(); !ok || match != "g1k" {
		t.Fatalf("longhand MatchPreset = %q, %v; want g1k", match, ok)
	}
}

// TestMatchPresetIgnoresInertFirstCall: firstcall only reaches a native tool
// completer, so a text-transport bank run with firstcall=auto is still g1k,
// while the same deviation on the native transport stays ad-hoc.
func TestMatchPresetIgnoresInertFirstCall(t *testing.T) {
	t.Parallel()
	text, _, err := Resolve("g1k+first-auto")
	if err != nil {
		t.Fatal(err)
	}
	if match, ok := text.MatchPreset(); !ok || match != "g1k" {
		t.Fatalf("text g1k+first-auto MatchPreset = %q, %v; want g1k", match, ok)
	}
	native, _, err := Resolve("native-v1+first-auto")
	if err != nil {
		t.Fatal(err)
	}
	if match, ok := native.MatchPreset(); ok {
		t.Fatalf("native first-auto matched preset %q; the axis is live there", match)
	}
}
