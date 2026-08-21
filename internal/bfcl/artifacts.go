package bfcl

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

type Manifest struct {
	SchemaVersion     int            `json:"schema_version"`
	StartedAt         time.Time      `json:"started_at"`
	RepoCommit        string         `json:"repo_commit,omitempty"`
	RepoDirty         bool           `json:"repo_dirty,omitempty"`
	BinarySHA256      string         `json:"binary_sha256,omitempty"`
	DataDir           string         `json:"data_dir"`
	DataCommit        string         `json:"data_commit"`
	EvaluatorVersion  string         `json:"evaluator_version"`
	Model             string         `json:"model"`
	ModelDirName      string         `json:"model_dir_name"`
	Transport         string         `json:"transport"`
	Tier              string         `json:"tier"`
	RenderProtocol    string         `json:"render_protocol,omitempty"`
	Concurrency       int            `json:"concurrency"`
	Sampling          SamplingRecord `json:"sampling"`
	MaxTokens         int            `json:"max_tokens"`
	MaxPromptChars    int            `json:"max_prompt_chars"`
	CaseTimeout       string         `json:"case_timeout"`
	Splits            []string       `json:"splits"`
	CaseIDs           []string       `json:"case_ids,omitempty"`
	Hardware          string         `json:"hardware,omitempty"`
	Serving           string         `json:"serving,omitempty"`
	ParserMode        string         `json:"parser_mode,omitempty"`
	RetryPrompt       string         `json:"retry_prompt,omitempty"`
	RetryMax          int            `json:"retry_max,omitempty"`
	APIStopTokens     string         `json:"api_stop_tokens,omitempty"`
	APIStream         *bool          `json:"api_stream,omitempty"`
	RemoteBatchWait   string         `json:"remote_batch_wait,omitempty"`
	APIHeaderNames    []string       `json:"api_header_names,omitempty"`
	SourceRun         string         `json:"source_run,omitempty"`
	SourceTraceSHA256 string         `json:"source_trace_sha256,omitempty"`
	SampleManifest    string         `json:"sample_manifest,omitempty"`
	SampleVersion     string         `json:"sample_manifest_version,omitempty"`
	SampleSHA256      string         `json:"sample_manifest_sha256,omitempty"`
}

type SamplingRecord struct {
	Greedy               bool    `json:"greedy"`
	TopK                 int     `json:"top_k"`
	TopKIncluded         bool    `json:"top_k_included"`
	EffectiveTemperature float32 `json:"effective_temperature"`
}

type Summary struct {
	Total            int            `json:"total"`
	Failed           int            `json:"failed"`
	ParseFailed      int            `json:"parse_failed"`
	Repaired         int            `json:"repaired,omitempty"`
	Repairs          map[string]int `json:"repairs,omitempty"`
	Retried          int            `json:"retried,omitempty"`
	RetryParsed      int            `json:"retry_parsed,omitempty"`
	Skipped          int            `json:"skipped"`
	PromptTokens     int            `json:"prompt_tokens"`
	CompletionTokens int            `json:"completion_tokens"`
	ElapsedSeconds   float64        `json:"elapsed_seconds"`
}

func WriteArtifacts(outputDir string, manifest Manifest, result RunResult) error {
	if outputDir == "" {
		return fmt.Errorf("BFCL output directory is required")
	}
	if err := os.MkdirAll(outputDir, 0o700); err != nil {
		return err
	}
	if err := writeJSON(filepath.Join(outputDir, "run.json"), manifest); err != nil {
		return err
	}
	if err := writeTrace(filepath.Join(outputDir, "trace.jsonl"), result.Trace); err != nil {
		return err
	}
	return writeJSON(filepath.Join(outputDir, "summary.json"), Summary{
		Total:            len(result.Trace),
		Failed:           result.Failed,
		ParseFailed:      result.ParseFailed,
		Repaired:         result.Repaired,
		Repairs:          result.RepairCounts,
		Retried:          result.Retried,
		RetryParsed:      result.RetryParsed,
		Skipped:          result.Skipped,
		PromptTokens:     result.Usage.PromptTokens,
		CompletionTokens: result.Usage.CompletionTokens,
		ElapsedSeconds:   result.Elapsed.Seconds(),
	})
}

func writeJSON(path string, value any) error {
	encoded, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	encoded = append(encoded, '\n')
	return os.WriteFile(path, encoded, 0o600)
}

func writeTrace(path string, entries []TraceEntry) error {
	file, err := os.OpenFile(path, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o600)
	if err != nil {
		return err
	}
	writer := bufio.NewWriter(file)
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(false)
	for _, entry := range entries {
		if err := encoder.Encode(entry); err != nil {
			file.Close()
			return err
		}
	}
	if err := writer.Flush(); err != nil {
		file.Close()
		return err
	}
	return file.Close()
}
