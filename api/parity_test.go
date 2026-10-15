package api

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"path/filepath"
	"reflect"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/product"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// The product evaluation (--harness app) drives the same assembly the App
// does, with fixture backends. These tests build the session twice from the
// same description, once the way the App does (api.Config -> assembleSessionTools
// + sessionRunnerOptions) and once the way the evaluation does (product.Tools +
// product.HarnessOptions with hand-written fixture backends and a fixed clock),
// and require the model-visible surface to match byte for byte: control prompt,
// response prompt, session-time message, and the tool list with its order and
// per-tool schema hashes.

type stubSearch struct{}

func (stubSearch) Search(context.Context, assistanttools.WebSearchRequest) ([]assistanttools.WebSearchResult, error) {
	return nil, nil
}

type stubFetch struct{}

func (stubFetch) Fetch(context.Context, assistanttools.WebFetchRequest) ([]assistanttools.WebFetchResult, error) {
	return nil, nil
}

type stubWeather struct{}

func (stubWeather) Forecast(context.Context, assistanttools.WeatherRequest) (assistanttools.WeatherReport, error) {
	return assistanttools.WeatherReport{}, nil
}

type fixedClock struct{ at time.Time }

func (c fixedClock) Now() time.Time { return c.at }

// requireSidecar points the bash tool at the repository's sidecar build and
// skips when it has not been built (scripts/build-justbash.sh).
func requireSidecar(t *testing.T) {
	t.Helper()
	binary, err := assistanttools.ResolveBashSidecar(filepath.Join("..", "local", "bin", "justbash-sidecar"))
	if err != nil {
		t.Skip("bash sidecar not built; run scripts/build-justbash.sh")
	}
	t.Setenv(assistanttools.BashSidecarEnv, binary)
}

type surface struct {
	Control, ResponseControl, SessionContext string
	Tools                                    []string
	SchemaHashes                             []string
}

func specHash(tool agent.Tool) string {
	payload, err := json.Marshal(tool.Spec())
	if err != nil {
		panic(err)
	}
	sum := sha256.Sum256(payload)
	return hex.EncodeToString(sum[:8])
}

func surfaceOf(t *testing.T, options agent.Options, tools []agent.Tool) surface {
	t.Helper()
	preview, err := agent.PreviewPrompts(options, tools, false)
	if err != nil {
		t.Fatal(err)
	}
	out := surface{Control: preview.Control, ResponseControl: preview.ResponseControl, SessionContext: options.SessionContext}
	for _, tool := range tools {
		out.Tools = append(out.Tools, tool.Spec().Name)
		out.SchemaHashes = append(out.SchemaHashes, specHash(tool))
	}
	return out
}

func TestAppAndEvalPathsShareTheModelVisibleSurface(t *testing.T) {
	requireSidecar(t)
	started := time.Date(2026, time.October, 15, 9, 30, 0, 0, time.Local)
	cases := []struct {
		name      string
		workspace bool
		mutate    func(*Config)
	}{
		{name: "new connection defaults", workspace: true},
		{name: "user contract and subagents", workspace: true, mutate: func(c *Config) {
			c.TaskControl = " 回答使用中文。 "
			c.EnableSubagents = true
			c.InjectSessionTime = true
		}},
		{name: "no workspace", workspace: false},
		{name: "legacy markdown connection", workspace: true, mutate: func(c *Config) {
			c.Profile = ""
			c.AgentProtocol = AgentProtocolMarkdown
		}},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			config := newConnection()
			config.InjectSessionTime = true
			if tc.mutate != nil {
				tc.mutate(&config)
			}
			config, err := normalizeConfig(config)
			if err != nil {
				t.Fatal(err)
			}
			workspace := ""
			if tc.workspace {
				workspace = t.TempDir()
			}

			// App path: the session constructor's own steps, minus the live service.
			appTools, err := assembleSessionTools(config, nil, workspace, 0)
			if err != nil {
				t.Fatal(err)
			}
			appOptions := sessionRunnerOptions(config, Status{Model: config.Model}, workspace, appTools,
				config.AgentProtocol != AgentProtocolXML, tc.workspace)
			appOptions.SessionContext = sessionTimeContext(config.InjectSessionTime, started)

			// Evaluation path: product package only, fixture backends, fixed clock.
			set := product.ToolSet{
				Files: true, Edit: tc.workspace, Web: config.EnableWeb, Weather: config.WeatherBackend != "",
				Bash: tc.workspace && config.EnableBash, Subagents: config.EnableSubagents,
			}
			evalTools, err := product.Tools(set, product.Backends{
				Workspace: workspace,
				Clock:     fixedClock{at: time.Date(2026, time.September, 16, 10, 0, 0, 0, time.UTC)},
				Web:       product.WebBackend{Search: stubSearch{}, Fetch: stubFetch{}},
				Weather:   stubWeather{},
				Bash:      product.BashBackend{CatalogOnly: true},
				Delegation: product.DelegationBackend{
					MaxParallel: config.SubagentMaxParallel,
					Timeout:     time.Duration(config.SubagentTimeoutSeconds) * time.Second,
					Run: func(context.Context, string, func(agent.Event)) (assistanttools.AgentTaskResult, error) {
						return assistanttools.AgentTaskResult{}, nil
					},
				},
			})
			if err != nil {
				t.Fatal(err)
			}
			evalConfig := product.HarnessConfig{
				Markdown: config.AgentProtocol != AgentProtocolXML,
				Profile:  config.Profile, Thinking: config.Thinking,
				Model: config.Model, MaxSteps: config.MaxSteps, MaxTokens: config.MaxTokens,
				DecisionMaxTokens: config.DecisionMaxTokens, RouteMaxTokens: config.RouteMaxTokens,
				Sampling: continuation.Sampling{
					Temperature: float32(config.Temperature), TopK: config.TopK, TopP: float32(config.TopP),
					PenaltyDecay: float32(config.PenaltyDecay),
				},
				SemanticNoTool: config.SemanticNoTool, DeepToolAnchor: config.DeepToolAnchor,
				WorkspaceOpen: tc.workspace, Staged: tc.workspace,
				UserTaskControl: config.TaskControl,
				SessionStart:    started,
				Tools:           evalTools,
			}
			if !config.InjectSessionTime {
				evalConfig.SessionStart = time.Time{}
			}
			evalOptions := product.HarnessOptions(evalConfig)

			app, eval := surfaceOf(t, appOptions, appTools), surfaceOf(t, evalOptions, evalTools)
			if !reflect.DeepEqual(app.Tools, eval.Tools) {
				t.Fatalf("tool order differs:\napp  %v\neval %v", app.Tools, eval.Tools)
			}
			if !reflect.DeepEqual(app.SchemaHashes, eval.SchemaHashes) {
				t.Fatalf("tool schemas differ:\napp  %v\neval %v", app.SchemaHashes, eval.SchemaHashes)
			}
			for field, pair := range map[string][2]string{
				"control":          {app.Control, eval.Control},
				"response control": {app.ResponseControl, eval.ResponseControl},
				"session context":  {app.SessionContext, eval.SessionContext},
			} {
				if pair[0] != pair[1] {
					t.Fatalf("%s differs:\n--- app\n%s\n--- eval\n%s", field, pair[0], pair[1])
				}
			}
			appSpec, _ := agent.WireSpecOf(appOptions)
			evalSpec, _ := agent.WireSpecOf(evalOptions)
			if appSpec.Canonical() != evalSpec.Canonical() {
				t.Fatalf("wire differs: %s vs %s", appSpec.Canonical(), evalSpec.Canonical())
			}
			if appOptions.DuplicateReplayLimit != evalOptions.DuplicateReplayLimit ||
				appOptions.DuplicateRescueThreshold != evalOptions.DuplicateRescueThreshold ||
				appOptions.SameToolRescueLimit != evalOptions.SameToolRescueLimit ||
				appOptions.DecisionMaxOutputTokens != evalOptions.DecisionMaxOutputTokens ||
				appOptions.AnswerStageLead != evalOptions.AnswerStageLead ||
				appOptions.MaxSteps != evalOptions.MaxSteps {
				t.Fatalf("loop policy differs: %+v vs %+v", appOptions, evalOptions)
			}
			t.Log(fmt.Sprintf("%d tools, control %d bytes", len(app.Tools), len(app.Control)))
		})
	}
}

// TestCanonicalToolOrder pins the order the model sees for the App's default
// tool set.
func TestCanonicalToolOrder(t *testing.T) {
	requireSidecar(t)
	config, err := normalizeConfig(newConnection())
	if err != nil {
		t.Fatal(err)
	}
	tools, err := assembleSessionTools(config, nil, t.TempDir(), 0)
	if err != nil {
		t.Fatal(err)
	}
	var names []string
	for _, tool := range tools {
		names = append(names, tool.Spec().Name)
	}
	want := []string{
		"list_files", "read_file", "search_text",
		"read_lines", "write_file", "replace_lines", "append_file",
		"calculator", "data_query", "datetime",
		"web_search", "web_fetch", "get_weather", "bash",
	}
	if !reflect.DeepEqual(names, want) {
		t.Fatalf("tool order = %v, want %v", names, want)
	}
}
