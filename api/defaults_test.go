package api

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/samplingpreset"
)

// newConnection is what the App creates for a brand-new remote connection: the
// shared defaults plus the caller's provider fields.
func newConnection() Config {
	config := NewConfigDefaults()
	config.Provider, config.Model, config.Endpoint = ProviderRWKVLightningCUDA, "model", "https://example.test"
	return config
}

// TestNewConfigDefaultsRunOnTheMeasuredWire locks the goal of the shared
// assembly: a new App connection resolves to the agent-wire-v1.0 preset (the
// corpus and evaluation wire, called g1k before 2026-10-21), the agent-default
// sampling preset and the product loop-policy limits 2/3/3, and the combination
// is accepted by normalizeConfig.
func TestNewConfigDefaultsRunOnTheMeasuredWire(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(newConnection())
	if err != nil {
		t.Fatalf("new connection defaults rejected: %v", err)
	}
	options := sessionRunnerOptions(config, Status{Model: "model"}, t.TempDir(), nil, config.AgentProtocol != AgentProtocolXML, true)
	spec, err := agent.WireSpecOf(options)
	if err != nil {
		t.Fatal(err)
	}
	if preset, ok := spec.MatchPreset(); !ok || preset != wire.AgentWireV1 {
		t.Fatalf("wire preset = %q (%v), want %s; canonical %s", preset, ok, wire.AgentWireV1, spec.Canonical())
	}
	if options.DuplicateReplayLimit != 2 || options.DuplicateRescueThreshold != 3 || options.SameToolRescueLimit != 3 {
		t.Fatalf("loop limits = %d/%d/%d, want 2/3/3",
			options.DuplicateReplayLimit, options.DuplicateRescueThreshold, options.SameToolRescueLimit)
	}
	if got := samplingpreset.Match(config.Temperature, config.TopK, config.TopP,
		config.PresencePenalty, config.FrequencyPenalty, config.PenaltyDecay); got != samplingpreset.AgentDefault {
		t.Fatalf("sampling preset = %q, want %s", got, samplingpreset.AgentDefault)
	}
	if !config.EnableWeb || !config.EnableBash || config.WeatherBackend != "open-meteo" || config.EnableSubagents {
		t.Fatalf("tool switches = %+v", config)
	}
}

// TestLegacyConfigsAreNotRewritten: a saved connection without a profile keeps
// the legacy XML defaults (xml-v1 wire, greedy sampling); only new connections
// get the g1k defaults.
func TestLegacyConfigsAreNotRewritten(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightningCUDA, Model: "model", Endpoint: "https://example.test",
	})
	if err != nil {
		t.Fatal(err)
	}
	if config.Profile != "" || config.EnableWeb || config.EnableBash || config.WeatherBackend != "" ||
		config.TopK != 1 || config.DecisionMaxTokens != agent.DefaultXMLDecisionMaxOutputTokens {
		t.Fatalf("legacy config was rewritten: %+v", config)
	}
	options := sessionRunnerOptions(config, Status{Model: "model"}, t.TempDir(), nil, false, false)
	spec, err := agent.WireSpecOf(options)
	if err != nil {
		t.Fatal(err)
	}
	if preset, _ := spec.MatchPreset(); preset != "xml-v1" {
		t.Fatalf("legacy preset = %q, want xml-v1", preset)
	}
}

// TestNewConfigThinkingFollowsTheProfile: the thinking selector maps onto a
// wire override, so choosing a thinking mode on an agent-wire connection stays
// valid.
func TestNewConfigThinkingFollowsTheProfile(t *testing.T) {
	t.Parallel()
	config := newConnection()
	config.Thinking = "fast"
	config.Wire = "thinking=fast"
	normalized, err := normalizeConfig(config)
	if err != nil {
		t.Fatalf("agent-wire + thinking override rejected: %v", err)
	}
	options := sessionRunnerOptions(normalized, Status{Model: "model"}, t.TempDir(), nil, false, true)
	spec, err := agent.WireSpecOf(options)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(spec.Canonical(), "thinking=fast") {
		t.Fatalf("canonical = %s", spec.Canonical())
	}
}
