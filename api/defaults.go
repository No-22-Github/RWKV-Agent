package api

import (
	"github.com/no22/RWKV-Agent/internal/agent/product"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/samplingpreset"
)

// NewConfigProfile is the wire preset a new App connection starts on: the same
// g1k wire the training corpus and the product evaluation use, so what the user
// does in the App is what the model was tuned and measured on. normalizeConfig
// deliberately does NOT default to it: saved connections without a profile keep
// the legacy per-protocol behavior until the user changes them.
const NewConfigProfile = "g1k"

// NewConfigMaxTokens and NewConfigDecisionMaxTokens are a new connection's
// answer and decision budgets.
const (
	NewConfigMaxTokens         = 4096
	NewConfigDecisionMaxTokens = 2048
)

// NewConfigSampling is the sampling preset a new App connection starts on.
const NewConfigSampling = "g1k-agent"

// NewConfigWeatherBackend is the keyless weather backend a new connection uses.
const NewConfigWeatherBackend = assistanttools.WeatherBackendOpenMeteo

// NewConfigDefaults returns the agent-facing defaults of a NEW connection
// (provider, model and endpoint are the caller's). The frontend mirrors these
// values in providerManager.ts (NEW_CONFIG_DEFAULTS); api tests pin both sides
// to the shared product tool set. Saved configurations are never rewritten with
// them.
func NewConfigDefaults() Config {
	set := product.AppDefaultToolSet()
	sampling, _ := samplingpreset.Lookup(NewConfigSampling)
	config := Config{
		AgentProtocol: AgentProtocolXML,
		Profile:       NewConfigProfile,
		Thinking:      "off",
		// g1k thinks before nearly every first step; a 512-token decision
		// budget cuts the thought off. These are the benchmark protocol's
		// budgets (docs/evaluations/benchmark-protocol.md).
		MaxTokens:         NewConfigMaxTokens,
		DecisionMaxTokens: NewConfigDecisionMaxTokens,
		EnableWeb:         set.Web,
		EnableBash:        set.Bash,
		EnableSubagents:   set.Subagents,
		Temperature:       sampling.Temperature,
		TopK:              sampling.TopK,
		TopP:              sampling.TopP,
		PresencePenalty:   sampling.PresencePenalty,
		FrequencyPenalty:  sampling.FrequencyPenalty,
		PenaltyDecay:      sampling.PenaltyDecay,
	}
	if set.Weather {
		config.WeatherBackend = NewConfigWeatherBackend
	}
	return config
}
