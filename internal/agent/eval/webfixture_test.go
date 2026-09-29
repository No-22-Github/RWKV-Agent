package eval

import (
	"context"
	"strings"
	"testing"

	tools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// §2.3: a fixture entry with an error makes web_fetch fail (ok:false with that
// text) instead of handing back the deterministic not-found page, so failure-
// reporting cases can exercise a page that is genuinely unreachable. Search is
// untouched — the broken page is still advertised — and entries without an
// error keep the old behavior.
func TestWebFixtureFetchError(t *testing.T) {
	t.Parallel()
	provider := webFixtureProviders{entries: []WebFixtureEntry{
		{URLMatch: "status.example.com/live", URL: "https://status.example.com/live", Content: "all systems go"},
		{URLMatch: "status.example.com/broken", URL: "https://status.example.com/broken", QueryMatch: "broken page",
			Error: "Tavily extract failed: 502 Bad Gateway"},
	}}

	t.Run("an error entry makes the fetch fail", func(t *testing.T) {
		results, err := provider.Fetch(context.Background(), tools.WebFetchRequest{
			URLs: []string{"https://status.example.com/broken"},
		})
		if err == nil {
			t.Fatalf("err = nil, results = %+v", results)
		}
		if !strings.Contains(err.Error(), "502 Bad Gateway") {
			t.Fatalf("err = %v, want the fixture error text", err)
		}
	})

	t.Run("a healthy entry still returns its page", func(t *testing.T) {
		results, err := provider.Fetch(context.Background(), tools.WebFetchRequest{
			URLs: []string{"https://status.example.com/live"},
		})
		if err != nil {
			t.Fatal(err)
		}
		if len(results) != 1 || results[0].Content != "all systems go" {
			t.Fatalf("results = %+v", results)
		}
	})

	t.Run("a miss without any entry keeps the not-found page", func(t *testing.T) {
		results, err := provider.Fetch(context.Background(), tools.WebFetchRequest{
			URLs: []string{"https://status.example.com/unknown"},
		})
		if err != nil {
			t.Fatal(err)
		}
		if len(results) != 1 || results[0].Content != "[fixture] no page matched this URL." {
			t.Fatalf("results = %+v", results)
		}
	})

	t.Run("search still advertises the broken page", func(t *testing.T) {
		results, err := provider.Search(context.Background(), tools.WebSearchRequest{
			Query:      "status broken page",
			MaxResults: 5,
		})
		if err != nil {
			t.Fatal(err)
		}
		if len(results) != 1 || results[0].URL != "https://status.example.com/broken" {
			t.Fatalf("results = %+v", results)
		}
	})
}
