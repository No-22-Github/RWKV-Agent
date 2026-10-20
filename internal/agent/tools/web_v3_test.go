package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

type fixedFetch map[string]string

func (f fixedFetch) Fetch(_ context.Context, request WebFetchRequest) ([]WebFetchResult, error) {
	var out []WebFetchResult
	for index, pageURL := range request.URLs {
		if content, ok := f[pageURL]; ok {
			out = append(out, WebFetchResult{SourceID: fmt.Sprintf("page-%d", index+1), URL: pageURL, Content: content})
		}
	}
	return out, nil
}

// longPage is ~6000 estimated tokens: a heading and a blank line every 50
// lines, 612 lines in all.
func longPage() string {
	var out strings.Builder
	for index := 1; index <= 600; index++ {
		if index%50 == 1 {
			fmt.Fprintf(&out, "## Section %d\n\n", index/50+1)
			continue
		}
		fmt.Fprintf(&out, "Paragraph line %d with some words to read about the topic.\n", index)
	}
	return out.String()
}

func fetchV3(t *testing.T, provider WebFetchProvider, urls ...string) map[string]any {
	t.Helper()
	tools := WebToolsV3(WebOptions{Fetch: provider})
	raw, _ := json.Marshal(map[string]any{"urls": urls})
	value, err := tools[1].Execute(context.Background(), raw)
	if err != nil {
		t.Fatal(err)
	}
	data, _ := json.Marshal(value)
	var out map[string]any
	if err := json.Unmarshal(data, &out); err != nil {
		t.Fatal(err)
	}
	return out
}

func TestWebFetchV3CutsLongPageAtWholeLines(t *testing.T) {
	provider := fixedFetch{"https://www.example.com/guide": longPage() + longPage(), "https://short.example.org/a": "# Short\n\nOnly a few words.\n"}
	got := fetchV3(t, provider, "https://www.example.com/guide", "https://short.example.org/a")
	pages := got["pages"].([]any)
	long, short := pages[0].(map[string]any), pages[1].(map[string]any)
	if long["truncated"] != true {
		t.Fatalf("long page not flagged: %v", long["truncated"])
	}
	content := long["content"].(string)
	if !strings.HasPrefix(content, "## Section 1") || !strings.HasSuffix(content, "the topic.") {
		t.Fatalf("long page not cut at a whole line: ...%q", content[len(content)-40:])
	}
	used := agent.EstimateTokens(content) + agent.EstimateTokens(short["content"].(string))
	if used > webFetchV3BudgetTokens || used < webFetchV3BudgetTokens-100 {
		t.Fatalf("pages use %d tokens, want just under %d", used, webFetchV3BudgetTokens)
	}
	if _, ok := short["truncated"]; ok || short["content"] != "# Short\n\nOnly a few words." {
		t.Fatalf("short page = %v", short)
	}
	if got["note"] != truncatedWebFetchNote {
		t.Fatalf("note = %v", got["note"])
	}
}

func TestWebFetchV3SplitsBudgetBetweenLongPages(t *testing.T) {
	provider := fixedFetch{"https://a.example.com/": longPage() + longPage(), "https://b.example.com/": longPage()}
	got := fetchV3(t, provider, "https://a.example.com/", "https://b.example.com/")
	total := 0
	for _, raw := range got["pages"].([]any) {
		page := raw.(map[string]any)
		tokens := agent.EstimateTokens(page["content"].(string))
		total += tokens
		if page["truncated"] != true || tokens < webFetchV3BudgetTokens/2-100 || tokens > webFetchV3BudgetTokens/2+100 {
			t.Fatalf("%v: %d tokens, truncated %v", page["url"], tokens, page["truncated"])
		}
	}
	if total > webFetchV3BudgetTokens {
		t.Fatalf("pages use %d tokens", total)
	}
}

func TestWebFetchV3ShortPageWhole(t *testing.T) {
	got := fetchV3(t, fixedFetch{"https://example.com/x": "# T\n\nBody line.\n"}, "https://example.com/x")
	page := got["pages"].([]any)[0].(map[string]any)
	if page["content"] != "# T\n\nBody line." || page["truncated"] != nil || got["note"] != nil {
		t.Fatalf("got %v", got)
	}
}

func TestStripLinkTargets(t *testing.T) {
	for in, want := range map[string]string{
		`See [Go](https://go.dev/ "Go home") and [x](https://en.wikipedia.org/wiki/Transformer_(deep_learning)).`: "See Go and x.",
		`Cited.[\[28\]](https://zh.wikipedia.org#cite_note-28)`:                                                   `Cited.\[28\]`,
		"![logo](https://cdn.example/a.png)\nText ![](x.png) end":                                                 "\nText  end",
		`[![badge](https://img.example/b.svg)](https://ci.example)`:                                               "",
		"plain [brackets] and (parens) stay":                                                                      "plain [brackets] and (parens) stay",
	} {
		if got := stripLinkTargets(in); got != want {
			t.Errorf("stripLinkTargets(%q) = %q, want %q", in, got, want)
		}
	}
}

func TestWebFetchV3EmptyPageKeepsProbeNote(t *testing.T) {
	got := fetchV3(t, fixedFetch{}, "https://missing.example.com/")
	if got["note"] != emptyWebFetchNote {
		t.Fatalf("note = %v", got["note"])
	}
}
