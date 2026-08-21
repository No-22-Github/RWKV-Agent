package bfcl

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

type MultiTurnManifest struct {
	SchemaVersion            int            `json:"schema_version"`
	DataCommit               string         `json:"data_commit"`
	EvaluatorVersion         string         `json:"evaluator_version"`
	Model                    string         `json:"model"`
	ModelDirName             string         `json:"model_dir_name"`
	Tier                     string         `json:"tier"`
	Transport                string         `json:"transport"`
	RenderProtocol           string         `json:"render_protocol"`
	ParserMode               string         `json:"parser_mode"`
	SidecarProtocol          string         `json:"sidecar_protocol"`
	Split                    string         `json:"split"`
	CaseID                   string         `json:"case_id"`
	Anchor                   string         `json:"anchor"`
	AnchorPrefill            string         `json:"anchor_prefill"`
	EmptyTurnReachable       bool           `json:"empty_turn_reachable"`
	RenderInitialConfig      bool           `json:"render_initial_config"`
	MaxSteps                 int            `json:"max_steps"`
	MaxTurns                 int            `json:"max_turns,omitempty"`
	MaxPromptChars           int            `json:"max_prompt_chars"`
	MaxPromptTokens          int            `json:"max_prompt_tokens,omitempty"`
	TokenizerVocabSHA256     string         `json:"tokenizer_vocab_sha256,omitempty"`
	MaxTokens                int            `json:"max_tokens"`
	RouteMaxTokens           int            `json:"route_max_tokens,omitempty"`
	RouteRetries             int            `json:"route_retries,omitempty"`
	DuplicateReplayLimit     int            `json:"duplicate_replay_limit,omitempty"`
	DuplicateRescueThreshold int            `json:"duplicate_rescue_threshold,omitempty"`
	SameToolRescueLimit      int            `json:"same_tool_rescue_limit,omitempty"`
	APIStopTokens            string         `json:"api_stop_tokens,omitempty"`
	APIStream                *bool          `json:"api_stream,omitempty"`
	RemoteBatchWait          string         `json:"remote_batch_wait,omitempty"`
	APIHeaderNames           []string       `json:"api_header_names,omitempty"`
	Sampling                 SamplingRecord `json:"sampling"`
	RepoCommit               string         `json:"repo_commit,omitempty"`
	RepoDirty                bool           `json:"repo_dirty,omitempty"`
	BinarySHA256             string         `json:"binary_sha256,omitempty"`
}

type MultiTurnSummary struct {
	Cases          int     `json:"cases"`
	Turns          int     `json:"turns"`
	Steps          int     `json:"steps"`
	ModelCalls     int     `json:"model_calls"`
	RouteCalls     int     `json:"route_calls,omitempty"`
	InputTokens    int     `json:"input_tokens,omitempty"`
	OutputTokens   int     `json:"output_tokens,omitempty"`
	Latency        float64 `json:"latency_seconds,omitempty"`
	MaxPromptBytes int     `json:"max_prompt_bytes"`
	Events         int     `json:"events"`
	Error          string  `json:"error,omitempty"`
}

func WriteMultiTurnArtifacts(outputDir string, manifest MultiTurnManifest, trace MultiTurnTrace) error {
	if outputDir == "" {
		return fmt.Errorf("BFCL multi-turn output directory is required")
	}
	if err := os.MkdirAll(outputDir, 0o700); err != nil {
		return err
	}
	if err := writeJSON(filepath.Join(outputDir, "run.json"), manifest); err != nil {
		return err
	}
	tracePath := filepath.Join(outputDir, "trace.jsonl")
	file, err := os.OpenFile(tracePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o600)
	if err != nil {
		return err
	}
	writer := bufio.NewWriter(file)
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(false)
	if err := encoder.Encode(trace); err != nil {
		file.Close()
		return err
	}
	if err := writer.Flush(); err != nil {
		file.Close()
		return err
	}
	if err := file.Close(); err != nil {
		return err
	}
	steps := 0
	for _, turn := range trace.Turns {
		steps += len(turn.Steps)
	}
	return writeJSON(filepath.Join(outputDir, "summary.json"), MultiTurnSummary{
		Cases: 1, Turns: len(trace.Turns), Steps: steps, ModelCalls: trace.ModelCalls,
		RouteCalls: trace.RouteCalls, InputTokens: trace.InputTokens, OutputTokens: trace.OutputTokens,
		Latency: trace.Latency, MaxPromptBytes: trace.MaxPromptBytes, Events: len(trace.Events), Error: trace.Error,
	})
}

func WriteMultiTurnResult(resultDir, modelDir string, trace MultiTurnTrace) error {
	path := filepath.Join(resultDir, modelDir, "multi_turn", "BFCL_v4_"+trace.Category+"_result.json")
	if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
		return err
	}
	file, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o600)
	if err != nil {
		return err
	}
	encoder := json.NewEncoder(file)
	encoder.SetEscapeHTML(false)
	// The official partial evaluator computes a sample standard deviation when
	// latency is present and crashes for the single-case M3 run. The complete
	// timing remains in trace.jsonl and summary.json.
	err = encoder.Encode(struct {
		ID           string       `json:"id"`
		Result       [][][]string `json:"result"`
		InputTokens  int          `json:"input_token_count,omitempty"`
		OutputTokens int          `json:"output_token_count,omitempty"`
	}{ID: trace.ID, Result: trace.Result, InputTokens: trace.InputTokens, OutputTokens: trace.OutputTokens})
	if closeErr := file.Close(); err == nil {
		err = closeErr
	}
	return err
}
