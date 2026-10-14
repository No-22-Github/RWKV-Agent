package rwkvlightning

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// The cuda deployment streams no usage block; with chunk_size=1 every content
// delta is one generated token, so the completion count comes from the stream
// and says so.
func TestClientCountsCompletionTokensFromStreamChunks(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writeSSE(
			writer,
			`{"choices":[{"index":0,"delta":{"content":"a"}}]}`,
			`{"choices":[{"index":0,"delta":{"content":""}}]}`,
			`{"choices":[{"index":0,"delta":{"content":"b"}}]}`,
			`{"choices":[{"index":0,"delta":{"content":"</tool_call>"}}]}`,
		)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	request := validRequest()
	request.Stops = []string{"</tool_call>"}
	result, err := client.Continue(context.Background(), request, nil)
	if err != nil {
		t.Fatal(err)
	}
	want := continuation.Usage{
		CompletionTokens: 3,
		CompletionSource: continuation.UsageSourceServerStream,
	}
	if result.Usage != want {
		t.Fatalf("usage = %+v, want %+v", result.Usage, want)
	}
}

func TestClientKeepsServerReportedUsage(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writeSSE(
			writer,
			`{"choices":[{"index":0,"delta":{"content":"a"}}]}`,
			`{"choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":11,"completion_tokens":5}}`,
		)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	result, err := client.Continue(context.Background(), validRequest(), nil)
	if err != nil {
		t.Fatal(err)
	}
	want := continuation.Usage{
		PromptTokens: 11, CompletionTokens: 5,
		PromptSource:     continuation.UsageSourceServer,
		CompletionSource: continuation.UsageSourceServer,
	}
	if result.Usage != want {
		t.Fatalf("usage = %+v, want %+v", result.Usage, want)
	}
	if result.Usage.ReportedCompletionTokens() != 5 {
		t.Fatalf("reported completion = %d", result.Usage.ReportedCompletionTokens())
	}
}

// Each coalesced call counts its own choice's chunks, not the batch's.
func TestClientBatchCountsCompletionTokensPerChoice(t *testing.T) {
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
		var chunks []string
		for index := range received.Contents {
			// Choice i streams i+1 one-character tokens.
			for range index + 1 {
				chunks = append(chunks, fmt.Sprintf(
					`{"choices":[{"index":%d,"delta":{"content":"x"}}]}`, index))
			}
			chunks = append(chunks, fmt.Sprintf(
				`{"choices":[{"index":%d,"delta":{},"finish_reason":"stop"}]}`, index))
		}
		writeSSE(writer, chunks...)
	}))
	defer server.Close()
	prompts := []string{"p0", "p1", "p2"}
	results := runBatchedCalls(t, batchClient(t, server, true), prompts, nil)
	seen := map[int]bool{}
	for prompt, result := range results {
		if result.err != nil {
			t.Fatalf("call %q failed: %v", prompt, result.err)
		}
		usage := result.result.Usage
		if usage.CompletionSource != continuation.UsageSourceServerStream ||
			usage.CompletionTokens != len(result.result.Text) {
			t.Fatalf("call %q usage = %+v text %q", prompt, usage, result.result.Text)
		}
		if usage.ReportedCompletionTokens() != 0 {
			t.Fatalf("a stream count must not read as a server report: %+v", usage)
		}
		seen[usage.CompletionTokens] = true
	}
	if len(seen) != len(prompts) {
		t.Fatalf("per-choice counts = %v, want one distinct count per call", seen)
	}
}
