package tools

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

var updateGolden = flag.Bool("update", false, "rewrite testdata goldens")

func writeWorkspace(t *testing.T, files map[string]string) string {
	t.Helper()
	root := t.TempDir()
	for name, content := range files {
		path := filepath.Join(root, name)
		if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

func numberedFile(lines, width int) string {
	var out strings.Builder
	for index := 1; index <= lines; index++ {
		line := fmt.Sprintf("line %d ", index)
		out.WriteString(line + strings.Repeat("x", max(0, width-len(line))) + "\n")
	}
	return out.String()
}

func call(t *testing.T, tool agent.Tool, args string) (map[string]any, error) {
	t.Helper()
	value, err := tool.Execute(context.Background(), json.RawMessage(args))
	if err != nil {
		return nil, err
	}
	data, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	var out map[string]any
	if err := json.Unmarshal(data, &out); err != nil {
		t.Fatal(err)
	}
	return out, nil
}

func v3Tools(t *testing.T, root string, options agent.WorkspaceV3Options) map[string]agent.Tool {
	t.Helper()
	read, edits, err := FileToolsV3(root, nil, options)
	if err != nil {
		t.Fatal(err)
	}
	workspace, err := agent.WorkspaceToolsV3(root, nil, options)
	if err != nil {
		t.Fatal(err)
	}
	out := map[string]agent.Tool{}
	for _, tool := range append(append([]agent.Tool{read}, edits...), workspace...) {
		out[tool.Spec().Name] = tool
	}
	return out
}

func TestReadFileV3FirstScreenAndNote(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"big.log": numberedFile(5000, 20)})
	got, err := call(t, v3Tools(t, root, agent.WorkspaceV3Options{})["read_file"], `{"path":"big.log","start_line":null,"end_line":null}`)
	if err != nil {
		t.Fatal(err)
	}
	if got["end_line"].(float64) != 200 || got["total_lines"].(float64) != 5000 {
		t.Fatalf("window = %v..%v of %v", got["start_line"], got["end_line"], got["total_lines"])
	}
	want := "只显示了第 1–200 行，文件共 5000 行。往后读用 start_line=201；要查找或统计，用 search_text，或用 bash 的 grep、wc、awk 处理整个文件。"
	if got["note"] != want {
		t.Fatalf("note = %q\nwant %q", got["note"], want)
	}
	if !strings.HasPrefix(got["content"].(string), "1: line 1 ") || strings.Count(got["content"].(string), "\n") != 200 {
		t.Fatalf("content not 200 numbered lines: %.80q", got["content"])
	}
}

func TestReadFileV3ByteCap(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"wide.csv": numberedFile(300, 100)})
	got, err := call(t, v3Tools(t, root, agent.WorkspaceV3Options{})["read_file"], `{"path":"wide.csv","start_line":null,"end_line":null}`)
	if err != nil {
		t.Fatal(err)
	}
	// 101 bytes per line with its newline: 12 KiB holds 121 lines.
	if end := got["end_line"].(float64); end != 121 {
		t.Fatalf("end_line = %v, want 121 (12 KiB cap)", end)
	}
}

func TestReadFileV3ReadsPast64KiB(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"huge.txt": numberedFile(3000, 40)})
	tools := v3Tools(t, root, agent.WorkspaceV3Options{})
	got, err := call(t, tools["read_file"], `{"path":"huge.txt","start_line":2900,"end_line":null}`)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.HasPrefix(got["content"].(string), "2900: line 2900 ") || got["total_lines"].(float64) != 3000 {
		t.Fatalf("got %.60q total %v", got["content"], got["total_lines"])
	}
	if _, ok := got["note"]; ok {
		t.Fatalf("last screen must not carry a note: %v", got["note"])
	}
	past, err := call(t, tools["read_file"], `{"path":"huge.txt","start_line":3005,"end_line":null}`)
	if err != nil {
		t.Fatal(err)
	}
	if past["note"] != "文件只有 3000 行，没有第 3005 行。" || past["content"] != "" {
		t.Fatalf("past end = %v", past)
	}
}

func TestReadFileV3LongLine(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"one.json": strings.Repeat("a", 5000) + "\n"})
	got, err := call(t, v3Tools(t, root, agent.WorkspaceV3Options{})["read_file"], `{"path":"one.json","start_line":null,"end_line":null}`)
	if err != nil {
		t.Fatal(err)
	}
	content := got["content"].(string)
	if !strings.HasSuffix(content, " …[本行共 5000 字符]\n") || len(content) > 2100 {
		t.Fatalf("long line not capped: %d bytes", len(content))
	}
}

func TestReplaceLinesV3ClampsAndEchoes(t *testing.T) {
	root := writeWorkspace(t, map[string]string{"app.yaml": "name: billing\nport: 8443\nregion: eu-west\n"})
	tools := v3Tools(t, root, agent.WorkspaceV3Options{})
	got, err := call(t, tools["replace_lines"], `{"path":"app.yaml","start_line":3,"end_line":999,"content":"region: us-east"}`)
	if err != nil {
		t.Fatal(err)
	}
	if got["end_line_clamped"] != true || got["around"] != "1: name: billing\n2: port: 8443\n3: region: us-east\n" {
		t.Fatalf("got %v", got)
	}
	if _, err := call(t, tools["replace_lines"], `{"path":"app.yaml","start_line":9,"end_line":9,"content":"x"}`); err == nil || !strings.Contains(err.Error(), "start_line 最大是 4") {
		t.Fatalf("start past end: %v", err)
	}
}

func TestWriteGuards(t *testing.T) {
	root := writeWorkspace(t, map[string]string{})
	tools := v3Tools(t, root, agent.WorkspaceV3Options{})
	if _, err := call(t, tools["write_file"], `{"path":"a.txt","content":"1: a\n2: b\n3: c\n"}`); err == nil || !strings.Contains(err.Error(), "行号前缀") {
		t.Fatalf("numbered content accepted: %v", err)
	}
	if _, err := call(t, tools["write_file"], `{"path":"a.yaml","content":"1: a\n"}`); err != nil {
		t.Fatalf("single YAML-like line rejected: %v", err)
	}
	if _, err := call(t, tools["write_file"], `{"path":"b.yaml","content":"1: a\n5: b\n"}`); err != nil {
		t.Fatalf("non-consecutive numbers rejected: %v", err)
	}
	if _, err := call(t, tools["append_file"], `{"path":".web/x.md","content":"hi"}`); err == nil || !strings.Contains(err.Error(), "只读") {
		t.Fatalf(".web write accepted: %v", err)
	}
}

func TestListAndSearchHideWebArchive(t *testing.T) {
	root := writeWorkspace(t, map[string]string{
		"notes.txt":             "alpha\nbeta\n",
		".web/1-example.com.md": "alpha from the web\n",
	})
	tools := v3Tools(t, root, agent.WorkspaceV3Options{})
	listing, err := call(t, tools["list_files"], `{"path":null,"max_depth":null,"max_results":null}`)
	if err != nil {
		t.Fatal(err)
	}
	entries := listing["entries"].([]any)
	if len(entries) != 1 || entries[0].(map[string]any)["lines"].(float64) != 2 {
		t.Fatalf("listing = %v", entries)
	}
	found, err := call(t, tools["search_text"], `{"query":"alpha","path":null,"case_sensitive":null,"max_results":null}`)
	if err != nil {
		t.Fatal(err)
	}
	if n := len(found["matches"].([]any)); n != 1 {
		t.Fatalf("workspace-wide search saw the archive: %v", found)
	}
	inArchive, err := call(t, tools["search_text"], `{"query":"alpha","path":".web","case_sensitive":null,"max_results":null}`)
	if err != nil {
		t.Fatal(err)
	}
	if n := len(inArchive["matches"].([]any)); n != 1 {
		t.Fatalf("archive search = %v", inArchive)
	}
}

func TestScratchWithoutWorkspace(t *testing.T) {
	scratch := t.TempDir()
	if err := os.MkdirAll(filepath.Join(scratch, ".web"), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(scratch, ".web", "1-example.com.md"), []byte("# Title\nbody\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools := v3Tools(t, "", agent.WorkspaceV3Options{ScratchDir: scratch})
	got, err := call(t, tools["read_file"], `{"path":".web/1-example.com.md","start_line":null,"end_line":null}`)
	if err != nil {
		t.Fatal(err)
	}
	if got["content"] != "1: # Title\n2: body\n" || got["path"] != ".web/1-example.com.md" {
		t.Fatalf("scratch read = %v", got)
	}
	if _, err := call(t, tools["read_file"], `{"path":"a.txt","start_line":null,"end_line":null}`); err == nil || !strings.Contains(err.Error(), "没有打开工作区") {
		t.Fatalf("workspace path without workspace: %v", err)
	}
}

// TestWorkV2FileToolsGolden pins work-v2 tool output on a fixed workspace
// (work-v3-tools.md §4.1). Regenerate only from a commit where work-v2 is known
// good: go test ./internal/agent/tools -run TestWorkV2FileToolsGolden -update
func TestWorkV2FileToolsGolden(t *testing.T) {
	root := writeWorkspace(t, map[string]string{
		"small.txt":    "one\ntwo\nthree\n",
		"big.log":      numberedFile(3000, 40),
		"dir/notes.md": "alpha\nbeta alpha\n",
		".web/page.md": "alpha in a dot dir\n",
	})
	workspace, err := agent.WorkspaceTools(root)
	if err != nil {
		t.Fatal(err)
	}
	edits, err := FileEditTools(root, FileEditLines)
	if err != nil {
		t.Fatal(err)
	}
	byName := map[string]agent.Tool{}
	for _, tool := range append(workspace, edits...) {
		byName[tool.Spec().Name] = tool
	}
	calls := [][2]string{
		{"list_files", `{"path":null,"max_depth":null,"max_results":null}`},
		{"search_text", `{"query":"alpha","path":null,"case_sensitive":null,"max_results":null}`},
		{"read_file", `{"path":"big.log"}`},
		{"read_lines", `{"path":"big.log","start_line":2900,"end_line":null}`},
		{"read_lines", `{"path":"small.txt","start_line":null,"end_line":null}`},
		{"replace_lines", `{"path":"small.txt","start_line":2,"end_line":9,"content":"TWO"}`},
		{"replace_lines", `{"path":"small.txt","start_line":2,"end_line":2,"content":"TWO"}`},
		{"write_file", `{"path":"w.txt","content":"1: a\n2: b\n"}`},
	}
	var out strings.Builder
	for _, c := range calls {
		value, err := byName[c[0]].Execute(context.Background(), json.RawMessage(c[1]))
		data, _ := json.Marshal(value)
		if len(data) > 400 {
			data = append(data[:400], []byte(fmt.Sprintf("…(%d bytes)", len(data)))...)
		}
		fmt.Fprintf(&out, "%s %s\n-> %s err=%v\n", c[0], c[1], data, err)
	}
	golden := filepath.Join("testdata", "work_v2_file_tools.golden")
	if *updateGolden {
		if err := os.WriteFile(golden, []byte(out.String()), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	want, err := os.ReadFile(golden)
	if err != nil {
		t.Fatal(err)
	}
	if out.String() != string(want) {
		t.Fatalf("work-v2 file tool output drifted:\n%s\nwant:\n%s", out.String(), want)
	}
}
