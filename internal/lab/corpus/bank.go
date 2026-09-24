package corpus

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// RepoRoot is the repository the tools resolve their defaults against.
func RepoRoot() string { return lab.RepoRoot() }

// TestBank is the measured bank. Distilling from it would train on the
// benchmark, so render refuses to read it without --allow-test-bank.
func TestBank() string {
	return filepath.Join(RepoRoot(), "bench", "workbank")
}

// Load reads every case.json under root, in path order.
func Load(root string) ([]*lab.OrderedMap, error) {
	var paths []string
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if !d.IsDir() && d.Name() == "case.json" {
			paths = append(paths, path)
		}
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Strings(paths)
	cases := make([]*lab.OrderedMap, 0, len(paths))
	for _, path := range paths {
		obj, err := lab.DecodeOrderedJSONFile(path)
		if err != nil {
			return nil, fmt.Errorf("parse %s: %w", path, err)
		}
		om, ok := obj.(*lab.OrderedMap)
		if !ok {
			return nil, fmt.Errorf("%s is not a JSON object", path)
		}
		cases = append(cases, om)
	}
	return cases, nil
}

// ByID indexes cases by their id, refusing duplicates.
func ByID(cases []*lab.OrderedMap) (map[string]*lab.OrderedMap, error) {
	index := make(map[string]*lab.OrderedMap, len(cases))
	for _, c := range cases {
		id := mapString(c, "id")
		if _, dup := index[id]; dup {
			return nil, fmt.Errorf("duplicate case id %s", id)
		}
		index[id] = c
	}
	return index, nil
}

// Write materialises cases as a bank directory of <id>/case.json files.
//
// Writing a bank rather than a single cases.json is deliberate: agent-eval
// then takes the workbank suite path and its defaults (rescue off,
// firstcall=auto), the same as a benchmark.
func Write(root string, cases []*lab.OrderedMap) error {
	for _, c := range cases {
		caseDir := filepath.Join(root, mapString(c, "id"))
		if err := os.MkdirAll(caseDir, 0o755); err != nil {
			return err
		}
		// Python writes json.dumps(case, ensure_ascii=False, indent=1) with no
		// trailing newline, keys in the order the case was built.
		data, err := lab.EncodeOrderedJSON(c, lab.EncodeOptions{Indent: 1})
		if err != nil {
			return err
		}
		if err := os.WriteFile(filepath.Join(caseDir, "case.json"), data, 0o644); err != nil {
			return err
		}
	}
	return nil
}

// IsTestBank reports whether path sits inside bench/workbank.
func IsTestBank(path string) bool {
	abs, err := filepath.Abs(path)
	if err != nil {
		return false
	}
	bank := TestBank()
	rel, err := filepath.Rel(bank, abs)
	if err != nil {
		return false
	}
	return rel == "." || (!strings.HasPrefix(rel, ".."+string(filepath.Separator)) && rel != "..")
}

// Normalized records (datasets/workspace-agent-700-*/generated/normalized)
// hold one user turn and assistant messages of kind tool_call / no_tool /
// final. These two converters turn one record into a case and a script entry.

// RecordToCase builds the bank case a corpus record describes.
func RecordToCase(record *lab.OrderedMap) (*lab.OrderedMap, error) {
	id := mapString(record, "id")
	messages := mapSlice(record, "messages")
	var users []*lab.OrderedMap
	for _, message := range messages {
		if mapString(message, "role") == "user" {
			users = append(users, message)
		}
	}
	if len(users) != 1 {
		return nil, fmt.Errorf("%s: expected one user turn, got %d", id, len(users))
	}
	expected, _ := mapValue(record, "expected").(*lab.OrderedMap)

	turn := lab.NewOrderedMap()
	turn.Set("prompt", mapString(users[0], "text"))
	if exp := mapValue(expected, "turn_expectation"); exp != nil {
		turn.Set("expect", exp)
	} else {
		turn.Set("expect", lab.NewOrderedMap())
	}

	scenario := mapString(record, "scenario")
	caseObj := lab.NewOrderedMap()
	caseObj.Set("id", id)
	caseObj.Set("description", fmt.Sprintf("%s corpus record %s", scenario, id))
	caseObj.Set("category", scenario)
	if files := mapValue(record, "initial_files"); files != nil {
		caseObj.Set("files", files)
	} else {
		caseObj.Set("files", lab.NewOrderedMap())
	}
	caseObj.Set("turns", []any{turn})
	if fixture := mapValue(record, "web_fixture"); truthy(fixture) {
		caseObj.Set("web_fixture", fixture)
	}
	if caseExpect := mapValue(expected, "case_expect"); truthy(caseExpect) {
		caseObj.Set("expect", caseExpect)
	}
	return caseObj, nil
}

// RecordToScript builds the replay entry a corpus record describes.
func RecordToScript(record *lab.OrderedMap) (eval.ScriptEntry, error) {
	id := mapString(record, "id")
	var texts []string
	var supervised []bool
	for _, message := range mapSlice(record, "messages") {
		if mapString(message, "role") != "assistant" {
			continue
		}
		kind := mapString(message, "kind")
		switch kind {
		case "tool_call", "no_tool":
			arguments, ok := mapValue(message, "arguments").(*lab.OrderedMap)
			if !ok {
				arguments = lab.NewOrderedMap()
			}
			text, err := ToolCall(mapString(message, "name"), arguments)
			if err != nil {
				return eval.ScriptEntry{}, err
			}
			texts = append(texts, text)
		case "final":
			texts = append(texts, mapString(message, "text"))
		default:
			return eval.ScriptEntry{}, fmt.Errorf("%s: unknown assistant kind %q", id, kind)
		}
		supervised = append(supervised, truthy(mapValue(message, "supervised")))
	}
	return Entry(id, texts, supervised), nil
}

func mapValue(m *lab.OrderedMap, key string) any {
	if m == nil {
		return nil
	}
	v, _ := m.Get(key)
	return v
}

func mapString(m *lab.OrderedMap, key string) string {
	s, _ := mapValue(m, key).(string)
	return s
}

func mapSlice(m *lab.OrderedMap, key string) []*lab.OrderedMap {
	items, _ := mapValue(m, key).([]any)
	out := make([]*lab.OrderedMap, 0, len(items))
	for _, item := range items {
		if om, ok := item.(*lab.OrderedMap); ok {
			out = append(out, om)
		}
	}
	return out
}

// truthy is Python's bool(x) for decoded JSON.
func truthy(v any) bool {
	switch t := v.(type) {
	case nil:
		return false
	case bool:
		return t
	case string:
		return t != ""
	case *lab.OrderedMap:
		return len(t.Keys) > 0
	case []any:
		return len(t) > 0
	}
	return true
}
