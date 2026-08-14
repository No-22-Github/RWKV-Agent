package tools

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestBraveSearchProviderAndTool(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Header.Get("X-Subscription-Token") != "brave-secret" {
			t.Fatalf("missing Brave token")
		}
		if request.URL.Query().Get("q") != "RWKV Agent" || request.URL.Query().Get("count") != "2" {
			t.Fatalf("query = %s", request.URL.RawQuery)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"web":{"results":[{"title":"Official","url":"https://example.com/official","description":"Primary source","age":"2026-08-14"},{"title":"Review","url":"https://example.net/review","description":"Independent source"}]}}`))
	}))
	defer server.Close()

	provider, err := NewBraveSearchProvider(BraveConfig{
		APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	tool := WebTools(WebOptions{Search: provider})[0]
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"query":"RWKV Agent","max_results":2}`))
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := json.Marshal(value)
	text := string(encoded)
	for _, expected := range []string{"Official", "Primary source", "web-1", "2026-08-14"} {
		if !strings.Contains(text, expected) {
			t.Fatalf("result %s does not contain %q", text, expected)
		}
	}
}

func TestTavilyFetchProviderAndTool(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost {
			t.Fatalf("method = %s", request.Method)
		}
		var body struct {
			APIKey string   `json:"api_key"`
			URLs   []string `json:"urls"`
			Format string   `json:"format"`
		}
		if err := json.NewDecoder(request.Body).Decode(&body); err != nil {
			t.Fatal(err)
		}
		if body.APIKey != "tavily-secret" || len(body.URLs) != 1 || body.Format != "markdown" {
			t.Fatalf("body = %+v", body)
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"results":[{"url":"https://example.com/page","raw_content":"# Page\nUseful body."}]}`))
	}))
	defer server.Close()

	provider, err := NewTavilyFetchProvider(TavilyConfig{
		APIKey: "tavily-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	tool := WebTools(WebOptions{Fetch: provider})[1]
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"urls":["https://example.com/page#fragment"],"max_results":1}`))
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := json.Marshal(value)
	if text := string(encoded); !strings.Contains(text, "Useful body") || strings.Contains(text, "#fragment") {
		t.Fatalf("result = %s", text)
	}
}

func TestWebToolsRejectInvalidInputs(t *testing.T) {
	t.Parallel()
	tools := WebTools(WebOptions{})
	if _, err := tools[0].Execute(context.Background(), json.RawMessage(`{"query":"","max_results":20}`)); err == nil {
		t.Fatal("web_search accepted invalid arguments")
	}
	if _, err := tools[1].Execute(context.Background(), json.RawMessage(`{"urls":["file:///etc/hosts"]}`)); err == nil {
		t.Fatal("web_fetch accepted a non-HTTP URL")
	}
}
