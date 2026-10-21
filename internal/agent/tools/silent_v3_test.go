package tools

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// The agent-tool-v3 fixes for results that went wrong without an error (A1–A4 of
// the 2026-10-21 tool review). Each test also pins agent-tool-v2.0's old behavior,
// which must stay byte-identical for historical runs.

func TestDataQueryV3FilterComparisons(t *testing.T) {
	root := writeWorkspace(t, map[string]string{
		"orders.csv": "sku,qty,status,date\nA,3,open,2026-10-01\nB,5,shipped,2026-10-05\nC,8,open,2026-10-09\n",
	})
	tools, err := LocalToolsV3(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	for filter, want := range map[string]float64{
		`{"qty":">3"}`:                 2,
		`{"qty":">=5"}`:                2,
		`{"qty":"< 5"}`:                1,
		`{"qty":"!=5"}`:                2,
		`{"qty":"=5"}`:                 1,
		`{"date":">=2026-10-05"}`:      2,
		`{"status":["open","closed"]}`: 2,
		`{"status":"open","qty":">3"}`: 1,
		`{"status":"OPEN"}`:            2,
	} {
		got, err := call(t, tools[1], `{"path":"orders.csv","operation":"count","filter":`+filter+`}`)
		if err != nil || got["matched_rows"].(float64) != want {
			t.Fatalf("filter %s matched %v, %v; want %v", filter, got["matched_rows"], err, want)
		}
	}
	// agent-tool-v2.0 keeps exact equality: ">3" is literal text and matches nothing.
	v2, err := LocalTools(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	for _, tool := range v2 {
		if tool.Spec().Name != "data_query" {
			continue
		}
		got, err := call(t, tool, `{"path":"orders.csv","filter":{"qty":">3"}}`)
		if err != nil || got["matched_rows"].(float64) != 0 {
			t.Fatalf("agent-tool-v2.0 filter drifted: %v, %v", got, err)
		}
	}
}

func TestAppendFileV3WholeLines(t *testing.T) {
	root := writeWorkspace(t, map[string]string{
		"open.txt": "alpha\nbeta",
		"done.txt": "alpha\n",
		"crlf.txt": "one\r\ntwo",
	})
	tools := v3Tools(t, root)
	for _, c := range []struct{ path, content, want string }{
		{"open.txt", "gamma", "alpha\nbeta\ngamma\n"},
		{"done.txt", "gamma\n", "alpha\ngamma\n"},
		{"done.txt", "x\ny", "alpha\ngamma\nx\ny\n"},
		{"crlf.txt", "three\nfour", "one\r\ntwo\r\nthree\r\nfour\r\n"},
		{"new.txt", "first", "first\n"},
	} {
		args, _ := json.Marshal(map[string]string{"path": c.path, "content": c.content})
		got, err := call(t, tools["append_file"], string(args))
		if err != nil {
			t.Fatal(err)
		}
		data, _ := os.ReadFile(filepath.Join(root, c.path))
		if string(data) != c.want {
			t.Fatalf("append %q to %s = %q, want %q", c.content, c.path, data, c.want)
		}
		if got["path"] != c.path {
			t.Fatalf("append result %v", got)
		}
	}
	// agent-tool-v2.0 appends the bytes as given.
	edits, err := FileEditTools(root, FileEditLines)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := call(t, edits[3], `{"path":"new.txt","content":"tail"}`); err != nil {
		t.Fatal(err)
	}
	if data, _ := os.ReadFile(filepath.Join(root, "new.txt")); string(data) != "first\ntail" {
		t.Fatalf("agent-tool-v2.0 append drifted: %q", data)
	}
}

func TestWorkspaceV3KeepsBuildDirs(t *testing.T) {
	root := writeWorkspace(t, map[string]string{
		"build/report.md":     "quarterly total\n",
		"dist/export.csv":     "quarterly,1\n",
		"node_modules/x/a.js": "quarterly\n",
		".git/HEAD":           "quarterly\n",
	})
	v3 := v3Tools(t, root)
	listed, err := call(t, v3["list_files"], `{}`)
	if err != nil {
		t.Fatal(err)
	}
	var paths []string
	for _, entry := range listed["entries"].([]any) {
		paths = append(paths, entry.(map[string]any)["path"].(string))
	}
	joined := strings.Join(paths, " ")
	if !strings.Contains(joined, "build/report.md") || !strings.Contains(joined, "dist/export.csv") ||
		strings.Contains(joined, "node_modules") || strings.Contains(joined, ".git") {
		t.Fatalf("agent-tool-v3 list_files = %v", paths)
	}
	found, err := call(t, v3["search_text"], `{"query":"quarterly"}`)
	if err != nil || len(found["matches"].([]any)) != 2 {
		t.Fatalf("agent-tool-v3 search_text = %v, %v", found, err)
	}
	// agent-tool-v2.0 still skips build/ and dist/.
	v2, err := agent.WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	old, err := call(t, v2[0], `{}`)
	if err != nil || len(old["entries"].([]any)) != 0 {
		t.Fatalf("agent-tool-v2.0 list_files drifted: %v, %v", old, err)
	}
}

func TestFileToolsV3CRLF(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"crlf.txt": "one\r\ntwo\r\nthree\r\n"})
	tools := v3Tools(t, root)
	got, err := call(t, tools["read_file"], `{"path":"crlf.txt"}`)
	if err != nil || got["content"] != "1: one\n2: two\n3: three\n" {
		t.Fatalf("read CRLF = %q, %v", got["content"], err)
	}
	got, err = call(t, tools["replace_lines"], `{"path":"crlf.txt","start_line":2,"end_line":2,"content":"TWO\r\nTWO-B"}`)
	if err != nil || got["around"] != "1: one\n2: TWO\n3: TWO-B\n4: three\n" {
		t.Fatalf("replace CRLF = %v, %v", got, err)
	}
	if data, _ := os.ReadFile(filepath.Join(root, "crlf.txt")); string(data) != "one\r\nTWO\r\nTWO-B\r\nthree\r\n" {
		t.Fatalf("CRLF file rewritten as %q", data)
	}
	// An LF file stays LF.
	root = writeWorkspace(t, map[string]string{"lf.txt": "a\nb\n"})
	tools = v3Tools(t, root)
	if _, err := call(t, tools["replace_lines"], `{"path":"lf.txt","start_line":1,"end_line":1,"content":"A"}`); err != nil {
		t.Fatal(err)
	}
	if data, _ := os.ReadFile(filepath.Join(root, "lf.txt")); string(data) != "A\nb\n" {
		t.Fatalf("LF file rewritten as %q", data)
	}
}
