package rwkvlightning

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

const maxResponseBytes = 4 * 1024 * 1024

var ErrRemote = errors.New("rwkv_lightning continuation error")

type Config struct {
	Endpoint   string
	Model      string
	Password   string
	Headers    http.Header
	HTTPClient *http.Client
}

type Client struct {
	endpoint   string
	model      string
	password   string
	headers    http.Header
	httpClient *http.Client
}

func New(config Config) (*Client, error) {
	endpoint := strings.TrimSpace(config.Endpoint)
	parsed, err := url.Parse(endpoint)
	if err != nil || parsed.Scheme == "" || parsed.Host == "" {
		return nil, fmt.Errorf("%w: endpoint must be an absolute HTTP(S) URL", continuation.ErrInvalidRequest)
	}
	if parsed.Scheme != "http" && parsed.Scheme != "https" {
		return nil, fmt.Errorf("%w: endpoint scheme must be HTTP or HTTPS", continuation.ErrInvalidRequest)
	}
	if parsed.User != nil {
		return nil, fmt.Errorf("%w: endpoint must not contain credentials", continuation.ErrInvalidRequest)
	}
	model := strings.TrimSpace(config.Model)
	if model == "" {
		return nil, fmt.Errorf("%w: model is required", continuation.ErrInvalidRequest)
	}
	httpClient := config.HTTPClient
	if httpClient == nil {
		httpClient = http.DefaultClient
	}
	return &Client{
		endpoint:   endpoint,
		model:      model,
		password:   config.Password,
		headers:    config.Headers.Clone(),
		httpClient: httpClient,
	}, nil
}

type requestBody struct {
	Model          string   `json:"model"`
	Contents       []string `json:"contents"`
	MaxTokens      int      `json:"max_tokens"`
	StopTokens     []string `json:"stop_tokens"`
	Temperature    float32  `json:"temperature"`
	TopK           int      `json:"top_k"`
	TopP           float32  `json:"top_p"`
	AlphaPresence  float32  `json:"alpha_presence"`
	AlphaFrequency float32  `json:"alpha_frequency"`
	AlphaDecay     float32  `json:"alpha_decay"`
	Stream         bool     `json:"stream"`
	Password       string   `json:"password,omitempty"`
}

type responseBody struct {
	Choices []struct {
		Index   int `json:"index"`
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
		FinishReason string `json:"finish_reason"`
	} `json:"choices"`
}

func (c *Client) Continue(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	if err := continuation.ValidateRequest(request); err != nil {
		return continuation.Result{}, err
	}
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	encoded, err := json.Marshal(requestBody{
		Model:          model,
		Contents:       []string{request.Prompt},
		MaxTokens:      request.MaxOutputTokens,
		StopTokens:     append([]string{}, request.Stops...),
		Temperature:    request.Sampling.Temperature,
		TopK:           request.Sampling.TopK,
		TopP:           request.Sampling.TopP,
		AlphaPresence:  request.Sampling.PresencePenalty,
		AlphaFrequency: request.Sampling.FrequencyPenalty,
		AlphaDecay:     request.Sampling.PenaltyDecay,
		Stream:         false,
		Password:       c.password,
	})
	if err != nil {
		return continuation.Result{}, fmt.Errorf("%w: encode request: %v", ErrRemote, err)
	}
	httpRequest, err := http.NewRequestWithContext(
		ctx,
		http.MethodPost,
		c.endpoint,
		bytes.NewReader(encoded),
	)
	if err != nil {
		return continuation.Result{}, fmt.Errorf("%w: build request: %v", ErrRemote, err)
	}
	for name, values := range c.headers {
		for _, value := range values {
			httpRequest.Header.Add(name, value)
		}
	}
	httpRequest.Header.Set("Content-Type", "application/json")
	response, err := c.httpClient.Do(httpRequest)
	if err != nil {
		if ctx.Err() != nil {
			return continuation.Result{FinishReason: continuation.FinishCancelled}, ctx.Err()
		}
		return continuation.Result{}, fmt.Errorf("%w: request failed: %v", ErrRemote, err)
	}
	defer response.Body.Close()
	body, err := io.ReadAll(io.LimitReader(response.Body, maxResponseBytes+1))
	if err != nil {
		return continuation.Result{}, fmt.Errorf("%w: read response: %v", ErrRemote, err)
	}
	if len(body) > maxResponseBytes {
		return continuation.Result{}, fmt.Errorf("%w: response exceeded %d bytes", ErrRemote, maxResponseBytes)
	}
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return continuation.Result{}, fmt.Errorf(
			"%w: HTTP %d: %s",
			ErrRemote,
			response.StatusCode,
			safeResponseMessage(body, c.password),
		)
	}
	var decoded responseBody
	if err := json.Unmarshal(body, &decoded); err != nil {
		return continuation.Result{}, fmt.Errorf("%w: decode response: %v", ErrRemote, err)
	}
	if len(decoded.Choices) == 0 {
		return continuation.Result{}, fmt.Errorf("%w: response has no choices", ErrRemote)
	}
	choice := decoded.Choices[0]
	for _, candidate := range decoded.Choices {
		if candidate.Index == 0 {
			choice = candidate
			break
		}
	}
	if sink != nil && choice.Message.Content != "" {
		if err := sink(continuation.Event{
			Kind: continuation.EventTextDelta,
			Text: choice.Message.Content,
		}); err != nil {
			return continuation.Result{
				Text:         choice.Message.Content,
				FinishReason: continuation.FinishCancelled,
			}, err
		}
	}
	return continuation.Result{
		Text:         choice.Message.Content,
		FinishReason: finishReason(choice.FinishReason),
	}, nil
}

func safeResponseMessage(body []byte, secret string) string {
	const limit = 512
	value := strings.TrimSpace(string(body))
	value = strings.Join(strings.Fields(value), " ")
	if secret != "" {
		value = strings.ReplaceAll(value, secret, "[REDACTED]")
	}
	if len(value) > limit {
		value = value[:limit] + "..."
	}
	if value == "" {
		return "empty response"
	}
	return value
}

func finishReason(value string) continuation.FinishReason {
	switch value {
	case "stop":
		return continuation.FinishStop
	case "length":
		return continuation.FinishLength
	case "cancelled":
		return continuation.FinishCancelled
	default:
		return continuation.FinishUnknown
	}
}

var _ continuation.Generator = (*Client)(nil)
