package main

import (
	"encoding/json"
	"math/rand"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/inference"
)

// repoRoot walks up from this package to the module root so the test can read
// the exported schemas regardless of where go test runs it.
func repoRoot(t *testing.T) string {
	t.Helper()
	dir, err := filepath.Abs(".")
	if err != nil {
		t.Fatal(err)
	}
	for range 6 {
		if _, err := os.Stat(filepath.Join(dir, "go.mod")); err == nil {
			return dir
		}
		dir = filepath.Dir(dir)
	}
	t.Fatal("go.mod not found above test directory")
	return ""
}

// productSpecs builds ToolSpecs straight from the product tool constructors,
// the way the runner does, so the test compares against what the model actually
// sees rather than against another test's idea of it.
func productSpecs(t *testing.T, names ...string) []agent.ToolSpec {
	t.Helper()
	root := t.TempDir()
	var all []agent.Tool
	fileEdit, err := tools.FileEditTools(root, tools.FileEditLines)
	if err != nil {
		t.Fatal(err)
	}
	all = append(all, fileEdit...)
	local, err := tools.LocalTools(tools.Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	all = append(all, local...)
	all = append(all, tools.WebTools(tools.WebOptions{})...)
	all = append(all, tools.DelegationTools(tools.DelegationOptions{})...)

	byName := map[string]agent.ToolSpec{}
	for _, tool := range all {
		spec := tool.Spec()
		byName[spec.Name] = spec
	}
	specs := make([]agent.ToolSpec, 0, len(names))
	for _, name := range names {
		spec, ok := byName[name]
		if !ok {
			t.Fatalf("product registry has no tool %q", name)
		}
		specs = append(specs, spec)
	}
	return specs
}

// TestPromptParityWithProductRegistry is the check that matters: the bytes this
// renderer emits must equal the bytes the product builds from its own tool
// registry. They are different call sites of the same protocol, so any
// divergence means a trained state would not match inference.
//
// The failure mode being guarded is silent. scarletwolf measured a state
// trained on one prompt shape scoring 39 where it scored 61 on its own, and
// abstention collapsing to 0/17 once the think block moved. Nothing errors; the
// state simply stops working.
func TestPromptParityWithProductRegistry(t *testing.T) {
	root := repoRoot(t)
	schemas, err := loadSchemas(filepath.Join(root, "datasets/state-tuning/tool_schemas.json"))
	if err != nil {
		t.Fatal(err)
	}

	entry := semanticCase{
		ID:      "parity-0001",
		Subtype: "positive",
		Lang:    "zh",
		Tools:   []string{"read_lines", "web_search", "datetime"},
		User:    "读一下 config.yaml 的前 40 行",
		Action:  "call",
	}
	entry.Call = &struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}{
		Name:      "read_lines",
		Arguments: json.RawMessage(`{"path":"config.yaml","start_line":1,"end_line":40}`),
	}

	record, err := renderCase(entry, schemas, inference.ThinkingFast, rand.New(rand.NewSource(1)))
	if err != nil {
		t.Fatal(err)
	}

	// Rebuild the same prompt through the product registry, in the order our
	// shuffle produced.
	want, err := (agent.RWKVChatRenderer{ThinkingMode: inference.ThinkingFast}).Render(
		[]agent.Message{
			{Role: agent.RoleSystem, Content: (agent.G1IProtocol{}).Instructions(
				productSpecs(t, record.ToolOrder...), inference.ThinkingFast)},
			{Role: agent.RoleUser, Content: entry.User},
		})
	if err != nil {
		t.Fatal(err)
	}

	if record.Prompt != want {
		reportFirstDifference(t, record.Prompt, want)
	}
}

func reportFirstDifference(t *testing.T, got, want string) {
	t.Helper()
	limit := min(len(got), len(want))
	for i := range limit {
		if got[i] != want[i] {
			from := max(0, i-70)
			t.Fatalf("prompt bytes differ from the product registry at byte %d:\n  ours:    %q\n  product: %q",
				i, got[from:min(len(got), i+70)], want[from:min(len(want), i+70)])
		}
	}
	if len(got) != len(want) {
		t.Fatalf("one prompt is a prefix of the other: ours %d bytes, product %d bytes\n  ours tail:    %q\n  product tail: %q",
			len(got), len(want),
			got[max(0, len(got)-80):], want[max(0, len(want)-80):])
	}
}

// TestCompletionStartsAtWithheldBracket pins the byte boundary. Render stops
// mid-tag at "<think></think" because RWKV tokenises ">" together with the text
// after it, so supplying the bracket would start generation from a boundary the
// model never saw in training. The model's own first byte is that ">", and a
// completion that omits it trains a boundary inference never produces.
func TestCompletionStartsAtWithheldBracket(t *testing.T) {
	root := repoRoot(t)
	schemas, err := loadSchemas(filepath.Join(root, "datasets/state-tuning/tool_schemas.json"))
	if err != nil {
		t.Fatal(err)
	}

	abstain := semanticCase{
		ID: "b-1", Subtype: "chitchat", Lang: "zh", Action: "abstain",
		Tools: []string{"read_lines", "web_search", "datetime"},
		User:  "你好", Answer: "你好！有什么我可以帮你的吗？",
	}
	call := semanticCase{
		ID: "b-2", Subtype: "positive", Lang: "zh", Action: "call",
		Tools: []string{"read_lines", "web_search", "datetime"},
		User:  "看看 config.yaml", Answer: "配置里定义了三个服务端口。",
	}
	call.Call = &struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	}{
		Name:      "read_lines",
		Arguments: json.RawMessage(`{"path":"config.yaml","start_line":1,"end_line":200}`),
	}

	for _, testCase := range []struct {
		name   string
		entry  semanticCase
		prefix string
	}{
		{"abstain", abstain, ">你好！"},
		// Key order is the product's, not Go's map order. Asserting
		// {"arguments": here is what let the reversed order ship.
		{"call", call, `><tool_call>{"name":`},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			record, err := renderCase(testCase.entry, schemas,
				inference.ThinkingFast, rand.New(rand.NewSource(1)))
			if err != nil {
				t.Fatal(err)
			}
			if !strings.HasSuffix(record.Prompt, inference.ThinkBlockFast) {
				t.Errorf("prompt must end at %q, got tail %q", inference.ThinkBlockFast,
					record.Prompt[max(0, len(record.Prompt)-40):])
			}
			if !strings.HasPrefix(record.Completion, testCase.prefix) {
				t.Errorf("completion = %q, want prefix %q",
					record.Completion[:min(40, len(record.Completion))], testCase.prefix)
			}
			// Concatenating prompt and completion must reconstruct a closed tag,
			// which is what reconstructOutput hands the parser at inference.
			if !strings.Contains(record.Text, inference.ThinkBlockClosed) {
				t.Error("prompt+completion does not contain a closed think block")
			}
		})
	}
}

// TestToolOrderShuffles guards the position-bias fix. The semantic layer tends
// to list the tool a positive case calls first; a state trained on that learns
// position instead of the tool.
func TestToolOrderShuffles(t *testing.T) {
	root := repoRoot(t)
	schemas, err := loadSchemas(filepath.Join(root, "datasets/state-tuning/tool_schemas.json"))
	if err != nil {
		t.Fatal(err)
	}
	entry := semanticCase{
		ID: "s-1", Subtype: "chitchat", Lang: "zh", Action: "abstain",
		Tools: []string{"read_lines", "write_file", "web_search", "datetime", "append_file"},
		User:  "谢谢", Answer: "不客气。",
	}
	shuffler := rand.New(rand.NewSource(7))
	firstPositions := map[string]int{}
	for range 40 {
		record, err := renderCase(entry, schemas, inference.ThinkingFast, shuffler)
		if err != nil {
			t.Fatal(err)
		}
		firstPositions[record.ToolOrder[0]]++
	}
	if len(firstPositions) < 3 {
		t.Errorf("tool order barely varies across renders: %v", firstPositions)
	}
}

// TestShippedCorpusIsFastThink guards the artifact on disk rather than the
// renderer. train/ is derived and gitignored, so nothing else notices if it is
// re-rendered with --thinking off: every prompt would then end at a bare
// "Assistant:" and every completion would start with a space. A state tuned on
// those bytes and served under thinking=fast (or the reverse) loses the
// abstention behaviour this corpus exists to teach, which is the one failure
// mode that looks like a bad model rather than a bad build.
func TestShippedCorpusIsFastThink(t *testing.T) {
	path := filepath.Join(repoRoot(t), "datasets/state-tuning/train/train.jsonl")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Skipf("no rendered corpus at %s: %v", path, err)
	}
	lines := strings.Split(strings.TrimSpace(string(data)), "\n")
	calls := 0
	for index, line := range lines {
		var record trainingRecord
		if err := json.Unmarshal([]byte(line), &record); err != nil {
			t.Fatalf("line %d: %v", index+1, err)
		}
		if !strings.HasSuffix(record.Prompt, inference.ThinkBlockFast) {
			t.Fatalf("line %d (%s): prompt does not end at the half-open think tag; re-render with --thinking fast",
				index+1, record.ID)
		}
		if !strings.HasPrefix(record.Completion, ">") {
			t.Fatalf("line %d (%s): completion must open with the withheld bracket, got %q",
				index+1, record.ID, record.Completion[:min(12, len(record.Completion))])
		}
		if record.Text != record.Prompt+record.Completion {
			t.Fatalf("line %d (%s): text is not prompt+completion", index+1, record.ID)
		}
		if !strings.Contains(record.Completion, "<tool_call>") {
			continue
		}
		calls++
		// The envelope must carry the product's key order. Go's map marshalling
		// sorts keys and would train {"arguments":…,"name":…}, the reverse of
		// both RecordAction and the instructions' own example.
		if !strings.Contains(record.Completion, `<tool_call>{"name":`) {
			t.Fatalf("line %d (%s): tool_call key order is not the product's: %q",
				index+1, record.ID, record.Completion[:min(60, len(record.Completion))])
		}
	}
	if calls == 0 {
		t.Fatal("corpus contains no tool_call samples; the renderer or the semantic layer is wrong")
	}
	t.Logf("checked %d samples, %d with tool calls", len(lines), calls)
}
