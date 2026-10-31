package geval

import (
	"bufio"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Scored is one item's verdict, written to scored.jsonl.
type Scored struct {
	ID    string `json:"id"`
	Task  string `json:"task"`
	Error string `json:"error,omitempty"`
	// Correct is the binary verdict (IFEval: prompt-level strict).
	Correct bool `json:"correct"`
	// Scores holds MT-Bench judge ratings per turn (-1: judge unparseable).
	Scores  []float64     `json:"scores,omitempty"`
	Pred    string        `json:"pred,omitempty"`
	Gold    string        `json:"gold,omitempty"`
	Boxed   bool          `json:"boxed,omitempty"`
	ByJudge bool          `json:"by_judge,omitempty"`
	IFEval  *IFEvalResult `json:"ifeval,omitempty"`
	Clean   bool          `json:"clean"`
}

type judgeConfig struct {
	client   *chatClient
	parallel int
	prompts  map[string]map[string]judgePrompt
	cache    *judgeCache
}

type judgePrompt struct {
	Name           string `json:"name"`
	SystemPrompt   string `json:"system_prompt"`
	PromptTemplate string `json:"prompt_template"`
}

func runScore(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab geval score", flag.ContinueOnError)
	itemsPath := flags.String("items", "", "items file (default: the one in run.json)")
	judgeURL := flags.String("judge-url", "", "OpenAI-compatible judge endpoint (e.g. $API_BASE from ~/.commandcode_key.sh)")
	judgeModel := flags.String("judge-model", "deepseek/deepseek-v4.1-flash", "judge model")
	judgeKeyEnv := flags.String("judge-key-env", "CC_API_KEY_1", "environment variable holding the judge key")
	judgeParallel := flags.Int("judge-parallel", 16, "judge requests in flight")
	noJudge := flags.Bool("no-judge", false, "skip the judge: MT-Bench unscored, MATH by rules only")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if flags.NArg() != 1 {
		fmt.Fprintln(os.Stderr, "usage: rwkv-lab geval score [flags] <run dir>")
		return 2
	}
	dir := flags.Arg(0)
	var judge *judgeConfig
	if !*noJudge {
		if *judgeURL == "" {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval score: --judge-url is required (or --no-judge)")
			return 2
		}
		judge = &judgeConfig{
			client: newChatClient(*judgeURL, *judgeModel, os.Getenv(*judgeKeyEnv), nil), parallel: *judgeParallel,
		}
	}
	summary, err := scoreRun(dir, *itemsPath, judge)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval score:", err)
		return 1
	}
	fmt.Print(renderTable([]runSummary{summary}))
	return 0
}

type runSummary struct {
	Dir    string                `json:"dir"`
	Config RunConfig             `json:"config"`
	Judge  string                `json:"judge,omitempty"`
	Tasks  map[string]*TaskScore `json:"tasks"`
	Stats  map[string]*TaskStats `json:"stats"`
	// History is the empty-think rate by turn: turn 1 has no history,
	// turn 2 (MT-Bench) follows an answer carrying `<think></think>`.
	History map[string]Rate `json:"history"`
}

// TaskScore holds a task's headline and its other metrics, over all items
// and over the clean (not contamination-flagged) ones.
type TaskScore struct {
	N        int                `json:"n"`
	Errors   int                `json:"errors"`
	Headline string             `json:"headline"`
	Metrics  map[string]float64 `json:"metrics"`
	Clean    map[string]float64 `json:"clean"`
	NClean   int                `json:"n_clean"`
}

// TaskStats are read off the outputs themselves.
type TaskStats struct {
	Turns          int     `json:"turns"`
	ThinkClosed    Rate    `json:"think_closed"`
	EmptyThink     Rate    `json:"empty_think"`
	Loop           Rate    `json:"loop"`
	HitLimit       Rate    `json:"hit_limit"`
	ThinkLangMatch Rate    `json:"think_lang_match"`
	ThinkCharsP50  int     `json:"think_chars_p50"`
	ThinkCharsP90  int     `json:"think_chars_p90"`
	TokensP50      int     `json:"completion_tokens_p50"`
	AnswerCharsP50 int     `json:"answer_chars_p50"`
	MeanSeconds    float64 `json:"mean_seconds"`
}

// Rate is k of n.
type Rate struct {
	K int     `json:"k"`
	N int     `json:"n"`
	P float64 `json:"p"`
}

func (r *Rate) add(ok bool) {
	r.N++
	if ok {
		r.K++
	}
	r.P = round3(float64(r.K) / float64(r.N))
}

func round3(x float64) float64 { return float64(int(x*1000+0.5)) / 1000 }

func scoreRun(dir, itemsPath string, judge *judgeConfig) (runSummary, error) {
	var cfg RunConfig
	data, err := os.ReadFile(filepath.Join(dir, "run.json"))
	if err != nil {
		return runSummary{}, err
	}
	if err := json.Unmarshal(data, &cfg); err != nil {
		return runSummary{}, err
	}
	if itemsPath == "" {
		itemsPath = cfg.Items
	}
	items, sha, err := loadItems(itemsPath)
	if err != nil {
		return runSummary{}, err
	}
	if sha != cfg.ItemsSHA256 {
		fmt.Fprintf(os.Stderr, "geval score: warning: %s has changed since the run (sha %s… vs %s…); scoring against the current file\n", itemsPath, sha[:12], cfg.ItemsSHA256[:12])
	}
	selected, err := selectItems(items, cfg.Subset, strings.Join(cfg.Tasks, ","), cfg.Limit)
	if err != nil {
		return runSummary{}, err
	}
	records, err := loadRecords(filepath.Join(dir, "results.jsonl"))
	if err != nil {
		return runSummary{}, err
	}
	summary := runSummary{Dir: dir, Config: cfg, Tasks: map[string]*TaskScore{}, Stats: map[string]*TaskStats{}, History: map[string]Rate{}}
	if judge != nil {
		summary.Judge = judge.client.model
		judge.cache, err = openJudgeCache(filepath.Join(dir, "judge.jsonl"))
		if err != nil {
			return summary, err
		}
		defer judge.cache.close()
		if err := judge.loadPrompts(filepath.Join(filepath.Dir(itemsPath), "judge_prompts.json")); err != nil {
			return summary, err
		}
	}
	scored := make([]Scored, len(selected))
	var mu sync.Mutex
	sem := make(chan struct{}, max(1, parallelOf(judge)))
	var wg sync.WaitGroup
	var firstErr error
	for i, item := range selected {
		rec, ok := records[item.ID]
		wg.Add(1)
		sem <- struct{}{}
		go func(i int, item Item, rec Record, ok bool) {
			defer wg.Done()
			defer func() { <-sem }()
			s, err := scoreItem(item, rec, ok, judge)
			mu.Lock()
			defer mu.Unlock()
			if err != nil && firstErr == nil {
				firstErr = err
			}
			scored[i] = s
		}(i, item, rec, ok)
	}
	wg.Wait()
	if firstErr != nil {
		return summary, firstErr
	}
	aggregate(&summary, selected, scored, records)
	if err := writeScored(filepath.Join(dir, "scored.jsonl"), scored); err != nil {
		return summary, err
	}
	out, err := lab.EncodeJSON(summary, 2)
	if err != nil {
		return summary, err
	}
	return summary, os.WriteFile(filepath.Join(dir, "summary.json"), append(out, '\n'), 0o644)
}

func parallelOf(j *judgeConfig) int {
	if j == nil {
		return 8
	}
	return j.parallel
}

func scoreItem(item Item, rec Record, ok bool, judge *judgeConfig) (Scored, error) {
	s := Scored{ID: item.ID, Task: item.Task, Gold: item.Answer, Clean: item.Contam == nil || !item.Contam.Flagged}
	if !ok {
		s.Error = "not run"
		return s, nil
	}
	if rec.Error != "" || len(rec.Turns) < len(item.Turns) {
		s.Error = rec.Error
		if s.Error == "" {
			s.Error = "missing turns"
		}
		return s, nil
	}
	answer := rec.Turns[0].Answer
	switch item.Task {
	case TaskIFEvalEN, TaskIFEvalZH:
		res, err := scoreIFEval(item, answer)
		if err != nil {
			return s, err
		}
		s.IFEval = &res
		s.Correct = allTrue(res.Strict)
	case TaskGSM8K:
		s.Pred, s.Boxed = gsm8kPrediction(answer)
		s.Correct = s.Pred != "" && numbersEqual(s.Pred, item.Answer)
	case TaskMATH500:
		s.Pred = lastBoxed(answer)
		s.Boxed = s.Pred != ""
		s.Correct = mathEqual(s.Pred, item.Answer)
		if !s.Correct && s.Pred != "" && judge != nil {
			eq, err := judge.mathEquivalent(item, s.Pred)
			if err != nil {
				return s, err
			}
			s.Correct, s.ByJudge = eq, eq
		}
	case TaskCEval, TaskCMMLU:
		s.Pred = choicePrediction(answer)
		s.Correct = s.Pred == item.Answer
	case TaskMTBenchEN, TaskMTBenchZH:
		if judge == nil {
			return s, nil
		}
		for turn := range item.Turns {
			score, err := judge.mtbench(item, rec, turn)
			if err != nil {
				return s, err
			}
			s.Scores = append(s.Scores, score)
		}
	}
	return s, nil
}

func allTrue(v []bool) bool {
	for _, b := range v {
		if !b {
			return false
		}
	}
	return true
}

func aggregate(summary *runSummary, items []Item, scored []Scored, records map[string]Record) {
	type acc struct {
		n, nClean, errors                     int
		correct, correctClean                 int
		instS, instSN, instL, promptL         int
		instSClean, instSNClean, promptLClean int
		instLClean                            int
		boxed                                 int
		turnScores                            [2][]float64
		turnScoresClean                       [2][]float64
	}
	accs := map[string]*acc{}
	for _, s := range scored {
		a := accs[s.Task]
		if a == nil {
			a = &acc{}
			accs[s.Task] = a
		}
		a.n++
		if s.Clean {
			a.nClean++
		}
		if s.Error != "" {
			a.errors++
			continue
		}
		if s.Correct {
			a.correct++
			if s.Clean {
				a.correctClean++
			}
		}
		if s.Boxed {
			a.boxed++
		}
		if r := s.IFEval; r != nil {
			nS, nL := countTrue(r.Strict), countTrue(r.Loose)
			a.instS += nS
			a.instL += nL
			a.instSN += len(r.Strict)
			if allTrue(r.Loose) {
				a.promptL++
			}
			if s.Clean {
				a.instSClean += nS
				a.instLClean += nL
				a.instSNClean += len(r.Strict)
				if allTrue(r.Loose) {
					a.promptLClean++
				}
			}
		}
		for t, v := range s.Scores {
			if v >= 0 && t < 2 {
				a.turnScores[t] = append(a.turnScores[t], v)
				if s.Clean {
					a.turnScoresClean[t] = append(a.turnScoresClean[t], v)
				}
			}
		}
	}
	for task, a := range accs {
		ts := &TaskScore{N: a.n, Errors: a.errors, NClean: a.nClean, Metrics: map[string]float64{}, Clean: map[string]float64{}}
		pct := func(k, n int) float64 {
			if n == 0 {
				return 0
			}
			return round3(100 * float64(k) / float64(n))
		}
		switch task {
		case TaskIFEvalEN, TaskIFEvalZH:
			ts.Headline = "prompt_strict"
			ts.Metrics["prompt_strict"] = pct(a.correct, a.n)
			ts.Metrics["inst_strict"] = pct(a.instS, a.instSN)
			ts.Metrics["prompt_loose"] = pct(a.promptL, a.n)
			ts.Metrics["inst_loose"] = pct(a.instL, a.instSN)
			ts.Clean["prompt_strict"] = pct(a.correctClean, a.nClean)
			ts.Clean["inst_strict"] = pct(a.instSClean, a.instSNClean)
			ts.Clean["prompt_loose"] = pct(a.promptLClean, a.nClean)
			ts.Clean["inst_loose"] = pct(a.instLClean, a.instSNClean)
		case TaskMTBenchEN, TaskMTBenchZH:
			ts.Headline = "score"
			all := append(append([]float64(nil), a.turnScores[0]...), a.turnScores[1]...)
			allClean := append(append([]float64(nil), a.turnScoresClean[0]...), a.turnScoresClean[1]...)
			ts.Metrics["score"] = mean(all)
			ts.Metrics["turn1"] = mean(a.turnScores[0])
			ts.Metrics["turn2"] = mean(a.turnScores[1])
			ts.Metrics["judged"] = float64(len(all))
			ts.Clean["score"] = mean(allClean)
		default:
			ts.Headline = "acc"
			ts.Metrics["acc"] = pct(a.correct, a.n)
			ts.Clean["acc"] = pct(a.correctClean, a.nClean)
			if task == TaskGSM8K || task == TaskMATH500 {
				ts.Metrics["boxed"] = pct(a.boxed, a.n-a.errors)
			}
		}
		summary.Tasks[task] = ts
	}
	langOf := map[string]string{}
	for _, item := range items {
		langOf[item.ID] = item.Lang
	}
	thinkChars := map[string][]int{}
	tokens := map[string][]int{}
	answerChars := map[string][]int{}
	seconds := map[string][]float64{}
	history := map[string]*Rate{}
	for _, s := range scored {
		rec, ok := records[s.ID]
		if !ok || rec.Error != "" {
			continue
		}
		st := summary.Stats[s.Task]
		if st == nil {
			st = &TaskStats{}
			summary.Stats[s.Task] = st
		}
		for t, turn := range rec.Turns {
			st.Turns++
			st.ThinkClosed.add(turn.ThinkClosed)
			st.EmptyThink.add(turn.EmptyThink)
			st.Loop.add(turn.Loop)
			st.HitLimit.add(turn.Finish == "length")
			if turn.Think != "" {
				st.ThinkLangMatch.add(textLang(turn.Think) == langOf[s.ID])
				thinkChars[s.Task] = append(thinkChars[s.Task], len([]rune(turn.Think)))
			}
			if turn.CompletionTokens > 0 {
				// A loop-guard cut ends the stream before usage arrives.
				tokens[s.Task] = append(tokens[s.Task], turn.CompletionTokens)
			}
			answerChars[s.Task] = append(answerChars[s.Task], len([]rune(turn.Answer)))
			seconds[s.Task] = append(seconds[s.Task], float64(turn.Millis)/1000)
			key := fmt.Sprintf("turn%d", t+1)
			if history[key] == nil {
				history[key] = &Rate{}
			}
			history[key].add(turn.EmptyThink)
		}
	}
	for task, st := range summary.Stats {
		st.ThinkCharsP50 = percentile(thinkChars[task], 50)
		st.ThinkCharsP90 = percentile(thinkChars[task], 90)
		st.TokensP50 = percentile(tokens[task], 50)
		st.AnswerCharsP50 = percentile(answerChars[task], 50)
		st.MeanSeconds = round3(mean(seconds[task]))
	}
	for k, v := range history {
		summary.History[k] = *v
	}
}

func countTrue(v []bool) int {
	n := 0
	for _, b := range v {
		if b {
			n++
		}
	}
	return n
}

func mean(v []float64) float64 {
	if len(v) == 0 {
		return 0
	}
	sum := 0.0
	for _, x := range v {
		sum += x
	}
	return round3(sum / float64(len(v)))
}

func percentile(v []int, p int) int {
	if len(v) == 0 {
		return 0
	}
	s := append([]int(nil), v...)
	sort.Ints(s)
	i := (len(s) - 1) * p / 100
	return s[i]
}

// textLang is "zh" when Han characters are at least half of the words
// (each Han character counted as a word), else "en".
func textLang(text string) string {
	han, latinWords := 0, 0
	inWord := false
	for _, r := range text {
		switch {
		case unicode.Is(unicode.Han, r):
			han++
			inWord = false
		case r < 128 && unicode.IsLetter(r):
			if !inWord {
				latinWords++
			}
			inWord = true
		default:
			inWord = false
		}
	}
	if han > 0 && han >= latinWords {
		return "zh"
	}
	return "en"
}

func writeScored(path string, scored []Scored) error {
	var b strings.Builder
	for _, s := range scored {
		line, err := lab.EncodeJSON(s, 0)
		if err != nil {
			return err
		}
		b.Write(line)
		b.WriteByte('\n')
	}
	return os.WriteFile(path, []byte(b.String()), 0o644)
}

// --- judge ---------------------------------------------------------------

func (j *judgeConfig) loadPrompts(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, &j.prompts)
}

var (
	reRating       = regexp.MustCompile(`\[\[(\d+\.?\d*)\]\]`)
	reRatingBackup = regexp.MustCompile(`\[(\d+\.?\d*)\]`)
)

// mtbench rates one turn as FastChat's single-answer grading does: turn 1
// alone, turn 2 with the whole conversation, against the reference answer
// for math, reasoning and coding.
func (j *judgeConfig) mtbench(item Item, rec Record, turn int) (float64, error) {
	if strings.TrimSpace(rec.Turns[turn].Answer) == "" {
		// No answer (think never closed): the lowest rating, no call.
		return 1, nil
	}
	name := "single-v1"
	if len(item.Reference) > 0 {
		name = "single-math-v1"
	}
	if turn > 0 {
		name += "-multi-turn"
	}
	lang := "en"
	if item.Lang == "zh" {
		lang = "zh"
	}
	p, ok := j.prompts[lang][name]
	if !ok {
		return 0, fmt.Errorf("no judge prompt %s/%s", lang, name)
	}
	vars := map[string]string{}
	if turn == 0 {
		vars["question"] = item.Turns[0]
		vars["answer"] = rec.Turns[0].Answer
		if len(item.Reference) > 0 {
			vars["ref_answer_1"] = item.Reference[0]
		}
	} else {
		vars["question_1"], vars["question_2"] = item.Turns[0], item.Turns[1]
		vars["answer_1"], vars["answer_2"] = rec.Turns[0].Answer, rec.Turns[1].Answer
		if len(item.Reference) > 1 {
			vars["ref_answer_1"], vars["ref_answer_2"] = item.Reference[0], item.Reference[1]
		}
	}
	user := fillTemplate(p.PromptTemplate, vars)
	out, err := j.ask(fmt.Sprintf("mtbench/%s/%d", item.ID, turn+1), p.SystemPrompt, user)
	if err != nil {
		return 0, err
	}
	return parseRating(out), nil
}

func fillTemplate(tmpl string, vars map[string]string) string {
	pairs := make([]string, 0, 2*len(vars))
	for k, v := range vars {
		pairs = append(pairs, "{"+k+"}", v)
	}
	return strings.NewReplacer(pairs...).Replace(tmpl)
}

func parseRating(out string) float64 {
	m := reRating.FindAllStringSubmatch(out, -1)
	if len(m) == 0 {
		m = reRatingBackup.FindAllStringSubmatch(out, -1)
	}
	if len(m) == 0 {
		return -1
	}
	v, err := strconv.ParseFloat(m[len(m)-1][1], 64)
	if err != nil || v < 0 || v > 10 {
		return -1
	}
	return v
}

const mathJudgeSystem = "You compare a student's final answer to a math problem with the reference answer."

func (j *judgeConfig) mathEquivalent(item Item, pred string) (bool, error) {
	user := fmt.Sprintf("Problem:\n%s\n\nReference answer: %s\nStudent's final answer: %s\n\n"+
		"Are the two answers mathematically equivalent (same value, expression, set or interval; ignore formatting, units and equivalent forms)? "+
		"Reply with exactly one word: YES or NO.", item.Raw, item.Answer, pred)
	out, err := j.ask("math/"+item.ID, mathJudgeSystem, user)
	if err != nil {
		return false, err
	}
	out = strings.ToUpper(strings.TrimSpace(out))
	return strings.HasPrefix(out, "YES") || (strings.Contains(out, "YES") && !strings.Contains(out, "NO")), nil
}

// ask sends one judge request, served from judge.jsonl when the same
// (model, prompt) was asked before.
func (j *judgeConfig) ask(label, system, user string) (string, error) {
	sum := sha256.Sum256([]byte(j.client.model + "\x00" + system + "\x00" + user))
	key := hex.EncodeToString(sum[:])
	if out, ok := j.cache.get(key); ok {
		return out, nil
	}
	reply, err := j.client.complete(context.Background(), []chatMessage{{"system", system}, {"user", user}},
		map[string]any{"temperature": 0.2, "max_tokens": 8192})
	if err != nil {
		return "", fmt.Errorf("judge %s: %w", label, err)
	}
	if err := j.cache.put(key, label, reply.Content); err != nil {
		return "", err
	}
	return reply.Content, nil
}

type judgeCache struct {
	mu  sync.Mutex
	m   map[string]string
	out *os.File
}

func openJudgeCache(path string) (*judgeCache, error) {
	c := &judgeCache{m: map[string]string{}}
	if fh, err := os.Open(path); err == nil {
		scanner := bufio.NewScanner(fh)
		scanner.Buffer(make([]byte, 1<<20), 64<<20)
		for scanner.Scan() {
			var row struct{ Key, Output string }
			if json.Unmarshal(scanner.Bytes(), &row) == nil {
				c.m[row.Key] = row.Output
			}
		}
		fh.Close()
	} else if !errors.Is(err, os.ErrNotExist) {
		return nil, err
	}
	out, err := os.OpenFile(path, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		return nil, err
	}
	if err := endWithNewline(out); err != nil {
		return nil, err
	}
	c.out = out
	return c, nil
}

func (c *judgeCache) get(key string) (string, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	v, ok := c.m[key]
	return v, ok
}

func (c *judgeCache) put(key, label, output string) error {
	line, err := lab.EncodeJSON(map[string]string{"key": key, "label": label, "output": output}, 0)
	if err != nil {
		return err
	}
	c.mu.Lock()
	defer c.mu.Unlock()
	c.m[key] = output
	_, err = c.out.Write(append(line, '\n'))
	return err
}

func (c *judgeCache) close() { c.out.Close() }
