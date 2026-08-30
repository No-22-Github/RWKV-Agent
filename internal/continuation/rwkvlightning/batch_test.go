package rwkvlightning

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// Characterization tests for the batch coalescing path. client_test.go only
// covered the streaming happy path through this code; these lock the buffered
// transport, compatibility grouping, partial failure delivery, and the
// cancelled-call filter so the later single/batch reader unification cannot
// silently change them.

func batchClient(t *testing.T, server *httptest.Server, stream bool) *Client {
	t.Helper()
	client, err := New(Config{
		Endpoint:  server.URL,
		Model:     "rwkv7",
		BatchWait: 100 * time.Millisecond,
		Stream:    &stream,
	})
	if err != nil {
		t.Fatal(err)
	}
	return client
}

func runBatchedCalls(
	t *testing.T,
	client *Client,
	prompts []string,
	mutate func(index int, request *continuation.Request),
) map[string]batchCallResult {
	t.Helper()
	const batchTimeout = 5 * time.Second
	type job struct {
		prompt string
		index  int
	}
	jobs := make(chan job, len(prompts))
	for index, prompt := range prompts {
		jobs <- job{prompt: prompt, index: index}
	}
	close(jobs)
	start := make(chan struct{})
	results := make(chan batchCallResult, len(prompts))
	for range prompts {
		go func() {
			job := <-jobs
			<-start
			ctx, cancel := context.WithTimeout(context.Background(), batchTimeout)
			defer cancel()
			request := validRequest()
			request.Prompt = job.prompt
			if mutate != nil {
				mutate(job.index, &request)
			}
			var streamed strings.Builder
			result, callErr := client.Continue(ctx, request, func(event continuation.Event) error {
				streamed.WriteString(event.Text)
				return nil
			})
			results <- batchCallResult{
				prompt: job.prompt, result: result, err: callErr, streamed: streamed.String(),
			}
		}()
	}
	close(start)
	collected := make(map[string]batchCallResult, len(prompts))
	for range prompts {
		result := <-results
		collected[result.prompt] = result
	}
	return collected
}

type batchCallResult struct {
	prompt   string
	result   continuation.Result
	err      error
	streamed string
}

func TestClientBatchBufferedTransportDeliversPerChoiceResults(t *testing.T) {
	t.Parallel()
	var mu sync.Mutex
	requestCount := 0
	var received requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		mu.Lock()
		requestCount++
		mu.Unlock()
		body, err := io.ReadAll(request.Body)
		if err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &received); err != nil {
			t.Error(err)
		}
		choices := make([]string, 0, len(received.Contents))
		for index, content := range received.Contents {
			choices = append(choices, fmt.Sprintf(
				`{"index":%d,"message":{"content":%q},"finish_reason":"stop"}`,
				index,
				content+"-ok",
			))
		}
		writer.Header().Set("Content-Type", "application/json")
		_, _ = fmt.Fprintf(
			writer,
			`{"choices":[%s],"usage":{"prompt_tokens":7,"completion_tokens":3}}`,
			strings.Join(choices, ","),
		)
	}))
	defer server.Close()

	const count = 3
	prompts := make([]string, count)
	for index := range prompts {
		prompts[index] = fmt.Sprintf("prompt-%d", index)
	}
	results := runBatchedCalls(t, batchClient(t, server, false), prompts, nil)

	mu.Lock()
	if requestCount != 1 {
		t.Fatalf("requests = %d, want 1 coalesced request", requestCount)
	}
	mu.Unlock()
	if received.Stream {
		t.Fatal("buffered batch client requested stream=true")
	}
	if len(received.Contents) != count {
		t.Fatalf("contents = %v", received.Contents)
	}
	wantUsage := continuation.Usage{PromptTokens: 7, CompletionTokens: 3}
	for prompt, result := range results {
		if result.err != nil {
			t.Fatalf("call %q failed: %v", prompt, result.err)
		}
		wantText := prompt + "-ok"
		if result.result.Text != wantText || result.streamed != wantText {
			t.Fatalf("call %q text = %q streamed = %q", prompt, result.result.Text, result.streamed)
		}
		if result.result.FinishReason != continuation.FinishStop {
			t.Fatalf("call %q finish = %q", prompt, result.result.FinishReason)
		}
		if result.result.Usage != wantUsage {
			t.Fatalf("call %q usage = %+v", prompt, result.result.Usage)
		}
	}
}

func TestClientBatchBufferedAppliesStopsAndReportsMissingChoice(t *testing.T) {
	t.Run("consumed stop truncates per choice", func(t *testing.T) {
		t.Parallel()
		server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
			var received requestBody
			body, err := io.ReadAll(request.Body)
			if err != nil {
				t.Error(err)
			}
			if err := json.Unmarshal(body, &received); err != nil {
				t.Error(err)
			}
			writer.Header().Set("Content-Type", "application/json")
			_, _ = fmt.Fprint(writer,
				`{"choices":[`+
					`{"index":0,"message":{"content":"alpha\nUser: ignored"},"finish_reason":"length"},`+
					`{"index":1,"message":{"content":"beta"},"finish_reason":"stop"}]}`,
			)
		}))
		defer server.Close()

		results := runBatchedCalls(t, batchClient(t, server, false), []string{"p0", "p1"}, nil)
		if got := results["p0"].result; got.Text != "alpha" || got.FinishReason != continuation.FinishStop {
			t.Fatalf("p0 = %+v (want stop-truncated alpha)", got)
		}
		if got := results["p1"].result; got.Text != "beta" || got.FinishReason != continuation.FinishStop {
			t.Fatalf("p1 = %+v", got)
		}
	})

	t.Run("missing choice fails only that caller", func(t *testing.T) {
		t.Parallel()
		server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
			writer.Header().Set("Content-Type", "application/json")
			_, _ = io.WriteString(writer,
				`{"choices":[{"index":0,"message":{"content":"only-zero"},"finish_reason":"stop"}]}`)
		}))
		defer server.Close()

		results := runBatchedCalls(t, batchClient(t, server, false), []string{"p0", "p1"}, nil)
		if got := results["p0"]; got.err != nil || got.result.Text != "only-zero" {
			t.Fatalf("p0 = %+v err = %v", got.result, got.err)
		}
		got := results["p1"]
		if !errors.Is(got.err, ErrRemote) || !strings.Contains(got.err.Error(), "no choice for index 1") {
			t.Fatalf("p1 error = %v, want missing-choice remote error", got.err)
		}
	})
}

func TestClientBatchStreamErrorChunkFailsWholeBatch(t *testing.T) {
	t.Parallel()
	const password = "batch-secret"
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		writeSSE(writer, `{"error":{"message":"oom for batch-secret"}}`)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint:  server.URL,
		Model:     "rwkv7",
		Password:  password,
		BatchWait: 100 * time.Millisecond,
	})
	if err != nil {
		t.Fatal(err)
	}
	results := runBatchedCalls(t, client, []string{"p0", "p1"}, nil)
	for prompt, result := range results {
		if !errors.Is(result.err, ErrRemote) || !strings.Contains(result.err.Error(), "oom") {
			t.Fatalf("call %q error = %v, want stream remote error", prompt, result.err)
		}
		if strings.Contains(result.err.Error(), password) {
			t.Fatalf("call %q leaked the password: %v", prompt, result.err)
		}
	}
}

func TestClientBatchSeparatesIncompatibleSampling(t *testing.T) {
	t.Parallel()
	var mu sync.Mutex
	requestCount := 0
	contentsPerRequest := 0
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		var received requestBody
		body, err := io.ReadAll(request.Body)
		if err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &received); err != nil {
			t.Error(err)
		}
		mu.Lock()
		requestCount++
		contentsPerRequest = len(received.Contents)
		mu.Unlock()
		writeSSE(writer,
			`{"choices":[{"index":0,"delta":{"content":"ok"}}]}`,
			`{"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}`,
		)
	}))
	defer server.Close()

	client, err := New(Config{
		Endpoint:  server.URL,
		Model:     "rwkv7",
		BatchWait: 100 * time.Millisecond,
	})
	if err != nil {
		t.Fatal(err)
	}
	results := runBatchedCalls(t, client, []string{"p0", "p1"}, func(index int, request *continuation.Request) {
		request.Sampling.Temperature = 0.5 + float32(index)/10
	})
	for prompt, result := range results {
		if result.err != nil {
			t.Fatalf("call %q failed: %v", prompt, result.err)
		}
		if result.result.Text != "ok" {
			t.Fatalf("call %q text = %q", prompt, result.result.Text)
		}
	}
	mu.Lock()
	defer mu.Unlock()
	if requestCount != 2 || contentsPerRequest != 1 {
		t.Fatalf("requests = %d contents = %d, want two single-call requests", requestCount, contentsPerRequest)
	}
}

func TestClientBatchFiltersCancelledCallBeforeExecute(t *testing.T) {
	t.Parallel()
	var mu sync.Mutex
	var received requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		body, err := io.ReadAll(request.Body)
		if err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &received); err != nil {
			t.Error(err)
		}
		writeSSE(writer,
			`{"choices":[{"index":0,"delta":{"content":"survivor"}}]}`,
			`{"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}`,
		)
	}))
	defer server.Close()

	client, err := New(Config{
		Endpoint:  server.URL,
		Model:     "rwkv7",
		BatchWait: 250 * time.Millisecond,
	})
	if err != nil {
		t.Fatal(err)
	}
	cancelledCtx, cancel := context.WithCancel(context.Background())
	survivor := make(chan batchCallResult, 1)
	cancelled := make(chan batchCallResult, 1)
	go func() {
		request := validRequest()
		request.Prompt = "cancelled-prompt"
		result, callErr := client.Continue(cancelledCtx, request, nil)
		cancelled <- batchCallResult{result: result, err: callErr}
	}()
	go func() {
		request := validRequest()
		request.Prompt = "survivor-prompt"
		result, callErr := client.Continue(context.Background(), request, nil)
		survivor <- batchCallResult{result: result, err: callErr}
	}()
	// Cancel one caller while both are still queued in front of the flush timer.
	time.Sleep(50 * time.Millisecond)
	cancel()
	survivorResult := <-survivor
	if survivorResult.err != nil || survivorResult.result.Text != "survivor" {
		t.Fatalf("survivor = %+v err = %v", survivorResult.result, survivorResult.err)
	}
	if got := <-cancelled; !errors.Is(got.err, context.Canceled) {
		t.Fatalf("cancelled call error = %v, want context.Canceled", got.err)
	}
	mu.Lock()
	defer mu.Unlock()
	if len(received.Contents) != 1 || received.Contents[0] != "survivor-prompt" {
		t.Fatalf("contents = %v, want only the surviving call", received.Contents)
	}
}

func TestBatchRequestContextUsesEarliestDeadline(t *testing.T) {
	t.Parallel()
	soon := time.Now().Add(time.Minute)
	later := time.Now().Add(time.Hour)
	soonCtx, cancelSoon := context.WithDeadline(context.Background(), soon)
	defer cancelSoon()
	laterCtx, cancelLater := context.WithDeadline(context.Background(), later)
	defer cancelLater()
	ctx, cancel := batchRequestContext([]*pendingCall{
		{ctx: context.Background()},
		{ctx: laterCtx},
		{ctx: soonCtx},
	})
	defer cancel()
	deadline, ok := ctx.Deadline()
	if !ok {
		t.Fatal("expected a derived deadline")
	}
	if diff := deadline.Sub(soon); diff < -time.Second || diff > time.Second {
		t.Fatalf("deadline = %v, want the earliest caller deadline", deadline)
	}

	ctx, cancel = batchRequestContext([]*pendingCall{{ctx: context.Background()}})
	defer cancel()
	if _, ok := ctx.Deadline(); ok {
		t.Fatal("expected a plain cancellable context without caller deadlines")
	}
}
