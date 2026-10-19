package tools

import (
	"context"
	"fmt"
	"io"
	"net/http"
	nurl "net/url"
	"strings"
	"time"

	readability "codeberg.org/readeck/go-readability/v2"
	htmltomarkdown "github.com/JohannesKaufmann/html-to-markdown/v2"
	"github.com/JohannesKaufmann/html-to-markdown/v2/converter"
	"golang.org/x/net/html/charset"
)

// ReadabilityFetch reads pages itself: plain HTTP GET, go-readability for the
// main content, html-to-markdown for Markdown (work-v3 §2.6). It needs no key.
// A page it cannot read comes back with empty content, so FallbackFetch hands
// it to the next backend (Tavily / DeepSeek).
type ReadabilityFetch struct {
	Client *http.Client
}

const (
	readabilityTimeout   = 15 * time.Second
	readabilityMaxBytes  = 5 << 20
	readabilityMinLength = 200
	readabilityUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

// Anti-bot interstitials (2026-10-19: Ctrip returned "请完成下面的验证测试").
var antiBotMarkers = []string{"请完成下面的验证", "verify you are human", "Just a moment", "请输入验证码", "Access Denied"}

func (f ReadabilityFetch) Fetch(ctx context.Context, request WebFetchRequest) ([]WebFetchResult, error) {
	results := make([]WebFetchResult, 0, len(request.URLs))
	for index, pageURL := range request.URLs {
		title, content := f.read(ctx, pageURL)
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		results = append(results, WebFetchResult{
			SourceID: fmt.Sprintf("page-%d", index+1), URL: pageURL, Title: title, Content: content,
		})
	}
	return results, nil
}

func (f ReadabilityFetch) read(ctx context.Context, pageURL string) (string, string) {
	parsed, err := nurl.Parse(pageURL)
	if err != nil {
		return "", ""
	}
	ctx, cancel := context.WithTimeout(ctx, readabilityTimeout)
	defer cancel()
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, pageURL, nil)
	if err != nil {
		return "", ""
	}
	req.Header.Set("User-Agent", readabilityUserAgent)
	req.Header.Set("Accept", "text/html,application/xhtml+xml")
	client := f.Client
	if client == nil {
		client = http.DefaultClient
	}
	resp, err := client.Do(req)
	if err != nil {
		return "", ""
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return "", ""
	}
	contentType := resp.Header.Get("Content-Type")
	if contentType != "" && !strings.Contains(contentType, "html") {
		return "", ""
	}
	body, err := charset.NewReader(io.LimitReader(resp.Body, readabilityMaxBytes), contentType)
	if err != nil {
		return "", ""
	}
	article, err := readability.FromReader(body, parsed)
	if err != nil {
		return "", ""
	}
	var html strings.Builder
	if err := article.RenderHTML(&html); err != nil {
		return "", ""
	}
	markdown, err := htmltomarkdown.ConvertString(html.String(), converter.WithDomain(parsed.Scheme+"://"+parsed.Host))
	if err != nil {
		return "", ""
	}
	markdown = strings.TrimSpace(markdown)
	if len([]rune(markdown)) < readabilityMinLength {
		return "", ""
	}
	head := markdown
	if len(head) > 2000 {
		head = head[:2000]
	}
	for _, marker := range antiBotMarkers {
		if strings.Contains(head, marker) {
			return "", ""
		}
	}
	title := strings.TrimSpace(article.Title())
	if title != "" && !strings.HasPrefix(markdown, "#") {
		markdown = "# " + title + "\n\n" + markdown
	}
	return title, markdown
}
