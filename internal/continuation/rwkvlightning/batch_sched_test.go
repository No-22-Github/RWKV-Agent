package rwkvlightning

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// Scheduling and per-choice ending tests for the coalesced path: the in-flight
// cap, the hold that bounds it, the silence rule that releases EOS rows, and
// the local budget cut for members narrower than their request.

func sseLines(chunks ...string) string {
	var out strings.Builder
	for _, chunk := range chunks {
		fmt.Fprintf(&out, "data: %s\n\n", chunk)
	}
	return out.String()
}

func streamCalls(prompts ...continuation.Request) []*pendingCall {
	calls := make([]*pendingCall, len(prompts))
	for index, request := range prompts {
		calls[index] = &pendingCall{ctx: context.Background(), request: request, response: make(chan batchOutcome, 1)}
	}
	return calls
}

// An EOS row stops streaming while its peer keeps going; it is handed back
// after batchSilentSteps of the peer's steps, long before the request ends.
func TestBatchStreamSilentChoiceIsReleasedAsStop(t *testing.T) {
	t.Parallel()
	chunks := []string{
		`{"choices":[{"index":0,"delta":{"content":"short"}}]}`,
		`{"choices":[{"index":1,"delta":{"content":"a"}}]}`,
	}
	for range batchSilentSteps + 10 {
		chunks = append(chunks, `{"choices":[{"index":1,"delta":{"content":"a"}}]}`)
	}
	calls := streamCalls(validRequest(), validRequest())
	outcomes := readBatchStreamResponse(context.Background(),
		strings.NewReader(sseLines(chunks...)+"data: [DONE]\n\n"), calls, "", 321)
	if !outcomes[0].delivered {
		t.Fatal("silent choice was not released early")
	}
	early := <-calls[0].response
	if early.err != nil || early.result.Text != "short" || early.result.FinishReason != continuation.FinishStop {
		t.Fatalf("early outcome = %+v", early)
	}
	if outcomes[1].delivered || outcomes[1].result.FinishReason == continuation.FinishUnknown {
		t.Fatalf("streaming peer outcome = %+v", outcomes[1])
	}
}

// A row that has not streamed yet is never judged silent: a server may play
// choices one after another rather than step by step.
func TestBatchStreamUnstartedChoiceIsNotSilent(t *testing.T) {
	t.Parallel()
	var chunks []string
	for range batchSilentSteps * 2 {
		chunks = append(chunks, `{"choices":[{"index":0,"delta":{"content":"a"}}]}`)
	}
	chunks = append(chunks, `{"choices":[{"index":1,"delta":{"content":"late"}}]}`)
	calls := streamCalls(validRequest(), validRequest())
	outcomes := readBatchStreamResponse(context.Background(),
		strings.NewReader(sseLines(chunks...)+"data: [DONE]\n\n"), calls, "", 321)
	if outcomes[1].delivered || outcomes[1].result.Text != "late" {
		t.Fatalf("late choice = %+v", outcomes[1])
	}
}

// A member whose own budget is below the request's is cut locally at its
// budget and reported as a length stop.
func TestBatchStreamCutsNarrowMemberAtItsBudget(t *testing.T) {
	t.Parallel()
	narrow := validRequest()
	narrow.MaxOutputTokens = 3
	wide := validRequest()
	wide.MaxOutputTokens = 10
	var chunks []string
	for range 5 {
		chunks = append(chunks,
			`{"choices":[{"index":0,"delta":{"content":"n"}}]}`,
			`{"choices":[{"index":1,"delta":{"content":"w"}}]}`)
	}
	calls := streamCalls(narrow, wide)
	outcomes := readBatchStreamResponse(context.Background(),
		strings.NewReader(sseLines(chunks...)+"data: [DONE]\n\n"), calls, "", 10)
	if !outcomes[0].delivered {
		t.Fatal("narrow member ran past its budget")
	}
	cut := <-calls[0].response
	if cut.result.Text != "nnn" || cut.result.FinishReason != continuation.FinishLength {
		t.Fatalf("narrow outcome = %+v", cut.result)
	}
	if outcomes[1].result.Text != "wwwww" {
		t.Fatalf("wide outcome = %+v", outcomes[1].result)
	}
}

// Streamed calls that differ only in budget share one request sent with the
// widest budget.
func TestBatchStreamMergesBudgets(t *testing.T) {
	t.Parallel()
	bodies := make(chan requestBody, 4)
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		var body requestBody
		_ = json.NewDecoder(request.Body).Decode(&body)
		bodies <- body
		chunks := make([]string, 0, len(body.Contents))
		for index := range body.Contents {
			chunks = append(chunks, fmt.Sprintf(`{"choices":[{"index":%d,"delta":{"content":"ok"},"finish_reason":"stop"}]}`, index))
		}
		writeSSE(writer, chunks...)
	}))
	defer server.Close()
	client := batchClient(t, server, true)
	results := runBatchedCalls(t, client, []string{"p0", "p1"}, func(index int, request *continuation.Request) {
		request.MaxOutputTokens = 100 * (index + 1)
	})
	for prompt, result := range results {
		if result.err != nil {
			t.Fatalf("%s: %v", prompt, result.err)
		}
	}
	close(bodies)
	var got []requestBody
	for body := range bodies {
		got = append(got, body)
	}
	if len(got) != 1 || len(got[0].Contents) != 2 || got[0].MaxTokens != 200 {
		t.Fatalf("requests = %+v", got)
	}
}

// With one slot, calls that arrive while a request runs queue and leave
// together as one wider request when it finishes.
func TestBatchInflightCapQueuesBehindRunningRequest(t *testing.T) {
	t.Parallel()
	widths := make(chan int, 8)
	release := make(chan struct{})
	server := batchServer(t, widths, func(r *http.Request, out sseWriter, index map[string]int) {
		if _, first := index["first"]; first {
			<-release
		}
		for _, position := range index {
			out.choice(position, "ok", "stop")
		}
		out.raw("[DONE]")
	})
	defer server.Close()
	client, err := New(Config{
		Endpoint: server.URL, Model: "rwkv7", BatchWait: 5 * time.Millisecond,
		BatchInflight: 1, BatchHold: 10 * time.Second,
	})
	if err != nil {
		t.Fatal(err)
	}
	call := func(prompt string, done chan<- error) {
		request := validRequest()
		request.Prompt = prompt
		_, err := client.Continue(context.Background(), request, nil)
		done <- err
	}
	done := make(chan error, 4)
	go call("first", done)
	if got := <-widths; got != 1 {
		t.Fatalf("first width = %d", got)
	}
	for _, prompt := range []string{"a", "b", "c"} {
		go call(prompt, done)
	}
	select {
	case got := <-widths:
		t.Fatalf("a request of width %d left while the only slot was busy", got)
	case <-time.After(100 * time.Millisecond):
	}
	close(release)
	if got := <-widths; got != 3 {
		t.Fatalf("queued calls left as width %d, want one request of 3", got)
	}
	for range 4 {
		if err := <-done; err != nil {
			t.Fatal(err)
		}
	}
}

// The hold sends queued calls even while every slot stays busy.
func TestBatchHoldSendsQueuedCallsWhenSlotsStayBusy(t *testing.T) {
	t.Parallel()
	widths := make(chan int, 8)
	release := make(chan struct{})
	server := batchServer(t, widths, func(r *http.Request, out sseWriter, index map[string]int) {
		if _, first := index["first"]; first {
			select {
			case <-release:
			case <-r.Context().Done():
				return
			}
		}
		for _, position := range index {
			out.choice(position, "ok", "stop")
		}
		out.raw("[DONE]")
	})
	defer server.Close()
	defer close(release)
	client, err := New(Config{
		Endpoint: server.URL, Model: "rwkv7", BatchWait: 5 * time.Millisecond,
		BatchInflight: 1, BatchHold: 150 * time.Millisecond,
	})
	if err != nil {
		t.Fatal(err)
	}
	go func() {
		request := validRequest()
		request.Prompt = "first"
		_, _ = client.Continue(context.Background(), request, nil)
	}()
	<-widths
	started := time.Now()
	request := validRequest()
	request.Prompt = "queued"
	if _, err := client.Continue(context.Background(), request, nil); err != nil {
		t.Fatal(err)
	}
	if waited := time.Since(started); waited < 100*time.Millisecond || waited > 2*time.Second {
		t.Fatalf("queued call waited %v, want about the 150ms hold", waited)
	}
}

// A looping member is handed back as a length finish while its peer keeps
// streaming; the text it gets stops where the guard tripped.
func TestBatchStreamLoopGuardReleasesLoopingMember(t *testing.T) {
	t.Parallel()
	var chunks []string
	for index := range 400 {
		chunks = append(chunks,
			`{"choices":[{"index":0,"delta":{"content":"again and "}}]}`,
			fmt.Sprintf(`{"choices":[{"index":1,"delta":{"content":"word%d "}}]}`, index))
	}
	request := validRequest()
	request.MaxOutputTokens = 4096
	calls := streamCalls(request, request)
	for _, call := range calls {
		call.guard = continuation.NewLoopGuard()
	}
	outcomes := readBatchStreamResponse(context.Background(),
		strings.NewReader(sseLines(chunks...)+"data: [DONE]\n\n"), calls, "", 4096)
	if !outcomes[0].delivered {
		t.Fatal("looping member was not released early")
	}
	cut := <-calls[0].response
	if cut.result.FinishReason != continuation.FinishLength || len(cut.result.Text) >= 4000 {
		t.Fatalf("looping outcome = %q (%s)", cut.result.Text[:40], cut.result.FinishReason)
	}
	if outcomes[1].delivered || !strings.HasSuffix(outcomes[1].result.Text, "word399 ") {
		t.Fatalf("clean peer outcome = %+v", outcomes[1].result.FinishReason)
	}
}
