package irwkv

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

func request() continuation.Request {
	return continuation.Request{
		Prompt:          "User: hi\n\nAssistant:",
		MaxOutputTokens: 64,
		Stops:           []string{"\n\nUser:", "</tool_call>"},
		Sampling: continuation.Sampling{
			Temperature: 1, TopK: 20, TopP: 0.3,
			PresencePenalty: 0.5, FrequencyPenalty: 0.1, PenaltyDecay: 0.996,
		},
	}
}

func serve(t *testing.T, handler func(map[string]any) string) (*httptest.Server, *map[string]any) {
	t.Helper()
	got := map[string]any{}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/completions" {
			t.Errorf("path = %s", r.URL.Path)
		}
		body, _ := io.ReadAll(r.Body)
		if err := json.Unmarshal(body, &got); err != nil {
			t.Errorf("decode body: %v", err)
		}
		_, _ = io.WriteString(w, handler(got))
	}))
	t.Cleanup(server.Close)
	return server, &got
}

func sse(chunks ...string) string {
	var out strings.Builder
	for _, chunk := range chunks {
		fmt.Fprintf(&out, "data: %s\n\n", chunk)
	}
	out.WriteString("data: [DONE]\n\n")
	return out.String()
}

func TestRequestBodyMapsRWKVSampling(t *testing.T) {
	server, got := serve(t, func(map[string]any) string {
		return sse(`{"choices":[{"index":0,"text":"ok","finish_reason":"stop","stop_reason":null}]}`)
	})
	client, err := New(Config{
		Endpoint: server.URL + "/v1/completions", Model: "rwkv-7.2b",
		ForwardStops: true, StopTokenIDs: []int{0, userTokenID},
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Continue(context.Background(), request(), nil); err != nil {
		t.Fatal(err)
	}
	body := *got
	if body["add_special_tokens"] != false {
		t.Fatalf("add_special_tokens = %v, want false", body["add_special_tokens"])
	}
	if ids := fmt.Sprint(body["stop_token_ids"]); ids != "[0]" {
		t.Fatalf("stop_token_ids = %s, want the bare User id dropped", ids)
	}
	if stops := fmt.Sprint(body["stop"]); stops != "[\n\nUser: </tool_call>]" {
		t.Fatalf("stop = %q", stops)
	}
	for key, want := range map[string]float64{
		"top_k": 20, "presence_penalty": 0.5, "penalty_decay": 0.996, "max_tokens": 64,
	} {
		if value, _ := body[key].(float64); float32(value) != float32(want) {
			t.Errorf("%s = %v, want %v", key, body[key], want)
		}
	}
	if body["stream"] != true || body["stream_options"] == nil {
		t.Fatalf("stream settings = %v %v", body["stream"], body["stream_options"])
	}
}

func TestStreamReportsServerStopAndUsage(t *testing.T) {
	server, _ := serve(t, func(map[string]any) string {
		return sse(
			`{"choices":[{"index":0,"text":"<tool_call>{\"name\":","finish_reason":null}]}`,
			`{"choices":[{"index":0,"text":"\"x\"}","finish_reason":"stop","stop_reason":"</tool_call>"}]}`,
			`{"choices":[],"usage":{"prompt_tokens":9,"completion_tokens":7}}`,
		)
	})
	client, _ := New(Config{Endpoint: server.URL + "/v1/completions", Model: "m", ForwardStops: true})
	var streamed strings.Builder
	result, err := client.Continue(context.Background(), request(), func(event continuation.Event) error {
		streamed.WriteString(event.Text)
		return nil
	})
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != `<tool_call>{"name":"x"}` || streamed.String() != result.Text {
		t.Fatalf("text = %q streamed %q", result.Text, streamed.String())
	}
	if result.FinishReason != continuation.FinishStop || result.Stop != "</tool_call>" {
		t.Fatalf("finish = %s stop = %q", result.FinishReason, result.Stop)
	}
	if result.Usage.CompletionTokens != 7 || result.Usage.CompletionSource != continuation.UsageSourceServer {
		t.Fatalf("usage = %+v", result.Usage)
	}
}

func TestStreamCutsClientSideStop(t *testing.T) {
	server, _ := serve(t, func(map[string]any) string {
		return sse(
			`{"choices":[{"index":0,"text":"done\n\nUs","finish_reason":null}]}`,
			`{"choices":[{"index":0,"text":"er: more","finish_reason":null}]}`,
		)
	})
	client, _ := New(Config{Endpoint: server.URL + "/v1/completions", Model: "m"})
	result, err := client.Continue(context.Background(), request(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != "done" || result.Stop != "\n\nUser:" || result.FinishReason != continuation.FinishStop {
		t.Fatalf("result = %+v", result)
	}
}

func TestBufferedLengthFinish(t *testing.T) {
	server, got := serve(t, func(map[string]any) string {
		return `{"choices":[{"index":0,"text":"abc","finish_reason":"length"}],"usage":{"prompt_tokens":3,"completion_tokens":64}}`
	})
	stream := false
	client, _ := New(Config{Endpoint: server.URL + "/v1/completions", Model: "m", Stream: &stream})
	result, err := client.Continue(context.Background(), request(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != "abc" || result.FinishReason != continuation.FinishLength {
		t.Fatalf("result = %+v", result)
	}
	if (*got)["stop"] != nil || (*got)["stream_options"] != nil {
		t.Fatalf("unexpected fields: %v", *got)
	}
}

func TestErrorsAreUpstream(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusBadRequest)
		_, _ = io.WriteString(w, `{"object":"error","message":"too long"}`)
	}))
	defer server.Close()
	client, _ := New(Config{Endpoint: server.URL + "/v1/completions", Model: "m"})
	_, err := client.Continue(context.Background(), request(), nil)
	if !errors.Is(err, continuation.ErrUpstream) || !strings.Contains(err.Error(), "HTTP 400") {
		t.Fatalf("err = %v", err)
	}
}

func TestRejectsUploadedState(t *testing.T) {
	client, _ := New(Config{Endpoint: "http://127.0.0.1:1/v1", Model: "m"})
	req := request()
	req.StateID = "state-1"
	if _, err := client.Continue(context.Background(), req, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("err = %v", err)
	}
}
