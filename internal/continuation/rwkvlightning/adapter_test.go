package rwkvlightning

import (
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
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
