package tools

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
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

func TestBraveSearchRetriesRateLimit(t *testing.T) {
	t.Parallel()
	var requests atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		if requests.Add(1) == 1 {
			writer.Header().Set("Retry-After", "2")
			writer.WriteHeader(http.StatusTooManyRequests)
			return
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"web":{"results":[{"title":"Recovered","url":"https://example.com","description":"Retry succeeded"}]}}`))
	}))
	defer server.Close()

	provider, err := NewBraveSearchProvider(BraveConfig{
		APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	var delays []time.Duration
	provider.retry.sleep = func(_ context.Context, delay time.Duration) error {
		delays = append(delays, delay)
		return nil
	}
	results, err := provider.Search(context.Background(), WebSearchRequest{Query: "RWKV", MaxResults: 1})
	if err != nil {
		t.Fatal(err)
	}
	if requests.Load() != 2 || len(results) != 1 || results[0].Title != "Recovered" {
		t.Fatalf("requests=%d results=%+v", requests.Load(), results)
	}
	if len(delays) != 1 || delays[0] != 2*time.Second {
		t.Fatalf("retry delays = %v", delays)
	}
}

func TestBraveSearchRetriesAllServerFailures(t *testing.T) {
	t.Parallel()
	for _, status := range []int{http.StatusInternalServerError, http.StatusNotImplemented, 599} {
		status := status
		t.Run(fmt.Sprintf("HTTP_%d", status), func(t *testing.T) {
			t.Parallel()
			var requests atomic.Int32
			server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
				if requests.Add(1) == 1 {
					writer.WriteHeader(status)
					return
				}
				writer.Header().Set("Content-Type", "application/json")
				_, _ = writer.Write([]byte(`{"web":{"results":[]}}`))
			}))
			defer server.Close()
			provider, err := NewBraveSearchProvider(BraveConfig{
				APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
			})
			if err != nil {
				t.Fatal(err)
			}
			provider.retry.sleep = func(context.Context, time.Duration) error { return nil }
			if _, err := provider.Search(context.Background(), WebSearchRequest{Query: "RWKV", MaxResults: 1}); err != nil {
				t.Fatal(err)
			}
			if requests.Load() != 2 {
				t.Fatalf("requests = %d, want 2", requests.Load())
			}
		})
	}
}

func TestTavilyFetchRetriesAndReplaysBody(t *testing.T) {
	t.Parallel()
	var requests atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		var body struct {
			APIKey string   `json:"api_key"`
			URLs   []string `json:"urls"`
		}
		if err := json.NewDecoder(request.Body).Decode(&body); err != nil {
			t.Errorf("decode attempt body: %v", err)
			writer.WriteHeader(http.StatusBadRequest)
			return
		}
		if body.APIKey != "tavily-secret" || len(body.URLs) != 1 || body.URLs[0] != "https://example.com/page" {
			t.Errorf("attempt body = %+v", body)
			writer.WriteHeader(http.StatusBadRequest)
			return
		}
		if requests.Add(1) == 1 {
			writer.WriteHeader(http.StatusServiceUnavailable)
			return
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"results":[{"url":"https://example.com/page","raw_content":"Recovered page"}]}`))
	}))
	defer server.Close()

	provider, err := NewTavilyFetchProvider(TavilyConfig{
		APIKey: "tavily-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	provider.retry.sleep = func(context.Context, time.Duration) error { return nil }
	results, err := provider.Fetch(context.Background(), WebFetchRequest{URLs: []string{"https://example.com/page"}})
	if err != nil {
		t.Fatal(err)
	}
	if requests.Load() != 2 || len(results) != 1 || results[0].Content != "Recovered page" {
		t.Fatalf("requests=%d results=%+v", requests.Load(), results)
	}
}

func TestBraveSearchReportsRetryExhaustion(t *testing.T) {
	t.Parallel()
	var requests atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		requests.Add(1)
		writer.WriteHeader(http.StatusTooManyRequests)
	}))
	defer server.Close()

	provider, err := NewBraveSearchProvider(BraveConfig{
		APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	provider.retry.sleep = func(context.Context, time.Duration) error { return nil }
	_, err = provider.Search(context.Background(), WebSearchRequest{Query: "RWKV", MaxResults: 1})
	want := fmt.Sprintf("HTTP 429 Too Many Requests after %d attempts", defaultRetryAttempts)
	if err == nil || !strings.Contains(err.Error(), want) || !errors.Is(err, agent.ErrProviderUnavailable) {
		t.Fatalf("error = %v", err)
	}
	if requests.Load() != defaultRetryAttempts {
		t.Fatalf("requests = %d, want %d", requests.Load(), defaultRetryAttempts)
	}
}

func TestBraveSearchRetriesTransportFailure(t *testing.T) {
	t.Parallel()
	var requests atomic.Int32
	client := &http.Client{Transport: roundTripFunc(func(request *http.Request) (*http.Response, error) {
		if requests.Add(1) == 1 {
			return nil, errors.New("temporary connection reset")
		}
		return &http.Response{
			StatusCode: http.StatusOK,
			Status:     "200 OK",
			Header:     make(http.Header),
			Body: io.NopCloser(strings.NewReader(
				`{"web":{"results":[{"title":"Recovered","url":"https://example.com"}]}}`,
			)),
			Request: request,
		}, nil
	})}
	provider, err := NewBraveSearchProvider(BraveConfig{
		APIKey: "brave-secret", Endpoint: "https://search.example.test", HTTPClient: client,
	})
	if err != nil {
		t.Fatal(err)
	}
	provider.retry.sleep = func(context.Context, time.Duration) error { return nil }
	results, err := provider.Search(context.Background(), WebSearchRequest{Query: "RWKV", MaxResults: 1})
	if err != nil || requests.Load() != 2 || len(results) != 1 {
		t.Fatalf("requests=%d results=%+v error=%v", requests.Load(), results, err)
	}
}

func TestBraveSearchSerializesSharedProviderCalls(t *testing.T) {
	t.Parallel()
	started := make(chan string, 2)
	releaseFirst := make(chan struct{})
	var requests atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		started <- request.URL.Query().Get("q")
		if requests.Add(1) == 1 {
			<-releaseFirst
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"web":{"results":[]}}`))
	}))
	defer server.Close()
	provider, err := NewBraveSearchProvider(BraveConfig{
		APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	results := make(chan error, 2)
	go func() {
		_, err := provider.Search(context.Background(), WebSearchRequest{Query: "first", MaxResults: 1})
		results <- err
	}()
	if query := <-started; query != "first" {
		t.Fatalf("first query = %q", query)
	}
	go func() {
		_, err := provider.Search(context.Background(), WebSearchRequest{Query: "second", MaxResults: 1})
		results <- err
	}()
	select {
	case query := <-started:
		t.Fatalf("second call reached provider before first completed: %q", query)
	case <-time.After(50 * time.Millisecond):
	}
	close(releaseFirst)
	if query := <-started; query != "second" {
		t.Fatalf("second query = %q", query)
	}
	for range 2 {
		if err := <-results; err != nil {
			t.Fatal(err)
		}
	}
}

func TestBraveSearchCancelsRetryWait(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writer.Header().Set("Retry-After", "5")
		writer.WriteHeader(http.StatusTooManyRequests)
	}))
	defer server.Close()

	provider, err := NewBraveSearchProvider(BraveConfig{
		APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatal(err)
	}
	waiting := make(chan struct{}, 1)
	provider.retry.sleep = func(ctx context.Context, _ time.Duration) error {
		waiting <- struct{}{}
		<-ctx.Done()
		return ctx.Err()
	}
	ctx, cancel := context.WithCancel(context.Background())
	result := make(chan error, 1)
	go func() {
		_, err := provider.Search(ctx, WebSearchRequest{Query: "RWKV", MaxResults: 1})
		result <- err
	}()
	<-waiting
	cancel()
	if err := <-result; !errors.Is(err, context.Canceled) {
		t.Fatalf("error = %v, want context canceled", err)
	}
}

func TestBraveSearchDoesNotRetryPermanentHTTPFailures(t *testing.T) {
	t.Parallel()
	for _, status := range []int{http.StatusBadRequest, http.StatusUnauthorized, http.StatusForbidden} {
		status := status
		t.Run(http.StatusText(status), func(t *testing.T) {
			t.Parallel()
			var requests atomic.Int32
			server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
				requests.Add(1)
				writer.WriteHeader(status)
			}))
			defer server.Close()
			provider, err := NewBraveSearchProvider(BraveConfig{
				APIKey: "brave-secret", Endpoint: server.URL, HTTPClient: server.Client(),
			})
			if err != nil {
				t.Fatal(err)
			}
			provider.retry.sleep = func(context.Context, time.Duration) error {
				t.Fatal("permanent failure scheduled a retry")
				return nil
			}
			_, err = provider.Search(context.Background(), WebSearchRequest{Query: "RWKV", MaxResults: 1})
			if err == nil || requests.Load() != 1 {
				t.Fatalf("requests=%d error=%v", requests.Load(), err)
			}
		})
	}
}

func TestParseRetryAfter(t *testing.T) {
	t.Parallel()
	now := time.Date(2026, time.August, 14, 12, 0, 0, 0, time.UTC)
	tests := []struct {
		value string
		want  time.Duration
		ok    bool
	}{
		{value: "3", want: 3 * time.Second, ok: true},
		{value: now.Add(4 * time.Second).Format(http.TimeFormat), want: 4 * time.Second, ok: true},
		{value: now.Add(-time.Second).Format(http.TimeFormat), want: 0, ok: true},
		{value: "invalid", ok: false},
	}
	for _, test := range tests {
		got, ok := parseRetryAfter(test.value, now)
		if ok != test.ok || got != test.want {
			t.Errorf("parseRetryAfter(%q) = (%v, %v), want (%v, %v)", test.value, got, ok, test.want, test.ok)
		}
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

type roundTripFunc func(*http.Request) (*http.Response, error)

func (fn roundTripFunc) RoundTrip(request *http.Request) (*http.Response, error) {
	return fn(request)
}
