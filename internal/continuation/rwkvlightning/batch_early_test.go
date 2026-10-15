package rwkvlightning

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// Early-delivery tests for the coalesced stream path: a short member of a
// merged batch must get its result when it is finished, not when the longest
// member is. The fake server plays each content by its prompt text.

// sseWriter streams chunks to one batch response, one flush per write.
type sseWriter struct {
	writer http.ResponseWriter
}

func (s sseWriter) choice(index int, content, finish string) {
	chunk := fmt.Sprintf(`{"choices":[{"index":%d,"delta":{"content":%q}}]}`, index, content)
	if finish != "" {
		chunk = fmt.Sprintf(`{"choices":[{"index":%d,"delta":{"content":%q},"finish_reason":%q}]}`, index, content, finish)
	}
	s.raw(chunk)
}

func (s sseWriter) raw(data string) {
	_, _ = fmt.Fprintf(s.writer, "data: %s\n\n", data)
	s.writer.(http.Flusher).Flush()
}

// batchServer decodes contents[], reports each request's width, and hands the
// prompt-to-index map to play.
func batchServer(t *testing.T, widths chan<- int, play func(r *http.Request, out sseWriter, index map[string]int)) *httptest.Server {
	t.Helper()
	return httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		var body requestBody
		if err := json.NewDecoder(request.Body).Decode(&body); err != nil {
			t.Error(err)
			return
		}
		if widths != nil {
			widths <- len(body.Contents)
		}
		index := make(map[string]int, len(body.Contents))
		for position, prompt := range body.Contents {
			index[prompt] = position
		}
		writer.Header().Set("Content-Type", "text/event-stream")
		writer.WriteHeader(http.StatusOK)
		play(request, sseWriter{writer}, index)
	}))
}

// loopUntil streams filler for index until the deadline or the client hangs up.
func loopUntil(r *http.Request, out sseWriter, index int, deadline time.Duration) bool {
	stop := time.After(deadline)
	for {
		select {
		case <-r.Context().Done():
			return false
		case <-stop:
			return true
		case <-time.After(10 * time.Millisecond):
			out.choice(index, "x", "")
		}
	}
}

func TestBatchStreamShortRepliesDoNotWaitForLongMember(t *testing.T) {
	t.Parallel()
	const longFor = 1500 * time.Millisecond
	widths := make(chan int, 4)
	server := batchServer(t, widths, func(r *http.Request, out sseWriter, index map[string]int) {
		// A checkpoint that writes the next turn: client-side stop.
		out.choice(index["user-stop"], " ok", "")
		out.choice(index["user-stop"], "\nUser:", "")
		// A server that reports each choice's finish as it ends (rwkv_lightning
		// today sends them all after the request ends).
		out.choice(index["eos"], "done", "")
		out.choice(index["eos"], "", "stop")
		// One member repeats itself until max_tokens.
		if loopUntil(r, out, index["loop"], longFor) {
			out.choice(index["loop"], "", "length")
			out.raw(`{"usage":{"prompt_tokens":3,"completion_tokens":9}}`)
			out.raw("[DONE]")
		}
	})
	defer server.Close()

	results := runBatchedCalls(t, batchClient(t, server, true), []string{"user-stop", "eos", "loop"}, nil)
	if width := <-widths; width != 3 {
		t.Fatalf("first request carried %d contents, want all 3 merged", width)
	}
	for _, prompt := range []string{"user-stop", "eos"} {
		result := results[prompt]
		if result.err != nil {
			t.Fatalf("%s: %v", prompt, result.err)
		}
		if result.elapsed > longFor/2 {
			t.Fatalf("%s waited %v for the looping member", prompt, result.elapsed)
		}
		if result.result.FinishReason != continuation.FinishStop {
			t.Fatalf("%s finish = %q", prompt, result.result.FinishReason)
		}
	}
	if got := results["user-stop"]; got.result.Text != " ok" || got.result.Stop != "\nUser:" || got.streamed != " ok" {
		t.Fatalf("user-stop = %+v streamed %q", got.result, got.streamed)
	}
	if got := results["eos"]; got.result.Text != "done" || got.streamed != "done" {
		t.Fatalf("eos = %+v streamed %q", got.result, got.streamed)
	}
	loop := results["loop"]
	if loop.err != nil {
		t.Fatal(loop.err)
	}
	if loop.elapsed < longFor || loop.result.FinishReason != continuation.FinishLength ||
		loop.result.Text == "" || strings.Trim(loop.result.Text, "x") != "" {
		t.Fatalf("loop = %+v after %v", loop.result, loop.elapsed)
	}
}

// A choice the server ends must also release the text held back as a
// possible stop prefix ("\nUs" could have grown into "\nUser:").
func TestBatchStreamFinishReasonFlushesHeldStopPrefix(t *testing.T) {
	t.Parallel()
	server := batchServer(t, nil, func(r *http.Request, out sseWriter, index map[string]int) {
		out.choice(index["held"], "answer\nUs", "")
		out.choice(index["held"], "", "stop")
		if loopUntil(r, out, index["loop"], 3*time.Second) {
			out.raw("[DONE]")
		}
	})
	defer server.Close()
	client := batchClient(t, server, true)
	ctx, cancel := context.WithTimeout(t.Context(), 5*time.Second)
	defer cancel()
	go func() {
		request := validRequest()
		request.Prompt = "loop"
		_, _ = client.Continue(ctx, request, nil)
	}()
	request := validRequest()
	request.Prompt = "held"
	var streamed strings.Builder
	started := time.Now()
	result, err := client.Continue(ctx, request, func(event continuation.Event) error {
		streamed.WriteString(event.Text)
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	if elapsed := time.Since(started); elapsed > time.Second {
		t.Fatalf("finished choice waited %v", elapsed)
	}
	if result.Text != "answer\nUs" || streamed.String() != "answer\nUs" || result.FinishReason != continuation.FinishStop {
		t.Fatalf("result = %+v streamed %q", result, streamed.String())
	}
}

func TestBatchStreamCancelledMemberLeavesPeerRunning(t *testing.T) {
	t.Parallel()
	widths := make(chan int, 2)
	server := batchServer(t, widths, func(r *http.Request, out sseWriter, index map[string]int) {
		for step := 0; step < 40; step++ {
			select {
			case <-r.Context().Done():
				return
			case <-time.After(10 * time.Millisecond):
			}
			out.choice(index["cancelled"], "c", "")
			out.choice(index["peer"], "p", "")
		}
		out.choice(index["peer"], "", "stop")
		out.raw("[DONE]")
	})
	defer server.Close()
	client := batchClient(t, server, true)

	ctx, cancel := context.WithCancel(t.Context())
	defer cancel()
	firstToken := make(chan struct{})
	var once sync.Once
	type outcome struct {
		result continuation.Result
		err    error
		after  time.Duration
	}
	cancelled := make(chan outcome, 1)
	peer := make(chan outcome, 1)
	var cancelledAt time.Time
	var mu sync.Mutex
	var lateEvents int
	returned := false
	go func() {
		request := validRequest()
		request.Prompt = "cancelled"
		result, err := client.Continue(ctx, request, func(continuation.Event) error {
			mu.Lock()
			if returned {
				lateEvents++
			}
			mu.Unlock()
			once.Do(func() { close(firstToken) })
			return nil
		})
		mu.Lock()
		returned = true
		mu.Unlock()
		cancelled <- outcome{result: result, err: err, after: time.Since(cancelledAt)}
	}()
	go func() {
		request := validRequest()
		request.Prompt = "peer"
		result, err := client.Continue(t.Context(), request, nil)
		peer <- outcome{result: result, err: err}
	}()
	if width := <-widths; width != 2 {
		t.Fatalf("request carried %d contents, want 2", width)
	}
	select {
	case <-firstToken:
	case <-time.After(3 * time.Second):
		t.Fatal("no token reached the cancelled member")
	}
	cancelledAt = time.Now()
	cancel()
	got := <-cancelled
	if !errors.Is(got.err, context.Canceled) || got.result.FinishReason != continuation.FinishCancelled {
		t.Fatalf("cancelled member = %+v, %v", got.result, got.err)
	}
	if got.after > 200*time.Millisecond {
		t.Fatalf("cancelled member returned %v after cancel", got.after)
	}
	other := <-peer
	if other.err != nil || other.result.Text != strings.Repeat("p", 40) {
		t.Fatalf("peer = %+v, %v", other.result, other.err)
	}
	mu.Lock()
	defer mu.Unlock()
	if lateEvents != 0 {
		t.Fatalf("cancelled member's sink ran %d times after Continue returned", lateEvents)
	}
}

func TestBatchStreamSinkErrorFailsOnlyThatMember(t *testing.T) {
	t.Parallel()
	server := batchServer(t, nil, func(r *http.Request, out sseWriter, index map[string]int) {
		out.choice(index["broken"], "a", "")
		out.choice(index["peer"], "b", "")
		time.Sleep(50 * time.Millisecond)
		out.choice(index["broken"], "a", "")
		out.choice(index["peer"], "b", "stop")
		out.raw("[DONE]")
	})
	defer server.Close()
	client := batchClient(t, server, true)
	errSink := errors.New("observer gave up")
	ctx, cancel := context.WithTimeout(t.Context(), 5*time.Second)
	defer cancel()
	var wg sync.WaitGroup
	var brokenErr, peerErr error
	var peerResult continuation.Result
	wg.Add(2)
	go func() {
		defer wg.Done()
		request := validRequest()
		request.Prompt = "broken"
		_, brokenErr = client.Continue(ctx, request, func(continuation.Event) error { return errSink })
	}()
	go func() {
		defer wg.Done()
		request := validRequest()
		request.Prompt = "peer"
		peerResult, peerErr = client.Continue(ctx, request, nil)
	}()
	wg.Wait()
	if !errors.Is(brokenErr, errSink) {
		t.Fatalf("broken member error = %v", brokenErr)
	}
	if peerErr != nil || peerResult.Text != "bb" || peerResult.FinishReason != continuation.FinishStop {
		t.Fatalf("peer = %+v, %v", peerResult, peerErr)
	}
}

// A stream error after one member already finished fails only the members
// still waiting; the delivered result stands.
func TestBatchStreamErrorAfterEarlyDeliveryKeepsDeliveredResult(t *testing.T) {
	t.Parallel()
	server := batchServer(t, nil, func(r *http.Request, out sseWriter, index map[string]int) {
		out.choice(index["short"], "hi", "stop")
		out.choice(index["long"], "partial", "")
		time.Sleep(50 * time.Millisecond)
		out.raw(`{"error":{"message":"cuda oom"}}`)
	})
	defer server.Close()
	results := runBatchedCalls(t, batchClient(t, server, true), []string{"short", "long"}, nil)
	if short := results["short"]; short.err != nil || short.result.Text != "hi" {
		t.Fatalf("short = %+v, %v", short.result, short.err)
	}
	if long := results["long"]; !errors.Is(long.err, ErrRemote) || !strings.Contains(long.err.Error(), "cuda oom") {
		t.Fatalf("long error = %v", long.err)
	}
}

func TestBatchMaxSplitsWideWindow(t *testing.T) {
	t.Parallel()
	widths := make(chan int, 16)
	server := batchServer(t, widths, func(r *http.Request, out sseWriter, index map[string]int) {
		for _, position := range index {
			out.choice(position, "ok", "stop")
		}
		out.raw("[DONE]")
	})
	defer server.Close()
	stream := true
	client, err := New(Config{
		Endpoint: server.URL, Model: "rwkv7", Stream: &stream,
		// A long window: only BatchMax can send these before it expires.
		BatchWait: 2 * time.Second, BatchMax: 2,
	})
	if err != nil {
		t.Fatal(err)
	}
	prompts := []string{"p0", "p1", "p2", "p3"}
	started := time.Now()
	results := runBatchedCalls(t, client, prompts, nil)
	if elapsed := time.Since(started); elapsed > time.Second {
		t.Fatalf("full windows waited %v for the timer", elapsed)
	}
	for _, prompt := range prompts {
		if results[prompt].err != nil || results[prompt].result.Text != "ok" {
			t.Fatalf("%s = %+v, %v", prompt, results[prompt].result, results[prompt].err)
		}
	}
	close(widths)
	total := 0
	for width := range widths {
		if width > 2 {
			t.Fatalf("request carried %d contents, cap is 2", width)
		}
		total += width
	}
	if total != len(prompts) {
		t.Fatalf("server saw %d contents, want %d", total, len(prompts))
	}
}

func TestBatchMaxSplitsOneGroupAtFlush(t *testing.T) {
	t.Parallel()
	widths := make(chan int, 16)
	server := batchServer(t, widths, func(r *http.Request, out sseWriter, index map[string]int) {
		for _, position := range index {
			out.choice(position, "ok", "stop")
		}
		out.raw("[DONE]")
	})
	defer server.Close()
	client := batchClient(t, server, true)
	client.batchMax = 2
	calls := make([]*pendingCall, 5)
	for index := range calls {
		request := validRequest()
		request.Prompt = fmt.Sprintf("p%d", index)
		calls[index] = &pendingCall{ctx: t.Context(), request: request, response: make(chan batchOutcome, 1)}
	}
	client.batchPending = calls
	client.flushBatch()
	for _, call := range calls {
		if outcome := <-call.response; outcome.err != nil || outcome.result.Text != "ok" {
			t.Fatalf("%s = %+v", call.request.Prompt, outcome)
		}
	}
	close(widths)
	var seen []int
	for width := range widths {
		seen = append(seen, width)
	}
	if len(seen) != 3 {
		t.Fatalf("request widths = %v, want three requests (2+2+1)", seen)
	}
}

func TestBatchCompatibilityKeyCoversAdapterAndState(t *testing.T) {
	t.Parallel()
	newClient := func(adapter, state string) *Client {
		client, err := New(Config{Endpoint: "http://127.0.0.1:1/v1/batch/completions", Model: "rwkv7", AdapterID: adapter, StateID: state})
		if err != nil {
			t.Fatal(err)
		}
		return client
	}
	request := validRequest()
	base := newClient("miss-a", "").batchCompatibilityKey(request)
	if base == newClient("miss-b", "").batchCompatibilityKey(request) {
		t.Fatal("different adapter_id share a batch key")
	}
	if base == newClient("miss-a", "state-1").batchCompatibilityKey(request) {
		t.Fatal("different state_id share a batch key")
	}
	overridden := request
	overridden.StateID = "state-2"
	if base == newClient("miss-a", "").batchCompatibilityKey(overridden) {
		t.Fatal("per-request state_id shares a batch key with the default state")
	}
	if base != newClient("miss-a", "").batchCompatibilityKey(request) {
		t.Fatal("identical settings produce different batch keys")
	}
}
