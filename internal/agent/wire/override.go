package wire

import (
	"fmt"
	"sort"
	"strings"
)

// overrideSetters maps the canonical axis names to their setters. The key set
// is exactly the canonical field names, so `--wire format=…,prefill=…` reads
// the same vocabulary that `--explain-profile` prints.
var overrideSetters = map[string]func(*Spec, string){
	"format":     func(s *Spec, v string) { s.Format = Format(v) },
	"transcript": func(s *Spec, v string) { s.Transcript = Transcript(v) },
	"transport":  func(s *Spec, v string) { s.Transport = Transport(v) },
	"thinking":   func(s *Spec, v string) { s.Thinking = Thinking(v) },
	"prefill":    func(s *Spec, v string) { s.Prefill = Prefill(v) },
	"abstain":    func(s *Spec, v string) { s.Abstain = Abstain(v) },
	"terminal":   func(s *Spec, v string) { s.Terminal = Terminal(v) },
	"route":      func(s *Spec, v string) { s.Route = RouteMode(v) },
	"catalog":    func(s *Spec, v string) { s.Catalog = Catalog(v) },
	"control":    func(s *Spec, v string) { s.Control = Control(v) },
	"feedback":   func(s *Spec, v string) { s.Feedback = Feedback(v) },
	"subagent":   func(s *Spec, v string) { s.SubagentFeedback = SubagentFeedback(v) },
	"align":      func(s *Spec, v string) { s.Align = Align(v) },
	"stages":     func(s *Spec, v string) { s.Stages = Stages(v) },
}

// OverrideKeys lists the axes a `--wire` override may set, sorted.
func OverrideKeys() []string {
	keys := make([]string, 0, len(overrideSetters))
	for key := range overrideSetters {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// ParseOverrides decodes a comma-separated `key=value` list. It rejects empty
// entries, missing "=", empty keys/values and duplicate keys so a typo cannot
// silently produce a different run.
func ParseOverrides(value string) (map[string]string, error) {
	overrides := make(map[string]string)
	for _, entry := range strings.Split(value, ",") {
		entry = strings.TrimSpace(entry)
		if entry == "" {
			return nil, fail("override.empty", "empty --wire entry", "use key=value pairs, e.g. format=md-fence,prefill=fence")
		}
		key, raw, ok := strings.Cut(entry, "=")
		key = strings.TrimSpace(key)
		raw = strings.TrimSpace(raw)
		if !ok || key == "" || raw == "" {
			return nil, fail("override.shape", fmt.Sprintf("malformed --wire entry %q", entry), "use key=value")
		}
		if _, duplicate := overrides[key]; duplicate {
			return nil, fail("override.duplicate", fmt.Sprintf("duplicate --wire key %q", key), "")
		}
		if _, known := overrideSetters[key]; !known {
			return nil, fail("override.unknown",
				fmt.Sprintf("unknown --wire key %q", key),
				"valid keys: "+strings.Join(OverrideKeys(), ", "))
		}
		overrides[key] = raw
	}
	return overrides, nil
}

// WithOverrides applies axis overrides onto the spec and validates the result.
// It is the longhand half of the profile model: a preset or suite default is
// the base, and `--wire` spells out only the axes being changed.
func (s Spec) WithOverrides(overrides map[string]string) (Spec, error) {
	result := s
	for key, value := range overrides {
		setter, ok := overrideSetters[key]
		if !ok {
			return Spec{}, fail("override.unknown",
				fmt.Sprintf("unknown wire axis %q", key),
				"valid keys: "+strings.Join(OverrideKeys(), ", "))
		}
		setter(&result, value)
	}
	if err := result.Validate(); err != nil {
		return Spec{}, err
	}
	return result, nil
}
