package mlx

import (
	"context"
	"errors"
)

var ErrUnavailable = errors.New("native MLX backend is unavailable in this build")

type GenerateOptions struct {
	MaxTokens   int
	Temperature float32
	TopK        int
	TopP        float32
}

type Stats struct {
	PrefillTokensPerSecond float64
	DecodeTokensPerSecond  float64
}

type runtimeImpl interface {
	generate(context.Context, string, GenerateOptions, func(string) error) error
	clearState() error
	stats() Stats
	close() error
}

type Runtime struct {
	impl runtimeImpl
}

func Available() bool {
	return platformAvailable()
}

func Open(modelPath, tokenizerPath string) (*Runtime, error) {
	impl, err := platformOpen(modelPath, tokenizerPath)
	if err != nil {
		return nil, err
	}
	return &Runtime{impl: impl}, nil
}

func (r *Runtime) Generate(ctx context.Context, prompt string, options GenerateOptions, write func(string) error) error {
	if r == nil || r.impl == nil {
		return errors.New("MLX runtime is closed")
	}
	return r.impl.generate(ctx, prompt, options, write)
}

func (r *Runtime) ClearState() error {
	if r == nil || r.impl == nil {
		return errors.New("MLX runtime is closed")
	}
	return r.impl.clearState()
}

func (r *Runtime) Stats() Stats {
	if r == nil || r.impl == nil {
		return Stats{}
	}
	return r.impl.stats()
}

func (r *Runtime) Close() error {
	if r == nil || r.impl == nil {
		return nil
	}
	err := r.impl.close()
	r.impl = nil
	return err
}
