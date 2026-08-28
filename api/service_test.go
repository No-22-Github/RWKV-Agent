package api

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestListRemoteModelsUsesBearerAndCustomHeaders(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path != "/v1/models" {
			t.Errorf("path = %q", request.URL.Path)
		}
		if request.Header.Get("Authorization") != "Bearer test-key" {
			t.Errorf("authorization was not forwarded")
		}
		if request.Header.Get("CF-Access-Client-Id") != "tunnel-id" ||
			request.Header.Get("CF-Access-Client-Secret") != "tunnel-secret" {
			t.Errorf("custom headers = %v", request.Header)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"data":[{"id":"rwkv-7b"},{"id":"rwkv-3b"}]}`))
	}))
	defer server.Close()

	service, err := NewService(Options{Workspace: t.TempDir()})
	if err != nil {
		t.Fatal(err)
	}
	defer service.Close()
	models, err := service.ListRemoteModels(context.Background(), Config{
		Provider: ProviderChatCompletions,
		Endpoint: server.URL,
		APIKey:   "test-key",
		Headers: map[string]string{
			"CF-Access-Client-Id":     "tunnel-id",
			"CF-Access-Client-Secret": "tunnel-secret",
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(models) != 2 || models[0].ID != "rwkv-3b" || models[1].ID != "rwkv-7b" {
		t.Fatalf("models = %+v", models)
	}
}

func TestRWKVConfigurationDefaultsToClientControlledStops(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Endpoint: "https://example.test",
		Model:    "rwkv7-test",
	})
	if err != nil {
		t.Fatal(err)
	}
	if config.RWKVStopTokens != "none" {
		t.Fatalf("RWKVStopTokens = %q, want none", config.RWKVStopTokens)
	}
}

func TestAgentCapabilityDefaults(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(Config{Provider: ProviderRWKVLightning, Model: "model", Endpoint: "https://example.test"})
	if err != nil {
		t.Fatal(err)
	}
	if config.ProgressiveTools != nil || !progressiveToolsEnabled(config.ProgressiveTools) {
		t.Fatalf("ProgressiveTools = %v", config.ProgressiveTools)
	}
	if config.AgentProtocol != AgentProtocolMarkdown {
		t.Fatalf("AgentProtocol = %q", config.AgentProtocol)
	}
	// semanticNoTool and deepToolAnchor now default on for the product profile
	// (60-case paired A/B: +12/-0, p=0.000488, repair rate 0/131). Unset stays
	// nil so a client can still turn either one off.
	if config.SemanticNoTool != nil || config.DeepToolAnchor != nil {
		t.Fatalf("unset product switches must stay nil: %+v", config)
	}
	if !productSwitchEnabled(config.SemanticNoTool) || !productSwitchEnabled(config.DeepToolAnchor) {
		t.Fatalf("product switches must default on: %+v", config)
	}
	if config.DecisionFakeThink {
		t.Fatalf("decisionFakeThink must default off: %+v", config)
	}
	if config.RouteMaxTokens != 48 || config.DecisionMaxTokens != 96 || config.MaxActiveBatch != 4 || config.SubagentMaxParallel != 4 || config.SubagentMaxSteps != 4 || config.SubagentTimeoutSeconds != 120 {
		t.Fatalf("capability defaults = %+v", config)
	}
}

func TestAgentProtocolCompatibilityMode(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol: AgentProtocolXML,
	})
	if err != nil || config.AgentProtocol != AgentProtocolXML {
		t.Fatalf("XML config = %+v, error = %v", config, err)
	}
	if _, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol: "invalid",
	}); err == nil {
		t.Fatal("invalid Agent protocol accepted")
	}
	// XML is a supported product transcript, so selecting it never fails.
	// Unset switches default off there: no JSON fence for deepToolAnchor to
	// extend, and no_tool measured 0 selections on this transcript.
	xml, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol: AgentProtocolXML,
	})
	if err != nil {
		t.Fatalf("XML Agent protocol rejected: %v", err)
	}
	if productSwitchEnabled(xml.SemanticNoTool) || productSwitchEnabled(xml.DeepToolAnchor) {
		t.Fatalf("XML config defaulted product switches on: %+v", xml)
	}
	// An explicit no_tool opt-in is still honored, so the comparison can be
	// re-run; deepToolAnchor has nothing to extend and stays off regardless.
	explicit, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol:  AgentProtocolXML,
		SemanticNoTool: boolPointer(true),
		DeepToolAnchor: boolPointer(true),
	})
	if err != nil {
		t.Fatalf("XML Agent protocol rejected the product switches: %v", err)
	}
	if !productSwitchEnabled(explicit.SemanticNoTool) || productSwitchEnabled(explicit.DeepToolAnchor) {
		t.Fatalf("XML config resolved explicit switches wrongly: %+v", explicit)
	}
	// decisionFakeThink still errors: the XML renderer prefills its own think
	// block, so the two would fight over the same assistant prefix.
	if _, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol:     AgentProtocolXML,
		DecisionFakeThink: true,
	}); err == nil {
		t.Fatal("XML Agent protocol accepted decisionFakeThink")
	}
	if _, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol: AgentProtocolMarkdown,
		Thinking:      "fast",
	}); err == nil {
		t.Fatal("markdown Agent protocol accepted an ignored thinking mode")
	}
	if _, err := normalizeConfig(Config{
		Provider: ProviderRWKVLightning,
		Model:    "model", Endpoint: "https://example.test",
		AgentProtocol: AgentProtocolXML,
		Thinking:      "full",
	}); err != nil {
		t.Fatalf("XML Agent protocol rejected thinking mode: %v", err)
	}
}

func TestSubagentsEnableRemoteBatchCoalescingByDefault(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(Config{Provider: ProviderRWKVLightning, Model: "model", Endpoint: "https://example.test", EnableSubagents: true})
	if err != nil {
		t.Fatal(err)
	}
	if config.RemoteBatchWaitMS != 10 {
		t.Fatalf("RemoteBatchWaitMS = %d", config.RemoteBatchWaitMS)
	}
}

func TestSingleLocalBatchRemainsValidWithoutSubagents(t *testing.T) {
	t.Parallel()
	config, err := normalizeConfig(Config{Provider: ProviderRWKVLightning, Model: "model", Endpoint: "https://example.test", MaxActiveBatch: 1})
	if err != nil {
		t.Fatal(err)
	}
	if config.MaxActiveBatch != 1 || config.SubagentMaxParallel != 4 {
		t.Fatalf("batch config = %+v", config)
	}
}

func TestWebToolsRequireBothProviderKeys(t *testing.T) {
	t.Parallel()
	for _, config := range []Config{
		{Model: "model.pth", EnableWeb: true},
		{Model: "model.pth", EnableWeb: true, BraveAPIKey: "brave"},
		{Model: "model.pth", EnableWeb: true, TavilyAPIKey: "tavily"},
	} {
		if _, err := normalizeConfig(config); err == nil || !strings.Contains(err.Error(), "requires Brave and Tavily API keys") {
			t.Fatalf("normalizeConfig(%+v) error = %v", config, err)
		}
	}
}

func TestAgentCapabilityBounds(t *testing.T) {
	t.Parallel()
	tests := []Config{
		{Model: "model.pth", RouteMaxTokens: -1},
		{Model: "model.pth", MaxActiveBatch: 9},
		{Model: "model.pth", RemoteBatchWaitMS: -1},
		{Model: "model.pth", SubagentMaxParallel: 1},
		{Model: "model.pth", SubagentMaxSteps: 1},
		{Model: "model.pth", SubagentTimeoutSeconds: 3601},
	}
	for _, config := range tests {
		if _, err := normalizeConfig(config); err == nil {
			t.Fatalf("normalizeConfig(%+v) succeeded", config)
		}
	}
}

func TestRemoteStatusDoesNotExposeSecrets(t *testing.T) {
	t.Parallel()
	service, err := NewService(Options{Workspace: t.TempDir()})
	if err != nil {
		t.Fatal(err)
	}
	defer service.Close()
	status, err := service.Configure(context.Background(), Config{
		Provider: ProviderRWKVLightning,
		Endpoint: "https://example.test",
		Model:    "rwkv7-test",
		Password: "service-password",
		Headers: map[string]string{
			"CF-Access-Client-Secret": "tunnel-secret",
		},
		EnableWeb:    true,
		BraveAPIKey:  "brave-secret",
		TavilyAPIKey: "tavily-secret",
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	if !status.HasAPIKey || len(status.HeaderNames) != 1 || status.HeaderNames[0] != "Cf-Access-Client-Secret" {
		t.Fatalf("status = %+v", status)
	}
	encoded, err := json.Marshal(status)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(encoded), "service-password") || strings.Contains(string(encoded), "tunnel-secret") || strings.Contains(string(encoded), "brave-secret") || strings.Contains(string(encoded), "tavily-secret") {
		t.Fatalf("status leaked a secret: %s", encoded)
	}
}

func TestNewServiceEmptyWorkspaceStaysUnset(t *testing.T) {
	t.Parallel()
	service, err := NewService(Options{Workspace: ""})
	if err != nil {
		t.Fatal(err)
	}
	defer service.Close()
	if service.Status().Workspace != "" {
		t.Fatalf("workspace = %q, want empty (no project open)", service.Status().Workspace)
	}
}

func boolPointer(value bool) *bool { return &value }
