package tools

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
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

func fetchV3(t *testing.T, provider WebFetchProvider, archive *WebArchive, urls ...string) map[string]any {
	t.Helper()
	tools := WebToolsV3(WebOptions{Fetch: provider}, archive)
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

func TestWebFetchV3ArchivesLongPageWithOutline(t *testing.T) {
	scratch := t.TempDir()
	provider := fixedFetch{"https://www.example.com/guide": longPage(), "https://short.example.org/a": "# Short\n\nOnly a few words.\n"}
	got := fetchV3(t, provider, NewWebArchive(DirPageStore{Dir: scratch}), "https://www.example.com/guide", "https://short.example.org/a")
	pages := got["pages"].([]any)
	long, short := pages[0].(map[string]any), pages[1].(map[string]any)
	if long["saved_as"] != ".web/1-example.com.md" || long["total_lines"].(float64) != 612 {
		t.Fatalf("long page = %v %v", long["saved_as"], long["total_lines"])
	}
	if _, ok := short["saved_as"]; ok || short["content"] != "# Short\n\nOnly a few words." {
		t.Fatalf("short page = %v", short)
	}
	if !strings.HasPrefix(got["note"].(string), "有的页面较长") {
		t.Fatalf("note = %v", got["note"])
	}
	// Every outline line number must point at that heading in the archived
	// file as read_file numbers it (work-v3 §4.3 item 5).
	read, _, err := FileToolsV3("", nil, agent.WorkspaceV3Options{ScratchDir: scratch})
	if err != nil {
		t.Fatal(err)
	}
	for _, raw := range long["outline"].([]any) {
		entry := raw.(string)
		number := entry[:strings.Index(entry, ":")]
		args := fmt.Sprintf(`{"path":".web/1-example.com.md","start_line":%s,"end_line":%s}`, number, number)
		value, err := read.Execute(context.Background(), json.RawMessage(args))
		if err != nil {
			t.Fatal(err)
		}
		if line := value.(readFileV3Result).Content; strings.TrimSuffix(line, "\n") != entry {
			t.Fatalf("outline %q points at %q", entry, line)
		}
	}
}

func TestWebFetchV3ReplayIsDeterministic(t *testing.T) {
	run := func() string {
		scratch := t.TempDir()
		got := fetchV3(t, fixedFetch{"https://example.com/x": longPage()}, NewWebArchive(DirPageStore{Dir: scratch}), "https://example.com/x")
		data, _ := json.Marshal(got)
		saved, err := os.ReadFile(filepath.Join(scratch, ".web", "1-example.com.md"))
		if err != nil {
			t.Fatal(err)
		}
		return string(data) + string(saved)
	}
	if run() != run() {
		t.Fatal("two replays differ")
	}
}

func TestWebFetchV3EmptyPageKeepsProbeNote(t *testing.T) {
	got := fetchV3(t, fixedFetch{}, NewWebArchive(DirPageStore{Dir: t.TempDir()}), "https://missing.example.com/")
	if got["note"] != emptyWebFetchNote {
		t.Fatalf("note = %v", got["note"])
	}
}

func TestStagedArchiveHiddenFromReview(t *testing.T) {
	bash, root := newTestBashTool(t)
	view := bash.overlay
	view.HideFromReview(agent.WebScratchDir)
	archive := NewWebArchive(StagedPageStore{View: view})
	fetchV3(t, fixedFetch{"https://example.com/x": longPage()}, archive, "https://example.com/x")
	if out := runBash(t, bash, "wc -l < .web/1-example.com.md"); strings.TrimSpace(out.Stdout) != "612" {
		t.Fatalf("bash cannot read the archive: %+v", out)
	}
	runBash(t, bash, "echo hi > note.txt")
	changes, err := view.Changes()
	if err != nil {
		t.Fatal(err)
	}
	if len(changes) != 1 || changes[0].Path != "note.txt" {
		t.Fatalf("changes = %+v", changes)
	}
	if _, err := view.Resolve(changes, true); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(filepath.Join(root, ".web")); !os.IsNotExist(err) {
		t.Fatalf(".web reached the disk: %v", err)
	}
}
