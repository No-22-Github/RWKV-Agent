package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"reflect"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestLightningTransportContracts(t *testing.T) {
	for _, kind := range []string{LightningPython, LightningCUDA} {
		for _, stream := range []bool{false, true} {
			t.Run(fmt.Sprintf("%s/stream=%v", kind, stream), func(t *testing.T) {
				request := continuation.Request{Prompt: "User: test\n\nAssistant:", MaxOutputTokens: 30, Stops: []string{"<END>"}, Sampling: continuation.Sampling{Temperature: 1, TopK: 10, TopP: 0.8, PenaltyDecay: 0.99}}
				server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					wantPath := "/prefix/v1/chat/completions"
					if kind == LightningCUDA {
						wantPath = "/prefix/v1/batch/completions"
					}
					if r.URL.Path != wantPath || r.URL.Query().Get("tenant") != "test" {
						t.Errorf("wrong endpoint %s", r.URL)
					}
					var body struct {
						Contents []string        `json:"contents"`
						Messages json.RawMessage `json:"messages"`
						Stops    json.RawMessage `json:"stop_tokens"`
						Password string          `json:"password"`
					}
					if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
						t.Error(err)
					}
					if !reflect.DeepEqual(body.Contents, []string{request.Prompt}) || body.Messages != nil {
						t.Errorf("prompt was not preserved: %+v", body)
					}
					wantStops := `["<END>"]`
					if kind == LightningCUDA {
						wantStops = `[0]`
					}
					var gotStops, expectedStops any
					_ = json.Unmarshal(body.Stops, &gotStops)
					_ = json.Unmarshal([]byte(wantStops), &expectedStops)
					if !reflect.DeepEqual(gotStops, expectedStops) || body.Password != "secret" {
						t.Errorf("wrong stops/auth: %s", body.Stops)
					}
					if stream {
						w.Header().Set("Content-Type", "text/event-stream")
						fmt.Fprint(w, "data: {\"choices\":[{\"index\":0,\"delta\":{\"content\":\"answer<END>ignored\"}}]}\n\ndata: [DONE]\n\n")
					} else {
						w.Header().Set("Content-Type", "application/json")
						fmt.Fprint(w, `{"choices":[{"index":0,"message":{"content":"answer<END>ignored"},"finish_reason":"stop"}]}`)
					}
				}))
				defer server.Close()
				generator, err := NewRemote(Config{Kind: kind, Endpoint: server.URL + "/prefix/v1/models?tenant=test", Model: "test", Credential: "secret", Stream: &stream})
				if err != nil {
					t.Fatal(err)
				}
				var deltas string
				result, err := generator.Continue(context.Background(), request, func(e continuation.Event) error { deltas += e.Text; return nil })
				if err != nil {
					t.Fatal(err)
				}
				if result.Text != "answer" || deltas != "answer" {
					t.Fatalf("result=%+v deltas=%q", result, deltas)
				}
			})
		}
	}
}

func TestRejectIncompatibleLightningOptions(t *testing.T) {
	for _, tc := range []struct {
		kind  string
		mode  string
		state string
	}{
		{LightningPython, "eos", ""},
		{LightningCUDA, "text", ""},
		{LightningPython, "", "uploaded.pth"},
	} {
		if _, err := NewRemote(Config{Kind: tc.kind, Endpoint: "https://example.test", StopTokens: tc.mode, StateID: tc.state}); err == nil {
			t.Fatalf("accepted incompatible options %+v", tc)
		}
	}
	generator, err := NewRemote(Config{Kind: LightningPython, Endpoint: "https://example.test"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := generator.Continue(context.Background(), continuation.Request{StateID: "uploaded.pth"}, nil); err == nil {
		t.Fatal("accepted per-request state")
	}
}

func TestEndpointNormalization(t *testing.T) {
	for _, suffix := range []string{"", "/", "/v1", "/v1/", "/v1/models", "/v1/chat/completions", "/v1/batch/completions"} {
		for _, kind := range []string{ChatCompletions, LightningPython, LightningCUDA} {
			route := "chat/completions"
			if kind == LightningCUDA {
				route = "batch/completions"
			}
			got := CompletionEndpoint(kind, "https://example.test/proxy"+suffix+"?tenant=x")
			if want := "https://example.test/proxy/v1/" + route + "?tenant=x"; got != want {
				t.Errorf("%s %s got %s want %s", kind, suffix, got, want)
			}
		}
	}
}

func TestOnlyExplicitBackendsAreAccepted(t *testing.T) {
	for _, kind := range []string{Local, ChatCompletions, LightningPython, LightningCUDA} {
		if !Valid(kind) {
			t.Fatalf("backend %q rejected", kind)
		}
	}
	for _, kind := range []string{"rwkv-lightning", "unknown", ""} {
		if Valid(kind) {
			t.Fatalf("obsolete or unknown backend %q accepted", kind)
		}
		if _, err := NewRemote(Config{Kind: kind, Endpoint: "https://example.test"}); err == nil {
			t.Fatalf("constructed unsupported backend %q", kind)
		}
	}
}
