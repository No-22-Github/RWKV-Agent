package rwkvlightning

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestStateEndpointDerivation(t *testing.T) {
	t.Parallel()
	testCases := []struct {
		endpoint string
		suffix   string
		want     string
	}{
		{"https://host/v1/batch/completions", "/state/upload", "https://host/v1/state/upload"},
		{"https://host/v1/chat/completions", "/state/list", "https://host/v1/state/list"},
		{"https://host/v1/models", "/state/upload", "https://host/v1/state/upload"},
		{"https://host/batch/completions", "/state/delete", "https://host/v1/state/delete"},
		{"https://host/chat/completions", "/state/upload", "https://host/v1/state/upload"},
		{"https://host/v1", "/state/list", "https://host/v1/state/list"},
		{"https://host", "/state/upload", "https://host/v1/state/upload"},
	}
	for _, testCase := range testCases {
		client, err := New(Config{Endpoint: testCase.endpoint, Model: "rwkv7"})
		if err != nil {
			t.Fatalf("New(%q): %v", testCase.endpoint, err)
		}
		if got := client.stateEndpoint(testCase.suffix); got != testCase.want {
			t.Errorf("stateEndpoint(%q) with endpoint %q = %q, want %q", testCase.suffix, testCase.endpoint, got, testCase.want)
		}
	}
}

func TestUploadState(t *testing.T) {
	t.Parallel()
	var receivedPath string
	var accessID, accessSecret string
	var contentType string
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost {
			t.Errorf("method = %s, want POST", request.Method)
		}
		if request.URL.Path != "/v1/state/upload" {
			t.Errorf("path = %s, want /v1/state/upload", request.URL.Path)
		}
		accessID = request.Header.Get("CF-Access-Client-Id")
		accessSecret = request.Header.Get("CF-Access-Client-Secret")
		contentType = request.Header.Get("Content-Type")
		if err := request.ParseMultipartForm(4 * 1024 * 1024); err != nil {
			t.Errorf("parse multipart form: %v", err)
		}
		file, header, err := request.FormFile("file")
		if err != nil {
			t.Errorf("form file: %v", err)
			return
		}
		defer file.Close()
		payload, err := io.ReadAll(file)
		if err != nil {
			t.Error(err)
		}
		if header.Filename != "state-1.pth" {
			t.Errorf("form filename = %q, want state-1.pth", header.Filename)
		}
		if string(payload) != "state-bytes" {
			t.Errorf("form file contents = %q", payload)
		}
		receivedPath = header.Filename
		writer.Header().Set("Content-Type", "application/json")
		_, _ = writer.Write([]byte(`{"object":"rwkv.state","state_id":"state-abc123","filename":"state-1.pth","size_bytes":11,"tensor_count":32,"created":1788855449}`))
	}))
	defer server.Close()

	statePath := filepath.Join(t.TempDir(), "state-1.pth")
	if err := os.WriteFile(statePath, []byte("state-bytes"), 0o600); err != nil {
		t.Fatal(err)
	}
	client, err := New(Config{
		Endpoint: server.URL + "/v1/batch/completions",
		Model:    "rwkv7",
		Headers: http.Header{
			"CF-Access-Client-Id":     []string{"client-id"},
			"CF-Access-Client-Secret": []string{"client-secret"},
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	state, err := client.UploadState(context.Background(), statePath)
	if err != nil {
		t.Fatal(err)
	}
	if state.StateID != "state-abc123" {
		t.Errorf("state_id = %q, want state-abc123", state.StateID)
	}
	if state.SizeBytes != 11 || state.TensorCount != 32 {
		t.Errorf("state = %+v", state)
	}
	if receivedPath != "state-1.pth" {
		t.Errorf("received filename = %q", receivedPath)
	}
	if accessID != "client-id" || accessSecret != "client-secret" {
		t.Errorf("deployment headers not forwarded: id=%q secret=%q", accessID, accessSecret)
	}
	if !strings.HasPrefix(contentType, "multipart/form-data; boundary=") {
		t.Errorf("content type = %q, want multipart form", contentType)
	}
}

func TestUploadStateMissingFile(t *testing.T) {
	t.Parallel()
	client, err := New(Config{Endpoint: "https://example.test/v1", Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.UploadState(context.Background(), filepath.Join(t.TempDir(), "absent.pth")); err == nil {
		t.Fatal("UploadState accepted a missing file")
	}
}

func TestUploadStateRejectsEmptyStateID(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		_, _ = writer.Write([]byte(`{"object":"rwkv.state"}`))
	}))
	defer server.Close()
	statePath := filepath.Join(t.TempDir(), "state.pth")
	if err := os.WriteFile(statePath, []byte("x"), 0o600); err != nil {
		t.Fatal(err)
	}
	client, err := New(Config{Endpoint: server.URL + "/v1/batch/completions", Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.UploadState(context.Background(), statePath); err == nil {
		t.Fatal("UploadState accepted a response without state_id")
	}
}

func TestListStates(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodGet {
			t.Errorf("method = %s, want GET", request.Method)
		}
		if request.URL.Path != "/v1/state/list" {
			t.Errorf("path = %s, want /v1/state/list", request.URL.Path)
		}
		_, _ = writer.Write([]byte(`{"object":"list","data":[
			{"state_id":"state-a","filename":"a.pth","size_bytes":10,"tensor_count":32,"created":1},
			{"state_id":"state-b","filename":"b.pth","size_bytes":20,"tensor_count":32,"created":2}
		]}`))
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL + "/v1/chat/completions", Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	states, err := client.ListStates(context.Background())
	if err != nil {
		t.Fatal(err)
	}
	if len(states) != 2 || states[0].StateID != "state-a" || states[1].StateID != "state-b" {
		t.Fatalf("states = %+v", states)
	}
	if states[0].Filename != "a.pth" || states[0].SizeBytes != 10 {
		t.Errorf("states[0] = %+v", states[0])
	}
}

func TestDeleteState(t *testing.T) {
	t.Parallel()
	var received map[string]string
	var method string
	var contentType string
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		method = request.Method
		contentType = request.Header.Get("Content-Type")
		body, _ := io.ReadAll(request.Body)
		_ = json.Unmarshal(body, &received)
		_, _ = writer.Write([]byte(`{"deleted":true,"state_id":"state-abc123"}`))
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL + "/v1/batch/completions", Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	if err := client.DeleteState(context.Background(), "state-abc123"); err != nil {
		t.Fatal(err)
	}
	if method != http.MethodDelete {
		t.Errorf("method = %s, want DELETE", method)
	}
	if contentType != "application/json" {
		t.Errorf("content type = %q, want application/json", contentType)
	}
	if received["state_id"] != "state-abc123" {
		t.Errorf("delete body = %v", received)
	}
}

func TestDeleteStateRequiresStateID(t *testing.T) {
	t.Parallel()
	client, err := New(Config{Endpoint: "https://example.test/v1", Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	if err := client.DeleteState(context.Background(), "  "); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("DeleteState error = %v, want ErrInvalidRequest", err)
	}
}

func TestStateEndpointsRedactPasswordOnError(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		writer.WriteHeader(http.StatusBadRequest)
		_, _ = writer.Write([]byte("upload failed with secret-token inside"))
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL + "/v1/batch/completions", Model: "rwkv7", Password: "secret-token"})
	if err != nil {
		t.Fatal(err)
	}
	statePath := filepath.Join(t.TempDir(), "state.pth")
	if err := os.WriteFile(statePath, []byte("x"), 0o600); err != nil {
		t.Fatal(err)
	}
	_, err = client.UploadState(context.Background(), statePath)
	if err == nil {
		t.Fatal("UploadState accepted HTTP 400")
	}
	if strings.Contains(err.Error(), "secret-token") {
		t.Errorf("error leaked the password: %v", err)
	}
	if !errors.Is(err, ErrRemote) {
		t.Errorf("error = %v, want ErrRemote", err)
	}
}
