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
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

const maxResponseBytes = 4 * 1024 * 1024

var ErrRemote = errors.New("rwkv_lightning continuation error")

// StopTokenMode selects how the request populates rwkv_lightning's stop_tokens.
type StopTokenMode string

const (
	// StopTokenText forwards the request's decoded-text stop sequences, which is
	// the wire type rwkv_lightning documents and expects.
	StopTokenText StopTokenMode = "text"
	// StopTokenEOS sends the legacy integer EOS token list.
	StopTokenEOS StopTokenMode = "eos"
	// StopTokenNone omits the field so the server applies its own defaults.
	StopTokenNone StopTokenMode = "none"
)

type Config struct {
	Endpoint string
	Model    string
	Password string
	// StopTokenMode selects the stop_tokens wire form. The zero value forwards
	// the request's decoded-text stops.
	StopTokenMode StopTokenMode
	// StopTokenIDs is the integer list used when StopTokenMode is StopTokenEOS.
	// A nil slice defaults to EOS only.
	StopTokenIDs []int
	// Stream selects the SSE transport. The zero value streams, matching the
	// server default; a false pointer requests one buffered JSON response, which
	// carries a real finish_reason and avoids the SSE path entirely.
	Stream *bool
	// BatchWait coalesces concurrent Continue calls that have compatible
	// generation settings into one rwkv_lightning contents[] request. A zero
	// duration preserves the one-request-per-call behavior.
	BatchWait  time.Duration
	Headers    http.Header
	HTTPClient *http.Client
}

type Client struct {
	endpoint      string
	model         string
	password      string
	stopTokenMode StopTokenMode
	stopTokenIDs  []int
	stream        bool
	batchWait     time.Duration
	headers       http.Header
	httpClient    *http.Client
	batchMu       sync.Mutex
	batchPending  []*pendingCall
	batchTimer    *time.Timer
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
	stopTokenMode := config.StopTokenMode
	if stopTokenMode == "" {
		stopTokenMode = StopTokenText
	}
	switch stopTokenMode {
	case StopTokenText, StopTokenEOS, StopTokenNone:
	default:
		return nil, fmt.Errorf(
			"%w: stop token mode must be text, eos, or none",
			continuation.ErrInvalidRequest,
		)
	}
	stopTokenIDs := config.StopTokenIDs
	if stopTokenIDs == nil {
		stopTokenIDs = []int{0}
	}
	stream := true
	if config.Stream != nil {
		stream = *config.Stream
	}
	return &Client{
		endpoint:      endpoint,
		model:         model,
		password:      config.Password,
		stopTokenMode: stopTokenMode,
		stopTokenIDs:  stopTokenIDs,
		stream:        stream,
		batchWait:     config.BatchWait,
		headers:       config.Headers.Clone(),
		httpClient:    httpClient,
	}, nil
}

type requestBody struct {
	Model          string   `json:"model"`
	Contents       []string `json:"contents"`
	MaxTokens      int      `json:"max_tokens"`
	StopTokens     any      `json:"stop_tokens,omitempty"`
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

// bufferedBody is the stream=false shape: one OpenAI-style completion object
// carrying the whole message and a real finish_reason.
type bufferedBody struct {
	Choices []struct {
		Index   int `json:"index"`
		Message struct {
			Content string `json:"content"`
		} `json:"message"`
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
	if c.batchWait > 0 {
		return c.continueBatched(ctx, request, sink)
	}
	return c.continueOne(ctx, request, sink)
}

func (c *Client) continueOne(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	encoded, err := json.Marshal(requestBody{
		Model:          model,
		Contents:       []string{request.Prompt},
		MaxTokens:      request.MaxOutputTokens,
		StopTokens:     c.serverStopTokens(request.Stops),
		Temperature:    request.Sampling.Temperature,
		TopK:           request.Sampling.TopK,
		TopP:           request.Sampling.TopP,
		AlphaPresence:  request.Sampling.PresencePenalty,
		AlphaFrequency: request.Sampling.FrequencyPenalty,
		AlphaDecay:     request.Sampling.PenaltyDecay,
		Stream:         c.stream,
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
	if !c.stream {
		return readBufferedResponse(
			response.Body,
			request.Stops,
			request.MaxOutputTokens,
			sink,
			c.password,
		)
	}
	return readStreamResponse(
		ctx,
		response.Body,
		request.Stops,
		request.MaxOutputTokens,
		sink,
		c.password,
	)
}

// readBufferedResponse handles stream=false. The whole completion arrives at
// once, so decoded-text stops are applied over the full text rather than
// incrementally, and the server's finish_reason is preferred when present.
func readBufferedResponse(
	body io.Reader,
	stops []string,
	maxOutputTokens int,
	sink continuation.EventSink,
	secret string,
) (continuation.Result, error) {
	payload, err := io.ReadAll(io.LimitReader(body, maxResponseBytes+1))
	if err != nil {
		return continuation.Result{}, fmt.Errorf("%w: read response: %v", ErrRemote, err)
	}
	if len(payload) > maxResponseBytes {
		return continuation.Result{}, fmt.Errorf(
			"%w: response exceeded %d bytes",
			ErrRemote,
			maxResponseBytes,
		)
	}
	var buffered bufferedBody
	if err := json.Unmarshal(payload, &buffered); err != nil {
		return continuation.Result{}, fmt.Errorf(
			"%w: decode response: %s",
			ErrRemote,
			safeResponseMessage(payload, secret),
		)
	}
	if len(buffered.Error) != 0 && string(buffered.Error) != "null" {
		return continuation.Result{}, fmt.Errorf(
			"%w: response error: %s",
			ErrRemote,
			safeResponseMessage(buffered.Error, secret),
		)
	}
	text := ""
	finish := continuation.FinishUnknown
	found := false
	for _, choice := range buffered.Choices {
		if choice.Index != 0 {
			continue
		}
		found = true
		text = choice.Message.Content
		if choice.FinishReason != "" {
			finish = finishReason(choice.FinishReason)
		}
		break
	}
	if !found {
		return continuation.Result{}, fmt.Errorf("%w: response has no choices", ErrRemote)
	}
	if truncated, stopped := truncateAtStop(text, stops); stopped {
		text = truncated
		finish = continuation.FinishStop
	}
	if text != "" && sink != nil {
		if err := sink(continuation.Event{
			Kind: continuation.EventTextDelta,
			Text: text,
		}); err != nil {
			return continuation.Result{
				Text:         text,
				FinishReason: continuation.FinishCancelled,
				Usage:        buffered.Usage,
			}, err
		}
	}
	return continuation.Result{
		Text: text,
		// Only usage can indicate a length finish here; character count is not a
		// token count, so pass 0 rather than inventing a token estimate.
		FinishReason: inferFinishReason(finish, buffered.Usage, 0, maxOutputTokens),
		Usage:        buffered.Usage,
	}, nil
}

// truncateAtStop cuts text at the earliest decoded-text stop sequence. The
// buffered path has the whole completion up front, so it needs no streaming
// tail-carry logic.
func truncateAtStop(value string, stops []string) (string, bool) {
	cut := len(value)
	for _, stop := range stops {
		if stop == "" {
			continue
		}
		if index := strings.Index(value, stop); index >= 0 && index < cut {
			cut = index
		}
	}
	if cut == len(value) {
		return value, false
	}
	return value[:cut], true
}

func readStreamResponse(
	ctx context.Context,
	body io.Reader,
	stops []string,
	maxOutputTokens int,
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
	deltas := 0
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
			if choice.Delta.Content != "" {
				deltas++
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
		FinishReason: inferFinishReason(finish, usage, deltas, maxOutputTokens),
		Usage:        usage,
	}, nil
}

// inferFinishReason recovers a finish reason for deployments that stream none at
// all, which would otherwise leave every response FinishUnknown and make the
// action protocol misreport it as a malformed envelope or an incomplete think
// block. A stream that reached its token budget is a length truncation. A stream
// that ended below the budget means the server stopped on its own — EOS, or a
// server-side stop sequence it consumed without echoing — which is a normal stop.
// chunk_size is 1, so one content delta is one token; usage is preferred when the
// deployment reports it.
func inferFinishReason(
	finish continuation.FinishReason,
	usage continuation.Usage,
	deltas int,
	maxOutputTokens int,
) continuation.FinishReason {
	if finish != continuation.FinishUnknown {
		return finish
	}
	generated := deltas
	if usage.CompletionTokens > 0 {
		generated = usage.CompletionTokens
	}
	if maxOutputTokens > 0 && generated >= maxOutputTokens {
		return continuation.FinishLength
	}
	if generated > 0 {
		return continuation.FinishStop
	}
	return finish
}

// serverStopTokens renders the configured stop_tokens payload. rwkv_lightning
// documents stop_tokens as decoded-text strings, so StopTokenText forwards the
// request's own stop sequences and lets the server stop generating early instead
// of running to max_tokens and relying only on client-side truncation.
func (c *Client) serverStopTokens(stops []string) any {
	switch c.stopTokenMode {
	case StopTokenEOS:
		if len(c.stopTokenIDs) == 0 {
			return nil
		}
		return c.stopTokenIDs
	case StopTokenNone:
		return nil
	default:
		if len(stops) == 0 {
			return nil
		}
		return stops
	}
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
