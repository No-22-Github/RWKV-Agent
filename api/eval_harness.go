package api

import (
	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/product"
)

// EvalConnection is what the product evaluation varies on top of a new App
// connection: which model and wire it talks to. Everything else (step and
// token budgets, rescue limits, task control, tool order) is the App's own
// default, so a score measured this way is a score the App user sees.
type EvalConnection struct {
	Model   string
	StateID string
	// Profile and Wire override the new-connection profile (g1k) the same way
	// the App's protocol and thinking selectors do; empty keeps the default.
	Profile string
	Wire    string
	// Staged mirrors the App's staged file system: the staged-files task
	// control is part of the prompt exactly when the session is staged.
	Staged     bool
	TokenCount func(string) int
}

// EvalHarnessOptions returns the runner options a new App connection with an
// open workspace would use for conn. It goes through the same defaulting
// (applyConfigDefaults) and the same conversion (harnessConfig) as a live
// session, so the evaluation cannot drift from the App by construction.
func EvalHarnessOptions(conn EvalConnection) (agent.Options, error) {
	config := NewConfigDefaults()
	config.Model = conn.Model
	config.StateID = conn.StateID
	if conn.Profile != "" {
		config.Profile = conn.Profile
	}
	config.Wire = conn.Wire
	if err := applyConfigDefaults(&config); err != nil {
		return agent.Options{}, err
	}
	harness := harnessConfig(config, Status{Model: conn.Model}, "workspace", nil,
		config.AgentProtocol != AgentProtocolXML, conn.Staged)
	harness.TokenCount = conn.TokenCount
	return product.HarnessOptions(harness), nil
}
