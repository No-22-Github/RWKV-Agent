package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"os/signal"
	"syscall"
	"time"

	"github.com/no22/RWKV-Agent/internal/client"
)

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "run":
		run(os.Args[2:])
	case "complete":
		complete(os.Args[2:])
	case "llama":
		llama(os.Args[2:])
	default:
		usage()
		os.Exit(2)
	}
}

func usage() {
	fmt.Fprintln(os.Stderr, "rwkv-cli run --engine <rwkv_server> --model <model> --tokenizer <tokenizer> --backend <name> [--prompt text]")
	fmt.Fprintln(os.Stderr, "rwkv-cli complete --url <runtime URL> --prompt <text>")
	fmt.Fprintln(os.Stderr, "rwkv-cli llama --engine <llama-cli> --model <rwkv.gguf> [--prompt text]")
}

func commonFlags(name string) (*flag.FlagSet, *string, *string, *int, *float64) {
	fs := flag.NewFlagSet(name, flag.ExitOnError)
	url := fs.String("url", "http://127.0.0.1:8000", "rwkv-mobile server URL")
	prompt := fs.String("prompt", "", "prompt; omit for interactive mode")
	maxTokens := fs.Int("max-tokens", 256, "maximum generated tokens")
	temperature := fs.Float64("temperature", 1, "sampling temperature")
	return fs, url, prompt, maxTokens, temperature
}

func run(args []string) {
	fs, url, prompt, maxTokens, temperature := commonFlags("run")
	engine := fs.String("engine", "rwkv_server", "path to rwkv-mobile rwkv_server executable")
	model := fs.String("model", "", "model path")
	tokenizer := fs.String("tokenizer", "", "tokenizer path")
	backend := fs.String("backend", "", "rwkv-mobile backend, e.g. web_rwkv or mnn")
	port := fs.Int("port", 8000, "local runtime port")
	fs.Parse(args)
	if *model == "" || *tokenizer == "" || *backend == "" {
		fs.Usage()
		os.Exit(2)
	}
	*url = fmt.Sprintf("http://127.0.0.1:%d", *port)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	cmd := exec.CommandContext(ctx, *engine, "--host", "127.0.0.1", "--port", fmt.Sprint(*port), "--model", *model, "--tokenizer", *tokenizer, "--backend", *backend)
	cmd.Stdout, cmd.Stderr = os.Stderr, os.Stderr
	if err := cmd.Start(); err != nil {
		fatal("start rwkv runtime: %v", err)
	}
	defer func() { _ = cmd.Process.Signal(os.Interrupt); _ = cmd.Wait() }()
	if err := waitForHealth(ctx, *url); err != nil {
		fatal("runtime did not become ready: %v", err)
	}
	generate(ctx, *url, *prompt, *maxTokens, *temperature)
}

func complete(args []string) {
	fs, url, prompt, maxTokens, temperature := commonFlags("complete")
	fs.Parse(args)
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()
	generate(ctx, *url, *prompt, *maxTokens, *temperature)
}

// llama uses llama.cpp's Metal backend. It is the verified minimal path for
// RWKV GGUF models on Apple Silicon.
func llama(args []string) {
	fs := flag.NewFlagSet("llama", flag.ExitOnError)
	engine := fs.String("engine", "llama-cli", "path to a llama.cpp llama-cli executable")
	model := fs.String("model", "", "RWKV GGUF model path")
	prompt := fs.String("prompt", "", "prompt; omit for interactive mode")
	maxTokens := fs.Int("max-tokens", 256, "maximum generated tokens")
	fs.Parse(args)
	if *model == "" {
		fs.Usage()
		os.Exit(2)
	}

	commandArgs := []string{"-m", *model, "-n", fmt.Sprint(*maxTokens), "--no-warmup", "--simple-io"}
	if *prompt != "" {
		commandArgs = append(commandArgs, "--single-turn", "-p", *prompt)
	}
	cmd := exec.Command(*engine, commandArgs...)
	cmd.Stdin, cmd.Stdout, cmd.Stderr = os.Stdin, os.Stdout, os.Stderr
	if err := cmd.Run(); err != nil {
		fatal("llama.cpp generation failed: %v", err)
	}
}

func waitForHealth(ctx context.Context, url string) error {
	ticker := time.NewTicker(250 * time.Millisecond)
	defer ticker.Stop()
	timeout := time.NewTimer(2 * time.Minute)
	defer timeout.Stop()
	for {
		if err := client.Healthy(ctx, url); err == nil {
			return nil
		}
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-timeout.C:
			return fmt.Errorf("timed out after two minutes")
		case <-ticker.C:
		}
	}
}

func generate(ctx context.Context, url, prompt string, maxTokens int, temperature float64) {
	if prompt != "" {
		completePrompt(ctx, url, prompt, maxTokens, temperature)
		return
	}
	fmt.Fprintln(os.Stderr, "Interactive continuation mode. Enter a prompt; Ctrl-C exits.")
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")
		if !scanner.Scan() {
			return
		}
		completePrompt(ctx, url, scanner.Text(), maxTokens, temperature)
	}
}

func completePrompt(ctx context.Context, url, prompt string, maxTokens int, temperature float64) {
	fmt.Print(prompt)
	err := client.Complete(ctx, url, client.CompletionRequest{Prompt: prompt, MaxTokens: maxTokens, Temperature: temperature}, func(text string) error { _, err := io.WriteString(os.Stdout, text); return err })
	fmt.Println()
	if err != nil && ctx.Err() == nil {
		fmt.Fprintln(os.Stderr, "generation failed:", err)
	}
}

func fatal(format string, args ...any) { fmt.Fprintf(os.Stderr, format+"\n", args...); os.Exit(1) }
