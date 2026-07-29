package rwkvlightning

import (
	"context"
	"encoding/json"
	"errors"
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
		if err := json.NewDecoder(request.Body).Decode(&received); err != nil {
			t.Error(err)
		}
		_, _ = writer.Write([]byte(`{
			"choices":[
				{"index":0,"message":{"role":"assistant","content":"{\"type\":\"final\",\"content\":\"done\"}"},"finish_reason":"stop"}
			]
		}`))
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
		delta != result.Text {
		t.Fatalf("result = %+v, delta = %q", result, delta)
	}
	if received.Model != "rwkv7-13b" ||
		len(received.Contents) != 1 ||
		received.Contents[0] != validRequest().Prompt ||
		received.StopTokens == nil ||
		received.MaxTokens != 321 ||
		received.TopK != 12 ||
		received.Password != "secret" ||
		received.Stream {
		t.Fatalf("request = %+v", received)
	}
	if accessID != "client-id" || accessSecret != "client-secret" {
		t.Fatalf("access headers = %q, %q", accessID, accessSecret)
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
		_, _ = writer.Write([]byte(`{"choices":[]}`))
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

type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(request *http.Request) (*http.Response, error) {
	return f(request)
}

var _ http.RoundTripper = roundTripFunc(nil)
