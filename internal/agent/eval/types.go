package eval

import (
	"context"
	"io"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

const (
	CaseSchemaVersion = 5
	// caseSchemaVersionLegacy keeps v4 case files loadable unchanged; a v4
	// file simply has no tags / case-level web fixture / case-level expect.
	caseSchemaVersionLegacy = 4
	RunSchemaVersion        = 8
	HarnessVersion          = "rwkv-agent-eval-v22"
	ScorerVersion           = "rwkv-agent-eval-scorer-v3"
	OutcomeTaxonomyVersion  = "rwkv-agent-outcome-v2"

	PrimitiveProfileUpstream = "upstream-compatible"
	PrimitiveProfileGoNative = "go-native"
)

type GeneratorFactory func(
	context.Context,
) (continuation.Generator, io.Closer, error)

type Case struct {
	ID                  string            `json:"id"`
	Description         string            `json:"description"`
	Category            string            `json:"category,omitempty"`
	Source              string            `json:"source,omitempty"`
	Difficulty          string            `json:"difficulty,omitempty"`
	Files               map[string]string `json:"files,omitempty"`
	OutsideFiles        map[string]string `json:"outside_files,omitempty"`
	ProviderUnavailable []string          `json:"provider_unavailable,omitempty"`
	// Tags is a schema-v5 passthrough object (scenario/traps/level/status/...)
	// carried into run.json, summary and traces untouched. The harness only
	// interprets tags.status (draft gating for --include-draft).
	Tags map[string]any `json:"tags,omitempty"`
	// WebFixture (v5) attaches a per-case fixture so a bank of web tasks cannot
	// cross-contaminate through one shared keyword map. Empty falls back to the
	// suite-level fixture for legacy custom suites.
	WebFixture []WebFixtureEntry `json:"web_fixture,omitempty"`
	// Expect (v5) holds case-level result expectations evaluated after the
	// final turn against the workspace state and the whole transcript.
	Expect    *CaseExpect        `json:"expect,omitempty"`
	Turns     []Turn             `json:"turns"`
	Primitive *PrimitiveMetadata `json:"primitive,omitempty"`
	primitive *primitiveRuntime
}

// CaseExpect carries the v5 case-level expectations. Unlike turn expectations,
// which score per-turn model output, these score end state: files on disk, an
// offline script run against a copy of the final workspace, and per-tool call
// budgets counted over the whole case (including duplicate-rejected calls, so
// the harness cannot hide a loop behind duplicate rejection).
type CaseExpect struct {
	Files    map[string]FileExpectation `json:"files,omitempty"`
	Run      *RunExpectation            `json:"run,omitempty"`
	MaxCalls map[string]int             `json:"max_calls,omitempty"`
}

// FileExpectation scores one path of the final workspace. At most one of
// equals / contains / absent / unchanged may be set; unchanged compares
// byte-for-byte against the initial fixture (which must exist in files).
type FileExpectation struct {
	Equals    *string  `json:"equals,omitempty"`
	Contains  []string `json:"contains,omitempty"`
	Absent    bool     `json:"absent,omitempty"`
	Unchanged bool     `json:"unchanged,omitempty"`
}

// RunExpectation executes a workspace script offline against a copy of the
// final workspace: python3 -I -S (isolated site-packages), a hard timeout,
// and stdout compared line by line (trailing \r ignored). The sandbox root
// holds workspace/ (the copy) plus hidden/ (HiddenFiles), so scripts can be
// re-run on second inputs the model never saw. Network isolation is
// best-effort: the runner strips the environment but cannot guarantee it on
// every platform, which the bank docs call out.
type RunExpectation struct {
	Path           string            `json:"path"`
	Args           []string          `json:"args,omitempty"`
	ExpectedStdout string            `json:"expected_stdout"`
	HiddenFiles    map[string]string `json:"hidden_files,omitempty"`
	TimeoutMillis  int               `json:"timeout_millis,omitempty"`
}

// PrimitiveMetadata preserves the source-side scoring and emulator contract in
// run.json for an imported Primitive Bench case. It is populated only by the
// trusted-directory loader, not by the versioned native case schema.
type PrimitiveMetadata struct {
	ToolNames      []string          `json:"tool_names"`
	Modes          map[string]string `json:"modes,omitempty"`
	RunOutputs     map[string]string `json:"run_outputs,omitempty"`
	ExpectedSubmit *string           `json:"expected_submit,omitempty"`
	Scenario       string            `json:"scenario,omitempty"`
	Scorer         string            `json:"scorer"`
	Tolerance      *float64          `json:"tolerance,omitempty"`
	MaxTurns       int               `json:"max_turns,omitempty"`
}

type Turn struct {
	Prompt string      `json:"prompt"`
	Expect Expectation `json:"expect"`
}

type Expectation struct {
	Route agent.Route `json:"route,omitempty"`
	// Tools is deliberately not omitempty: an empty-but-present list is the
	// zero-call contract and a nil list is no constraint at all. With omitempty
	// the two serialized identically, so a frozen run.json lost every notool
	// case's contract and no offline re-scoring could see it.
	Tools               []string         `json:"tools"`
	Calls               []ExpectedCall   `json:"calls,omitempty"`
	RequiredTools       []string         `json:"required_tools,omitempty"`
	ForbiddenTools      []string         `json:"forbidden_tools,omitempty"`
	RequiredCalls       []ExpectedCall   `json:"required_calls,omitempty"`
	OutputEquals        *string          `json:"output_equals,omitempty"`
	OutputEqualsAny     []string         `json:"output_equals_any,omitempty"`
	OutputContains      []string         `json:"output_contains,omitempty"`
	OutputContainsAny   []string         `json:"output_contains_any,omitempty"`
	OutputExcludes      []string         `json:"output_excludes,omitempty"`
	ExpectedNumber      *float64         `json:"expected_number,omitempty"`
	Tolerance           *float64         `json:"tolerance,omitempty"`
	Plan                *PlanExpectation `json:"plan,omitempty"`
	MustStateUnverified []string         `json:"must_state_unverified,omitempty"`
	RequireActiveNoCall bool             `json:"require_active_no_call,omitempty"`
	ForbidRouteFallback bool             `json:"forbid_route_fallback,omitempty"`
}

type PlanExpectation struct {
	SubtaskCount int         `json:"subtask_count"`
	Waves        [][]string  `json:"waves"`
	References   []Reference `json:"references"`
}

type Reference struct {
	Subtask  int    `json:"subtask"`
	Argument string `json:"argument"`
	Source   string `json:"source"`
}

type ExpectedCall struct {
	Name      string         `json:"name"`
	Arguments map[string]any `json:"arguments,omitempty"`
}

type ModelMetadata struct {
	Identifier           string   `json:"identifier"`
	Fingerprint          string   `json:"fingerprint,omitempty"`
	TokenizerFingerprint string   `json:"tokenizer_fingerprint,omitempty"`
	Architecture         string   `json:"architecture,omitempty"`
	Format               string   `json:"format,omitempty"`
	Precision            string   `json:"precision,omitempty"`
	Quantization         string   `json:"quantization,omitempty"`
	Backend              string   `json:"backend"`
	Provider             string   `json:"provider"`
	Completion           string   `json:"completion"`
	PromptMode           string   `json:"prompt_mode,omitempty"`
	UnsupportedSampling  []string `json:"unsupported_sampling,omitempty"`
	UpstreamThinking     string   `json:"upstream_thinking,omitempty"`
	TokenLimitField      string   `json:"token_limit_field,omitempty"`
}

type HarnessMetadata struct {
	SemanticNoTool           bool     `json:"semantic_no_tool"`
	DecisionFakeThink        bool     `json:"decision_fake_think"`
	DeepToolAnchor           bool     `json:"deep_tool_anchor"`
	Version                  string   `json:"version"`
	ScorerVersion            string   `json:"scorer_version"`
	OutcomeTaxonomyVersion   string   `json:"outcome_taxonomy_version"`
	Protocol                 string   `json:"protocol"`
	Renderer                 string   `json:"renderer"`
	RouteRenderer            string   `json:"route_renderer"`
	RouteProtocol            string   `json:"route_protocol"`
	RouteStage               bool     `json:"route_stage"`
	ControlPrompt            string   `json:"control_prompt"`
	TaskControl              string   `json:"task_control,omitempty"`
	TerminalTool             string   `json:"terminal_tool,omitempty"`
	EndOnTerminalTool        bool     `json:"end_on_terminal_tool,omitempty"`
	ThinkingMode             string   `json:"thinking_mode"`
	RouteThinkingMode        string   `json:"route_thinking_mode"`
	Reasoning                bool     `json:"reasoning"`
	FewShot                  bool     `json:"few_shot"`
	MaxSteps                 int      `json:"max_steps"`
	ProtocolRetries          int      `json:"protocol_retries"`
	RouteRetries             int      `json:"route_retries"`
	AnswerMaxOutputTokens    int      `json:"answer_max_output_tokens"`
	DecisionMaxOutputTokens  int      `json:"decision_max_output_tokens"`
	RouteMaxOutputTokens     int      `json:"route_max_output_tokens"`
	TracePromptBytes         int      `json:"trace_prompt_bytes"`
	CaseParallelism          int      `json:"case_parallelism"`
	CaseTimeoutSeconds       int      `json:"case_timeout_seconds"`
	RemoteBatchWaitMillis    int      `json:"remote_batch_wait_ms"`
	ToolProfile              string   `json:"tool_profile,omitempty"`
	DuplicateReplayLimit     int      `json:"duplicate_replay_limit"`
	DuplicateRescueThreshold int      `json:"duplicate_rescue_threshold"`
	SameToolRescueLimit      int      `json:"same_tool_rescue_limit"`
	ScenarioHooks            []string `json:"scenario_hooks,omitempty"`
	CompressFetch            bool     `json:"compress_fetch,omitempty"`
	WebFixture               bool     `json:"web_fixture,omitempty"`
	SubagentFixture          bool     `json:"subagent_fixture,omitempty"`
	TokenCountVocabSHA256    string   `json:"token_count_vocab_sha256,omitempty"`
	// ToolCatalog names the registered tool catalog ("work-v1" for the work
	// bank's fixed twelve-tool directory); ToolCatalogHash pins the exact
	// schemas offered, so a catalog change invalidates ledger comparability.
	ToolCatalog     string `json:"tool_catalog,omitempty"`
	ToolCatalogHash string `json:"tool_catalog_hash,omitempty"`
	// WireProfile records the raw --profile string (ad-hoc modifier chains do
	// not match a preset, so WirePreset alone cannot recover the input).
	WireProfile string `json:"wire_profile,omitempty"`
	// StateID/StateSHA256 identify a reused rwkv_lightning state; the digest
	// is over the state ID string (the harness never sees the .pth bytes).
	StateID     string `json:"state_id,omitempty"`
	StateSHA256 string `json:"state_sha256,omitempty"`
	// WireCanonical and WireHash identify the exact model-facing
	// configuration (format x thinking x prefill x action space x loop). They
	// are derived from the runtime options by agent.WireSpecOf, so an archived
	// run can be compared and reproduced from its manifest alone.
	WireCanonical string `json:"wire_canonical,omitempty"`
	WireHash      string `json:"wire_hash,omitempty"`
	// WireConflict records a legacy option combination that the canonical spec
	// rejects (for example XML + thinking + router, whose envelope prefix the
	// runner silently drops). The run still executes with the legacy fields
	// until P2 turns the conflict into a hard error.
	WireConflict string `json:"wire_conflict,omitempty"`
	// WirePreset names the registered preset the effective spec matches, or is
	// empty for an ad-hoc combination. Anonymous combinations stay traceable
	// through wire_canonical/wire_hash.
	WirePreset string `json:"wire_preset,omitempty"`
}

type EnvironmentMetadata struct {
	OS        string `json:"os"`
	Arch      string `json:"arch"`
	GoVersion string `json:"go_version"`
}

// CaseWireRecord is the effective harness configuration of one case. The
// suite-level HarnessMetadata cannot describe a per-case terminal tool, step
// budget or transcript, so the manifest carries the resolved values here. A
// case whose options the canonical spec rejects records the reason instead of
// silently reporting the suite-level values.
type CaseWireRecord struct {
	ID                      string `json:"id"`
	WireCanonical           string `json:"wire_canonical,omitempty"`
	WireHash                string `json:"wire_hash,omitempty"`
	WirePreset              string `json:"wire_preset,omitempty"`
	WireConflict            string `json:"wire_conflict,omitempty"`
	TerminalTool            string `json:"terminal_tool,omitempty"`
	MaxSteps                int    `json:"max_steps,omitempty"`
	DecisionMaxOutputTokens int    `json:"decision_max_output_tokens,omitempty"`
}

type RunManifest struct {
	SchemaVersion int             `json:"schema_version"`
	RunID         string          `json:"run_id"`
	Suite         string          `json:"suite"`
	StartedAt     time.Time       `json:"started_at"`
	CompletedAt   time.Time       `json:"completed_at"`
	Model         ModelMetadata   `json:"model"`
	Harness       HarnessMetadata `json:"harness"`
	// Sampling records the sampling keys actually sent to the backend: keys
	// listed in Model.UnsupportedSampling are omitted, so a chat-completions
	// manifest does not claim a top_k/penalty_decay the API never received.
	Sampling    map[string]any      `json:"sampling"`
	Environment EnvironmentMetadata `json:"environment"`
	CaseIDs     []string            `json:"case_ids"`
	CaseWires   []CaseWireRecord    `json:"case_wires,omitempty"`
	Cases       []Case              `json:"cases"`
}

type Score struct {
	Correct int     `json:"correct"`
	Total   int     `json:"total"`
	Rate    float64 `json:"rate"`
}

type TurnOutcome string

const (
	OutcomeExplicitRespond       TurnOutcome = "explicit_respond"
	OutcomeDirectFinal           TurnOutcome = "direct_final"
	OutcomeSemanticNoCall        TurnOutcome = "semantic_no_call"
	OutcomeCalledTool            TurnOutcome = "called_tool"
	OutcomeRouteFailedClosed     TurnOutcome = "route_failed_closed"
	OutcomeToolEnvelopeMissing   TurnOutcome = "tool_envelope_missing"
	OutcomeToolJSONDecodeFailed  TurnOutcome = "tool_json_decode_failed"
	OutcomeToolShapeInvalid      TurnOutcome = "tool_shape_invalid"
	OutcomeProtocolRepaired      TurnOutcome = "protocol_repaired"
	OutcomeDecisionProtocolError TurnOutcome = "decision_protocol_invalid"
)

type Metrics struct {
	TaskSuccess              Score `json:"task_success"`
	AnswerAccuracy           Score `json:"answer_accuracy"`
	RouteAccuracy            Score `json:"route_accuracy"`
	ProtocolValidity         Score `json:"protocol_validity"`
	StageContractValidity    Score `json:"stage_contract_validity"`
	ToolSelection            Score `json:"tool_selection"`
	ArgumentAccuracy         Score `json:"argument_accuracy"`
	RequiredToolCompletion   Score `json:"required_tool_completion"`
	ForbiddenToolAvoidance   Score `json:"forbidden_tool_avoidance"`
	RequiredCallAccuracy     Score `json:"required_call_accuracy"`
	NoCallAccuracy           Score `json:"no_call_accuracy"`
	ActiveNoCall             Score `json:"active_no_call"`
	RouteProtocolValidity    Score `json:"route_protocol_validity"`
	DecisionProtocolValidity Score `json:"decision_protocol_validity"`
	// NativeProtocolValidity scores native-channel decision steps only: the
	// structured provider call either produced a decodable action or it did
	// not. Text-wire repair markers do not exist on this channel.
	NativeProtocolValidity Score `json:"native_protocol_validity"`
	PlanSubtaskCount       Score `json:"plan_subtask_count"`
	PlanWaveOrder          Score `json:"plan_wave_order"`
	PlanReferenceUse       Score `json:"plan_reference_use"`
	ExplicitAbstention     Score `json:"explicit_abstention"`
	AnswerContractRepaired Score `json:"answer_contract_repaired"`

	// InvalidCases counts cases dropped from task_success because the provider
	// or transport aborted them. task_success.total is the surviving sample, so
	// a run's denominator and this counter have to be read together.
	InvalidCases int `json:"invalid_cases"`
	// AnswerFormatViolations counts failed answers that led with the right
	// value and failed on the text around it. Read against answer_accuracy it
	// separates "answered wrongly" from "answered correctly, formatted
	// wrongly"; a bare pass rate cannot tell them apart.
	AnswerFormatViolations int                                `json:"answer_format_violations"`
	ModelCalls             int                                `json:"model_calls"`
	ToolCalls              int                                `json:"tool_calls"`
	ToolExecutions         int                                `json:"tool_executions"`
	ToolErrors             int                                `json:"tool_errors"`
	RejectedCalls          int                                `json:"rejected_tool_calls"`
	DuplicateCalls         int                                `json:"duplicate_tool_calls"`
	RecoveryBlocks         int                                `json:"recovery_blocked_calls"`
	ForcedAnswers          int                                `json:"forced_answers"`
	RescueAttempts         int                                `json:"rescue_attempts"`
	RescueSubmits          int                                `json:"rescue_submits"`
	ProtocolRetries        int                                `json:"protocol_retries"`
	ProtocolRepairs        int                                `json:"protocol_repairs"`
	AnswerStageToolCalls   int                                `json:"answer_stage_tool_calls"`
	RouteFallbacks         int                                `json:"route_fallbacks"`
	PlanRejections         int                                `json:"plan_rejections"`
	PlanFallbacks          int                                `json:"plan_fallbacks"`
	PromptTokens           int                                `json:"prompt_tokens"`
	CompletionTokens       int                                `json:"completion_tokens"`
	WallTimeMillis         int64                              `json:"wall_time_millis"`
	Outcomes               map[TurnOutcome]int                `json:"outcomes"`
	ParseFailuresByClass   map[agent.ProtocolFailureClass]int `json:"parse_failures_by_class"`
	// RepairsByID counts which tolerant-recovery stage fired. A prompt or
	// format change that silently pushes work into the parser shows up here as
	// a repair-count shift instead of a flat score.
	RepairsByID map[string]int `json:"repairs_by_id,omitempty"`
}

type TurnResult struct {
	Number      int          `json:"number"`
	Prompt      string       `json:"prompt"`
	Result      agent.Result `json:"result"`
	Outcome     TurnOutcome  `json:"outcome"`
	RunnerError string       `json:"runner_error,omitempty"`
	Failures    []string     `json:"failures,omitempty"`
	Passed      bool         `json:"passed"`
}

type CaseResult struct {
	ID          string         `json:"id"`
	Description string         `json:"description"`
	Category    string         `json:"category,omitempty"`
	Tags        map[string]any `json:"tags,omitempty"`
	Turns       []TurnResult   `json:"turns"`
	// Failures holds case-level (end-state) violations: expect.files,
	// expect.run and expect.max_calls. Turn-level failures stay on the turns.
	Failures []string `json:"failures,omitempty"`
	Error    string   `json:"error,omitempty"`
	Passed   bool     `json:"passed"`
	// Invalid marks a case whose run was aborted by the provider or the
	// transport rather than decided by the model: the turn produced no answer
	// to score. An invalid case leaves the task_success denominator entirely
	// and is counted in invalid_cases, so an upstream break shows up as a
	// smaller sample rather than as a lower score. InvalidReason carries the
	// upstream error for the run record.
	Invalid       bool   `json:"invalid,omitempty"`
	InvalidReason string `json:"invalid_reason,omitempty"`
	// Per-case intervention counters (H3): how much harness assistance this
	// case consumed, aggregated from the embedded turn results so the ledger
	// can separate rescue-assisted passes from clean ones.
	ToolCalls        int `json:"tool_calls,omitempty"`
	DuplicateRejects int `json:"duplicate_rejects,omitempty"`
	Rescues          int `json:"rescues,omitempty"`
	RescueSubmits    int `json:"rescue_submits,omitempty"`
	ForcedAnswers    int `json:"forced_answers,omitempty"`
	ProtocolRepairs  int `json:"protocol_repairs,omitempty"`
}

type Summary struct {
	RunID   string       `json:"run_id"`
	Metrics Metrics      `json:"metrics"`
	Cases   []CaseResult `json:"cases"`
}

type SamplingSnapshot struct {
	Temperature      float32 `json:"temperature"`
	TopK             int     `json:"top_k"`
	TopP             float32 `json:"top_p"`
	PresencePenalty  float32 `json:"presence_penalty"`
	FrequencyPenalty float32 `json:"frequency_penalty"`
	PenaltyDecay     float32 `json:"penalty_decay"`
	Seed             *int64  `json:"seed,omitempty"`
}

type RequestSnapshot struct {
	Model           string           `json:"model"`
	Prompt          string           `json:"prompt"`
	MaxOutputTokens int              `json:"max_output_tokens"`
	Stops           []string         `json:"stops"`
	Sampling        SamplingSnapshot `json:"sampling"`
}

type UsageSnapshot struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
}

type ResponseSnapshot struct {
	Text         string                    `json:"text"`
	FinishReason continuation.FinishReason `json:"finish_reason"`
	Usage        UsageSnapshot             `json:"usage"`
}

type ModelCallTrace struct {
	Stage          string           `json:"stage"`
	Request        RequestSnapshot  `json:"request"`
	Response       ResponseSnapshot `json:"response"`
	Error          string           `json:"error,omitempty"`
	DurationMillis int64            `json:"duration_millis"`
}

type RunnerEventTrace struct {
	Kind  agent.EventKind `json:"kind"`
	Step  int             `json:"step,omitempty"`
	Tool  string          `json:"tool,omitempty"`
	Route agent.Route     `json:"route,omitempty"`
	Error string          `json:"error,omitempty"`
}

type TurnTrace struct {
	Result  agent.Result `json:"result"`
	Outcome TurnOutcome  `json:"outcome"`
	Error   string       `json:"error,omitempty"`
}

type TraceRecord struct {
	Sequence    int               `json:"sequence"`
	Timestamp   time.Time         `json:"timestamp"`
	CaseID      string            `json:"case_id"`
	Turn        int               `json:"turn"`
	Kind        string            `json:"kind"`
	ModelCall   *ModelCallTrace   `json:"model_call,omitempty"`
	RunnerEvent *RunnerEventTrace `json:"runner_event,omitempty"`
	TurnResult  *TurnTrace        `json:"turn_result,omitempty"`
}

type Report struct {
	Manifest RunManifest
	Summary  Summary
	Trace    []TraceRecord
}

type Config struct {
	Cases            []Case
	Suite            string
	Model            ModelMetadata
	Runner           agent.Options
	GeneratorFactory GeneratorFactory
	CaseTimeout      time.Duration
	CaseParallelism  int
	// RemoteBatchWait is the client-side request coalescing window, recorded
	// in the harness manifest; the runner itself does not coalesce.
	RemoteBatchWait  time.Duration
	Now              func() time.Time
	TempDir          string
	PrimitiveProfile string
	// FileToolForm optionally appends the file-editing toolset ("lines" or
	// "whole", see tools.FileEditForm) to non-primitive suites.
	FileToolForm string
	// SubagentFixture optionally appends a fixture-backed spawn_agents tool.
	// Each entry matches a subtask by keyword (case-insensitive substring) and
	// returns the canned output, so class-3 (sub-agent) e2e tasks run
	// deterministically without network or nested model calls.
	SubagentFixture []SubagentFixtureEntry
	// FetchBudgetTokens overrides the per-call token budget of fixture-backed
	// and fixture-less web tools (0 = default); round-2 E1 re-judgment A/B.
	FetchBudgetTokens int
	// TokenCount counts tokens with the real World vocabulary in-process
	// (round-3 step 1). Nil keeps the fetch-compression hook off and makes the
	// web tools fall back to the estimator for budget slicing. The vocabulary
	// SHA-256 rides in the harness manifest via TokenCountVocabSHA256.
	TokenCount func(string) int
	// TokenCountVocabSHA256 pins the vocabulary that produced every real token
	// count in this run ("" = estimator fallback).
	TokenCountVocabSHA256 string
	// WebFixture optionally appends fixture-backed web_search and web_fetch
	// tools. Entries match queries and URLs by keyword (case-insensitive
	// substring), so web-tool e2e tasks run deterministically without network
	// access and fetch compression can be validated end to end.
	WebFixture []WebFixtureEntry
	// ToolCatalog selects a registered fixed tool catalog ("work-v1"); it
	// replaces the per-suite toolset so every bank case faces the same
	// directory, with the fixed clock and always-on web tools.
	ToolCatalog string
	// WireProfile records the raw --profile input for the manifest.
	WireProfile string
	// StateID/StateSHA256 record a reused rwkv_lightning state in the manifest.
	StateID     string
	StateSHA256 string
}

type SubagentFixtureEntry struct {
	Match   string   `json:"match"`
	Output  string   `json:"output"`
	Sources []string `json:"sources,omitempty"`
	// MatchAll requires every keyword (case-insensitive substring, hyphens
	// and spaces treated as equal) to appear in the subtask text. Class-3
	// candidates need subject AND source discrimination in one entry; a
	// single Match keyword cannot express that across shared subjects.
	MatchAll []string `json:"match_all,omitempty"`
}

type caseFile struct {
	SchemaVersion int    `json:"schema_version"`
	Cases         []Case `json:"cases"`
}
