package wire

import (
	"fmt"
	"sort"
	"strings"
)

// Presets are named, registered points in the Spec space. A preset is only a
// shortcut: the CLI accepts the same configuration as longhand axes, and the
// two produce the identical canonical string and hash.
var presets = map[string]Spec{}

// Register adds a named preset. It panics on a duplicate or invalid spec so a
// programming error fails at init, not at run time.
func Register(name string, spec Spec) {
	if _, exists := presets[name]; exists {
		panic("wire: duplicate preset " + name)
	}
	if err := spec.Validate(); err != nil {
		panic("wire: preset " + name + ": " + err.Error())
	}
	presets[name] = spec
}

// Lookup returns the registered preset, if any.
func Lookup(name string) (Spec, bool) {
	spec, ok := presets[name]
	return spec, ok
}

// Names lists registered presets in sorted order.
func Names() []string {
	names := make([]string, 0, len(presets))
	for name := range presets {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// MatchPreset reports the registered preset whose axes equal this spec. The
// loop policy is excluded: presets carry a zero loop and the entry point
// supplies the concrete limits, so a run with real step budgets still matches
// the preset it started from. When several presets share the same axes (for
// example "default" and "xml-v1"), the non-default name is preferred so the
// reported identity is the informative one. An empty name means the spec is an
// ad-hoc combination: it stays fully traceable through Canonical/Hash.
func (s Spec) MatchPreset() (string, bool) {
	candidate := s
	candidate.Loop = Loop{}
	canonical := candidate.Canonical()
	match := ""
	for _, name := range Names() {
		preset, _ := Lookup(name)
		if preset.Canonical() != canonical {
			continue
		}
		if match == "" || match == "default" {
			match = name
		}
	}
	return match, match != ""
}

// Resolve accepts three spellings and returns the spec plus the registered
// preset name when one matched (empty for an ad-hoc configuration):
//
//  1. a registered preset name: "md-v1"
//  2. a preset plus modifiers: "md-v1+anchor+no-tool"
//  3. a canonical string: "format=xml;...;loop=..."
//
// The returned spec is validated.
func Resolve(value string) (Spec, string, error) {
	candidate := strings.TrimSpace(value)
	if candidate == "" {
		return Spec{}, "", fail("resolve.empty", "empty wire spec", "use a preset name, preset+modifiers, or a canonical string")
	}
	if spec, ok := Lookup(candidate); ok {
		return spec, candidate, nil
	}
	if strings.Contains(candidate, "=") {
		spec, err := parseCanonical(candidate)
		if err != nil {
			return Spec{}, "", err
		}
		return spec, "", nil
	}
	parts := strings.Split(candidate, "+")
	base, ok := Lookup(parts[0])
	if !ok {
		return Spec{}, "", fail("resolve.unknown-preset",
			fmt.Sprintf("unknown wire preset %q", parts[0]),
			"known presets: "+strings.Join(Names(), ", "))
	}
	spec := base
	for _, modifier := range parts[1:] {
		apply, ok := modifiers[modifier]
		if !ok {
			return Spec{}, "", fail("resolve.unknown-modifier",
				fmt.Sprintf("unknown wire modifier %q", modifier),
				"known modifiers: "+strings.Join(ModifierNames(), ", "))
		}
		spec = apply(spec)
	}
	if err := spec.Validate(); err != nil {
		return Spec{}, "", err
	}
	return spec, "", nil
}

// ModifierNames lists the accepted modifiers in sorted order.
func ModifierNames() []string {
	names := make([]string, 0, len(modifiers))
	for name := range modifiers {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// modifiers are the free-composition tokens accepted after a preset name.
var modifiers = map[string]func(Spec) Spec{
	"think-off":  func(s Spec) Spec { s.Thinking = ThinkingOff; return s },
	"think-fast": func(s Spec) Spec { s.Thinking = ThinkingFast; s.Prefill = PrefillNone; return s },
	"think-full": func(s Spec) Spec { s.Thinking = ThinkingFull; s.Prefill = PrefillNone; return s },

	"prefill-none":      func(s Spec) Spec { s.Prefill = PrefillNone; return s },
	"envelope":          func(s Spec) Spec { s.Prefill = PrefillEnvelope; s.Route = RouteRespondInspect; return s },
	"fence":             func(s Spec) Spec { s.Prefill = PrefillFence; return s },
	"deep-fence":        func(s Spec) Spec { s.Prefill = PrefillDeepFence; return s },
	"anchor":            func(s Spec) Spec { s.Prefill = PrefillDeepFence; return s },
	"fake-think":        func(s Spec) Spec { s.Prefill = PrefillFakeThinkHalf; return s },
	"fake-think-closed": func(s Spec) Spec { s.Prefill = PrefillFakeThinkClosed; return s },

	"no-tool":       func(s Spec) Spec { s.Abstain = AbstainNoTool; return s },
	"gate-state":    func(s Spec) Spec { s.Abstain = AbstainNoToolGateState; return s },
	"gate-evidence": func(s Spec) Spec { s.Abstain = AbstainNoToolGateEvidence; return s },

	"submit": func(s Spec) Spec { s.Terminal = TerminalSubmit; return s },

	"route-respond": func(s Spec) Spec { s.Route = RouteRespondInspect; return s },
	"route-progressive": func(s Spec) Spec {
		s.Route = RouteProgressive
		s.Catalog = CatalogProgressive
		if s.Format == FormatXML {
			// Both routers arm the envelope prefix on an inspect decision.
			s.Prefill = PrefillEnvelope
		}
		return s
	},
	"progressive": func(s Spec) Spec {
		s.Route = RouteProgressive
		s.Catalog = CatalogProgressive
		if s.Format == FormatXML {
			s.Prefill = PrefillEnvelope
		}
		return s
	},

	"fewshot": func(s Spec) Spec { s.Control = ControlFewShot; return s },
	"native":  func(s Spec) Spec { s.Transport = TransportNative; s.Prefill = PrefillNone; return s },

	"align-qwen36": func(s Spec) Spec { s.Align = AlignQwen36; return s },
	"align-legacy": func(s Spec) Spec { s.Align = AlignLegacy; return s },

	"compress-fetch": func(s Spec) Spec { s.Feedback = FeedbackCompressFetch; return s },
	"raw-subagent":   func(s Spec) Spec { s.SubagentFeedback = SubagentFeedbackRaw; return s },
}

func init() {
	Register("default", Default())
	Register("xml-v1", Default())

	xmlRoute := Default()
	xmlRoute.Route = RouteRespondInspect
	xmlRoute.Prefill = PrefillEnvelope
	Register("xml-route-v1", xmlRoute)

	xmlProgressive := Default()
	xmlProgressive.Route = RouteProgressive
	xmlProgressive.Catalog = CatalogProgressive
	Register("xml-progressive-v1", xmlProgressive)

	md := Default()
	md.Format = FormatMDFence
	md.Prefill = PrefillDeepFence
	md.Abstain = AbstainNoTool
	Register("md-v1", md)

	mdShallow := md
	mdShallow.Prefill = PrefillFence
	Register("md-fence-v1", mdShallow)

	mdFakeThink := md
	mdFakeThink.Prefill = PrefillFakeThinkHalf
	Register("md-fakethink-v1", mdFakeThink)

	primitive := Default()
	primitive.Format = FormatMDFence
	primitive.Transcript = TranscriptBenchmark
	primitive.Prefill = PrefillFence
	primitive.Terminal = TerminalSubmit
	Register("primitive-v1", primitive)

	bfclMD := md
	bfclMD.Route = RouteProgressive
	bfclMD.Catalog = CatalogProgressive
	Register("bfcl-md-v1", bfclMD)

	bfclXML := Default()
	bfclXML.Route = RouteProgressive
	bfclXML.Catalog = CatalogProgressive
	Register("bfcl-xml-v1", bfclXML)

	native := Default()
	native.Transport = TransportNative
	Register("native-v1", native)
}

// parseCanonical decodes the exact string produced by Spec.Canonical. It is
// deliberately strict: a hand-written string must use the canonical field
// order and names, so a typo cannot silently produce a different run.
func parseCanonical(value string) (Spec, error) {
	spec := Spec{}
	fields := strings.Split(value, ";")
	if len(fields) != 14 {
		return Spec{}, fail("resolve.canonical-fields",
			fmt.Sprintf("canonical spec has %d fields, want 14", len(fields)),
			"copy the string printed by `eval explain`")
	}
	seen := map[string]bool{}
	for _, field := range fields {
		key, raw, ok := strings.Cut(field, "=")
		if !ok {
			return Spec{}, fail("resolve.canonical-shape", fmt.Sprintf("malformed field %q", field), "")
		}
		if seen[key] {
			return Spec{}, fail("resolve.canonical-duplicate", fmt.Sprintf("duplicate field %q", key), "")
		}
		seen[key] = true
		switch key {
		case "format":
			spec.Format = Format(raw)
		case "transcript":
			spec.Transcript = Transcript(raw)
		case "transport":
			spec.Transport = Transport(raw)
		case "thinking":
			spec.Thinking = Thinking(raw)
		case "prefill":
			spec.Prefill = Prefill(raw)
		case "abstain":
			spec.Abstain = Abstain(raw)
		case "terminal":
			spec.Terminal = Terminal(raw)
		case "route":
			spec.Route = RouteMode(raw)
		case "catalog":
			spec.Catalog = Catalog(raw)
		case "control":
			spec.Control = Control(raw)
		case "feedback":
			spec.Feedback = Feedback(raw)
		case "subagent":
			spec.SubagentFeedback = SubagentFeedback(raw)
		case "align":
			spec.Align = Align(raw)
		case "loop":
			loop, err := parseLoop(raw)
			if err != nil {
				return Spec{}, err
			}
			spec.Loop = loop
		default:
			return Spec{}, fail("resolve.canonical-unknown", fmt.Sprintf("unknown field %q", key), "")
		}
	}
	if err := spec.Validate(); err != nil {
		return Spec{}, err
	}
	return spec, nil
}

func parseLoop(value string) (Loop, error) {
	parts := strings.Split(value, ",")
	if len(parts) != 11 {
		return Loop{}, fail("resolve.loop-fields",
			fmt.Sprintf("canonical loop has %d fields, want 11", len(parts)), "")
	}
	numbers := make([]int, 10)
	for index, part := range parts[:10] {
		parsed, err := parseInt(part)
		if err != nil {
			return Loop{}, fail("resolve.loop-number", fmt.Sprintf("loop field %d is not an integer: %q", index, part), "")
		}
		numbers[index] = parsed
	}
	allowRepeated, ok := parseBool(parts[10])
	if !ok {
		return Loop{}, fail("resolve.loop-bool", fmt.Sprintf("loop field 11 is not a bool: %q", parts[10]), "")
	}
	return Loop{
		MaxSteps:                 numbers[0],
		ProtocolRetries:          numbers[1],
		RouteRetries:             numbers[2],
		DecisionMaxOutputTokens:  numbers[3],
		AnswerMaxOutputTokens:    numbers[4],
		RouteMaxOutputTokens:     numbers[5],
		DuplicateReplayLimit:     numbers[6],
		DuplicateRescueThreshold: numbers[7],
		SameToolRescueLimit:      numbers[8],
		AnswerStageLead:          numbers[9],
		AllowRepeatedCalls:       allowRepeated,
	}, nil
}

func parseInt(value string) (int, error) {
	var result int
	if _, err := fmt.Sscanf(value, "%d", &result); err != nil {
		return 0, err
	}
	return result, nil
}

func parseBool(value string) (bool, bool) {
	switch value {
	case "true":
		return true, true
	case "false":
		return false, true
	default:
		return false, false
	}
}
