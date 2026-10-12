package main

import (
	"encoding/json"
	"fmt"
	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/appstorage"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
)

func TestTurnFileArtifactsAssociateOnlyNewProposals(t *testing.T) {
	a := agentapi.FileChange{Path: "a.txt", Before: tools.FileSnapshot{Kind: "missing"}, After: tools.FileSnapshot{Kind: "file", Data: "YQ==", Mode: 0644}}
	b := a
	b.Path = "b.txt"
	files := turnFileArtifacts([]agentapi.FileChange{a}, []agentapi.FileChange{a, b})
	if len(files) != 1 || files[0].Change != b || files[0].Status != "pending" {
		t.Fatalf("files %+v", files)
	}
	updated := a
	updated.After.Data = "Yg=="
	files = turnFileArtifacts([]agentapi.FileChange{a}, []agentapi.FileChange{updated})
	if len(files) != 1 || files[0].Change != updated {
		t.Fatal(files)
	}
}
func TestConversationViewRetainsFileArtifacts(t *testing.T) {
	files := []appstorage.FileArtifact{{Change: agentapi.FileChange{Path: "index.html"}, Status: "saved"}}
	value := conversationView(appstorage.Conversation{Messages: []appstorage.DisplayMessage{{ID: "m", Role: "assistant", Files: files}}})
	if len(value.Messages) != 1 || len(value.Messages[0].Files) != 1 || value.Messages[0].Files[0].Status != "saved" {
		t.Fatalf("view %+v", value)
	}
}

func TestFileArtifactStaysOnResponseAfterApproval(t *testing.T) {
	binary, err := tools.ResolveBashSidecar(filepath.Join("..", "..", "local", "bin", "justbash-sidecar"))
	if err != nil {
		t.Skip("build just-bash sidecar first")
	}
	t.Setenv(tools.BashSidecarEnv, binary)
	outputs := []string{`<tool_call>{"name":"write_file","arguments":{"path":"index.html","content":"<h1>Hello</h1>"}}</tool_call>`, "已暂存，请确认保存。"}
	var calls atomic.Int32
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		index := int(calls.Add(1)) - 1
		if index >= len(outputs) {
			t.Error("unexpected extra request")
			http.Error(w, "extra request", 500)
			return
		}
		payload, _ := json.Marshal(map[string]any{"choices": []any{map[string]any{"index": 0, "delta": map[string]any{"content": outputs[index]}, "finish_reason": "stop"}}})
		w.Header().Set("Content-Type", "text/event-stream")
		fmt.Fprintf(w, "data: %s\n\ndata: [DONE]\n\n", payload)
	}))
	defer server.Close()
	root := resolvedWorkspace(t)
	store := testAppStore(t)
	service, err := agentapi.NewService(agentapi.Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, store)
	defer backend.Close()
	if _, err = backend.ConfigureProvider(t.Context(), "", "fixture", agentapi.Config{Provider: agentapi.ProviderRWKVLightningCUDA, Endpoint: server.URL, Model: "fixture", MaxTokens: 4096, DecisionMaxTokens: 4096}); err != nil {
		t.Fatal(err)
	}
	if _, err = backend.Chat(t.Context(), "创建 index.html"); err != nil {
		t.Fatal(err)
	}
	value, err := backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	files := value.Conversation.Messages[len(value.Conversation.Messages)-1].Files
	if len(files) != 1 || files[0].Status != "pending" {
		t.Fatalf("artifacts %+v", files)
	}
	if _, err = os.Stat(filepath.Join(root, "index.html")); !os.IsNotExist(err) {
		t.Fatal("unapproved file persisted")
	}
	if err = backend.NewConversation(); err == nil {
		t.Fatal("unconfirmed changes lost on conversation switch")
	}
	if _, err = backend.ResolveFileChanges([]agentapi.FileChange{files[0].Change}, true); err != nil {
		t.Fatal(err)
	}
	saved, err := store.LoadConversation(value.Conversation.ID)
	if err != nil {
		t.Fatal(err)
	}
	finalFiles := saved.Messages[len(saved.Messages)-1].Files
	if len(finalFiles) != 1 || finalFiles[0].Status != "saved" || finalFiles[0].Change.After.Data != files[0].Change.After.Data {
		t.Fatalf("saved artifacts %+v", finalFiles)
	}
	b, err := os.ReadFile(filepath.Join(root, "index.html"))
	if err != nil || string(b) != "<h1>Hello</h1>" {
		t.Fatalf("file %q %v", b, err)
	}
}
