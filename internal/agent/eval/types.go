package eval

import (
	"context"
	"io"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

const (
	SchemaVersion  = 3
	HarnessVersion = "rwkv-agent-eval-v10"
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
	Turns               []Turn            `json:"turns"`
}

type Turn struct {
	Prompt string      `json:"prompt"`
	Expect Expectation `json:"expect"`
}

type Expectation struct {
	Route               agent.Route      `json:"route,omitempty"`
	Tools               []string         `json:"tools,omitempty"`
	Calls               []ExpectedCall   `json:"calls,omitempty"`
	RequiredTools       []string         `json:"required_tools,omitempty"`
	ForbiddenTools      []string         `json:"forbidden_tools,omitempty"`
	RequiredCalls       []ExpectedCall   `json:"required_calls,omitempty"`
	OutputEquals        *string          `json:"output_equals,omitempty"`
	OutputContains      []string         `json:"output_contains,omitempty"`
	OutputContainsAny   []string         `json:"output_contains_any,omitempty"`
	OutputExcludes      []string         `json:"output_excludes,omitempty"`
	ExpectedNumber      *float64         `json:"expected_number,omitempty"`
	Tolerance           *float64         `json:"tolerance,omitempty"`
	Plan                *PlanExpectation `json:"plan,omitempty"`
	MustStateUnverified []string         `json:"must_state_unverified,omitempty"`
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
	Version                 string `json:"version"`
	Protocol                string `json:"protocol"`
	Renderer                string `json:"renderer"`
	RouteRenderer           string `json:"route_renderer"`
	RouteProtocol           string `json:"route_protocol"`
	RouteStage              bool   `json:"route_stage"`
	ControlPrompt           string `json:"control_prompt"`
	ThinkingMode            string `json:"thinking_mode"`
	Reasoning               bool   `json:"reasoning"`
	FewShot                 bool   `json:"few_shot"`
	MaxSteps                int    `json:"max_steps"`
	ProtocolRetries         int    `json:"protocol_retries"`
	RouteRetries            int    `json:"route_retries"`
	AnswerMaxOutputTokens   int    `json:"answer_max_output_tokens"`
	DecisionMaxOutputTokens int    `json:"decision_max_output_tokens"`
	RouteMaxOutputTokens    int    `json:"route_max_output_tokens"`
	TracePromptBytes        int    `json:"trace_prompt_bytes"`
}

type EnvironmentMetadata struct {
	OS        string `json:"os"`
	Arch      string `json:"arch"`
	GoVersion string `json:"go_version"`
}

type RunManifest struct {
	SchemaVersion int                 `json:"schema_version"`
	RunID         string              `json:"run_id"`
	Suite         string              `json:"suite"`
	StartedAt     time.Time           `json:"started_at"`
	CompletedAt   time.Time           `json:"completed_at"`
	Model         ModelMetadata       `json:"model"`
	Harness       HarnessMetadata     `json:"harness"`
	Sampling      SamplingSnapshot    `json:"sampling"`
	Environment   EnvironmentMetadata `json:"environment"`
	CaseIDs       []string            `json:"case_ids"`
	Cases         []Case              `json:"cases"`
}

type Score struct {
	Correct int     `json:"correct"`
	Total   int     `json:"total"`
	Rate    float64 `json:"rate"`
}

type Metrics struct {
	TaskSuccess            Score `json:"task_success"`
	AnswerAccuracy         Score `json:"answer_accuracy"`
	RouteAccuracy          Score `json:"route_accuracy"`
	ProtocolValidity       Score `json:"protocol_validity"`
	ToolSelection          Score `json:"tool_selection"`
	ArgumentAccuracy       Score `json:"argument_accuracy"`
	RequiredToolCompletion Score `json:"required_tool_completion"`
	ForbiddenToolAvoidance Score `json:"forbidden_tool_avoidance"`
	RequiredCallAccuracy   Score `json:"required_call_accuracy"`
	NoCallAccuracy         Score `json:"no_call_accuracy"`
	PlanSubtaskCount       Score `json:"plan_subtask_count"`
	PlanWaveOrder          Score `json:"plan_wave_order"`
	PlanReferenceUse       Score `json:"plan_reference_use"`
	ExplicitAbstention     Score `json:"explicit_abstention"`
	AnswerContractRepaired Score `json:"answer_contract_repaired"`

	ModelCalls       int   `json:"model_calls"`
	ToolCalls        int   `json:"tool_calls"`
	ToolExecutions   int   `json:"tool_executions"`
	ToolErrors       int   `json:"tool_errors"`
	RejectedCalls    int   `json:"rejected_tool_calls"`
	DuplicateCalls   int   `json:"duplicate_tool_calls"`
	RecoveryBlocks   int   `json:"recovery_blocked_calls"`
	ForcedAnswers    int   `json:"forced_answers"`
	ProtocolRetries  int   `json:"protocol_retries"`
	RouteFallbacks   int   `json:"route_fallbacks"`
	PlanRejections   int   `json:"plan_rejections"`
	PlanFallbacks    int   `json:"plan_fallbacks"`
	PromptTokens     int   `json:"prompt_tokens"`
	CompletionTokens int   `json:"completion_tokens"`
	WallTimeMillis   int64 `json:"wall_time_millis"`
}

type TurnResult struct {
	Number      int          `json:"number"`
	Prompt      string       `json:"prompt"`
	Result      agent.Result `json:"result"`
	RunnerError string       `json:"runner_error,omitempty"`
	Failures    []string     `json:"failures,omitempty"`
	Passed      bool         `json:"passed"`
}

type CaseResult struct {
	ID          string       `json:"id"`
	Description string       `json:"description"`
	Category    string       `json:"category,omitempty"`
	Turns       []TurnResult `json:"turns"`
	Error       string       `json:"error,omitempty"`
	Passed      bool         `json:"passed"`
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
	Result agent.Result `json:"result"`
	Error  string       `json:"error,omitempty"`
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
	Now              func() time.Time
	TempDir          string
}

type caseFile struct {
	SchemaVersion int    `json:"schema_version"`
	Cases         []Case `json:"cases"`
}
