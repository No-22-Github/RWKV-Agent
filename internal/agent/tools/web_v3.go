package tools

import (
	"context"
	"encoding/json"
	"regexp"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// work-v3 web_fetch (docs/design/work-v3-tools.md §2.6, as revised
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

// WebToolsV3 is work-v3's web pair: web_search with a backend-neutral
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

func (t *webSearchV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
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
	var args struct {
		URLs       []string        `json:"urls"`
		MaxResults json.RawMessage `json:"max_results"`
	}
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
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
	results = fillMissingPages(args.URLs, results)
	truncated := t.fit(results)
	value := map[string]any{"pages": results}
	var notes []string
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
