package tools

import (
	"context"
	"encoding/json"
	"errors"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// The work-v3 argument leniency and feedback of the 2026-10-21 tool review
// (B1–B5, C1–C3). None of it changes a description or argument text, so the
// catalog hash stays; work-v2 keeps rejecting what it rejected.

func TestWebFetchV3AcceptsURLSpellings(t *testing.T) {
	provider := fixedFetch{"https://example.org/a": "A", "https://example.org/b": "B"}
	tool := WebToolsV3(WebOptions{Fetch: provider})[1]
	for _, args := range []string{
		`{"url":"https://example.org/a"}`,
		`{"urls":"https://example.org/a"}`,
		`{"url":["https://example.org/a"]}`,
		`{"urls":["example.org/a"]}`,
		`{"urls":["//example.org/a"]}`,
	} {
		got, err := call(t, tool, args)
		if err != nil {
			t.Fatalf("%s: %v", args, err)
		}
		pages := got["pages"].([]any)
		if len(pages) != 1 || pages[0].(map[string]any)["content"] != "A" {
			t.Fatalf("%s = %v", args, got)
		}
	}
	got, err := call(t, tool, `{"urls":["https://example.org/a","https://example.org/b","https://x.org/3","https://x.org/4","https://x.org/5"]}`)
	if err != nil || !strings.Contains(got["note"].(string), "https://x.org/5") {
		t.Fatalf("five urls = %v, %v", got, err)
	}
	for _, args := range []string{`{"urls":[]}`, `{"urls":["localhost"]}`, `{"urls":[1]}`} {
		if _, err := call(t, tool, args); !errors.Is(err, agent.ErrInvalidToolArguments) {
			t.Fatalf("%s: want argument error, got %v", args, err)
		}
	}
	// work-v2 keeps the strict shape.
	if _, err := call(t, WebTools(WebOptions{Fetch: provider})[1], `{"url":"https://example.org/a"}`); err == nil {
		t.Fatal("work-v2 web_fetch accepted url")
	}
}

type countingSearch struct{ got *int }

func (s countingSearch) Search(_ context.Context, request WebSearchRequest) ([]WebSearchResult, error) {
	*s.got = request.MaxResults
	return []WebSearchResult{{SourceID: "s1", Title: "t", URL: "https://example.org", Snippet: "x"}}, nil
}

func TestWebSearchV3ClampsMaxResults(t *testing.T) {
	var got int
	tool := WebToolsV3(WebOptions{Search: countingSearch{&got}})[0]
	for args, want := range map[string]int{`{"query":"x","max_results":20}`: 10, `{"query":"x","max_results":"50"}`: 10, `{"query":"x","max_results":-1}`: 5, `{"query":"x","max_results":null}`: 5, `{"query":"x","max_results":3}`: 3} {
		if _, err := call(t, tool, args); err != nil || got != want {
			t.Fatalf("%s sent %d, %v; want %d", args, got, err, want)
		}
	}
	if _, err := call(t, WebTools(WebOptions{Search: countingSearch{&got}})[0], `{"query":"x","max_results":20}`); err == nil {
		t.Fatal("work-v2 web_search accepted 20")
	}
}

func TestWorkspaceV3LimitsNotesAndMissingPaths(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"a.txt": "alpha\nbeta\n", "dir/b.txt": "gamma\n"})
	v3 := v3Tools(t, root)
	if _, err := call(t, v3["list_files"], `{"max_depth":20,"max_results":1000}`); err != nil {
		t.Fatalf("list_files clamp: %v", err)
	}
	if _, err := call(t, v3["search_text"], `{"query":"alpha","max_results":999}`); err != nil {
		t.Fatalf("search_text clamp: %v", err)
	}
	got, err := call(t, v3["search_text"], `{"query":"alpha|beta"}`)
	if err != nil || !strings.Contains(got["note"].(string), "不支持正则") {
		t.Fatalf("regex query = %v, %v", got, err)
	}
	got, err = call(t, v3["search_text"], `{"query":"delta"}`)
	if err != nil || !strings.Contains(got["note"].(string), "换一个更短的关键词") {
		t.Fatalf("empty query = %v, %v", got, err)
	}
	if got, _ := call(t, v3["search_text"], `{"query":"alpha"}`); got["note"] != nil {
		t.Fatalf("a hit must not carry a note: %v", got)
	}
	for name, args := range map[string]string{
		"read_file":     `{"path":"nope.txt"}`,
		"list_files":    `{"path":"nope"}`,
		"search_text":   `{"query":"x","path":"nope"}`,
		"replace_lines": `{"path":"nope.txt","start_line":1,"end_line":1,"content":"x"}`,
	} {
		_, err := call(t, v3[name], args)
		if err == nil || !strings.HasPrefix(err.Error(), "找不到 nope") || strings.Contains(err.Error(), root) {
			t.Fatalf("%s missing path = %v", name, err)
		}
	}
	if _, err := call(t, v3["list_files"], `{"path":"a.txt"}`); err == nil || !strings.Contains(err.Error(), "用 read_file") {
		t.Fatalf("list_files on a file = %v", err)
	}
	if _, err := call(t, v3["read_file"], `{"path":"dir"}`); err == nil || !strings.Contains(err.Error(), "用 list_files") {
		t.Fatalf("read_file on a directory = %v", err)
	}
	// work-v2 keeps its English errors, its bounds and no note.
	v2, err := agent.WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := call(t, v2[1], `{"path":"nope.txt"}`); err == nil || !strings.Contains(err.Error(), "no such file") {
		t.Fatalf("work-v2 missing path = %v", err)
	}
	if _, err := call(t, v2[0], `{"max_results":1000}`); err == nil {
		t.Fatal("work-v2 list_files accepted 1000")
	}
	if got, _ := call(t, v2[2], `{"query":"delta"}`); got["note"] != nil {
		t.Fatalf("work-v2 search_text got a note: %v", got)
	}
}

func TestReadFileV3PagingSpellings(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"big.log": numberedFile(500, 20)})
	tool := v3Tools(t, root)["read_file"]
	for args, want := range map[string][2]float64{
		`{"path":"big.log","offset":10,"limit":5}`:                   {10, 14},
		`{"file_path":"big.log","offset":"300"}`:                     {300, 499},
		`{"path":"big.log","offset":0,"limit":3}`:                    {1, 3},
		`{"path":"big.log","start_line":7,"offset":50,"limit":2}`:    {7, 8},
		`{"path":"big.log","start_line":null,"end_line":null}`:       {1, 200},
		`{"path":"big.log","start_line":20,"end_line":21,"limit":9}`: {20, 21},
	} {
		got, err := call(t, tool, args)
		if err != nil || got["start_line"].(float64) != want[0] || got["end_line"].(float64) != want[1] {
			t.Fatalf("%s = %v..%v, %v; want %v", args, got["start_line"], got["end_line"], err, want)
		}
	}
}

func TestDataQueryV3RowsAndFormattedNumbers(t *testing.T) {
	var csv strings.Builder
	csv.WriteString("sku,qty,price\n")
	for index := 0; index < 150; index++ {
		csv.WriteString("A,1,\"$1,200.50\"\n")
	}
	root := writeWorkspace(t, map[string]string{"orders.csv": csv.String(), "small.csv": "sku,price\nA,\"1,200\"\nB,80\n"})
	tools, err := LocalToolsV3(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	query := tools[1]
	got, err := call(t, query, `{"path":"orders.csv"}`)
	if err != nil || len(got["rows"].([]any)) != 100 || !strings.Contains(got["note"].(string), "共匹配 150 行") {
		t.Fatalf("150 rows = %d, %v, %v", len(got["rows"].([]any)), got["note"], err)
	}
	got, err = call(t, query, `{"path":"orders.csv","limit":"5"}`)
	if err != nil || len(got["rows"].([]any)) != 5 || !strings.Contains(got["note"].(string), "只列出了前 5 行") {
		t.Fatalf("limit 5 = %v, %v", got["note"], err)
	}
	got, err = call(t, query, `{"path":"small.csv","operation":"sum","field":"price"}`)
	if err != nil || got["value"].(float64) != 1280 {
		t.Fatalf("sum of formatted prices = %v, %v", got, err)
	}
	for filter, want := range map[string]float64{`{"price":">1000"}`: 1, `{"price":"1,200"}`: 1, `{"price":"<= $100"}`: 1} {
		got, err := call(t, query, `{"path":"small.csv","filter":`+filter+`}`)
		if err != nil || got["matched_rows"].(float64) != want {
			t.Fatalf("filter %s = %v, %v", filter, got["matched_rows"], err)
		}
	}
	if got, _ := call(t, query, `{"path":"small.csv"}`); got["note"] != nil {
		t.Fatalf("all rows listed must not carry a note: %v", got)
	}
}

func TestCalculatorV3Spellings(t *testing.T) {
	for expression, want := range map[string]float64{
		"1,200*3":          3600,
		"200*15%":          30,
		"(200*15%)+1":      31,
		"10%3":             1,
		"3×4÷2":            6,
		"（1+2）*3":          9,
		"math.sqrt(16)":    4,
		"pow(2,10)":        1024,
		"max(1,200)":       200,
		"12,345.5 - 0.5 =": 12345,
		"1,000,000/4":      250000,
	} {
		got, err := calcV3(t, expression)
		if err != nil || got.Result != want {
			t.Fatalf("%s = %v, %v; want %v", expression, got.Result, err, want)
		}
	}
	if _, err := calcV3(t, "a.b(2)"); err == nil || strings.Contains(err.Error(), "only abs, min, max, and round") {
		t.Fatalf("selector call error = %v", err)
	}
	// work-v2 is unchanged.
	raw, _ := json.Marshal(map[string]any{"expression": "1,200*3", "precision": nil})
	if _, err := (calculatorTool{}).Execute(context.Background(), raw); err == nil {
		t.Fatal("work-v2 calculator accepted 1,200")
	}
}

type wednesdayClock struct{}

func (wednesdayClock) Now() time.Time {
	return time.Date(2026, 10, 21, 9, 0, 0, 0, time.FixedZone("CST", 8*3600))
}

func TestDatetimeV3(t *testing.T) {
	tools, err := LocalToolsV3(Options{Workspace: t.TempDir(), Clock: wednesdayClock{}})
	if err != nil {
		t.Fatal(err)
	}
	tool := tools[2]
	got, err := call(t, tool, `{"op":"today"}`)
	if err != nil || got["weekday"] != "星期三" || got["now"] != "2026-10-21T09:00:00+08:00" {
		t.Fatalf("now = %v, %v", got, err)
	}
	got, err = call(t, tool, `{"op":"diff","args":{"left":"2026-10-21","right":"2026-12-25"}}`)
	if err != nil || got["days_between"].(float64) != 65 || got["relation"].(float64) != -1 || got["right_weekday"] != "星期五" {
		t.Fatalf("compare = %v, %v", got, err)
	}
	for duration, want := range map[string]string{
		"3d":      "2026-10-24T00:00:00+08:00",
		"2w":      "2026-11-04T00:00:00+08:00",
		"1d12h":   "2026-10-22T12:00:00+08:00",
		"3天":      "2026-10-24T00:00:00+08:00",
		"1 month": "2026-11-21T00:00:00+08:00",
		"-1y":     "2025-10-21T00:00:00+08:00",
		"-30m":    "2026-10-20T23:30:00+08:00",
	} {
		got, err := call(t, tool, `{"op":"add","args":{"time":"2026-10-21","duration":"`+duration+`"}}`)
		if err != nil || got["result"] != want {
			t.Fatalf("add %s = %v, %v; want %s", duration, got, err, want)
		}
	}
	if _, err := call(t, tool, `{"op":"add","args":{"time":"2026-10-21","duration":"soon"}}`); err == nil || !strings.Contains(err.Error(), "3d") {
		t.Fatalf("bad duration = %v", err)
	}
	// work-v2 keeps relation only and Go durations only.
	v2 := &datetimeTool{clock: wednesdayClock{}}
	got, err = call(t, v2, `{"op":"compare","args":{"left":"2026-10-21","right":"2026-12-25"}}`)
	if err != nil || got["days_between"] != nil {
		t.Fatalf("work-v2 compare drifted: %v, %v", got, err)
	}
	if _, err := call(t, v2, `{"op":"add","args":{"time":"2026-10-21","duration":"3d"}}`); err == nil {
		t.Fatal("work-v2 datetime accepted 3d")
	}
}
