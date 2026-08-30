package rwkvlightning

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/httputil"
)

type pendingCall struct {
	ctx      context.Context
	request  continuation.Request
	sink     continuation.EventSink
	response chan batchOutcome
}

type batchOutcome struct {
	result continuation.Result
	err    error
}

func (c *Client) continueBatched(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	call := &pendingCall{
		ctx:      ctx,
		request:  request,
		sink:     sink,
		response: make(chan batchOutcome, 1),
	}
	c.batchMu.Lock()
	c.batchPending = append(c.batchPending, call)
	if c.batchTimer == nil {
		c.batchTimer = time.AfterFunc(c.batchWait, c.flushBatch)
	}
	c.batchMu.Unlock()

	select {
	case outcome := <-call.response:
		return outcome.result, outcome.err
	case <-ctx.Done():
		return continuation.Result{FinishReason: continuation.FinishCancelled}, ctx.Err()
	}
}

func (c *Client) flushBatch() {
	c.batchMu.Lock()
	calls := c.batchPending
	c.batchPending = nil
	c.batchTimer = nil
	c.batchMu.Unlock()
	if len(calls) == 0 {
		return
	}

	groups := make(map[string][]*pendingCall)
	order := make([]string, 0, len(calls))
	for _, call := range calls {
		key := c.batchCompatibilityKey(call.request)
		if _, exists := groups[key]; !exists {
			order = append(order, key)
		}
		groups[key] = append(groups[key], call)
	}
	for _, key := range order {
		go c.executeBatch(groups[key])
	}
}

func (c *Client) batchCompatibilityKey(request continuation.Request) string {
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	encoded, _ := json.Marshal(struct {
		Model      string
		MaxTokens  int
		StopTokens any
		Sampling   continuation.Sampling
		Stream     bool
	}{
		Model:      model,
		MaxTokens:  request.MaxOutputTokens,
		StopTokens: c.serverStopTokens(request.Stops),
		Sampling:   request.Sampling,
		Stream:     c.stream,
	})
	return string(encoded)
}

func (c *Client) executeBatch(calls []*pendingCall) {
	active := make([]*pendingCall, 0, len(calls))
	for _, call := range calls {
		if err := call.ctx.Err(); err != nil {
			call.deliver(batchOutcome{
				result: continuation.Result{FinishReason: continuation.FinishCancelled},
				err:    err,
			})
			continue
		}
		active = append(active, call)
	}
	if len(active) == 0 {
		return
	}

	request := active[0].request
	model := strings.TrimSpace(request.Model)
	if model == "" {
		model = c.model
	}
	contents := make([]string, len(active))
	for index, call := range active {
		contents[index] = call.request.Prompt
	}
	encoded, err := c.encodeRequestBody(model, contents, request)
	if err != nil {
		c.deliverBatchError(active, err)
		return
	}

	requestContext, cancel := batchRequestContext(active)
	defer cancel()
	response, err := c.post(requestContext, encoded)
	if err != nil {
		if requestContext.Err() != nil {
			c.deliverBatchError(active, requestContext.Err())
		} else {
			c.deliverBatchError(active, err)
		}
		return
	}
	defer response.Body.Close()
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		c.deliverBatchError(active, c.responseError(response))
		return
	}

	var outcomes []batchOutcome
	if c.stream {
		outcomes = readBatchStreamResponse(requestContext, response.Body, active, c.password)
	} else {
		outcomes = readBatchBufferedResponse(response.Body, active, c.password)
	}
	for index, call := range active {
		call.deliver(outcomes[index])
	}
}

func batchRequestContext(calls []*pendingCall) (context.Context, context.CancelFunc) {
	var earliest time.Time
	for _, call := range calls {
		if deadline, ok := call.ctx.Deadline(); ok && (earliest.IsZero() || deadline.Before(earliest)) {
			earliest = deadline
		}
	}
	if !earliest.IsZero() {
		return context.WithDeadline(context.Background(), earliest)
	}
	return context.WithCancel(context.Background())
}

func (call *pendingCall) deliver(outcome batchOutcome) {
	call.response <- outcome
}

func (c *Client) deliverBatchError(calls []*pendingCall, err error) {
	for _, call := range calls {
		finish := continuation.FinishUnknown
		if errorsIsContext(err) {
			finish = continuation.FinishCancelled
		}
		call.deliver(batchOutcome{result: continuation.Result{FinishReason: finish}, err: err})
	}
}

func errorsIsContext(err error) bool {
	return err == context.Canceled || err == context.DeadlineExceeded
}

type batchStreamState struct {
	result  strings.Builder
	pending string
	finish  continuation.FinishReason
	deltas  int
	saw     bool
	stopped bool
	err     error
}

func readBatchStreamResponse(
	ctx context.Context,
	body io.Reader,
	calls []*pendingCall,
	secret string,
) []batchOutcome {
	states := make([]batchStreamState, len(calls))
	scanner := bufio.NewScanner(body)
	scanner.Buffer(make([]byte, 64*1024), maxResponseBytes)
	usage := continuation.Usage{}
	sawDone := false
	responseBytes := 0
	var streamErr error
	for scanner.Scan() {
		line := scanner.Text()
		responseBytes += len(line) + 1
		if responseBytes > maxResponseBytes {
			streamErr = fmt.Errorf("%w: response exceeded %d bytes", ErrRemote, maxResponseBytes)
			break
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
			streamErr = fmt.Errorf("%w: decode stream chunk: %v", ErrRemote, err)
			break
		}
		if len(chunk.Error) != 0 && string(chunk.Error) != "null" {
			streamErr = fmt.Errorf(
				"%w: stream error: %s",
				ErrRemote,
				httputil.SafeResponseMessage(chunk.Error, secret),
			)
			break
		}
		if chunk.Usage != (continuation.Usage{}) {
			usage = chunk.Usage
		}
		for _, choice := range chunk.Choices {
			if choice.Index < 0 || choice.Index >= len(states) {
				continue
			}
			state := &states[choice.Index]
			state.saw = true
			if state.stopped || state.err != nil {
				continue
			}
			if choice.FinishReason != "" {
				state.finish = finishReason(choice.FinishReason)
			}
			if choice.Delta.Content != "" {
				state.deltas++
			}
			state.pending += choice.Delta.Content
			text, tail, stopped := splitAtStop(state.pending, calls[choice.Index].request.Stops)
			if err := emitBatchText(state, calls[choice.Index].sink, text); err != nil {
				state.err = err
				state.finish = continuation.FinishCancelled
				continue
			}
			state.pending = tail
			if stopped {
				state.stopped = true
				state.finish = continuation.FinishStop
			}
		}
	}
	if streamErr == nil {
		if err := scanner.Err(); err != nil {
			if ctx.Err() != nil {
				streamErr = ctx.Err()
			} else {
				streamErr = fmt.Errorf("%w: read stream: %v", ErrRemote, err)
			}
		} else if !sawDone {
			streamErr = fmt.Errorf("%w: stream ended before [DONE]", ErrRemote)
		}
	}

	outcomes := make([]batchOutcome, len(calls))
	for index := range states {
		state := &states[index]
		if streamErr != nil && state.err == nil {
			state.err = streamErr
		}
		if state.err == nil && !state.saw {
			state.err = fmt.Errorf("%w: response has no choice for index %d", ErrRemote, index)
		}
		if state.err == nil && !state.stopped {
			if err := emitBatchText(state, calls[index].sink, state.pending); err != nil {
				state.err = err
				state.finish = continuation.FinishCancelled
			}
		}
		outcomes[index] = batchOutcome{
			result: continuation.Result{
				Text: state.result.String(),
				FinishReason: inferFinishReason(
					state.finish,
					continuation.Usage{},
					state.deltas,
					calls[index].request.MaxOutputTokens,
				),
				Usage: usage,
			},
			err: state.err,
		}
	}
	return outcomes
}

func emitBatchText(
	state *batchStreamState,
	sink continuation.EventSink,
	value string,
) error {
	if value == "" {
		return nil
	}
	state.result.WriteString(value)
	if sink == nil {
		return nil
	}
	return sink(continuation.Event{Kind: continuation.EventTextDelta, Text: value})
}

func readBatchBufferedResponse(
	body io.Reader,
	calls []*pendingCall,
	secret string,
) []batchOutcome {
	outcomes := make([]batchOutcome, len(calls))
	payload, err := io.ReadAll(io.LimitReader(body, maxResponseBytes+1))
	if err != nil {
		return batchOutcomesWithError(len(calls), fmt.Errorf("%w: read response: %v", ErrRemote, err))
	}
	if len(payload) > maxResponseBytes {
		return batchOutcomesWithError(len(calls), fmt.Errorf(
			"%w: response exceeded %d bytes",
			ErrRemote,
			maxResponseBytes,
		))
	}
	var buffered bufferedBody
	if err := json.Unmarshal(payload, &buffered); err != nil {
		return batchOutcomesWithError(len(calls), fmt.Errorf(
			"%w: decode response: %s",
			ErrRemote,
			httputil.SafeResponseMessage(payload, secret),
		))
	}
	if len(buffered.Error) != 0 && string(buffered.Error) != "null" {
		return batchOutcomesWithError(len(calls), fmt.Errorf(
			"%w: response error: %s",
			ErrRemote,
			httputil.SafeResponseMessage(buffered.Error, secret),
		))
	}
	found := make([]bool, len(calls))
	for _, choice := range buffered.Choices {
		if choice.Index < 0 || choice.Index >= len(calls) {
			continue
		}
		found[choice.Index] = true
		text := choice.Message.Content
		finish := finishReason(choice.FinishReason)
		if truncated, stopped := httputil.TruncateAtStop(text, calls[choice.Index].request.Stops); stopped {
			text = truncated
			finish = continuation.FinishStop
		}
		if text != "" && calls[choice.Index].sink != nil {
			if err := calls[choice.Index].sink(continuation.Event{
				Kind: continuation.EventTextDelta,
				Text: text,
			}); err != nil {
				outcomes[choice.Index] = batchOutcome{
					result: continuation.Result{
						Text:         text,
						FinishReason: continuation.FinishCancelled,
						Usage:        buffered.Usage,
					},
					err: err,
				}
				continue
			}
		}
		outcomes[choice.Index] = batchOutcome{result: continuation.Result{
			Text: text,
			FinishReason: inferFinishReason(
				finish,
				buffered.Usage,
				0,
				calls[choice.Index].request.MaxOutputTokens,
			),
			Usage: buffered.Usage,
		}}
	}
	for index, ok := range found {
		if !ok {
			outcomes[index].err = fmt.Errorf("%w: response has no choice for index %d", ErrRemote, index)
		}
	}
	return outcomes
}

func batchOutcomesWithError(count int, err error) []batchOutcome {
	outcomes := make([]batchOutcome, count)
	for index := range outcomes {
		outcomes[index].err = err
	}
	return outcomes
}
