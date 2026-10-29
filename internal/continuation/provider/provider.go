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
	"github.com/no22/RWKV-Agent/internal/continuation/irwkv"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
)

const (
	Local           = "local"
	ChatCompletions = "chat-completions"
	LightningPython = "rwkv-lightning-python"
	LightningCUDA   = "rwkv-lightning-cuda"
	// IRWKV is an iRWKV server (rwkv-org/irwkv, a vLLM fork) driven through
	// raw text Completions with the harness's own RWKV prompt.
	IRWKV = "irwkv"
)

func IsLightning(kind string) bool {
	return kind == LightningPython || kind == LightningCUDA
}

// IsRawRWKV reports a remote RWKV backend that continues the harness's own
// rendered prompt and takes the RWKV stop-token setting.
func IsRawRWKV(kind string) bool { return IsLightning(kind) || kind == IRWKV }
func IsRemote(kind string) bool  { return kind == ChatCompletions || IsRawRWKV(kind) }
func Valid(kind string) bool     { return kind == Local || IsRemote(kind) }

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
	switch kind {
	case LightningCUDA:
		return Endpoint(value, "batch/completions")
	case IRWKV:
		return Endpoint(value, "completions")
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
	// ChatTemplateEnableThinking is sent as chat_template_kwargs.enable_thinking
	// when non-nil.
	ChatTemplateEnableThinking *bool
	// ChatIncludeTopK sends the sampling top_k upstream (vLLM/SGLang).
	ChatIncludeTopK bool
	// ChatReasoningEffort is sent as reasoning_effort when non-empty.
	ChatReasoningEffort string
	// ChatSystemSuffix is appended to every Chat Completions system message
	// (distillation teacher instructions); see chatcompletions.Config.
	ChatSystemSuffix string
	StopTokens       string
	StateID          string
	AdapterID        string
	Stream           *bool
	BatchWait        time.Duration
	// BatchMax caps one coalesced RWKV Lightning request; zero is no cap.
	BatchMax int
	// BatchInflight caps concurrently running coalesced requests; zero is no cap.
	BatchInflight int
	// LoopGuard ends looping RWKV Lightning generations early; see
	// rwkvlightning.Config.
	LoopGuard bool
}

func DefaultStopTokens(kind string) string {
	switch kind {
	case LightningPython, IRWKV:
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
			SystemSuffix: config.ChatSystemSuffix, ReasoningEffort: config.ChatReasoningEffort,
			ChatTemplateEnableThinking: config.ChatTemplateEnableThinking,
			IncludeTopK:                config.ChatIncludeTopK,
		})
	case IRWKV:
		return newIRWKV(config, endpoint)
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
			if strings.TrimSpace(config.AdapterID) != "" {
				return nil, fmt.Errorf("Python Lightning raw continuation does not support MiSS adapter_id")
			}
		} else if mode == rwkvlightning.StopTokenText {
			return nil, fmt.Errorf("CUDA Lightning requires integer stop token IDs; decoded-text stops are handled locally")
		}
		client, err := rwkvlightning.New(rwkvlightning.Config{
			Endpoint: endpoint, Model: config.Model, Password: config.Credential,
			Headers: config.Headers, HTTPClient: config.HTTPClient,
			StopTokenMode: mode, StopTokenIDs: ids, StateID: config.StateID, AdapterID: config.AdapterID,
			Stream: config.Stream, BatchWait: config.BatchWait, BatchMax: config.BatchMax,
			BatchInflight: config.BatchInflight, LoopGuard: config.LoopGuard,
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

// newIRWKV maps the shared stop-token setting onto iRWKV: text forwards the
// request's decoded-text stops, an id list (or eos) is sent as stop_token_ids
// alongside them, and none leaves stopping to the client and EOS.
func newIRWKV(config Config, endpoint string) (continuation.Generator, error) {
	if strings.TrimSpace(config.StateID) != "" {
		return nil, fmt.Errorf("iRWKV does not support uploaded state_id")
	}
	if strings.TrimSpace(config.AdapterID) != "" {
		return nil, fmt.Errorf("iRWKV does not support MiSS adapter_id")
	}
	stops := config.StopTokens
	if stops == "" {
		stops = DefaultStopTokens(IRWKV)
	}
	mode, ids, err := ParseStopTokens(stops)
	if err != nil {
		return nil, err
	}
	return irwkv.New(irwkv.Config{
		Endpoint: endpoint, Model: config.Model, APIKey: config.Credential,
		Headers: config.Headers, HTTPClient: config.HTTPClient,
		ForwardStops: mode != rwkvlightning.StopTokenNone, StopTokenIDs: ids,
		Stream: config.Stream, LoopGuard: config.LoopGuard,
	})
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
