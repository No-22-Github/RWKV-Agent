package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// agent-tool-v3 web_fetch (docs/design/agent-tool-v3.md §2.6, as revised
// 2026-10-20): Markdown link targets and images are dropped, then the pages
// share one 6000-token budget; a page over its share keeps its leading whole
// lines and is flagged truncated. The 10-20 long-page probe found the MiSS
// weights summarize soundly up to ~12K tokens of page but read facts reliably
// only to ~6K, and the archive-then-read path (.web/) asked too much of a 7B
// model, so long pages are cut rather than archived.
const webFetchV3BudgetTokens = 6000

const webFetchV3Description = "Fetch up to four public web pages as readable Markdown. A long page comes back cut to its opening part."

const truncatedWebFetchNote = "有的页面较长，只给出了前面一部分（truncated 为 true），后面已省略；重复抓取同一网址也拿不到更多内容。"

var (
	markdownImage = regexp.MustCompile(`!\[(?:\\.|[^\]\\])*\]\((?:[^()\s]|\([^()]*\))*(?:\s+"[^"]*")?\)`)
	markdownLink  = regexp.MustCompile(`\[((?:\\.|[^\]\\])*)\]\((?:[^()\s]|\([^()]*\))*(?:\s+"[^"]*")?\)`)
)

// stripLinkTargets drops images and keeps only the text of inline links: on
// real pages the URLs are most of the tokens (a Wikipedia article halves)
// and the model answers from the text; the page's own URL stays in the result.
func stripLinkTargets(content string) string {
	content = markdownImage.ReplaceAllString(content, "")
	return markdownLink.ReplaceAllString(content, "$1")
}

// WebToolsV3 is agent-tool-v3's web pair: web_search with a backend-neutral
// description and the cutting web_fetch.
func WebToolsV3(options WebOptions) []agent.Tool {
	return []agent.Tool{
		&webSearchV3Tool{inner: &webSearchTool{provider: options.Search}},
		&webFetchV3Tool{provider: options.Fetch, tokenCount: options.TokenCount},
	}
}

type webSearchV3Tool struct{ inner *webSearchTool }

func (t *webSearchV3Tool) Spec() agent.ToolSpec {
	spec := t.inner.Spec()
	spec.Description = "Search the public web and return titles, URLs, snippets, and source IDs."
	return spec
}

// Execute clamps max_results into 1..10 instead of rejecting the call: it is
// only a cap, and a model asking for 20 wants "as many as there are".
func (t *webSearchV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var fields map[string]json.RawMessage
	if json.Unmarshal(raw, &fields) == nil {
		var value any
		if json.Unmarshal(fields["max_results"], &value) == nil {
			if number, ok := dataNumber(value); ok && (number < 0 || number > 10) {
				// 0 already means the default (5); a negative count does too.
				fields["max_results"] = json.RawMessage(strconv.Itoa(int(min(max(number, 0), 10))))
				if clamped, err := json.Marshal(fields); err == nil {
					raw = clamped
				}
			}
		}
	}
	return t.inner.Execute(ctx, raw)
}

type webFetchV3Tool struct {
	provider   WebFetchProvider
	tokenCount func(string) int
}

func (t *webFetchV3Tool) Spec() agent.ToolSpec {
	spec := (&webFetchTool{}).Spec()
	spec.Description = webFetchV3Description
	return spec
}

func (t *webFetchV3Tool) countTokens(text string) int {
	if t.tokenCount != nil {
		return t.tokenCount(text)
	}
	return fallbackEstimateTokens(text)
}

func (t *webFetchV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	urls, err := decodeFetchURLs(raw)
	if err != nil {
		return nil, err
	}
	var dropped []string
	if len(urls) > webFetchV3MaxPages {
		urls, dropped = urls[:webFetchV3MaxPages], urls[webFetchV3MaxPages:]
	}
	for index, value := range urls {
		normalized, err := validatePublicURL(withScheme(value))
		if err != nil {
			return nil, invalidArguments("urls[%d]: %v", index, err)
		}
		urls[index] = normalized
	}
	if t.provider == nil {
		return nil, agent.ErrProviderUnavailable
	}
	results, err := t.provider.Fetch(ctx, WebFetchRequest{URLs: urls})
	if err != nil {
		return nil, err
	}
	results = fillMissingPages(urls, results)
	truncated := t.fit(results)
	value := map[string]any{"pages": results}
	var notes []string
	if len(dropped) > 0 {
		notes = append(notes, fmt.Sprintf(webFetchV3DroppedNote, webFetchV3MaxPages, strings.Join(dropped, " ")))
	}
	if truncated {
		notes = append(notes, truncatedWebFetchNote)
	}
	if !WebFetchHasContent(value) {
		notes = append(notes, emptyWebFetchNote)
	} else if blankPages(results) > 0 {
		notes = append(notes, partialWebFetchNote)
	}
	if len(notes) > 0 {
		value["note"] = strings.Join(notes, "；")
	}
	return value, nil
}

const (
	webFetchV3MaxPages    = 4
	webFetchV3DroppedNote = "一次最多抓 %d 个网址，这几个没有抓：%s。需要的话再调用一次。"
)

// decodeFetchURLs reads web_fetch's urls the ways models actually send them:
// the documented array, a single string in urls, or a singular url (string or
// array). Measured on the 10-21 probe, each of those was a hard argument error
// before. max_results stays accepted and ignored, as in agent-tool-v2.0.
func decodeFetchURLs(raw json.RawMessage) ([]string, error) {
	var args struct {
		URLs       json.RawMessage `json:"urls"`
		URL        json.RawMessage `json:"url"`
		MaxResults json.RawMessage `json:"max_results"`
	}
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	var urls []string
	for _, field := range []json.RawMessage{args.URLs, args.URL} {
		if len(field) == 0 || string(field) == "null" {
			continue
		}
		var list []string
		if err := json.Unmarshal(field, &list); err != nil {
			var single string
			if err := json.Unmarshal(field, &single); err != nil {
				return nil, invalidArguments(`urls must be a list of web addresses, such as {"urls":["https://example.com/page"]}`)
			}
			list = []string{single}
		}
		for _, value := range list {
			if value = strings.TrimSpace(value); value != "" {
				urls = append(urls, value)
			}
		}
	}
	if len(urls) == 0 {
		return nil, invalidArguments(`urls must contain at least one web address, such as {"urls":["https://example.com/page"]}`)
	}
	return urls, nil
}

// withScheme adds https:// to a bare host such as "example.com/page"; a value
// that already names a scheme is left for validatePublicURL to judge.
func withScheme(value string) string {
	if strings.Contains(value, "://") {
		return value
	}
	host, _, _ := strings.Cut(strings.TrimPrefix(value, "//"), "/")
	if !strings.Contains(host, ".") || strings.ContainsAny(host, " @") {
		return value
	}
	return "https://" + strings.TrimPrefix(value, "//")
}

// fit strips link targets and cuts the pages to the shared budget. Pages are
// served smallest first, each taking at most an even share of what is left, so
// a short page is never cut to make room for a long one and two long pages
// split the budget. It reports whether any page was cut.
func (t *webFetchV3Tool) fit(results []WebFetchResult) bool {
	tokens := make([]int, len(results))
	var order []int
	for index := range results {
		page := &results[index]
		page.Content = strings.TrimSpace(stripLinkTargets(page.Content))
		if page.Content == "" {
			continue
		}
		tokens[index] = t.countTokens(page.Content)
		order = append(order, index)
	}
	sort.SliceStable(order, func(a, b int) bool { return tokens[order[a]] < tokens[order[b]] })
	budget, cut := webFetchV3BudgetTokens, false
	for position, index := range order {
		share := budget / (len(order) - position)
		if tokens[index] <= share {
			budget -= tokens[index]
			continue
		}
		head, used := t.head(results[index].Content, share)
		results[index].Content = head
		results[index].Truncated = true
		budget -= used
		cut = true
	}
	return cut
}

// head keeps the most whole leading lines whose text fits limit tokens,
// measured on the joined prefix (per-line counts do not add up exactly); a
// first line longer than the limit is cut by runes instead.
func (t *webFetchV3Tool) head(content string, limit int) (string, int) {
	lines := strings.SplitAfter(content, "\n")
	prefix := func(n int) string { return strings.TrimRight(strings.Join(lines[:n], ""), "\n") }
	low, high := 0, len(lines)
	for low < high {
		mid := (low + high + 1) / 2
		if t.countTokens(prefix(mid)) <= limit {
			low = mid
		} else {
			high = mid - 1
		}
	}
	if low > 0 {
		text := prefix(low)
		return text, t.countTokens(text)
	}
	runes := []rune(lines[0])
	low, high = 0, len(runes)
	for low < high {
		mid := (low + high + 1) / 2
		if t.countTokens(string(runes[:mid])) <= limit {
			low = mid
		} else {
			high = mid - 1
		}
	}
	text := string(runes[:low])
	return text, t.countTokens(text)
}
