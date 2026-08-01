package eval

import (
	"bufio"
	"context"
	"encoding/json"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestRunScoresAndWritesTraceArtifacts(t *testing.T) {
	scripts := [][]continuation.Result{
		{
			generated("respond"),
			generated("4"),
		},
		{
			generated("inspect"),
			generated(`<tool_call>{"name":"read_file","arguments":{"path":"facts.txt"}}</tool_call>`),
			generated("The code is TRACE-2048."),
		},
	}
	factoryCalls := 0
	factory := func(context.Context) (continuation.Generator, io.Closer, error) {
		script := scripts[factoryCalls]
		factoryCalls++
		index := 0
		generator := continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			result := script[index]
			index++
			return result, nil
		})
		return generator, noopTestCloser{}, nil
	}
	now := time.Date(2026, 7, 30, 8, 0, 0, 0, time.UTC)
	report, err := Run(context.Background(), Config{
		Cases: []Case{
			{
				ID:          "respond",
				Description: "Respond without a tool.",
				Turns: []Turn{{
					Prompt: "What is two plus two?",
					Expect: Expectation{
						Route:          agent.RouteRespond,
						Tools:          []string{},
						OutputContains: []string{"4"},
					},
				}},
			},
			{
				ID:          "inspect",
				Description: "Read exact workspace evidence.",
				Files:       map[string]string{"facts.txt": "TRACE-2048\n"},
				Turns: []Turn{{
					Prompt: "Read facts.txt and report its code.",
					Expect: Expectation{
						Route: agent.RouteInspect,
						Tools: []string{"read_file"},
						Calls: []ExpectedCall{{
							Name:      "read_file",
							Arguments: map[string]any{"path": "facts.txt"},
						}},
						OutputContains: []string{"TRACE-2048"},
					},
				}},
			},
		},
		Model: ModelMetadata{
			Identifier: "scripted",
			Backend:    "test",
			Provider:   "test",
			Completion: "test",
		},
		Runner: agent.Options{
			MaxSteps:                3,
			ProtocolRetries:         1,
			DecisionMaxOutputTokens: 32,
			Protocol:                agent.G1IProtocol{},
			Renderer:                agent.RWKVChatRenderer{},
			Router:                  agent.G1IRouteProtocol{},
			RouteRenderer:           agent.RWKVChatRenderer{},
			RouteRetries:            1,
			RouteMaxOutputTokens:    8,
			Generation: continuation.Request{
				Model:           "scripted",
				MaxOutputTokens: 64,
				Sampling: continuation.Sampling{
					Temperature:  1,
					TopK:         1,
					TopP:         1,
					PenaltyDecay: 1,
				},
			},
		},
		GeneratorFactory: func(
			ctx context.Context,
		) (continuation.Generator, io.Closer, error) {
			generator, closer, factoryErr := factory(ctx)
			return generator, closer, factoryErr
		},
		CaseTimeout: time.Second,
		Now: func() time.Time {
			now = now.Add(time.Millisecond)
			return now
		},
		TempDir: t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if factoryCalls != 2 {
		t.Fatalf("generator factories = %d, want 2", factoryCalls)
	}
	assertScore(t, "task success", report.Summary.Metrics.TaskSuccess, 2, 2)
	assertScore(t, "answer accuracy", report.Summary.Metrics.AnswerAccuracy, 2, 2)
	assertScore(t, "route accuracy", report.Summary.Metrics.RouteAccuracy, 2, 2)
	assertScore(t, "protocol validity", report.Summary.Metrics.ProtocolValidity, 3, 3)
	assertScore(t, "tool selection", report.Summary.Metrics.ToolSelection, 2, 2)
	assertScore(t, "argument accuracy", report.Summary.Metrics.ArgumentAccuracy, 1, 1)
	assertScore(t, "no-call accuracy", report.Summary.Metrics.NoCallAccuracy, 1, 1)
	if report.Summary.Metrics.ModelCalls != 5 ||
		report.Summary.Metrics.ToolCalls != 1 ||
		report.Summary.Metrics.ToolExecutions != 1 ||
		report.Summary.Metrics.ToolErrors != 0 ||
		report.Summary.Metrics.RejectedCalls != 0 ||
		report.Summary.Metrics.DuplicateCalls != 0 ||
		report.Summary.Metrics.RecoveryBlocks != 0 ||
		report.Summary.Metrics.ForcedAnswers != 0 ||
		report.Summary.Metrics.PromptTokens != 10 ||
		report.Summary.Metrics.CompletionTokens != 5 {
		t.Fatalf("metrics = %+v", report.Summary.Metrics)
	}

	var modelCalls []ModelCallTrace
	for _, record := range report.Trace {
		if record.ModelCall != nil {
			modelCalls = append(modelCalls, *record.ModelCall)
		}
	}
	if len(modelCalls) != 5 {
		t.Fatalf("model call traces = %d", len(modelCalls))
	}
	stages := []string{"route", "decision", "route", "decision", "decision"}
	for index, call := range modelCalls {
		if call.Stage != stages[index] ||
			strings.TrimSpace(call.Request.Prompt) == "" ||
			call.Response.FinishReason != continuation.FinishStop ||
			call.Response.Usage.PromptTokens != 2 ||
			call.Response.Usage.CompletionTokens != 1 {
			t.Fatalf("model call %d = %+v", index, call)
		}
	}
	if !strings.Contains(modelCalls[0].Request.Prompt, "What is two plus two?") ||
		modelCalls[1].Response.Text != "4" ||
		!strings.Contains(modelCalls[4].Request.Prompt, "TRACE-2048") {
		t.Fatalf("raw model traces were not preserved: %+v", modelCalls)
	}

	output := filepath.Join(t.TempDir(), "artifacts")
	paths, err := WriteArtifacts(output, report)
	if err != nil {
		t.Fatal(err)
	}
	var manifest RunManifest
	decodeJSONFile(t, paths.Run, &manifest)
	var summary Summary
	decodeJSONFile(t, paths.Summary, &summary)
	if manifest.RunID != report.Manifest.RunID ||
		len(manifest.Cases) != 2 ||
		manifest.Cases[1].Files["facts.txt"] != "TRACE-2048\n" ||
		summary.Metrics.TaskSuccess.Correct != 2 {
		t.Fatalf("decoded manifest=%+v summary=%+v", manifest, summary)
	}
	handle, err := os.Open(paths.Trace)
	if err != nil {
		t.Fatal(err)
	}
	defer handle.Close()
	scanner := bufio.NewScanner(handle)
	traceRecords := 0
	for scanner.Scan() {
		var record TraceRecord
		if err := json.Unmarshal(scanner.Bytes(), &record); err != nil {
			t.Fatalf("decode trace line: %v", err)
		}
		traceRecords++
	}
	if err := scanner.Err(); err != nil {
		t.Fatal(err)
	}
	if traceRecords != len(report.Trace) {
		t.Fatalf("trace records = %d, want %d", traceRecords, len(report.Trace))
	}
	runData, err := os.ReadFile(paths.Trace)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(runData), `"Prompt"`) ||
		strings.Contains(string(runData), `"PromptTokens"`) ||
		!strings.Contains(string(runData), `"max_output_tokens"`) ||
		!strings.Contains(string(runData), `"prompt_tokens"`) {
		t.Fatalf("trace does not use the versioned JSON shape:\n%s", runData)
	}
	if _, err := WriteArtifacts(output, report); err == nil ||
		!strings.Contains(err.Error(), "already exists") {
		t.Fatalf("existing output error = %v", err)
	}
}

func TestBoundaryScoringMatchesRequiredCallsWithoutOrder(t *testing.T) {
	answer := "VALUE-42"
	result := agent.Result{
		Route:  agent.RouteInspect,
		Output: " VALUE-42\n",
		Steps: []agent.Step{
			{
				Tool:          "search_text",
				ToolArguments: json.RawMessage(`{"query":"needle","path":"docs"}`),
			},
			{
				Tool:          "read_file",
				ToolArguments: json.RawMessage(`{"path":"docs/result.txt","extra":true}`),
			},
		},
	}
	expect := Expectation{
		Route:          agent.RouteInspect,
		RequiredTools:  []string{"read_file", "search_text"},
		ForbiddenTools: []string{"list_files"},
		RequiredCalls: []ExpectedCall{
			{Name: "read_file", Arguments: map[string]any{"path": "docs/result.txt"}},
			{Name: "search_text", Arguments: map[string]any{"query": "needle"}},
		},
		OutputEquals: &answer,
	}
	if failures := validateTurn(expect, result, nil); len(failures) != 0 {
		t.Fatalf("boundary validation failures = %v", failures)
	}
	testCase := Case{
		ID:          "boundary",
		Description: "Boundary metrics.",
		Turns:       []Turn{{Prompt: "Find it.", Expect: expect}},
	}
	summary := summarize(
		"run",
		[]Case{testCase},
		[]CaseResult{{
			ID:     testCase.ID,
			Passed: true,
			Turns:  []TurnResult{{Result: result, Passed: true}},
		}},
		nil,
	)
	assertScore(t, "answer accuracy", summary.Metrics.AnswerAccuracy, 1, 1)
	assertScore(t, "required tool completion", summary.Metrics.RequiredToolCompletion, 2, 2)
	assertScore(t, "forbidden tool avoidance", summary.Metrics.ForbiddenToolAvoidance, 1, 1)
	assertScore(t, "required call accuracy", summary.Metrics.RequiredCallAccuracy, 2, 2)
}

func TestBoundaryNumericToleranceRequiresPlainNumber(t *testing.T) {
	expected := 289.13
	tolerance := 1.5
	expect := Expectation{
		RequiredTools:  []string{"read_file"},
		ExpectedNumber: &expected,
		Tolerance:      &tolerance,
	}
	result := agent.Result{
		Output: "290.00",
		Steps:  []agent.Step{{Tool: "read_file"}},
	}
	if failures := validateTurn(expect, result, nil); len(failures) != 0 {
		t.Fatalf("numeric tolerance failures = %v", failures)
	}
	result.Output = "The answer is 290.00"
	failures := validateTurn(expect, result, nil)
	if len(failures) != 1 || !strings.Contains(failures[0], "not a plain number") {
		t.Fatalf("non-numeric output failures = %v", failures)
	}
}

func TestSummarizeRecoveryMetrics(t *testing.T) {
	t.Parallel()
	cases := []Case{{
		ID: "recovery",
		Turns: []Turn{{
			Prompt: "recover",
		}},
	}}
	results := []CaseResult{{
		ID:     "recovery",
		Passed: true,
		Turns: []TurnResult{{
			Passed: true,
			Result: agent.Result{
				ForcedAnswerReason: "step_budget_after_tool_attempt",
				Steps: []agent.Step{
					{
						Tool:         "read_file",
						ToolExecuted: true,
						ToolError:    "missing",
					},
					{
						Tool:         "read_file",
						ToolRejected: "duplicate_tool_call",
						ToolError:    "duplicate",
					},
					{
						Tool:         "read_file",
						ToolRejected: "consecutive_tool_failures",
						ToolError:    "blocked",
					},
				},
			},
		}},
	}}
	metrics := summarize("run", cases, results, nil).Metrics
	if metrics.ToolCalls != 3 ||
		metrics.ToolExecutions != 1 ||
		metrics.ToolErrors != 3 ||
		metrics.RejectedCalls != 2 ||
		metrics.DuplicateCalls != 1 ||
		metrics.RecoveryBlocks != 1 ||
		metrics.ForcedAnswers != 1 {
		t.Fatalf("recovery metrics = %+v", metrics)
	}
}

func generated(text string) continuation.Result {
	return continuation.Result{
		Text:         text,
		FinishReason: continuation.FinishStop,
		Usage: continuation.Usage{
			PromptTokens:     2,
			CompletionTokens: 1,
		},
	}
}

func assertScore(t *testing.T, name string, score Score, correct int, total int) {
	t.Helper()
	if score.Correct != correct || score.Total != total || score.Rate != 1 {
		t.Fatalf("%s = %+v", name, score)
	}
}

func decodeJSONFile(t *testing.T, path string, target any) {
	t.Helper()
	handle, err := os.Open(path)
	if err != nil {
		t.Fatal(err)
	}
	defer handle.Close()
	if err := json.NewDecoder(handle).Decode(target); err != nil {
		t.Fatalf("decode %s: %v", path, err)
	}
}

type noopTestCloser struct{}

func (noopTestCloser) Close() error { return nil }
