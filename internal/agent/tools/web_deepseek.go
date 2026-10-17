package tools

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"html"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"sync"
	"time"
	"unicode"
	"unicode/utf8"
)

const (
	defaultDeepSeekEndpoint = "https://api.deepseek.com"
	// DeepSeek rejects queries over 128 runes; web_search accepts up to 500.
	maxDeepSeekQueryRunes = 128
	// DeepSeek's summary runs 600-800 runes, several times a Brave snippet.
	// The cap keeps five results near one Brave page of context while still
	// carrying the answer-bearing sentences the summary is written around.
	maxDeepSeekSnippetRunes = 300
	// Fetch is one URL per request and pages take 5-30 s, so the up-to-four
	// URLs of a web_fetch call go out together. Four stays under the
	// account-level 5 QPS limit.
	deepSeekFetchParallel = 4
	// A slow page ends in a 504 after ~30 s; five such retries would hold a
	// turn for minutes, so fetch retries once.
	deepSeekFetchAttempts = 2
)

type DeepSeekConfig struct {
	APIKey     string
	Endpoint   string
	HTTPClient *http.Client
}

// DeepSeekWeb implements both web providers on DeepSeek's /v1/tools/search
// and /v1/tools/fetch.
type DeepSeekWeb struct {
	apiKey      string
	endpoint    string
	httpClient  *http.Client
	retry       providerRetryPolicy
	searchGate  *providerRequestGate
	fetchGate   *providerRequestGate
	fetchPolicy providerRetryPolicy
}

func NewDeepSeekWeb(config DeepSeekConfig) (*DeepSeekWeb, error) {
	if strings.TrimSpace(config.APIKey) == "" {
		return nil, fmt.Errorf("DeepSeek API key is required")
	}
	endpoint := strings.TrimRight(strings.TrimSpace(config.Endpoint), "/")
	if endpoint == "" {
		endpoint = defaultDeepSeekEndpoint
	}
	if _, err := validateProviderEndpoint(endpoint); err != nil {
		return nil, fmt.Errorf("DeepSeek endpoint: %w", err)
	}
	client := config.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 45 * time.Second}
	}
	fetchPolicy := defaultProviderRetryPolicy()
	fetchPolicy.maxAttempts = deepSeekFetchAttempts
	return &DeepSeekWeb{
		apiKey: config.APIKey, endpoint: endpoint, httpClient: client,
		retry: defaultProviderRetryPolicy(), fetchPolicy: fetchPolicy,
		searchGate: newProviderRequestGate(), fetchGate: newProviderRequestGateN(deepSeekFetchParallel),
	}, nil
}

func (p *DeepSeekWeb) post(ctx context.Context, tool, path string, policy providerRetryPolicy, gate *providerRequestGate, payload any) (*http.Response, int, error) {
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, 0, fmt.Errorf("encode DeepSeek request: %w", err)
	}
	return doProviderRequest(ctx, tool, p.httpClient, policy, gate, func() (*http.Request, error) {
		request, err := http.NewRequestWithContext(ctx, http.MethodPost, p.endpoint+path, bytes.NewReader(body))
		if err != nil {
			return nil, fmt.Errorf("build DeepSeek request: %w", err)
		}
		request.Header.Set("Authorization", "Bearer "+p.apiKey)
		request.Header.Set("Content-Type", "application/json")
		return request, nil
	})
}

func (p *DeepSeekWeb) Search(ctx context.Context, request WebSearchRequest) ([]WebSearchResult, error) {
	query := strings.TrimSpace(request.Query)
	if utf8.RuneCountInString(query) > maxDeepSeekQueryRunes {
		query = strings.TrimSpace(string([]rune(query)[:maxDeepSeekQueryRunes]))
	}
	response, attempts, err := p.post(ctx, "web_search", "/v1/tools/search", p.retry, p.searchGate,
		map[string]any{"query": query, "count": request.MaxResults})
	if err != nil {
		var exhausted providerRetryExhaustedError
		if errors.As(err, &exhausted) {
			return nil, providerUnavailableError{message: fmt.Sprintf(
				"DeepSeek search request failed after %d attempts: %v", exhausted.attempts, exhausted.cause,
			)}
		}
		return nil, fmt.Errorf("DeepSeek search request: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return nil, providerHTTPError("DeepSeek search", response.Status, attempts)
	}
	var payload struct {
		Results []struct {
			Title   string  `json:"title"`
			URL     string  `json:"url"`
			Snippet string  `json:"snippet"`
			Summary string  `json:"summary"`
			Date    *string `json:"date"`
		} `json:"results"`
	}
	if err := decodeLimitedJSON(response.Body, &payload); err != nil {
		return nil, fmt.Errorf("decode DeepSeek search response: %w", err)
	}
	results := make([]WebSearchResult, 0, min(request.MaxResults, len(payload.Results)))
	for _, item := range payload.Results {
		if len(results) >= request.MaxResults {
			break
		}
		snippet := strings.TrimSpace(item.Summary)
		if snippet == "" {
			snippet = strings.TrimSpace(item.Snippet)
		}
		published := ""
		if item.Date != nil {
			// RFC 3339 in UTC; the day is all the model needs.
			published, _, _ = strings.Cut(strings.TrimSpace(*item.Date), "T")
		}
		results = append(results, WebSearchResult{
			SourceID:    fmt.Sprintf("web-%d", len(results)+1),
			Title:       strings.TrimSpace(item.Title),
			URL:         cleanSearchURL(item.URL),
			Snippet:     truncateRunes(snippet, maxDeepSeekSnippetRunes),
			PublishedAt: published,
		})
	}
	return results, nil
}

// Fetch requests each URL on its own. A page DeepSeek cannot read (404, or
// 403 from its safety policy) is left out of the result like Tavily does, so
// web_fetch reports it as unreadable; only a call where every URL failed on
// a transport or server error is an error.
func (p *DeepSeekWeb) Fetch(ctx context.Context, request WebFetchRequest) ([]WebFetchResult, error) {
	pages := make([]*WebFetchResult, len(request.URLs))
	errs := make([]error, len(request.URLs))
	var wait sync.WaitGroup
	for index, pageURL := range request.URLs {
		wait.Add(1)
		go func() {
			defer wait.Done()
			pages[index], errs[index] = p.fetchOne(ctx, pageURL)
		}()
	}
	wait.Wait()
	results := make([]WebFetchResult, 0, len(request.URLs))
	var firstErr error
	for index, page := range pages {
		if errs[index] != nil && firstErr == nil {
			firstErr = errs[index]
		}
		if page == nil {
			continue
		}
		page.SourceID = fmt.Sprintf("page-%d", len(results)+1)
		results = append(results, *page)
	}
	if len(results) == 0 && firstErr != nil && countErrors(errs) == len(request.URLs) {
		return nil, firstErr
	}
	return results, nil
}

func (p *DeepSeekWeb) fetchOne(ctx context.Context, pageURL string) (*WebFetchResult, error) {
	response, attempts, err := p.post(ctx, "web_fetch", "/v1/tools/fetch", p.fetchPolicy, p.fetchGate,
		map[string]any{"url": pageURL})
	if err != nil {
		var exhausted providerRetryExhaustedError
		if errors.As(err, &exhausted) {
			return nil, providerUnavailableError{message: fmt.Sprintf(
				"DeepSeek fetch request failed after %d attempts: %v", exhausted.attempts, exhausted.cause,
			)}
		}
		return nil, fmt.Errorf("DeepSeek fetch request: %w", err)
	}
	defer response.Body.Close()
	switch {
	case response.StatusCode == http.StatusNotFound || response.StatusCode == http.StatusForbidden:
		return nil, nil
	case response.StatusCode < 200 || response.StatusCode >= 300:
		return nil, providerHTTPError("DeepSeek fetch", response.Status, attempts)
	}
	var payload struct {
		Content string `json:"content"`
	}
	if err := decodeLimitedJSON(response.Body, &payload); err != nil {
		return nil, fmt.Errorf("decode DeepSeek fetch response: %w", err)
	}
	content := strings.TrimSpace(unescapeMarkdown(payload.Content))
	if content == "" {
		return nil, nil
	}
	return &WebFetchResult{URL: pageURL, Content: content}, nil
}

func countErrors(errs []error) int {
	count := 0
	for _, err := range errs {
		if err != nil {
			count++
		}
	}
	return count
}

// markdownEscape matches DeepSeek fetch's backslash before every ASCII
// punctuation mark ("\# RWKV7\-G0 7\.2B"), about one rune in ten of a page.
// A literal backslash arrives escaped as "\\" and so survives as one.
var markdownEscape = regexp.MustCompile("\\\\([!-/:-@\\[-`{-~])")

func unescapeMarkdown(text string) string { return markdownEscape.ReplaceAllString(text, "$1") }

// trackingParams are query keys that only identify where a click came from.
// DeepSeek returns URLs as crawled, so they carry these (and a "#1"-style
// fragment); dropping them shortens what the model copies into web_fetch.
var trackingParams = map[string]bool{
	"trk": true, "hmsr": true, "spm": true, "fbclid": true, "gclid": true, "yclid": true,
	"mc_cid": true, "mc_eid": true, "_hsenc": true, "_hsmi": true, "partner": true,
}

func cleanSearchURL(raw string) string {
	raw = strings.TrimSpace(raw)
	parsed, err := url.Parse(raw)
	if err != nil || parsed.Host == "" {
		return raw
	}
	parsed.Fragment = ""
	parsed.RawFragment = ""
	if parsed.RawQuery != "" {
		values, err := url.ParseQuery(parsed.RawQuery)
		if err != nil {
			parsed.RawQuery = ""
			return parsed.String()
		}
		for key := range values {
			// "?%3Futm_source=" decodes to a key with a leading "?".
			name := strings.ToLower(strings.TrimLeft(key, "?"))
			if strings.HasPrefix(name, "utm_") || trackingParams[name] {
				values.Del(key)
			}
		}
		parsed.RawQuery = values.Encode()
	}
	return parsed.String()
}

func truncateRunes(text string, limit int) string {
	if utf8.RuneCountInString(text) <= limit {
		return text
	}
	return strings.TrimSpace(string([]rune(text)[:limit])) + "…"
}

var htmlTag = regexp.MustCompile(`<[^>]*>`)

// plainSnippet strips the highlight markup and entities a search API may
// leave in a description ("<strong>12月27日</strong>", "&quot;").
func plainSnippet(text string) string {
	return strings.TrimSpace(html.UnescapeString(htmlTag.ReplaceAllString(text, "")))
}

type SearchRoute string

const (
	SearchRouteAuto     SearchRoute = "auto"
	SearchRouteDeepSeek SearchRoute = "deepseek"
	SearchRouteBrave    SearchRoute = "brave"
)

// RoutedSearch picks the backend per query and falls back to the other one
// when the first errors or finds nothing. In auto mode a query with Chinese
// characters goes to DeepSeek first and anything else to Brave first: on a
// 2026-10-17 side-by-side DeepSeek returned primary Chinese news and
// government pages in 0.3-0.6 s, while Brave ranked official English docs
// (docs.python.org, PEPs, Stack Overflow) above DeepSeek's mirrors.
type RoutedSearch struct {
	Route    SearchRoute
	DeepSeek WebSearchProvider
	Brave    WebSearchProvider
}

func (r RoutedSearch) order(query string) []WebSearchProvider {
	deepseekFirst := r.Route == SearchRouteDeepSeek
	if r.Route != SearchRouteDeepSeek && r.Route != SearchRouteBrave {
		deepseekFirst = hasHan(query)
	}
	ordered := []WebSearchProvider{r.Brave, r.DeepSeek}
	if deepseekFirst {
		ordered = []WebSearchProvider{r.DeepSeek, r.Brave}
	}
	providers := ordered[:0]
	for _, provider := range ordered {
		if provider != nil {
			providers = append(providers, provider)
		}
	}
	return providers
}

func (r RoutedSearch) Search(ctx context.Context, request WebSearchRequest) ([]WebSearchResult, error) {
	var firstErr error
	answered := false
	for _, provider := range r.order(request.Query) {
		results, err := provider.Search(ctx, request)
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		if err != nil {
			if firstErr == nil {
				firstErr = err
			}
			continue
		}
		answered = true
		if len(results) > 0 {
			return results, nil
		}
	}
	if answered {
		return nil, nil
	}
	return nil, firstErr
}

func hasHan(text string) bool {
	for _, r := range text {
		if unicode.Is(unicode.Han, r) {
			return true
		}
	}
	return false
}

// FallbackFetch asks Primary for every URL and Secondary only for the URLs
// Primary returned no text for. On 2026-10-17's 18-URL side-by-side Tavily
// read 11 pages and DeepSeek 7, two of them (rwkv.cn, pkg.go.dev) pages
// Tavily missed.
type FallbackFetch struct {
	Primary   WebFetchProvider
	Secondary WebFetchProvider
}

func (f FallbackFetch) Fetch(ctx context.Context, request WebFetchRequest) ([]WebFetchResult, error) {
	primary, primaryErr := f.Primary.Fetch(ctx, request)
	if ctx.Err() != nil {
		return nil, ctx.Err()
	}
	results := make([]WebFetchResult, 0, len(request.URLs))
	covered := make(map[string]bool, len(request.URLs))
	for _, page := range primary {
		if strings.TrimSpace(page.Content) != "" {
			results = append(results, page)
			covered[pageKey(page.URL)] = true
		}
	}
	// As in fillMissingPages: a full set of pages means any URL mismatch is
	// a redirect, not a miss.
	var missing []string
	if len(results) < len(request.URLs) {
		for _, pageURL := range request.URLs {
			if !covered[pageKey(pageURL)] {
				missing = append(missing, pageURL)
			}
		}
	}
	if len(missing) == 0 || f.Secondary == nil {
		if len(results) == 0 && primaryErr != nil {
			return nil, primaryErr
		}
		return renumberPages(results), nil
	}
	secondary, secondaryErr := f.Secondary.Fetch(ctx, WebFetchRequest{URLs: missing})
	if ctx.Err() != nil {
		return nil, ctx.Err()
	}
	results = append(results, secondary...)
	if len(results) == 0 {
		if primaryErr != nil {
			return nil, primaryErr
		}
		if secondaryErr != nil {
			return nil, secondaryErr
		}
	}
	return renumberPages(results), nil
}

func renumberPages(pages []WebFetchResult) []WebFetchResult {
	for index := range pages {
		pages[index].SourceID = fmt.Sprintf("page-%d", index+1)
	}
	return pages
}
