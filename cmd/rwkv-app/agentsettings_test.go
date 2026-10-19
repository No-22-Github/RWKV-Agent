package main

import (
	"context"
	"net/http/httptest"
	"testing"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
)

// 共用 Agent 设置：旧档案里的 Key 第一次读取时迁移出来；连接时填进运行配置，
// 档案里不再存；改设置后运行配置立即更新，不重建连接。
func TestAppServiceSharesAgentSettingsAcrossProfiles(t *testing.T) {
	server := httptest.NewServer(&fakeStateServer{})
	t.Cleanup(server.Close)

	store := testAppStore(t)
	legacy := agentapi.Config{
		Provider: agentapi.ProviderRWKVLightningCUDA, Endpoint: server.URL + "/v1/batch/completions", Model: "rwkv7",
		EnableWeb: true, BraveAPIKey: "brave-old", WebSearchBackend: "brave", WeatherBackend: "wttr",
	}
	if _, err := store.SaveProvider("", "legacy", legacy, true); err != nil {
		t.Fatal(err)
	}
	service, err := agentapi.NewService(agentapi.Options{Workspace: resolvedWorkspace(t)})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, store)
	t.Cleanup(func() { _ = backend.Close() })

	agent, err := backend.GetAgentSettings()
	if err != nil {
		t.Fatal(err)
	}
	if agent.BraveAPIKey != "brave-old" || agent.WebSearchBackend != "brave" || agent.WeatherBackend != "wttr" {
		t.Fatalf("migrated agent settings = %+v", agent)
	}

	value, err := backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	if _, err := backend.ActivateProvider(context.Background(), value.Providers[0].ID); err != nil {
		t.Fatal(err)
	}
	value, err = backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	saved := value.Providers[0].Config
	if saved.BraveAPIKey != "" || saved.WebSearchBackend != "" || saved.WeatherBackend != agentapi.NewConfigWeatherBackend {
		t.Fatalf("profile still carries shared settings: %+v", saved)
	}
	if value.Config.BraveAPIKey != "brave-old" || value.Config.WeatherBackend != "wttr" || value.RuntimeOutdated {
		t.Fatalf("runtime config = %+v outdated = %v", value.Config, value.RuntimeOutdated)
	}

	if _, err := backend.SaveAgentSettings(appstorage.AgentSettings{BraveAPIKey: "brave-new", WeatherBackend: "open-meteo", WebFetchBackend: "deepseek"}); err != nil {
		t.Fatal(err)
	}
	value, err = backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	if value.Config.BraveAPIKey != "brave-new" || value.Config.WebSearchBackend != "" || value.Config.WebFetchBackend != "deepseek" || value.Config.WeatherBackend != "open-meteo" || value.RuntimeOutdated {
		t.Fatalf("runtime config after save = %+v outdated = %v", value.Config, value.RuntimeOutdated)
	}
	if _, err := backend.SaveAgentSettings(appstorage.AgentSettings{WebFetchBackend: "brave"}); err == nil {
		t.Fatal("unknown fetch backend saved")
	}
	if _, err := backend.SaveAgentSettings(appstorage.AgentSettings{WebSearchBackend: "google"}); err == nil {
		t.Fatal("unknown search backend accepted")
	}
}
