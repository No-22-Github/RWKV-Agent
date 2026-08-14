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
	if strings.Contains(string(encoded), "service-password") || strings.Contains(string(encoded), "tunnel-secret") {
		t.Fatalf("status leaked a secret: %s", encoded)
	}
}
