package main

import (
	"bufio"
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"sync"
	"syscall"

	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
	rwkvbackend "github.com/no22/RWKV-Agent/internal/inference/backend/rwkvmobile"
	"github.com/no22/RWKV-Agent/internal/native/converter"
	"github.com/no22/RWKV-Agent/internal/terminal"
	concurrenttui "github.com/no22/RWKV-Agent/internal/tui/concurrent"
)

type runOptions struct {
	modelPath         string
	backend           string
	provider          string
	tokenizer         string
	sessionPath       string
	prompt            string
	maxTokens         int
	temperature       float64
	topK              int
	topP              float64
	presencePenalty   float64
	frequencyPenalty  float64
	penaltyDecay      float64
	reasoning         bool
	reasoningExplicit bool
	autosave          bool
	nativeState       string
	concurrency       int
	concurrentPrompt  string
	ui                string
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
  rwkv-cli run --model <MLX model directory> [--prompt <text> | --session <bundle>]
  rwkv-cli concurrent --model <MLX model directory> [--concurrency 1..8] [--ui auto|tui|plain]
  rwkv-cli bench --model <MLX model directory> [--concurrency 1..8]`)
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
	fs.StringVar(&options.modelPath, "model", "", "MLX model directory")
	fs.StringVar(&options.backend, "backend", "auto", "inference backend: auto or rwkvmobile")
	fs.StringVar(&options.provider, "provider", "auto", "native provider: auto or mlx")
	fs.StringVar(&options.tokenizer, "tokenizer", "", "RWKV World tokenizer; defaults to model directory")
	fs.IntVar(&options.maxTokens, "max-tokens", 256, "maximum generated tokens")
	fs.Float64Var(&options.temperature, "temperature", 1, "sampling temperature")
	fs.IntVar(&options.topK, "top-k", 128, "top-k sampling cutoff")
	fs.Float64Var(&options.topP, "top-p", 0.5, "top-p sampling cutoff")
	fs.Float64Var(&options.presencePenalty, "presence-penalty", 2, "RWKV presence penalty")
	fs.Float64Var(&options.frequencyPenalty, "frequency-penalty", 0.1, "RWKV frequency penalty")
	fs.Float64Var(&options.penaltyDecay, "penalty-decay", 0.99, "RWKV repetition-penalty decay")
	fs.BoolVar(&options.reasoning, "reasoning", false, "enable the RWKV G1 fast-thinking profile")
	fs.StringVar(&options.nativeState, "native-state", "auto", "native State mode: auto, off, or required")
	switch name {
	case "run":
		fs.StringVar(&options.sessionPath, "session", "", "session bundle path")
		fs.StringVar(&options.prompt, "prompt", "", "single-turn prompt; omit for the REPL")
		fs.BoolVar(&options.autosave, "autosave", false, "save the session after each committed turn")
	case "concurrent":
		fs.IntVar(&options.concurrency, "concurrency", 4, "number of overlapping sessions")
		fs.StringVar(&options.concurrentPrompt, "concurrent-prompt", "用一句话介绍 RWKV。", "prompt for every session")
		fs.StringVar(&options.ui, "ui", "auto", "concurrent renderer: auto, tui, or plain")
	}
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	fs.Visit(func(value *flag.Flag) {
		if value.Name == "reasoning" {
			options.reasoningExplicit = true
		}
	})
	if options.modelPath == "" {
		fs.Usage()
		return options, fmt.Errorf("%s requires --model", name)
	}
	if options.tokenizer == "" {
		options.tokenizer = filepath.Join(options.modelPath, "rwkv_vocab_v20230424.txt")
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
	if name == "concurrent" {
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
		Profile:     inference.DefaultPromptProfile(options.reasoning),
		NativeState: options.nativeState,
	}
}

func loadConversationOptions(options runOptions) conversation.Options {
	value := conversation.Options{
		NativeState:               options.nativeState,
		AllowPromptProfileUpgrade: true,
	}
	if options.reasoningExplicit {
		value.Profile = inference.DefaultPromptProfile(options.reasoning)
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
	options.reasoning = current.Profile().Reasoning
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
		options.reasoning = current.Profile().Reasoning
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
