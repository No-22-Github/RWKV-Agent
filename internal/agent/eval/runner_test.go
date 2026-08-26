package eval

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestRunExecutesCasesConcurrentlyAndKeepsReportOrder(t *testing.T) {
	t.Parallel()
	answer := "ok"
	cases := make([]Case, 6)
	for index := range cases {
		cases[index] = Case{
			ID:          fmt.Sprintf("parallel-%d", index),
			Description: "parallel case",
			Turns: []Turn{{
				Prompt: "answer ok",
				Expect: Expectation{Route: agent.RouteInspect, Tools: []string{}, OutputEquals: &answer},
			}},
		}
	}
	var active atomic.Int64
	var maximum atomic.Int64
	report, err := Run(context.Background(), Config{
		Cases:           cases,
		Suite:           "custom",
		CaseParallelism: 6,
		Runner: agent.Options{
			MaxSteps:   2,
			Generation: continuation.Request{MaxOutputTokens: 32},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return continuation.GenerateFunc(func(context.Context, continuation.Request, continuation.EventSink) (continuation.Result, error) {
				current := active.Add(1)
				defer active.Add(-1)
				for {
					observed := maximum.Load()
					if current <= observed || maximum.CompareAndSwap(observed, current) {
						break
					}
				}
				time.Sleep(20 * time.Millisecond)
				return continuation.Result{Text: answer, FinishReason: continuation.FinishStop}, nil
			}), nil, nil
		},
		TempDir: t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if maximum.Load() < 2 {
		t.Fatalf("maximum active cases = %d, want concurrent execution", maximum.Load())
	}
	if report.Manifest.Harness.CaseParallelism != 6 {
		t.Fatalf("manifest case parallelism = %d", report.Manifest.Harness.CaseParallelism)
	}
	for index, result := range report.Summary.Cases {
		if result.ID != cases[index].ID || !result.Passed {
			t.Fatalf("result %d = %+v, want ordered passing case %q", index, result, cases[index].ID)
		}
	}
	for index, record := range report.Trace {
		if record.Sequence != index+1 {
			t.Fatalf("trace sequence %d = %d", index, record.Sequence)
		}
	}
}

type nativeEvalGenerator struct {
	requests []toolchat.Request
}

func (*nativeEvalGenerator) Continue(
	context.Context,
	continuation.Request,
	continuation.EventSink,
) (continuation.Result, error) {
	return continuation.Result{}, errors.New("native eval unexpectedly used text continuation")
}

func (*nativeEvalGenerator) NativeToolCalling() bool {
	return true
}

func (g *nativeEvalGenerator) Complete(
	_ context.Context,
	request toolchat.Request,
	_ continuation.EventSink,
) (toolchat.Result, error) {
	g.requests = append(g.requests, request)
	result := toolchat.Result{
		FinishReason: continuation.FinishStop,
		Usage: continuation.Usage{
			PromptTokens:     3,
			CompletionTokens: 1,
		},
	}
	switch len(g.requests) {
	case 1:
		result.Content = "<route>inspect</route>"
	case 2:
		result.FinishReason = continuation.FinishToolCalls
		result.Content = "I will read the requested file."
		result.ToolCalls = []toolchat.ToolCall{{
			ID:        "call-native",
			Name:      "read_file",
			Arguments: `{"path":"facts.txt"}`,
		}}
	case 3:
		result.Content = "TRACE-2048"
	default:
		return toolchat.Result{}, errors.New("unexpected native completion")
	}
	return result, nil
}

var _ continuation.Generator = (*nativeEvalGenerator)(nil)
var _ toolchat.Completer = (*nativeEvalGenerator)(nil)

func TestRunPreservesNativeToolCompleterThroughRecording(t *testing.T) {
	generator := &nativeEvalGenerator{}
	report, err := Run(context.Background(), Config{
		Cases: []Case{{
			ID:          "native",
			Description: "Use a native function call through the eval recorder.",
			Files:       map[string]string{"facts.txt": "TRACE-2048\n"},
			Turns: []Turn{{
				Prompt: "Read facts.txt and return only its value.",
				Expect: Expectation{
					Route:        agent.RouteInspect,
					Tools:        []string{"read_file"},
					OutputEquals: stringPointerForTest("TRACE-2048"),
				},
			}},
		}},
		Model: ModelMetadata{Identifier: "native", Completion: "chat-completions"},
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
				Model:           "native",
				MaxOutputTokens: 64,
				Sampling: continuation.Sampling{
					Temperature:  1,
					TopK:         1,
					TopP:         1,
					PenaltyDecay: 1,
				},
			},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return generator, nil, nil
		},
		CaseTimeout: time.Second,
		TempDir:     t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if report.Summary.Metrics.TaskSuccess.Correct != 1 || len(generator.requests) != 3 {
		t.Fatalf("native eval did not complete: metrics=%+v requests=%d", report.Summary.Metrics, len(generator.requests))
	}
	structuredTrace := false
	for _, record := range report.Trace {
		if record.ModelCall != nil && strings.Contains(record.ModelCall.Request.Prompt, `"tools"`) {
			structuredTrace = true
			break
		}
	}
	if !structuredTrace {
		t.Fatalf("native trace did not preserve structured request: %+v", report.Trace)
	}
}

func stringPointerForTest(value string) *string {
	return &value
}

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
			Protocol:                agent.G1IProtocol{FewShot: true},
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
	if !report.Manifest.Harness.FewShot {
		t.Fatalf("few-shot profile was not recorded: %+v", report.Manifest.Harness)
	}
	if report.Manifest.SchemaVersion != RunSchemaVersion ||
		report.Manifest.Harness.ThinkingMode != string(inference.ThinkingOff) ||
		report.Manifest.Harness.RouteThinkingMode != string(inference.ThinkingOff) {
		t.Fatalf("thinking modes were not recorded independently: %+v", report.Manifest.Harness)
	}
	assertScore(t, "task success", report.Summary.Metrics.TaskSuccess, 2, 2)
	assertScore(t, "answer accuracy", report.Summary.Metrics.AnswerAccuracy, 2, 2)
	assertScore(t, "answer contract repaired", report.Summary.Metrics.AnswerContractRepaired, 0, 2)
	assertScore(t, "route accuracy", report.Summary.Metrics.RouteAccuracy, 2, 2)
	assertScore(t, "protocol validity", report.Summary.Metrics.ProtocolValidity, 3, 3)
	assertScore(t, "stage contract validity", report.Summary.Metrics.StageContractValidity, 3, 3)
	assertScore(t, "tool selection", report.Summary.Metrics.ToolSelection, 2, 2)
	assertScore(t, "argument accuracy", report.Summary.Metrics.ArgumentAccuracy, 1, 1)
	assertScore(t, "no-call accuracy", report.Summary.Metrics.NoCallAccuracy, 1, 1)
	assertScore(t, "active no-call", report.Summary.Metrics.ActiveNoCall, 1, 1)
	assertScore(t, "route protocol validity", report.Summary.Metrics.RouteProtocolValidity, 2, 2)
	assertScore(t, "decision protocol validity", report.Summary.Metrics.DecisionProtocolValidity, 3, 3)
	if report.Summary.Cases[0].Turns[0].Outcome != OutcomeExplicitRespond ||
		report.Summary.Cases[1].Turns[0].Outcome != OutcomeCalledTool ||
		report.Summary.Metrics.Outcomes[OutcomeExplicitRespond] != 1 ||
		report.Summary.Metrics.Outcomes[OutcomeCalledTool] != 1 {
		t.Fatalf("outcomes = %+v", report.Summary.Metrics.Outcomes)
	}
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

func TestRunManifestSeparatesDecisionAndRouteThinkingModes(t *testing.T) {
	t.Parallel()
	manifest := runManifest(Config{
		Cases: []Case{{ID: "one"}},
		Runner: agent.Options{
			Renderer:      agent.RWKVChatRenderer{ThinkingMode: inference.ThinkingFull},
			Router:        agent.G1IRouteProtocol{},
			RouteRenderer: agent.RWKVChatRenderer{ThinkingMode: inference.ThinkingOff},
		},
	}, "run", time.Unix(0, 0).UTC())
	if manifest.SchemaVersion != RunSchemaVersion ||
		manifest.Harness.ScorerVersion != ScorerVersion ||
		manifest.Harness.OutcomeTaxonomyVersion != OutcomeTaxonomyVersion ||
		manifest.Harness.ThinkingMode != string(inference.ThinkingFull) ||
		manifest.Harness.RouteThinkingMode != string(inference.ThinkingOff) ||
		!manifest.Harness.RouteStage {
		t.Fatalf("manifest harness = %+v", manifest.Harness)
	}
	toolRouteManifest := runManifest(Config{
		Cases: []Case{{ID: "one"}},
		Runner: agent.Options{
			ToolRouter:    agent.G1IProgressiveToolRouteProtocol{},
			RouteRenderer: agent.RWKVChatRenderer{},
		},
	}, "tool-route", time.Unix(0, 0).UTC())
	if !toolRouteManifest.Harness.RouteStage ||
		toolRouteManifest.Harness.RouteProtocol != (agent.G1IProgressiveToolRouteProtocol{}).ID() ||
		toolRouteManifest.Harness.RouteThinkingMode != string(inference.ThinkingOff) {
		t.Fatalf("tool route manifest harness = %+v", toolRouteManifest.Harness)
	}
}

func TestEvalOutcomeTaxonomyExposesNoCallAndToolParseFailures(t *testing.T) {
	tests := []struct {
		name              string
		script            []continuation.Result
		router            agent.RouteProtocol
		expect            Expectation
		wantOutcome       TurnOutcome
		wantPassed        bool
		wantActiveNoCall  Score
		wantRouteValidity Score
		wantDecisionValid Score
		wantFailureClass  agent.ProtocolFailureClass
	}{
		{
			name:   "explicit respond",
			script: []continuation.Result{generated("respond"), generated("OK")},
			router: agent.G1IRouteProtocol{},
			expect: Expectation{
				Route:               agent.RouteRespond,
				Tools:               []string{},
				OutputEquals:        stringPointerForTest("OK"),
				RequireActiveNoCall: true,
				ForbidRouteFallback: true,
			},
			wantOutcome:       OutcomeExplicitRespond,
			wantPassed:        true,
			wantActiveNoCall:  Score{Correct: 1, Total: 1, Rate: 1},
			wantRouteValidity: Score{Correct: 1, Total: 1, Rate: 1},
			wantDecisionValid: Score{Correct: 1, Total: 1, Rate: 1},
		},
		{
			name:   "ordinary final",
			script: []continuation.Result{generated("OK")},
			expect: Expectation{
				Tools:               []string{},
				OutputEquals:        stringPointerForTest("OK"),
				RequireActiveNoCall: true,
			},
			wantOutcome:       OutcomeDirectFinal,
			wantPassed:        true,
			wantActiveNoCall:  Score{Correct: 1, Total: 1, Rate: 1},
			wantDecisionValid: Score{Correct: 1, Total: 1, Rate: 1},
		},
		{
			name:   "route garbage preserves legacy task success",
			script: []continuation.Result{generated("garbage"), generated("OK")},
			router: agent.G1IRouteProtocol{},
			expect: Expectation{
				Route:        agent.RouteRespond,
				Tools:        []string{},
				OutputEquals: stringPointerForTest("OK"),
			},
			wantOutcome:       OutcomeRouteFailedClosed,
			wantPassed:        true,
			wantActiveNoCall:  Score{Total: 1},
			wantRouteValidity: Score{Total: 1},
			wantDecisionValid: Score{Correct: 1, Total: 1, Rate: 1},
		},
		{
			name:              "bare tool JSON",
			script:            []continuation.Result{generated(`{"name":"read_file","arguments":{"path":"README.md"}}`)},
			expect:            Expectation{Tools: []string{}},
			wantOutcome:       OutcomeToolEnvelopeMissing,
			wantPassed:        false,
			wantActiveNoCall:  Score{Total: 1},
			wantDecisionValid: Score{Total: 1},
			wantFailureClass:  agent.ProtocolFailureToolEnvelopeMissing,
		},
		{
			name:              "damaged tool envelope",
			script:            []continuation.Result{generated(`<tool_call>{"name":"read_file","arguments":`)},
			expect:            Expectation{Tools: []string{}},
			wantOutcome:       OutcomeToolJSONDecodeFailed,
			wantPassed:        false,
			wantActiveNoCall:  Score{Total: 1},
			wantDecisionValid: Score{Total: 1},
			wantFailureClass:  agent.ProtocolFailureToolJSONDecode,
		},
		{
			name:              "invalid tool shape",
			script:            []continuation.Result{generated(`<tool_call>{"name":"","arguments":[]}</tool_call>`)},
			expect:            Expectation{Tools: []string{}},
			wantOutcome:       OutcomeToolShapeInvalid,
			wantPassed:        false,
			wantActiveNoCall:  Score{Total: 1},
			wantDecisionValid: Score{Total: 1},
			wantFailureClass:  agent.ProtocolFailureToolShapeInvalid,
		},
	}
	for _, testCase := range tests {
		t.Run(testCase.name, func(t *testing.T) {
			index := 0
			report, err := Run(context.Background(), Config{
				Cases: []Case{{
					ID:          "taxonomy",
					Description: "Exercise a fixed protocol outcome.",
					Turns:       []Turn{{Prompt: "respond", Expect: testCase.expect}},
				}},
				Runner: agent.Options{
					MaxSteps:      2,
					Protocol:      agent.G1IProtocol{},
					Renderer:      agent.RWKVChatRenderer{},
					Router:        testCase.router,
					RouteRenderer: agent.RWKVChatRenderer{},
					Generation:    continuation.Request{MaxOutputTokens: 64},
				},
				GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
					return continuation.GenerateFunc(func(context.Context, continuation.Request, continuation.EventSink) (continuation.Result, error) {
						if index >= len(testCase.script) {
							return continuation.Result{}, errors.New("unexpected generation")
						}
						result := testCase.script[index]
						index++
						return result, nil
					}), nil, nil
				},
				CaseTimeout: time.Second,
				TempDir:     t.TempDir(),
			})
			if err != nil {
				t.Fatal(err)
			}
			turn := report.Summary.Cases[0].Turns[0]
			if turn.Outcome != testCase.wantOutcome || turn.Passed != testCase.wantPassed {
				t.Fatalf("turn = %+v", turn)
			}
			if report.Summary.Metrics.ActiveNoCall != testCase.wantActiveNoCall ||
				report.Summary.Metrics.RouteProtocolValidity != testCase.wantRouteValidity ||
				report.Summary.Metrics.DecisionProtocolValidity != testCase.wantDecisionValid {
				t.Fatalf("protocol metrics = %+v", report.Summary.Metrics)
			}
			if report.Summary.Metrics.Outcomes[testCase.wantOutcome] != 1 {
				t.Fatalf("outcomes = %+v", report.Summary.Metrics.Outcomes)
			}
			if testCase.wantFailureClass != "" &&
				report.Summary.Metrics.ParseFailuresByClass[testCase.wantFailureClass] != 1 {
				t.Fatalf("parse failures = %+v", report.Summary.Metrics.ParseFailuresByClass)
			}
			if testCase.wantOutcome == OutcomeRouteFailedClosed {
				strict := testCase.expect
				strict.RequireActiveNoCall = true
				strict.ForbidRouteFallback = true
				failures := validateTurn(strict, turn.Result, nil)
				if len(failures) != 2 ||
					!strings.Contains(failures[0], "active no-call") ||
					!strings.Contains(failures[1], "route fallback") {
					t.Fatalf("strict no-call failures = %v", failures)
				}
			}
		})
	}
}

func TestEvalRepairedOutcomeKeepsOriginalFailureClass(t *testing.T) {
	script := []continuation.Result{
		generated(`<read_file path="README.md" />`),
		generated("OK"),
	}
	index := 0
	report, err := Run(context.Background(), Config{
		Cases: []Case{{
			ID:          "repaired",
			Description: "Record a repaired legacy tool call.",
			Files:       map[string]string{"README.md": "OK\n"},
			Turns: []Turn{{
				Prompt: "Read README.md.",
				Expect: Expectation{
					Tools:        []string{"read_file"},
					OutputEquals: stringPointerForTest("OK"),
				},
			}},
		}},
		Runner: agent.Options{
			MaxSteps:   2,
			Protocol:   agent.G1IProtocol{},
			Renderer:   agent.RWKVChatRenderer{},
			Generation: continuation.Request{MaxOutputTokens: 64},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			return continuation.GenerateFunc(func(context.Context, continuation.Request, continuation.EventSink) (continuation.Result, error) {
				result := script[index]
				index++
				return result, nil
			}), nil, nil
		},
		CaseTimeout: time.Second,
		TempDir:     t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	turn := report.Summary.Cases[0].Turns[0]
	if !turn.Passed || turn.Outcome != OutcomeProtocolRepaired {
		t.Fatalf("turn = %+v", turn)
	}
	if got := turn.Result.Steps[0].ProtocolFailure; got != agent.ProtocolFailureToolEnvelopeMissing {
		t.Fatalf("original failure class = %q", got)
	}
	if report.Summary.Metrics.ProtocolRepairs != 1 ||
		report.Summary.Metrics.ParseFailuresByClass[agent.ProtocolFailureToolEnvelopeMissing] != 1 {
		t.Fatalf("repair metrics = %+v", report.Summary.Metrics)
	}
}

func TestAssistantSuiteMockAcceptance(t *testing.T) {
	cases, err := AssistantCases()
	if err != nil {
		t.Fatal(err)
	}
	cases, err = SelectCases(cases, []string{
		"as_weather_transit_hours",
		"as_expense_fx_convert",
		"as_expense_fx_unavailable",
	})
	if err != nil {
		t.Fatal(err)
	}
	scripts := [][]continuation.Result{
		{
			generated("inspect"),
			generated(`<tool_call>{"name":"weather","arguments":{"city":"上海"}}</tool_call>`),
			generated(`<tool_call>{"name":"nearest_transit","arguments":{"kind":"subway"}}</tool_call>`),
			generated(`<tool_call>{"name":"transit_hours","arguments":{"station":"世纪大道站"}}</tool_call>`),
			generated("上海今天多云，27 摄氏度。最近的地铁站是世纪大道站，23:30 关门。"),
		},
		{
			generated("inspect"),
			generated(`<tool_call>{"name":"data_query","arguments":{"path":"notes","filter":{"week":"current"},"operation":"sum","field":"amount"}}</tool_call>`),
			generated(`<tool_call>{"name":"fx_convert","arguments":{"amount":150,"from":"CNY","to":"USD"}}</tool_call>`),
			generated("本周共花费 150 元人民币，约合 21 美元。"),
		},
		{
			generated("inspect"),
			generated(`<tool_call>{"name":"data_query","arguments":{"path":"notes","filter":{"week":"current"},"operation":"sum","field":"amount"}}</tool_call>`),
			generated(`<tool_call>{"name":"fx_convert","arguments":{"amount":150,"from":"CNY","to":"USD"}}</tool_call>`),
			generated("本周共花费 150 元人民币；汇率服务不可用，美元换算未完成。"),
		},
	}
	factoryCalls := 0
	report, err := Run(context.Background(), Config{
		Cases: cases,
		Suite: SuiteAssistant,
		Model: ModelMetadata{Identifier: "scripted", Backend: "test", Provider: "test", Completion: "test"},
		Runner: agent.Options{
			MaxSteps:      6,
			Protocol:      agent.G1IProtocol{},
			Renderer:      agent.RWKVChatRenderer{},
			Router:        agent.G1IRouteProtocol{},
			RouteRenderer: agent.RWKVChatRenderer{},
			Generation: continuation.Request{
				Model:           "scripted",
				MaxOutputTokens: 1024,
			},
		},
		GeneratorFactory: func(context.Context) (continuation.Generator, io.Closer, error) {
			script := scripts[factoryCalls]
			factoryCalls++
			index := 0
			return continuation.GenerateFunc(func(
				context.Context,
				continuation.Request,
				continuation.EventSink,
			) (continuation.Result, error) {
				result := script[index]
				index++
				return result, nil
			}), noopTestCloser{}, nil
		},
		CaseTimeout: time.Second,
		TempDir:     t.TempDir(),
	})
	if err != nil {
		t.Fatal(err)
	}
	if factoryCalls != 3 {
		t.Fatalf("generator factories = %d, want 3", factoryCalls)
	}
	assertScore(t, "assistant task success", report.Summary.Metrics.TaskSuccess, 3, 3)
	assertScore(t, "assistant answer accuracy", report.Summary.Metrics.AnswerAccuracy, 3, 3)
	assertScore(t, "assistant explicit abstention", report.Summary.Metrics.ExplicitAbstention, 1, 1)
	assertScore(t, "assistant contract repair", report.Summary.Metrics.AnswerContractRepaired, 0, 3)
}

func TestValidateTurnPlanExpectation(t *testing.T) {
	expect := Expectation{Plan: &PlanExpectation{
		SubtaskCount: 3,
		Waves:        [][]string{{"weather", "nearest_transit"}, {"transit_hours"}},
		References: []Reference{{
			Subtask:  3,
			Argument: "station",
			Source:   "$2.name",
		}},
	}}
	result := agent.Result{Plan: &agent.PlanTrace{
		Subtasks: []agent.PlanSubtaskTrace{
			{ID: 1, Tool: "weather", Arguments: json.RawMessage(`{"city":"上海"}`)},
			{ID: 2, Tool: "nearest_transit", Arguments: json.RawMessage(`{"kind":"subway"}`)},
			{ID: 3, Tool: "transit_hours", Arguments: json.RawMessage(`{"station":"$2.name"}`)},
		},
		Waves: [][]int{{2, 1}, {3}},
	}}
	if failures := validateTurn(expect, result, nil); len(failures) != 0 {
		t.Fatalf("valid plan failures = %v", failures)
	}
	result.Plan.Subtasks[2].Arguments = json.RawMessage(`{"station":"世纪大道站"}`)
	if failures := validateTurn(expect, result, nil); len(failures) != 1 || !strings.Contains(failures[0], "does not use reference") {
		t.Fatalf("literal dependency failures = %v", failures)
	}
}

func TestValidateTurnExplicitAbstention(t *testing.T) {
	expect := Expectation{MustStateUnverified: []string{"美元换算未完成"}}
	if failures := validateTurn(expect, agent.Result{Output: "人民币总额 150 元；美元换算未完成。"}, nil); len(failures) != 0 {
		t.Fatalf("explicit abstention failures = %v", failures)
	}
	if failures := validateTurn(expect, agent.Result{Output: "人民币总额 150 元，约 21 美元。"}, nil); len(failures) != 1 {
		t.Fatalf("unsupported conversion failures = %v", failures)
	}
}

func TestAnswerContainsAnyAlternative(t *testing.T) {
	expect := Expectation{
		OutputContains:    []string{"多云"},
		OutputContainsAny: []string{"2026-08-04", "2026年8月4日"},
	}
	if failures := answerFailures(expect, "今天是2026年8月4日，天气多云。"); len(failures) != 0 {
		t.Fatalf("localized date failures = %v", failures)
	}
	if failures := answerFailures(expect, "今天是2026-08-04，天气多云。"); len(failures) != 0 {
		t.Fatalf("ISO date failures = %v", failures)
	}
	if failures := answerFailures(expect, "今天天气多云。"); len(failures) != 1 {
		t.Fatalf("missing date failures = %v", failures)
	}
	if !hasAnswerExpectation(Expectation{OutputContainsAny: []string{"2026-08-04"}}) {
		t.Fatal("output_contains_any alone must count as an answer expectation")
	}
}

func TestAnswerContractRepairKeepsOriginalAccuracySeparate(t *testing.T) {
	answer := "42"
	expect := Expectation{OutputEquals: &answer}
	result := agent.Result{
		Output:                 "I could not provide a reliable answer.",
		OriginalOutput:         "42",
		AnswerContractRepaired: true,
		AnswerViolations:       []string{"role_header"},
	}
	failures := validateTurn(expect, result, nil)
	if len(failures) != 1 || !strings.Contains(failures[0], "answer contract repaired") {
		t.Fatalf("repair validation failures = %v", failures)
	}
	testCase := Case{ID: "repair", Turns: []Turn{{Expect: expect}}}
	summary := summarize("run", []Case{testCase}, []CaseResult{{
		ID:     "repair",
		Passed: false,
		Turns:  []TurnResult{{Result: result, Passed: false}},
	}}, nil)
	assertScore(t, "answer accuracy", summary.Metrics.AnswerAccuracy, 1, 1)
	assertScore(t, "answer contract repaired", summary.Metrics.AnswerContractRepaired, 1, 1)
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

// TestBoundaryScoringAcceptsEquivalentDiscoveryPaths mirrors pb_search_read_submit
// and pb_find_read_submit, where both models reached the correct answer through a
// different discovery tool than the case names. Locating a value with search_text
// alone is not a worse trajectory than list_files plus read_file, so it must not
// be scored as a missing required tool.
func TestBoundaryScoringAcceptsEquivalentDiscoveryPaths(t *testing.T) {
	answer := "EMBER-91"
	result := agent.Result{
		Route:  agent.RouteInspect,
		Output: "EMBER-91",
		Steps: []agent.Step{
			{
				Tool:          "search_text",
				ToolArguments: json.RawMessage(`{"query":"SECRET_CODE"}`),
			},
		},
	}
	expect := Expectation{
		Route:         agent.RouteInspect,
		RequiredTools: []string{"search_text", "read_file"},
		RequiredCalls: []ExpectedCall{
			{Name: "search_text", Arguments: map[string]any{"query": "SECRET_CODE"}},
			{Name: "read_file", Arguments: map[string]any{"path": "logs/run.log"}},
		},
		OutputEquals: &answer,
	}
	if failures := validateTurn(expect, result, nil); len(failures) != 0 {
		t.Fatalf("equivalent discovery path was rejected: %v", failures)
	}
	summary := summarize(
		"run",
		[]Case{{
			ID:          "equivalent",
			Description: "Equivalent discovery path.",
			Turns:       []Turn{{Prompt: "Find SECRET_CODE.", Expect: expect}},
		}},
		[]CaseResult{{
			ID:     "equivalent",
			Passed: true,
			Turns:  []TurnResult{{Result: result, Passed: true}},
		}},
		nil,
	)
	assertScore(t, "required tool completion", summary.Metrics.RequiredToolCompletion, 2, 2)
	assertScore(t, "required call accuracy", summary.Metrics.RequiredCallAccuracy, 2, 2)
}

// TestBoundaryScoringStillRequiresInvestigation guards the relaxation: a model
// that answers with no tool call at all, or that substitutes a non-discovery
// tool, must still fail.
func TestBoundaryScoringStillRequiresInvestigation(t *testing.T) {
	answer := "EMBER-91"
	expect := Expectation{
		Route:         agent.RouteInspect,
		RequiredTools: []string{"read_file"},
		RequiredCalls: []ExpectedCall{
			{Name: "read_file", Arguments: map[string]any{"path": "logs/run.log"}},
		},
		OutputEquals: &answer,
	}
	guessed := agent.Result{
		Route:  agent.RouteInspect,
		Output: "EMBER-91",
	}
	if failures := validateTurn(expect, guessed, nil); len(failures) == 0 {
		t.Fatal("a guessed answer with no tool call was accepted")
	}
	// calculator is not a discovery tool, so it cannot stand in for a read.
	substituted := agent.Result{
		Route:  agent.RouteInspect,
		Output: "EMBER-91",
		Steps: []agent.Step{{
			Tool:          "calculator",
			ToolArguments: json.RawMessage(`{"expression":"1+1"}`),
		}},
	}
	if failures := validateTurn(expect, substituted, nil); len(failures) == 0 {
		t.Fatal("a non-discovery tool satisfied a discovery requirement")
	}
	// A non-discovery requirement stays strictly matched.
	strict := Expectation{
		Route:         agent.RouteInspect,
		RequiredTools: []string{"calculator"},
	}
	discovered := agent.Result{
		Route: agent.RouteInspect,
		Steps: []agent.Step{{
			Tool:          "search_text",
			ToolArguments: json.RawMessage(`{"query":"x"}`),
		}},
	}
	if failures := validateTurn(strict, discovered, nil); len(failures) == 0 {
		t.Fatal("a discovery tool satisfied a calculator requirement")
	}
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

func TestPrimitiveProtocolRepeatPolicyFollowsProfile(t *testing.T) {
	t.Parallel()
	if primitiveProtocol(PrimitiveProfileGoNative).AllowRepeatedCalls {
		t.Fatal("go-native profile must reject repeated calls")
	}
	if !primitiveProtocol(PrimitiveProfileUpstream).AllowRepeatedCalls {
		t.Fatal("upstream-compatible profile must preserve repeated calls")
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
	expectedRate := 0.0
	if total > 0 {
		expectedRate = float64(correct) / float64(total)
	}
	if score.Correct != correct || score.Total != total || score.Rate != expectedRate {
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
