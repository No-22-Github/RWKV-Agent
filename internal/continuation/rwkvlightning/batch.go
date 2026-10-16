package rwkvlightning

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/httputil"
)

type pendingCall struct {
	sinkMu   sync.Mutex
	closed   bool
	ctx      context.Context
	request  continuation.Request
	sink     continuation.EventSink
	response chan batchOutcome
	// guard, when set, ends this call early once its stream starts looping.
	guard *continuation.LoopGuard
}

type batchOutcome struct {
	result continuation.Result
	err    error
	// delivered marks an outcome the stream reader already handed to its call
	// as soon as that choice stopped; executeBatch must not deliver it again.
	delivered bool
}

func (c *Client) continueBatched(
	ctx context.Context,
	request continuation.Request,
	sink continuation.EventSink,
) (continuation.Result, error) {
	ctx, finish := context.WithCancel(ctx)
	defer finish()
	call := &pendingCall{
		ctx:      ctx,
		request:  request,
		sink:     sink,
		response: make(chan batchOutcome, 1),
		guard:    c.newLoopGuard(),
	}
	defer func() {
		call.sinkMu.Lock()
		call.closed = true
		call.sinkMu.Unlock()
	}()
	c.batchMu.Lock()
	if len(c.batchPending) == 0 {
		c.pendingSince = time.Now()
	}
	c.batchPending = append(c.batchPending, call)
	var batches [][]*pendingCall
	if c.batchMax > 0 && len(c.batchPending) >= c.batchMax {
		// A full window goes out now, slot or not: it is as wide as a
		// request gets, which is what the in-flight cap is waiting for.
		batches = c.takeBatchesLocked()
	} else if c.batchTimer == nil && c.holdTimer == nil {
		c.batchTimer = time.AfterFunc(c.batchWait, c.windowClosed)
	}
	c.batchMu.Unlock()
	c.launch(batches)

	select {
	case outcome := <-call.response:
		return outcome.result, outcome.err
	case <-ctx.Done():
		return continuation.Result{FinishReason: continuation.FinishCancelled}, ctx.Err()
	}
}

// windowClosed sends the gathered calls when a request slot is free, and
// otherwise leaves them queued until a running request finishes or the hold
// expires.
func (c *Client) windowClosed() {
	c.batchMu.Lock()
	c.batchTimer = nil
	var batches [][]*pendingCall
	if c.batchInflight <= 0 || c.inflight < c.batchInflight {
		batches = c.takeBatchesLocked()
	} else if len(c.batchPending) > 0 && c.holdTimer == nil {
		c.holdTimer = time.AfterFunc(time.Until(c.pendingSince.Add(c.batchHold)), c.holdExpired)
	}
	c.batchMu.Unlock()
	c.launch(batches)
}

// holdExpired sends calls that waited batchHold for a slot: a request whose
// last live row repeats up to max_tokens would otherwise stall the queue.
func (c *Client) holdExpired() {
	c.batchMu.Lock()
	c.holdTimer = nil
	batches := c.takeBatchesLocked()
	c.batchMu.Unlock()
	c.launch(batches)
}

// requestFinished frees a slot and sends whatever queued behind it, unless
// the gathering window of a fresh arrival is still open.
func (c *Client) requestFinished() {
	c.batchMu.Lock()
	c.inflight--
	var batches [][]*pendingCall
	if c.batchTimer == nil {
		batches = c.takeBatchesLocked()
	}
	c.batchMu.Unlock()
	c.launch(batches)
}

// flushBatch sends everything pending at once, ignoring the in-flight cap.
func (c *Client) flushBatch() {
	c.batchMu.Lock()
	batches := c.takeBatchesLocked()
	c.batchMu.Unlock()
	c.launch(batches)
}

// takeBatchesLocked empties the queue into requests: one per compatibility
// group, split at batchMax. Each counts as in flight until requestFinished.
func (c *Client) takeBatchesLocked() [][]*pendingCall {
	calls := c.batchPending
	c.batchPending = nil
	for _, timer := range []**time.Timer{&c.batchTimer, &c.holdTimer} {
		if *timer != nil {
			(*timer).Stop()
			*timer = nil
		}
	}
	if len(calls) == 0 {
		return nil
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
	var batches [][]*pendingCall
	for _, key := range order {
		group := groups[key]
		for len(group) > 0 {
			size := len(group)
			if c.batchMax > 0 && size > c.batchMax {
				size = c.batchMax
			}
			batches = append(batches, group[:size:size])
			group = group[size:]
		}
	}
	c.inflight += len(batches)
	return batches
}

func (c *Client) launch(batches [][]*pendingCall) {
	for _, batch := range batches {
		go func() {
			defer c.requestFinished()
			c.executeBatch(batch)
		}()
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
		StateID    string
		// rwkv_lightning binds one MiSS adapter per request, so calls on
		// different adapters can never share contents[].
		AdapterID string
	}{
		Model:      model,
		MaxTokens:  c.groupMaxTokens(request),
		StopTokens: c.serverStopTokens(request.Stops),
		Sampling:   request.Sampling,
		Stream:     c.stream,
		StateID:    c.effectiveStateID(request),
		AdapterID:  c.adapterID,
	})
	return string(encoded)
}

// groupMaxTokens is the token budget that splits calls into separate
// requests. A streamed batch is sent with its widest member's budget and cuts
// each narrower member locally (one delta per token at chunk_size 1), so
// decision, answer and compression calls share a request. A buffered response
// cannot be cut per token, so there the budget stays part of the key.
func (c *Client) groupMaxTokens(request continuation.Request) int {
	if c.stream {
		return 0
	}
	return request.MaxOutputTokens
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
		request.MaxOutputTokens = max(request.MaxOutputTokens, call.request.MaxOutputTokens)
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
		outcomes = readBatchStreamResponse(requestContext, response.Body, active, c.password, request.MaxOutputTokens)
	} else {
		outcomes = readBatchBufferedResponse(response.Body, active, c.password)
	}
	for index, call := range active {
		if !outcomes[index].delivered {
			call.deliver(outcomes[index])
		}
	}
}

func batchRequestContext(calls []*pendingCall) (context.Context, context.CancelFunc) {
	var earliest time.Time
	for _, call := range calls {
		if deadline, ok := call.ctx.Deadline(); ok && (earliest.IsZero() || deadline.Before(earliest)) {
			earliest = deadline
		}
	}
	var ctx context.Context
	var cancel context.CancelFunc
	if !earliest.IsZero() {
		ctx, cancel = context.WithDeadline(context.Background(), earliest)
	} else {
		ctx, cancel = context.WithCancel(context.Background())
	}
	// A shared request lives only while at least one caller still needs it.
	var remaining atomic.Int64
	remaining.Store(int64(len(calls)))
	stops := make([]func() bool, 0, len(calls))
	for _, call := range calls {
		stops = append(stops, context.AfterFunc(call.ctx, func() {
			if remaining.Add(-1) == 0 {
				cancel()
			}
		}))
	}
	return ctx, func() {
		for _, stop := range stops {
			stop()
		}
		cancel()
	}
}

// Serialize callbacks with caller teardown: no observer may run after Continue returns.
func (call *pendingCall) emit(event continuation.Event) error {
	call.sinkMu.Lock()
	defer call.sinkMu.Unlock()
	if err := call.ctx.Err(); err != nil {
		return err
	}
	if call.closed {
		return context.Canceled
	}
	if call.sink == nil {
		return nil
	}
	return call.sink(event)
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
	result    strings.Builder
	pending   string
	finish    continuation.FinishReason
	deltas    int
	saw       bool
	stopped   bool
	stop      string
	err       error
	delivered bool
	// lastTick is the batch clock when this choice last streamed content.
	lastTick int
}

// batchSilentSteps is how many decode steps a choice may stream nothing
// while its peers keep streaming before it counts as ended by the server.
// rwkv_lightning stops a row on EOS without saying so until the whole request
// ends; a live row streams one delta per token, and only a split multi-byte
// character (at most three tokens) holds a delta back.
const batchSilentSteps = 64

func readBatchStreamResponse(
	ctx context.Context,
	body io.Reader,
	calls []*pendingCall,
	secret string,
	requestMaxTokens int,
) []batchOutcome {
	states := make([]batchStreamState, len(calls))
	// clock counts decode steps: the most content chunks any choice of this
	// request has streamed, including choices already handed back, which the
	// server keeps decoding.
	clock := 0
	ticks := make([]int, len(calls))
	scanner := bufio.NewScanner(body)
	scanner.Buffer(make([]byte, 64*1024), maxResponseBytes)
	usage := continuation.Usage{}
	sawDone := false
	responseBytes := 0
	limit := batchResponseLimit(len(calls))
	var streamErr error
	// A server usage block is passed to every call as before; without one,
	// each call gets the count of its own streamed chunks.
	callUsage := func(index int) continuation.Usage {
		return streamUsage(usage, states[index].deltas)
	}
	// A choice that hit a stop sequence, or that the server marked finished
	// with a finish_reason (EOS, a server-side stop token, max_tokens), is done
	// for its caller: hand its result over right away instead of after [DONE].
	// A checkpoint that writes the next "User:" turn instead of EOS keeps the
	// server generating up to max_tokens, which made a two-character reply wait
	// seconds for the whole batch. Once every choice is finished, stop reading;
	// executeBatch then closes the body, which also lets the server drop the
	// generation.
	//
	// rwkv_lightning_cuda (2026-10) sends every choice's finish_reason in one
	// closing chunk after the whole request ends, and a row that samples EOS
	// just stops producing chunks. Such a call is therefore only released when
	// the batch ends; the finish_reason path covers servers that report each
	// choice as it ends, and text stops are always caught here.
	deliverEarly := func(index int) {
		state := &states[index]
		state.delivered = true
		finish := state.finish
		if state.err == nil {
			finish = inferFinishReason(finish, continuation.Usage{}, state.deltas, calls[index].request.MaxOutputTokens)
		}
		calls[index].deliver(batchOutcome{result: continuation.Result{
			Text: state.result.String(), FinishReason: finish, Usage: callUsage(index), Stop: state.stop,
		}, err: state.err})
	}
	// finishChoice hands back a choice that ended without a stop sequence:
	// what is still held back as a possible stop prefix is final text now.
	finishChoice := func(index int, finish continuation.FinishReason) {
		state := &states[index]
		state.finish = finish
		if err := emitBatchText(state, calls[index].emit, state.pending); err != nil {
			state.err = err
			state.finish = continuation.FinishCancelled
		}
		state.pending = ""
		state.stopped = true
		deliverEarly(index)
	}
	allFinished := func() bool {
		for index := range states {
			if !states[index].delivered {
				return false
			}
		}
		return true
	}
	for scanner.Scan() {
		line := scanner.Text()
		responseBytes += len(line) + 1
		if responseBytes > limit {
			streamErr = fmt.Errorf("%w: response exceeded %d bytes", ErrRemote, limit)
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
			if choice.Delta.Content != "" {
				ticks[choice.Index]++
				clock = max(clock, ticks[choice.Index])
				state.lastTick = clock
			}
			if err := calls[choice.Index].ctx.Err(); err != nil && !state.delivered {
				state.err = err
				state.finish = continuation.FinishCancelled
				deliverEarly(choice.Index)
			}
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
			text, tail, stop := splitAtStop(state.pending, calls[choice.Index].request.Stops)
			if err := emitBatchText(state, calls[choice.Index].emit, text); err != nil {
				state.err = err
				state.finish = continuation.FinishCancelled
				deliverEarly(choice.Index)
				continue
			}
			state.pending = tail
			if stop != "" {
				state.stopped = true
				state.stop = stop
				state.finish = continuation.FinishStop
				deliverEarly(choice.Index)
				continue
			}
			if guard := calls[choice.Index].guard; guard != nil && guard.Write(text) {
				// The server keeps decoding this row until the request ends;
				// its caller gets the loop-free part now, as a length finish.
				finishChoice(choice.Index, continuation.FinishLength)
				continue
			}
			if budget := calls[choice.Index].request.MaxOutputTokens; budget > 0 &&
				budget < requestMaxTokens && state.deltas >= budget {
				// The request runs to its widest member's budget; this call's
				// own budget ends here.
				finishChoice(choice.Index, continuation.FinishLength)
				continue
			}
			if choice.FinishReason != "" {
				finishChoice(choice.Index, state.finish)
			}
		}
		for index := range states {
			state := &states[index]
			if !state.delivered && !state.stopped && state.err == nil && ticks[index] > 0 &&
				clock-state.lastTick >= batchSilentSteps {
				// The server ended this choice (EOS or a stop token) some
				// steps ago; its text is complete. A choice that never
				// streamed is left for the request's end.
				finishChoice(index, continuation.FinishUnknown)
			}
		}
		if allFinished() {
			sawDone = true
			break
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
		if state.delivered {
			outcomes[index] = batchOutcome{delivered: true}
			continue
		}
		if streamErr != nil && state.err == nil {
			state.err = streamErr
		}
		if state.err == nil && !state.saw {
			state.err = fmt.Errorf("%w: response has no choice for index %d", ErrRemote, index)
		}
		if state.err == nil && !state.stopped {
			if err := emitBatchText(state, calls[index].emit, state.pending); err != nil {
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
				Usage: callUsage(index),
				Stop:  state.stop,
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
	limit := batchResponseLimit(len(calls))
	payload, err := io.ReadAll(io.LimitReader(body, int64(limit)+1))
	if err != nil {
		return batchOutcomesWithError(len(calls), fmt.Errorf("%w: read response: %v", ErrRemote, err))
	}
	if len(payload) > limit {
		return batchOutcomesWithError(len(calls), fmt.Errorf(
			"%w: response exceeded %d bytes",
			ErrRemote,
			limit,
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
	shared := streamUsage(buffered.Usage, 0)
	found := make([]bool, len(calls))
	for _, choice := range buffered.Choices {
		if choice.Index < 0 || choice.Index >= len(calls) {
			continue
		}
		found[choice.Index] = true
		text := choice.Message.Content
		finish := finishReason(choice.FinishReason)
		matchedStop := ""
		if truncated, stop := httputil.TruncateAtStopMatch(text, calls[choice.Index].request.Stops); stop != "" {
			text = truncated
			finish = continuation.FinishStop
			matchedStop = stop
		}
		if text != "" && calls[choice.Index].sink != nil {
			if err := calls[choice.Index].emit(continuation.Event{
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
			Usage: shared,
			Stop:  matchedStop,
		}}
	}
	for index, ok := range found {
		if !ok {
			outcomes[index].err = fmt.Errorf("%w: response has no choice for index %d", ErrRemote, index)
		}
	}
	return outcomes
}

// batchResponseLimit is the byte budget for one coalesced response. The
// single-call cap guards against one runaway generation; a batch carries one
// such generation per call, so the budget scales with the call count. A fixed
// 4 MiB across the whole batch failed every call of a batch whose members were
// each well inside their own budget (2026-09-23: 132/148 workbank cases lost
// once the decision budget rose from 512 to 2048 tokens).
func batchResponseLimit(calls int) int {
	if calls < 1 {
		calls = 1
	}
	return maxResponseBytes * calls
}

func batchOutcomesWithError(count int, err error) []batchOutcome {
	outcomes := make([]batchOutcome, count)
	for index := range outcomes {
		outcomes[index].err = err
	}
	return outcomes
}
