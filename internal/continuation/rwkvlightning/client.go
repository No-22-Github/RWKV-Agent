package rwkvlightning

import (
	"bufio"
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
	StopTokens     []int    `json:"stop_tokens"`
	Temperature    float32  `json:"temperature"`
	TopK           int      `json:"top_k"`
	TopP           float32  `json:"top_p"`
	AlphaPresence  float32  `json:"alpha_presence"`
	AlphaFrequency float32  `json:"alpha_frequency"`
	AlphaDecay     float32  `json:"alpha_decay"`
	Stream         bool     `json:"stream"`
	ChunkSize      int      `json:"chunk_size"`
	Password       string   `json:"password,omitempty"`
}

type streamBody struct {
	Choices []struct {
		Index int `json:"index"`
		Delta struct {
			Content string `json:"content"`
		} `json:"delta"`
		FinishReason string `json:"finish_reason"`
	} `json:"choices"`
	Usage continuation.Usage `json:"usage"`
	Error json.RawMessage    `json:"error"`
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
		StopTokens:     []int{0},
		Temperature:    request.Sampling.Temperature,
		TopK:           request.Sampling.TopK,
		TopP:           request.Sampling.TopP,
		AlphaPresence:  request.Sampling.PresencePenalty,
		AlphaFrequency: request.Sampling.FrequencyPenalty,
		AlphaDecay:     request.Sampling.PenaltyDecay,
		Stream:         true,
		ChunkSize:      1,
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
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		body, readErr := io.ReadAll(io.LimitReader(response.Body, maxResponseBytes+1))
		if readErr != nil {
			return continuation.Result{}, fmt.Errorf("%w: read error response: %v", ErrRemote, readErr)
		}
		if len(body) > maxResponseBytes {
			return continuation.Result{}, fmt.Errorf(
				"%w: error response exceeded %d bytes",
				ErrRemote,
				maxResponseBytes,
			)
		}
		return continuation.Result{}, fmt.Errorf(
			"%w: HTTP %d: %s",
			ErrRemote,
			response.StatusCode,
			safeResponseMessage(body, c.password),
		)
	}
	return readStreamResponse(ctx, response.Body, request.Stops, sink, c.password)
}

func readStreamResponse(
	ctx context.Context,
	body io.Reader,
	stops []string,
	sink continuation.EventSink,
	secret string,
) (continuation.Result, error) {
	scanner := bufio.NewScanner(body)
	scanner.Buffer(make([]byte, 64*1024), maxResponseBytes)
	var result strings.Builder
	pending := ""
	finish := continuation.FinishUnknown
	usage := continuation.Usage{}
	sawChoice := false
	sawDone := false
	responseBytes := 0
	emit := func(text string) error {
		if text == "" {
			return nil
		}
		result.WriteString(text)
		if sink == nil {
			return nil
		}
		return sink(continuation.Event{Kind: continuation.EventTextDelta, Text: text})
	}
	for scanner.Scan() {
		line := scanner.Text()
		responseBytes += len(line) + 1
		if responseBytes > maxResponseBytes {
			return continuation.Result{}, fmt.Errorf(
				"%w: response exceeded %d bytes",
				ErrRemote,
				maxResponseBytes,
			)
		}
		line = strings.TrimSpace(line)
		if !strings.HasPrefix(line, "data:") {
			continue
		}
		data := strings.TrimSpace(strings.TrimPrefix(line, "data:"))
		if data == "[DONE]" {
			sawDone = true
			break
		}
		if data == "" {
			continue
		}
		var chunk streamBody
		if err := json.Unmarshal([]byte(data), &chunk); err != nil {
			return continuation.Result{}, fmt.Errorf("%w: decode stream chunk: %v", ErrRemote, err)
		}
		if len(chunk.Error) != 0 && string(chunk.Error) != "null" {
			return continuation.Result{}, fmt.Errorf(
				"%w: stream error: %s",
				ErrRemote,
				safeResponseMessage(chunk.Error, secret),
			)
		}
		if chunk.Usage != (continuation.Usage{}) {
			usage = chunk.Usage
		}
		for _, choice := range chunk.Choices {
			if choice.Index != 0 {
				continue
			}
			sawChoice = true
			if choice.FinishReason != "" {
				finish = finishReason(choice.FinishReason)
			}
			pending += choice.Delta.Content
			text, tail, stopped := splitAtStop(pending, stops)
			if err := emit(text); err != nil {
				return continuation.Result{
					Text:         result.String(),
					FinishReason: continuation.FinishCancelled,
					Usage:        usage,
				}, err
			}
			pending = tail
			if stopped {
				return continuation.Result{
					Text:         result.String(),
					FinishReason: continuation.FinishStop,
					Usage:        usage,
				}, nil
			}
		}
	}
	if err := scanner.Err(); err != nil {
		if ctx.Err() != nil {
			return continuation.Result{
				Text:         result.String(),
				FinishReason: continuation.FinishCancelled,
				Usage:        usage,
			}, ctx.Err()
		}
		return continuation.Result{}, fmt.Errorf("%w: read stream: %v", ErrRemote, err)
	}
	if !sawDone {
		return continuation.Result{}, fmt.Errorf("%w: stream ended before [DONE]", ErrRemote)
	}
	if !sawChoice {
		return continuation.Result{}, fmt.Errorf("%w: response has no choices", ErrRemote)
	}
	if err := emit(pending); err != nil {
		return continuation.Result{
			Text:         result.String(),
			FinishReason: continuation.FinishCancelled,
			Usage:        usage,
		}, err
	}
	return continuation.Result{
		Text:         result.String(),
		FinishReason: finish,
		Usage:        usage,
	}, nil
}

func splitAtStop(value string, stops []string) (string, string, bool) {
	stopIndex := len(value)
	for _, stop := range stops {
		if index := strings.Index(value, stop); index >= 0 && index < stopIndex {
			stopIndex = index
		}
	}
	if stopIndex < len(value) {
		return value[:stopIndex], "", true
	}
	tailBytes := 0
	for _, stop := range stops {
		limit := min(len(value), len(stop)-1)
		for length := 1; length <= limit; length++ {
			if length > tailBytes && strings.HasSuffix(value, stop[:length]) {
				tailBytes = length
			}
		}
	}
	safeBytes := len(value) - tailBytes
	return value[:safeBytes], value[safeBytes:], false
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
