package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"os/signal"
	"path/filepath"
	"strings"
	"syscall"

	"github.com/no22/RWKV-Agent/internal/native/mlx"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}

	switch os.Args[1] {
	case "run":
		run(os.Args[2:])
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, "rwkv-cli run --model <MLX model directory> [--tokenizer <vocab file>] [--prompt <text>]")
}

func run(args []string) {
	fs := flag.NewFlagSet("run", flag.ExitOnError)
	model := fs.String("model", "", "MLX model directory containing config.json and safetensors")
	tokenizer := fs.String("tokenizer", "", "RWKV World tokenizer vocabulary; defaults to the model directory")
	prompt := fs.String("prompt", "", "prompt; omit for interactive mode")
	maxTokens := fs.Int("max-tokens", 256, "maximum generated tokens")
	temperature := fs.Float64("temperature", 1, "sampling temperature")
	topK := fs.Int("top-k", 128, "top-k sampling cutoff")
	topP := fs.Float64("top-p", 0.8, "top-p sampling cutoff")
	raw := fs.Bool("raw", false, "use the prompt verbatim instead of the RWKV chat template")
	reasoning := fs.Bool("reasoning", true, "include the G1 fast-thinking prompt markers")
	fs.Parse(args)

	if *model == "" {
		fs.Usage()
		os.Exit(2)
	}
	if *tokenizer == "" {
		*tokenizer = filepath.Join(*model, "rwkv_vocab_v20230424.txt")
	}
	if *maxTokens <= 0 || *temperature <= 0 || *topK <= 0 || *topP <= 0 || *topP > 1 {
		fatal("invalid sampling options")
	}
	if !mlx.Available() {
		fatal("MLX support is not present in this build; run ./scripts/build-mlx.sh on Apple Silicon")
	}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	fmt.Fprintln(os.Stderr, "Loading native MLX model...")
	runtime, err := mlx.Open(*model, *tokenizer)
	if err != nil {
		fatal("load native MLX model: %v", err)
	}
	defer runtime.Close()

	options := mlx.GenerateOptions{
		MaxTokens:   *maxTokens,
		Temperature: float32(*temperature),
		TopK:        *topK,
		TopP:        float32(*topP),
	}
	generate := func(input string) {
		formatted := renderPrompt(input, *raw, *reasoning)
		err := runtime.Generate(ctx, formatted, options, func(text string) error {
			_, writeErr := io.WriteString(os.Stdout, text)
			return writeErr
		})
		fmt.Println()
		if err != nil && ctx.Err() == nil {
			fmt.Fprintln(os.Stderr, "generation failed:", err)
		}
	}

	if *prompt != "" {
		generate(*prompt)
		printSpeeds(runtime)
		return
	}

	fmt.Fprintln(os.Stderr, "Interactive mode. Enter a prompt; Ctrl-C exits.")
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			break
		}
		if input := strings.TrimSpace(scanner.Text()); input != "" {
			generate(input)
		}
		if ctx.Err() != nil {
			break
		}
	}
	if err := scanner.Err(); err != nil {
		fmt.Fprintln(os.Stderr, "read prompt:", err)
	}
	printSpeeds(runtime)
}

func renderPrompt(prompt string, raw, reasoning bool) string {
	if raw {
		return prompt
	}
	formatted := "User: " + prompt + "\n\nAssistant:"
	if reasoning {
		formatted = "<|bos|>" + formatted + " <think>\n</think>"
	}
	return formatted
}

func printSpeeds(runtime *mlx.Runtime) {
	stats := runtime.Stats()
	if stats.PrefillTokensPerSecond > 0 {
		fmt.Fprintf(os.Stderr, "Prefill: %.1f tok/s; decode: %.1f tok/s\n", stats.PrefillTokensPerSecond, stats.DecodeTokensPerSecond)
	}
}

func fatal(format string, args ...any) {
	fmt.Fprintf(os.Stderr, format+"\n", args...)
	os.Exit(1)
}
