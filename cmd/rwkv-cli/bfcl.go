package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/no22/RWKV-Agent/internal/bfcl"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

const (
	bfclDataCommit       = "6ea57973c7a6097fd7c5915698c54c17c5b1b6c8"
	bfclEvaluatorVersion = "2026.3.23"
	bfclModelDirName     = "rwkv-agent-bfcl-ab-v1"
)

type bfclEvalOptions struct {
	model                string
	tier                 string
	transport            string
	apiURL               string
	apiKeyEnv            string
	apiHeaderEnvs        stringListFlag
	dataDir              string
	output               string
	splits               stringListFlag
	caseIDs              stringListFlag
	sampleManifest       string
	full                 bool
	concurrency          int
	maxTokens            int
	maxPromptChars       int
	temperature          float64
	caseTimeout          time.Duration
	apiStopTokens        string
	apiStream            bool
	remoteBatchWait      time.Duration
	chatThinking         string
	chatTemplateThinking string
	chatTokenLimit       string
	chatIncludeTopK      bool
	hardware             string
	serving              string
}

// chatTemplateEnableThinking maps the tri-state --chat-template-thinking flag to
// the optional chat_template_kwargs.enable_thinking value. Auto leaves the
// server default untouched by returning nil.
func (options bfclEvalOptions) chatTemplateEnableThinking() *bool {
	if options.chatTemplateThinking == string(chatcompletions.ThinkingAuto) {
		return nil
	}
	enableThinking := options.chatTemplateThinking == string(chatcompletions.ThinkingEnabled)
	return &enableThinking
}

// requireFreshOutput rejects an output path that already exists so a rerun
// never mixes artifacts from two runs.
func requireFreshOutput(path, label string) error {
	if _, err := os.Stat(path); err == nil {
		return fmt.Errorf("%s already exists: %s", label, path)
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	return nil
}

func runBFCLEval(args []string) error {
	options, err := parseBFCLEvalOptions(args)
	if err != nil {
		return err
	}
	if err := requireFreshOutput(options.output, "BFCL output"); err != nil {
		return err
	}
	headers, err := loadAPIHeaders(options.apiHeaderEnvs)
	if err != nil {
		return err
	}
	var cases []bfcl.Case
	for _, split := range options.splits {
		loaded, err := bfcl.LoadSplit(options.dataDir, split)
		if err != nil {
			return err
		}
		fmt.Fprintf(os.Stderr, "Loaded BFCL %s: %d cases\n", split, len(loaded))
		cases = append(cases, loaded...)
	}
	if len(options.caseIDs) > 0 {
		cases, err = filterBFCLCases(cases, options.caseIDs)
		if err != nil {
			return err
		}
	}
	var sampleVersion string
	var sampleSHA256 string
	if options.sampleManifest != "" {
		cases, err = bfcl.FilterBySampleList(cases, options.sampleManifest)
		if err != nil {
			return err
		}
		sample, digest, err := bfcl.LoadSampleManifest(options.sampleManifest)
		if err != nil {
			return err
		}
		if sample.DataCommit != bfclDataCommit {
			return fmt.Errorf("BFCL sample data commit %s does not match pinned %s", sample.DataCommit, bfclDataCommit)
		}
		sampleVersion = sample.ManifestVersion
		sampleSHA256 = digest
	}
	started := time.Now().UTC()
	fmt.Fprintf(os.Stderr, "Running %d cases at concurrency %d\n", len(cases), options.concurrency)
	progress := bfclProgressReporter(time.Now())
	ctx, cancel := signalContext()
	defer cancel()
	var result bfcl.RunResult
	var runErr error
	if options.tier == "baseline" || options.tier == "enhanced" || options.tier == "finish-task-probe" {
		var generator continuation.Generator
		switch options.transport {
		case string(bfcl.TransportRWKVContinuation):
			stopMode, stopIDs, err := parseAPIStopTokens(options.apiStopTokens)
			if err != nil {
				return err
			}
			stream := options.apiStream
			client, err := rwkvlightning.New(rwkvlightning.Config{
				Endpoint:      options.apiURL,
				Model:         options.model,
				StopTokenMode: stopMode,
				StopTokenIDs:  stopIDs,
				Stream:        &stream,
				BatchWait:     options.remoteBatchWait,
				Headers:       headers,
			})
			if err != nil {
				return fmt.Errorf("initialize BFCL RWKV continuation client: %w", err)
			}
			generator = client
		case string(bfcl.TransportChatCompletionsWrapped):
			client, err := chatcompletions.New(chatcompletions.Config{
				Endpoint:                   options.apiURL,
				Model:                      options.model,
				APIKey:                     os.Getenv(options.apiKeyEnv),
				Thinking:                   chatcompletions.ThinkingMode(options.chatThinking),
				ChatTemplateEnableThinking: options.chatTemplateEnableThinking(),
				PromptMode:                 chatcompletions.PromptWrappedContinuation,
				TokenLimit:                 chatcompletions.TokenLimitField(options.chatTokenLimit),
				IncludeTopK:                options.chatIncludeTopK,
				HTTPClient:                 &http.Client{Timeout: options.caseTimeout + time.Minute},
				Headers:                    headers,
			})
			if err != nil {
				return fmt.Errorf("initialize BFCL wrapped Chat Completions client: %w", err)
			}
			generator = client
		}
		result, runErr = bfcl.RunBaseline(ctx, cases, bfcl.BaselineRunnerOptions{
			Generator:       generator,
			Model:           options.model,
			Tier:            bfcl.Tier(options.tier),
			Transport:       bfcl.Transport(options.transport),
			Concurrency:     options.concurrency,
			MaxOutputTokens: options.maxTokens,
			MaxPromptChars:  options.maxPromptChars,
			Temperature:     float32(options.temperature),
			CaseTimeout:     options.caseTimeout,
			Progress:        progress,
		})
	} else {
		client, err := chatcompletions.New(chatcompletions.Config{
			Endpoint:                   options.apiURL,
			Model:                      options.model,
			APIKey:                     os.Getenv(options.apiKeyEnv),
			Thinking:                   chatcompletions.ThinkingMode(options.chatThinking),
			ChatTemplateEnableThinking: options.chatTemplateEnableThinking(),
			PromptMode:                 chatcompletions.PromptNativeChat,
			TokenLimit:                 chatcompletions.TokenLimitField(options.chatTokenLimit),
			IncludeTopK:                options.chatIncludeTopK,
			HTTPClient:                 &http.Client{Timeout: options.caseTimeout + time.Minute},
			Headers:                    headers,
		})
		if err != nil {
			return fmt.Errorf("initialize BFCL Chat Completions client: %w", err)
		}
		result, runErr = bfcl.RunNative(ctx, cases, bfcl.RunnerOptions{
			Completer:       client,
			Model:           options.model,
			Concurrency:     options.concurrency,
			MaxOutputTokens: options.maxTokens,
			MaxPromptChars:  options.maxPromptChars,
			Temperature:     float32(options.temperature),
			CaseTimeout:     options.caseTimeout,
			Progress:        progress,
		})
	}
	if runErr != nil {
		return runErr
	}
	resultDir := filepath.Join(options.output, "result")
	if err := bfcl.WriteResults(resultDir, bfclModelDirName, result.Entries); err != nil {
		return fmt.Errorf("write BFCL results: %w", err)
	}
	manifest := bfcl.Manifest{
		SchemaVersion:    1,
		StartedAt:        started,
		RepoCommit:       repositoryCommit(),
		RepoDirty:        repositoryDirty(),
		BinarySHA256:     executableSHA256(),
		DataDir:          options.dataDir,
		DataCommit:       bfclDataCommit,
		EvaluatorVersion: bfclEvaluatorVersion,
		Model:            options.model,
		ModelDirName:     bfclModelDirName,
		Transport:        options.transport,
		Tier:             options.tier,
		RenderProtocol:   markdownRenderProtocol(options.tier),
		Concurrency:      options.concurrency,
		Sampling: bfcl.SamplingRecord{
			Greedy:               options.temperature == 0 || options.chatIncludeTopK || options.transport == string(bfcl.TransportRWKVContinuation),
			TopK:                 1,
			TopKIncluded:         options.chatIncludeTopK || options.transport == string(bfcl.TransportRWKVContinuation),
			EffectiveTemperature: float32(options.temperature),
		},
		MaxTokens:      options.maxTokens,
		MaxPromptChars: options.maxPromptChars,
		CaseTimeout:    options.caseTimeout.String(),
		Splits:         append([]string(nil), options.splits...),
		CaseIDs:        append([]string(nil), options.caseIDs...),
		Hardware:       options.hardware,
		Serving:        options.serving,
		ParserMode:     markdownParserMode(options.tier),
		SampleManifest: options.sampleManifest,
		SampleVersion:  sampleVersion,
		SampleSHA256:   sampleSHA256,
	}
	if options.tier == "enhanced" {
		manifest.RetryPrompt = bfcl.RetryPromptVersion
		manifest.RetryMax = 1
	}
	if options.transport == string(bfcl.TransportRWKVContinuation) {
		stream := options.apiStream
		manifest.APIStopTokens = options.apiStopTokens
		manifest.APIStream = &stream
		manifest.RemoteBatchWait = options.remoteBatchWait.String()
	}
	manifest.APIHeaderNames = headerNames(headers)
	if err := bfcl.WriteArtifacts(options.output, manifest, result); err != nil {
		return fmt.Errorf("write BFCL artifacts: %w", err)
	}
	fmt.Fprintf(
		os.Stderr,
		"BFCL generation complete: total=%d failed=%d parse_failed=%d repaired=%d retried=%d retry_parsed=%d skipped=%d elapsed=%s\n",
		len(result.Trace),
		result.Failed,
		result.ParseFailed,
		result.Repaired,
		result.Retried,
		result.RetryParsed,
		result.Skipped,
		result.Elapsed.Round(time.Millisecond),
	)
	if result.Failed > 0 || result.Skipped > 0 {
		return fmt.Errorf("BFCL generation completed with failed=%d skipped=%d", result.Failed, result.Skipped)
	}
	return nil
}

func parseBFCLEvalOptions(args []string) (bfclEvalOptions, error) {
	var options bfclEvalOptions
	fs := flag.NewFlagSet("bfcl-eval", flag.ContinueOnError)
	fs.StringVar(&options.model, "model", "", "remote model identifier")
	fs.StringVar(&options.tier, "tier", "adapter-health", "BFCL tier: adapter-health, baseline, enhanced, or finish-task-probe")
	fs.StringVar(&options.transport, "transport", "", "BFCL transport; defaults by tier")
	fs.StringVar(&options.apiURL, "api-url", "", "full remote inference endpoint URL")
	fs.StringVar(&options.apiKeyEnv, "api-key-env", "OPENAI_API_KEY", "environment variable containing the API key")
	fs.Var(&options.apiHeaderEnvs, "api-header-env", "repeatable HTTP_HEADER=ENV_VAR authentication mapping")
	fs.StringVar(&options.dataDir, "data-dir", "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data", "BFCL data directory")
	fs.StringVar(&options.output, "output", "", "new output directory for run, trace, result, and score artifacts")
	fs.Var(&options.splits, "split", "repeatable or comma-separated BFCL split")
	fs.Var(&options.caseIDs, "case", "repeatable BFCL case ID; omit to run full splits")
	fs.StringVar(&options.sampleManifest, "sample-manifest", "", "frozen BFCL sample manifest used to filter loaded splits")
	fs.BoolVar(&options.full, "full", false, "run complete loaded splits instead of an M2 smoke or frozen sample")
	fs.IntVar(&options.concurrency, "concurrency", 8, "number of concurrent BFCL cases")
	fs.IntVar(&options.maxTokens, "max-tokens", 1024, "maximum completion tokens per case")
	fs.IntVar(&options.maxPromptChars, "max-prompt-chars", 40000, "skip requests larger than this encoded character count")
	fs.Float64Var(&options.temperature, "temperature", 0.001, "effective temperature; 0 selects provider greedy mode")
	fs.DurationVar(&options.caseTimeout, "case-timeout", 2*time.Minute, "timeout per BFCL case")
	fs.StringVar(&options.apiStopTokens, "api-stop-tokens", "text", "rwkv_lightning stop_tokens form")
	fs.BoolVar(&options.apiStream, "api-stream", true, "stream rwkv_lightning responses over SSE")
	fs.DurationVar(&options.remoteBatchWait, "remote-batch-wait", 10*time.Millisecond, "RWKV Lightning request coalescing window")
	fs.StringVar(&options.chatThinking, "chat-thinking", string(chatcompletions.ThinkingAuto), "thinking extension: auto, disabled, or enabled")
	fs.StringVar(&options.chatTemplateThinking, "chat-template-thinking", string(chatcompletions.ThinkingAuto), "chat template thinking: auto, disabled, or enabled")
	fs.StringVar(&options.chatTokenLimit, "chat-token-limit-field", string(chatcompletions.TokenLimitMaxTokens), "token field: max-completion-tokens or max-tokens")
	fs.BoolVar(&options.chatIncludeTopK, "chat-include-top-k", false, "include provider-specific top_k in Chat Completions requests")
	fs.StringVar(&options.hardware, "hardware", "", "serving hardware recorded in run.json")
	fs.StringVar(&options.serving, "serving", "", "serving configuration recorded in run.json")
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	options.model = strings.TrimSpace(options.model)
	options.tier = strings.TrimSpace(options.tier)
	options.transport = strings.TrimSpace(options.transport)
	options.apiURL = strings.TrimSpace(options.apiURL)
	options.output = strings.TrimSpace(options.output)
	options.sampleManifest = strings.TrimSpace(options.sampleManifest)
	if options.model == "" || options.apiURL == "" || options.output == "" {
		fs.Usage()
		return options, fmt.Errorf("bfcl-eval requires --model, --api-url, and --output")
	}
	if options.tier != "adapter-health" && options.tier != "baseline" && options.tier != "enhanced" && options.tier != "finish-task-probe" {
		return options, fmt.Errorf("unsupported BFCL tier %q", options.tier)
	}
	if options.transport == "" {
		options.transport = "chat-completions-native-fc"
		if options.tier == "baseline" || options.tier == "enhanced" || options.tier == "finish-task-probe" {
			options.transport = string(bfcl.TransportRWKVContinuation)
		}
	}
	if options.tier == "adapter-health" && options.transport != "chat-completions-native-fc" {
		return options, fmt.Errorf("BFCL adapter-health requires chat-completions-native-fc transport")
	}
	if (options.tier == "baseline" || options.tier == "enhanced" || options.tier == "finish-task-probe") && options.transport != string(bfcl.TransportRWKVContinuation) &&
		options.transport != string(bfcl.TransportChatCompletionsWrapped) {
		return options, fmt.Errorf("unsupported BFCL baseline transport %q", options.transport)
	}
	options.splits = splitFlagValues(options.splits)
	options.caseIDs = splitFlagValues(options.caseIDs)
	if len(options.splits) == 0 {
		return options, fmt.Errorf("bfcl-eval requires at least one --split")
	}
	if options.concurrency <= 0 || options.maxTokens <= 0 || options.maxPromptChars <= 0 ||
		options.temperature < 0 || options.caseTimeout <= 0 || options.remoteBatchWait < 0 {
		return options, fmt.Errorf("invalid BFCL limits")
	}
	if options.temperature == 0 && options.transport == string(bfcl.TransportRWKVContinuation) {
		return options, fmt.Errorf("--temperature 0 requires a Chat Completions transport")
	}
	if options.chatIncludeTopK && options.transport == string(bfcl.TransportRWKVContinuation) {
		return options, fmt.Errorf("--chat-include-top-k requires a Chat Completions transport")
	}
	if (options.tier == "baseline" || options.tier == "enhanced") && (len(options.splits) != 1 || options.splits[0] != "simple_python") {
		if options.sampleManifest == "" && !options.full && len(options.caseIDs) == 0 {
			return options, fmt.Errorf("BFCL M2 baseline requires exactly --split simple_python unless --sample-manifest is set")
		}
	}
	if options.tier == "finish-task-probe" {
		for _, split := range options.splits {
			if split != "irrelevance" && split != "live_irrelevance" {
				return options, fmt.Errorf("BFCL finish-task-probe only supports irrelevance and live_irrelevance, got %q", split)
			}
		}
	}
	if options.full && (options.sampleManifest != "" || len(options.caseIDs) > 0) {
		return options, fmt.Errorf("--full cannot be combined with --sample-manifest or --case")
	}
	if options.sampleManifest != "" && len(options.caseIDs) > 0 {
		return options, fmt.Errorf("--sample-manifest and --case cannot be combined")
	}
	thinking, err := chatcompletions.ParseThinkingMode(options.chatThinking)
	if err != nil {
		return options, err
	}
	options.chatThinking = string(thinking)
	chatTemplateThinking, err := chatcompletions.ParseThinkingMode(options.chatTemplateThinking)
	if err != nil {
		return options, err
	}
	options.chatTemplateThinking = string(chatTemplateThinking)
	if chatTemplateThinking != chatcompletions.ThinkingAuto &&
		options.transport == string(bfcl.TransportRWKVContinuation) {
		return options, fmt.Errorf("--chat-template-thinking requires a Chat Completions transport")
	}
	tokenLimit, err := chatcompletions.ParseTokenLimitField(options.chatTokenLimit)
	if err != nil {
		return options, err
	}
	options.chatTokenLimit = string(tokenLimit)
	return options, nil
}

func markdownRenderProtocol(tier string) string {
	if tier == "finish-task-probe" {
		return bfcl.RenderProtocolFinishTaskV1
	}
	if tier == "baseline" || tier == "enhanced" {
		return bfcl.RenderProtocolAnchorV1
	}
	return ""
}

func markdownParserMode(tier string) string {
	if tier == "baseline" || tier == "finish-task-probe" {
		return string(bfcl.ParserStrict)
	}
	if tier == "enhanced" {
		return string(bfcl.ParserRWKVWireCompatV1)
	}
	return ""
}

func headerNames(headers http.Header) []string {
	if len(headers) == 0 {
		return nil
	}
	names := make([]string, 0, len(headers))
	for name := range headers {
		names = append(names, name)
	}
	sort.Strings(names)
	return names
}

func repositoryCommit() string {
	output, err := exec.Command("git", "rev-parse", "HEAD").Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(output))
}

func repositoryDirty() bool {
	output, err := exec.Command("git", "status", "--porcelain").Output()
	return err != nil || len(output) > 0
}

func executableSHA256() string {
	path, err := os.Executable()
	if err != nil {
		return ""
	}
	encoded, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	digest := sha256.Sum256(encoded)
	return hex.EncodeToString(digest[:])
}

func bfclProgressReporter(started time.Time) func(completed, total int) {
	var mu sync.Mutex
	return func(completed, total int) {
		if completed%100 != 0 && completed != total {
			return
		}
		mu.Lock()
		defer mu.Unlock()
		elapsed := time.Since(started)
		rate := float64(completed) / elapsed.Seconds()
		remaining := time.Duration(0)
		if rate > 0 {
			remaining = time.Duration(float64(total-completed)/rate) * time.Second
		}
		fmt.Fprintf(os.Stderr, "BFCL progress: completed=%d/%d rate=%.2f cases/s eta=%s\n", completed, total, rate, remaining.Round(time.Second))
	}
}

func filterBFCLCases(cases []bfcl.Case, ids []string) ([]bfcl.Case, error) {
	wanted := make(map[string]struct{}, len(ids))
	for _, id := range ids {
		wanted[id] = struct{}{}
	}
	filtered := make([]bfcl.Case, 0, len(ids))
	for _, entry := range cases {
		if _, ok := wanted[entry.ID]; ok {
			filtered = append(filtered, entry)
			delete(wanted, entry.ID)
		}
	}
	if len(wanted) > 0 {
		missing := make([]string, 0, len(wanted))
		for id := range wanted {
			missing = append(missing, id)
		}
		return nil, fmt.Errorf("BFCL case IDs not found: %s", strings.Join(missing, ", "))
	}
	return filtered, nil
}

func splitFlagValues(values []string) stringListFlag {
	var result stringListFlag
	seen := make(map[string]struct{})
	for _, value := range values {
		for _, split := range strings.Split(value, ",") {
			split = strings.TrimSpace(split)
			if split == "" {
				continue
			}
			if _, exists := seen[split]; exists {
				continue
			}
			seen[split] = struct{}{}
			result = append(result, split)
		}
	}
	return result
}

func signalContext() (context.Context, context.CancelFunc) {
	return signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
}
