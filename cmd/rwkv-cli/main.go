package main

import (
	"bufio"
	"context"
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

	"github.com/no22/RWKV-Agent/internal/agent"
	agenteval "github.com/no22/RWKV-Agent/internal/agent/eval"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
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
	modelPath          string
	backend            string
	provider           string
	tokenizer          string
	sessionPath        string
	prompt             string
	maxTokens          int
	decisionMaxTokens  int
	routeMaxTokens     int
	tracePromptBytes   int
	temperature        float64
	topK               int
	topP               float64
	presencePenalty    float64
	frequencyPenalty   float64
	penaltyDecay       float64
	thinkingMode       string
	thinkingExplicit   bool
	reasoning          bool
	reasoningExplicit  bool
	fewShot            bool
	autosave           bool
	nativeState        string
	concurrency        int
	concurrentPrompt   string
	ui                 string
	workspace          string
	maxSteps           int
	completion         string
	apiURL             string
	apiKeyEnv          string
	chatThinking       string
	chatPromptMode     string
	chatPromptExplicit bool
	chatTokenLimit     string
	apiPasswordEnv     string
	apiStopTokens      string
	apiStream          bool
	apiHeaderEnvs      stringListFlag
	evalSuite          string
	evalSuiteExplicit  bool
	evalCasesPath      string
	evalOutput         string
	evalCaseIDs        stringListFlag
	evalCaseTimeout    time.Duration
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
  rwkv-cli agent-eval --model <path or remote model ID> [--suite boundary|smoke|assistant] [--output <directory>]
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
		fs.IntVar(&options.maxSteps, "max-steps", 6, "maximum model steps including protocol retries")
		fs.IntVar(&options.decisionMaxTokens, "decision-max-tokens", 96, "maximum generated tokens for tool selection")
		fs.IntVar(&options.routeMaxTokens, "route-max-tokens", 16, "maximum generated tokens for respond/inspect routing")
		fs.BoolVar(&options.fewShot, "few-shot", false, "enable agent decision trajectory examples")
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
			"rwkv_lightning stop_tokens form: text, none, eos, or a comma-separated token ID list",
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
		} else {
			fs.StringVar(&options.evalSuite, "suite", agenteval.SuiteBoundary, "built-in Agent eval suite: boundary, smoke, or assistant")
			fs.StringVar(&options.evalCasesPath, "cases", "", "versioned custom Agent eval case JSON; conflicts with --suite")
			fs.StringVar(&options.evalOutput, "output", "", "new directory for run.json, trace.jsonl, and summary.json")
			fs.Var(&options.evalCaseIDs, "case", "repeatable built-in or file-backed case ID to run")
			fs.DurationVar(&options.evalCaseTimeout, "case-timeout", 2*time.Minute, "timeout for each isolated eval case")
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
		}
	})
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
		if name == "agent-eval" && options.evalCaseTimeout <= 0 {
			return options, errors.New("--case-timeout must be positive")
		}
		if name == "agent-eval" {
			if options.evalSuite != agenteval.SuiteBoundary &&
				options.evalSuite != agenteval.SuiteSmoke &&
				options.evalSuite != agenteval.SuiteAssistant {
				return options, fmt.Errorf(
					"unsupported Agent eval suite %q; expected boundary, smoke, or assistant",
					options.evalSuite,
				)
			}
			if options.evalCasesPath != "" && options.evalSuiteExplicit {
				return options, errors.New("--suite and --cases cannot be used together")
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
	if agentMode && options.decisionMaxTokens <= 0 {
		return options, errors.New("invalid agent decision token limit")
	}
	if agentMode && options.routeMaxTokens <= 0 {
		return options, errors.New("invalid agent route token limit")
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
		client, err := rwkvlightning.New(rwkvlightning.Config{
			Endpoint:      options.apiURL,
			Model:         options.modelPath,
			Password:      os.Getenv(options.apiPasswordEnv),
			StopTokenMode: stopTokenMode,
			StopTokenIDs:  stopTokenIDs,
			Stream:        &options.apiStream,
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

func agentRunnerOptions(options runOptions, observe func(agent.Event)) agent.Options {
	return agent.Options{
		MaxSteps:                options.maxSteps,
		ProtocolRetries:         1,
		DecisionMaxOutputTokens: options.decisionMaxTokens,
		ControlPrompt:           agent.ControlPromptSystem,
		Protocol:                agent.G1IProtocol{FewShot: options.fewShot},
		Renderer: agent.RWKVChatRenderer{
			ThinkingMode: inference.ThinkingMode(options.thinkingMode),
		},
		Router:               agent.G1IRouteProtocol{},
		RouteRenderer:        agent.RWKVChatRenderer{},
		RouteRetries:         1,
		RouteMaxOutputTokens: options.routeMaxTokens,
		TracePromptBytes:     options.tracePromptBytes,
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
		Observe: observe,
	}
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
	source, err := newAgentGeneratorSource(ctx, options)
	if err != nil {
		return err
	}
	defer source.Close()
	generator, generatorCloser, err := source.newGenerator(ctx)
	if err != nil {
		return err
	}
	defer generatorCloser.Close()
	tools, err := agent.WorkspaceTools(options.workspace)
	if err != nil {
		return fmt.Errorf("initialize agent workspace: %w", err)
	}
	mockProvider, err := assistanttools.DefaultMockProvider()
	if err != nil {
		return fmt.Errorf("initialize assistant mock provider: %w", err)
	}
	assistant, err := assistanttools.AssistantTools(assistanttools.Options{
		Provider:  mockProvider,
		Workspace: options.workspace,
	})
	if err != nil {
		return fmt.Errorf("initialize assistant tools: %w", err)
	}
	tools = append(tools, assistant...)
	theme := terminal.NewTheme(terminal.SupportsStyle(os.Stderr))
	var observe func(agent.Event)
	if selected == terminal.UIPlain {
		observe = func(event agent.Event) {
			switch event.Kind {
			case agent.EventRouteDone:
				if event.Err != nil {
					fmt.Fprintf(
						os.Stderr,
						"%s %s: %v\n",
						theme.Render(theme.Warning, "Route fallback"),
						event.Route,
						event.Err,
					)
				} else {
					fmt.Fprintf(
						os.Stderr,
						"%s %s\n",
						theme.Render(theme.Accent, "Route"),
						event.Route,
					)
				}
			case agent.EventModelStart:
				fmt.Fprintf(os.Stderr, "%s step %d\n", theme.Render(theme.Muted, "Agent"), event.Step)
			case agent.EventRetry:
				fmt.Fprintln(os.Stderr, theme.Render(theme.Warning, "Retrying invalid model action"))
			case agent.EventToolStart:
				fmt.Fprintf(os.Stderr, "%s %s\n", theme.Render(theme.Accent, "Tool"), event.Tool)
			case agent.EventToolDone:
				if event.Err != nil {
					fmt.Fprintf(os.Stderr, "%s %s: %v\n", theme.Render(theme.Warning, "Tool failed"), event.Tool, event.Err)
				}
			}
		}
	}
	runner, err := agent.NewRunner(
		generator,
		tools,
		agentRunnerOptions(options, observe),
	)
	if err != nil {
		return err
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
			runner,
			agenttui.Metadata{
				Model:     filepath.Base(options.modelPath),
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
	result, err := runner.Run(ctx, options.prompt)
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
		cases, err = agenteval.LoadCases(options.evalCasesPath)
		if err != nil {
			return fmt.Errorf("load Agent eval cases: %w", err)
		}
		suite = "custom"
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
		Cases:       cases,
		Suite:       suite,
		Model:       model,
		Runner:      agentRunnerOptions(options, nil),
		CaseTimeout: options.evalCaseTimeout,
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
		"Agent eval (%s): %d/%d cases passed; answer %s; route %s; protocol %s\n",
		suite,
		metrics.TaskSuccess.Correct,
		metrics.TaskSuccess.Total,
		formatEvalScore(metrics.AnswerAccuracy),
		formatEvalScore(metrics.RouteAccuracy),
		formatEvalScore(metrics.ProtocolValidity),
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
// mode. "text" forwards the protocol's decoded-text stops, which is the wire type
// rwkv_lightning documents. "none" omits the field, "eos" sends the legacy integer
// EOS list, and an explicit comma-separated list passes those token IDs through.
func parseAPIStopTokens(value string) (rwkvlightning.StopTokenMode, []int, error) {
	switch trimmed := strings.ToLower(strings.TrimSpace(value)); trimmed {
	case "", "text":
		return rwkvlightning.StopTokenText, nil, nil
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
					"--api-stop-tokens must be text, none, eos, or a comma-separated list of non-negative token IDs",
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
