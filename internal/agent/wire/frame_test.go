package wire

import "testing"

func TestDecisionFramePolicy(t *testing.T) {
	t.Parallel()
	product := func(prefill Prefill) Spec {
		spec := Default()
		spec.Format = FormatMDFence
		spec.Prefill = prefill
		spec.Abstain = AbstainNoTool
		return spec
	}
	benchmark := func() Spec {
		spec := Default()
		spec.Format = FormatMDFence
		spec.Transcript = TranscriptBenchmark
		spec.Prefill = PrefillFence
		spec.Terminal = TerminalSubmit
		return spec
	}
	first := DecisionState{Inspect: true}
	afterTool := DecisionState{Inspect: true, AfterTool: true}
	afterTerminal := DecisionState{Inspect: true, AfterTool: true, TerminalComplete: true}
	respond := DecisionState{Inspect: false}

	cases := []struct {
		name  string
		spec  Spec
		state DecisionState
		want  Frame
	}{
		{
			name:  "envelope arms on the first inspect decision",
			spec:  func() Spec { s := Default(); s.Prefill = PrefillEnvelope; s.Route = RouteRespondInspect; return s }(),
			state: first,
			want:  Frame{Text: EnvelopePrefix, Inject: true},
		},
		{
			name:  "envelope re-arms while the terminal tool is open",
			spec:  func() Spec { s := Default(); s.Prefill = PrefillEnvelope; s.Route = RouteRespondInspect; return s }(),
			state: afterTool,
			want:  Frame{Text: EnvelopePrefix, Inject: true},
		},
		{
			name:  "anchor stands down once the terminal tool completed",
			spec:  product(PrefillDeepFence),
			state: afterTerminal,
			want:  Frame{},
		},
		{
			name:  "deep anchor bytes are the compact measured form",
			spec:  product(PrefillDeepFence),
			state: first,
			want:  Frame{Text: DeepFencePrefix, Inject: true},
		},
		{
			name:  "fake-think owns every decision step",
			spec:  product(PrefillFakeThinkHalf),
			state: afterTerminal,
			want: Frame{
				Text:   FakeThinkHalfPrefix,
				Inject: true,
				Strip:  FakeThinkHalfPrefix + ">",
			},
		},
		{
			name:  "closed fake-think strips the whole block",
			spec:  product(PrefillFakeThinkClosed),
			state: first,
			want: Frame{
				Text:   FakeThinkClosedPrefix,
				Inject: true,
				Strip:  FakeThinkClosedPrefix,
			},
		},
		{
			name:  "respond route never pre-fills a tool format",
			spec:  product(PrefillDeepFence),
			state: respond,
			want:  Frame{},
		},
		{
			name:  "benchmark renderer owns the fence",
			spec:  benchmark(),
			state: first,
			want:  Frame{},
		},
		{
			name:  "prefill none arms nothing",
			spec:  Default(),
			state: first,
			want:  Frame{},
		},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			got := testCase.spec.DecisionFrame(testCase.state)
			if got != testCase.want {
				t.Fatalf("DecisionFrame = %+v, want %+v", got, testCase.want)
			}
		})
	}
}
