package runs

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

// Per-case cost report: which cases held a run up, on time and on tokens.
//
// A run written with per-case cost (summary cases[].cost, turns[].cost) is
// read as recorded. An older run is recomputed from its steps: wall time from
// the step timestamps (or, for runs older than those, from the trace record
// timestamps), model and tool time from the step durations, tokens from the
// step usage. rwkv_lightning runs from before the counts were recorded carry
// zero usage; for those the prompts and outputs in trace.jsonl are counted
// with the local World vocabulary (cheap, in-process), unless --no-recount
// asks to show them as missing.

// CostArgs are the `run cost` flags.
type CostArgs struct {
	Runs []string
	Top  int
	JSON bool
	// NoRecount leaves tokens missing from the summary as missing instead of
	// counting them from trace.jsonl.
	NoRecount bool
	Vocab     string
	// counter replaces the World vocabulary in tests.
	counter func(string) int
}

// costRecord mirrors eval.Cost as summary.json carries it.
type costRecord struct {
	StartedAtMS        int64  `json:"started_at_ms"`
	EndedAtMS          int64  `json:"ended_at_ms"`
	WallMS             int64  `json:"wall_ms"`
	ModelMS            int64  `json:"model_ms"`
	ToolMS             int64  `json:"tool_ms"`
	Steps              int    `json:"steps"`
	MaxSteps           int    `json:"max_steps"`
	PromptTokens       int    `json:"prompt_tokens"`
	CompletionTokens   int    `json:"completion_tokens"`
	MaxPromptTokens    int    `json:"max_prompt_tokens"`
	TokenSource        string `json:"token_source"`
	TokensMissingSteps int    `json:"tokens_missing_steps"`
	LengthSteps        int    `json:"length_steps"`
	HitMaxTokens       bool   `json:"hit_max_tokens"`
	HitMaxSteps        bool   `json:"hit_max_steps"`
	HitTimeout         bool   `json:"hit_timeout"`
}

type costStepFile struct {
	ModelStartedAtMS int64  `json:"model_started_at_ms"`
	ModelDurationMS  int64  `json:"model_duration_ms"`
	ToolStartedAtMS  int64  `json:"tool_started_at_ms"`
	ToolDurationMS   int64  `json:"tool_duration_ms"`
	FinishReason     string `json:"finish_reason"`
	ModelError       string `json:"model_error"`
	Usage            struct {
		PromptTokens     int    `json:"prompt_tokens"`
		CompletionTokens int    `json:"completion_tokens"`
		PromptSource     string `json:"prompt_source"`
		CompletionSource string `json:"completion_source"`
	} `json:"usage"`
}

type costTurnFile struct {
	RunnerError string `json:"runner_error"`
	Result      struct {
		StartedAtMS        int64  `json:"started_at_ms"`
		ForcedAnswerReason string `json:"forced_answer_reason"`
		RouteSteps         []struct {
			StartedAtMS int64 `json:"started_at_ms"`
			DurationMS  int64 `json:"duration_ms"`
		} `json:"route_steps"`
		Steps []costStepFile `json:"steps"`
	} `json:"result"`
	Cost *costRecord `json:"cost"`
}

type costCaseFile struct {
	ID       string         `json:"id"`
	Category string         `json:"category"`
	Tags     map[string]any `json:"tags"`
	Passed   bool           `json:"passed"`
	Invalid  bool           `json:"invalid"`
	Error    string         `json:"error"`
	Turns    []costTurnFile `json:"turns"`
	Cost     *costRecord    `json:"cost"`
}

type costSummaryFile struct {
	RunID   string `json:"run_id"`
	Metrics struct {
		WallTimeMillis int64 `json:"wall_time_millis"`
	} `json:"metrics"`
	Cases []costCaseFile `json:"cases"`
}

type costRunFile struct {
	RunID     string    `json:"run_id"`
	StartedAt time.Time `json:"started_at"`
	Harness   struct {
		MaxSteps        int    `json:"max_steps"`
		CaseParallelism int    `json:"case_parallelism"`
		StateID         string `json:"state_id"`
	} `json:"harness"`
	CaseWires []struct {
		ID       string `json:"id"`
		MaxSteps int    `json:"max_steps"`
	} `json:"case_wires"`
}

// CaseCost is one case of one run.
type CaseCost struct {
	Run       string `json:"run"`
	ID        string `json:"id"`
	Passed    bool   `json:"passed"`
	Invalid   bool   `json:"invalid,omitempty"`
	Scenario  string `json:"scenario,omitempty"`
	ProbeAxis string `json:"probe_axis,omitempty"`
	// StartOffsetMS and EndOffsetMS place the case on the run's clock; 0 when
	// the artifacts carry no timestamps.
	StartOffsetMS    int64  `json:"start_offset_ms"`
	EndOffsetMS      int64  `json:"end_offset_ms"`
	WallMS           int64  `json:"wall_ms"`
	ModelMS          int64  `json:"model_ms"`
	ToolMS           int64  `json:"tool_ms"`
	Steps            int    `json:"steps"`
	MaxSteps         int    `json:"max_steps,omitempty"`
	PromptTokens     int    `json:"prompt_tokens"`
	CompletionTokens int    `json:"completion_tokens"`
	MaxPromptTokens  int    `json:"max_prompt_tokens"`
	TokenSource      string `json:"token_source,omitempty"`
	HitMaxTokens     bool   `json:"hit_max_tokens,omitempty"`
	HitMaxSteps      bool   `json:"hit_max_steps,omitempty"`
	HitTimeout       bool   `json:"hit_timeout,omitempty"`
	// TimeSource says how the clock was obtained: "recorded" (summary
	// cost), "steps" (recomputed from step timestamps), "trace" (trace record
	// timestamps), or empty when the artifacts carry no timestamps.
	TimeSource string `json:"time_source"`
	start      int64
	end        int64
}

// TokensKnown reports whether the case carries any token count.
func (c CaseCost) TokensKnown() bool { return c.TokenSource != "" }

// Stat is the mean and maximum of one metric over the runs that have it.
type Stat struct {
	Mean float64 `json:"mean"`
	Max  float64 `json:"max"`
	N    int     `json:"n"`
}

func statOf(values []float64) Stat {
	if len(values) == 0 {
		return Stat{}
	}
	stat := Stat{Max: values[0], N: len(values)}
	sum := 0.0
	for _, value := range values {
		sum += value
		if value > stat.Max {
			stat.Max = value
		}
	}
	stat.Mean = sum / float64(len(values))
	return stat
}

// MergedCost is one case over every run that contains it.
type MergedCost struct {
	ID               string `json:"id"`
	Scenario         string `json:"scenario,omitempty"`
	ProbeAxis        string `json:"probe_axis,omitempty"`
	Runs             int    `json:"runs"`
	Passes           int    `json:"passes"`
	Invalid          int    `json:"invalid,omitempty"`
	WallMS           Stat   `json:"wall_ms"`
	ModelMS          Stat   `json:"model_ms"`
	ToolMS           Stat   `json:"tool_ms"`
	Steps            Stat   `json:"steps"`
	EndOffsetMS      Stat   `json:"end_offset_ms"`
	PromptTokens     Stat   `json:"prompt_tokens"`
	CompletionTokens Stat   `json:"completion_tokens"`
	MaxPromptTokens  Stat   `json:"max_prompt_tokens"`
	TokenSource      string `json:"token_source,omitempty"`
	MaxTokensHits    int    `json:"max_tokens_hits"`
	MaxStepsHits     int    `json:"max_steps_hits"`
	TimeoutHits      int    `json:"timeout_hits"`
}

// GroupCost aggregates the merged cases of one scenario or probe axis.
type GroupCost struct {
	Key              string  `json:"key"`
	Cases            int     `json:"cases"`
	CaseRuns         int     `json:"case_runs"`
	PassRate         float64 `json:"pass_rate"`
	WallMS           Stat    `json:"wall_ms"`
	ModelMS          Stat    `json:"model_ms"`
	Steps            Stat    `json:"steps"`
	CompletionTokens Stat    `json:"completion_tokens"`
	MaxPromptTokens  Stat    `json:"max_prompt_tokens"`
	WallShare        float64 `json:"wall_share"`
	MaxTokensHits    int     `json:"max_tokens_hits"`
	MaxStepsHits     int     `json:"max_steps_hits"`
	TimeoutHits      int     `json:"timeout_hits"`
}

// RunCostInfo describes one input run.
type RunCostInfo struct {
	Dir             string `json:"dir"`
	RunID           string `json:"run_id"`
	Cases           int    `json:"cases"`
	WallMS          int64  `json:"wall_ms"`
	CaseParallelism int    `json:"case_parallelism,omitempty"`
	StateID         string `json:"state_id,omitempty"`
	CostRecorded    int    `json:"cost_recorded"`
	TokensKnown     int    `json:"tokens_known"`
	Recounted       int    `json:"recounted,omitempty"`
}

// CostReport is the whole `run cost` payload.
type CostReport struct {
	Runs     []RunCostInfo          `json:"runs"`
	Top      int                    `json:"top"`
	Rankings map[string][]string    `json:"rankings"`
	Cases    []MergedCost           `json:"cases"`
	Groups   map[string][]GroupCost `json:"groups"`
	PerRun   []CaseCost             `json:"per_run"`
}

// Ranking keys, in report order.
var costRankings = []struct {
	key   string
	title string
	value func(MergedCost) float64
}{
	{"wall_ms", "Wall time", func(c MergedCost) float64 { return c.WallMS.Mean }},
	{"completion_tokens", "Generated tokens (whole case)", func(c MergedCost) float64 { return c.CompletionTokens.Mean }},
	{"max_prompt_tokens", "Largest context (longest step prompt)", func(c MergedCost) float64 { return c.MaxPromptTokens.Mean }},
	{"end_offset_ms", "Last to finish (end time from run start)", func(c MergedCost) float64 { return c.EndOffsetMS.Mean }},
}

// RunCost is the `run cost` command.
func RunCost(args CostArgs) int {
	report, err := BuildCostReport(args)
	if err != nil {
		fmt.Fprintf(stderr, "error: %s\n", err)
		return 1
	}
	if args.JSON {
		data, err := json.MarshalIndent(report, "", "  ")
		if err != nil {
			fmt.Fprintf(stderr, "error: %s\n", err)
			return 1
		}
		fmt.Println(string(data))
		return 0
	}
	fmt.Print(RenderCostMarkdown(report))
	return 0
}

// BuildCostReport loads every run and builds the merged report.
func BuildCostReport(args CostArgs) (CostReport, error) {
	if args.Top <= 0 {
		args.Top = 15
	}
	var count func(string) int
	if !args.NoRecount {
		count = args.counter
	}
	if !args.NoRecount && count == nil {
		var world *tokenizer.World
		var err error
		if args.Vocab != "" {
			world, err = tokenizer.OpenWorldCached(args.Vocab)
		} else {
			world, err = lab.OpenWorld()
		}
		switch {
		case err == nil:
			count = world.Count
		case args.Vocab != "":
			return CostReport{}, fmt.Errorf("--vocab: %v", err)
		default:
			// Without the vocabulary the report still works; missing
			// counts stay missing.
			fmt.Fprintf(stderr, "warning: no World vocabulary (%v); tokens missing from the summary stay missing\n", err)
		}
	}
	report := CostReport{Top: args.Top, Rankings: map[string][]string{}, Groups: map[string][]GroupCost{}}
	for _, dir := range args.Runs {
		info, cases, err := loadRunCost(dir, count)
		if err != nil {
			return CostReport{}, err
		}
		report.Runs = append(report.Runs, info)
		report.PerRun = append(report.PerRun, cases...)
	}
	report.Cases = mergeCaseCosts(report.PerRun)
	for _, ranking := range costRankings {
		ranked := rankCosts(report.Cases, ranking.value)
		ids := make([]string, 0, args.Top)
		for index, item := range ranked {
			if index >= args.Top {
				break
			}
			ids = append(ids, item.ID)
		}
		report.Rankings[ranking.key] = ids
	}
	report.Groups["scenario"] = groupCosts(report.Cases, func(c MergedCost) string { return c.Scenario })
	report.Groups["probe_axis"] = groupCosts(report.Cases, func(c MergedCost) string { return c.ProbeAxis })
	return report, nil
}

func loadRunCost(dir string, count func(string) int) (RunCostInfo, []CaseCost, error) {
	info := RunCostInfo{Dir: dir}
	var run costRunFile
	if err := readJSONInto(filepath.Join(dir, "run.json"), &run); err != nil {
		return info, nil, err
	}
	var summary costSummaryFile
	if err := readJSONInto(filepath.Join(dir, "summary.json"), &summary); err != nil {
		return info, nil, err
	}
	info.RunID = firstNonEmptyString(summary.RunID, run.RunID)
	info.Cases = len(summary.Cases)
	info.WallMS = summary.Metrics.WallTimeMillis
	info.CaseParallelism = run.Harness.CaseParallelism
	info.StateID = run.Harness.StateID
	maxSteps := map[string]int{}
	for _, wire := range run.CaseWires {
		maxSteps[wire.ID] = wire.MaxSteps
	}
	runStart := int64(0)
	if !run.StartedAt.IsZero() {
		runStart = run.StartedAt.UnixMilli()
	}
	label := filepath.Base(filepath.Clean(dir))
	cases := make([]CaseCost, 0, len(summary.Cases))
	needTrace := false
	for _, file := range summary.Cases {
		limit := maxSteps[file.ID]
		if limit == 0 {
			limit = run.Harness.MaxSteps
		}
		item := caseCostOf(file, limit)
		item.Run = label
		if file.Cost != nil {
			info.CostRecorded++
		}
		if item.start == 0 || (count != nil && !item.TokensKnown()) {
			needTrace = true
		}
		cases = append(cases, item)
	}
	if needTrace {
		recounted, err := applyTrace(filepath.Join(dir, "trace.jsonl"), cases, count)
		if err != nil {
			return info, nil, err
		}
		info.Recounted = recounted
	}
	for index := range cases {
		item := &cases[index]
		if runStart > 0 && item.start > 0 {
			item.StartOffsetMS = item.start - runStart
			item.EndOffsetMS = item.end - runStart
		}
		if item.TokensKnown() {
			info.TokensKnown++
		}
	}
	return info, cases, nil
}

// caseCostOf reads a case's recorded cost, or recomputes it from its steps.
func caseCostOf(file costCaseFile, maxSteps int) CaseCost {
	item := CaseCost{
		ID:        file.ID,
		Passed:    file.Passed,
		Invalid:   file.Invalid,
		Scenario:  tagString(file.Tags, "scenario", file.Category),
		ProbeAxis: tagString(file.Tags, "probe_axis", ""),
	}
	if file.Cost != nil {
		cost := file.Cost
		item.start, item.end = cost.StartedAtMS, cost.EndedAtMS
		item.WallMS, item.ModelMS, item.ToolMS = cost.WallMS, cost.ModelMS, cost.ToolMS
		item.Steps, item.MaxSteps = cost.Steps, cost.MaxSteps
		item.PromptTokens, item.CompletionTokens = cost.PromptTokens, cost.CompletionTokens
		item.MaxPromptTokens, item.TokenSource = cost.MaxPromptTokens, cost.TokenSource
		item.HitMaxTokens, item.HitMaxSteps, item.HitTimeout = cost.HitMaxTokens, cost.HitMaxSteps, cost.HitTimeout
		item.TimeSource = "recorded"
		return item
	}
	item.MaxSteps = maxSteps
	sources := map[string]bool{}
	for _, turn := range file.Turns {
		result := turn.Result
		stretch := func(start, duration int64) {
			if start <= 0 {
				return
			}
			if item.start == 0 || start < item.start {
				item.start = start
			}
			if start+duration > item.end {
				item.end = start + duration
			}
		}
		stretch(result.StartedAtMS, 0)
		for _, route := range result.RouteSteps {
			item.ModelMS += route.DurationMS
			stretch(route.StartedAtMS, route.DurationMS)
		}
		for _, step := range result.Steps {
			item.ModelMS += step.ModelDurationMS
			item.ToolMS += step.ToolDurationMS
			stretch(step.ModelStartedAtMS, step.ModelDurationMS)
			stretch(step.ToolStartedAtMS, step.ToolDurationMS)
			usage := step.Usage
			item.PromptTokens += usage.PromptTokens
			item.CompletionTokens += usage.CompletionTokens
			item.MaxPromptTokens = max(item.MaxPromptTokens, usage.PromptTokens)
			if usage.PromptTokens > 0 {
				sources[firstNonEmptyString(usage.PromptSource, "server")] = true
			}
			if usage.CompletionTokens > 0 {
				sources[firstNonEmptyString(usage.CompletionSource, "server")] = true
			}
			if step.FinishReason == "length" {
				item.HitMaxTokens = true
			}
		}
		turnSteps := len(result.Steps)
		item.Steps += turnSteps
		lowered := strings.ToLower(turn.RunnerError)
		if strings.Contains(lowered, "step limit") ||
			result.ForcedAnswerReason == "step_budget_after_tool_attempt" ||
			(maxSteps > 0 && turnSteps >= maxSteps) {
			item.HitMaxSteps = true
		}
		if strings.Contains(lowered, "deadline exceeded") {
			item.HitTimeout = true
		}
	}
	if strings.Contains(strings.ToLower(file.Error), "deadline exceeded") {
		item.HitTimeout = true
	}
	item.TokenSource = joinSortedKeys(sources)
	if item.start > 0 {
		item.WallMS = item.end - item.start
		item.TimeSource = "steps"
	}
	return item
}

type traceLine struct {
	Timestamp time.Time `json:"timestamp"`
	CaseID    string    `json:"case_id"`
	ModelCall *struct {
		Request struct {
			Prompt string `json:"prompt"`
		} `json:"request"`
		Response struct {
			Text string `json:"text"`
		} `json:"response"`
	} `json:"model_call"`
}

// applyTrace fills what the summary lacks from trace.jsonl: the case clock
// from the first and last record timestamps, and (with a counter) the token
// counts of every model call, route calls included. It returns how many cases
// were recounted.
func applyTrace(path string, cases []CaseCost, count func(string) int) (int, error) {
	file, err := os.Open(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return 0, nil
		}
		return 0, err
	}
	defer file.Close()
	index := map[string]int{}
	for position, item := range cases {
		index[item.ID] = position
	}
	type tally struct {
		first, last        int64
		prompt, completion int
		maxPrompt, calls   int
	}
	tallies := map[string]*tally{}
	reader := bufio.NewReaderSize(file, 1<<20)
	for {
		line, readErr := reader.ReadBytes('\n')
		if len(strings.TrimSpace(string(line))) > 0 {
			var record traceLine
			if json.Unmarshal(line, &record) == nil {
				if _, ok := index[record.CaseID]; ok {
					current := tallies[record.CaseID]
					if current == nil {
						current = &tally{}
						tallies[record.CaseID] = current
					}
					if !record.Timestamp.IsZero() {
						stamp := record.Timestamp.UnixMilli()
						if current.first == 0 || stamp < current.first {
							current.first = stamp
						}
						current.last = max(current.last, stamp)
					}
					if record.ModelCall != nil && count != nil {
						prompt := count(record.ModelCall.Request.Prompt)
						current.prompt += prompt
						current.completion += count(record.ModelCall.Response.Text)
						current.maxPrompt = max(current.maxPrompt, prompt)
						current.calls++
					}
				}
			}
		}
		if readErr == io.EOF {
			break
		}
		if readErr != nil {
			return 0, readErr
		}
	}
	recounted := 0
	for id, current := range tallies {
		item := &cases[index[id]]
		if item.start == 0 && current.first > 0 {
			item.start, item.end = current.first, current.last
			item.WallMS = current.last - current.first
			item.TimeSource = "trace"
		}
		if !item.TokensKnown() && current.calls > 0 {
			item.PromptTokens = current.prompt
			item.CompletionTokens = current.completion
			item.MaxPromptTokens = current.maxPrompt
			item.TokenSource = "local_vocab_trace"
			recounted++
		}
	}
	return recounted, nil
}

func mergeCaseCosts(perRun []CaseCost) []MergedCost {
	order := []string{}
	groups := map[string][]CaseCost{}
	for _, item := range perRun {
		if _, ok := groups[item.ID]; !ok {
			order = append(order, item.ID)
		}
		groups[item.ID] = append(groups[item.ID], item)
	}
	merged := make([]MergedCost, 0, len(order))
	for _, id := range order {
		items := groups[id]
		out := MergedCost{ID: id, Scenario: items[0].Scenario, ProbeAxis: items[0].ProbeAxis, Runs: len(items)}
		var wall, model, tool, steps, end, prompt, completion, maxPrompt []float64
		sources := map[string]bool{}
		for _, item := range items {
			if item.Passed {
				out.Passes++
			}
			if item.Invalid {
				out.Invalid++
			}
			if item.HitMaxTokens {
				out.MaxTokensHits++
			}
			if item.HitMaxSteps {
				out.MaxStepsHits++
			}
			if item.HitTimeout {
				out.TimeoutHits++
			}
			steps = append(steps, float64(item.Steps))
			// Step durations exist only where steps carry timing; a trace clock
			// gives the wall time alone.
			if item.TimeSource == "recorded" || item.TimeSource == "steps" {
				model = append(model, float64(item.ModelMS))
				tool = append(tool, float64(item.ToolMS))
			}
			if item.TimeSource != "" {
				wall = append(wall, float64(item.WallMS))
			}
			if item.EndOffsetMS > 0 {
				end = append(end, float64(item.EndOffsetMS))
			}
			if item.TokensKnown() {
				prompt = append(prompt, float64(item.PromptTokens))
				completion = append(completion, float64(item.CompletionTokens))
				maxPrompt = append(maxPrompt, float64(item.MaxPromptTokens))
				for _, source := range strings.Split(item.TokenSource, "+") {
					sources[source] = true
				}
			}
		}
		out.WallMS, out.ModelMS, out.ToolMS = statOf(wall), statOf(model), statOf(tool)
		out.Steps, out.EndOffsetMS = statOf(steps), statOf(end)
		out.PromptTokens, out.CompletionTokens = statOf(prompt), statOf(completion)
		out.MaxPromptTokens = statOf(maxPrompt)
		out.TokenSource = joinSortedKeys(sources)
		merged = append(merged, out)
	}
	return merged
}

// rankCosts sorts descending by value, dropping cases without the metric;
// ties keep the input order.
func rankCosts(cases []MergedCost, value func(MergedCost) float64) []MergedCost {
	ranked := make([]MergedCost, 0, len(cases))
	for _, item := range cases {
		if value(item) > 0 {
			ranked = append(ranked, item)
		}
	}
	sort.SliceStable(ranked, func(i, j int) bool { return value(ranked[i]) > value(ranked[j]) })
	return ranked
}

func groupCosts(cases []MergedCost, key func(MergedCost) string) []GroupCost {
	order := []string{}
	groups := map[string][]MergedCost{}
	totalWall := 0.0
	for _, item := range cases {
		name := key(item)
		if name == "" {
			name = "-"
		}
		if _, ok := groups[name]; !ok {
			order = append(order, name)
		}
		groups[name] = append(groups[name], item)
		totalWall += item.WallMS.Mean
	}
	out := make([]GroupCost, 0, len(order))
	for _, name := range order {
		items := groups[name]
		group := GroupCost{Key: name, Cases: len(items)}
		var wall, model, steps, completion, maxPrompt []float64
		passes, groupWall := 0, 0.0
		for _, item := range items {
			group.CaseRuns += item.Runs
			passes += item.Passes
			group.MaxTokensHits += item.MaxTokensHits
			group.MaxStepsHits += item.MaxStepsHits
			group.TimeoutHits += item.TimeoutHits
			if item.WallMS.N > 0 {
				wall = append(wall, item.WallMS.Mean)
				groupWall += item.WallMS.Mean
			}
			if item.ModelMS.N > 0 {
				model = append(model, item.ModelMS.Mean)
			}
			steps = append(steps, item.Steps.Mean)
			if item.CompletionTokens.N > 0 {
				completion = append(completion, item.CompletionTokens.Mean)
				maxPrompt = append(maxPrompt, item.MaxPromptTokens.Mean)
			}
		}
		if group.CaseRuns > 0 {
			group.PassRate = float64(passes) / float64(group.CaseRuns)
		}
		if totalWall > 0 {
			group.WallShare = groupWall / totalWall
		}
		group.WallMS, group.ModelMS, group.Steps = statOf(wall), statOf(model), statOf(steps)
		group.CompletionTokens, group.MaxPromptTokens = statOf(completion), statOf(maxPrompt)
		out = append(out, group)
	}
	sort.SliceStable(out, func(i, j int) bool { return out[i].WallMS.Mean > out[j].WallMS.Mean })
	return out
}

// RenderCostMarkdown renders the report as Markdown tables.
func RenderCostMarkdown(report CostReport) string {
	var b strings.Builder
	multi := len(report.Runs) > 1
	b.WriteString("# Case cost report\n\n")
	b.WriteString("| run | cases | run wall | parallelism | cost recorded | tokens known |\n")
	b.WriteString("|---|---:|---:|---:|---:|---:|\n")
	for _, run := range report.Runs {
		known := fmt.Sprintf("%d", run.TokensKnown)
		if run.Recounted > 0 {
			known += fmt.Sprintf(" (%d recounted)", run.Recounted)
		}
		parallelism := "—"
		if run.CaseParallelism > 0 {
			parallelism = fmt.Sprintf("%d", run.CaseParallelism)
		}
		fmt.Fprintf(&b, "| %s | %d | %s | %s | %d | %s |\n", filepath.Base(filepath.Clean(run.Dir)),
			run.Cases, seconds(float64(run.WallMS)), parallelism, run.CostRecorded, known)
	}
	b.WriteString("\n")
	if multi {
		b.WriteString("Cells with two numbers are mean / max over the runs that contain the case.\n\n")
	}
	b.WriteString("Wall is elapsed time on the case (includes waiting on the shared endpoint); " +
		"model is the sum of model-call durations; gen tok is the whole case's generated tokens; " +
		"max ctx is the longest single step prompt. `—` means the artifacts carry no value.\n\n")
	byID := map[string]MergedCost{}
	for _, item := range report.Cases {
		byID[item.ID] = item
	}
	for _, ranking := range costRankings {
		ids := report.Rankings[ranking.key]
		fmt.Fprintf(&b, "## Top %d by %s\n\n", report.Top, strings.ToLower(ranking.title[:1])+ranking.title[1:])
		if len(ids) == 0 {
			b.WriteString("No case carries this metric.\n\n")
			continue
		}
		b.WriteString("| # | case | pass | steps | wall s | model s | tool s | gen tok | max ctx | finish s | limits | scenario / axis |\n")
		b.WriteString("|---:|---|:---:|---:|---:|---:|---:|---:|---:|---:|---|---|\n")
		for rank, id := range ids {
			item := byID[id]
			fmt.Fprintf(&b, "| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n",
				rank+1, item.ID, passCell(item), statCell(item.Steps, 1, false),
				statCell(item.WallMS, 1000, true), statCell(item.ModelMS, 1000, true),
				statCell(item.ToolMS, 1000, true), statCell(item.CompletionTokens, 1, false),
				statCell(item.MaxPromptTokens, 1, false), statCell(item.EndOffsetMS, 1000, true),
				limitsCell(item), axisCell(item))
		}
		b.WriteString("\n")
	}
	for _, key := range []string{"scenario", "probe_axis"} {
		groups := report.Groups[key]
		if len(groups) == 0 || (len(groups) == 1 && groups[0].Key == "-") {
			continue
		}
		fmt.Fprintf(&b, "## By %s\n\n", key)
		b.WriteString("| " + key + " | cases | pass | wall s mean / max | wall share | model s | steps | gen tok mean / max | max ctx mean / max | max_tokens | max_steps | timeout |\n")
		b.WriteString("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
		for _, group := range groups {
			fmt.Fprintf(&b, "| %s | %d | %.0f%% | %s | %.1f%% | %s | %s | %s | %s | %d | %d | %d |\n",
				group.Key, group.Cases, group.PassRate*100, statPair(group.WallMS, 1000, true),
				group.WallShare*100, meanCell(group.ModelMS, 1000, "%.1f"),
				meanCell(group.Steps, 1, "%.1f"),
				statPair(group.CompletionTokens, 1, false), statPair(group.MaxPromptTokens, 1, false),
				group.MaxTokensHits, group.MaxStepsHits, group.TimeoutHits)
		}
		b.WriteString("\n")
	}
	return b.String()
}

func passCell(item MergedCost) string {
	if item.Runs == 1 {
		switch {
		case item.Invalid > 0:
			return "inv"
		case item.Passes == 1:
			return "✓"
		default:
			return "✗"
		}
	}
	return fmt.Sprintf("%d/%d", item.Passes, item.Runs)
}

func limitsCell(item MergedCost) string {
	var parts []string
	add := func(name string, hits int) {
		if hits == 0 {
			return
		}
		if item.Runs == 1 {
			parts = append(parts, name)
		} else {
			parts = append(parts, fmt.Sprintf("%s %d/%d", name, hits, item.Runs))
		}
	}
	add("max_tokens", item.MaxTokensHits)
	add("max_steps", item.MaxStepsHits)
	add("timeout", item.TimeoutHits)
	return strings.Join(parts, ", ")
}

func axisCell(item MergedCost) string {
	switch {
	case item.Scenario != "" && item.ProbeAxis != "":
		return item.Scenario + " / " + item.ProbeAxis
	case item.ProbeAxis != "":
		return item.ProbeAxis
	default:
		return item.Scenario
	}
}

// statCell renders mean (and max when there is more than one value).
func statCell(stat Stat, scale float64, decimal bool) string {
	if stat.N == 0 {
		return "—"
	}
	format := func(value float64) string {
		if decimal {
			return fmt.Sprintf("%.1f", value/scale)
		}
		return fmt.Sprintf("%.0f", value/scale)
	}
	mean, maximum := format(stat.Mean), format(stat.Max)
	if stat.N == 1 || mean == maximum {
		return mean
	}
	return mean + " / " + maximum
}

func meanCell(stat Stat, scale float64, format string) string {
	if stat.N == 0 {
		return "—"
	}
	return fmt.Sprintf(format, stat.Mean/scale)
}

func statPair(stat Stat, scale float64, decimal bool) string {
	if stat.N == 0 {
		return "—"
	}
	cell := statCell(stat, scale, decimal)
	if !strings.Contains(cell, "/") {
		cell += " / " + cell
	}
	return cell
}

func seconds(ms float64) string {
	switch {
	case ms <= 0:
		return "—"
	case ms < 10_000:
		return fmt.Sprintf("%.1fs", ms/1000)
	default:
		return fmt.Sprintf("%.0fs", ms/1000)
	}
}

func tagString(tags map[string]any, key string, fallback string) string {
	if value, ok := tags[key].(string); ok && value != "" {
		return value
	}
	return fallback
}

func joinSortedKeys(set map[string]bool) string {
	names := make([]string, 0, len(set))
	for name := range set {
		if name != "" {
			names = append(names, name)
		}
	}
	sort.Strings(names)
	return strings.Join(names, "+")
}

func firstNonEmptyString(values ...string) string {
	for _, value := range values {
		if value != "" {
			return value
		}
	}
	return ""
}

func readJSONInto(path string, target any) error {
	file, err := os.Open(path)
	if err != nil {
		if errors.Is(err, os.ErrNotExist) {
			return fmt.Errorf("missing required file: %s", path)
		}
		return err
	}
	defer file.Close()
	if err := json.NewDecoder(bufio.NewReaderSize(file, 1<<20)).Decode(target); err != nil {
		return fmt.Errorf("invalid JSON in %s: %v", path, err)
	}
	return nil
}
