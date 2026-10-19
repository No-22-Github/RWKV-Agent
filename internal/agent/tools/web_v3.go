package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// work-v3 web_fetch (docs/design/work-v3-tools.md §2.6–§2.7): a short page is
// returned whole; a long page is saved under .web/ and only its opening lines
// and heading outline come back. The rest is read with read_file/search_text
// — restorable compression, no new arguments.
const (
	webFetchV3ShortTokens  = 3000
	webFetchV3HeadTokens   = 1200
	webFetchV3BudgetTokens = 6000
	webFetchV3Outline      = 40
	webFetchV3OutlineRunes = 80
)

const webFetchV3Description = "Fetch up to four public web pages as readable Markdown. A short page comes back whole; a long page is saved under .web/ and only its opening lines and outline come back, so read the rest with read_file or search_text."

const longWebFetchNote = "有的页面较长，只显示了开头。全文已存到 saved_as 里的文件：用 read_file 的 start_line 跳到 outline 里的章节，或用 search_text 在 .web/ 里搜关键词。"

// PageStore persists one archived page at .web/<name>.
type PageStore interface {
	SavePage(name, content string) error
}

// WebArchive names archived pages in call order (.web/<n>-<host>.md) so a
// replay of the same actions writes the same files.
type WebArchive struct {
	mu    sync.Mutex
	store PageStore
	count int
}

func NewWebArchive(store PageStore) *WebArchive { return &WebArchive{store: store} }

func (a *WebArchive) save(pageURL, content string) (string, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.count++
	name := fmt.Sprintf("%d-%s.md", a.count, archiveHost(pageURL))
	if err := a.store.SavePage(name, content); err != nil {
		a.count--
		return "", err
	}
	return agent.WebScratchDir + "/" + name, nil
}

var hostUnsafe = regexp.MustCompile(`[^a-z0-9.-]`)

func archiveHost(pageURL string) string {
	host := strings.ToLower(pageURL)
	if index := strings.Index(host, "://"); index >= 0 {
		host = host[index+3:]
	}
	if index := strings.IndexAny(host, "/?#"); index >= 0 {
		host = host[:index]
	}
	if index := strings.LastIndex(host, "@"); index >= 0 {
		host = host[index+1:]
	}
	if index := strings.Index(host, ":"); index >= 0 {
		host = host[:index]
	}
	host = hostUnsafe.ReplaceAllString(strings.TrimPrefix(host, "www."), "")
	if host == "" {
		return "page"
	}
	return host
}

// StagedPageStore writes archived pages into the staged workspace view, so
// bash sees them under /workspace/.web; the view hides that prefix from the
// file-changes panel and never applies it to disk.
type StagedPageStore struct{ View *StagedWorkspace }

func (s StagedPageStore) SavePage(name, content string) error {
	dir := filepath.Join(s.View.root, agent.WebScratchDir)
	if err := s.View.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	return s.View.WriteFile(filepath.Join(dir, name), []byte(content), 0o644)
}

// DirPageStore writes archived pages under Dir/.web on the host disk, for
// sessions without a staged workspace (agent.WorkspaceV3Options.ScratchDir).
type DirPageStore struct{ Dir string }

func (s DirPageStore) SavePage(name, content string) error {
	dir := filepath.Join(s.Dir, agent.WebScratchDir)
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(dir, name), []byte(content), 0o644)
}

// WebToolsV3 is work-v3's web pair: web_search with a backend-neutral
// description and the archiving web_fetch.
func WebToolsV3(options WebOptions, archive *WebArchive) []agent.Tool {
	return []agent.Tool{
		&webSearchV3Tool{inner: &webSearchTool{provider: options.Search}},
		&webFetchV3Tool{provider: options.Fetch, archive: archive, tokenCount: options.TokenCount},
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
	archive    *WebArchive
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
	budget := webFetchV3BudgetTokens
	archived := false
	for index := range results {
		page := &results[index]
		page.Content = strings.TrimSpace(page.Content)
		if page.Content == "" {
			continue
		}
		tokens := t.countTokens(page.Content)
		if tokens <= webFetchV3ShortTokens && tokens <= budget {
			budget -= tokens
			continue
		}
		stored := page.Content + "\n"
		if t.archive == nil {
			return nil, fmt.Errorf("web_fetch: no page archive configured")
		}
		saved, err := t.archive.save(page.URL, stored)
		if err != nil {
			return nil, err
		}
		lines := strings.Split(page.Content, "\n")
		head, used := t.head(lines, min(webFetchV3HeadTokens, budget))
		budget -= used
		page.Content = head
		page.SavedAs = saved
		page.TotalLines = len(lines)
		page.Outline = outline(lines)
		archived = true
	}
	value := map[string]any{"pages": results}
	var notes []string
	if archived {
		notes = append(notes, longWebFetchNote)
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

// head keeps whole leading lines within limit tokens.
func (t *webFetchV3Tool) head(lines []string, limit int) (string, int) {
	var out strings.Builder
	used := 0
	for _, line := range lines {
		cost := t.countTokens(line + "\n")
		if used+cost > limit {
			break
		}
		used += cost
		out.WriteString(line)
		out.WriteByte('\n')
	}
	return out.String(), used
}

var headingLine = regexp.MustCompile(`^#{1,3} \S`)

// outline lists the page's "#".."###" headings with their line numbers in the
// archived file; fewer than three headings is no outline.
func outline(lines []string) []string {
	var entries []string
	for index, line := range lines {
		if !headingLine.MatchString(line) {
			continue
		}
		text := line
		if utf8.RuneCountInString(text) > webFetchV3OutlineRunes {
			text = string([]rune(text)[:webFetchV3OutlineRunes]) + "…"
		}
		entries = append(entries, fmt.Sprintf("%d: %s", index+1, text))
		if len(entries) == webFetchV3Outline {
			break
		}
	}
	if len(entries) < 3 {
		return nil
	}
	return entries
}
