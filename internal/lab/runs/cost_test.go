package runs

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeCostRun(t *testing.T, run map[string]any, summary map[string]any, trace []map[string]any) string {
	t.Helper()
	dir := t.TempDir()
	for name, value := range map[string]any{"run.json": run, "summary.json": summary} {
		data, err := json.Marshal(value)
		if err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(dir, name), data, 0o644); err != nil {
			t.Fatal(err)
		}
	}
	if trace != nil {
		var lines []string
		for _, record := range trace {
			data, err := json.Marshal(record)
			if err != nil {
				t.Fatal(err)
			}
			lines = append(lines, string(data))
		}
		if err := os.WriteFile(filepath.Join(dir, "trace.jsonl"), []byte(strings.Join(lines, "\n")+"\n"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return dir
}

const costRunStart = "2026-10-14T00:00:00Z"

// costRunStartMS is costRunStart in Unix milliseconds.
const costRunStartMS = int64(1791936000000)

func recordedCase(id string, passed bool, axis string, wall, model int64, completion, maxPrompt int, limits ...string) map[string]any {
	cost := map[string]any{
		"started_at_ms": costRunStartMS + 1000, "ended_at_ms": costRunStartMS + 1000 + wall,
		"wall_ms": wall, "model_ms": model, "tool_ms": 10, "steps": 4, "max_steps": 16,
		"prompt_tokens": maxPrompt * 2, "completion_tokens": completion, "max_prompt_tokens": maxPrompt,
		"token_source": "local_vocab+server_stream",
	}
	for _, limit := range limits {
		cost["hit_"+limit] = true
	}
	return map[string]any{
		"id": id, "passed": passed, "category": "bashprobe",
		"tags":  map[string]any{"scenario": "bashprobe", "probe_axis": axis},
		"turns": []any{map[string]any{"cost": cost, "result": map[string]any{"steps": []any{}}}},
		"cost":  cost,
	}
}

func TestCostReportRanksRecordedCasesAndMergesRuns(t *testing.T) {
	run := map[string]any{"run_id": "r", "started_at": costRunStart,
		"harness": map[string]any{"max_steps": 16, "case_parallelism": 48}}
	first := writeCostRun(t, run, map[string]any{
		"run_id":  "k0",
		"metrics": map[string]any{"wall_time_millis": 600000},
		"cases": []any{
			recordedCase("slow", false, "edit", 500000, 480000, 30000, 9000, "max_tokens", "max_steps"),
			recordedCase("chatty", true, "aggregate", 60000, 50000, 50000, 4000),
			recordedCase("quick", true, "aggregate", 5000, 4000, 300, 2000),
		},
	}, nil)
	second := writeCostRun(t, run, map[string]any{
		"run_id":  "k1",
		"metrics": map[string]any{"wall_time_millis": 300000},
		"cases": []any{
			recordedCase("slow", true, "edit", 100000, 90000, 10000, 7000),
			recordedCase("chatty", true, "aggregate", 40000, 30000, 40000, 3000),
			recordedCase("quick", true, "aggregate", 7000, 6000, 500, 2500),
		},
	}, nil)
	report, err := BuildCostReport(CostArgs{Runs: []string{first, second}, Top: 2})
	if err != nil {
		t.Fatal(err)
	}
	if got := report.Rankings["wall_ms"]; strings.Join(got, ",") != "slow,chatty" {
		t.Fatalf("wall ranking = %v", got)
	}
	if got := report.Rankings["completion_tokens"]; strings.Join(got, ",") != "chatty,slow" {
		t.Fatalf("token ranking = %v", got)
	}
	if got := report.Rankings["max_prompt_tokens"]; strings.Join(got, ",") != "slow,chatty" {
		t.Fatalf("context ranking = %v", got)
	}
	slow := report.Cases[0]
	if slow.ID != "slow" || slow.Runs != 2 || slow.Passes != 1 {
		t.Fatalf("slow = %+v", slow)
	}
	if slow.WallMS.Mean != 300000 || slow.WallMS.Max != 500000 ||
		slow.CompletionTokens.Mean != 20000 || slow.CompletionTokens.Max != 30000 ||
		slow.MaxPromptTokens.Max != 9000 || slow.MaxTokensHits != 1 || slow.MaxStepsHits != 1 {
		t.Fatalf("slow stats = %+v", slow)
	}
	if slow.EndOffsetMS.Max != 501000 {
		t.Fatalf("slow end offset = %+v", slow.EndOffsetMS)
	}
	axes := report.Groups["probe_axis"]
	if len(axes) != 2 || axes[0].Key != "edit" || axes[0].MaxTokensHits != 1 || axes[1].Cases != 2 {
		t.Fatalf("axis groups = %+v", axes)
	}
	if axes[1].PassRate != 1 || axes[0].PassRate != 0.5 {
		t.Fatalf("axis pass rates = %+v", axes)
	}

	markdown := RenderCostMarkdown(report)
	for _, want := range []string{
		"## Top 2 by wall time",
		"| 1 | slow | 1/2 | 4 | 300.0 / 500.0 | 285.0 / 480.0 |",
		"max_tokens 1/2, max_steps 1/2",
		"bashprobe / edit",
		"## By probe_axis",
	} {
		if !strings.Contains(markdown, want) {
			t.Fatalf("markdown lacks %q:\n%s", want, markdown)
		}
	}
}

// A run written before cost was recorded is recomputed from its steps; its
// zero usage reads as missing, and --recount fills it from the trace.
func TestCostReportRecomputesLegacyRunsAndRecountsFromTrace(t *testing.T) {
	step := func(start, duration, toolStart, toolDuration int64, finish string) map[string]any {
		return map[string]any{
			"model_started_at_ms": start, "model_duration_ms": duration,
			"tool_started_at_ms": toolStart, "tool_duration_ms": toolDuration,
			"finish_reason": finish,
			"usage":         map[string]any{"prompt_tokens": 0, "completion_tokens": 0},
		}
	}
	base := costRunStartMS
	dir := writeCostRun(t,
		map[string]any{"run_id": "old", "started_at": costRunStart,
			"harness":    map[string]any{"max_steps": 2},
			"case_wires": []any{map[string]any{"id": "loop", "max_steps": 2}}},
		map[string]any{"run_id": "old", "cases": []any{
			map[string]any{"id": "loop", "passed": false, "category": "workbank", "turns": []any{
				map[string]any{
					"runner_error": "agent reached the step limit",
					"result": map[string]any{"started_at_ms": base + 100, "steps": []any{
						step(base+100, 1000, base+1100, 50, "stop"),
						step(base+1200, 2000, 0, 0, "length"),
					}},
				},
			}},
			map[string]any{"id": "timeout", "passed": false, "invalid": true, "turns": []any{
				map[string]any{
					"runner_error": "context deadline exceeded",
					"result": map[string]any{"started_at_ms": base + 50, "steps": []any{
						step(base+50, 500, 0, 0, "stop"),
					}},
				},
			}},
		}},
		[]map[string]any{
			{"case_id": "loop", "kind": "model_call", "timestamp": costRunStart,
				"model_call": map[string]any{"request": map[string]any{"prompt": "aaaa"}, "response": map[string]any{"text": "bb"}}},
			{"case_id": "loop", "kind": "model_call", "timestamp": costRunStart,
				"model_call": map[string]any{"request": map[string]any{"prompt": "aaaaaaaa"}, "response": map[string]any{"text": "ccc"}}},
		},
	)

	report, err := BuildCostReport(CostArgs{Runs: []string{dir}})
	if err != nil {
		t.Fatal(err)
	}
	loop := report.PerRun[0]
	if loop.TimeSource != "steps" || loop.WallMS != 3100 || loop.ModelMS != 3000 || loop.ToolMS != 50 {
		t.Fatalf("legacy loop time = %+v", loop)
	}
	if !loop.HitMaxSteps || !loop.HitMaxTokens || loop.HitTimeout || loop.TokensKnown() {
		t.Fatalf("legacy loop flags = %+v", loop)
	}
	if timeout := report.PerRun[1]; !timeout.HitTimeout || !timeout.Invalid {
		t.Fatalf("legacy timeout = %+v", timeout)
	}
	if len(report.Rankings["completion_tokens"]) != 0 {
		t.Fatalf("tokens ranked without counts: %v", report.Rankings["completion_tokens"])
	}
	if markdown := RenderCostMarkdown(report); !strings.Contains(markdown, "No case carries this metric.") {
		t.Fatalf("missing tokens not shown as missing:\n%s", markdown)
	}

	recounted, err := BuildCostReport(CostArgs{
		Runs: []string{dir}, Recount: true,
		counter: func(text string) int { return len(text) },
	})
	if err != nil {
		t.Fatal(err)
	}
	loop = recounted.PerRun[0]
	if loop.TokenSource != "local_vocab_trace" || loop.PromptTokens != 12 ||
		loop.CompletionTokens != 5 || loop.MaxPromptTokens != 8 {
		t.Fatalf("recounted loop = %+v", loop)
	}
	if recounted.Runs[0].Recounted != 1 || recounted.PerRun[1].TokensKnown() {
		t.Fatalf("recount = %+v / %+v", recounted.Runs[0], recounted.PerRun[1])
	}
}

func TestCostCommandEmitsJSON(t *testing.T) {
	run := map[string]any{"run_id": "r", "started_at": costRunStart}
	dir := writeCostRun(t, run, map[string]any{"cases": []any{
		recordedCase("only", true, "edit", 1000, 900, 10, 100),
	}}, nil)
	report, err := BuildCostReport(CostArgs{Runs: []string{dir}})
	if err != nil {
		t.Fatal(err)
	}
	data, err := json.Marshal(report)
	if err != nil {
		t.Fatal(err)
	}
	var decoded map[string]any
	if err := json.Unmarshal(data, &decoded); err != nil {
		t.Fatal(err)
	}
	for _, key := range []string{"runs", "rankings", "cases", "groups", "per_run"} {
		if _, ok := decoded[key]; !ok {
			t.Fatalf("JSON report lacks %q: %s", key, data)
		}
	}
}
