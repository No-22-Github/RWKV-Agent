package tools

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"testing"
	"time"
)

func newTestDeepSeek(t *testing.T, handler http.HandlerFunc) *DeepSeekWeb {
	t.Helper()
	server := httptest.NewServer(handler)
	t.Cleanup(server.Close)
	provider, err := NewDeepSeekWeb(DeepSeekConfig{APIKey: "ds-secret", Endpoint: server.URL, HTTPClient: server.Client()})
	if err != nil {
		t.Fatal(err)
	}
	provider.retry.sleep = func(context.Context, time.Duration) error { return nil }
	provider.fetchPolicy.sleep = provider.retry.sleep
	return provider
}

func TestDeepSeekSearchCleansResults(t *testing.T) {
	t.Parallel()
	var body map[string]any
	provider := newTestDeepSeek(t, func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path != "/v1/tools/search" || request.Header.Get("Authorization") != "Bearer ds-secret" {
			t.Errorf("path=%s auth=%s", request.URL.Path, request.Header.Get("Authorization"))
		}
		_ = json.NewDecoder(request.Body).Decode(&body)
		summary := strings.Repeat("长", 400)
		_, _ = writer.Write([]byte(`{"results":[
			{"title":"A","url":"https://example.com/a?utm_source=x&id=7&trk=y#1","snippet":"short","summary":"` + summary + `","date":"2026-10-06T00:00:00+00:00"},
			{"title":"B","url":"https://example.com/b/?%3Futm_source=Kurir","snippet":"only snippet","summary":"","date":null}]}`))
	})
	results, err := provider.Search(context.Background(), WebSearchRequest{Query: strings.Repeat("查", 200), MaxResults: 5})
	if err != nil {
		t.Fatal(err)
	}
	if got := []rune(body["query"].(string)); len(got) != maxDeepSeekQueryRunes || body["count"] != float64(5) {
		t.Fatalf("request body = %d runes, count %v", len(got), body["count"])
	}
	if len(results) != 2 {
		t.Fatalf("results = %+v", results)
	}
	if results[0].URL != "https://example.com/a?id=7" || results[1].URL != "https://example.com/b/" {
		t.Fatalf("urls = %q, %q", results[0].URL, results[1].URL)
	}
	if n := len([]rune(results[0].Snippet)); n != maxDeepSeekSnippetRunes+1 || !strings.HasSuffix(results[0].Snippet, "…") {
		t.Fatalf("summary not capped: %d runes", n)
	}
	if results[1].Snippet != "only snippet" || results[0].PublishedAt != "2026-10-06" || results[1].PublishedAt != "" {
		t.Fatalf("results = %+v", results)
	}
}

func TestDeepSeekFetchUnescapesAndSkipsUnreadable(t *testing.T) {
	t.Parallel()
	var calls atomic.Int32
	provider := newTestDeepSeek(t, func(writer http.ResponseWriter, request *http.Request) {
		calls.Add(1)
		var body struct{ URL string }
		_ = json.NewDecoder(request.Body).Decode(&body)
		if strings.Contains(body.URL, "blocked") {
			writer.WriteHeader(http.StatusNotFound)
			_, _ = writer.Write([]byte(`{"error":{"message":"failed to fetch URL"}}`))
			return
		}
		_, _ = writer.Write([]byte(`{"title":"T","content":"\\# RWKV7\\-G0 7\\.2B \\(62\\.7\\%\\) path C:\\\\tmp"}`))
	})
	pages, err := provider.Fetch(context.Background(), WebFetchRequest{URLs: []string{"https://ok.example/a", "https://blocked.example/b"}})
	if err != nil {
		t.Fatal(err)
	}
	if calls.Load() != 2 || len(pages) != 1 {
		t.Fatalf("calls=%d pages=%+v", calls.Load(), pages)
	}
	if pages[0].URL != "https://ok.example/a" || pages[0].Content != `# RWKV7-G0 7.2B (62.7%) path C:\tmp` || pages[0].SourceID != "page-1" {
		t.Fatalf("page = %+v", pages[0])
	}
}

func TestDeepSeekFetchErrorsOnlyWhenEveryURLFails(t *testing.T) {
	t.Parallel()
	provider := newTestDeepSeek(t, func(writer http.ResponseWriter, _ *http.Request) {
		writer.WriteHeader(http.StatusUnauthorized)
	})
	_, err := provider.Fetch(context.Background(), WebFetchRequest{URLs: []string{"https://a.example/", "https://b.example/"}})
	if err == nil || !strings.Contains(err.Error(), "401") {
		t.Fatalf("err = %v", err)
	}
}

func TestBraveSnippetDropsMarkup(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		_, _ = writer.Write([]byte(`{"web":{"results":[{"title":"Go &amp; Rust","url":"https://e.com","description":"开通时间：<strong>2025年12月27日</strong> &quot;首班车&quot;"}]}}`))
	}))
	defer server.Close()
	provider, err := NewBraveSearchProvider(BraveConfig{APIKey: "k", Endpoint: server.URL, HTTPClient: server.Client()})
	if err != nil {
		t.Fatal(err)
	}
	results, err := provider.Search(context.Background(), WebSearchRequest{Query: "q", MaxResults: 1})
	if err != nil {
		t.Fatal(err)
	}
	if results[0].Title != "Go & Rust" || results[0].Snippet != `开通时间：2025年12月27日 "首班车"` {
		t.Fatalf("result = %+v", results[0])
	}
}

type stubSearch struct {
	name    string
	results []WebSearchResult
	err     error
	calls   *[]string
}

func (s stubSearch) Search(context.Context, WebSearchRequest) ([]WebSearchResult, error) {
	*s.calls = append(*s.calls, s.name)
	return s.results, s.err
}

func TestRoutedSearchOrderAndFallback(t *testing.T) {
	t.Parallel()
	hit := []WebSearchResult{{Title: "hit"}}
	cases := []struct {
		name      string
		route     SearchRoute
		query     string
		dsResults []WebSearchResult
		dsErr     error
		brResults []WebSearchResult
		brErr     error
		wantCalls string
		wantHit   bool
		wantErr   bool
	}{
		{"auto chinese", SearchRouteAuto, "北京天气", hit, nil, hit, nil, "ds", true, false},
		{"auto english", "", "python release", hit, nil, hit, nil, "brave", true, false},
		{"forced deepseek", SearchRouteDeepSeek, "python", hit, nil, hit, nil, "ds", true, false},
		{"forced brave", SearchRouteBrave, "北京", hit, nil, hit, nil, "brave", true, false},
		{"empty falls back", SearchRouteAuto, "北京", nil, nil, hit, nil, "ds,brave", true, false},
		{"error falls back", SearchRouteAuto, "rust", hit, nil, nil, errors.New("down"), "brave,ds", true, false},
		{"empty then error is empty", SearchRouteAuto, "北京", nil, nil, nil, errors.New("down"), "ds,brave", false, false},
		{"both error", SearchRouteAuto, "rust", nil, errors.New("ds down"), nil, errors.New("brave down"), "brave,ds", false, true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			var calls []string
			routed := RoutedSearch{
				Route:    tc.route,
				DeepSeek: stubSearch{"ds", tc.dsResults, tc.dsErr, &calls},
				Brave:    stubSearch{"brave", tc.brResults, tc.brErr, &calls},
			}
			results, err := routed.Search(context.Background(), WebSearchRequest{Query: tc.query, MaxResults: 5})
			if got := strings.Join(calls, ","); got != tc.wantCalls {
				t.Fatalf("calls = %s, want %s", got, tc.wantCalls)
			}
			if (len(results) > 0) != tc.wantHit || (err != nil) != tc.wantErr {
				t.Fatalf("results=%v err=%v", results, err)
			}
			if tc.wantErr && err.Error() != "brave down" {
				t.Fatalf("want the first backend's error, got %v", err)
			}
		})
	}
	var calls []string
	onlyBrave := RoutedSearch{Route: SearchRouteDeepSeek, Brave: stubSearch{"brave", hit, nil, &calls}}
	if results, err := onlyBrave.Search(context.Background(), WebSearchRequest{Query: "北京", MaxResults: 5}); err != nil || len(results) != 1 {
		t.Fatalf("missing DeepSeek should leave Brave: %v %v", results, err)
	}
}

type stubFetch struct {
	pages map[string]string
	err   error
	asked *[][]string
}

func (s stubFetch) Fetch(_ context.Context, request WebFetchRequest) ([]WebFetchResult, error) {
	*s.asked = append(*s.asked, request.URLs)
	if s.err != nil {
		return nil, s.err
	}
	var results []WebFetchResult
	for _, pageURL := range request.URLs {
		if content, ok := s.pages[pageURL]; ok {
			results = append(results, WebFetchResult{SourceID: "x", URL: pageURL, Content: content})
		}
	}
	return results, nil
}

func TestFallbackFetchFillsOnlyMissingPages(t *testing.T) {
	t.Parallel()
	var primaryAsked, secondaryAsked [][]string
	fetch := FallbackFetch{
		Primary:   stubFetch{pages: map[string]string{"https://a/": "A", "https://b/": "  "}, asked: &primaryAsked},
		Secondary: stubFetch{pages: map[string]string{"https://b/": "B"}, asked: &secondaryAsked},
	}
	pages, err := fetch.Fetch(context.Background(), WebFetchRequest{URLs: []string{"https://a/", "https://b/", "https://c/"}})
	if err != nil {
		t.Fatal(err)
	}
	if len(secondaryAsked) != 1 || strings.Join(secondaryAsked[0], " ") != "https://b/ https://c/" {
		t.Fatalf("secondary asked %v", secondaryAsked)
	}
	if len(pages) != 2 || pages[0].Content != "A" || pages[1].Content != "B" || pages[1].SourceID != "page-2" {
		t.Fatalf("pages = %+v", pages)
	}

	// The tool still reports the page neither backend could read.
	tool := WebTools(WebOptions{Fetch: fetch})[1]
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"urls":["https://a/","https://b/","https://c/"]}`))
	if err != nil {
		t.Fatal(err)
	}
	if note := value.(map[string]any)["note"]; note != partialWebFetchNote {
		t.Fatalf("note = %v", note)
	}
}

func TestFallbackFetchSurvivesPrimaryError(t *testing.T) {
	t.Parallel()
	var primaryAsked, secondaryAsked [][]string
	fetch := FallbackFetch{
		Primary:   stubFetch{err: errors.New("tavily down"), asked: &primaryAsked},
		Secondary: stubFetch{pages: map[string]string{"https://a/": "A"}, asked: &secondaryAsked},
	}
	pages, err := fetch.Fetch(context.Background(), WebFetchRequest{URLs: []string{"https://a/"}})
	if err != nil || len(pages) != 1 {
		t.Fatalf("pages=%v err=%v", pages, err)
	}
	fetch.Secondary = stubFetch{pages: map[string]string{}, asked: &secondaryAsked}
	if _, err := fetch.Fetch(context.Background(), WebFetchRequest{URLs: []string{"https://a/"}}); err == nil || err.Error() != "tavily down" {
		t.Fatalf("err = %v", err)
	}
}

func TestCleanSearchURLKeepsMeaningfulQuery(t *testing.T) {
	t.Parallel()
	for raw, want := range map[string]string{
		"https://www.rwkv.cn/news/read/20250724?id=20250724":          "https://www.rwkv.cn/news/read/20250724?id=20250724",
		"https://www.python.org/search/?q=python+tools&page=11#1":     "https://www.python.org/search/?page=11&q=python+tools",
		"https://blog.rust-lang.org/2025/05/26/x/?utm_source=a&spm=b": "https://blog.rust-lang.org/2025/05/26/x/",
		"not a url": "not a url",
	} {
		if got := cleanSearchURL(raw); got != want {
			t.Errorf("cleanSearchURL(%q) = %q, want %q", raw, got, want)
		}
	}
}
