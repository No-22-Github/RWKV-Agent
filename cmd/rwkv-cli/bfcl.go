package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"
	"time"

	"github.com/no22/RWKV-Agent/internal/bfcl"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
)

const (
	bfclDataCommit       = "6ea57973c7a6097fd7c5915698c54c17c5b1b6c8"
	bfclEvaluatorVersion = "2026.3.23"
	bfclModelDirName     = "rwkv-agent-bfcl-ab-v1"
)

type bfclEvalOptions struct {
	model          string
	apiURL         string
	apiKeyEnv      string
	apiHeaderEnvs  stringListFlag
	dataDir        string
	output         string
	splits         stringListFlag
	caseIDs        stringListFlag
	concurrency    int
	maxTokens      int
	maxPromptChars int
	temperature    float64
	caseTimeout    time.Duration
	chatThinking   string
	chatTokenLimit string
	hardware       string
	serving        string
}

func runBFCLEval(args []string) error {
	options, err := parseBFCLEvalOptions(args)
	if err != nil {
		return err
	}
	if _, err := os.Stat(options.output); err == nil {
		return fmt.Errorf("BFCL output already exists: %s", options.output)
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	headers, err := loadAPIHeaders(options.apiHeaderEnvs)
	if err != nil {
		return err
	}
	client, err := chatcompletions.New(chatcompletions.Config{
		Endpoint:   options.apiURL,
		Model:      options.model,
		APIKey:     os.Getenv(options.apiKeyEnv),
		Thinking:   chatcompletions.ThinkingMode(options.chatThinking),
		PromptMode: chatcompletions.PromptNativeChat,
		TokenLimit: chatcompletions.TokenLimitField(options.chatTokenLimit),
		Headers:    headers,
	})
	if err != nil {
		return fmt.Errorf("initialize BFCL Chat Completions client: %w", err)
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
	started := time.Now().UTC()
	fmt.Fprintf(os.Stderr, "Running %d cases at concurrency %d\n", len(cases), options.concurrency)
	ctx, cancel := signalContext()
	defer cancel()
	result, err := bfcl.RunNative(ctx, cases, bfcl.RunnerOptions{
		Completer:       client,
		Model:           options.model,
		Concurrency:     options.concurrency,
		MaxOutputTokens: options.maxTokens,
		MaxPromptChars:  options.maxPromptChars,
		Temperature:     float32(options.temperature),
		CaseTimeout:     options.caseTimeout,
	})
	if err != nil {
		return err
	}
	resultDir := filepath.Join(options.output, "result")
	if err := bfcl.WriteResults(resultDir, bfclModelDirName, result.Entries); err != nil {
		return fmt.Errorf("write BFCL results: %w", err)
	}
	if err := bfcl.WriteArtifacts(options.output, bfcl.Manifest{
		SchemaVersion:    1,
		StartedAt:        started,
		DataDir:          options.dataDir,
		DataCommit:       bfclDataCommit,
		EvaluatorVersion: bfclEvaluatorVersion,
		Model:            options.model,
		ModelDirName:     bfclModelDirName,
		Transport:        "chat-completions-native-fc",
		Tier:             "adapter-health",
		Concurrency:      options.concurrency,
		Sampling: bfcl.SamplingRecord{
			Greedy:               true,
			TopK:                 1,
			EffectiveTemperature: float32(options.temperature),
		},
		MaxTokens:      options.maxTokens,
		MaxPromptChars: options.maxPromptChars,
		CaseTimeout:    options.caseTimeout.String(),
		Splits:         append([]string(nil), options.splits...),
		CaseIDs:        append([]string(nil), options.caseIDs...),
		Hardware:       options.hardware,
		Serving:        options.serving,
	}, result); err != nil {
		return fmt.Errorf("write BFCL artifacts: %w", err)
	}
	fmt.Fprintf(
		os.Stderr,
		"BFCL generation complete: total=%d failed=%d skipped=%d elapsed=%s\n",
		len(result.Trace),
		result.Failed,
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
	fs.StringVar(&options.model, "model", "", "remote Chat Completions model identifier")
	fs.StringVar(&options.apiURL, "api-url", "", "full Chat Completions endpoint URL")
	fs.StringVar(&options.apiKeyEnv, "api-key-env", "OPENAI_API_KEY", "environment variable containing the API key")
	fs.Var(&options.apiHeaderEnvs, "api-header-env", "repeatable HTTP_HEADER=ENV_VAR authentication mapping")
	fs.StringVar(&options.dataDir, "data-dir", "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data", "BFCL data directory")
	fs.StringVar(&options.output, "output", "", "new output directory for run, trace, result, and score artifacts")
	fs.Var(&options.splits, "split", "repeatable or comma-separated BFCL split")
	fs.Var(&options.caseIDs, "case", "repeatable BFCL case ID; omit to run full splits")
	fs.IntVar(&options.concurrency, "concurrency", 8, "number of concurrent BFCL cases")
	fs.IntVar(&options.maxTokens, "max-tokens", 1024, "maximum completion tokens per case")
	fs.IntVar(&options.maxPromptChars, "max-prompt-chars", 40000, "skip requests larger than this encoded character count")
	fs.Float64Var(&options.temperature, "temperature", 0.001, "effective positive greedy temperature")
	fs.DurationVar(&options.caseTimeout, "case-timeout", 2*time.Minute, "timeout per BFCL case")
	fs.StringVar(&options.chatThinking, "chat-thinking", string(chatcompletions.ThinkingAuto), "thinking extension: auto, disabled, or enabled")
	fs.StringVar(&options.chatTokenLimit, "chat-token-limit-field", string(chatcompletions.TokenLimitMaxTokens), "token field: max-completion-tokens or max-tokens")
	fs.StringVar(&options.hardware, "hardware", "", "serving hardware recorded in run.json")
	fs.StringVar(&options.serving, "serving", "", "serving configuration recorded in run.json")
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	options.model = strings.TrimSpace(options.model)
	options.apiURL = strings.TrimSpace(options.apiURL)
	options.output = strings.TrimSpace(options.output)
	if options.model == "" || options.apiURL == "" || options.output == "" {
		fs.Usage()
		return options, fmt.Errorf("bfcl-eval requires --model, --api-url, and --output")
	}
	options.splits = splitFlagValues(options.splits)
	if len(options.splits) == 0 {
		return options, fmt.Errorf("bfcl-eval requires at least one --split")
	}
	if options.concurrency <= 0 || options.maxTokens <= 0 || options.maxPromptChars <= 0 ||
		options.temperature <= 0 || options.caseTimeout <= 0 {
		return options, fmt.Errorf("invalid BFCL limits")
	}
	thinking, err := chatcompletions.ParseThinkingMode(options.chatThinking)
	if err != nil {
		return options, err
	}
	options.chatThinking = string(thinking)
	tokenLimit, err := chatcompletions.ParseTokenLimitField(options.chatTokenLimit)
	if err != nil {
		return options, err
	}
	options.chatTokenLimit = string(tokenLimit)
	return options, nil
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
