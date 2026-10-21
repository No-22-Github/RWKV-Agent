package exam

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"io/fs"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// The quick exam is a stratified draw from the full one. Each task kind gets a
// fixed share, split as evenly as the pool allows between Chinese and English;
// inside a cell the draw prefers cases that discriminate between RWKV
// checkpoints in the local run history (pass rate strictly between 0 and 90%),
// keeps one easy and one hard anchor per task kind so regressions and
// breakthroughs stay visible, and then tops up difficulty factors that fell
// below a floor. Ties break on a hash of the id, so the draw is reproducible
// from the same history.
var quickShare = map[string]int{
	TaskAnswerDirect: 14,
	TaskFindRead:     14,
	TaskCompute:      16,
	TaskWrite:        14,
	TaskExternal:     14,
}

const quickDifficultyFloor = 6

// teacherRunMarkers keep teacher and API-model runs out of the RWKV history.
var teacherRunMarkers = []string{"deepseek", "minimax", "dsf", "m31f", "qwen", "claude", "glm"}

type caseHistory struct {
	passed, runs int
}

func (h caseHistory) rate() float64 {
	if h.runs == 0 {
		return math.NaN()
	}
	return float64(h.passed) / float64(h.runs)
}

// loadHistory tallies per-case passes over every RWKV run summary below dir.
func loadHistory(dir string) (map[string]caseHistory, int, error) {
	history := map[string]caseHistory{}
	runs := 0
	err := filepath.WalkDir(dir, func(path string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return nil
		}
		if entry.IsDir() {
			name := strings.ToLower(entry.Name())
			if name == "aborted" || strings.Contains(name, "aborted") {
				return filepath.SkipDir
			}
			return nil
		}
		if entry.Name() != "summary.json" {
			return nil
		}
		lower := strings.ToLower(path)
		for _, marker := range teacherRunMarkers {
			if strings.Contains(lower, marker) {
				return nil
			}
		}
		// Only real RWKV generations count: teacher-script replays and API
		// models would make every case look easy.
		var manifest struct {
			Model struct {
				Completion string `json:"completion"`
			} `json:"model"`
		}
		if raw, err := os.ReadFile(filepath.Join(filepath.Dir(path), "run.json")); err != nil ||
			json.Unmarshal(raw, &manifest) != nil || !strings.HasPrefix(manifest.Model.Completion, "rwkv") {
			return nil
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		var summary struct {
			Cases []struct {
				ID      string `json:"id"`
				Passed  bool   `json:"passed"`
				Invalid bool   `json:"invalid"`
			} `json:"cases"`
		}
		if json.Unmarshal(data, &summary) != nil || len(summary.Cases) < 4 {
			return nil
		}
		runs++
		for _, c := range summary.Cases {
			if c.Invalid {
				continue
			}
			h := history[c.ID]
			h.runs++
			if c.Passed {
				h.passed++
			}
			history[c.ID] = h
		}
		return nil
	})
	return history, runs, err
}

type candidate struct {
	row  eval.ExamCase
	hist caseHistory
	key  string // id hash, the deterministic tie-break
}

func (c candidate) discriminative() bool {
	r := c.hist.rate()
	return !math.IsNaN(r) && r > 0 && r < 0.9
}

// priority orders candidates inside a cell: discriminative first (closest to
// a 50% pass rate), then cases without history, then the rest.
func (c candidate) priority() float64 {
	r := c.hist.rate()
	switch {
	case c.discriminative():
		return math.Abs(r - 0.5)
	case math.IsNaN(r):
		return 1
	default:
		return 2
	}
}

type pick struct {
	candidate
	reason string
}

func selectQuick(full []eval.ExamCase, history map[string]caseHistory) []pick {
	byTask := map[string][]candidate{}
	for _, row := range full {
		sum := sha256.Sum256([]byte(row.ID))
		byTask[row.Task] = append(byTask[row.Task], candidate{row, history[row.ID], fmt.Sprintf("%x", sum[:8])})
	}
	chosen := map[string]pick{}
	take := func(c candidate, reason string) {
		if _, ok := chosen[c.row.ID]; !ok {
			chosen[c.row.ID] = pick{c, reason}
		}
	}
	for _, task := range TaskOrder {
		pool := byTask[task]
		share := quickShare[task]
		// Anchors: the most reliably passed and a never-passed case.
		var easy, hard *candidate
		for i := range pool {
			c := &pool[i]
			r := c.hist.rate()
			if math.IsNaN(r) || c.hist.runs < 3 {
				continue
			}
			if r >= 0.9 && (easy == nil || r > easy.hist.rate() || (r == easy.hist.rate() && c.key < easy.key)) {
				easy = c
			}
			if r == 0 && (hard == nil || c.key < hard.key) {
				hard = c
			}
		}
		if easy != nil {
			take(*easy, "anchor-easy")
			share--
		}
		if hard != nil {
			take(*hard, "anchor-hard")
			share--
		}
		for _, language := range []string{"zh", "en"} {
			var cell []candidate
			for _, c := range pool {
				if c.row.Language == language {
					if _, done := chosen[c.row.ID]; !done {
						cell = append(cell, c)
					}
				}
			}
			sort.Slice(cell, func(i, j int) bool {
				if pi, pj := cell[i].priority(), cell[j].priority(); pi != pj {
					return pi < pj
				}
				return cell[i].key < cell[j].key
			})
			want := share / 2
			if language == "zh" {
				want = share - share/2
			}
			for i := 0; i < want && i < len(cell); i++ {
				reason := "no-history"
				if cell[i].discriminative() {
					reason = "discriminative"
				} else if !math.IsNaN(cell[i].hist.rate()) {
					reason = "fill"
				}
				take(cell[i], reason)
			}
		}
	}
	// Source floor: a source with little run history (the holdout, the b14
	// probe halves) would otherwise lose every cell to history-rich workbank
	// cases; each keeps at least 12% of its cases (at least 3).
	for _, source := range Sources {
		var pool []candidate
		count := 0
		for _, task := range TaskOrder {
			for _, c := range byTask[task] {
				if c.row.Suite != source.Name {
					continue
				}
				if _, done := chosen[c.row.ID]; done {
					count++
				} else {
					pool = append(pool, c)
				}
			}
		}
		floor := max(3, (len(pool)+count)*12/100)
		if len(pool)+count == 0 {
			continue
		}
		sort.Slice(pool, func(i, j int) bool {
			if pi, pj := pool[i].priority(), pool[j].priority(); pi != pj {
				return pi < pj
			}
			return pool[i].key < pool[j].key
		})
		for i := 0; count < floor && i < len(pool); i++ {
			take(pool[i], "source:"+source.Name)
			count++
		}
	}
	// Difficulty floor: add the best-priority case carrying each thin factor.
	for _, factor := range DifficultyOrder {
		count := 0
		for _, p := range chosen {
			if containsString(p.row.Difficulties, factor) {
				count++
			}
		}
		var extra []candidate
		for _, pool := range byTask {
			for _, c := range pool {
				if _, done := chosen[c.row.ID]; !done && containsString(c.row.Difficulties, factor) {
					extra = append(extra, c)
				}
			}
		}
		sort.Slice(extra, func(i, j int) bool {
			if pi, pj := extra[i].priority(), extra[j].priority(); pi != pj {
				return pi < pj
			}
			return extra[i].key < extra[j].key
		})
		for i := 0; count < quickDifficultyFloor && i < len(extra); i++ {
			take(extra[i], "difficulty:"+factor)
			count++
		}
	}
	out := make([]pick, 0, len(chosen))
	for _, p := range chosen {
		out = append(out, p)
	}
	sort.Slice(out, func(i, j int) bool {
		a, b := suiteIndex(out[i].row.Suite), suiteIndex(out[j].row.Suite)
		if a != b {
			return a < b
		}
		return out[i].row.ID < out[j].row.ID
	})
	return out
}

func containsString(list []string, want string) bool {
	for _, item := range list {
		if item == want {
			return true
		}
	}
	return false
}

func runSelectQuick(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam select-quick", flag.ContinueOnError)
	runsDir := flags.String("runs", "", "run history directory (default: local/runs)")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	paths := DefaultPaths()
	if *runsDir == "" {
		*runsDir = filepath.Join(paths.Root, "local", "runs")
	}
	exam, err := Assemble(paths)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam select-quick:", err)
		return 1
	}
	history, runs, err := loadHistory(*runsDir)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam select-quick:", err)
		return 1
	}
	picks := selectQuick(exam.Full.Cases, history)
	var b strings.Builder
	fmt.Fprintf(&b, "# agent-exam-quick-v1.0: quick set generated by `rwkv-lab exam select-quick` from %d RWKV run summaries.\n", runs)
	b.WriteString("# Hand edits are allowed (then rerun `rwkv-lab exam build`); a rerun of select-quick overwrites them.\n")
	b.WriteString("# columns: id  # task language pass-rate(runs) reason\n")
	for _, p := range picks {
		rate := "n/a"
		if !math.IsNaN(p.hist.rate()) {
			rate = fmt.Sprintf("%.2f(%d)", p.hist.rate(), p.hist.runs)
		}
		fmt.Fprintf(&b, "%s  # %s %s %s %s\n", p.row.ID, p.row.Task, p.row.Language, rate, p.reason)
	}
	if err := os.WriteFile(paths.QuickIDs, []byte(b.String()), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam select-quick:", err)
		return 1
	}
	fmt.Printf("selected %d quick cases from %d RWKV runs -> %s\n", len(picks), runs, paths.QuickIDs)
	return 0
}
