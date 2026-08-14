package api

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
	localcontinuation "github.com/no22/RWKV-Agent/internal/continuation/local"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
	"github.com/no22/RWKV-Agent/internal/inference"
	rwkvbackend "github.com/no22/RWKV-Agent/internal/inference/backend/rwkvmobile"
)

type generatorSource interface {
	newGenerator(context.Context) (continuation.Generator, io.Closer, error)
	status() Status
	close() error
}

type localSource struct {
	core  *inference.Core
	model inference.Model
	base  Status
}

func (s *localSource) newGenerator(ctx context.Context) (continuation.Generator, io.Closer, error) {
	session, err := s.model.NewSession(ctx, inference.SessionOptions{})
	if err != nil {
		return nil, nil, fmt.Errorf("create local model session: %w", err)
	}
	generator, err := localcontinuation.New(session)
	if err != nil {
		_ = session.Close()
		return nil, nil, fmt.Errorf("initialize local continuation: %w", err)
	}
	return generator, session, nil
}

func (s *localSource) status() Status { return s.base }
func (s *localSource) close() error   { return s.core.Close() }

type remoteSource struct {
	generator continuation.Generator
	base      Status
}

func (s *remoteSource) newGenerator(context.Context) (continuation.Generator, io.Closer, error) {
	return s.generator, noopCloser{}, nil
}

func (s *remoteSource) status() Status { return s.base }
func (s *remoteSource) close() error   { return nil }

type noopCloser struct{}

func (noopCloser) Close() error { return nil }

func buildSource(ctx context.Context, config Config, progress func(Status)) (generatorSource, error) {
	switch config.Provider {
	case ProviderLocal:
		return buildLocalSource(ctx, config, progress)
	case ProviderChatCompletions:
		return buildChatCompletionsSource(config)
	case ProviderRWKVLightning:
		return buildRWKVLightningSource(config)
	default:
		return nil, fmt.Errorf("unsupported provider %q", config.Provider)
	}
}

func buildLocalSource(ctx context.Context, config Config, progress func(Status)) (generatorSource, error) {
	backend := rwkvbackend.New(rwkvbackend.Options{
		Provider:       config.NativeProvider,
		MaxActiveBatch: config.MaxActiveBatch,
		QueueCapacity:  64,
	})
	core, err := inference.NewCore(backend)
	if err != nil {
		return nil, fmt.Errorf("initialize inference core: %w", err)
	}
	model, err := core.LoadModel(ctx, inference.LoadRequest{
		Source: inference.ModelSource{
			Path:          config.Model,
			TokenizerPath: config.TokenizerPath,
		},
		Backend: inference.BackendID(config.Backend),
	}, func(value inference.Progress) error {
		if progress != nil {
			message := value.Stage
			if value.Total > 0 {
				message = fmt.Sprintf("%s %d/%d", value.Stage, value.Completed, value.Total)
			}
			progress(Status{State: ModelLoading, Provider: ProviderLocal, Model: config.Model, Message: message})
		}
		return nil
	})
	if err != nil {
		_ = core.Close()
		return nil, fmt.Errorf("load local model: %w", err)
	}
	info := model.Info()
	return &localSource{
		core:  core,
		model: model,
		base: Status{
			State:        ModelReady,
			Provider:     ProviderLocal,
			Model:        string(info.ID),
			Backend:      string(info.Backend),
			Format:       string(info.Format),
			Architecture: info.Architecture,
			Message:      "Local model ready",
		},
	}, nil
}

func buildChatCompletionsSource(config Config) (generatorSource, error) {
	headers, names, err := validatedHeaders(config.Headers)
	if err != nil {
		return nil, err
	}
	client, err := chatcompletions.New(chatcompletions.Config{
		Endpoint:   normalizeChatEndpoint(config.Endpoint),
		Model:      config.Model,
		APIKey:     config.APIKey,
		Thinking:   chatcompletions.ThinkingMode(config.ChatThinking),
		PromptMode: chatcompletions.PromptMode(config.ChatPromptMode),
		TokenLimit: chatcompletions.TokenLimitField(config.ChatTokenLimit),
		Headers:    headers,
	})
	if err != nil {
		return nil, fmt.Errorf("initialize Chat Completions continuation: %w", err)
	}
	return &remoteSource{
		generator: client,
		base: Status{
			State:       ModelReady,
			Provider:    ProviderChatCompletions,
			Model:       config.Model,
			Endpoint:    normalizeChatEndpoint(config.Endpoint),
			Backend:     "openai-compatible",
			Message:     "Remote model configured",
			HeaderNames: names,
			HasAPIKey:   strings.TrimSpace(config.APIKey) != "",
		},
	}, nil
}

func buildRWKVLightningSource(config Config) (generatorSource, error) {
	headers, names, err := validatedHeaders(config.Headers)
	if err != nil {
		return nil, err
	}
	client, err := rwkvlightning.New(rwkvlightning.Config{
		Endpoint:      normalizeRWKVEndpoint(config.Endpoint),
		Model:         config.Model,
		Password:      config.Password,
		StopTokenMode: rwkvlightning.StopTokenMode(config.RWKVStopTokens),
		Stream:        config.Stream,
		BatchWait:     time.Duration(config.RemoteBatchWaitMS) * time.Millisecond,
		Headers:       headers,
	})
	if err != nil {
		return nil, fmt.Errorf("initialize RWKV Lightning continuation: %w", err)
	}
	return &remoteSource{
		generator: client,
		base: Status{
			State:       ModelReady,
			Provider:    ProviderRWKVLightning,
			Model:       config.Model,
			Endpoint:    normalizeRWKVEndpoint(config.Endpoint),
			Backend:     "rwkv-lightning",
			Message:     "Remote model configured",
			HeaderNames: names,
			HasAPIKey:   strings.TrimSpace(config.Password) != "",
		},
	}, nil
}

func normalizeRWKVEndpoint(value string) string {
	value = strings.TrimRight(strings.TrimSpace(value), "/")
	switch {
	case strings.HasSuffix(value, "/v1/models"):
		return strings.TrimSuffix(value, "/models") + "/batch/completions"
	case strings.HasSuffix(value, "/v1/batch/completions"), strings.HasSuffix(value, "/batch/completions"):
		return value
	case strings.HasSuffix(value, "/v1"):
		return value + "/batch/completions"
	default:
		return value + "/v1/batch/completions"
	}
}

func normalizeChatEndpoint(value string) string {
	value = strings.TrimRight(strings.TrimSpace(value), "/")
	switch {
	case strings.HasSuffix(value, "/v1/models"):
		return strings.TrimSuffix(value, "/models") + "/chat/completions"
	case strings.HasSuffix(value, "/v1/chat/completions"), strings.HasSuffix(value, "/chat/completions"):
		return value
	case strings.HasSuffix(value, "/v1"):
		return value + "/chat/completions"
	default:
		return value + "/v1/chat/completions"
	}
}

func normalizeModelsEndpoint(value string) string {
	value = strings.TrimRight(strings.TrimSpace(value), "/")
	switch {
	case strings.HasSuffix(value, "/v1/models"):
		return value
	case strings.HasSuffix(value, "/v1/batch/completions"):
		return strings.TrimSuffix(value, "/batch/completions") + "/models"
	case strings.HasSuffix(value, "/batch/completions"):
		return strings.TrimSuffix(value, "/batch/completions") + "/v1/models"
	case strings.HasSuffix(value, "/v1/chat/completions"):
		return strings.TrimSuffix(value, "/chat/completions") + "/models"
	case strings.HasSuffix(value, "/chat/completions"):
		return strings.TrimSuffix(value, "/chat/completions") + "/models"
	case strings.HasSuffix(value, "/v1"):
		return value + "/models"
	default:
		return value + "/v1/models"
	}
}

func validatedHeaders(values map[string]string) (http.Header, []string, error) {
	headers := make(http.Header, len(values))
	names := make([]string, 0, len(values))
	for rawName, rawValue := range values {
		name := http.CanonicalHeaderKey(strings.TrimSpace(rawName))
		value := strings.TrimSpace(rawValue)
		if name == "" || strings.ContainsAny(name, " \t\r\n:") {
			return nil, nil, fmt.Errorf("invalid HTTP header name %q", rawName)
		}
		if strings.ContainsAny(value, "\r\n") {
			return nil, nil, fmt.Errorf("HTTP header %s contains a newline", name)
		}
		headers.Set(name, value)
		names = append(names, name)
	}
	sort.Strings(names)
	return headers, names, nil
}

// ResolveTokenizer locates the tokenizer used for a local model.
func ResolveTokenizer(modelPath, explicit string) (string, error) {
	if explicit = strings.TrimSpace(explicit); explicit != "" {
		absolute, err := filepath.Abs(explicit)
		if err != nil {
			return "", err
		}
		if info, err := os.Stat(absolute); err != nil || info.IsDir() {
			if err == nil {
				err = fmt.Errorf("path is a directory")
			}
			return "", fmt.Errorf("tokenizer: %w", err)
		}
		return absolute, nil
	}
	const filename = "rwkv_vocab_v20230424.txt"
	candidates := []string{}
	if strings.EqualFold(filepath.Ext(modelPath), ".pth") {
		candidates = append(candidates, filepath.Join(filepath.Dir(modelPath), filename))
	} else if modelPath != "" {
		candidates = append(candidates, filepath.Join(modelPath, filename))
	}
	if executable, err := os.Executable(); err == nil {
		candidates = append(candidates, filepath.Join(filepath.Dir(executable), "assets", filename))
	}
	candidates = append(candidates,
		filepath.Join("dist", "assets", filename),
		filepath.Join("third_party", "rwkv-mobile", "assets", filename),
	)
	for _, candidate := range candidates {
		absolute, err := filepath.Abs(candidate)
		if err != nil {
			continue
		}
		if info, err := os.Stat(absolute); err == nil && !info.IsDir() {
			return absolute, nil
		}
	}
	return "", fmt.Errorf("tokenizer %q was not found; choose it explicitly", filename)
}
