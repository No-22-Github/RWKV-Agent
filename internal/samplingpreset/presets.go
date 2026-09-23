// Package samplingpreset names the sampling configurations measured for RWKV
// Agent work, so a run can say "g1k-agent" instead of six numbers that are easy
// to get wrong (a top_k of 1 silently disables temperature, for example).
//
// There is no single best preset: each one is the measured winner for a kind
// of task. The numbers come from the 2026-09-23 g1k sampling sweep
// (docs/evaluations/g1k-sampling-sweep-20260923/); changing one is a new
// measurement, not a tweak.
package samplingpreset

import (
	"math"
	"sort"
	"strings"
)

// Preset is one named sampling configuration.
type Preset struct {
	Name             string
	Temperature      float64
	TopK             int
	TopP             float64
	PresencePenalty  float64
	FrequencyPenalty float64
	PenaltyDecay     float64
	// Use says which task the preset was measured for.
	Use string
}

// NoTruncation is the top_k that keeps every candidate. The CLI rejects 0, so
// "no top-k cutoff" is spelled as the RWKV World vocabulary size.
const NoTruncation = 65536

var presets = map[string]Preset{
	"greedy": {
		Name: "greedy", Temperature: 1, TopK: 1, TopP: 1, PenaltyDecay: 1,
		Use: "regression and debugging; closest to reproducible (batching still moves about ±1 case)",
	},
	"g1k-agent": {
		Name: "g1k-agent", Temperature: 0.3, TopK: NoTruncation, TopP: 0.5, PenaltyDecay: 1,
		Use: "default for tool-calling decisions; best bfcl-product (mean 48/60)",
	},
	"g1k-agent-fast": {
		Name: "g1k-agent-fast", Temperature: 0.3, TopK: NoTruncation, TopP: 0.5,
		PresencePenalty: 0.5, FrequencyPenalty: 0.1, PenaltyDecay: 0.996,
		Use: "long multi-step agent tasks; same score band as g1k-agent, ~27% faster (a light penalty curbs loops; presence 1.0 already costs score)",
	},
	"g1k-stable": {
		Name: "g1k-stable", Temperature: 1, TopK: 20, TopP: 0.3, PenaltyDecay: 1,
		Use: "A/B comparisons with few replicas; smallest run-to-run spread",
	},
	"backend": {
		Name: "backend", Temperature: 1, TopK: 20, TopP: 0.3,
		PresencePenalty: 2, FrequencyPenalty: 0.2, PenaltyDecay: 0.996,
		Use: "rwkv_lightning's own defaults; chat and the fastest runs (heavy penalty halves output length)",
	},
}

// Lookup returns the named preset.
func Lookup(name string) (Preset, bool) {
	preset, ok := presets[strings.TrimSpace(name)]
	return preset, ok
}

// Names lists the presets in sorted order.
func Names() []string {
	names := make([]string, 0, len(presets))
	for name := range presets {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

// Match reports the preset whose values equal the given sampling, so a run
// records the preset it actually used even when the values were typed out, and
// a preset with one value overridden is no longer reported as that preset.
// Fields listed in ignore (for example top_k on a provider that drops it) are
// not compared.
func Match(temperature float64, topK int, topP, presence, frequency, decay float64, ignore ...string) string {
	skip := map[string]bool{}
	for _, key := range ignore {
		skip[key] = true
	}
	for _, name := range Names() {
		preset := presets[name]
		if near(preset.Temperature, temperature) &&
			(skip["top_k"] || preset.TopK == topK) &&
			near(preset.TopP, topP) &&
			near(preset.PresencePenalty, presence) &&
			near(preset.FrequencyPenalty, frequency) &&
			(skip["penalty_decay"] || near(preset.PenaltyDecay, decay)) {
			return name
		}
	}
	return ""
}

func near(a, b float64) bool { return math.Abs(a-b) < 1e-4 }
