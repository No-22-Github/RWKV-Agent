package main

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"net/http"
	"net/textproto"
	"os"
	"os/signal"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
	"syscall"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/agent"
	agenteval "github.com/no22/RWKV-Agent/internal/agent/eval"
	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
	localcontinuation "github.com/no22/RWKV-Agent/internal/continuation/local"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
	rwkvbackend "github.com/no22/RWKV-Agent/internal/inference/backend/rwkvmobile"
	"github.com/no22/RWKV-Agent/internal/native/converter"
	"github.com/no22/RWKV-Agent/internal/terminal"
	agenttui "github.com/no22/RWKV-Agent/internal/tui/agent"
	concurrenttui "github.com/no22/RWKV-Agent/internal/tui/concurrent"
)

type runOptions struct {
	modelPath                string
	backend                  string
	provider                 string
	tokenizer                string
	sessionPath              string
	prompt                   string
	maxTokens                int
	decisionMaxTokens        int
	routeMaxTokens           int
	routeMaxTokensExplicit   bool
	routeStage               bool
	tracePromptBytes         int
	temperature              float64
	topK                     int
	topP                     float64
	presencePenalty          float64
	frequencyPenalty         float64
	penaltyDecay             float64
	thinkingMode             string
	thinkingExplicit         bool
	reasoning                bool
	reasoningExplicit        bool
	fewShot                  bool
	autosave                 bool
	nativeState              string
	concurrency              int
	concurrentPrompt         string
	ui                       string
	workspace                string
	maxSteps                 int
	completion               string
	apiURL                   string
	apiKeyEnv                string
	chatThinking             string
	chatPromptMode           string
	chatPromptExplicit       bool
	chatTokenLimit           string
	apiPasswordEnv           string
	apiStopTokens            string
	apiStream                bool
	apiHeaderEnvs            stringListFlag
	evalSuite                string
	evalSuiteExplicit        bool
	evalCasesPath            string
	evalOutput               string
	evalCaseIDs              stringListFlag
	evalCaseTimeout          time.Duration
	evalCaseParallelism      int
	evalFileToolForm         string
	evalSubagentFixture      string
	evalWebFixture           string
	primitiveProfile         string
	duplicateReplayLimit     int
	duplicateRescueThreshold int
	sameToolRescueLimit      int
	sameToolRescueExplicit   bool
	agentProtocol            string
	progressiveTools         bool
	progressiveToolsExplicit bool
	semanticNoTool           bool
	semanticNoToolExplicit   bool
	decisionFakeThink        bool
	compressFetch            bool
	noToolGate               string
	answerStageLead          int
	fetchBudgetTokens        int
	subagentRawFeedback      bool
	closedFakeThink          bool
	deepToolAnchor           bool
	deepToolAnchorExplicit   bool
	enableWeb                bool
	braveAPIKeyEnv           string
	braveEndpoint            string
	tavilyAPIKeyEnv          string
	tavilyEndpoint           string
	enableSubagents          bool
	maxActiveBatch           int
	remoteBatchWait          time.Duration
	subagentMaxParallel      int
	subagentMaxSteps         int
	subagentTimeout          time.Duration
}

type stringListFlag []string

func (values *stringListFlag) String() string {
	return strings.Join(*values, ",")
}

func (values *stringListFlag) Set(value string) error {
	*values = append(*values, value)
	return nil
}

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	var err error
	switch os.Args[1] {
	case "run":
		err = run(os.Args[2:])
	case "agent":
		err = runAgent(os.Args[2:])
	case "agent-eval":
		err = runAgentEval(os.Args[2:])
	case "bfcl-eval":
		err = runBFCLEval(os.Args[2:])
	case "bfcl-mt-eval":
		err = runBFCLMultiTurn(os.Args[2:])
	case "bfcl-reparse":
		err = runBFCLReparse(os.Args[2:])
	case "bfcl-sample":
		err = runBFCLSample(os.Args[2:])
	case "bfcl-sampling-diagnostic":
		err = runBFCLSamplingDiagnostic(os.Args[2:])
	case "concurrent":
		err = runConcurrent(os.Args[2:])
	case "bench":
		err = runConcurrent(append(os.Args[2:], "--ui", "plain"))
	case "convert":
		err = convertModel(os.Args[2:])
	default:
		usage()
		os.Exit(2)
	}
	if errors.Is(err, flag.ErrHelp) {
		return
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, `Usage:
  rwkv-cli convert --input <RWKV .pth> --output <MLX model directory>
  rwkv-cli run --model <RWKV .pth or MLX directory> [--prompt <text> | --session <bundle>]
  rwkv-cli agent --model <path or remote model ID> [--prompt <task>] [--ui auto|tui|plain]
  rwkv-cli agent-eval --model <path or remote model ID> [--suite boundary|smoke|assistant|bfcl-product|primitive-orig30|primitive-feedback30] [--primitive-profile upstream-compatible|go-native] [--output <directory>]
  rwkv-cli bfcl-eval --model <remote model ID> --api-url <inference URL> --tier <adapter-health|baseline|enhanced|finish-task-probe> [--transport <name>] --split <name> --output <directory>
  rwkv-cli bfcl-mt-eval --model <remote model ID> --api-url <inference URL> --tier <baseline|enhanced> --case multi_turn_base_0 --output <directory>
  rwkv-cli bfcl-reparse --source <BFCL run directory> --parser rwkv-wire-compat-v1 --output <directory>
  rwkv-cli bfcl-sample [--output configs/bfcl-sample-v1.json | --verify configs/bfcl-sample-v1.json]
  rwkv-cli bfcl-sampling-diagnostic --score <complete Qwen enhanced score directory>
  rwkv-cli concurrent --model <RWKV .pth or MLX directory> [--concurrency 1..8] [--ui auto|tui|plain]
  rwkv-cli bench --model <RWKV .pth or MLX directory> [--concurrency 1..8]`)
}

func convertModel(args []string) error {
	fs := flag.NewFlagSet("convert", flag.ContinueOnError)
	input := fs.String("input", "", "official RWKV PyTorch .pth checkpoint")
	output := fs.String("output", "", "destination MLX model directory")
	tokenizer := fs.String("tokenizer", "", "RWKV World tokenizer vocabulary")
	precision := fs.String("precision", "bf16", "output precision: bf16, fp16, or fp32")
	overwrite := fs.Bool("overwrite", false, "atomically replace an existing output directory")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *input == "" || *output == "" {
		fs.Usage()
		return errors.New("convert requires --input and --output")
	}
	if *tokenizer == "" {
		var err error
		*tokenizer, err = bundledTokenizerPath()
		if err != nil {
			return fmt.Errorf("%w; pass --tokenizer explicitly", err)
		}
	}
	if !converter.Available() {
		return errors.New("native converter is not present in this build; run ./scripts/build-macos.sh")
	}
	if err := converter.Convert(converter.Options{
		InputPath:     *input,
		OutputPath:    *output,
		TokenizerPath: *tokenizer,
		Precision:     *precision,
		Overwrite:     *overwrite,
	}); err != nil {
		return fmt.Errorf("convert model: %w", err)
	}
	return nil
}

func bundledTokenizerPath() (string, error) {
	const filename = "rwkv_vocab_v20230424.txt"
	candidates := make([]string, 0, 2)
	if executable, err := os.Executable(); err == nil {
		candidates = append(candidates, filepath.Join(filepath.Dir(executable), "assets", filename))
	}
	candidates = append(candidates, filepath.Join("third_party", "rwkv-mobile", "assets", filename))
	for _, candidate := range candidates {
		info, err := os.Stat(candidate)
		if err == nil && !info.IsDir() {
			return filepath.Abs(candidate)
		}
	}
	return "", fmt.Errorf("bundled tokenizer %q was not found", filename)
}

func parseRunOptions(name string, args []string) (runOptions, error) {
	var options runOptions
	fs := flag.NewFlagSet(name, flag.ContinueOnError)
	agentMode := name == "agent" || name == "agent-eval"
	defaultTopK := 128
	defaultTopP := 0.5
	defaultPresencePenalty := 2.0
	defaultFrequencyPenalty := 0.1
	defaultPenaltyDecay := 0.99
	defaultMaxTokens := 256
	if agentMode {
		defaultTopK = 1
		defaultTopP = 1
		defaultPresencePenalty = 0
		defaultFrequencyPenalty = 0
		defaultPenaltyDecay = 1
		defaultMaxTokens = 1024
	}
	fs.StringVar(&options.modelPath, "model", "", "local model path or remote model identifier")
	fs.StringVar(&options.backend, "backend", "auto", "inference backend: auto or rwkvmobile")
	fs.StringVar(&options.provider, "provider", "auto", "native provider: auto or mlx")
	fs.StringVar(&options.tokenizer, "tokenizer", "", "RWKV World tokenizer; bundled automatically for .pth")
	fs.IntVar(&options.maxTokens, "max-tokens", defaultMaxTokens, "maximum generated tokens")
	fs.Float64Var(&options.temperature, "temperature", 1, "sampling temperature")
	fs.IntVar(&options.topK, "top-k", defaultTopK, "top-k sampling cutoff")
	fs.Float64Var(&options.topP, "top-p", defaultTopP, "top-p sampling cutoff")
	fs.Float64Var(&options.presencePenalty, "presence-penalty", defaultPresencePenalty, "RWKV presence penalty")
	fs.Float64Var(&options.frequencyPenalty, "frequency-penalty", defaultFrequencyPenalty, "RWKV frequency penalty")
	fs.Float64Var(&options.penaltyDecay, "penalty-decay", defaultPenaltyDecay, "RWKV repetition-penalty decay")
	fs.StringVar(&options.thinkingMode, "thinking", string(inference.ThinkingOff), "thinking mode: off, fast, or full")
	fs.BoolVar(&options.reasoning, "reasoning", false, "deprecated alias for --thinking=fast")
	fs.StringVar(&options.nativeState, "native-state", "auto", "native State mode: auto, off, or required")
	switch name {
	case "run":
		fs.StringVar(&options.sessionPath, "session", "", "session bundle path")
		fs.StringVar(&options.prompt, "prompt", "", "single-turn prompt; omit for the REPL")
		fs.BoolVar(&options.autosave, "autosave", false, "save the session after each committed turn")
	case "agent", "agent-eval":
		routeMaxTokens := 16
		if name == "agent" {
			routeMaxTokens = 48
		}
		fs.IntVar(&options.maxSteps, "max-steps", 6, "maximum model steps including protocol retries")
		// 0 means "let the harness pick": the fenced-JSON profile needs ~96 while
		// the XML envelope reasons first and needs ~512. See runner.go.
		fs.IntVar(&options.decisionMaxTokens, "decision-max-tokens", 0, "maximum generated tokens for tool selection; 0 uses the per-protocol default")
		fs.IntVar(&options.routeMaxTokens, "route-max-tokens", routeMaxTokens, "maximum generated tokens for capability routing")
		fs.BoolVar(&options.semanticNoTool, "semantic-no-tool", false, "offer no_tool on the Markdown profile; defaults on when Markdown is selected")
		fs.BoolVar(&options.decisionFakeThink, "decision-fake-think", false, "enable the experimental half-open fake-think prefix on unanchored tool decisions")
		fs.BoolVar(&options.closedFakeThink, "closed-fake-think", false, "prefill the fully closed think block instead of the half-open one; requires --decision-fake-think")
		fs.BoolVar(
			&options.deepToolAnchor,
			"deep-tool-anchor",
			false,
			"extend the Markdown decision prefill from the bare fence to the object and name keys; defaults on with Markdown and "+
				"removes syntactic abstention, so pair it with --semantic-no-tool",
		)
		fs.IntVar(
			&options.tracePromptBytes,
			"trace-prompt-bytes",
			agent.DefaultTracePromptBytes,
			"per-prompt recording budget in trace output; 0 disables, negative records in full",
		)
		fs.StringVar(
			&options.completion,
			"completion",
			"local",
			"continuation provider: local, rwkv-lightning, or chat-completions (optional build)",
		)
		fs.StringVar(&options.apiURL, "api-url", "", "full remote continuation endpoint URL")
		fs.StringVar(
			&options.apiKeyEnv,
			"api-key-env",
			"OPENAI_API_KEY",
			"environment variable containing the Chat Completions bearer token",
		)
		fs.StringVar(
			&options.chatThinking,
			"chat-thinking",
			string(chatcompletions.ThinkingAuto),
			"upstream Chat Completions thinking extension: auto, disabled, or enabled",
		)
		fs.StringVar(
			&options.chatPromptMode,
			"chat-prompt-mode",
			string(chatcompletions.PromptNativeChat),
			"Chat Completions prompt transport: wrapped-continuation or native-chat",
		)
		fs.StringVar(
			&options.chatTokenLimit,
			"chat-token-limit-field",
			string(chatcompletions.TokenLimitMaxCompletionTokens),
			"Chat Completions token limit field: max-completion-tokens or max-tokens",
		)
		fs.StringVar(
			&options.apiPasswordEnv,
			"api-password-env",
			"RWKV_API_PASSWORD",
			"environment variable containing the rwkv_lightning password",
		)
		fs.StringVar(
			&options.apiStopTokens,
			"api-stop-tokens",
			"text",
			"rwkv_lightning stop_tokens form: text, cuda, none, eos, or a comma-separated token ID list",
		)
		fs.BoolVar(
			&options.apiStream,
			"api-stream",
			true,
			"stream rwkv_lightning responses over SSE; false requests one buffered response",
		)
		fs.Var(
			&options.apiHeaderEnvs,
			"api-header-env",
			"repeatable HTTP_HEADER=ENV_VAR mapping for deployment authentication",
		)
		if name == "agent" {
			fs.StringVar(&options.prompt, "prompt", "", "task for the read-only repository agent")
			fs.StringVar(&options.ui, "ui", "auto", "agent renderer: auto, tui, or plain")
			fs.StringVar(&options.workspace, "workspace", ".", "workspace root available to read-only tools")
			fs.StringVar(&options.agentProtocol, "agent-protocol", string(agentapi.AgentProtocolXML), "tool transcript: xml (default) or markdown")
			fs.BoolVar(&options.progressiveTools, "progressive-tools", false, "route to one or two capability bundles before exposing tool schemas")
			fs.BoolVar(&options.enableWeb, "web", false, "enable Brave web_search and Tavily web_fetch")
			fs.BoolVar(&options.compressFetch, "compress-fetch", true, "compress long web_fetch results with a query-aware extraction before they enter the transcript (round-2 e2e: 0/25 → 25/25 on long-page tasks; pass =false for the A/B)")
			fs.StringVar(&options.braveAPIKeyEnv, "brave-api-key-env", "BRAVE_API_KEY", "environment variable containing the Brave Search API key")
			fs.StringVar(&options.braveEndpoint, "brave-endpoint", "", "optional Brave Search API endpoint")
			fs.StringVar(&options.tavilyAPIKeyEnv, "tavily-api-key-env", "TAVILY_API_KEY", "environment variable containing the Tavily API key")
			fs.StringVar(&options.tavilyEndpoint, "tavily-endpoint", "", "optional Tavily Extract API endpoint")
			fs.BoolVar(&options.enableSubagents, "subagents", false, "enable concurrent spawn_agents delegation")
			fs.IntVar(&options.maxActiveBatch, "max-active-batch", 4, "maximum local active generation batch, 1..8")
			fs.DurationVar(&options.remoteBatchWait, "remote-batch-wait", 10*time.Millisecond, "RWKV Lightning coalescing window for concurrent Agent requests")
			fs.IntVar(&options.subagentMaxParallel, "subagent-max-parallel", 4, "maximum tasks in one spawn_agents call, 2..8")
			fs.IntVar(&options.subagentMaxSteps, "subagent-max-steps", 4, "maximum model steps for each child Agent")
			fs.DurationVar(&options.subagentTimeout, "subagent-timeout", 2*time.Minute, "wall-clock timeout for one spawn_agents batch")
		} else {
			fs.BoolVar(&options.progressiveTools, "progressive-tools", false, "use the product progressive capability router (bfcl-product only; enabled there by default)")
			fs.IntVar(
				&options.duplicateReplayLimit,
				"duplicate-replay-limit",
				2,
				"re-execute identical calls to pure read tools up to this many times before rejecting; 0 disables (product and Go-native Primitive profiles)",
			)
			fs.IntVar(
				&options.duplicateRescueThreshold,
				"duplicate-rescue-threshold",
				3,
				"enter rescue mode after this many consecutive identical calls; 0 disables (product and Go-native Primitive profiles)",
			)
			fs.IntVar(
				&options.sameToolRescueLimit,
				"same-tool-rescue-limit",
				8,
				"enter rescue mode after this many consecutive successful calls to one tool; 0 disables (product and Go-native Primitive profiles)",
			)
			fs.BoolVar(
				&options.routeStage,
				"route-stage",
				false,
				"run the XML compatibility respond/inspect router before the decision stage",
			)
			fs.BoolVar(&options.fewShot, "few-shot", false, "enable XML Agent decision trajectory examples")
			fs.StringVar(&options.evalSuite, "suite", agenteval.SuiteBoundary, "built-in Agent eval suite: boundary, smoke, assistant, bfcl-product, primitive-orig30, or primitive-feedback30")
			fs.StringVar(
				&options.agentProtocol,
				"agent-protocol",
				string(agentapi.AgentProtocolMarkdown),
				"product transcript for --suite bfcl-product: markdown or xml",
			)
			fs.StringVar(
				&options.evalCasesPath,
				"cases",
				"",
				"versioned Agent eval JSON or trusted Primitive Bench case directory; conflicts with --suite",
			)
			fs.StringVar(&options.evalOutput, "output", "", "new directory for run.json, trace.jsonl, and summary.json")
			fs.Var(&options.evalCaseIDs, "case", "repeatable built-in or file-backed case ID to run")
			fs.DurationVar(&options.evalCaseTimeout, "case-timeout", 2*time.Minute, "timeout for each isolated eval case")
			fs.IntVar(&options.evalCaseParallelism, "case-parallelism", 1, "number of eval cases to run concurrently")
			fs.StringVar(&options.evalFileToolForm, "file-tools", "", "optional file-editing toolset for custom suites: lines (A) or whole (B)")
			fs.StringVar(&options.evalSubagentFixture, "subagent-fixture", "", "JSON file mapping subtask keywords to canned outputs, enabling a fixture-backed spawn_agents for custom suites")
			fs.StringVar(&options.evalWebFixture, "web-fixture", "", "JSON file mapping query/URL keywords to canned search results and pages, enabling fixture-backed web_search and web_fetch for custom suites")
			fs.BoolVar(&options.compressFetch, "compress-fetch", true, "compress long web_fetch results with a query-aware extraction before they enter the transcript (web-tool custom suites; round-2 e2e: 0/25 → 25/25; pass =false for the A/B)")
			fs.StringVar(&options.noToolGate, "no-tool-gate", "", "harness-level no_tool enforcement for product-profile suites: state (after one successful tool call) or evidence (reason must cite Function output)")
			fs.IntVar(&options.answerStageLead, "answer-stage-lead", 0, "force the answer stage this many steps before the budget ends and grant one dedicated answer-stage re-ask (0 = off)")
			fs.IntVar(&options.fetchBudgetTokens, "fetch-budget-tokens", 0, "override the shared web_fetch token budget (0 = 8192 default); E1 re-judgment A/B")
			fs.BoolVar(&options.subagentRawFeedback, "subagent-raw-feedback", false, "feed spawn_agents results back as raw JSON (pre-E2 behaviour); E2 re-judgment A/B")
			fs.StringVar(
				&options.primitiveProfile,
				"primitive-profile",
				agenteval.PrimitiveProfileUpstream,
				"Primitive tool profile: upstream-compatible or go-native",
			)
		}
	case "concurrent":
		fs.IntVar(&options.concurrency, "concurrency", 4, "number of overlapping sessions")
		fs.StringVar(&options.concurrentPrompt, "concurrent-prompt", "用一句话介绍 RWKV。", "prompt for every session")
		fs.StringVar(&options.ui, "ui", "auto", "concurrent renderer: auto, tui, or plain")
	}
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	fs.Visit(func(value *flag.Flag) {
		switch value.Name {
		case "thinking":
			options.thinkingExplicit = true
		case "reasoning":
			options.reasoningExplicit = true
		case "suite":
			options.evalSuiteExplicit = true
		case "chat-prompt-mode":
			options.chatPromptExplicit = true
		case "route-max-tokens":
			options.routeMaxTokensExplicit = true
		case "same-tool-rescue-limit":
			options.sameToolRescueExplicit = true
		case "progressive-tools":
			options.progressiveToolsExplicit = true
		case "semantic-no-tool":
			options.semanticNoToolExplicit = true
		case "deep-tool-anchor":
			options.deepToolAnchorExplicit = true
		}
	})
	if name == "agent-eval" {
		options.evalSuite = agenteval.CanonicalBuiltinSuiteName(options.evalSuite)
		if options.evalSuite == agenteval.SuiteBFCLProduct {
			if !options.progressiveToolsExplicit {
				options.progressiveTools = true
			}
			// The product profile defaults; agent-eval registers these flags as
			// off so non-product suites stay unaffected, so re-apply them here.
			if !options.semanticNoToolExplicit {
				options.semanticNoTool = true
			}
			if !options.deepToolAnchorExplicit {
				options.deepToolAnchor = true
			}
			if !options.routeMaxTokensExplicit {
				options.routeMaxTokens = 48
			}
			if !options.sameToolRescueExplicit {
				options.sameToolRescueLimit = agent.ProductSameToolRescueLimit
			}
		}
	}
	if name == "agent" && options.agentProtocol == string(agentapi.AgentProtocolMarkdown) {
		// Preserve the validated Markdown pair when that profile is selected
		// explicitly; the default XML profile keeps both switches off.
		if !options.semanticNoToolExplicit {
			options.semanticNoTool = true
		}
		if !options.deepToolAnchorExplicit {
			options.deepToolAnchor = true
		}
	}
	if options.thinkingExplicit && options.reasoningExplicit {
		return options, errors.New("--thinking and deprecated --reasoning cannot be used together")
	}
	if options.reasoningExplicit {
		options.thinkingMode = string(inference.ThinkingOff)
		if options.reasoning {
			options.thinkingMode = string(inference.ThinkingFast)
		}
		options.thinkingExplicit = true
	}
	mode, err := inference.ParseThinkingMode(options.thinkingMode)
	if err != nil {
		return options, fmt.Errorf("invalid --thinking: %w", err)
	}
	options.thinkingMode = string(mode)
	options.reasoning = mode != inference.ThinkingOff
	if options.modelPath == "" {
		fs.Usage()
		return options, fmt.Errorf("%s requires --model", name)
	}
	if agentMode {
		if options.maxSteps < 2 || options.maxSteps > 20 {
			return options, errors.New("--max-steps must be between 2 and 20")
		}
		if options.duplicateReplayLimit < 0 || options.duplicateReplayLimit > 10 {
			return options, errors.New("--duplicate-replay-limit must be between 0 and 10")
		}
		if options.duplicateRescueThreshold < 0 || options.duplicateRescueThreshold > 20 {
			return options, errors.New("--duplicate-rescue-threshold must be between 0 and 20")
		}
		if options.sameToolRescueLimit < 0 || options.sameToolRescueLimit > 50 {
			return options, errors.New("--same-tool-rescue-limit must be between 0 and 50")
		}
		if options.completion != "local" &&
			options.completion != "rwkv-lightning" &&
			options.completion != "chat-completions" {
			return options, fmt.Errorf("unsupported continuation provider %q", options.completion)
		}
		if options.completion != "local" && strings.TrimSpace(options.apiURL) == "" {
			return options, fmt.Errorf("%s continuation requires --api-url", options.completion)
		}
		chatThinking, err := chatcompletions.ParseThinkingMode(options.chatThinking)
		if err != nil {
			return options, err
		}
		options.chatThinking = string(chatThinking)
		if options.completion != "chat-completions" && chatThinking != chatcompletions.ThinkingAuto {
			return options, errors.New("--chat-thinking requires --completion chat-completions")
		}
		chatPromptMode, err := chatcompletions.ParsePromptMode(options.chatPromptMode)
		if err != nil {
			return options, err
		}
		options.chatPromptMode = string(chatPromptMode)
		if options.completion != "chat-completions" && options.chatPromptExplicit {
			return options, errors.New("--chat-prompt-mode requires --completion chat-completions")
		}
		if options.completion == "chat-completions" &&
			chatPromptMode == chatcompletions.PromptNativeChat &&
			options.thinkingMode != string(inference.ThinkingOff) {
			return options, errors.New("--chat-prompt-mode native-chat requires --thinking off")
		}
		chatTokenLimit, err := chatcompletions.ParseTokenLimitField(options.chatTokenLimit)
		if err != nil {
			return options, err
		}
		options.chatTokenLimit = string(chatTokenLimit)
		if options.completion != "chat-completions" &&
			chatTokenLimit != chatcompletions.TokenLimitMaxCompletionTokens {
			return options, errors.New("--chat-token-limit-field requires --completion chat-completions")
		}
		if name == "agent" &&
			options.ui == string(terminal.UIPlain) &&
			strings.TrimSpace(options.prompt) == "" {
			return options, errors.New("agent --ui plain requires --prompt")
		}
		if name == "agent" {
			if options.maxActiveBatch < 1 || options.maxActiveBatch > 8 {
				return options, errors.New("--max-active-batch must be between 1 and 8")
			}
			if options.remoteBatchWait < 0 || options.remoteBatchWait > time.Second {
				return options, errors.New("--remote-batch-wait must be between 0 and 1s")
			}
			if options.subagentMaxParallel < 2 || options.subagentMaxParallel > 8 {
				return options, errors.New("--subagent-max-parallel must be between 2 and 8")
			}
			if options.subagentMaxSteps < 2 || options.subagentMaxSteps > 32 {
				return options, errors.New("--subagent-max-steps must be between 2 and 32")
			}
			if options.subagentTimeout <= 0 || options.subagentTimeout > time.Hour {
				return options, errors.New("--subagent-timeout must be between 1ns and 1h")
			}
		}
		if name == "agent-eval" && options.evalCaseTimeout <= 0 {
			return options, errors.New("--case-timeout must be positive")
		}
		if name == "agent-eval" && options.evalCaseParallelism <= 0 {
			return options, errors.New("--case-parallelism must be positive")
		}
		if name == "agent-eval" && options.primitiveProfile != agenteval.PrimitiveProfileUpstream &&
			options.primitiveProfile != agenteval.PrimitiveProfileGoNative {
			return options, fmt.Errorf("unsupported Primitive tool profile %q", options.primitiveProfile)
		}
		if name == "agent-eval" {
			if options.evalSuite != agenteval.SuiteBoundary &&
				options.evalSuite != agenteval.SuiteSmoke &&
				options.evalSuite != agenteval.SuiteAssistant &&
				options.evalSuite != agenteval.SuiteBFCLProduct &&
				options.evalSuite != agenteval.SuitePrimitiveOrig30 &&
				options.evalSuite != agenteval.SuitePrimitiveFeedback30 {
				return options, fmt.Errorf(
					"unsupported Agent eval suite %q; expected boundary, smoke, assistant, bfcl-product, primitive-orig30, or primitive-feedback30",
					options.evalSuite,
				)
			}
			if options.evalCasesPath != "" && options.evalSuiteExplicit {
				return options, errors.New("--suite and --cases cannot be used together")
			}
			if options.evalSuite != agenteval.SuiteBFCLProduct &&
				options.evalCasesPath == "" &&
				(options.semanticNoToolExplicit || options.decisionFakeThink ||
					options.deepToolAnchorExplicit || options.progressiveToolsExplicit ||
					options.noToolGate != "" || options.answerStageLead != 0 ||
					options.subagentRawFeedback) {
				return options, errors.New("--semantic-no-tool, --deep-tool-anchor, --decision-fake-think, --progressive-tools, --no-tool-gate, and --answer-stage-lead are product-profile options and require --suite bfcl-product or a custom --cases file")
			}
			if options.noToolGate != "" && options.noToolGate != "state" && options.noToolGate != "evidence" {
				return options, errors.New("invalid --no-tool-gate: use state or evidence")
			}
			if options.answerStageLead < 0 || options.answerStageLead > 3 {
				return options, errors.New("--answer-stage-lead must be between 0 and 3")
			}
			if options.evalSuite == agenteval.SuiteBFCLProduct && options.routeStage {
				return options, errors.New("--route-stage is the XML compatibility router; bfcl-product uses --progressive-tools")
			}
		}
	}
	if options.tokenizer == "" && !(agentMode && options.completion != "local") {
		if strings.EqualFold(filepath.Ext(options.modelPath), ".pth") {
			tokenizer, err := bundledTokenizerPath()
			if err != nil {
				return options, err
			}
			options.tokenizer = tokenizer
		} else {
			options.tokenizer = filepath.Join(options.modelPath, "rwkv_vocab_v20230424.txt")
		}
	}
	if options.backend == "mlx" {
		options.backend = string(rwkvbackend.BackendID)
	}
	if options.backend != "auto" && options.backend != string(rwkvbackend.BackendID) {
		return options, fmt.Errorf("unsupported backend %q", options.backend)
	}
	if options.provider != "auto" && options.provider != "mlx" {
		return options, fmt.Errorf("unsupported provider %q", options.provider)
	}
	if options.nativeState != "auto" && options.nativeState != "off" && options.nativeState != "required" {
		return options, fmt.Errorf("invalid --native-state %q", options.nativeState)
	}
	if name == "agent" || name == "concurrent" {
		if _, err := terminal.ParseUIMode(options.ui); err != nil {
			return options, err
		}
	}
	if options.maxTokens <= 0 || options.temperature <= 0 ||
		options.topK <= 0 || options.topP <= 0 || options.topP > 1 ||
		options.presencePenalty < 0 || options.frequencyPenalty < 0 ||
		options.penaltyDecay <= 0 || options.penaltyDecay > 1 {
		return options, errors.New("invalid sampling options")
	}
	if agentMode && options.decisionMaxTokens < 0 {
		return options, errors.New("invalid agent decision token limit")
	}
	if agentMode && options.routeMaxTokens <= 0 {
		return options, errors.New("invalid agent route token limit")
	}
	if name == "agent" && options.agentProtocol != string(agentapi.AgentProtocolMarkdown) &&
		options.agentProtocol != string(agentapi.AgentProtocolXML) {
		return options, fmt.Errorf("invalid --agent-protocol %q", options.agentProtocol)
	}
	if name == "agent" && options.agentProtocol == string(agentapi.AgentProtocolXML) {
		// The XML envelope is the supported product default: <tool_call> closes
		// more reliably than the JSON fence
		// (20/20 and 15/20 versus 16/20 and 10/20 on 13.3b/7.2b), it carries
		// more complete arguments, and </tool_call> cannot collide with fenced
		// content the way the product profile's "```" stop can. So selecting it
		// never fails, and it implements no_tool in its own envelope.
		//
		// Both product prefill switches are off by default here. --deep-tool-anchor
		// has no JSON fence to extend. --semantic-no-tool is available but unused:
		// on the 60-case product suite the model selected no_tool 0 times under
		// XML versus 44 times under markdown, because this transcript already
		// answers directly without opening a call envelope. Offering it only
		// lengthens the catalog, so it stays opt-in.
		options.deepToolAnchor = false
		if !options.semanticNoToolExplicit {
			options.semanticNoTool = false
		}
		// --decision-fake-think stays an error here rather than a silent drop:
		// the XML renderer prefills its own think block via --thinking, so the
		// two would fight over the same assistant prefix and the run would not
		// mean what the flag says.
		if options.decisionFakeThink {
			return options, errors.New(
				"--decision-fake-think is the product-profile think experiment; " +
					"use --thinking fast or --thinking full with --agent-protocol xml",
			)
		}
	}
	if name == "agent" && options.agentProtocol == string(agentapi.AgentProtocolMarkdown) &&
		options.thinkingMode != string(inference.ThinkingOff) {
		return options, errors.New("--thinking fast/full requires --agent-protocol xml; use --decision-fake-think for the product text experiment")
	}
	if name == "agent-eval" && options.evalSuite == agenteval.SuiteBFCLProduct &&
		options.agentProtocol != string(agentapi.AgentProtocolXML) &&
		options.thinkingMode != string(inference.ThinkingOff) {
		return options, errors.New("--thinking fast/full is not part of the markdown bfcl-product profile; use --decision-fake-think, or --agent-protocol xml")
	}
	if options.closedFakeThink && !options.decisionFakeThink {
		return options, errors.New("--closed-fake-think selects the shape of the fake-think prefill and requires --decision-fake-think")
	}
	if name == "agent-eval" && options.agentProtocol != string(agentapi.AgentProtocolMarkdown) &&
		options.agentProtocol != string(agentapi.AgentProtocolXML) {
		return options, fmt.Errorf("invalid --agent-protocol %q", options.agentProtocol)
	}
	if name == "agent-eval" && options.agentProtocol == string(agentapi.AgentProtocolXML) {
		if options.evalSuite != agenteval.SuiteBFCLProduct {
			return options, errors.New("--agent-protocol xml applies to --suite bfcl-product")
		}
		// No JSON fence to extend, and no_tool measured 0 selections on this
		// transcript, so both stay opt-in here too.
		options.deepToolAnchor = false
		if !options.semanticNoToolExplicit {
			options.semanticNoTool = false
		}
	}
	return options, nil
}

type loadedRuntime struct {
	core  *inference.Core
	model inference.Model
}

func loadRuntime(ctx context.Context, options runOptions) (*loadedRuntime, error) {
	maxActiveBatch := 1
	if options.concurrency > 0 {
		maxActiveBatch = options.concurrency
	}
	backend := rwkvbackend.New(rwkvbackend.Options{
		Provider:       options.provider,
		MaxActiveBatch: maxActiveBatch,
		QueueCapacity:  64,
	})
	core, err := inference.NewCore(backend)
	if err != nil {
		return nil, fmt.Errorf("initialize inference core: %w", err)
	}
	theme := terminal.NewTheme(terminal.SupportsStyle(os.Stderr))
	spinner := terminal.StartSpinner(os.Stderr, theme, "Loading native model")
	model, err := core.LoadModel(ctx, inference.LoadRequest{
		Source: inference.ModelSource{
			Path:          options.modelPath,
			TokenizerPath: options.tokenizer,
		},
		Backend: inference.BackendID(options.backend),
	}, func(inference.Progress) error { return nil })
	if err != nil {
		spinner.Stop(false, "Model load failed")
		_ = core.Close()
		return nil, fmt.Errorf("load native model: %w", err)
	}
	spinner.Stop(true, "Model ready")
	return &loadedRuntime{core: core, model: model}, nil
}

func (r *loadedRuntime) Close() error {
	if r == nil || r.core == nil {
		return nil
	}
	return r.core.Close()
}

func newConversationOptions(options runOptions) conversation.Options {
	return conversation.Options{
		Profile: inference.DefaultPromptProfileForThinking(
			inference.ThinkingMode(options.thinkingMode),
		),
		NativeState: options.nativeState,
	}
}

func loadConversationOptions(options runOptions) conversation.Options {
	value := conversation.Options{
		NativeState:               options.nativeState,
		AllowPromptProfileUpgrade: true,
	}
	if options.thinkingExplicit {
		value.Profile = inference.DefaultPromptProfileForThinking(
			inference.ThinkingMode(options.thinkingMode),
		)
	}
	return value
}

func turnOptions(options runOptions) conversation.TurnOptions {
	return conversation.TurnOptions{
		Sampling: inference.SamplingOptions{
			Temperature:      float32(options.temperature),
			TopK:             options.topK,
			TopP:             float32(options.topP),
			PresencePenalty:  float32(options.presencePenalty),
			FrequencyPenalty: float32(options.frequencyPenalty),
			PenaltyDecay:     float32(options.penaltyDecay),
		},
		Limits: inference.GenerationLimits{MaxOutputTokens: options.maxTokens},
	}
}

func run(args []string) error {
	options, err := parseRunOptions("run", args)
	if err != nil {
		return err
	}
	lifecycle, stopLifecycle := context.WithCancel(context.Background())
	defer stopLifecycle()
	runtime, err := loadRuntime(lifecycle, options)
	if err != nil {
		return err
	}
	defer runtime.Close()

	var current *conversation.Conversation
	if options.sessionPath != "" {
		if _, statErr := os.Stat(filepath.Join(options.sessionPath, "CURRENT")); statErr == nil {
			current, err = conversation.Load(
				lifecycle,
				runtime.model,
				options.sessionPath,
				loadConversationOptions(options),
				printReplayProgress,
			)
		} else if !errors.Is(statErr, os.ErrNotExist) {
			return statErr
		}
	}
	if current == nil && err == nil {
		current, err = conversation.New(lifecycle, runtime.model, newConversationOptions(options))
	}
	if err != nil {
		return fmt.Errorf("initialize conversation: %w", err)
	}
	options.thinkingMode = string(inference.ProfileThinkingMode(current.Profile()))
	options.reasoning = options.thinkingMode != string(inference.ThinkingOff)
	if current.State().RecoveryMode == "profile-migration" {
		fmt.Fprintf(
			os.Stderr,
			"✓ Upgraded session prompt profile to v%d and rebuilt State from transcript\n",
			current.Profile().TemplateVersion,
		)
	}
	defer current.Close()

	controller := newSignalController()
	defer controller.Close()
	if options.prompt != "" {
		_, err := executeTurn(controller, current, options.prompt, turnOptions(options), os.Stdout)
		if err != nil && !errors.Is(err, context.Canceled) {
			return err
		}
		if options.autosave && options.sessionPath != "" {
			return current.Save(lifecycle, options.sessionPath)
		}
		return nil
	}
	return repl(lifecycle, controller, runtime.model, current, options)
}

type agentGeneratorSource struct {
	newGenerator func(context.Context) (continuation.Generator, io.Closer, error)
	close        func() error
	modelInfo    inference.ModelInfo
	hasModelInfo bool
}

func newAgentGeneratorSource(
	ctx context.Context,
	options runOptions,
) (*agentGeneratorSource, error) {
	if options.completion != "local" {
		headers, err := loadAPIHeaders(options.apiHeaderEnvs)
		if err != nil {
			return nil, err
		}
		if options.completion == "chat-completions" {
			client, err := chatcompletions.New(chatcompletions.Config{
				Endpoint:   options.apiURL,
				Model:      options.modelPath,
				APIKey:     os.Getenv(options.apiKeyEnv),
				Thinking:   chatcompletions.ThinkingMode(options.chatThinking),
				PromptMode: chatcompletions.PromptMode(options.chatPromptMode),
				TokenLimit: chatcompletions.TokenLimitField(options.chatTokenLimit),
				Headers:    headers,
			})
			if err != nil {
				return nil, fmt.Errorf("initialize Chat Completions continuation: %w", err)
			}
			return &agentGeneratorSource{
				newGenerator: func(context.Context) (continuation.Generator, io.Closer, error) {
					return client, noopCloser{}, nil
				},
				close: func() error { return nil },
			}, nil
		}
		stopTokenMode, stopTokenIDs, err := parseAPIStopTokens(options.apiStopTokens)
		if err != nil {
			return nil, err
		}
		batchWait := time.Duration(0)
		if options.evalCaseParallelism > 1 {
			// Match the official Primitive Bench runner: case goroutines share one
			// short coalescing window and send one contents[] request per turn.
			batchWait = 10 * time.Millisecond
		}
		client, err := rwkvlightning.New(rwkvlightning.Config{
			Endpoint:      options.apiURL,
			Model:         options.modelPath,
			Password:      os.Getenv(options.apiPasswordEnv),
			StopTokenMode: stopTokenMode,
			StopTokenIDs:  stopTokenIDs,
			Stream:        &options.apiStream,
			BatchWait:     batchWait,
			Headers:       headers,
		})
		if err != nil {
			return nil, fmt.Errorf("initialize remote continuation: %w", err)
		}
		return &agentGeneratorSource{
			newGenerator: func(context.Context) (continuation.Generator, io.Closer, error) {
				return client, noopCloser{}, nil
			},
			close: func() error { return nil },
		}, nil
	}
	runtime, err := loadRuntime(ctx, options)
	if err != nil {
		return nil, err
	}
	source := &agentGeneratorSource{
		close:        runtime.Close,
		modelInfo:    runtime.model.Info(),
		hasModelInfo: true,
	}
	source.newGenerator = func(
		sessionContext context.Context,
	) (continuation.Generator, io.Closer, error) {
		session, err := runtime.model.NewSession(sessionContext, inference.SessionOptions{})
		if err != nil {
			return nil, nil, fmt.Errorf("create agent session: %w", err)
		}
		generator, err := localcontinuation.New(session)
		if err != nil {
			_ = session.Close()
			return nil, nil, fmt.Errorf("initialize local continuation: %w", err)
		}
		return generator, session, nil
	}
	return source, nil
}

func (s *agentGeneratorSource) Close() error {
	if s == nil || s.close == nil {
		return nil
	}
	return s.close()
}

type noopCloser struct{}

func (noopCloser) Close() error { return nil }

// subagentFixtureEntries loads the keyword->output mapping for the fixture
// spawn_agents tool; an empty path disables the tool.
func subagentFixtureEntries(path string) []agenteval.SubagentFixtureEntry {
	if path == "" {
		return nil
	}
	data, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "subagent-fixture: %v\n", err)
		os.Exit(1)
	}
	var entries []agenteval.SubagentFixtureEntry
	if err := json.Unmarshal(data, &entries); err != nil {
		fmt.Fprintf(os.Stderr, "subagent-fixture: %v\n", err)
		os.Exit(1)
	}
	return entries
}

// webFixtureEntries loads the keyword->page mapping for the fixture web tools;
// an empty path disables the tools.
func webFixtureEntries(path string) []agenteval.WebFixtureEntry {
	if path == "" {
		return nil
	}
	data, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "web-fixture: %v\n", err)
		os.Exit(1)
	}
	var entries []agenteval.WebFixtureEntry
	if err := json.Unmarshal(data, &entries); err != nil {
		fmt.Fprintf(os.Stderr, "web-fixture: %v\n", err)
		os.Exit(1)
	}
	return entries
}

// evalToolBundles returns the default bundles, with the workspace description
// extended to cover file editing when the file-edit toolset is enabled. The
// progressive router routes on these descriptions: with the read-only wording
// it judged edit tasks as needing no tool evidence (E6 finding).
func evalToolBundles(options runOptions) []agent.ToolBundle {
	bundles := agent.DefaultToolBundles()
	for index := range bundles {
		if bundles[index].Name == agent.ToolBundleWorkspace && options.evalFileToolForm != "" {
			bundles[index].Description = "Read, create, and edit files inside the configured workspace."
			bundles[index].Editable = true
		}
		if bundles[index].Name == agent.ToolBundleDelegate && options.evalSubagentFixture != "" {
			bundles[index].Delegation = true
		}
	}
	return bundles
}

func agentRunnerOptions(options runOptions, suite string, observe func(agent.Event)) agent.Options {
	if suite == agenteval.SuiteBFCLProduct {
		// The suite accepts either product-facing transcript so the two can be
		// compared on the same cases. XML has no JSON fence, so the deep anchor
		// does not apply there; no_tool exists in both.
		if options.agentProtocol == string(agentapi.AgentProtocolXML) {
			return agent.XMLHarnessOptions(agent.XMLHarnessConfig{
				MaxSteps:                 options.maxSteps,
				DecisionMaxOutputTokens:  options.decisionMaxTokens,
				RouteMaxOutputTokens:     options.routeMaxTokens,
				TracePromptBytes:         options.tracePromptBytes,
				DuplicateReplayLimit:     options.duplicateReplayLimit,
				DuplicateRescueThreshold: options.duplicateRescueThreshold,
				SameToolRescueLimit:      options.sameToolRescueLimit,
				Generation: continuation.Request{
					Model:           options.modelPath,
					MaxOutputTokens: options.maxTokens,
					Sampling: continuation.Sampling{
						Temperature:      float32(options.temperature),
						TopK:             options.topK,
						TopP:             float32(options.topP),
						PresencePenalty:  float32(options.presencePenalty),
						FrequencyPenalty: float32(options.frequencyPenalty),
						PenaltyDecay:     float32(options.penaltyDecay),
					},
				},
				ProgressiveTools: options.progressiveTools,
				ToolBundles:      agent.DefaultToolBundles(),
				SemanticNoTool:   options.semanticNoTool,
				ThinkingMode:     inference.ThinkingMode(options.thinkingMode),
				FewShot:          options.fewShot,
				CompressFetch:    options.compressFetch,
				Observe:          observe,
			})
		}
		return agent.ProductHarnessOptions(agent.ProductHarnessConfig{
			MaxSteps:                 options.maxSteps,
			DecisionMaxOutputTokens:  options.decisionMaxTokens,
			RouteMaxOutputTokens:     options.routeMaxTokens,
			TracePromptBytes:         options.tracePromptBytes,
			DuplicateReplayLimit:     options.duplicateReplayLimit,
			DuplicateRescueThreshold: options.duplicateRescueThreshold,
			SameToolRescueLimit:      options.sameToolRescueLimit,
			Generation: continuation.Request{
				Model:           options.modelPath,
				MaxOutputTokens: options.maxTokens,
				Sampling: continuation.Sampling{
					Temperature:      float32(options.temperature),
					TopK:             options.topK,
					TopP:             float32(options.topP),
					PresencePenalty:  float32(options.presencePenalty),
					FrequencyPenalty: float32(options.frequencyPenalty),
					PenaltyDecay:     float32(options.penaltyDecay),
				},
			},
			ProgressiveTools:    options.progressiveTools,
			ToolBundles:         evalToolBundles(options),
			SemanticNoTool:      options.semanticNoTool,
			DecisionFakeThink:   options.decisionFakeThink,
			ClosedFakeThink:     options.closedFakeThink,
			DeepToolAnchor:      options.deepToolAnchor,
			CompressFetch:       options.compressFetch,
			NoToolGate:          options.noToolGate,
			AnswerStageLead:     options.answerStageLead,
			SubagentRawFeedback: options.subagentRawFeedback,
			Observe:             observe,
		})
	}
	if options.evalCasesPath != "" && options.agentProtocol == string(agentapi.AgentProtocolMarkdown) {
		// Custom suites honor --agent-protocol markdown by running the same
		// product-facing profile as bfcl-product; before this branch the flag
		// was silently ignored here (found during the E6 file-tool A/B).
		// Built-in suites keep their established mapping: boundary and the
		// primitive suites run the XML envelope regardless of the flag, so
		// their baselines stay comparable.
		return agent.ProductHarnessOptions(agent.ProductHarnessConfig{
			MaxSteps:                 options.maxSteps,
			DecisionMaxOutputTokens:  options.decisionMaxTokens,
			RouteMaxOutputTokens:     options.routeMaxTokens,
			TracePromptBytes:         options.tracePromptBytes,
			DuplicateReplayLimit:     options.duplicateReplayLimit,
			DuplicateRescueThreshold: options.duplicateRescueThreshold,
			SameToolRescueLimit:      options.sameToolRescueLimit,
			Generation: continuation.Request{
				Model:           options.modelPath,
				MaxOutputTokens: options.maxTokens,
				Sampling: continuation.Sampling{
					Temperature:      float32(options.temperature),
					TopK:             options.topK,
					TopP:             float32(options.topP),
					PresencePenalty:  float32(options.presencePenalty),
					FrequencyPenalty: float32(options.frequencyPenalty),
					PenaltyDecay:     float32(options.penaltyDecay),
				},
			},
			ProgressiveTools:    options.progressiveTools,
			ToolBundles:         evalToolBundles(options),
			SemanticNoTool:      options.semanticNoTool,
			DecisionFakeThink:   options.decisionFakeThink,
			ClosedFakeThink:     options.closedFakeThink,
			DeepToolAnchor:      options.deepToolAnchor,
			CompressFetch:       options.compressFetch,
			NoToolGate:          options.noToolGate,
			AnswerStageLead:     options.answerStageLead,
			SubagentRawFeedback: options.subagentRawFeedback,
			Observe:             observe,
		})
	}
	agentOptions := agent.XMLHarnessOptions(agent.XMLHarnessConfig{
		MaxSteps:                 options.maxSteps,
		DecisionMaxOutputTokens:  options.decisionMaxTokens,
		RouteMaxOutputTokens:     options.routeMaxTokens,
		TracePromptBytes:         options.tracePromptBytes,
		DuplicateReplayLimit:     options.duplicateReplayLimit,
		DuplicateRescueThreshold: options.duplicateRescueThreshold,
		SameToolRescueLimit:      options.sameToolRescueLimit,
		Generation: continuation.Request{
			Model:           options.modelPath,
			MaxOutputTokens: options.maxTokens,
			Sampling: continuation.Sampling{
				Temperature:      float32(options.temperature),
				TopK:             options.topK,
				TopP:             float32(options.topP),
				PresencePenalty:  float32(options.presencePenalty),
				FrequencyPenalty: float32(options.frequencyPenalty),
				PenaltyDecay:     float32(options.penaltyDecay),
			},
		},
		ThinkingMode: inference.ThinkingMode(options.thinkingMode),
		FewShot:      options.fewShot,
		Observe:      observe,
	})
	// The eval CLI keeps the older respond/inspect router as a separate stage,
	// rather than the progressive tool router the product profile uses.
	if options.routeStage {
		agentOptions.Router = agent.G1IRouteProtocol{}
		agentOptions.RouteRenderer = agent.RWKVChatRenderer{}
		agentOptions.RouteRetries = 1
	}
	return agentOptions
}

func runAgent(args []string) error {
	options, err := parseRunOptions("agent", args)
	if err != nil {
		return err
	}
	reportCompletionCompatibility(options)
	mode, err := terminal.ParseUIMode(options.ui)
	if err != nil {
		return err
	}
	selected, err := terminal.SelectUI(mode, terminal.Detect(os.Stdin, os.Stdout))
	if err != nil {
		return err
	}
	if selected == terminal.UIPlain && strings.TrimSpace(options.prompt) == "" {
		return errors.New("agent requires --prompt outside an interactive TUI")
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	service, err := agentapi.NewService(agentapi.Options{Workspace: options.workspace})
	if err != nil {
		return err
	}
	defer service.Close()
	config, err := agentAPIConfig(options)
	if err != nil {
		return err
	}
	theme := terminal.NewTheme(terminal.SupportsStyle(os.Stderr))
	spinner := terminal.StartSpinner(os.Stderr, theme, "Preparing model provider")
	status, err := service.Configure(ctx, config, nil)
	if err != nil {
		spinner.Stop(false, "Model provider failed")
		return err
	}
	spinner.Stop(true, "Model provider ready")
	session, err := service.NewSession(ctx)
	if err != nil {
		return err
	}
	defer session.Close()
	var observe func(agentapi.Event)
	if selected == terminal.UIPlain {
		observe = func(event agentapi.Event) {
			switch event.Kind {
			case agentapi.EventRouteDone:
				if event.Error != "" {
					fmt.Fprintf(
						os.Stderr,
						"%s %s: %s\n",
						theme.Render(theme.Warning, "Route fallback"),
						event.Route,
						event.Error,
					)
				} else {
					fmt.Fprintf(
						os.Stderr,
						"%s %s\n",
						theme.Render(theme.Accent, "Route"),
						event.Route,
					)
				}
			case agentapi.EventModelStart:
				fmt.Fprintf(os.Stderr, "%s step %d\n", theme.Render(theme.Muted, "Agent"), event.Step)
			case agentapi.EventRetry:
				fmt.Fprintln(os.Stderr, theme.Render(theme.Warning, "Retrying invalid model action"))
			case agentapi.EventToolStart:
				fmt.Fprintf(os.Stderr, "%s %s\n", theme.Render(theme.Accent, "Tool"), event.Tool)
			case agentapi.EventToolDone:
				if event.Error != "" {
					fmt.Fprintf(os.Stderr, "%s %s: %s\n", theme.Render(theme.Warning, "Tool failed"), event.Tool, event.Error)
				}
			}
		}
	}
	if selected == terminal.UITUI {
		provider := options.provider
		if options.completion != "local" {
			provider = options.completion
		} else if provider == "auto" {
			provider = "mlx"
		}
		_, err = agenttui.Run(
			ctx,
			session,
			agenttui.Metadata{
				Model:     filepath.Base(status.Model),
				Provider:  provider,
				Workspace: options.workspace,
				Thinking:  options.thinkingMode,
			},
			options.prompt,
			os.Stdin,
			os.Stdout,
		)
		if errors.Is(err, context.Canceled) {
			return nil
		}
		return err
	}
	result, err := session.RunWithObserver(ctx, options.prompt, observe)
	if err != nil {
		if os.Getenv("RWKV_AGENT_DEBUG") == "1" {
			for _, step := range result.Steps {
				fmt.Fprintf(
					os.Stderr,
					"Agent raw step %d: %q\n",
					step.Number,
					step.ModelOutput,
				)
			}
		}
		return err
	}
	fmt.Fprintln(os.Stdout, terminal.SanitizeModelText(result.Output))
	return nil
}

func agentAPIConfig(options runOptions) (agentapi.Config, error) {
	headers, err := loadAPIHeaders(options.apiHeaderEnvs)
	if err != nil {
		return agentapi.Config{}, err
	}
	headerValues := make(map[string]string, len(headers))
	for name, values := range headers {
		if len(values) > 0 {
			headerValues[name] = values[len(values)-1]
		}
	}
	stream := options.apiStream
	progressive := options.progressiveTools
	semanticNoTool := options.semanticNoTool
	deepToolAnchor := options.deepToolAnchor
	tracePromptBytes := options.tracePromptBytes
	return agentapi.Config{
		Provider:               agentapi.Provider(options.completion),
		Model:                  options.modelPath,
		Endpoint:               options.apiURL,
		APIKey:                 os.Getenv(options.apiKeyEnv),
		Password:               os.Getenv(options.apiPasswordEnv),
		Headers:                headerValues,
		TokenizerPath:          options.tokenizer,
		Backend:                options.backend,
		NativeProvider:         options.provider,
		Thinking:               options.thinkingMode,
		AgentProtocol:          agentapi.AgentProtocol(options.agentProtocol),
		SemanticNoTool:         &semanticNoTool,
		DecisionFakeThink:      options.decisionFakeThink,
		CompressFetch:          options.compressFetch,
		DeepToolAnchor:         &deepToolAnchor,
		MaxSteps:               options.maxSteps,
		MaxTokens:              options.maxTokens,
		DecisionMaxTokens:      options.decisionMaxTokens,
		RouteMaxTokens:         options.routeMaxTokens,
		TracePromptBytes:       &tracePromptBytes,
		Temperature:            options.temperature,
		TopK:                   options.topK,
		TopP:                   options.topP,
		PresencePenalty:        options.presencePenalty,
		FrequencyPenalty:       options.frequencyPenalty,
		PenaltyDecay:           options.penaltyDecay,
		ChatThinking:           options.chatThinking,
		ChatPromptMode:         options.chatPromptMode,
		ChatTokenLimit:         options.chatTokenLimit,
		Stream:                 &stream,
		ProgressiveTools:       &progressive,
		EnableWeb:              options.enableWeb,
		BraveAPIKey:            os.Getenv(options.braveAPIKeyEnv),
		BraveEndpoint:          options.braveEndpoint,
		TavilyAPIKey:           os.Getenv(options.tavilyAPIKeyEnv),
		TavilyEndpoint:         options.tavilyEndpoint,
		EnableSubagents:        options.enableSubagents,
		MaxActiveBatch:         options.maxActiveBatch,
		RemoteBatchWaitMS:      int(options.remoteBatchWait / time.Millisecond),
		SubagentMaxParallel:    options.subagentMaxParallel,
		SubagentMaxSteps:       options.subagentMaxSteps,
		SubagentTimeoutSeconds: int(options.subagentTimeout / time.Second),
	}, nil
}

func runAgentEval(args []string) error {
	options, err := parseRunOptions("agent-eval", args)
	if err != nil {
		return err
	}
	reportCompletionCompatibility(options)
	suite := options.evalSuite
	cases, err := agenteval.BuiltinSuite(suite)
	if err != nil {
		return err
	}
	if options.evalCasesPath != "" {
		info, statErr := os.Stat(options.evalCasesPath)
		if statErr != nil {
			return fmt.Errorf("inspect Agent eval cases: %w", statErr)
		}
		if info.IsDir() {
			cases, err = agenteval.LoadPrimitiveCases(options.evalCasesPath)
			suite = agenteval.SuitePrimitive
		} else {
			cases, err = agenteval.LoadCases(options.evalCasesPath)
			suite = "custom"
		}
		if err != nil {
			return fmt.Errorf("load Agent eval cases: %w", err)
		}
	}
	if !agenteval.IsPrimitiveSuite(suite) && options.primitiveProfile != agenteval.PrimitiveProfileUpstream {
		return errors.New("--primitive-profile go-native requires a Primitive suite or case directory")
	}
	cases, err = agenteval.SelectCases(cases, options.evalCaseIDs)
	if err != nil {
		return err
	}
	if options.evalOutput == "" {
		options.evalOutput = filepath.Join(
			"runs",
			"agent-eval-"+time.Now().UTC().Format("20060102-150405.000000000"),
		)
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	source, err := newAgentGeneratorSource(ctx, options)
	if err != nil {
		return err
	}
	defer source.Close()
	model := agenteval.ModelMetadata{
		Identifier: options.modelPath,
		Backend:    options.backend,
		Provider:   options.provider,
		Completion: options.completion,
	}
	if options.completion == "chat-completions" {
		model.PromptMode = options.chatPromptMode
		model.UnsupportedSampling = []string{"top_k", "penalty_decay"}
		model.UpstreamThinking = options.chatThinking
		model.TokenLimitField = options.chatTokenLimit
	}
	if source.hasModelInfo {
		info := source.modelInfo
		model.Fingerprint = info.Fingerprint
		model.TokenizerFingerprint = info.TokenizerFingerprint
		model.Architecture = info.Architecture
		model.Format = string(info.Format)
		model.Precision = info.Precision
		model.Quantization = info.Quantization
		model.Backend = string(info.Backend)
	}
	report, runErr := agenteval.Run(ctx, agenteval.Config{
		Cases:             cases,
		Suite:             suite,
		Model:             model,
		Runner:            agentRunnerOptions(options, suite, nil),
		CaseTimeout:       options.evalCaseTimeout,
		CaseParallelism:   options.evalCaseParallelism,
		PrimitiveProfile:  options.primitiveProfile,
		FileToolForm:      options.evalFileToolForm,
		SubagentFixture:   subagentFixtureEntries(options.evalSubagentFixture),
		WebFixture:        webFixtureEntries(options.evalWebFixture),
		FetchBudgetTokens: options.fetchBudgetTokens,
		GeneratorFactory: func(
			caseContext context.Context,
		) (continuation.Generator, io.Closer, error) {
			return source.newGenerator(caseContext)
		},
	})
	if report.Manifest.RunID == "" {
		return runErr
	}
	paths, writeErr := agenteval.WriteArtifacts(options.evalOutput, report)
	if writeErr != nil {
		return fmt.Errorf("write Agent eval artifacts: %w", writeErr)
	}
	metrics := report.Summary.Metrics
	fmt.Fprintf(
		os.Stdout,
		"Agent eval (%s): %d/%d cases passed; answer %s; route %s; protocol %s; stage %s\n",
		suite,
		metrics.TaskSuccess.Correct,
		metrics.TaskSuccess.Total,
		formatEvalScore(metrics.AnswerAccuracy),
		formatEvalScore(metrics.RouteAccuracy),
		formatEvalScore(metrics.ProtocolValidity),
		formatEvalScore(metrics.StageContractValidity),
	)
	fmt.Fprintf(
		os.Stdout,
		"Tool checks: exact %s; required %s; forbidden %s; calls %s\n",
		formatEvalScore(metrics.ToolSelection),
		formatEvalScore(metrics.RequiredToolCompletion),
		formatEvalScore(metrics.ForbiddenToolAvoidance),
		formatEvalScore(metrics.RequiredCallAccuracy),
	)
	fmt.Fprintf(os.Stdout, "Artifacts: %s\n", paths.Directory)
	if runErr != nil {
		return runErr
	}
	if metrics.TaskSuccess.Correct != metrics.TaskSuccess.Total {
		return fmt.Errorf(
			"Agent eval failed %d of %d cases",
			metrics.TaskSuccess.Total-metrics.TaskSuccess.Correct,
			metrics.TaskSuccess.Total,
		)
	}
	return nil
}

func reportCompletionCompatibility(options runOptions) {
	if options.completion != "chat-completions" {
		return
	}
	fmt.Fprintln(
		os.Stderr,
		"Chat Completions compatibility: prompt mode="+options.chatPromptMode+"; "+
			"tool transport="+chatToolTransport(options.chatPromptMode)+"; "+
			"top-k and penalty-decay are not sent upstream; streaming is disabled; "+
			"upstream thinking="+options.chatThinking+"; token limit="+options.chatTokenLimit,
	)
}

func chatToolTransport(promptMode string) string {
	if promptMode == string(chatcompletions.PromptNativeChat) {
		return "native"
	}
	return "g1i-text"
}

func formatEvalScore(score agenteval.Score) string {
	if score.Total == 0 {
		return "n/a"
	}
	return fmt.Sprintf("%.1f%%", 100*score.Rate)
}

// parseAPIStopTokens resolves --api-stop-tokens into a rwkv_lightning stop token
// mode. "text" forwards the protocol's decoded-text stops for the PyTorch server.
// "cuda" sends the rwkv_lightning_cuda stop IDs needed by the G1I protocol,
// "none" omits the field, "eos" sends only the legacy integer EOS token, and an
// explicit comma-separated list passes those token IDs through.
func parseAPIStopTokens(value string) (rwkvlightning.StopTokenMode, []int, error) {
	switch trimmed := strings.ToLower(strings.TrimSpace(value)); trimmed {
	case "", "text":
		return rwkvlightning.StopTokenText, nil, nil
	case "cuda":
		// CUDA stops when any listed token is generated. Token 6884 is the JSON
		// fence used by the native G1i function transcript; 24281 stops before a
		// generated User continuation. Do not include newline token 261 because
		// it truncates long JSON arguments mid-value.
		return rwkvlightning.StopTokenEOS, []int{0, 6884, 24281}, nil
	case "none":
		return rwkvlightning.StopTokenNone, nil, nil
	case "eos":
		return rwkvlightning.StopTokenEOS, []int{0}, nil
	default:
		fields := strings.Split(trimmed, ",")
		tokens := make([]int, 0, len(fields))
		for _, field := range fields {
			token, err := strconv.Atoi(strings.TrimSpace(field))
			if err != nil || token < 0 {
				return "", nil, fmt.Errorf(
					"--api-stop-tokens must be text, cuda, none, eos, or a comma-separated list of non-negative token IDs",
				)
			}
			tokens = append(tokens, token)
		}
		return rwkvlightning.StopTokenEOS, tokens, nil
	}
}

func loadAPIHeaders(mappings []string) (http.Header, error) {
	headers := make(http.Header, len(mappings))
	for _, mapping := range mappings {
		name, environment, ok := strings.Cut(mapping, "=")
		name = textproto.CanonicalMIMEHeaderKey(strings.TrimSpace(name))
		environment = strings.TrimSpace(environment)
		if !ok || name == "" || environment == "" {
			return nil, fmt.Errorf(
				"invalid --api-header-env %q; expected HTTP_HEADER=ENV_VAR",
				mapping,
			)
		}
		value, exists := os.LookupEnv(environment)
		if !exists {
			return nil, fmt.Errorf(
				"--api-header-env for %s references unset environment variable %s",
				name,
				environment,
			)
		}
		if strings.ContainsAny(value, "\r\n") {
			return nil, fmt.Errorf("environment variable %s contains an invalid header value", environment)
		}
		headers.Set(name, value)
	}
	return headers, nil
}

func repl(
	ctx context.Context,
	controller *signalController,
	model inference.Model,
	current *conversation.Conversation,
	options runOptions,
) error {
	theme := terminal.NewTheme(terminal.SupportsStyle(os.Stderr))
	fmt.Fprintf(
		os.Stderr,
		"%s %s\n%s\n",
		theme.Render(theme.Title, "RWKV"),
		theme.Render(theme.Muted, "· interactive"),
		theme.Render(theme.Muted, "Type /help for commands · Ctrl-C cancels a turn or exits while idle"),
	)
	lines := make(chan string)
	readErrors := make(chan error, 1)
	go func() {
		scanner := bufio.NewScanner(os.Stdin)
		for scanner.Scan() {
			lines <- scanner.Text()
		}
		readErrors <- scanner.Err()
		close(lines)
	}()
	for {
		fmt.Fprint(os.Stdout, theme.Render(theme.Prompt, "❯ "))
		select {
		case <-controller.Exit():
			fmt.Fprintln(os.Stderr)
			return autosave(ctx, current, options)
		case err := <-readErrors:
			if err != nil {
				return fmt.Errorf("read prompt: %w", err)
			}
			return autosave(ctx, current, options)
		case line, ok := <-lines:
			if !ok {
				return autosave(ctx, current, options)
			}
			input := strings.TrimSpace(line)
			if input == "" {
				continue
			}
			if strings.HasPrefix(input, "/") {
				exit, err := executeCommand(ctx, model, current, &options, input)
				if err != nil {
					fmt.Fprintln(os.Stderr, "command failed:", err)
				}
				if exit {
					return autosave(ctx, current, options)
				}
				continue
			}
			_, err := executeTurn(controller, current, input, turnOptions(options), os.Stdout)
			if err != nil {
				if errors.Is(err, context.Canceled) {
					fmt.Fprintln(os.Stderr, "Generation cancelled; the committed transcript was not changed.")
				} else {
					fmt.Fprintln(os.Stderr, "generation failed:", err)
				}
			} else if options.autosave && options.sessionPath != "" {
				if err := current.Save(ctx, options.sessionPath); err != nil {
					fmt.Fprintln(os.Stderr, "autosave failed:", err)
				}
			}
		}
	}
}

func executeTurn(
	controller *signalController,
	current *conversation.Conversation,
	input string,
	options conversation.TurnOptions,
	writer io.Writer,
) (inference.GenerateResult, error) {
	ctx, cancel := context.WithCancel(context.Background())
	controller.SetActive(cancel)
	defer func() {
		controller.SetIdle()
		cancel()
	}()
	result, err := current.Turn(ctx, input, options, func(event inference.GenerationEvent) error {
		if event.Kind != inference.EventOutputDelta || event.Delta == nil {
			return nil
		}
		_, writeErr := io.WriteString(writer, terminal.SanitizeModelText(event.Delta.Text))
		return writeErr
	})
	fmt.Fprintln(writer)
	if result.Timings.DecodeTokensPerSecond > 0 {
		theme := terminal.NewTheme(terminal.SupportsStyle(os.Stderr))
		fmt.Fprintf(
			os.Stderr,
			"%s prefill %.1f tok/s · decode %.1f tok/s\n",
			theme.Render(theme.Muted, "◇"),
			result.Timings.PrefillTokensPerSecond,
			result.Timings.DecodeTokensPerSecond,
		)
	}
	return result, err
}

func executeCommand(
	ctx context.Context,
	model inference.Model,
	current *conversation.Conversation,
	options *runOptions,
	input string,
) (bool, error) {
	fields := strings.Fields(input)
	theme := terminal.NewTheme(terminal.SupportsStyle(os.Stdout))
	switch fields[0] {
	case "/help":
		fmt.Println(theme.Render(theme.Title, "Commands"))
		fmt.Println(`/state                show logical and native State
/history              show committed transcript
/save [path]           save an immutable session revision
/load <path>           load and validate a session
/reset, /new           clear transcript and native State
/exit                  save if requested and exit`)
	case "/state":
		state := current.State()
		fmt.Println(theme.Render(theme.Title, "State"))
		fmt.Printf(
			"  revision  %s\n  status    %s\n  messages  %d\n  tokens    %d\n  native    %s\n  snapshot  %t\n  recovery  %s",
			shortRevision(state.Revision),
			state.Status,
			state.MessageCount,
			state.CommittedPrefixTokenCount,
			state.NativeRevision,
			state.NativeSnapshot,
			state.RecoveryMode,
		)
		if state.DirtyReason != "" {
			fmt.Printf("\n  dirty     %q", state.DirtyReason)
		}
		fmt.Println()
	case "/history":
		fmt.Println(theme.Render(theme.Title, "History"))
		for _, message := range current.History() {
			role := string(message.Role)
			style := theme.Accent
			if message.Role == inference.RoleAssistant {
				style = theme.Success
			}
			fmt.Printf("%s %s\n", theme.Render(style, role+" ›"), messageText(message))
		}
	case "/save":
		path := options.sessionPath
		if len(fields) == 2 {
			path = fields[1]
		}
		if path == "" {
			return false, errors.New("no session path; use /save <path> or --session")
		}
		if err := current.Save(ctx, path); err != nil {
			return false, err
		}
		fmt.Println(theme.Render(theme.Success, "✓ saved"), path)
	case "/load":
		if len(fields) != 2 {
			return false, errors.New("usage: /load <path>")
		}
		replacement, err := conversation.Load(
			ctx,
			model,
			fields[1],
			loadConversationOptions(*options),
			printReplayProgress,
		)
		if err != nil {
			return false, err
		}
		if err := current.ReplaceWith(replacement); err != nil {
			_ = replacement.Close()
			return false, err
		}
		_ = replacement.Close()
		options.sessionPath = fields[1]
		options.thinkingMode = string(inference.ProfileThinkingMode(current.Profile()))
		options.reasoning = options.thinkingMode != string(inference.ThinkingOff)
		fmt.Println(theme.Render(theme.Success, "✓ loaded"), fields[1])
	case "/reset", "/new":
		if err := current.Reset(ctx); err != nil {
			return false, err
		}
		fmt.Println(theme.Render(theme.Success, "✓ conversation reset"))
	case "/exit":
		return true, nil
	default:
		return false, fmt.Errorf("unknown command %q; use /help", fields[0])
	}
	return false, nil
}

func messageText(message inference.Message) string {
	var result strings.Builder
	for _, part := range message.Parts {
		result.WriteString(part.Text)
	}
	return result.String()
}

func shortRevision(value string) string {
	value = strings.TrimPrefix(value, "sha256:")
	if len(value) > 12 {
		return value[:12]
	}
	return value
}

func printReplayProgress(progress inference.Progress) error {
	if progress.Total > 0 {
		if terminal.SupportsStyle(os.Stderr) {
			fmt.Fprintf(os.Stderr, "\rRebuilding State: %d/%d tokens", progress.Completed, progress.Total)
			if progress.Completed == progress.Total {
				fmt.Fprintln(os.Stderr)
			}
		} else if progress.Completed == progress.Total {
			fmt.Fprintf(os.Stderr, "Rebuilt State: %d tokens\n", progress.Total)
		}
	}
	return nil
}

func autosave(ctx context.Context, current *conversation.Conversation, options runOptions) error {
	if options.autosave && options.sessionPath != "" {
		return current.Save(ctx, options.sessionPath)
	}
	return nil
}

type signalController struct {
	signals chan os.Signal
	exit    chan struct{}
	done    chan struct{}
	once    sync.Once
	mu      sync.Mutex
	cancel  context.CancelFunc
	active  bool
	count   int
}

func newSignalController() *signalController {
	controller := &signalController{
		signals: make(chan os.Signal, 2),
		exit:    make(chan struct{}),
		done:    make(chan struct{}),
	}
	signal.Notify(controller.signals, os.Interrupt, syscall.SIGTERM)
	go controller.loop()
	return controller
}

func (c *signalController) loop() {
	defer close(c.done)
	for value := range c.signals {
		c.mu.Lock()
		if c.active {
			c.count++
			cancel := c.cancel
			if cancel != nil {
				cancel()
			}
			if c.count == 1 {
				fmt.Fprintln(os.Stderr, "\nCancelling current generation...")
			} else {
				c.once.Do(func() { close(c.exit) })
			}
		} else {
			c.once.Do(func() { close(c.exit) })
		}
		if value == syscall.SIGTERM {
			c.once.Do(func() { close(c.exit) })
		}
		c.mu.Unlock()
	}
}

func (c *signalController) SetActive(cancel context.CancelFunc) {
	c.mu.Lock()
	c.cancel = cancel
	c.active = true
	c.count = 0
	c.mu.Unlock()
}

func (c *signalController) SetIdle() {
	c.mu.Lock()
	c.cancel = nil
	c.active = false
	c.count = 0
	c.mu.Unlock()
}

func (c *signalController) Exit() <-chan struct{} { return c.exit }

func (c *signalController) Close() {
	signal.Stop(c.signals)
	close(c.signals)
	<-c.done
}

func runConcurrent(args []string) error {
	options, err := parseRunOptions("concurrent", args)
	if err != nil {
		return err
	}
	if options.concurrency < 1 || options.concurrency > 8 {
		return errors.New("--concurrency must be between 1 and 8")
	}
	mode, err := terminal.ParseUIMode(options.ui)
	if err != nil {
		return err
	}
	selected, err := terminal.SelectUI(mode, terminal.Detect(os.Stdin, os.Stdout))
	if err != nil {
		return err
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	runtime, err := loadRuntime(ctx, options)
	if err != nil {
		return err
	}
	defer runtime.Close()
	factory := func() (*concurrentcli.Runner, error) {
		return concurrentcli.NewRunner(runtime.model, concurrentcli.Options{
			Conversation: newConversationOptions(options),
			Turn:         turnOptions(options),
			Prompt:       options.concurrentPrompt,
			Concurrency:  options.concurrency,
			BaseSeed:     42,
		})
	}
	if selected == terminal.UIPlain {
		runner, err := factory()
		if err != nil {
			return err
		}
		_, err = (concurrentcli.PlainRenderer{Out: os.Stdout, Status: os.Stderr}).Run(ctx, runner)
		if errors.Is(err, context.Canceled) {
			return nil
		}
		return err
	}
	provider := options.provider
	if provider == "auto" {
		provider = "mlx"
	}
	summary, err := concurrenttui.Run(
		ctx,
		factory,
		concurrenttui.Metadata{
			Model:       filepath.Base(options.modelPath),
			Provider:    provider,
			Concurrency: options.concurrency,
		},
		os.Stdin,
		os.Stdout,
	)
	fmt.Fprintln(os.Stderr, summary.String())
	if errors.Is(err, context.Canceled) {
		return nil
	}
	return err
}
