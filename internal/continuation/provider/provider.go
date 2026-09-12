// Package provider owns backend identity and remote transport construction.
// Conversation templates and tool protocols belong to the agent wire layer.
package provider

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

const (
	Local           = "local"
	ChatCompletions = "chat-completions"
	LightningPython = "rwkv-lightning-python"
	LightningCUDA   = "rwkv-lightning-cuda"
)

func IsLightning(kind string) bool {
	return kind == LightningPython || kind == LightningCUDA
}
func IsRemote(kind string) bool { return kind == ChatCompletions || IsLightning(kind) }
func Valid(kind string) bool    { return kind == Local || IsRemote(kind) }

// Endpoint replaces recognized API suffixes, retaining deployment prefixes and
// URL queries. Explicit custom completion endpoints remain usable.
func Endpoint(value, route string) string {
	parsed, err := url.Parse(strings.TrimSpace(value))
	if err != nil {
		return strings.TrimSpace(value)
	}
	path := strings.TrimRight(parsed.Path, "/")
	found := false
	for _, suffix := range []string{"/chat/completions", "/batch/completions", "/models"} {
		if strings.HasSuffix(path, suffix) {
			path = strings.TrimSuffix(path, suffix)
			found = true
			break
		}
	}
	if !found && strings.HasSuffix(path, "/completions") {
		return parsed.String()
	}
	if !strings.HasSuffix(path, "/v1") && !found {
		path += "/v1"
	}
	if path == "" {
		path = "/v1"
	}
	parsed.Path = path + "/" + route
	parsed.RawPath = ""
	return parsed.String()
}

func CompletionEndpoint(kind, value string) string {
	if kind == LightningCUDA {
		return Endpoint(value, "batch/completions")
	}
	return Endpoint(value, "chat/completions")
}

// Config is the remote transport configuration shared by API and CLI.
// Credential becomes a Bearer token for Chat Completions or a JSON password
// for Lightning. Wire/profile settings remain outside this transport layer.
type Config struct {
	Kind           string
	Endpoint       string
	Model          string
	Credential     string
	Headers        http.Header
	HTTPClient     *http.Client
	ChatThinking   chatcompletions.ThinkingMode
	ChatPromptMode chatcompletions.PromptMode
	ChatTokenLimit chatcompletions.TokenLimitField
	StopTokens     string
	StateID        string
	Stream         *bool
	BatchWait      time.Duration
}

func DefaultStopTokens(kind string) string {
	switch kind {
	case LightningPython:
		return "text"
	case LightningCUDA:
		return "eos"
	default:
		return ""
	}
}

// NewRemote maps common configuration to the selected adapter. The returned
// generator retains optional native tool-chat capabilities for Chat Completions.
func NewRemote(config Config) (continuation.Generator, error) {
	endpoint := CompletionEndpoint(config.Kind, config.Endpoint)
	switch config.Kind {
	case ChatCompletions:
		return chatcompletions.New(chatcompletions.Config{
			Endpoint: endpoint, Model: config.Model, APIKey: config.Credential,
			Headers: config.Headers, HTTPClient: config.HTTPClient,
			Thinking: config.ChatThinking, PromptMode: config.ChatPromptMode, TokenLimit: config.ChatTokenLimit,
		})
	case LightningPython, LightningCUDA:
		stops := config.StopTokens
		if stops == "" {
			stops = DefaultStopTokens(config.Kind)
		}
		mode, ids, err := ParseStopTokens(stops)
		if err != nil {
			return nil, err
		}
		if config.Kind == LightningPython {
			if mode == rwkvlightning.StopTokenEOS {
				return nil, fmt.Errorf("Python Lightning requires text stop tokens; integer token IDs are CUDA-specific")
			}
			if strings.TrimSpace(config.StateID) != "" {
				return nil, fmt.Errorf("Python Lightning raw continuation does not support uploaded state_id")
			}
		} else if mode == rwkvlightning.StopTokenText {
			return nil, fmt.Errorf("CUDA Lightning requires integer stop token IDs; decoded-text stops are handled locally")
		}
		client, err := rwkvlightning.New(rwkvlightning.Config{
			Endpoint: endpoint, Model: config.Model, Password: config.Credential,
			Headers: config.Headers, HTTPClient: config.HTTPClient,
			StopTokenMode: mode, StopTokenIDs: ids, StateID: config.StateID,
			Stream: config.Stream, BatchWait: config.BatchWait,
		})
		if err != nil {
			return nil, err
		}
		if config.Kind == LightningPython {
			return pythonGenerator{client}, nil
		}
		return client, nil
	default:
		return nil, fmt.Errorf("unsupported remote provider %q", config.Kind)
	}
}

// Python's raw route ignores state_id; reject it instead of silently generating
// from zero state when the caller requested an uploaded state.
type pythonGenerator struct{ continuation.Generator }

func (p pythonGenerator) Continue(ctx context.Context, request continuation.Request, sink continuation.EventSink) (continuation.Result, error) {
	if strings.TrimSpace(request.StateID) != "" {
		return continuation.Result{}, fmt.Errorf("%w: Python Lightning raw continuation does not support uploaded state_id", continuation.ErrInvalidRequest)
	}
	return p.Generator.Continue(ctx, request, sink)
}

// ParseStopTokens resolves the shared API and CLI stop-token setting.
func ParseStopTokens(value string) (rwkvlightning.StopTokenMode, []int, error) {
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
					"stop tokens must be text, none, eos, or a comma-separated list of non-negative token IDs",
				)
			}
			tokens = append(tokens, token)
		}
		return rwkvlightning.StopTokenEOS, tokens, nil
	}
}
