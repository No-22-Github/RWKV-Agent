package eval

import (
	"context"
	"fmt"
	"strings"

	tools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// Fixture-backed web providers for custom e2e tasks: a canned search index and
// canned pages, matched by keyword or URL substring, so web-tool tasks run
// deterministically without network access. This mirrors SubagentFixtureEntry:
// round-1 could not validate fetch compression end to end because eval never
// registered web tools (the interactive --web flag had no effect on the
// evaluation runner).
//
// Entries drive both providers. A search hits every entry whose query_match is
// a case-insensitive substring of the query, in file order (so entry order is
// the result order — a design lever for source-position tasks). A fetch hits
// the entry with the LONGEST url_match that is a case-insensitive substring of
// the requested URL, so a fixture whose url_match is a prefix of another's URL
// cannot capture both; a miss returns a deterministic not-found page instead of
// a provider error so the model sees stable behaviour.

type WebFixtureEntry struct {
	// QueryMatch selects the entry for web_search (substring, case-insensitive).
	QueryMatch string `json:"query_match,omitempty"`
	// URLMatch selects the entry for web_fetch (substring, case-insensitive).
	URLMatch string `json:"url_match,omitempty"`
	// URL is the address web_search advertises for this entry; the model then
	// fetches it and URLMatch must resolve it.
	URL     string `json:"url,omitempty"`
	Title   string `json:"title,omitempty"`
	Snippet string `json:"snippet,omitempty"`
	Content string `json:"content,omitempty"`
	// PublishedAt rides into WebSearchResult.PublishedAt (RFC3339 or the
	// upstream Brave age form) so bank web tasks can plant stale-vs-fresh
	// source discrimination without hand-written result objects.
	PublishedAt string `json:"published_at,omitempty"`
}

type webFixtureProviders struct {
	entries []WebFixtureEntry
}

func (f webFixtureProviders) Search(
	_ context.Context,
	request tools.WebSearchRequest,
) ([]tools.WebSearchResult, error) {
	lowered := strings.ToLower(request.Query)
	results := make([]tools.WebSearchResult, 0, len(f.entries))
	for _, entry := range f.entries {
		if entry.QueryMatch == "" || entry.URL == "" {
			continue
		}
		if !strings.Contains(lowered, strings.ToLower(entry.QueryMatch)) {
			continue
		}
		results = append(results, tools.WebSearchResult{
			SourceID:    fmt.Sprintf("web-%d", len(results)+1),
			Title:       entry.Title,
			URL:         entry.URL,
			Snippet:     entry.Snippet,
			PublishedAt: entry.PublishedAt,
		})
		if len(results) >= request.MaxResults {
			break
		}
	}
	return results, nil
}

func (f webFixtureProviders) Fetch(
	_ context.Context,
	request tools.WebFetchRequest,
) ([]tools.WebFetchResult, error) {
	results := make([]tools.WebFetchResult, 0, len(request.URLs))
	for index, pageURL := range request.URLs {
		lowered := strings.ToLower(pageURL)
		content := "[fixture] no page matched this URL."
		// The most specific match wins, not the first one declared. One
		// fixture URL is routinely a prefix of another — ".../desk-rates" and
		// ".../desk-rates-september" — and first-match-wins silently served
		// the shorter entry's page for both. hyb-0004 shipped that way and was
		// unsolvable for it: the model asked for the September rate sheet, was
		// handed the June one, and every model that "failed" the case had
		// correctly reported the only rate it was ever shown.
		best := -1
		for _, entry := range f.entries {
			if entry.URLMatch == "" {
				continue
			}
			match := strings.ToLower(entry.URLMatch)
			if strings.Contains(lowered, match) && len(match) > best {
				best = len(match)
				content = entry.Content
			}
		}
		results = append(results, tools.WebFetchResult{
			SourceID: fmt.Sprintf("page-%d", index+1),
			URL:      pageURL,
			Content:  content,
		})
	}
	return results, nil
}
