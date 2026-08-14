package tools

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

const (
	defaultBraveEndpoint   = "https://api.search.brave.com/res/v1/web/search"
	defaultTavilyEndpoint  = "https://api.tavily.com/extract"
	maxWebResponseBytes    = 4 * 1024 * 1024
	maxFetchedContentRunes = 32 * 1024
)

type WebSearchRequest struct {
	Query      string
	MaxResults int
}

type WebSearchResult struct {
	SourceID    string `json:"source_id"`
	Title       string `json:"title"`
	URL         string `json:"url"`
	Snippet     string `json:"snippet"`
	PublishedAt string `json:"published_at,omitempty"`
}

type WebSearchProvider interface {
	Search(context.Context, WebSearchRequest) ([]WebSearchResult, error)
}

type WebFetchRequest struct {
	URLs []string
}

type WebFetchResult struct {
	SourceID  string `json:"source_id"`
	URL       string `json:"url"`
	Content   string `json:"content"`
	Truncated bool   `json:"truncated,omitempty"`
}

type WebFetchProvider interface {
	Fetch(context.Context, WebFetchRequest) ([]WebFetchResult, error)
}

type WebOptions struct {
	Search WebSearchProvider
	Fetch  WebFetchProvider
}

func WebTools(options WebOptions) []agent.Tool {
	return []agent.Tool{
		&webSearchTool{provider: options.Search},
		&webFetchTool{provider: options.Fetch},
	}
}

type webSearchTool struct{ provider WebSearchProvider }

func (*webSearchTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "web_search",
		Description: "Search the public web with Brave and return titles, URLs, snippets, and source IDs.",
		Arguments:   `{"query":"search query","max_results":"integer 1..10"}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"query":{"type":"string","minLength":1,"maxLength":500},"max_results":{"type":["integer","null"],"minimum":1,"maximum":10}},"required":["query","max_results"],"additionalProperties":false}`),
		Strict:      true,
		Bundle:      agent.ToolBundleWeb,
		Permission:  agent.PermissionNetworkRead,
		Replayable:  true,
	}
}

func (t *webSearchTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Query      string `json:"query"`
		MaxResults int    `json:"max_results"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	args.Query = strings.TrimSpace(args.Query)
	if args.Query == "" {
		return nil, invalidArguments("query is required")
	}
	if args.MaxResults == 0 {
		args.MaxResults = 5
	}
	if args.MaxResults < 1 || args.MaxResults > 10 {
		return nil, invalidArguments("max_results must be between 1 and 10")
	}
	if t.provider == nil {
		return nil, agent.ErrProviderUnavailable
	}
	results, err := t.provider.Search(ctx, WebSearchRequest{Query: args.Query, MaxResults: args.MaxResults})
	if err != nil {
		return nil, err
	}
	return map[string]any{"query": args.Query, "results": results}, nil
}

type webFetchTool struct{ provider WebFetchProvider }

func (*webFetchTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "web_fetch",
		Description: "Fetch readable Markdown content for up to four public web pages with Tavily Extract.",
		Arguments:   `{"urls":["https://example.com/page"]}`,
		Parameters:  json.RawMessage(`{"type":"object","properties":{"urls":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":4}},"required":["urls"],"additionalProperties":false}`),
		Strict:      true,
		Bundle:      agent.ToolBundleWeb,
		Permission:  agent.PermissionNetworkRead,
		Replayable:  true,
	}
}

func (t *webFetchTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		URLs       []string        `json:"urls"`
		MaxResults json.RawMessage `json:"max_results"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	if len(args.URLs) < 1 || len(args.URLs) > 4 {
		return nil, invalidArguments("urls must contain between 1 and 4 entries")
	}
	for index, value := range args.URLs {
		normalized, err := validatePublicURL(value)
		if err != nil {
			return nil, invalidArguments("urls[%d]: %v", index, err)
		}
		args.URLs[index] = normalized
	}
	if t.provider == nil {
		return nil, agent.ErrProviderUnavailable
	}
	results, err := t.provider.Fetch(ctx, WebFetchRequest{URLs: args.URLs})
	if err != nil {
		return nil, err
	}
	for index := range results {
		runes := []rune(results[index].Content)
		if len(runes) > maxFetchedContentRunes {
			results[index].Content = string(runes[:maxFetchedContentRunes])
			results[index].Truncated = true
		}
	}
	return map[string]any{"pages": results}, nil
}

type BraveConfig struct {
	APIKey     string
	Endpoint   string
	HTTPClient *http.Client
}

type BraveSearchProvider struct {
	apiKey     string
	endpoint   string
	httpClient *http.Client
}

func NewBraveSearchProvider(config BraveConfig) (*BraveSearchProvider, error) {
	if strings.TrimSpace(config.APIKey) == "" {
		return nil, fmt.Errorf("Brave API key is required")
	}
	endpoint := strings.TrimSpace(config.Endpoint)
	if endpoint == "" {
		endpoint = defaultBraveEndpoint
	}
	if _, err := validateProviderEndpoint(endpoint); err != nil {
		return nil, fmt.Errorf("Brave endpoint: %w", err)
	}
	client := config.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 30 * time.Second}
	}
	return &BraveSearchProvider{apiKey: config.APIKey, endpoint: endpoint, httpClient: client}, nil
}

func (p *BraveSearchProvider) Search(ctx context.Context, request WebSearchRequest) ([]WebSearchResult, error) {
	endpoint, _ := url.Parse(p.endpoint)
	query := endpoint.Query()
	query.Set("q", request.Query)
	query.Set("count", fmt.Sprintf("%d", request.MaxResults))
	query.Set("safesearch", "moderate")
	query.Set("text_decorations", "false")
	endpoint.RawQuery = query.Encode()
	httpRequest, err := http.NewRequestWithContext(ctx, http.MethodGet, endpoint.String(), nil)
	if err != nil {
		return nil, fmt.Errorf("build Brave request: %w", err)
	}
	httpRequest.Header.Set("Accept", "application/json")
	httpRequest.Header.Set("X-Subscription-Token", p.apiKey)
	response, err := p.httpClient.Do(httpRequest)
	if err != nil {
		return nil, fmt.Errorf("Brave search request: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return nil, fmt.Errorf("Brave search returned HTTP %s", response.Status)
	}
	var payload struct {
		Web struct {
			Results []struct {
				Title       string `json:"title"`
				URL         string `json:"url"`
				Description string `json:"description"`
				Age         string `json:"age"`
			} `json:"results"`
		} `json:"web"`
	}
	if err := decodeLimitedJSON(response.Body, &payload); err != nil {
		return nil, fmt.Errorf("decode Brave search response: %w", err)
	}
	results := make([]WebSearchResult, 0, min(request.MaxResults, len(payload.Web.Results)))
	for _, item := range payload.Web.Results {
		if len(results) >= request.MaxResults {
			break
		}
		results = append(results, WebSearchResult{
			SourceID:    fmt.Sprintf("web-%d", len(results)+1),
			Title:       strings.TrimSpace(item.Title),
			URL:         strings.TrimSpace(item.URL),
			Snippet:     strings.TrimSpace(item.Description),
			PublishedAt: strings.TrimSpace(item.Age),
		})
	}
	return results, nil
}

type TavilyConfig struct {
	APIKey     string
	Endpoint   string
	HTTPClient *http.Client
}

type TavilyFetchProvider struct {
	apiKey     string
	endpoint   string
	httpClient *http.Client
}

func NewTavilyFetchProvider(config TavilyConfig) (*TavilyFetchProvider, error) {
	if strings.TrimSpace(config.APIKey) == "" {
		return nil, fmt.Errorf("Tavily API key is required")
	}
	endpoint := strings.TrimSpace(config.Endpoint)
	if endpoint == "" {
		endpoint = defaultTavilyEndpoint
	}
	if _, err := validateProviderEndpoint(endpoint); err != nil {
		return nil, fmt.Errorf("Tavily endpoint: %w", err)
	}
	client := config.HTTPClient
	if client == nil {
		client = &http.Client{Timeout: 45 * time.Second}
	}
	return &TavilyFetchProvider{apiKey: config.APIKey, endpoint: endpoint, httpClient: client}, nil
}

func (p *TavilyFetchProvider) Fetch(ctx context.Context, request WebFetchRequest) ([]WebFetchResult, error) {
	body, err := json.Marshal(map[string]any{
		"api_key":       p.apiKey,
		"urls":          request.URLs,
		"format":        "markdown",
		"extract_depth": "basic",
	})
	if err != nil {
		return nil, fmt.Errorf("encode Tavily request: %w", err)
	}
	httpRequest, err := http.NewRequestWithContext(ctx, http.MethodPost, p.endpoint, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("build Tavily request: %w", err)
	}
	httpRequest.Header.Set("Content-Type", "application/json")
	response, err := p.httpClient.Do(httpRequest)
	if err != nil {
		return nil, fmt.Errorf("Tavily extract request: %w", err)
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return nil, fmt.Errorf("Tavily extract returned HTTP %s", response.Status)
	}
	var payload struct {
		Results []struct {
			URL        string `json:"url"`
			RawContent string `json:"raw_content"`
		} `json:"results"`
	}
	if err := decodeLimitedJSON(response.Body, &payload); err != nil {
		return nil, fmt.Errorf("decode Tavily extract response: %w", err)
	}
	results := make([]WebFetchResult, 0, len(payload.Results))
	for _, item := range payload.Results {
		results = append(results, WebFetchResult{
			SourceID: fmt.Sprintf("page-%d", len(results)+1),
			URL:      strings.TrimSpace(item.URL),
			Content:  strings.TrimSpace(item.RawContent),
		})
	}
	return results, nil
}

func validateProviderEndpoint(value string) (*url.URL, error) {
	parsed, err := url.Parse(value)
	if err != nil || parsed.Host == "" || parsed.User != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") {
		return nil, fmt.Errorf("must be an absolute HTTP(S) URL without credentials")
	}
	return parsed, nil
}

func validatePublicURL(value string) (string, error) {
	parsed, err := validateProviderEndpoint(strings.TrimSpace(value))
	if err != nil {
		return "", err
	}
	parsed.Fragment = ""
	return parsed.String(), nil
}

func decodeLimitedJSON(reader io.Reader, target any) error {
	limited := io.LimitReader(reader, maxWebResponseBytes+1)
	data, err := io.ReadAll(limited)
	if err != nil {
		return err
	}
	if len(data) > maxWebResponseBytes {
		return fmt.Errorf("response exceeded %d bytes", maxWebResponseBytes)
	}
	return json.Unmarshal(data, target)
}
