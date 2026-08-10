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
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func validRequest() continuation.Request {
	return continuation.Request{
		Prompt:          "User: inspect the repository\n\nAssistant:",
		MaxOutputTokens: 321,
		Stops:           []string{"\nUser:"},
		Sampling: continuation.Sampling{
			Temperature:      0.8,
			TopK:             12,
			TopP:             0.7,
			PresencePenalty:  1.2,
			FrequencyPenalty: 0.2,
			PenaltyDecay:     0.996,
		},
	}
}

func TestClientMapsContinuationRequestAndResponse(t *testing.T) {
	t.Parallel()
	var received requestBody
	var receivedFields map[string]json.RawMessage
	var accessID string
	var accessSecret string
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost {
			t.Errorf("method = %s", request.Method)
		}
		if request.Header.Get("Content-Type") != "application/json" {
			t.Errorf("content type = %q", request.Header.Get("Content-Type"))
		}
		accessID = request.Header.Get("CF-Access-Client-Id")
		accessSecret = request.Header.Get("CF-Access-Client-Secret")
		body, err := io.ReadAll(request.Body)
		if err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &received); err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &receivedFields); err != nil {
			t.Error(err)
		}
		writeSSE(
			writer,
			`{"choices":[{"index":0,"delta":{"content":"{\"type\":\"final\",\"content\":\"done\"}"}}],"usage":{"prompt_tokens":12,"completion_tokens":4}}`,
			`{"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}`,
		)
	}))
	defer server.Close()

	client, err := New(Config{
		Endpoint: server.URL + "/v1/chat/completions",
		Model:    "rwkv7-13b",
		Password: "secret",
		Headers: http.Header{
			"CF-Access-Client-Id":     []string{"client-id"},
			"CF-Access-Client-Secret": []string{"client-secret"},
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	var delta string
	requestValue := validRequest()
	requestValue.Stops = nil
	result, err := client.Continue(
		context.Background(),
		requestValue,
		func(event continuation.Event) error {
			delta += event.Text
			return nil
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != `{"type":"final","content":"done"}` ||
		result.FinishReason != continuation.FinishStop ||
		result.Usage.PromptTokens != 12 ||
		result.Usage.CompletionTokens != 4 ||
		delta != result.Text {
		t.Fatalf("result = %+v, delta = %q", result, delta)
	}
	if received.Model != "rwkv7-13b" ||
		len(received.Contents) != 1 ||
		received.Contents[0] != validRequest().Prompt ||
		received.MaxTokens != 321 ||
		received.TopK != 12 ||
		received.Password != "secret" ||
		!received.Stream ||
		received.ChunkSize != 1 {
		t.Fatalf("request = %+v", received)
	}
	if _, exists := receivedFields["stop_tokens"]; exists {
		t.Fatal("request sent stop_tokens for a continuation with no stop sequences")
	}
	if accessID != "client-id" || accessSecret != "client-secret" {
		t.Fatalf("access headers = %q, %q", accessID, accessSecret)
	}
}

func TestClientStopTokensAreConfigurable(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		name     string
		mode     StopTokenMode
		tokenIDs []int
		want     string
	}{
		{name: "default forwards text stops", want: `["\nUser:"]`},
		{name: "explicit text mode", mode: StopTokenText, want: `["\nUser:"]`},
		{name: "omitted", mode: StopTokenNone, want: ""},
		{name: "legacy EOS", mode: StopTokenEOS, want: "[0]"},
		{name: "explicit ID list", mode: StopTokenEOS, tokenIDs: []int{0, 261}, want: "[0,261]"},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			var received requestBody
			var receivedFields map[string]json.RawMessage
			server := httptest.NewServer(
				http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
					body, err := io.ReadAll(request.Body)
					if err != nil {
						t.Error(err)
					}
					if err := json.Unmarshal(body, &received); err != nil {
						t.Error(err)
					}
					if err := json.Unmarshal(body, &receivedFields); err != nil {
						t.Error(err)
					}
					writeSSE(
						writer,
						`{"choices":[{"index":0,"delta":{"content":"ok"}}]}`,
						`{"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}`,
					)
				}),
			)
			defer server.Close()
			client, err := New(Config{
				Endpoint:      server.URL,
				Model:         "rwkv7-13b",
				StopTokenMode: testCase.mode,
				StopTokenIDs:  testCase.tokenIDs,
			})
			if err != nil {
				t.Fatal(err)
			}
			if _, err := client.Continue(context.Background(), validRequest(), nil); err != nil {
				t.Fatal(err)
			}
			stopTokens, exists := receivedFields["stop_tokens"]
			if exists != (testCase.want != "") {
				t.Fatalf("stop_tokens present = %v, want %v", exists, testCase.want != "")
			}
			if exists && string(stopTokens) != testCase.want {
				t.Fatalf("stop_tokens = %s, want %s", stopTokens, testCase.want)
			}
		})
	}
}

func TestClientRejectsUnknownStopTokenMode(t *testing.T) {
	t.Parallel()
	if _, err := New(Config{
		Endpoint:      "https://example.test/v1/chat/completions",
		Model:         "rwkv7-13b",
		StopTokenMode: StopTokenMode("token-ids"),
	}); err == nil {
		t.Fatal("New accepted an unknown stop token mode")
	}
}

func TestInferFinishReasonRecoversLengthWithoutFinishReason(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		name   string
		finish continuation.FinishReason
		usage  continuation.Usage
		deltas int
		maxTok int
		want   continuation.FinishReason
	}{
		{
			name:   "budget exhausted by delta count",
			finish: continuation.FinishUnknown,
			deltas: 64,
			maxTok: 64,
			want:   continuation.FinishLength,
		},
		{
			name:   "budget exhausted by reported usage",
			finish: continuation.FinishUnknown,
			usage:  continuation.Usage{CompletionTokens: 64},
			deltas: 3,
			maxTok: 64,
			want:   continuation.FinishLength,
		},
		{
			name:   "server stopped short of the budget",
			finish: continuation.FinishUnknown,
			deltas: 12,
			maxTok: 64,
			want:   continuation.FinishStop,
		},
		{
			name:   "explicit finish reason is preserved",
			finish: continuation.FinishStop,
			deltas: 64,
			maxTok: 64,
			want:   continuation.FinishStop,
		},
		{
			name:   "no budget still reports a normal stop",
			finish: continuation.FinishUnknown,
			deltas: 64,
			maxTok: 0,
			want:   continuation.FinishStop,
		},
		{
			name:   "empty stream stays unknown",
			finish: continuation.FinishUnknown,
			deltas: 0,
			maxTok: 64,
			want:   continuation.FinishUnknown,
		},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			got := inferFinishReason(
				testCase.finish,
				testCase.usage,
				testCase.deltas,
				testCase.maxTok,
			)
			if got != testCase.want {
				t.Fatalf("finish reason = %q, want %q", got, testCase.want)
			}
		})
	}
}

func TestClientReportsLengthFinishForTruncatedStream(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(
		http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
			writeSSE(
				writer,
				`{"choices":[{"index":0,"delta":{"content":"a"}}]}`,
				`{"choices":[{"index":0,"delta":{"content":"b"}}]}`,
				`{"choices":[{"index":0,"delta":{"content":"c"}}]}`,
			)
		}),
	)
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7-13b"})
	if err != nil {
		t.Fatal(err)
	}
	request := validRequest()
	request.MaxOutputTokens = 3
	result, err := client.Continue(context.Background(), request, nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.FinishReason != continuation.FinishLength {
		t.Fatalf("finish reason = %q, want %q", result.FinishReason, continuation.FinishLength)
	}
	if result.Text != "abc" {
		t.Fatalf("text = %q", result.Text)
	}
}

// TestClientReportsStopWhenServerConsumesStopSequence covers the regression that
// produced 0/18 in runs/v9-rwkv13b-think-boundary. With server-side stops enabled
// the server halts on the stop sequence and never echoes it, so a correct route
// arrives as a bare "inspect" with no finish_reason. Reporting FinishUnknown made
// the protocol reject it as an incomplete envelope; it must be FinishStop.
func TestClientReportsStopWhenServerConsumesStopSequence(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(
		http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
			writeSSE(writer, `{"choices":[{"index":0,"delta":{"content":"inspect"}}]}`)
		}),
	)
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7-13b"})
	if err != nil {
		t.Fatal(err)
	}
	request := validRequest()
	request.MaxOutputTokens = 512
	request.Stops = []string{"</route>", "\nUser:"}
	result, err := client.Continue(context.Background(), request, nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.FinishReason != continuation.FinishStop {
		t.Fatalf("finish reason = %q, want %q", result.FinishReason, continuation.FinishStop)
	}
	if result.Text != "inspect" {
		t.Fatalf("text = %q", result.Text)
	}
}

// TestClientBufferedTransport covers stream=false, added because this
// deployment's SSE path degrades to HTTP 200 with an empty body under load. The
// buffered shape carries a real finish_reason, so nothing has to be inferred.
func TestClientBufferedTransport(t *testing.T) {
	t.Parallel()
	var received requestBody
	server := httptest.NewServer(
		http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
			body, err := io.ReadAll(request.Body)
			if err != nil {
				t.Error(err)
			}
			if err := json.Unmarshal(body, &received); err != nil {
				t.Error(err)
			}
			writer.Header().Set("Content-Type", "application/json")
			_, _ = writer.Write([]byte(
				`{"id":"rwkv7-batch","object":"chat.completion","choices":` +
					`[{"index":0,"message":{"role":"assistant","content":"inspect"},` +
					`"finish_reason":"stop"}],` +
					`"usage":{"prompt_tokens":31,"completion_tokens":2}}`,
			))
		}),
	)
	defer server.Close()
	buffered := false
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7-13b", Stream: &buffered})
	if err != nil {
		t.Fatal(err)
	}
	var streamed string
	result, err := client.Continue(
		context.Background(),
		validRequest(),
		func(event continuation.Event) error {
			streamed += event.Text
			return nil
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if received.Stream {
		t.Fatal("buffered client requested stream=true")
	}
	if result.Text != "inspect" || streamed != "inspect" {
		t.Fatalf("text = %q, streamed = %q", result.Text, streamed)
	}
	if result.FinishReason != continuation.FinishStop {
		t.Fatalf("finish reason = %q", result.FinishReason)
	}
	if result.Usage.CompletionTokens != 2 || result.Usage.PromptTokens != 31 {
		t.Fatalf("usage = %+v", result.Usage)
	}
}

func TestClientBufferedTransportAppliesStopsAndErrors(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		name     string
		body     string
		wantText string
		wantErr  bool
	}{
		{
			name: "decoded-text stop truncates the full body",
			body: `{"choices":[{"index":0,"message":{"content":"done\nUser: next"},` +
				`"finish_reason":"length"}]}`,
			wantText: "done",
		},
		{
			name:    "error field surfaces as a remote failure",
			body:    `{"error":{"message":"model unavailable"}}`,
			wantErr: true,
		},
		{
			name:    "missing choices is a remote failure",
			body:    `{"choices":[]}`,
			wantErr: true,
		},
		{
			name:    "malformed JSON is a remote failure",
			body:    `not json`,
			wantErr: true,
		},
	} {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			server := httptest.NewServer(
				http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
					_, _ = writer.Write([]byte(testCase.body))
				}),
			)
			defer server.Close()
			buffered := false
			client, err := New(Config{
				Endpoint: server.URL,
				Model:    "rwkv7-13b",
				Stream:   &buffered,
			})
			if err != nil {
				t.Fatal(err)
			}
			result, err := client.Continue(context.Background(), validRequest(), nil)
			if testCase.wantErr {
				if err == nil {
					t.Fatalf("expected a remote error, got %+v", result)
				}
				if !errors.Is(err, ErrRemote) {
					t.Fatalf("error %v does not wrap ErrRemote", err)
				}
				return
			}
			if err != nil {
				t.Fatal(err)
			}
			if result.Text != testCase.wantText {
				t.Fatalf("text = %q, want %q", result.Text, testCase.wantText)
			}
			// A consumed stop wins over the server's own finish_reason.
			if result.FinishReason != continuation.FinishStop {
				t.Fatalf("finish reason = %q", result.FinishReason)
			}
		})
	}
}

func TestClientAppliesDecodedTextStops(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writeSSE(
			writer,
			`{"choices":[{"index":0,"delta":{"content":"answer\nTo"}}]}`,
			`{"choices":[{"index":0,"delta":{"content":"ol: ignored"}}]}`,
		)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	request := validRequest()
	request.Stops = []string{"\nUser:", "\nTool:"}
	var delta string
	result, err := client.Continue(
		context.Background(),
		request,
		func(event continuation.Event) error {
			delta += event.Text
			return nil
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != "answer" || delta != "answer" {
		t.Fatalf("result = %+v, delta = %q", result, delta)
	}
}

func TestClientReportsRemoteErrorsWithoutLeakingPassword(t *testing.T) {
	t.Parallel()
	const password = "do-not-log-this"
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		http.Error(writer, `authentication failed for do-not-log-this`, http.StatusUnauthorized)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7", Password: password})
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.Continue(context.Background(), validRequest(), nil)
	if !errors.Is(err, ErrRemote) || !strings.Contains(err.Error(), "HTTP 401") {
		t.Fatalf("error = %v", err)
	}
	if strings.Contains(err.Error(), password) {
		t.Fatalf("password leaked in error: %v", err)
	}
}

func TestClientCancellationStopsRequest(t *testing.T) {
	t.Parallel()
	started := make(chan struct{})
	httpClient := &http.Client{Transport: roundTripFunc(func(
		request *http.Request,
	) (*http.Response, error) {
		close(started)
		<-request.Context().Done()
		return nil, request.Context().Err()
	})}
	client, err := New(Config{
		Endpoint:   "https://example.test/v1/chat/completions",
		Model:      "rwkv7",
		HTTPClient: httpClient,
	})
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() {
		_, callErr := client.Continue(ctx, validRequest(), nil)
		done <- callErr
	}()
	<-started
	cancel()
	if err := <-done; !errors.Is(err, context.Canceled) {
		t.Fatalf("error = %v, want context.Canceled", err)
	}
}

func TestClientRejectsMalformedResponse(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		writeSSE(writer, `{"choices":[]}`)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Continue(context.Background(), validRequest(), nil); !errors.Is(err, ErrRemote) {
		t.Fatalf("error = %v, want ErrRemote", err)
	}
}

func writeSSE(writer http.ResponseWriter, chunks ...string) {
	writer.Header().Set("Content-Type", "text/event-stream")
	for _, chunk := range chunks {
		_, _ = fmt.Fprintf(writer, "data: %s\n\n", chunk)
	}
	_, _ = fmt.Fprint(writer, "data: [DONE]\n\n")
}

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(request *http.Request) (*http.Response, error) {
	return f(request)
}

var _ http.RoundTripper = roundTripFunc(nil)
