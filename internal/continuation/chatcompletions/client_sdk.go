//go:build chatcompletions

package chatcompletions

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/url"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/option"
	"github.com/openai/openai-go/v3/shared"
)

type Client struct {
	sdk        openai.Client
	model      string
	thinking   ThinkingMode
	promptMode PromptMode
	tokenLimit TokenLimitField
	secrets    []string
}

func New(config Config) (*Client, error) {
	normalized, err := normalizeConfig(config)
	if err != nil {
		return nil, err
	}
	options := []option.RequestOption{
		option.WithBaseURL(sdkBaseURL(normalized.endpoint)),
		option.WithAPIKey(normalized.apiKey),
		option.WithHTTPClient(normalized.httpClient),
	}
	for name, values := range normalized.headers {
		for index, value := range values {
			if index == 0 {
				options = append(options, option.WithHeader(name, value))
			} else {
				options = append(options, option.WithHeaderAdd(name, value))
			}
		}
	}
	return &Client{
		sdk:        openai.NewClient(options...),
		model:      normalized.model,
		thinking:   normalized.thinking,
		promptMode: normalized.promptMode,
		tokenLimit: normalized.tokenLimit,
		secrets:    normalized.secrets,
	}, nil
}

func sdkBaseURL(endpoint string) string {
	parsed, _ := url.Parse(endpoint)
	path := strings.TrimSuffix(parsed.Path, "/")
	if strings.HasSuffix(path, "/chat/completions") {
		path = strings.TrimSuffix(path, "/chat/completions")
	}
	parsed.Path = strings.TrimSuffix(path, "/") + "/"
	parsed.RawPath = ""
	return parsed.String()
}

func (c *Client) Continue(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	if c.promptMode == PromptNativeChat {
		return continuation.Result{}, fmt.Errorf(
			"%w: native-chat requires the structured Chat Completions path",
			continuation.ErrInvalidRequest,
		)
	}
	if err := continuation.ValidateRequest(request); err != nil {
		return continuation.Result{}, err
	}
	if err := validateSampling(request.Sampling); err != nil {
		return continuation.Result{}, err
	}
	if len(request.Stops) > 4 {
		return continuation.Result{}, fmt.Errorf(
			"%w: Chat Completions supports at most four stop sequences",
			continuation.ErrInvalidRequest,
		)
	}
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	params := c.baseParams(model, request.MaxOutputTokens, request.Stops, request.Sampling)
	params.Messages = []openai.ChatCompletionMessageParamUnion{
		openai.SystemMessage(continuationInstruction),
		openai.UserMessage(request.Prompt),
	}
	response, err := c.sdk.Chat.Completions.New(ctx, params, c.thinkingOption()...)
	if err != nil {
		if ctx.Err() != nil {
			return continuation.Result{FinishReason: continuation.FinishCancelled}, ctx.Err()
		}
		return continuation.Result{}, c.remoteError(err)
	}
	choice, ok := firstSDKChoice(response)
	if !ok {
		return continuation.Result{}, fmt.Errorf("%w: response has no choice at index 0", ErrRemote)
	}
	if len(choice.Message.ToolCalls) > 0 || choice.FinishReason == "tool_calls" {
		return continuation.Result{}, fmt.Errorf(
			"%w: text continuation unexpectedly returned native tool calls",
			ErrRemote,
		)
	}
	text, stopped := truncateAtStop(choice.Message.Content, request.Stops)
	finish := finishReason(choice.FinishReason)
	if stopped {
		finish = continuation.FinishStop
	}
	result := continuation.Result{
		Text:         text,
		FinishReason: finish,
		Usage:        sdkUsage(response),
	}
	if sink != nil && text != "" {
		if err := sink(continuation.Event{Kind: continuation.EventTextDelta, Text: text}); err != nil {
			result.FinishReason = continuation.FinishCancelled
			return result, err
		}
	}
	return result, nil
}

func (c *Client) NativeToolCalling() bool {
	return c.promptMode == PromptNativeChat
}

func (c *Client) Complete(
	ctx context.Context,
	request toolchat.Request,
	sink continuation.EventSink,
) (toolchat.Result, error) {
	if !c.NativeToolCalling() {
		return toolchat.Result{}, fmt.Errorf(
			"%w: structured Chat Completions requires native-chat prompt mode",
			continuation.ErrInvalidRequest,
		)
	}
	if err := validateToolChatRequest(request); err != nil {
		return toolchat.Result{}, err
	}
	messages := withAssistantPrefix(request.Messages, request.AssistantPrefix)
	encodedMessages, err := encodeSDKMessages(messages)
	if err != nil {
		return toolchat.Result{}, err
	}
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	params := c.baseParams(model, request.MaxOutputTokens, request.Stops, request.Sampling)
	params.Messages = encodedMessages
	requestOptions := c.thinkingOption()
	requestOptions = append(requestOptions, reasoningOptions(messages)...)
	if len(request.Tools) > 0 {
		params.Tools, err = encodeSDKTools(request.Tools)
		if err != nil {
			return toolchat.Result{}, err
		}
		toolChoice := request.ToolChoice
		if c.thinking == ThinkingEnabled && toolChoice == toolchat.ToolChoiceRequired {
			toolChoice = toolchat.ToolChoiceAuto
		}
		params.ToolChoice = openai.ChatCompletionToolChoiceOptionUnionParam{
			OfAuto: openai.String(string(toolChoice)),
		}
		params.ParallelToolCalls = openai.Bool(request.ParallelToolCalls)
	}
	response, err := c.sdk.Chat.Completions.New(ctx, params, requestOptions...)
	if err != nil {
		if ctx.Err() != nil {
			return toolchat.Result{FinishReason: continuation.FinishCancelled}, ctx.Err()
		}
		return toolchat.Result{}, c.remoteError(err)
	}
	choice, ok := firstSDKChoice(response)
	if !ok {
		return toolchat.Result{}, fmt.Errorf("%w: response has no choice at index 0", ErrRemote)
	}
	calls, err := decodeSDKToolCalls(choice.Message.ToolCalls)
	if err != nil {
		return toolchat.Result{}, err
	}
	if len(calls) > 0 && choice.FinishReason != "tool_calls" {
		return toolchat.Result{}, fmt.Errorf(
			"%w: response included tool_calls with finish_reason %q",
			ErrRemote,
			choice.FinishReason,
		)
	}
	if len(calls) == 0 && choice.FinishReason == "tool_calls" {
		return toolchat.Result{}, fmt.Errorf(
			"%w: finish_reason tool_calls requires at least one tool call",
			ErrRemote,
		)
	}
	if !request.ParallelToolCalls && len(calls) > 1 {
		calls = calls[:1]
	}
	content, stopped := truncateAtStop(choice.Message.Content, request.Stops)
	finish := finishReason(choice.FinishReason)
	if stopped {
		finish = continuation.FinishStop
	}
	result := toolchat.Result{
		Content:          content,
		ReasoningContent: reasoningContent(choice.Message),
		ToolCalls:        calls,
		FinishReason:     finish,
		Usage:            sdkUsage(response),
	}
	if sink != nil && content != "" {
		if err := sink(continuation.Event{Kind: continuation.EventTextDelta, Text: content}); err != nil {
			result.FinishReason = continuation.FinishCancelled
			return result, err
		}
	}
	return result, nil
}

func (c *Client) baseParams(
	model string,
	maxOutputTokens int,
	stops []string,
	sampling continuation.Sampling,
) openai.ChatCompletionNewParams {
	params := openai.ChatCompletionNewParams{
		Model:            shared.ChatModel(model),
		Temperature:      openai.Float(float64(sampling.Temperature)),
		TopP:             openai.Float(float64(sampling.TopP)),
		PresencePenalty:  openai.Float(float64(sampling.PresencePenalty)),
		FrequencyPenalty: openai.Float(float64(sampling.FrequencyPenalty)),
		Stop: openai.ChatCompletionNewParamsStopUnion{
			OfStringArray: append([]string(nil), stops...),
		},
	}
	if sampling.Seed != nil {
		params.Seed = openai.Int(*sampling.Seed)
	}
	if c.tokenLimit == TokenLimitMaxTokens {
		params.MaxTokens = openai.Int(int64(maxOutputTokens))
	} else {
		params.MaxCompletionTokens = openai.Int(int64(maxOutputTokens))
	}
	return params
}

func (c *Client) thinkingOption() []option.RequestOption {
	if c.thinking == ThinkingAuto {
		return nil
	}
	return []option.RequestOption{
		option.WithJSONSet("thinking", map[string]string{"type": string(c.thinking)}),
	}
}

func reasoningOptions(messages []toolchat.Message) []option.RequestOption {
	var options []option.RequestOption
	for index, message := range messages {
		if message.Role == toolchat.RoleAssistant && message.ReasoningContent != "" {
			options = append(options, option.WithJSONSet(
				fmt.Sprintf("messages.%d.reasoning_content", index),
				message.ReasoningContent,
			))
		}
	}
	return options
}

func encodeSDKMessages(sources []toolchat.Message) ([]openai.ChatCompletionMessageParamUnion, error) {
	result := make([]openai.ChatCompletionMessageParamUnion, 0, len(sources))
	for _, source := range sources {
		switch source.Role {
		case toolchat.RoleSystem:
			result = append(result, openai.SystemMessage(source.Content))
		case toolchat.RoleUser:
			result = append(result, openai.UserMessage(source.Content))
		case toolchat.RoleAssistant:
			assistant := openai.ChatCompletionAssistantMessageParam{}
			if source.Content != "" {
				assistant.Content = openai.ChatCompletionAssistantMessageParamContentUnion{
					OfString: openai.String(source.Content),
				}
			}
			for _, call := range source.ToolCalls {
				assistant.ToolCalls = append(
					assistant.ToolCalls,
					openai.ChatCompletionMessageToolCallUnionParam{
						OfFunction: &openai.ChatCompletionMessageFunctionToolCallParam{
							ID: call.ID,
							Function: openai.ChatCompletionMessageFunctionToolCallFunctionParam{
								Name: call.Name, Arguments: call.Arguments,
							},
						},
					},
				)
			}
			result = append(result, openai.ChatCompletionMessageParamUnion{OfAssistant: &assistant})
		case toolchat.RoleTool:
			result = append(result, openai.ToolMessage(source.Content, source.ToolCallID))
		default:
			return nil, fmt.Errorf(
				"%w: unsupported Chat Completions role %q",
				continuation.ErrInvalidRequest,
				source.Role,
			)
		}
	}
	return result, nil
}

func encodeSDKTools(tools []toolchat.Tool) ([]openai.ChatCompletionToolUnionParam, error) {
	result := make([]openai.ChatCompletionToolUnionParam, 0, len(tools))
	for _, tool := range tools {
		var parameters shared.FunctionParameters
		if err := json.Unmarshal(tool.Parameters, &parameters); err != nil {
			return nil, fmt.Errorf(
				"%w: decode parameters for tool %q: %v",
				continuation.ErrInvalidRequest,
				tool.Name,
				err,
			)
		}
		result = append(result, openai.ChatCompletionFunctionTool(shared.FunctionDefinitionParam{
			Name:        tool.Name,
			Description: openai.String(tool.Description),
			Parameters:  parameters,
			Strict:      openai.Bool(tool.Strict),
		}))
	}
	return result, nil
}

func decodeSDKToolCalls(calls []openai.ChatCompletionMessageToolCallUnion) ([]toolchat.ToolCall, error) {
	result := make([]toolchat.ToolCall, 0, len(calls))
	seen := make(map[string]struct{}, len(calls))
	for index, call := range calls {
		if strings.TrimSpace(call.ID) == "" {
			return nil, fmt.Errorf("%w: function tool call %d has no id", ErrRemote, index)
		}
		if call.Type != "function" {
			return nil, fmt.Errorf(
				"%w: function tool call %d has unsupported type %q",
				ErrRemote,
				index,
				call.Type,
			)
		}
		if !functionNamePattern.MatchString(call.Function.Name) {
			return nil, fmt.Errorf("%w: function tool call %d has an invalid name", ErrRemote, index)
		}
		if !isJSONObject(json.RawMessage(call.Function.Arguments)) {
			return nil, fmt.Errorf(
				"%w: function tool call %d arguments are not a JSON object",
				ErrRemote,
				index,
			)
		}
		if _, exists := seen[call.ID]; exists {
			return nil, fmt.Errorf("%w: duplicate tool call id %q", ErrRemote, call.ID)
		}
		seen[call.ID] = struct{}{}
		result = append(result, toolchat.ToolCall{
			ID: call.ID, Name: call.Function.Name, Arguments: call.Function.Arguments,
		})
	}
	return result, nil
}

func firstSDKChoice(response *openai.ChatCompletion) (openai.ChatCompletionChoice, bool) {
	for _, choice := range response.Choices {
		if choice.Index == 0 {
			return choice, true
		}
	}
	return openai.ChatCompletionChoice{}, false
}

func sdkUsage(response *openai.ChatCompletion) continuation.Usage {
	return continuation.Usage{
		PromptTokens:     int(response.Usage.PromptTokens),
		CompletionTokens: int(response.Usage.CompletionTokens),
	}
}

func reasoningContent(message openai.ChatCompletionMessage) string {
	for _, name := range []string{"reasoning_content", "reasoning"} {
		field, ok := message.JSON.ExtraFields[name]
		if !ok {
			continue
		}
		var result string
		if err := json.Unmarshal([]byte(field.Raw()), &result); err == nil {
			return result
		}
	}
	return ""
}

func (c *Client) remoteError(err error) error {
	var apiError *openai.Error
	if errors.As(err, &apiError) {
		body := apiError.RawJSON()
		if strings.TrimSpace(body) == "" {
			body = apiError.Message
		}
		return fmt.Errorf(
			"%w: HTTP %d: %s",
			ErrRemote,
			apiError.StatusCode,
			safeResponseMessage([]byte(body), c.secrets...),
		)
	}
	return fmt.Errorf(
		"%w: request failed: %s",
		ErrRemote,
		safeResponseMessage([]byte(err.Error()), c.secrets...),
	)
}

var _ continuation.Generator = (*Client)(nil)
var _ toolchat.Completer = (*Client)(nil)
