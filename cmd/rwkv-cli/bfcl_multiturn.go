package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/bfcl"
	"github.com/no22/RWKV-Agent/internal/bfcl/pysidecar"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

const bfclSidecarProtocolV1 = "bfcl-python-sidecar-v1"

type bfclMultiTurnOptions struct {
	model                    string
	tier                     string
	transport                string
	apiURL                   string
	apiKeyEnv                string
	apiHeaderEnvs            stringListFlag
	dataDir                  string
	output                   string
	split                    string
	caseID                   string
	python                   string
	sidecarScript            string
	maxTokens                int
	routeMaxTokens           int
	maxPromptChars           int
	maxSteps                 int
	routeRetries             int
	duplicateReplayLimit     int
	duplicateRescueThreshold int
	sameToolRescueLimit      int
	temperature              float64
	caseTimeout              time.Duration
	apiStopTokens            string
	apiStream                bool
	remoteBatchWait          time.Duration
	chatThinking             string
	chatTemplateThinking     string
	chatTokenLimit           string
	chatIncludeTopK          bool
}

func runBFCLMultiTurn(args []string) error {
	options, err := parseBFCLMultiTurnOptions(args)
	if err != nil {
		return err
	}
	if _, err := os.Stat(options.output); err == nil {
		return fmt.Errorf("BFCL multi-turn output already exists: %s", options.output)
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	cases, err := bfcl.LoadMultiTurnSplit(options.dataDir, options.split)
	if err != nil {
		return err
	}
	var entry bfcl.MultiTurnCase
	found := false
	for _, candidate := range cases {
		if candidate.ID == options.caseID {
			entry = candidate
			found = true
			break
		}
	}
	if !found {
		return fmt.Errorf("BFCL multi-turn case %q was not found in %s", options.caseID, options.split)
	}
	catalog, err := bfcl.LoadMultiTurnCatalog(options.dataDir, entry)
	if err != nil {
		return err
	}
	headers, err := loadAPIHeaders(options.apiHeaderEnvs)
	if err != nil {
		return err
	}
	generator, err := bfclMultiTurnGenerator(options, headers)
	if err != nil {
		return err
	}
	repoRoot, err := os.Getwd()
	if err != nil {
		return err
	}
	sidecar, err := pysidecar.Start(pysidecar.Config{Python: options.python, Script: options.sidecarScript, WorkingDir: repoRoot})
	if err != nil {
		return err
	}
	ctx, cancel := signalContext()
	defer cancel()
	sessionID, err := sidecar.NewSession(ctx, pysidecar.SessionOptions{
		ID: options.caseID + "-" + options.tier, InitialConfig: entry.InitialConfig,
		InvolvedClasses: entry.InvolvedClasses, LongContext: strings.Contains(options.split, "long_context"), TestEntryID: entry.ID,
	})
	if err != nil {
		sidecar.Close()
		return err
	}
	trace := bfcl.RunMultiTurnCase(ctx, entry, catalog, bfcl.MultiTurnRunnerOptions{
		Generator: generator, Executor: sidecar, SessionID: sessionID, Model: options.model,
		Tier: bfcl.Tier(options.tier), Transport: bfcl.Transport(options.transport),
		MaxOutputTokens: options.maxTokens, RouteMaxTokens: options.routeMaxTokens,
		MaxPromptChars: options.maxPromptChars, MaxSteps: options.maxSteps, RouteRetries: options.routeRetries,
		DuplicateReplayLimit: options.duplicateReplayLimit, DuplicateRescueThreshold: options.duplicateRescueThreshold,
		SameToolRescueLimit: options.sameToolRescueLimit, Temperature: float32(options.temperature), CaseTimeout: options.caseTimeout,
	})
	closeSessionErr := sidecar.CloseSession(context.Background(), sessionID)
	closeErr := sidecar.Close()
	if closeSessionErr != nil {
		return closeSessionErr
	}
	if closeErr != nil {
		return closeErr
	}
	if err := bfcl.WriteMultiTurnResult(filepath.Join(options.output, "result"), bfclModelDirName, trace); err != nil {
		return err
	}
	stream := options.apiStream
	manifest := bfcl.MultiTurnManifest{
		SchemaVersion: 1, DataCommit: bfclDataCommit, EvaluatorVersion: bfclEvaluatorVersion,
		Model: options.model, ModelDirName: bfclModelDirName, Tier: options.tier, Transport: options.transport,
		RenderProtocol: bfcl.MultiTurnRenderProtocolV1, ParserMode: multiTurnParserMode(options.tier), SidecarProtocol: bfclSidecarProtocolV1,
		Split: options.split, CaseID: options.caseID, MaxSteps: options.maxSteps, MaxPromptChars: options.maxPromptChars,
		MaxTokens: options.maxTokens, RouteMaxTokens: options.routeMaxTokens, RouteRetries: options.routeRetries,
		DuplicateReplayLimit: options.duplicateReplayLimit, DuplicateRescueThreshold: options.duplicateRescueThreshold,
		SameToolRescueLimit: options.sameToolRescueLimit, Sampling: bfcl.SamplingRecord{
			Greedy: options.temperature == 0 || options.transport == string(bfcl.TransportRWKVContinuation), TopK: 1,
			TopKIncluded: options.chatIncludeTopK || options.transport == string(bfcl.TransportRWKVContinuation), EffectiveTemperature: float32(options.temperature),
		}, RepoCommit: repositoryCommit(), RepoDirty: repositoryDirty(), BinarySHA256: executableSHA256(), APIHeaderNames: headerNames(headers),
	}
	if options.transport == string(bfcl.TransportRWKVContinuation) {
		manifest.APIStopTokens = options.apiStopTokens
		manifest.APIStream = &stream
		manifest.RemoteBatchWait = options.remoteBatchWait.String()
	}
	if err := bfcl.WriteMultiTurnArtifacts(options.output, manifest, trace); err != nil {
		return err
	}
	fmt.Fprintf(os.Stderr, "BFCL multi-turn complete: case=%s tier=%s turns=%d model_calls=%d route_calls=%d max_prompt_bytes=%d error=%q\n", trace.ID, trace.Tier, len(trace.Turns), trace.ModelCalls, trace.RouteCalls, trace.MaxPromptBytes, trace.Error)
	if trace.Error != "" {
		return fmt.Errorf("BFCL multi-turn run failed: %s", trace.Error)
	}
	return nil
}

func bfclMultiTurnGenerator(options bfclMultiTurnOptions, headers http.Header) (continuation.Generator, error) {
	switch options.transport {
	case string(bfcl.TransportRWKVContinuation):
		stopMode, stopIDs, err := parseAPIStopTokens(options.apiStopTokens)
		if err != nil {
			return nil, err
		}
		stream := options.apiStream
		return rwkvlightning.New(rwkvlightning.Config{Endpoint: options.apiURL, Model: options.model, StopTokenMode: stopMode, StopTokenIDs: stopIDs, Stream: &stream, BatchWait: options.remoteBatchWait, Headers: headers})
	case string(bfcl.TransportChatCompletionsWrapped):
		thinking, err := chatcompletions.ParseThinkingMode(options.chatThinking)
		if err != nil {
			return nil, err
		}
		templateThinking, err := chatcompletions.ParseThinkingMode(options.chatTemplateThinking)
		if err != nil {
			return nil, err
		}
		var enableThinking *bool
		if templateThinking != chatcompletions.ThinkingAuto {
			value := templateThinking == chatcompletions.ThinkingEnabled
			enableThinking = &value
		}
		return chatcompletions.New(chatcompletions.Config{
			Endpoint: options.apiURL, Model: options.model, APIKey: os.Getenv(options.apiKeyEnv), Thinking: thinking,
			ChatTemplateEnableThinking: enableThinking, PromptMode: chatcompletions.PromptWrappedContinuation,
			TokenLimit: chatcompletions.TokenLimitField(options.chatTokenLimit), IncludeTopK: options.chatIncludeTopK,
			HTTPClient: &http.Client{Timeout: options.caseTimeout + time.Minute}, Headers: headers,
		})
	default:
		return nil, fmt.Errorf("unsupported BFCL multi-turn transport %q", options.transport)
	}
}

func parseBFCLMultiTurnOptions(args []string) (bfclMultiTurnOptions, error) {
	var options bfclMultiTurnOptions
	fs := flag.NewFlagSet("bfcl-mt-eval", flag.ContinueOnError)
	fs.StringVar(&options.model, "model", "", "remote model identifier")
	fs.StringVar(&options.tier, "tier", "baseline", "multi-turn tier: baseline or enhanced")
	fs.StringVar(&options.transport, "transport", string(bfcl.TransportRWKVContinuation), "continuation transport")
	fs.StringVar(&options.apiURL, "api-url", "", "full remote inference endpoint URL")
	fs.StringVar(&options.apiKeyEnv, "api-key-env", "OPENAI_API_KEY", "environment variable containing API key")
	fs.Var(&options.apiHeaderEnvs, "api-header-env", "repeatable HTTP_HEADER=ENV_VAR authentication mapping")
	fs.StringVar(&options.dataDir, "data-dir", "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data", "BFCL data directory")
	fs.StringVar(&options.output, "output", "", "new output directory")
	fs.StringVar(&options.split, "split", "multi_turn_base", "BFCL multi-turn split")
	fs.StringVar(&options.caseID, "case", "multi_turn_base_0", "single BFCL multi-turn case ID")
	fs.StringVar(&options.python, "python", ".venv/bin/python", "Python executable with pinned bfcl-eval")
	fs.StringVar(&options.sidecarScript, "sidecar-script", "internal/bfcl/pysidecar/server.py", "BFCL execution sidecar script")
	fs.IntVar(&options.maxTokens, "max-tokens", 1024, "maximum tokens per agent step")
	fs.IntVar(&options.routeMaxTokens, "route-max-tokens", 48, "maximum tokens per route call")
	fs.IntVar(&options.maxPromptChars, "max-prompt-chars", 43008, "maximum encoded prompt characters")
	fs.IntVar(&options.maxSteps, "max-steps", 20, "maximum steps per turn")
	fs.IntVar(&options.routeRetries, "route-retries", 1, "route/protocol correction retries")
	fs.IntVar(&options.duplicateReplayLimit, "duplicate-replay-limit", 2, "allowed identical calls before rejection")
	fs.IntVar(&options.duplicateRescueThreshold, "duplicate-rescue-threshold", 3, "duplicate streak that ends the turn")
	fs.IntVar(&options.sameToolRescueLimit, "same-tool-rescue-limit", 8, "same-tool streak that ends the turn")
	fs.Float64Var(&options.temperature, "temperature", 0.001, "effective temperature")
	fs.DurationVar(&options.caseTimeout, "case-timeout", 10*time.Minute, "whole-case timeout")
	fs.StringVar(&options.apiStopTokens, "api-stop-tokens", "text", "rwkv_lightning stop token form")
	fs.BoolVar(&options.apiStream, "api-stream", true, "stream rwkv_lightning responses")
	fs.DurationVar(&options.remoteBatchWait, "remote-batch-wait", 0, "RWKV request coalescing window")
	fs.StringVar(&options.chatThinking, "chat-thinking", string(chatcompletions.ThinkingAuto), "Chat Completions thinking mode")
	fs.StringVar(&options.chatTemplateThinking, "chat-template-thinking", string(chatcompletions.ThinkingAuto), "chat template thinking mode")
	fs.StringVar(&options.chatTokenLimit, "chat-token-limit-field", string(chatcompletions.TokenLimitMaxTokens), "Chat Completions token limit field")
	fs.BoolVar(&options.chatIncludeTopK, "chat-include-top-k", false, "include provider top_k")
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	options.model, options.apiURL, options.output = strings.TrimSpace(options.model), strings.TrimSpace(options.apiURL), strings.TrimSpace(options.output)
	if options.model == "" || options.apiURL == "" || options.output == "" || options.caseID == "" {
		return options, fmt.Errorf("bfcl-mt-eval requires --model, --api-url, --case, and --output")
	}
	if options.tier != "baseline" && options.tier != "enhanced" {
		return options, fmt.Errorf("unsupported BFCL multi-turn tier %q", options.tier)
	}
	if options.transport != string(bfcl.TransportRWKVContinuation) && options.transport != string(bfcl.TransportChatCompletionsWrapped) {
		return options, fmt.Errorf("unsupported BFCL multi-turn transport %q", options.transport)
	}
	if !strings.HasPrefix(options.split, "multi_turn_") || !strings.HasPrefix(options.caseID, options.split+"_") {
		return options, fmt.Errorf("BFCL multi-turn split/case mismatch")
	}
	if options.maxTokens <= 0 || options.routeMaxTokens <= 0 || options.maxPromptChars <= 0 || options.maxSteps <= 0 || options.routeRetries < 0 || options.caseTimeout <= 0 || options.temperature < 0 {
		return options, fmt.Errorf("invalid BFCL multi-turn limits")
	}
	if options.temperature == 0 && options.transport == string(bfcl.TransportRWKVContinuation) {
		return options, fmt.Errorf("--temperature 0 requires Chat Completions transport")
	}
	return options, nil
}

func multiTurnParserMode(tier string) string {
	if tier == "enhanced" {
		return string(bfcl.ParserRWKVWireCompatV1)
	}
	return string(bfcl.ParserStrict)
}
