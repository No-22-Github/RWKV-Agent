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
	if fetch := localFirst(t, set.fetch); fetch == nil {
		t.Fatal("no keyed fetch behind the local reader")
	} else if _, ok := fetch.(*assistanttools.DeepSeekWeb); !ok {
		t.Fatalf("DeepSeek alone should back the local reader: %#v", fetch)
	}

	set, err = newWebProviders(Config{BraveAPIKey: "b", TavilyAPIKey: "t", DeepSeekWebAPIKey: "ds"})
	if err != nil {
		t.Fatal(err)
	}
	if routed := set.search.(assistanttools.RoutedSearch); routed.Brave == nil || routed.DeepSeek == nil {
		t.Fatalf("search = %#v", routed)
	}
	if fetch, ok := localFirst(t, set.fetch).(assistanttools.FallbackFetch); !ok || fetch.Secondary == nil {
		t.Fatalf("fetch = %#v", set.fetch)
	} else if _, tavilyFirst := fetch.Primary.(*assistanttools.TavilyFetchProvider); !tavilyFirst {
		t.Fatalf("Tavily should read pages first by default: %#v", fetch)
	}

	set, err = newWebProviders(Config{TavilyAPIKey: "t", DeepSeekWebAPIKey: "ds", WebFetchBackend: "deepseek"})
	if err != nil {
		t.Fatal(err)
	}
	fetch, ok := localFirst(t, set.fetch).(assistanttools.FallbackFetch)
	if !ok {
		t.Fatalf("fetch = %#v", set.fetch)
	}
	if _, deepseekFirst := fetch.Primary.(*assistanttools.DeepSeekWeb); !deepseekFirst {
		t.Fatalf("webFetchBackend=deepseek should read pages with DeepSeek first: %#v", fetch)
	}
	if _, tavilySecond := fetch.Secondary.(*assistanttools.TavilyFetchProvider); !tavilySecond {
		t.Fatalf("Tavily should cover the pages DeepSeek missed: %#v", fetch)
	}

	set, err = newWebProviders(Config{})
	if err != nil {
		t.Fatal(err)
	}
	if set.search != product.MissingWebSearch() {
		t.Fatalf("no keys should keep the not-configured search placeholder: %#v", set)
	}
	if keyed := localFirst(t, set.fetch); keyed != nil {
		t.Fatalf("no keys: the local reader should stand alone: %#v", keyed)
	}
}

// localFirst checks work-v3's keyless reader is the first fetch backend and
// returns what backs it (nil without keys).
func localFirst(t *testing.T, fetch assistanttools.WebFetchProvider) assistanttools.WebFetchProvider {
	t.Helper()
	chain, ok := fetch.(assistanttools.FallbackFetch)
	if !ok {
		t.Fatalf("fetch = %#v, want the local reader first", fetch)
	}
	if _, ok := chain.Primary.(assistanttools.ReadabilityFetch); !ok {
		t.Fatalf("primary = %#v, want ReadabilityFetch", chain.Primary)
	}
	return chain.Secondary
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
	config.WebFetchBackend = "brave"
	if _, err := normalizeConfig(config); err == nil {
		t.Fatal("unknown webFetchBackend accepted")
	}
	config.WebFetchBackend = "deepseek"
	if _, err := normalizeConfig(config); err != nil {
		t.Fatal(err)
	}
}
