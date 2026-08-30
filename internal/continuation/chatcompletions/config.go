package chatcompletions

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"regexp"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/httputil"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

const (
	continuationInstruction = "Continue the preformatted transcript in the next message. " +
		"Return only the text that belongs after its final Assistant: prefix. " +
		"Do not quote, summarize, or explain the transcript."
	defaultHTTPTimeout = 2 * time.Minute
)

var (
	ErrRemote   = errors.New("Chat Completions continuation error")
	ErrNotBuilt = errors.New(
		"Chat Completions support is not included in this build; rebuild with -tags chatcompletions",
	)
)

var functionNamePattern = regexp.MustCompile(`^[A-Za-z0-9_-]{1,64}$`)

type ThinkingMode string
type PromptMode string
type TokenLimitField string

const (
	ThinkingAuto     ThinkingMode = "auto"
	ThinkingDisabled ThinkingMode = "disabled"
	ThinkingEnabled  ThinkingMode = "enabled"

	PromptWrappedContinuation PromptMode = "wrapped-continuation"
	PromptNativeChat          PromptMode = "native-chat"

	TokenLimitMaxCompletionTokens TokenLimitField = "max-completion-tokens"
	TokenLimitMaxTokens           TokenLimitField = "max-tokens"
)

func ParseThinkingMode(value string) (ThinkingMode, error) {
	mode := ThinkingMode(strings.ToLower(strings.TrimSpace(value)))
	if mode == "" {
		mode = ThinkingAuto
	}
	switch mode {
	case ThinkingAuto, ThinkingDisabled, ThinkingEnabled:
		return mode, nil
	default:
		return "", fmt.Errorf(
			"%w: Chat Completions thinking mode must be auto, disabled, or enabled",
			continuation.ErrInvalidRequest,
		)
	}
}

func ParsePromptMode(value string) (PromptMode, error) {
	mode := PromptMode(strings.ToLower(strings.TrimSpace(value)))
	if mode == "" {
		mode = PromptWrappedContinuation
	}
	switch mode {
	case PromptWrappedContinuation, PromptNativeChat:
		return mode, nil
	default:
		return "", fmt.Errorf(
			"%w: Chat Completions prompt mode must be wrapped-continuation or native-chat",
			continuation.ErrInvalidRequest,
		)
	}
}

func ParseTokenLimitField(value string) (TokenLimitField, error) {
	field := TokenLimitField(strings.ToLower(strings.TrimSpace(value)))
	if field == "" {
		field = TokenLimitMaxCompletionTokens
	}
	switch field {
	case TokenLimitMaxCompletionTokens, TokenLimitMaxTokens:
		return field, nil
	default:
		return "", fmt.Errorf(
			"%w: Chat Completions token limit field must be max-completion-tokens or max-tokens",
			continuation.ErrInvalidRequest,
		)
	}
}

type Config struct {
	Endpoint                   string
	Model                      string
	APIKey                     string
	Thinking                   ThinkingMode
	ChatTemplateEnableThinking *bool
	IncludeTopK                bool
	PromptMode                 PromptMode
	TokenLimit                 TokenLimitField
	Headers                    http.Header
	HTTPClient                 *http.Client
}

type normalizedConfig struct {
	endpoint                   string
	model                      string
	apiKey                     string
	thinking                   ThinkingMode
	chatTemplateEnableThinking *bool
	includeTopK                bool
	promptMode                 PromptMode
	tokenLimit                 TokenLimitField
	headers                    http.Header
	secrets                    []string
	httpClient                 *http.Client
}

func normalizeConfig(config Config) (normalizedConfig, error) {
	endpoint := strings.TrimSpace(config.Endpoint)
	if err := httputil.ValidateEndpoint(endpoint); err != nil {
		return normalizedConfig{}, err
	}
	model := strings.TrimSpace(config.Model)
	if model == "" {
		return normalizedConfig{}, fmt.Errorf("%w: model is required", continuation.ErrInvalidRequest)
	}
	thinking, err := ParseThinkingMode(string(config.Thinking))
	if err != nil {
		return normalizedConfig{}, err
	}
	promptMode, err := ParsePromptMode(string(config.PromptMode))
	if err != nil {
		return normalizedConfig{}, err
	}
	tokenLimit, err := ParseTokenLimitField(string(config.TokenLimit))
	if err != nil {
		return normalizedConfig{}, err
	}
	httpClient := config.HTTPClient
	if httpClient == nil {
		httpClient = &http.Client{Timeout: defaultHTTPTimeout}
	}
	headers := config.Headers.Clone()
	secrets := make([]string, 0, len(headers)+1)
	apiKey := strings.TrimSpace(config.APIKey)
	if apiKey != "" {
		secrets = append(secrets, apiKey)
	}
	for _, values := range headers {
		for _, value := range values {
			if value = strings.TrimSpace(value); value != "" {
				secrets = append(secrets, value)
			}
		}
	}
	var chatTemplateEnableThinking *bool
	if config.ChatTemplateEnableThinking != nil {
		value := *config.ChatTemplateEnableThinking
		chatTemplateEnableThinking = &value
	}
	return normalizedConfig{
		endpoint:                   endpoint,
		model:                      model,
		apiKey:                     apiKey,
		thinking:                   thinking,
		chatTemplateEnableThinking: chatTemplateEnableThinking,
		includeTopK:                config.IncludeTopK,
		promptMode:                 promptMode,
		tokenLimit:                 tokenLimit,
		headers:                    headers,
		secrets:                    secrets,
		httpClient:                 httpClient,
	}, nil
}

func validateToolChatRequest(request toolchat.Request) error {
	validation := continuation.Request{
		Prompt:          "structured-chat",
		MaxOutputTokens: request.MaxOutputTokens,
		Stops:           request.Stops,
		Sampling:        request.Sampling,
	}
	if err := validateChatCompletionsRequest(validation); err != nil {
		return err
	}
	if err := validateSampling(request.Sampling); err != nil {
		return err
	}
	if len(request.Stops) > 4 {
		return fmt.Errorf(
			"%w: Chat Completions supports at most four stop sequences",
			continuation.ErrInvalidRequest,
		)
	}
	if len(request.Messages) == 0 {
		return fmt.Errorf("%w: Chat Completions messages are required", continuation.ErrInvalidRequest)
	}
	pendingCalls := make(map[string]struct{})
	seenCalls := make(map[string]struct{})
	for _, source := range request.Messages {
		switch source.Role {
		case toolchat.RoleSystem, toolchat.RoleUser:
			if strings.TrimSpace(source.Content) == "" || len(source.ToolCalls) > 0 ||
				source.ToolCallID != "" || source.ReasoningContent != "" || len(pendingCalls) > 0 {
				return fmt.Errorf("%w: invalid %s message", continuation.ErrInvalidRequest, source.Role)
			}
		case toolchat.RoleAssistant:
			if source.ToolCallID != "" || len(pendingCalls) > 0 ||
				(strings.TrimSpace(source.Content) == "" && len(source.ToolCalls) == 0) {
				return fmt.Errorf(
					"%w: assistant message requires content or tool_calls",
					continuation.ErrInvalidRequest,
				)
			}
			for _, call := range source.ToolCalls {
				if strings.TrimSpace(call.ID) == "" || !functionNamePattern.MatchString(call.Name) ||
					!isJSONObject(json.RawMessage(call.Arguments)) {
					return fmt.Errorf("%w: malformed assistant tool call", continuation.ErrInvalidRequest)
				}
				if _, exists := seenCalls[call.ID]; exists {
					return fmt.Errorf(
						"%w: duplicate assistant tool call id %q",
						continuation.ErrInvalidRequest,
						call.ID,
					)
				}
				seenCalls[call.ID] = struct{}{}
				pendingCalls[call.ID] = struct{}{}
			}
		case toolchat.RoleTool:
			if strings.TrimSpace(source.Content) == "" || strings.TrimSpace(source.ToolCallID) == "" ||
				len(source.ToolCalls) > 0 || source.ReasoningContent != "" {
				return fmt.Errorf(
					"%w: tool message requires content and tool_call_id",
					continuation.ErrInvalidRequest,
				)
			}
			if _, exists := pendingCalls[source.ToolCallID]; !exists {
				return fmt.Errorf(
					"%w: tool_call_id %q does not match a pending assistant tool call",
					continuation.ErrInvalidRequest,
					source.ToolCallID,
				)
			}
			delete(pendingCalls, source.ToolCallID)
		default:
			return fmt.Errorf(
				"%w: unsupported Chat Completions role %q",
				continuation.ErrInvalidRequest,
				source.Role,
			)
		}
	}
	if len(pendingCalls) > 0 {
		return fmt.Errorf(
			"%w: every assistant tool call requires a matching tool result before the next completion",
			continuation.ErrInvalidRequest,
		)
	}
	if len(request.Tools) == 0 {
		if request.ToolChoice != "" && request.ToolChoice != toolchat.ToolChoiceNone {
			return fmt.Errorf("%w: tool_choice requires tools", continuation.ErrInvalidRequest)
		}
		return nil
	}
	if request.ToolChoice != toolchat.ToolChoiceAuto &&
		request.ToolChoice != toolchat.ToolChoiceRequired &&
		request.ToolChoice != toolchat.ToolChoiceNone {
		return fmt.Errorf("%w: invalid tool_choice %q", continuation.ErrInvalidRequest, request.ToolChoice)
	}
	seen := make(map[string]struct{}, len(request.Tools))
	for _, tool := range request.Tools {
		if !functionNamePattern.MatchString(tool.Name) || strings.TrimSpace(tool.Description) == "" ||
			!isJSONObject(tool.Parameters) {
			return fmt.Errorf("%w: invalid function tool %q", continuation.ErrInvalidRequest, tool.Name)
		}
		if _, exists := seen[tool.Name]; exists {
			return fmt.Errorf("%w: duplicate function tool %q", continuation.ErrInvalidRequest, tool.Name)
		}
		seen[tool.Name] = struct{}{}
	}
	return nil
}

func validateChatCompletionsRequest(request continuation.Request) error {
	if request.Sampling.Temperature < 0 {
		return fmt.Errorf(
			"%w: temperature cannot be negative",
			continuation.ErrInvalidRequest,
		)
	}
	if request.Sampling.Temperature == 0 {
		request.Sampling.Temperature = 1
	}
	return continuation.ValidateRequest(request)
}

func withAssistantPrefix(sources []toolchat.Message, prefix string) []toolchat.Message {
	result := make([]toolchat.Message, len(sources))
	copy(result, sources)
	prefix = strings.TrimSpace(prefix)
	if prefix == "" {
		return result
	}
	instruction := fmt.Sprintf(
		"The next response must begin exactly with %q and contain no text before it. "+
			"Return the complete response, including that opening prefix.",
		prefix,
	)
	for index := range result {
		if result[index].Role == toolchat.RoleSystem {
			result[index].Content += "\n\n" + instruction
			return result
		}
	}
	return append([]toolchat.Message{{Role: toolchat.RoleSystem, Content: instruction}}, result...)
}

func isJSONObject(value json.RawMessage) bool {
	var object map[string]json.RawMessage
	return len(value) != 0 && json.Unmarshal(value, &object) == nil && object != nil
}

func validateSampling(sampling continuation.Sampling) error {
	if sampling.Temperature > 2 {
		return fmt.Errorf(
			"%w: Chat Completions temperature must be at most 2",
			continuation.ErrInvalidRequest,
		)
	}
	if sampling.PresencePenalty > 2 || sampling.FrequencyPenalty > 2 {
		return fmt.Errorf(
			"%w: Chat Completions presence and frequency penalties must be at most 2",
			continuation.ErrInvalidRequest,
		)
	}
	return nil
}

func finishReason(value string) continuation.FinishReason {
	switch value {
	case "stop":
		return continuation.FinishStop
	case "length":
		return continuation.FinishLength
	case "tool_calls":
		return continuation.FinishToolCalls
	case "cancelled":
		return continuation.FinishCancelled
	default:
		return continuation.FinishUnknown
	}
}
