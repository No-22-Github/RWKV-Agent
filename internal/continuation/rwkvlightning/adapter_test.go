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

func TestUploadAdapterStreamsMultipart(t *testing.T) {
	t.Parallel()
	content := []byte("miss-package-bytes")
	path := filepath.Join(t.TempDir(), "adapter-final.pth")
	if err := os.WriteFile(path, content, 0o600); err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.Method != http.MethodPost || request.URL.Path != "/v1/adapters" {
			t.Errorf("request = %s %s, want POST /v1/adapters", request.Method, request.URL.Path)
		}
		if err := request.ParseMultipartForm(1 << 20); err != nil {
			t.Fatalf("parse multipart form: %v", err)
		}
		if got := request.FormValue("adapter_id"); got != "v20-lr3e-5" {
			t.Errorf("adapter_id = %q", got)
		}
		file, header, err := request.FormFile("file")
		if err != nil {
			t.Fatalf("form file: %v", err)
		}
		defer file.Close()
		body, _ := io.ReadAll(file)
		if string(body) != string(content) || header.Filename != "adapter-final.pth" {
			t.Errorf("file = %q (%s)", body, header.Filename)
		}
		_, _ = writer.Write([]byte(`{"adapter_id":"v20-lr3e-5","version":"abc123"}`))
	}))
	defer server.Close()

	client, err := New(Config{Endpoint: server.URL + "/v1/batch/completions", Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	var sent, total int64
	version, err := client.UploadAdapter(context.Background(), " v20-lr3e-5 ", path, func(s, t int64) { sent, total = s, t })
	if err != nil {
		t.Fatalf("UploadAdapter: %v", err)
	}
	if version != "abc123" {
		t.Errorf("version = %q", version)
	}
	if total == 0 || sent != total {
		t.Errorf("progress sent=%d total=%d, want complete", sent, total)
	}
}

func TestRegisterListDeleteAdapter(t *testing.T) {
	t.Parallel()
	var bodies []map[string]any
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path != "/v1/adapters" {
			t.Errorf("path = %s", request.URL.Path)
		}
		switch request.Method {
		case http.MethodGet:
			_, _ = writer.Write([]byte(`{"data":[{"id":"a","version":"v1","manifest":{"rank":16,"alpha":16,"scale":1,"base_fingerprint":"fp","dtype":"bfloat16"}}],"ram_hits":0}`))
			return
		case http.MethodPost, http.MethodDelete:
			var body map[string]any
			_ = json.NewDecoder(request.Body).Decode(&body)
			bodies = append(bodies, body)
		}
		if request.Method == http.MethodPost {
			_, _ = writer.Write([]byte(`{"adapter_id":"a","version":"v1"}`))
			return
		}
		_, _ = writer.Write([]byte(`{"deleted":true}`))
	}))
	defer server.Close()

	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	ctx := context.Background()
	if version, err := client.RegisterAdapterPath(ctx, "a", "/srv/adapter-final.pth"); err != nil || version != "v1" {
		t.Fatalf("RegisterAdapterPath = %q, %v", version, err)
	}
	listed, err := client.ListAdapters(ctx)
	if err != nil || len(listed) != 1 || listed[0].Manifest.Rank != 16 || listed[0].Version != "v1" {
		t.Fatalf("ListAdapters = %+v, %v", listed, err)
	}
	if err := client.DeleteAdapter(ctx, "a", ""); err != nil {
		t.Fatalf("DeleteAdapter: %v", err)
	}
	if len(bodies) != 2 || bodies[0]["path"] != "/srv/adapter-final.pth" || bodies[1]["adapter_id"] != "a" {
		t.Fatalf("bodies = %v", bodies)
	}
	if _, ok := bodies[1]["adapter_version"]; ok {
		t.Errorf("delete without version sent adapter_version: %v", bodies[1])
	}
}

func TestUploadAdapterUsesHTTP1OverTLS(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "adapter-final.pth")
	if err := os.WriteFile(path, []byte("miss-package-bytes"), 0o600); err != nil {
		t.Fatal(err)
	}
	var proto string
	server := httptest.NewUnstartedServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		proto = request.Proto
		_, _ = writer.Write([]byte(`{"adapter_id":"a","version":"v1"}`))
	}))
	server.EnableHTTP2 = true
	server.StartTLS()
	defer server.Close()

	// A client that would normally negotiate h2 with this server.
	transport := server.Client().Transport.(*http.Transport)
	transport.ForceAttemptHTTP2 = true
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7", HTTPClient: &http.Client{Transport: transport}})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.UploadAdapter(context.Background(), "a", path, nil); err != nil {
		t.Fatalf("UploadAdapter: %v", err)
	}
	if proto != "HTTP/1.1" {
		t.Errorf("upload protocol = %s, want HTTP/1.1", proto)
	}

	// Control: the ordinary client does negotiate h2, so the test is meaningful.
	response, err := (&http.Client{Transport: transport}).Get(server.URL)
	if err != nil {
		t.Fatal(err)
	}
	response.Body.Close()
	if response.Proto != "HTTP/2.0" {
		t.Skipf("control request used %s; h2 not negotiated here", response.Proto)
	}
}

func TestUploadAdapterRejectsOversizedFile(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "training.pth")
	file, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	if err := file.Truncate(MaxAdapterUploadBytes + 1); err != nil {
		t.Fatal(err)
	}
	file.Close()
	requests := 0
	server := httptest.NewServer(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { requests++ }))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "rwkv7"})
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.UploadAdapter(context.Background(), "a", path, nil)
	if err == nil || !strings.Contains(err.Error(), "413") {
		t.Fatalf("err = %v, want size-limit error mentioning 413", err)
	}
	if !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Errorf("err = %v, want ErrInvalidRequest", err)
	}
	if requests != 0 {
		t.Errorf("server saw %d requests, want 0", requests)
	}
}
