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
)

// fakeStateServer mimics the rwkv_lightning /v1/state/* routes.
type fakeStateServer struct {
	mu     sync.Mutex
	states []map[string]any
	next   int
}

func (f *fakeStateServer) ServeHTTP(writer http.ResponseWriter, request *http.Request) {
	f.mu.Lock()
	defer f.mu.Unlock()
	switch request.URL.Path {
	case "/v1/state/list":
		_ = json.NewEncoder(writer).Encode(map[string]any{"data": f.states})
	case "/v1/state/upload":
		file, header, err := request.FormFile("file")
		if err != nil {
			http.Error(writer, err.Error(), http.StatusBadRequest)
			return
		}
		defer file.Close()
		f.next++
		state := map[string]any{
			"state_id": fmt.Sprintf("state-%d", f.next), "filename": header.Filename,
			"size_bytes": header.Size, "tensor_count": 32, "created": 1788855449,
		}
		f.states = append(f.states, state)
		_ = json.NewEncoder(writer).Encode(state)
	case "/v1/state/delete":
		var body struct {
			StateID string `json:"state_id"`
		}
		_ = json.NewDecoder(request.Body).Decode(&body)
		kept := f.states[:0]
		for _, state := range f.states {
			if state["state_id"] != body.StateID {
				kept = append(kept, state)
			}
		}
		f.states = kept
		_, _ = writer.Write([]byte(`{"object":"rwkv.state.deleted"}`))
	default:
		http.NotFound(writer, request)
	}
}

// restart drops every uploaded state, like a deployment process restart.
func (f *fakeStateServer) restart() {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.states = nil
}

func TestAppServiceStateUploadListReuploadAndDelete(t *testing.T) {
	fake := &fakeStateServer{}
	server := httptest.NewServer(fake)
	t.Cleanup(server.Close)

	store := testAppStore(t)
	service, err := agentapi.NewService(agentapi.Options{Workspace: resolvedWorkspace(t)})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, store)
	t.Cleanup(func() { _ = backend.Close() })

	statePath := filepath.Join(t.TempDir(), "s316.pth")
	if err := os.WriteFile(statePath, []byte("fake-state-bytes"), 0o600); err != nil {
		t.Fatal(err)
	}
	config := agentapi.Config{
		Provider: agentapi.ProviderRWKVLightningCUDA,
		Endpoint: server.URL + "/v1/batch/completions",
		Model:    "rwkv7",
	}
	ctx := context.Background()

	uploaded, err := backend.UploadState(ctx, config, statePath)
	if err != nil {
		t.Fatal(err)
	}
	if uploaded.ID != "state-1" || uploaded.Filename != "s316.pth" || uploaded.LocalPath != statePath || !uploaded.LocalAvailable {
		t.Fatalf("uploaded = %+v", uploaded)
	}
	listing, err := backend.ListStates(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.States) != 1 || listing.States[0].LocalPath != statePath || len(listing.Missing) != 0 {
		t.Fatalf("listing = %+v", listing)
	}

	config.StateID = uploaded.ID
	if err := backend.verifyStateAvailable(ctx, config); err != nil {
		t.Fatalf("verify present state: %v", err)
	}

	fake.restart()
	if err := backend.verifyStateAvailable(ctx, config); err == nil || !strings.Contains(err.Error(), "state-1") {
		t.Fatalf("verify wiped state error = %v", err)
	}
	listing, err = backend.ListStates(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.States) != 0 || len(listing.Missing) != 1 || listing.Missing[0].ID != "state-1" || listing.Missing[0].LocalPath != statePath {
		t.Fatalf("listing after restart = %+v", listing)
	}

	// Re-upload from the recorded path, then forget the stale record locally.
	reuploaded, err := backend.UploadState(ctx, config, listing.Missing[0].LocalPath)
	if err != nil {
		t.Fatal(err)
	}
	if err := backend.DeleteState(ctx, config, "state-1", false); err != nil {
		t.Fatal(err)
	}
	listing, err = backend.ListStates(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.States) != 1 || listing.States[0].ID != reuploaded.ID || len(listing.Missing) != 0 {
		t.Fatalf("listing after reupload = %+v", listing)
	}

	if err := backend.DeleteState(ctx, config, reuploaded.ID, true); err != nil {
		t.Fatal(err)
	}
	listing, err = backend.ListStates(ctx, config)
	if err != nil {
		t.Fatal(err)
	}
	if len(listing.States) != 0 || len(listing.Missing) != 0 {
		t.Fatalf("listing after delete = %+v", listing)
	}
}

func TestStateCallsRejectProvidersWithoutUploadedState(t *testing.T) {
	service, err := agentapi.NewService(agentapi.Options{Workspace: resolvedWorkspace(t)})
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = service.Close() })
	for _, provider := range []agentapi.Provider{agentapi.ProviderRWKVLightningPython, agentapi.ProviderChatCompletions, agentapi.ProviderLocal} {
		_, err := service.ListStates(context.Background(), agentapi.Config{Provider: provider, Endpoint: "http://127.0.0.1:1"})
		if err == nil {
			t.Fatalf("%s: ListStates succeeded", provider)
		}
	}
}
