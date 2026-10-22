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

// State 与 MiSS 适配器只在本次运行有效：运行配置带着它们，档案里不存，
// 也不因此把运行连接报成"待重新加载"。释放模型后回到空闲、没有运行连接。
// State 与 MiSS 适配器跟着连接档案走：选中即记进档案，下次切回这个连接照样用上；
// 设置里编辑连接时沿用记住的值；服务端重启清空后，切回来时这次不用、照常连接。
func TestAppServiceRemembersStatePerProfileAndUnloads(t *testing.T) {
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
	if _, err := backend.ConfigureProvider(ctx, "", "remote", config); err != nil {
		t.Fatal(err)
	}
	status, err := backend.SetRuntimeState(ctx, uploaded.ID)
	if err != nil {
		t.Fatal(err)
	}
	if status.StateID != uploaded.ID {
		t.Fatalf("runtime state = %q, want %q", status.StateID, uploaded.ID)
	}
	value, err := backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	if len(value.Providers) != 1 || value.Providers[0].Config.StateID != uploaded.ID {
		t.Fatalf("saved providers = %+v", value.Providers)
	}
	if value.Config.StateID != uploaded.ID || value.RuntimeOutdated {
		t.Fatalf("runtime config state = %q outdated = %v", value.Config.StateID, value.RuntimeOutdated)
	}
	id := value.Providers[0].ID

	// 设置里改连接（草稿里没有 State）不会把记住的 State 冲掉。
	if _, err := backend.SaveProvider(id, "renamed", config); err != nil {
		t.Fatal(err)
	}
	if entry, _ := backend.savedProvider(id); entry.Config.StateID != uploaded.ID {
		t.Fatalf("editor save dropped the state: %+v", entry.Config)
	}

	status, err = backend.UnloadModel()
	if err != nil {
		t.Fatal(err)
	}
	if status.State != agentapi.ModelIdle {
		t.Fatalf("status after unload = %+v", status)
	}
	value, err = backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	if value.RuntimeProviderID != "" || len(value.Providers) != 1 {
		t.Fatalf("after unload runtime = %q providers = %d", value.RuntimeProviderID, len(value.Providers))
	}

	if status, err = backend.ActivateProvider(ctx, id); err != nil || status.StateID != uploaded.ID {
		t.Fatalf("reactivated state = %q err = %v", status.StateID, err)
	}

	// 服务端重启：State 没了。切回来照常连接，只是这次不用它。
	fake.mu.Lock()
	fake.states = nil
	fake.mu.Unlock()
	if status, err = backend.ActivateProvider(ctx, id); err != nil || status.StateID != "" {
		t.Fatalf("activate with a wiped state = %q err = %v", status.StateID, err)
	}
}

// 对话格式记进运行中连接的档案，不重连、立即对下一轮生效；设置里编辑连接时沿用。
func TestAppServiceSetRuntimeFormatRemembersPerProfile(t *testing.T) {
	server := httptest.NewServer(&fakeStateServer{})
	t.Cleanup(server.Close)
	store := testAppStore(t)
	service, err := agentapi.NewService(agentapi.Options{Workspace: resolvedWorkspace(t)})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, store)
	t.Cleanup(func() { _ = backend.Close() })

	// 前端草稿总带一个空的请求头表；它不能让运行中的连接被当成「待重新加载」。
	config := agentapi.Config{Provider: agentapi.ProviderRWKVLightningCUDA, Endpoint: server.URL + "/v1/batch/completions", Model: "rwkv7", Profile: agentapi.NewConfigProfile, AgentProtocol: agentapi.AgentProtocolXML, Thinking: "off", Headers: map[string]string{}}
	ctx := context.Background()
	if _, err := backend.ConfigureProvider(ctx, "", "remote", config); err != nil {
		t.Fatal(err)
	}
	think := RuntimeFormat{AgentProtocol: agentapi.AgentProtocolXML, Profile: agentapi.NewConfigProfile, Wire: "thinking=full,nudge=think", Thinking: "full"}
	if _, err := backend.SetRuntimeFormat(think); err != nil {
		t.Fatal(err)
	}
	value, err := backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	saved := value.Providers[0].Config
	if saved.Thinking != "full" || saved.Wire != think.Wire || value.Config.Thinking != "full" || value.RuntimeOutdated {
		t.Fatalf("saved = %+v runtime = %+v outdated = %v", saved, value.Config, value.RuntimeOutdated)
	}
	if _, err := backend.ConfigureProvider(ctx, value.Providers[0].ID, "remote", config); err != nil {
		t.Fatal(err)
	}
	if entry, _ := backend.savedProvider(value.Providers[0].ID); entry.Config.Thinking != "full" {
		t.Fatalf("editor reconnect reset the format: %+v", entry.Config)
	}
	if value, err = backend.Bootstrap(); err != nil || value.RuntimeOutdated {
		t.Fatalf("running remote reported outdated after an editor reconnect: err = %v", err)
	}
	if _, err := backend.SetRuntimeFormat(RuntimeFormat{AgentProtocol: "json", Profile: agentapi.NewConfigProfile}); err == nil {
		t.Fatal("invalid format accepted")
	}
}
