package exam

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

func ptr[T any](v T) *T { return &v }

func TestDeriveRules(t *testing.T) {
	cases := []struct {
		name  string
		c     eval.Case
		suite string
		task  string
		diffs []string
		form  string
		lang  string
	}{
		{
			name: "notool is answer-direct",
			c: eval.Case{Tags: map[string]any{"scenario": "notool"},
				Turns: []eval.Turn{{Prompt: "What is 2+2?", Expect: eval.Expectation{Tools: []string{}}}}},
			task: TaskAnswerDirect, diffs: []string{}, form: FormNoCall, lang: "en",
		},
		{
			name: "weather probe is external",
			c: eval.Case{Tags: map[string]any{"scenario": "weatherprobe"},
				Turns: []eval.Turn{{Prompt: "北京今天最高气温多少度？", Expect: eval.Expectation{
					ExpectedNumber: ptr(28.0), Tolerance: ptr(0.0), ExpectedNumberInText: true}}}},
			suite: "weatherprobe", task: TaskExternal, diffs: []string{}, form: FormNumber, lang: "zh",
		},
		{
			name: "file-state case is write",
			c: eval.Case{Tags: map[string]any{"scenario": "config", "task_type": "read_effective"},
				Turns: []eval.Turn{{Prompt: "Set the port.", Expect: eval.Expectation{}}}},
			task: TaskWrite, diffs: []string{}, form: FormFile, lang: "en",
		},
		{
			name: "tabular aggregate with traps is compute",
			c: eval.Case{Tags: map[string]any{"scenario": "tabular", "task_type": "aggregate",
				"axes": []any{"CHN"}, "traps": []any{"TR-DECOY", "TR-TRUNC"}},
				Turns: []eval.Turn{
					{Prompt: "Sum it.", Expect: eval.Expectation{OutputContains: []string{"42"}}},
					{Prompt: "And now?", Expect: eval.Expectation{OutputContains: []string{"43"}}},
				}},
			task: TaskCompute, diffs: []string{DiffMultiSource, DiffLongInput, DiffFollowUp, DiffDecoy},
			form: FormContains, lang: "en",
		},
		{
			name: "override tags win",
			c: eval.Case{Tags: map[string]any{"scenario": "docs", "exam_task": TaskFindRead,
				"exam_difficulties": []any{"recovery", "check"}},
				Turns: []eval.Turn{{Prompt: "x", Expect: eval.Expectation{MustStateUnverified: []string{"a"}}}}},
			task: TaskFindRead, diffs: []string{DiffCheck, DiffRecovery}, form: FormAbstain, lang: "en",
		},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			if got := Task(c.c, c.suite); got != c.task {
				t.Errorf("Task = %q, want %q", got, c.task)
			}
			if got := Difficulties(c.c); !reflect.DeepEqual(got, c.diffs) {
				t.Errorf("Difficulties = %v, want %v", got, c.diffs)
			}
			if got := AnswerForm(c.c); got != c.form {
				t.Errorf("AnswerForm = %q, want %q", got, c.form)
			}
			if got := Language(c.c); got != c.lang {
				t.Errorf("Language = %q, want %q", got, c.lang)
			}
		})
	}
}

func TestReadIDList(t *testing.T) {
	path := filepath.Join(t.TempDir(), "ids.txt")
	if err := os.WriteFile(path, []byte("# header\n\na-1  # first reason\nb-2\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	ids, reasons, err := readIDList(path)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(ids, []string{"a-1", "b-2"}) || reasons["a-1"] != "first reason" || reasons["b-2"] != "" {
		t.Errorf("got %v %v", ids, reasons)
	}
	if err := os.WriteFile(path, []byte("a\na\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, _, err := readIDList(path); err == nil {
		t.Error("duplicate id accepted")
	}
	if ids, _, err := readIDList(filepath.Join(t.TempDir(), "missing.txt")); err != nil || len(ids) != 0 {
		t.Errorf("missing file: %v %v", ids, err)
	}
}

func TestExamHashTracksOrderAndContent(t *testing.T) {
	a := []eval.ExamCase{{ID: "x", SHA256: "1"}, {ID: "y", SHA256: "2"}}
	b := []eval.ExamCase{{ID: "y", SHA256: "2"}, {ID: "x", SHA256: "1"}}
	c := []eval.ExamCase{{ID: "x", SHA256: "1"}, {ID: "y", SHA256: "3"}}
	if eval.ExamHash(a) == eval.ExamHash(b) || eval.ExamHash(a) == eval.ExamHash(c) {
		t.Error("exam hash ignores order or content")
	}
	if eval.ExamHash(a) != eval.ExamHash(append([]eval.ExamCase(nil), a...)) {
		t.Error("exam hash is not deterministic")
	}
}

// TestRepositoryExamIsCurrent is the CI guard: the committed manifests and
// SUITES.md must match a fresh build, and the exam must lint clean.
func TestRepositoryExamIsCurrent(t *testing.T) {
	paths := DefaultPaths()
	if _, err := os.Stat(filepath.Join(paths.ExamDir, "full.json")); err != nil {
		t.Skip("no bench/exam in this checkout")
	}
	exam, err := Assemble(paths)
	if err != nil {
		t.Fatal(err)
	}
	if violations := exam.Lint(paths); len(violations) > 0 {
		t.Errorf("exam lint: %d violation(s), first: %s", len(violations), violations[0])
	}
}
