// Package irwkv drives an iRWKV server (github.com/rwkv-org/irwkv, a vLLM
// fork for RWKV-7) through its OpenAI-compatible text Completions route.
//
// The harness renders the whole RWKV prompt itself, so the raw /v1/completions
// route is used rather than Chat Completions: the server's chat template is a
// different transcript format ("User✿…✿\nBot✿", "### User" with tools) and its
// tool parser did not recognize the calls a G1L model wrote (probed
// 2026-10-29 on rwkv-115). The server batches continuously across requests,
// so unlike rwkv_lightning no client-side coalescing is needed; concurrency is
// simply the number of requests in flight.
//
// iRWKV keeps no uploaded states or MiSS adapters; requests that ask for one
// are rejected rather than silently generated from the base model.
package irwkv

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/httputil"
)

const maxResponseBytes = 4 * 1024 * 1024

var ErrRemote = fmt.Errorf("%w: iRWKV continuation error", continuation.ErrUpstream)

// userTokenID is the World-vocab id of the bare word "User". It also matches
// inside prose and code ("User(r)"), so it is never forwarded as a stop id;
// the "\n\nUser:" turn boundary is a text stop instead.
const userTokenID = 24281

type Config struct {
	Endpoint string
	Model    string
	// APIKey becomes a Bearer token when set (irwkv serve --api-key).
	APIKey string
	// ForwardStops sends the request's decoded-text stops as `stop`, so the
	// server ends generation on them instead of decoding to max_tokens. They
	// are matched client-side as well either way.
	ForwardStops bool
	// StopTokenIDs is sent as stop_token_ids (the bare User id is dropped).
	StopTokenIDs []int
	// Stream selects SSE; the zero value streams.
	Stream *bool
	// LoopGuard ends a streamed generation early, as a length finish, once
	// continuation.LoopGuard sees it repeating itself verbatim.
	LoopGuard  bool
	Headers    http.Header
	HTTPClient *http.Client
}

type Client struct {
	endpoint     string
	model        string
	apiKey       string
	forwardStops bool
	stopTokenIDs []int
	stream       bool
	loopGuard    bool
	headers      http.Header
	httpClient   *http.Client
}

func New(config Config) (*Client, error) {
	endpoint := strings.TrimSpace(config.Endpoint)
	if err := httputil.ValidateEndpoint(endpoint); err != nil {
		return nil, err
	}
	httpClient := config.HTTPClient
	if httpClient == nil {
		httpClient = http.DefaultClient
	}
	ids := make([]int, 0, len(config.StopTokenIDs))
	for _, id := range config.StopTokenIDs {
		if id != userTokenID {
			ids = append(ids, id)
		}
	}
	stream := true
	if config.Stream != nil {
		stream = *config.Stream
	}
	return &Client{
		endpoint:     endpoint,
		model:        strings.TrimSpace(config.Model),
		apiKey:       strings.TrimSpace(config.APIKey),
		forwardStops: config.ForwardStops,
		stopTokenIDs: ids,
		stream:       stream,
		loopGuard:    config.LoopGuard,
		headers:      config.Headers.Clone(),
		httpClient:   httpClient,
	}, nil
}

type streamOptions struct {
	IncludeUsage bool `json:"include_usage"`
}

type requestBody struct {
	Model            string   `json:"model"`
	Prompt           string   `json:"prompt"`
	MaxTokens        int      `json:"max_tokens"`
	Temperature      float32  `json:"temperature"`
	TopK             int      `json:"top_k"`
	TopP             float32  `json:"top_p"`
	PresencePenalty  float32  `json:"presence_penalty"`
	FrequencyPenalty float32  `json:"frequency_penalty"`
	PenaltyDecay     float32  `json:"penalty_decay"`
	Seed             *int64   `json:"seed,omitempty"`
	Stop             []string `json:"stop,omitempty"`
	StopTokenIDs     []int    `json:"stop_token_ids,omitempty"`
	// AddSpecialTokens is always false: the default prepends token 0, which
	// rwkv_lightning and the training renders never do.
	AddSpecialTokens bool           `json:"add_special_tokens"`
	Stream           bool           `json:"stream"`
	StreamOptions    *streamOptions `json:"stream_options,omitempty"`
}

type choice struct {
	Index        int    `json:"index"`
	Text         string `json:"text"`
	FinishReason string `json:"finish_reason"`
	// StopReason is the matched stop string, a stop token id, or null (EOS).
	StopReason json.RawMessage `json:"stop_reason"`
}

type responseBody struct {
	Object  string             `json:"object"`
	Message string             `json:"message"`
	Choices []choice           `json:"choices"`
	Usage   continuation.Usage `json:"usage"`
	Error   json.RawMessage    `json:"error"`
}

func (b responseBody) err(secret string) error {
	if len(b.Error) != 0 && string(b.Error) != "null" {
		return fmt.Errorf("%w: response error: %s", ErrRemote, httputil.SafeResponseMessage(b.Error, secret))
	}
	if b.Object == "error" {
		return fmt.Errorf("%w: response error: %s", ErrRemote, httputil.SafeResponseMessage([]byte(b.Message), secret))
	}
	return nil
}

func (c *Client) Continue(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	if err := continuation.ValidateRequest(request); err != nil {
		return continuation.Result{}, err
	}
	if strings.TrimSpace(request.StateID) != "" {
		return continuation.Result{}, fmt.Errorf("%w: iRWKV does not support uploaded state_id", continuation.ErrInvalidRequest)
	}
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	if model == "" {
		return continuation.Result{}, fmt.Errorf("%w: model is required", continuation.ErrInvalidRequest)
	}
	body := requestBody{
		Model:            model,
		Prompt:           request.Prompt,
		MaxTokens:        request.MaxOutputTokens,
		Temperature:      request.Sampling.Temperature,
		TopK:             request.Sampling.TopK,
		TopP:             request.Sampling.TopP,
		PresencePenalty:  request.Sampling.PresencePenalty,
		FrequencyPenalty: request.Sampling.FrequencyPenalty,
		PenaltyDecay:     request.Sampling.PenaltyDecay,
		Seed:             request.Sampling.Seed,
		StopTokenIDs:     c.stopTokenIDs,
		Stream:           c.stream,
	}
	if c.forwardStops {
		body.Stop = request.Stops
	}
	if c.stream {
		body.StreamOptions = &streamOptions{IncludeUsage: true}
	}
	encoded, err := json.Marshal(body)
	if err != nil {
		return continuation.Result{}, fmt.Errorf("%w: encode request: %v", ErrRemote, err)
	}
	response, err := c.post(ctx, encoded)
	if err != nil {
		if ctx.Err() != nil {
			return continuation.Result{FinishReason: continuation.FinishCancelled}, ctx.Err()
		}
		return continuation.Result{}, err
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		payload, _ := io.ReadAll(io.LimitReader(response.Body, maxResponseBytes))
		return continuation.Result{}, fmt.Errorf(
			"%w: HTTP %d: %s", ErrRemote, response.StatusCode, httputil.SafeResponseMessage(payload, c.apiKey),
		)
	}
	var guard *continuation.LoopGuard
	if c.loopGuard {
		guard = continuation.NewLoopGuard()
	}
	if !c.stream {
		return c.readBuffered(response.Body, request.Stops, sink)
	}
	return c.readStream(ctx, response.Body, request.Stops, sink, guard)
}

func (c *Client) post(ctx context.Context, encoded []byte) (*http.Response, error) {
	request, err := http.NewRequestWithContext(ctx, http.MethodPost, c.endpoint, bytes.NewReader(encoded))
	if err != nil {
		return nil, fmt.Errorf("%w: build request: %v", ErrRemote, err)
	}
	for name, values := range c.headers {
		for _, value := range values {
			request.Header.Add(name, value)
		}
	}
	request.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		request.Header.Set("Authorization", "Bearer "+c.apiKey)
	}
	response, err := c.httpClient.Do(request)
	if err != nil {
		if ctx.Err() != nil {
			return nil, ctx.Err()
		}
		return nil, fmt.Errorf("%w: request failed: %v", ErrRemote, err)
	}
	return response, nil
}

func (c *Client) readBuffered(
	body io.Reader,
	stops []string,
	sink continuation.EventSink,
) (continuation.Result, error) {
	payload, err := io.ReadAll(io.LimitReader(body, maxResponseBytes+1))
	if err != nil {
		return continuation.Result{}, fmt.Errorf("%w: read response: %v", ErrRemote, err)
	}
	if len(payload) > maxResponseBytes {
		return continuation.Result{}, fmt.Errorf("%w: response exceeded %d bytes", ErrRemote, maxResponseBytes)
	}
	var decoded responseBody
	if err := json.Unmarshal(payload, &decoded); err != nil {
		return continuation.Result{}, fmt.Errorf(
			"%w: decode response: %s", ErrRemote, httputil.SafeResponseMessage(payload, c.apiKey),
		)
	}
	if err := decoded.err(c.apiKey); err != nil {
		return continuation.Result{}, err
	}
	for _, item := range decoded.Choices {
		if item.Index != 0 {
			continue
		}
		result := continuation.Result{
			Text:         item.Text,
			FinishReason: finishReason(item.FinishReason),
			Usage:        serverUsage(decoded.Usage),
			Stop:         stopString(item.StopReason),
		}
		if text, stop := httputil.TruncateAtStopMatch(result.Text, stops); stop != "" {
			result.Text, result.Stop, result.FinishReason = text, stop, continuation.FinishStop
		}
		if result.Text != "" && sink != nil {
			if err := sink(continuation.Event{Kind: continuation.EventTextDelta, Text: result.Text}); err != nil {
				result.FinishReason = continuation.FinishCancelled
				return result, err
			}
		}
		return result, nil
	}
	return continuation.Result{}, fmt.Errorf("%w: response has no choices", ErrRemote)
}

func (c *Client) readStream(
	ctx context.Context,
	body io.Reader,
	stops []string,
	sink continuation.EventSink,
	guard *continuation.LoopGuard,
) (continuation.Result, error) {
	scanner := bufio.NewScanner(body)
	scanner.Buffer(make([]byte, 64*1024), maxResponseBytes)
	var text strings.Builder
	pending := ""
	finish := continuation.FinishUnknown
	serverStop := ""
	usage := continuation.Usage{}
	sawChoice, sawDone := false, false
	responseBytes := 0
	partial := func(reason continuation.FinishReason) continuation.Result {
		return continuation.Result{Text: text.String(), FinishReason: reason, Usage: serverUsage(usage)}
	}
	emit := func(value string) error {
		if value == "" {
			return nil
		}
		text.WriteString(value)
		if sink == nil {
			return nil
		}
		return sink(continuation.Event{Kind: continuation.EventTextDelta, Text: value})
	}
	for scanner.Scan() {
		line := scanner.Text()
		responseBytes += len(line) + 1
		if responseBytes > maxResponseBytes {
			return continuation.Result{}, fmt.Errorf("%w: response exceeded %d bytes", ErrRemote, maxResponseBytes)
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
		var chunk responseBody
		if err := json.Unmarshal([]byte(data), &chunk); err != nil {
			return continuation.Result{}, fmt.Errorf("%w: decode stream chunk: %v", ErrRemote, err)
		}
		if err := chunk.err(c.apiKey); err != nil {
			return continuation.Result{}, err
		}
		if chunk.Usage != (continuation.Usage{}) {
			usage = chunk.Usage
		}
		for _, item := range chunk.Choices {
			if item.Index != 0 {
				continue
			}
			sawChoice = true
			if item.FinishReason != "" {
				finish = finishReason(item.FinishReason)
				serverStop = stopString(item.StopReason)
			}
			pending += item.Text
			safe, tail, stop := httputil.SplitAtStop(pending, stops)
			if err := emit(safe); err != nil {
				return partial(continuation.FinishCancelled), err
			}
			pending = tail
			if stop != "" {
				// Returning closes the body, which aborts the server request.
				result := partial(continuation.FinishStop)
				result.Stop = stop
				return result, nil
			}
			if guard != nil && guard.Write(safe) {
				return partial(continuation.FinishLength), nil
			}
		}
	}
	if err := scanner.Err(); err != nil {
		if ctx.Err() != nil {
			return partial(continuation.FinishCancelled), ctx.Err()
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
		return partial(continuation.FinishCancelled), err
	}
	result := partial(finish)
	result.Stop = serverStop
	return result, nil
}

// stopString returns the stop sequence the server matched and cut, or "" when
// it stopped on a token id or EOS (which leave no text to restore).
func stopString(raw json.RawMessage) string {
	var value string
	if len(raw) == 0 || json.Unmarshal(raw, &value) != nil {
		return ""
	}
	return value
}

func serverUsage(usage continuation.Usage) continuation.Usage {
	if usage.PromptTokens > 0 {
		usage.PromptSource = continuation.UsageSourceServer
	}
	if usage.CompletionTokens > 0 {
		usage.CompletionSource = continuation.UsageSourceServer
	}
	return usage
}

func finishReason(value string) continuation.FinishReason {
	switch value {
	case "stop":
		return continuation.FinishStop
	case "length":
		return continuation.FinishLength
	case "abort":
		return continuation.FinishCancelled
	default:
		return continuation.FinishUnknown
	}
}

var _ continuation.Generator = (*Client)(nil)
