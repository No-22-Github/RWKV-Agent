// Package wire defines the canonical, serializable description of everything
// that decides what the model sees and how its tool calls are read back: the
// tool-call format, the thinking prefill, the decision-stage prefill, the
// abstention and termination action space, the routing and catalog shape, the
// control-prompt variant, the result rendering, and the loop policy.
//
// A Spec is pure data with no dependency on internal/agent, so it can be
// hashed, written into eval manifests, and compared across runs. The agent
// package owns the mapping between a Spec and its runtime Options
// (wire_legacy.go); the CLI and eval entry points own how a Spec is selected.
//
// Design rules (see docs/refactor/wire-spec-p0-baseline.md):
//
//  1. A new mechanism is a new value on an existing axis, never a new boolean.
//  2. Axes are closed enums validated in exactly one place: Validate.
//  3. Cross-axis rules live in Validate's table, each with a test.
//  4. Every combination has a canonical string and a content hash.
package wire

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"regexp"
	"strings"
)

// Format is the tool-call wire format.
type Format string

const (
	// FormatXML is the <tool_call>{json}</tool_call> envelope over the RWKV
	// chat transcript.
	FormatXML Format = "xml"
	// FormatMDFence is the fenced-JSON function transcript used to train the
	// G1i checkpoints.
	FormatMDFence Format = "md-fence"
)

// Transcript selects the policy flavor of a wire format. Product transcripts
// answer in ordinary Markdown; benchmark transcripts are submit-terminated and
// carry the trained benchmark framing.
type Transcript string

const (
	TranscriptProduct   Transcript = "product"
	TranscriptBenchmark Transcript = "benchmark"
)

// Transport selects how a tool call reaches the provider.
type Transport string

const (
	// TransportText sends a rendered continuation prompt and parses the text.
	TransportText Transport = "text"
	// TransportNative uses Chat Completions tools/tool_calls. The text
	// transcript still owns the control prompt, the answer stage, and the
	// tool-result rendering.
	TransportNative Transport = "native"
)

// Thinking is the thinking-mode prefill. fast and full withhold the closing
// bytes of the block they open, so they own the assistant opening.
type Thinking string

const (
	ThinkingOff  Thinking = "off"
	ThinkingFast Thinking = "fast"
	ThinkingFull Thinking = "full"
)

// Prefill is the decision-stage assistant-opening prefill. It is a single
// axis on purpose: only one mechanism may own the opening bytes.
type Prefill string

const (
	PrefillNone            Prefill = "none"
	PrefillEnvelope        Prefill = "envelope"
	PrefillFence           Prefill = "fence"
	PrefillDeepFence       Prefill = "deep-fence"
	PrefillFakeThinkHalf   Prefill = "fake-think-half"
	PrefillFakeThinkClosed Prefill = "fake-think-closed"
)

// Abstain is the text-only abstention action offered to the model.
type Abstain string

const (
	AbstainNone               Abstain = "none"
	AbstainNoTool             Abstain = "no-tool"
	AbstainNoToolGateState    Abstain = "no-tool+gate-state"
	AbstainNoToolGateEvidence Abstain = "no-tool+gate-evidence"
)

// Terminal is the turn-ending tool contract.
type Terminal string

const (
	TerminalNone   Terminal = "none"
	TerminalSubmit Terminal = "submit"
)

// RouteMode selects the pre-decision routing stage.
type RouteMode string

const (
	RouteNone           RouteMode = "none"
	RouteRespondInspect RouteMode = "respond-inspect"
	RouteProgressive    RouteMode = "progressive"
)

// Catalog is the tool catalog shape offered to the model.
type Catalog string

const (
	CatalogFull        Catalog = "full"
	CatalogProgressive Catalog = "progressive"
)

// Control is the control-prompt variant.
type Control string

const (
	ControlBase    Control = "base"
	ControlFewShot Control = "fewshot"
)

// Feedback is the tool-result rendering policy.
type Feedback string

const (
	FeedbackRaw           Feedback = "raw"
	FeedbackCompressFetch Feedback = "compress-fetch"
)

// SubagentFeedback is the spawn_agents result rendering policy.
type SubagentFeedback string

const (
	SubagentFeedbackBlock SubagentFeedback = "block"
	SubagentFeedbackRaw   SubagentFeedback = "raw"
)

// Loop is the loop policy. The fallback mechanisms (duplicate replay,
// duplicate rescue, same-tool rescue, answer-stage lead) trigger on these
// counters, so they are part of the reproducible contract.
type Loop struct {
	MaxSteps                 int
	ProtocolRetries          int
	RouteRetries             int
	DecisionMaxOutputTokens  int
	AnswerMaxOutputTokens    int
	RouteMaxOutputTokens     int
	DuplicateReplayLimit     int
	DuplicateRescueThreshold int
	SameToolRescueLimit      int
	AnswerStageLead          int
	// AllowRepeatedCalls preserves the upstream Primitive Bench controller,
	// which executes identical calls repeatedly. Benchmark-only.
	AllowRepeatedCalls bool
}

// Zero reports whether the loop policy is unset.
func (l Loop) Zero() bool { return l == Loop{} }

// Spec is the canonical description of one model-facing wire configuration.
type Spec struct {
	Format           Format
	Transcript       Transcript
	Transport        Transport
	Thinking         Thinking
	Prefill          Prefill
	Abstain          Abstain
	Terminal         Terminal
	Route            RouteMode
	Catalog          Catalog
	Control          Control
	Feedback         Feedback
	SubagentFeedback SubagentFeedback
	Loop             Loop
}

// Default returns the product XML baseline with unset loop policy.
func Default() Spec {
	return Spec{
		Format:           FormatXML,
		Transcript:       TranscriptProduct,
		Transport:        TransportText,
		Thinking:         ThinkingOff,
		Prefill:          PrefillNone,
		Abstain:          AbstainNone,
		Terminal:         TerminalNone,
		Route:            RouteNone,
		Catalog:          CatalogFull,
		Control:          ControlBase,
		Feedback:         FeedbackRaw,
		SubagentFeedback: SubagentFeedbackBlock,
	}
}

// Normalize fills unset axes from base. An all-zero Loop is treated as unset.
func (s Spec) Normalize(base Spec) Spec {
	result := s
	if result.Format == "" {
		result.Format = base.Format
	}
	if result.Transcript == "" {
		result.Transcript = base.Transcript
	}
	if result.Transport == "" {
		result.Transport = base.Transport
	}
	if result.Thinking == "" {
		result.Thinking = base.Thinking
	}
	if result.Prefill == "" {
		result.Prefill = base.Prefill
	}
	if result.Abstain == "" {
		result.Abstain = base.Abstain
	}
	if result.Terminal == "" {
		result.Terminal = base.Terminal
	}
	if result.Route == "" {
		result.Route = base.Route
	}
	if result.Catalog == "" {
		result.Catalog = base.Catalog
	}
	if result.Control == "" {
		result.Control = base.Control
	}
	if result.Feedback == "" {
		result.Feedback = base.Feedback
	}
	if result.SubagentFeedback == "" {
		result.SubagentFeedback = base.SubagentFeedback
	}
	if result.Loop.Zero() {
		result.Loop = base.Loop
	}
	return result
}

// SpecError is a validation failure. Code is stable so callers and tests can
// match on it; Hint names the axis value or the legal alternative.
type SpecError struct {
	Code    string
	Message string
	Hint    string
}

func (e *SpecError) Error() string {
	message := "wire spec[" + e.Code + "]: " + e.Message
	if e.Hint != "" {
		message += " (hint: " + e.Hint + ")"
	}
	return message
}

func fail(code, message, hint string) error {
	return &SpecError{Code: code, Message: message, Hint: hint}
}

// Validate enforces every cross-axis rule. It is the only place these rules
// live; callers must not re-implement them.
func (s Spec) Validate() error {
	if !known(FormatValues, s.Format) {
		return fail("format.unknown", fmt.Sprintf("unknown format %q", s.Format), "xml, md-fence")
	}
	if !known(TranscriptValues, s.Transcript) {
		return fail("transcript.unknown", fmt.Sprintf("unknown transcript %q", s.Transcript), "product, benchmark")
	}
	if !known(TransportValues, s.Transport) {
		return fail("transport.unknown", fmt.Sprintf("unknown transport %q", s.Transport), "text, native")
	}
	if !known(ThinkingValues, s.Thinking) {
		return fail("thinking.unknown", fmt.Sprintf("unknown thinking %q", s.Thinking), "off, fast, full")
	}
	if !known(PrefillValues, s.Prefill) {
		return fail("prefill.unknown", fmt.Sprintf("unknown prefill %q", s.Prefill), PrefillHint)
	}
	if !known(AbstainValues, s.Abstain) {
		return fail("abstain.unknown", fmt.Sprintf("unknown abstain %q", s.Abstain), AbstainHint)
	}
	// The terminal contract names an arbitrary tool ("none" disables it), so it
	// is validated as a tool name rather than against a closed list. "submit"
	// is the benchmark's name for it.
	if s.Terminal == "" {
		return fail("terminal.unknown", "terminal must be none or a tool name", "none, submit, or a tool name")
	}
	if s.Terminal != TerminalNone && !terminalNamePattern.MatchString(string(s.Terminal)) {
		return fail("terminal.unknown", fmt.Sprintf("invalid terminal tool name %q", s.Terminal),
			"none or a 1-64 character tool name")
	}
	if !known(RouteValues, s.Route) {
		return fail("route.unknown", fmt.Sprintf("unknown route %q", s.Route), "none, respond-inspect, progressive")
	}
	if !known(CatalogValues, s.Catalog) {
		return fail("catalog.unknown", fmt.Sprintf("unknown catalog %q", s.Catalog), "full, progressive")
	}
	if !known(ControlValues, s.Control) {
		return fail("control.unknown", fmt.Sprintf("unknown control %q", s.Control), "base, fewshot")
	}
	if !known(FeedbackValues, s.Feedback) {
		return fail("feedback.unknown", fmt.Sprintf("unknown feedback %q", s.Feedback), "raw, compress-fetch")
	}
	if !known(SubagentFeedbackValues, s.SubagentFeedback) {
		return fail("subagent_feedback.unknown", fmt.Sprintf("unknown subagent feedback %q", s.SubagentFeedback), "block, raw")
	}

	// C2: the product fenced transcript has no think slot.
	if s.Format == FormatMDFence && s.Thinking != ThinkingOff {
		return fail("thinking.unsupported", "the md-fence transcript only supports thinking=off",
			"use xml for fast/full thinking, or prefill=fake-think-* for the markdown think experiment")
	}
	// C1: a half-open think block owns the assistant opening.
	if s.Thinking != ThinkingOff && s.Prefill != PrefillNone {
		return fail("prefill.conflict", fmt.Sprintf("thinking=%s already owns the assistant opening, so prefill must be none", s.Thinking),
			"set prefill=none, or thinking=off")
	}
	// C3: the deep anchor removes every syntactic abstention exit.
	if s.Prefill == PrefillDeepFence && s.Abstain == AbstainNone {
		return fail("prefill.requires-abstain", "prefill=deep-fence removes every syntactic abstention exit",
			"pair it with abstain=no-tool (optionally +gate-state/+gate-evidence)")
	}
	// C4: fake-think owns the same slot as the fence anchors and is a product
	// experiment.
	switch s.Prefill {
	case PrefillFakeThinkHalf, PrefillFakeThinkClosed:
		if s.Format != FormatMDFence {
			return fail("prefill.unsupported", fmt.Sprintf("prefill=%s requires format=md-fence", s.Prefill),
				"fake-think is the markdown think experiment; use thinking=fast/full for xml")
		}
		if s.Transcript != TranscriptProduct {
			return fail("prefill.requires-product", fmt.Sprintf("prefill=%s is a product experiment", s.Prefill), "use transcript=product")
		}
	case PrefillDeepFence:
		if s.Format != FormatMDFence {
			return fail("prefill.unsupported", "prefill=deep-fence requires format=md-fence",
				"the xml envelope has no JSON fence to extend")
		}
		if s.Transcript != TranscriptProduct {
			return fail("prefill.requires-product", "prefill=deep-fence is a product experiment", "use transcript=product")
		}
	case PrefillEnvelope:
		if s.Format != FormatXML {
			return fail("prefill.unsupported", "prefill=envelope requires format=xml", "use prefill=fence or prefill=deep-fence")
		}
		if s.Route == RouteNone {
			return fail("prefill.not-wired", "prefill=envelope is only armed by a router in the current runner",
				"set route=respond-inspect or route=progressive (P2 will allow a routerless envelope)")
		}
	case PrefillFence:
		if s.Format != FormatMDFence {
			return fail("prefill.unsupported", "prefill=fence requires format=md-fence", "use prefill=envelope for xml")
		}
	}
	// C6: progressive catalog and progressive route are the same mechanism.
	if (s.Route == RouteProgressive) != (s.Catalog == CatalogProgressive) {
		return fail("route.catalog-mismatch",
			fmt.Sprintf("route=%s and catalog=%s must be selected together", s.Route, s.Catalog),
			"the progressive catalog is installed by the progressive router")
	}
	// C7: the native transport clears the assistant prefix whenever tools are
	// offered, so a decision prefill has no effect.
	if s.Transport == TransportNative && s.Prefill != PrefillNone {
		return fail("transport.prefill", "native tool calling offers no assistant prefill when tools are present",
			"set prefill=none")
	}
	if s.Control == ControlFewShot && s.Format != FormatXML {
		return fail("control.unsupported", "control=fewshot requires format=xml", "use control=base")
	}
	// The no_tool pseudo-action is only offered by the product transcripts.
	if s.Abstain != AbstainNone && s.Transcript != TranscriptProduct {
		return fail("abstain.unsupported", fmt.Sprintf("abstain=%s requires transcript=product", s.Abstain),
			"benchmark transcripts terminate through submit instead")
	}
	// Repeated identical calls are an upstream Primitive Bench controller
	// behaviour, not a product one.
	if s.Loop.AllowRepeatedCalls && s.Transcript != TranscriptBenchmark {
		return fail("loop.allow-repeated", "loop.AllowRepeatedCalls is benchmark-only",
			"use transcript=benchmark")
	}
	if s.Transcript == TranscriptBenchmark && s.Format != FormatMDFence {
		return fail("transcript.unsupported", "transcript=benchmark requires format=md-fence",
			"benchmark transcripts are the trained fenced-JSON transcript")
	}
	for name, value := range map[string]int{
		"MaxSteps":                 s.Loop.MaxSteps,
		"ProtocolRetries":          s.Loop.ProtocolRetries,
		"RouteRetries":             s.Loop.RouteRetries,
		"DecisionMaxOutputTokens":  s.Loop.DecisionMaxOutputTokens,
		"AnswerMaxOutputTokens":    s.Loop.AnswerMaxOutputTokens,
		"RouteMaxOutputTokens":     s.Loop.RouteMaxOutputTokens,
		"DuplicateReplayLimit":     s.Loop.DuplicateReplayLimit,
		"DuplicateRescueThreshold": s.Loop.DuplicateRescueThreshold,
		"SameToolRescueLimit":      s.Loop.SameToolRescueLimit,
		"AnswerStageLead":          s.Loop.AnswerStageLead,
	} {
		if value < 0 {
			return fail("loop.negative", fmt.Sprintf("loop.%s cannot be negative", name), "")
		}
	}
	return nil
}

// Canonical renders every axis in a fixed order. Two specs are the same
// configuration if and only if their canonical strings are equal.
func (s Spec) Canonical() string {
	loop := s.Loop
	return fmt.Sprintf(
		"format=%s;transcript=%s;transport=%s;thinking=%s;prefill=%s;abstain=%s;terminal=%s;"+
			"route=%s;catalog=%s;control=%s;feedback=%s;subagent=%s;"+
			"loop=%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%t",
		s.Format, s.Transcript, s.Transport, s.Thinking, s.Prefill, s.Abstain, s.Terminal,
		s.Route, s.Catalog, s.Control, s.Feedback, s.SubagentFeedback,
		loop.MaxSteps, loop.ProtocolRetries, loop.RouteRetries,
		loop.DecisionMaxOutputTokens, loop.AnswerMaxOutputTokens, loop.RouteMaxOutputTokens,
		loop.DuplicateReplayLimit, loop.DuplicateRescueThreshold, loop.SameToolRescueLimit,
		loop.AnswerStageLead, loop.AllowRepeatedCalls,
	)
}

// Hash is the content identity of the spec, used by eval manifests.
func (s Spec) Hash() string {
	sum := sha256.Sum256([]byte(s.Canonical()))
	return hex.EncodeToString(sum[:])
}

// Equal compares canonical content.
func (s Spec) Equal(other Spec) bool { return s.Canonical() == other.Canonical() }

// Short renders only the axes that differ from Default, joined with "+". It is
// the pasteable shorthand for an ad-hoc configuration; a registered preset
// name is preferred when one exists.
func (s Spec) Short() string {
	base := Default()
	parts := make([]string, 0, 8)
	add := func(condition bool, value string) {
		if condition {
			parts = append(parts, value)
		}
	}
	add(s.Format != base.Format, string(s.Format))
	add(s.Transcript != base.Transcript, string(s.Transcript))
	add(s.Transport != base.Transport, string(s.Transport))
	add(s.Thinking != base.Thinking, "think-"+string(s.Thinking))
	add(s.Prefill != base.Prefill, string(s.Prefill))
	add(s.Abstain != base.Abstain, string(s.Abstain))
	add(s.Terminal != base.Terminal, string(s.Terminal))
	add(s.Route != base.Route, "route-"+string(s.Route))
	add(s.Catalog != base.Catalog, string(s.Catalog))
	add(s.Control != base.Control, string(s.Control))
	add(s.Feedback != base.Feedback, string(s.Feedback))
	add(s.SubagentFeedback != base.SubagentFeedback, string(s.SubagentFeedback))
	if !s.Loop.Zero() {
		parts = append(parts, "loop")
	}
	if len(parts) == 0 {
		return "default"
	}
	return strings.Join(parts, "+")
}

// Value lists used by Validate and by the CLI help. They are exported so the
// CLI can print the legal domain without duplicating it.
var (
	FormatValues     = []string{string(FormatXML), string(FormatMDFence)}
	TranscriptValues = []string{string(TranscriptProduct), string(TranscriptBenchmark)}
	TransportValues  = []string{string(TransportText), string(TransportNative)}
	ThinkingValues   = []string{string(ThinkingOff), string(ThinkingFast), string(ThinkingFull)}
	PrefillValues    = []string{
		string(PrefillNone), string(PrefillEnvelope), string(PrefillFence),
		string(PrefillDeepFence), string(PrefillFakeThinkHalf), string(PrefillFakeThinkClosed),
	}
	AbstainValues = []string{
		string(AbstainNone), string(AbstainNoTool),
		string(AbstainNoToolGateState), string(AbstainNoToolGateEvidence),
	}
	TerminalValues         = []string{string(TerminalNone), string(TerminalSubmit)}
	RouteValues            = []string{string(RouteNone), string(RouteRespondInspect), string(RouteProgressive)}
	CatalogValues          = []string{string(CatalogFull), string(CatalogProgressive)}
	ControlValues          = []string{string(ControlBase), string(ControlFewShot)}
	FeedbackValues         = []string{string(FeedbackRaw), string(FeedbackCompressFetch)}
	SubagentFeedbackValues = []string{string(SubagentFeedbackBlock), string(SubagentFeedbackRaw)}
)

const (
	PrefillHint = "none, envelope, fence, deep-fence, fake-think-half, fake-think-closed"
	AbstainHint = "none, no-tool, no-tool+gate-state, no-tool+gate-evidence"
)

// terminalNamePattern matches the tool names a terminal contract may name.
var terminalNamePattern = regexp.MustCompile(`^[A-Za-z0-9_-]{1,64}$`)

func known[T ~string](values []string, value T) bool {
	for _, candidate := range values {
		if candidate == string(value) {
			return true
		}
	}
	return false
}
