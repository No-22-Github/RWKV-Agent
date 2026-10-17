package api

import (
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/product"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

func TestNewWebProvidersCombinesBackends(t *testing.T) {
	t.Parallel()
	set, err := newWebProviders(Config{DeepSeekWebAPIKey: "ds", WebSearchBackend: "brave"})
	if err != nil {
		t.Fatal(err)
	}
	routed, ok := set.search.(assistanttools.RoutedSearch)
	if !ok || routed.DeepSeek == nil || routed.Brave != nil || routed.Route != assistanttools.SearchRouteBrave {
		t.Fatalf("search = %#v", set.search)
	}
	if _, ok := set.fetch.(*assistanttools.DeepSeekWeb); !ok {
		t.Fatalf("DeepSeek alone should fetch: %#v", set.fetch)
	}

	set, err = newWebProviders(Config{BraveAPIKey: "b", TavilyAPIKey: "t", DeepSeekWebAPIKey: "ds"})
	if err != nil {
		t.Fatal(err)
	}
	if routed := set.search.(assistanttools.RoutedSearch); routed.Brave == nil || routed.DeepSeek == nil {
		t.Fatalf("search = %#v", routed)
	}
	if fetch, ok := set.fetch.(assistanttools.FallbackFetch); !ok || fetch.Secondary == nil {
		t.Fatalf("fetch = %#v", set.fetch)
	}

	set, err = newWebProviders(Config{})
	if err != nil {
		t.Fatal(err)
	}
	if set.search != product.MissingWebSearch() || set.fetch != product.MissingWebFetch() {
		t.Fatalf("no keys should keep the not-configured placeholders: %#v", set)
	}
}

func TestNormalizeConfigRejectsUnknownSearchBackend(t *testing.T) {
	t.Parallel()
	config := newConnection()
	config.WebSearchBackend = "google"
	if _, err := normalizeConfig(config); err == nil {
		t.Fatal("unknown webSearchBackend accepted")
	}
	config.WebSearchBackend = "deepseek"
	if _, err := normalizeConfig(config); err != nil {
		t.Fatal(err)
	}
}
