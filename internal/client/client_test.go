package client

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestCompleteStreamsText(t *testing.T) {
	t.Parallel()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			t.Errorf("method = %s, want POST", r.Method)
		}
		if r.URL.Path != "/v1/completions" {
			t.Errorf("path = %s, want /v1/completions", r.URL.Path)
		}

		var request CompletionRequest
		if err := json.NewDecoder(r.Body).Decode(&request); err != nil {
			t.Fatalf("decode request: %v", err)
		}
		if !request.Stream {
			t.Error("stream = false, want true")
		}

		w.Header().Set("Content-Type", "text/event-stream")
		_, _ = w.Write([]byte("data: {\"choices\":[{\"text\":\"hello\"}]}\n\n"))
		_, _ = w.Write([]byte("data: {\"choices\":[{\"text\":\" world\"}]}\n\n"))
		_, _ = w.Write([]byte("data: [DONE]\n\n"))
	}))
	defer server.Close()

	var output strings.Builder
	err := Complete(context.Background(), server.URL, CompletionRequest{
		Prompt:    "test",
		MaxTokens: 8,
	}, func(text string) error {
		_, writeErr := output.WriteString(text)
		return writeErr
	})
	if err != nil {
		t.Fatalf("Complete: %v", err)
	}
	if got, want := output.String(), "hello world"; got != want {
		t.Fatalf("output = %q, want %q", got, want)
	}
}

func TestCompleteReportsRuntimeError(t *testing.T) {
	t.Parallel()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		http.Error(w, "model unavailable", http.StatusServiceUnavailable)
	}))
	defer server.Close()

	err := Complete(context.Background(), server.URL, CompletionRequest{}, func(string) error {
		return nil
	})
	if err == nil || !strings.Contains(err.Error(), "503 Service Unavailable: model unavailable") {
		t.Fatalf("error = %v, want runtime status and message", err)
	}
}

func TestHealthy(t *testing.T) {
	t.Parallel()

	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/health" {
			http.NotFound(w, r)
			return
		}
		w.WriteHeader(http.StatusOK)
	}))
	defer server.Close()

	if err := Healthy(context.Background(), server.URL+"/"); err != nil {
		t.Fatalf("Healthy: %v", err)
	}
}
