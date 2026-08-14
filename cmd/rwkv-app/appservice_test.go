package main

import (
	"encoding/json"
	"path/filepath"
	"strings"
	"testing"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
)

func resolvedWorkspace(t *testing.T) string {
	t.Helper()
	workspace := t.TempDir()
	resolved, err := filepath.EvalSymlinks(workspace)
	if err != nil {
		t.Fatal(err)
	}
	return resolved
}

func testAppStore(t *testing.T) *appstorage.Store {
	t.Helper()
	root := t.TempDir()
	dataDirectory := filepath.Join(root, "data")
	return appstorage.New(appstorage.Paths{
		ConfigFile:       filepath.Join(root, "config", "settings.json"),
		DataDirectory:    dataDirectory,
		StateFile:        filepath.Join(root, "state", "app-state.json"),
		CacheDirectory:   filepath.Join(root, "cache"),
		ConversationData: filepath.Join(dataDirectory, "conversations"),
	})
}

func testConversation(t *testing.T, store *appstorage.Store, workspace, title, content string) appstorage.Conversation {
	t.Helper()
	conversation, err := appstorage.NewConversation(workspace, title)
	if err != nil {
		t.Fatal(err)
	}
	conversation.Messages = []appstorage.DisplayMessage{{ID: "message-1", Role: "user", Content: content}}
	conversation.Transcript = []agentapi.ConversationMessage{{Role: "user", Content: content}}
	if err := store.SaveConversation(conversation); err != nil {
		t.Fatal(err)
	}
	return conversation
}

func TestAppServiceBootstrapsSavedSettingsAndConversation(t *testing.T) {
	t.Parallel()
	workspace := resolvedWorkspace(t)
	store := testAppStore(t)
	config := agentapi.Config{
		Provider: agentapi.ProviderRWKVLightning,
		Endpoint: "https://example.test",
		Model:    "rwkv-test",
		Password: "plain-secret",
		Headers:  map[string]string{"X-Service-Key": "plain-header"},
	}
	if err := store.SaveSettings(config); err != nil {
		t.Fatal(err)
	}
	conversation := testConversation(t, store, workspace, "Saved conversation", "hello")
	if _, err := store.RememberWorkspace(workspace); err != nil {
		t.Fatal(err)
	}
	if err := store.SetActiveConversation(workspace, conversation.ID); err != nil {
		t.Fatal(err)
	}

	service, err := agentapi.NewService(agentapi.Options{Workspace: workspace})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, store)
	t.Cleanup(func() { _ = backend.Close() })

	bootstrap, err := backend.Bootstrap()
	if err != nil {
		t.Fatal(err)
	}
	if !bootstrap.HasConfig || bootstrap.Config.Password != "plain-secret" || bootstrap.Config.Headers["X-Service-Key"] != "plain-header" {
		t.Fatalf("saved config was not restored: %+v", bootstrap.Config)
	}
	if bootstrap.Status.State != agentapi.ModelIdle {
		t.Fatalf("startup unexpectedly configured a provider: %+v", bootstrap.Status)
	}
	if bootstrap.Conversation == nil || bootstrap.Conversation.ID != conversation.ID || len(bootstrap.Conversation.Messages) != 1 {
		t.Fatalf("active conversation was not restored: %+v", bootstrap.Conversation)
	}
}

func TestAppServiceSwitchesWorkspaceAndRestoresItsConversation(t *testing.T) {
	t.Parallel()
	workspaceA := resolvedWorkspace(t)
	workspaceB := resolvedWorkspace(t)
	store := testAppStore(t)
	conversationA := testConversation(t, store, workspaceA, "Conversation A", "from A")
	conversationB := testConversation(t, store, workspaceB, "Conversation B", "from B")
	if _, err := store.RememberWorkspace(workspaceA); err != nil {
		t.Fatal(err)
	}
	if _, err := store.RememberWorkspace(workspaceB); err != nil {
		t.Fatal(err)
	}
	if err := store.SetActiveConversation(workspaceA, conversationA.ID); err != nil {
		t.Fatal(err)
	}
	if err := store.SetActiveConversation(workspaceB, conversationB.ID); err != nil {
		t.Fatal(err)
	}

	service, err := agentapi.NewService(agentapi.Options{Workspace: workspaceA})
	if err != nil {
		t.Fatal(err)
	}
	backend := newAppService(service, store)
	t.Cleanup(func() { _ = backend.Close() })

	bootstrap, err := backend.OpenWorkspace(workspaceB)
	if err != nil {
		t.Fatal(err)
	}
	if bootstrap.Status.Workspace != workspaceB || bootstrap.Status.State != agentapi.ModelIdle {
		t.Fatalf("workspace status = %+v", bootstrap.Status)
	}
	if bootstrap.Conversation == nil || bootstrap.Conversation.ID != conversationB.ID || bootstrap.Conversation.Messages[0].Content != "from B" {
		t.Fatalf("workspace conversation = %+v", bootstrap.Conversation)
	}
	foundActive := false
	for _, workspace := range bootstrap.Workspaces {
		if workspace.Path == workspaceB && workspace.Active {
			foundActive = true
		}
	}
	if !foundActive {
		t.Fatalf("recent workspaces = %+v", bootstrap.Workspaces)
	}
}

func TestParseOptionsTracksExplicitWorkspace(t *testing.T) {
	t.Parallel()
	implicit, err := parseOptions(nil)
	if err != nil {
		t.Fatal(err)
	}
	if implicit.workspaceExplicit {
		t.Fatal("default workspace was marked explicit")
	}
	explicitPath := resolvedWorkspace(t)
	explicit, err := parseOptions([]string{"--workspace", explicitPath})
	if err != nil {
		t.Fatal(err)
	}
	if !explicit.workspaceExplicit || explicit.workspace != explicitPath {
		t.Fatalf("explicit options = %+v", explicit)
	}
}

func TestStoredToolTraceKeepsCompactStatus(t *testing.T) {
	t.Parallel()
	trace := storedToolTrace(agentapi.Result{Steps: []agentapi.Step{
		{Number: 1, Stage: "decision"},
		{
			Number: 2, Tool: "spawn_agents", ToolArguments: `{"tasks":["docs","code"]}`,
			ToolResult: `{"large":"parent payload must not be copied"}`, ToolExecuted: true,
			Subagents: []agentapi.SubagentTrace{{
				Index: 1, Task: "docs", Status: "completed", Route: "inspect",
				Bundles: []string{"web"}, DurationMS: 850, Output: "found docs",
				Sources: []string{"https://example.test"},
				Steps: []agentapi.SubagentStep{{
					Number: 1, Tool: "web_fetch", Arguments: `{"urls":["https://example.test"]}`,
					Status: "completed", Retries: []agentapi.ToolRetryTrace{{
						Attempt: 1, MaxAttempts: 5, StatusCode: 503, DelayMS: 1000,
					}},
				}},
			}},
		},
		{
			Number: 3, Tool: "web_fetch", ToolError: "request timed out", ToolExecuted: true,
			ToolRetries: []agentapi.ToolRetryTrace{{Attempt: 1, MaxAttempts: 5, DelayMS: 500}},
		},
	}})
	if len(trace) != 2 {
		t.Fatalf("trace = %+v", trace)
	}
	if trace[0].Step != 2 || trace[0].Tool != "spawn_agents" || trace[0].Status != "completed" || trace[0].Error != "" ||
		trace[0].Arguments != `{"tasks":["docs","code"]}` || len(trace[0].Subagents) != 1 ||
		trace[0].Subagents[0].Steps[0].Tool != "web_fetch" || trace[0].Subagents[0].Output != "found docs" ||
		trace[0].Subagents[0].Steps[0].Retries[0].StatusCode != 503 ||
		trace[0].Subagents[0].Steps[0].Retries[0].DelayMS != 1000 {
		t.Fatalf("completed trace = %+v", trace[0])
	}
	encoded, err := json.Marshal(trace)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(encoded), "parent payload must not be copied") {
		t.Fatalf("trace retained tool result: %s", encoded)
	}
	if trace[1].Status != "failed" || trace[1].Error != "request timed out" ||
		trace[1].Retries[0].StatusCode != 0 || trace[1].Retries[0].DelayMS != 500 {
		t.Fatalf("failed trace = %+v", trace[1])
	}
}
