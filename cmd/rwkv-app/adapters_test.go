package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
)

// fakeAdapterServer mimics the rwkv_lightning /v1/adapters route: versions
// are content hashes, registrations live in memory.
type fakeAdapterServer struct {
	mu       sync.Mutex
	adapters []map[string]any
}

func (f *fakeAdapterServer) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	f.mu.Lock()
	defer f.mu.Unlock()
	if request.URL.Path != "/v1/adapters" {
		http.NotFound(writer, request)
		return
	}
	switch request.Method {
	case http.MethodGet:
		_ = json.NewEncoder(writer).Encode(map[string]any{"data": f.adapters, "ram_hits": 0})
	case http.MethodPost:
		var id, content string
		if strings.HasPrefix(request.Header.Get("Content-Type"), "multipart/") {
			file, _, err := request.FormFile("file")
			if err != nil {
				http.Error(writer, err.Error(), http.StatusBadRequest)
				return
			}
			defer file.Close()
			id = request.FormValue("adapter_id")
			buffer := make([]byte, 64)
			n, _ := file.Read(buffer)
			content = string(buffer[:n])
		} else {
			var body struct {
				AdapterID string `json:"adapter_id"`
				Path      string `json:"path"`
			}
			_ = json.NewDecoder(request.Body).Decode(&body)
			id, content = body.AdapterID, body.Path
		}
		version := fmt.Sprintf("sha-%s", content)
		f.adapters = append(f.adapters, map[string]any{
			"id": id, "version": version, "manifest": map[string]any{"rank": 16, "alpha": 16, "scale": 1},
		})
		_ = json.NewEncoder(writer).Encode(map[string]any{"adapter_id": id, "version": version})
	case http.MethodDelete:
		var body struct {
			AdapterID string `json:"adapter_id"`
		}
		_ = json.NewDecoder(request.Body).Decode(&body)
		kept := f.adapters[:0]
		for _, adapter := range f.adapters {
			if adapter["id"] != body.AdapterID {
				kept = append(kept, adapter)
			}
		}
		f.adapters = kept
		_, _ = writer.Write([]byte(`{"deleted":true}`))
	}
}

func (f *fakeAdapterServer) restart() {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.adapters = nil
}

func TestAppServiceAdapterRegisterListVerifyAndDelete(t *testing.T) {
	fake := &fakeAdapterServer{}
	server := httptest.NewServer(fake)
	t.Cleanup(server.Close)

	service, err := agentapi.NewService(agentapi.Options{Workspace: resolvedWorkspace(t)})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, testAppStore(t))
	t.Cleanup(func() { _ = backend.Close() })

	localPath := filepath.Join(t.TempDir(), "adapter-final.pth")
	if err := os.WriteFile(localPath, []byte("local"), 0o600); err != nil {
		t.Fatal(err)
	}
	config := agentapi.Config{
		Provider: agentapi.ProviderRWKVLightningCUDA,
		Endpoint: server.URL + "/v1/batch/completions",
		Model:    "rwkv7",
	}
	ctx := context.Background()

	byPath, err := backend.RegisterAdapter(ctx, config, "lr3e-5", "/srv/train-2-0/adapter-final.pth", false)
	if err != nil {
		t.Fatal(err)
	}
	if byPath.Version != "sha-/srv/train-2-0/adapter-final.pth" || byPath.ServerPath == "" || byPath.LocalPath != "" {
		t.Fatalf("registered by path = %+v", byPath)
	}
	uploaded, err := backend.RegisterAdapter(ctx, config, "r64", localPath, true)
	if err != nil {
		t.Fatal(err)
	}
	if uploaded.Version != "sha-local" || uploaded.LocalPath != localPath || !uploaded.LocalAvailable {
		t.Fatalf("uploaded = %+v", uploaded)
	}

	listing, err := backend.ListAdapters(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.Adapters) != 2 || len(listing.Missing) != 0 || listing.Adapters[0].Rank != 16 {
		t.Fatalf("listing = %+v", listing)
	}

	config.AdapterID = "r64"
	if err := backend.verifyAdapterAvailable(ctx, config); err != nil {
		t.Fatalf("verify present adapter: %v", err)
	}
	fake.restart()
	if err := backend.verifyAdapterAvailable(ctx, config); err == nil || !strings.Contains(err.Error(), "r64") {
		t.Fatalf("verify wiped adapter error = %v", err)
	}
	listing, err = backend.ListAdapters(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.Adapters) != 0 || len(listing.Missing) != 2 {
		t.Fatalf("listing after restart = %+v", listing)
	}

	if err := backend.DeleteAdapter(ctx, config, "lr3e-5", false); err != nil {
		t.Fatal(err)
	}
	listing, err = backend.ListAdapters(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.Missing) != 1 || listing.Missing[0].ID != "r64" {
		t.Fatalf("listing after forget = %+v", listing)
	}
}

func TestJoinAdaptersPicksRecordedVersion(t *testing.T) {
	adapters := []agentapi.RemoteAdapter{
		{ID: "a", Version: "v1", Rank: 4},
		{ID: "a", Version: "v2", Rank: 16},
		{ID: "b", Version: "x1"},
		{ID: "b", Version: "x2"},
	}
	records := []appstorage.AdapterRegistration{{AdapterID: "a", Version: "v2", ServerPath: "/srv/a.pth"}}
	listing := joinAdapters(adapters, records)
	if len(listing.Adapters) != 2 {
		t.Fatalf("listing = %+v", listing)
	}
	a, b := listing.Adapters[0], listing.Adapters[1]
	if a.Version != "v2" || a.Rank != 16 || a.Versions != 2 || a.ServerPath != "/srv/a.pth" {
		t.Errorf("a = %+v", a)
	}
	// Two versions this machine never registered: the list cannot say which
	// is the default, so none is shown.
	if b.Version != "" || b.Versions != 2 {
		t.Errorf("b = %+v", b)
	}
}

func TestTurnMetaShowsAdapterBeforeState(t *testing.T) {
	meta := turnMeta(agentapi.Result{DurationMS: 1500}, "rwkv7", "lr3e-5", "state-1")
	if !strings.HasSuffix(meta, "rwkv7 · MiSS lr3e-5 · state-1") {
		t.Fatalf("meta = %q", meta)
	}
}

func TestAdapterOnOldDeploymentIsExplainedAndBlocksConnect(t *testing.T) {
	server := httptest.NewServer(http.NotFoundHandler())
	t.Cleanup(server.Close)
	service, err := agentapi.NewService(agentapi.Options{Workspace: resolvedWorkspace(t)})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, testAppStore(t))
	t.Cleanup(func() { _ = backend.Close() })
	config := agentapi.Config{Provider: agentapi.ProviderRWKVLightningCUDA, Endpoint: server.URL, Model: "rwkv7"}
	ctx := context.Background()

	if _, err := backend.ListAdapters(ctx, config); err == nil || !strings.Contains(err.Error(), "不支持 MiSS") || strings.Contains(err.Error(), "404 page") {
		t.Fatalf("list error = %v", err)
	}
	if err := backend.verifyAdapterAvailable(ctx, config); err != nil {
		t.Fatalf("no adapter selected must not block: %v", err)
	}
	config.AdapterID = "r16"
	if err := backend.verifyAdapterAvailable(ctx, config); err == nil || !strings.Contains(err.Error(), "r16") {
		t.Fatalf("selected adapter on old deployment error = %v", err)
	}
}
