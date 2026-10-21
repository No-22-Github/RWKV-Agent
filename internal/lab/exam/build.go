package exam

import (
	"bufio"
	"bytes"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// Source is one authored case collection the exam draws from. The case files
// stay in their source directory; the exam only lists them.
type Source struct {
	Name        string
	Dir         string // repository-relative
	Label       string
	Purpose     string
	ToolCatalog string // catalog the collection was authored and historically run under
	// Optional sources may be absent (the gap-filling batches land later).
	Optional bool
}

// Sources is the exam's draw order. The probe reserves are deliberately
// absent: they are the pool new cases are promoted from, not exam members.
var Sources = []Source{
	{"workbank", "bench/workbank/cases", "workbank",
		"原主考卷：模拟工作区里的日常任务（查表、看日志、改配置、写脚本、上网查）", eval.AgentToolV1, false},
	{"p13", "bench/holdout/p13", "p13 留存题",
		"从未进过训练的留存题，中文为主", eval.AgentToolV1, false},
	{"bfcl-product", "bench/exam/imported/bfcl-product", "bfcl-product",
		"工具时机：该不该调工具、缺信息先反问、两轮对话（改写自 BFCL v4）", "", false},
	{"boundary", "bench/exam/imported/boundary", "boundary",
		"早期边界题：多步工具、金融算术、注入（改写自 primitive-bench）", "", false},
	{"bashprobe", "bench/bashprobe/cases", "bash 探针·老题",
		"会不会用 bash 做聚合、批量编辑、出错恢复", eval.AgentToolV2, false},
	{"bashprobe-b14", "bench/bashprobe/cases-b14", "bash 探针·第二部分",
		"第 14 批题转来的 bash 场景题，中英各半", eval.AgentToolV2, false},
	{"weatherprobe", "bench/weatherprobe/cases", "天气探针·老题",
		"会不会用 get_weather、查完写产物", eval.AgentToolV2, false},
	{"weatherprobe-b14", "bench/weatherprobe/cases-b14", "天气探针·第二部分",
		"第 14 批题转来的天气场景题", eval.AgentToolV2, false},
	{"exam-new", "bench/exam/cases", "考卷补题",
		"按覆盖缺口新出的题（docs/evaluations/bench-composition-20261015/gap-fill-spec.md）", eval.AgentToolV2, true},
}

const (
	examToolCatalog = eval.AgentToolV2
	examHarness     = "app"
)

// Paths groups the exam's inputs and outputs, all under bench/exam.
type Paths struct {
	Root     string // repository root
	ExamDir  string
	Leaked   string
	Exclude  string
	QuickIDs string
}

// DefaultPaths resolves the standard locations from the repository root.
func DefaultPaths() Paths {
	root := lab.RepoRoot()
	examDir := filepath.Join(root, "bench", "exam")
	return Paths{
		Root:     root,
		ExamDir:  examDir,
		Leaked:   filepath.Join(root, "bench", "workbank", "seeded-base700.txt"),
		Exclude:  filepath.Join(examDir, "exclude.txt"),
		QuickIDs: filepath.Join(examDir, "quick-ids.txt"),
	}
}

// loaded is one scanned case with its manifest row.
type loaded struct {
	Case eval.Case
	Row  eval.ExamCase
}

// readIDList reads "id  # comment" lines; a missing file is an empty list.
// The comment of each id is returned as its reason.
func readIDList(path string) ([]string, map[string]string, error) {
	data, err := os.ReadFile(path)
	if errors.Is(err, fs.ErrNotExist) {
		return nil, map[string]string{}, nil
	}
	if err != nil {
		return nil, nil, err
	}
	var ids []string
	reasons := map[string]string{}
	scanner := bufio.NewScanner(bytes.NewReader(data))
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		id, reason, _ := strings.Cut(line, "#")
		id = strings.TrimSpace(id)
		if _, dup := reasons[id]; dup {
			return nil, nil, fmt.Errorf("%s: duplicate id %q", path, id)
		}
		ids = append(ids, id)
		reasons[id] = strings.TrimSpace(reason)
	}
	return ids, reasons, scanner.Err()
}

// scanSource loads every case.json below a source directory in path order.
func scanSource(paths Paths, source Source, leaked map[string]string) ([]loaded, error) {
	dir := filepath.Join(paths.Root, filepath.FromSlash(source.Dir))
	if _, err := os.Stat(dir); err != nil {
		if source.Optional && errors.Is(err, fs.ErrNotExist) {
			return nil, nil
		}
		return nil, fmt.Errorf("source %s: %w", source.Name, err)
	}
	var out []loaded
	err := filepath.WalkDir(dir, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() && entry.Name() == "cases-shelved" {
			return filepath.SkipDir
		}
		if entry.IsDir() || entry.Name() != "case.json" {
			return nil
		}
		testCase, err := eval.LoadCaseFile(path)
		if err != nil {
			return err
		}
		sum, err := eval.FileSHA256(path)
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(paths.Root, filepath.Dir(path))
		if err != nil {
			return err
		}
		row := Row(testCase, source.Name, filepath.ToSlash(rel), sum)
		_, row.Leaked = leaked[testCase.ID]
		out = append(out, loaded{Case: testCase, Row: row})
		return nil
	})
	if err != nil {
		return nil, err
	}
	sort.Slice(out, func(i, j int) bool { return out[i].Row.ID < out[j].Row.ID })
	return out, nil
}

// Exam is everything one build produces, kept in memory so build and lint
// share it.
type Exam struct {
	Suites  map[string][]loaded
	Full    eval.ExamManifest
	Quick   *eval.ExamManifest
	Exclude map[string]string
	Missing []string // quick ids not present in the full exam
}

// Assemble scans the sources and derives every manifest.
func Assemble(paths Paths) (*Exam, error) {
	_, leaked, err := readIDList(paths.Leaked)
	if err != nil {
		return nil, err
	}
	_, exclude, err := readIDList(paths.Exclude)
	if err != nil {
		return nil, err
	}
	exam := &Exam{Suites: map[string][]loaded{}, Exclude: exclude}
	seen := map[string]string{}
	var fullRows []eval.ExamCase
	for _, source := range Sources {
		items, err := scanSource(paths, source, leaked)
		if err != nil {
			return nil, err
		}
		exam.Suites[source.Name] = items
		for _, item := range items {
			if previous, dup := seen[item.Row.ID]; dup {
				return nil, fmt.Errorf("case id %q appears in %s and %s", item.Row.ID, previous, source.Name)
			}
			seen[item.Row.ID] = source.Name
			if item.Row.Leaked {
				continue
			}
			if _, skip := exclude[item.Row.ID]; skip {
				continue
			}
			fullRows = append(fullRows, item.Row)
		}
	}
	for id := range exclude {
		if _, ok := seen[id]; !ok {
			return nil, fmt.Errorf("%s lists unknown case id %q", paths.Exclude, id)
		}
	}
	exam.Full = newManifest("exam-full",
		"完整考卷：按 App 默认配置（g1k、工具全开、暂存文件、复读兜底）考用户在 App 里会做的事",
		examToolCatalog, examHarness, fullRows)

	quickIDs, _, err := readIDList(paths.QuickIDs)
	if err != nil {
		return nil, err
	}
	if len(quickIDs) > 0 {
		byID := map[string]eval.ExamCase{}
		for _, row := range fullRows {
			byID[row.ID] = row
		}
		var quickRows []eval.ExamCase
		for _, id := range quickIDs {
			row, ok := byID[id]
			if !ok {
				exam.Missing = append(exam.Missing, id)
				continue
			}
			quickRows = append(quickRows, row)
		}
		sortRows(quickRows)
		quick := newManifest("exam-quick",
			"快测版：从完整考卷分层抽出，几分钟跑完，用于快速比较",
			examToolCatalog, examHarness, quickRows)
		exam.Quick = &quick
	}
	return exam, nil
}

func suiteIndex(name string) int {
	for i, source := range Sources {
		if source.Name == name {
			return i
		}
	}
	return len(Sources)
}

func sortRows(rows []eval.ExamCase) {
	sort.SliceStable(rows, func(i, j int) bool {
		a, b := suiteIndex(rows[i].Suite), suiteIndex(rows[j].Suite)
		if a != b {
			return a < b
		}
		return rows[i].ID < rows[j].ID
	})
}

func newManifest(name, description, catalog, harness string, rows []eval.ExamCase) eval.ExamManifest {
	if rows == nil {
		rows = []eval.ExamCase{}
	}
	summary, _ := json.Marshal(Summarize(rows))
	return eval.ExamManifest{
		Schema:      eval.ExamSchema,
		Name:        name,
		Description: description,
		ToolCatalog: catalog,
		Harness:     harness,
		Hash:        eval.ExamHash(rows),
		Summary:     summary,
		Cases:       rows,
	}
}

// Summary is the aggregate block written into every manifest.
type Summary struct {
	Total          int                       `json:"total"`
	BySuite        map[string]int            `json:"by_suite"`
	ByTask         map[string]int            `json:"by_task"`
	ByDifficulty   map[string]int            `json:"by_difficulty"`
	ByLanguage     map[string]int            `json:"by_language"`
	ByAnswerForm   map[string]int            `json:"by_answer_form"`
	ByLevel        map[string]int            `json:"by_level"`
	TaskByLanguage map[string]map[string]int `json:"task_by_language"`
	Leaked         int                       `json:"leaked,omitempty"`
}

// Summarize counts rows along every reporting axis.
func Summarize(rows []eval.ExamCase) Summary {
	s := Summary{
		BySuite: map[string]int{}, ByTask: map[string]int{}, ByDifficulty: map[string]int{},
		ByLanguage: map[string]int{}, ByAnswerForm: map[string]int{}, ByLevel: map[string]int{},
		TaskByLanguage: map[string]map[string]int{},
	}
	for _, row := range rows {
		s.Total++
		s.BySuite[row.Suite]++
		s.ByTask[row.Task]++
		for _, item := range row.Difficulties {
			s.ByDifficulty[item]++
		}
		if len(row.Difficulties) == 0 {
			s.ByDifficulty["none"]++
		}
		s.ByLanguage[row.Language]++
		s.ByAnswerForm[row.AnswerForm]++
		level := row.Level
		if level == "" {
			level = "unset"
		}
		s.ByLevel[level]++
		if s.TaskByLanguage[row.Task] == nil {
			s.TaskByLanguage[row.Task] = map[string]int{}
		}
		s.TaskByLanguage[row.Task][row.Language]++
		if row.Leaked {
			s.Leaked++
		}
	}
	return s
}

// Outputs renders every generated file, keyed by repository-relative path.
func (exam *Exam) Outputs() (map[string][]byte, error) {
	out := map[string][]byte{}
	put := func(rel string, manifest eval.ExamManifest) error {
		data, err := json.MarshalIndent(manifest, "", "  ")
		if err != nil {
			return err
		}
		out[rel] = append(data, '\n')
		return nil
	}
	if err := put("bench/exam/full.json", exam.Full); err != nil {
		return nil, err
	}
	if exam.Quick != nil {
		if err := put("bench/exam/quick.json", *exam.Quick); err != nil {
			return nil, err
		}
	}
	for _, source := range Sources {
		rows := make([]eval.ExamCase, 0, len(exam.Suites[source.Name]))
		for _, item := range exam.Suites[source.Name] {
			rows = append(rows, item.Row)
		}
		manifest := newManifest(source.Name, source.Purpose, source.ToolCatalog, "legacy", rows)
		if err := put("bench/exam/suites/"+source.Name+".json", manifest); err != nil {
			return nil, err
		}
	}
	out["bench/exam/SUITES.md"] = []byte(exam.RenderSuites())
	return out, nil
}

func runBuild(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam build", flag.ContinueOnError)
	check := flags.Bool("check", false, "do not write; exit 1 when a generated file is stale")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	paths := DefaultPaths()
	exam, err := Assemble(paths)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam build:", err)
		return 1
	}
	if len(exam.Missing) > 0 {
		fmt.Fprintf(os.Stderr, "rwkv-lab exam build: quick-ids.txt lists ids outside the full exam: %v\n", exam.Missing)
		return 1
	}
	outputs, err := exam.Outputs()
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam build:", err)
		return 1
	}
	names := make([]string, 0, len(outputs))
	for name := range outputs {
		names = append(names, name)
	}
	sort.Strings(names)
	stale := 0
	for _, name := range names {
		target := filepath.Join(paths.Root, filepath.FromSlash(name))
		current, _ := os.ReadFile(target)
		if bytes.Equal(current, outputs[name]) {
			continue
		}
		stale++
		if *check {
			fmt.Printf("stale: %s\n", name)
			continue
		}
		if err := os.MkdirAll(filepath.Dir(target), 0o755); err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam build:", err)
			return 1
		}
		if err := os.WriteFile(target, outputs[name], 0o644); err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam build:", err)
			return 1
		}
		fmt.Printf("wrote %s\n", name)
	}
	quick := 0
	if exam.Quick != nil {
		quick = len(exam.Quick.Cases)
	}
	fmt.Printf("exam-full %d cases (hash %s), exam-quick %d cases; %d file(s) %s\n",
		len(exam.Full.Cases), exam.Full.Hash[:12], quick, stale, map[bool]string{true: "stale", false: "updated"}[*check])
	if *check && stale > 0 {
		return 1
	}
	return 0
}
