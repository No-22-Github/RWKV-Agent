package appstorage

import (
	"os"
	"path/filepath"
	"runtime"
	"testing"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
)

func testStore(t *testing.T) *Store {
	t.Helper()
	root := t.TempDir()
	return New(Paths{
		ConfigFile:       filepath.Join(root, "config", "settings.json"),
		DataDirectory:    filepath.Join(root, "data"),
		StateFile:        filepath.Join(root, "state", "app-state.json"),
		CacheDirectory:   filepath.Join(root, "cache"),
		ConversationData: filepath.Join(root, "data", "conversations"),
	})
}

func TestSettingsPersistCredentialsAtomically(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	config := agentapi.Config{
		Provider: agentapi.ProviderRWKVLightning,
		Endpoint: "https://example.test",
		Model:    "rwkv7-test",
		Password: "service-secret",
		Headers:  map[string]string{"CF-Access-Client-Secret": "header-secret"},
	}
	if err := store.SaveSettings(config); err != nil {
		t.Fatal(err)
	}
	config.Password = "updated-secret"
	if err := store.SaveSettings(config); err != nil {
		t.Fatal(err)
	}
	loaded, err := store.LoadSettings()
	if err != nil {
		t.Fatal(err)
	}
	if loaded.Provider.Password != "updated-secret" ||
		loaded.Provider.Headers["CF-Access-Client-Secret"] != "header-secret" {
		t.Fatalf("settings = %+v", loaded.Provider)
	}
	info, err := os.Stat(store.Paths().ConfigFile)
	if err != nil {
		t.Fatal(err)
	}
	if runtime.GOOS != "windows" && info.Mode().Perm() != 0o600 {
		t.Fatalf("settings permissions = %o", info.Mode().Perm())
	}
}

func TestSaveActiveProviderUpsertsAndActivates(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	first := agentapi.Config{Provider: agentapi.ProviderRWKVLightning, Endpoint: "https://a.test", Model: "model-a", Password: "p1"}
	second := agentapi.Config{Provider: agentapi.ProviderChatCompletions, Endpoint: "https://b.test", Model: "model-b", APIKey: "k1"}
	firstSaved, err := store.SaveActiveProvider(first)
	if err != nil {
		t.Fatal(err)
	}
	if _, err := store.SaveActiveProvider(second); err != nil {
		t.Fatal(err)
	}
	loaded, err := store.LoadSettings()
	if err != nil {
		t.Fatal(err)
	}
	if len(loaded.Providers) != 2 {
		t.Fatalf("expected 2 providers, got %d", len(loaded.Providers))
	}
	// 重新保存第一个（同 协议+地址+模型，仅改密钥）→ upsert，不新增，且 active 回到第一个。
	first.Password = "p2"
	reSaved, err := store.SaveActiveProvider(first)
	if err != nil {
		t.Fatal(err)
	}
	if reSaved.ID != firstSaved.ID {
		t.Fatalf("upsert should reuse id: %s vs %s", reSaved.ID, firstSaved.ID)
	}
	loaded, err = store.LoadSettings()
	if err != nil {
		t.Fatal(err)
	}
	if len(loaded.Providers) != 2 {
		t.Fatalf("upsert must not add a duplicate, got %d", len(loaded.Providers))
	}
	if loaded.ActiveID != firstSaved.ID {
		t.Fatalf("active should be re-saved provider, got %s", loaded.ActiveID)
	}
	for _, entry := range loaded.Providers {
		if entry.ID == firstSaved.ID && entry.Config.Password != "p2" {
			t.Fatalf("upsert must update config, got password %q", entry.Config.Password)
		}
	}
}

func TestLoadSettingsMigratesV1(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	if err := os.MkdirAll(filepath.Dir(store.Paths().ConfigFile), 0o700); err != nil {
		t.Fatal(err)
	}
	v1 := `{"schemaVersion":1,"provider":{"provider":"rwkv-lightning","endpoint":"https://legacy.test","model":"legacy-model","password":"secret"},"updatedAt":"2026-08-15T09:30:00Z"}`
	if err := os.WriteFile(store.Paths().ConfigFile, []byte(v1), 0o600); err != nil {
		t.Fatal(err)
	}
	loaded, err := store.LoadSettings()
	if err != nil {
		t.Fatal(err)
	}
	if loaded.SchemaVersion != SettingsSchemaVersion || len(loaded.Providers) != 1 {
		t.Fatalf("migration failed: %+v", loaded)
	}
	if loaded.ActiveID == "" || loaded.Providers[0].ID != loaded.ActiveID {
		t.Fatalf("migrated provider must be active: %+v", loaded)
	}
	if loaded.Providers[0].Config.Model != "legacy-model" || loaded.Providers[0].Config.Password != "secret" {
		t.Fatalf("migrated config lost fields: %+v", loaded.Providers[0].Config)
	}
}

func TestRemoveProviderReassignsActive(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	a, err := store.SaveActiveProvider(agentapi.Config{Provider: agentapi.ProviderRWKVLightning, Endpoint: "https://a.test", Model: "model-a"})
	if err != nil {
		t.Fatal(err)
	}
	b, err := store.SaveActiveProvider(agentapi.Config{Provider: agentapi.ProviderRWKVLightning, Endpoint: "https://b.test", Model: "model-b"})
	if err != nil {
		t.Fatal(err)
	}
	// 删除当前 active（b）→ active 回退到剩下的 a。
	settings, err := store.RemoveProvider(b.ID)
	if err != nil {
		t.Fatal(err)
	}
	if len(settings.Providers) != 1 || settings.ActiveID != a.ID {
		t.Fatalf("active should fall back to remaining provider: %+v", settings)
	}
	// 删除最后一个 → active 清空。
	settings, err = store.RemoveProvider(a.ID)
	if err != nil {
		t.Fatal(err)
	}
	if len(settings.Providers) != 0 || settings.ActiveID != "" {
		t.Fatalf("active should be empty after removing all: %+v", settings)
	}
}

func TestPrepareCreatesApplicationDirectories(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	if err := store.Prepare(); err != nil {
		t.Fatal(err)
	}
	paths := store.Paths()
	directories := []string{
		filepath.Dir(paths.ConfigFile), paths.DataDirectory, filepath.Dir(paths.StateFile),
		paths.CacheDirectory, paths.ConversationData,
	}
	for _, directory := range directories {
		info, err := os.Stat(directory)
		if err != nil {
			t.Fatal(err)
		}
		if !info.IsDir() {
			t.Fatalf("%s is not a directory", directory)
		}
		if runtime.GOOS != "windows" && info.Mode().Perm() != 0o700 {
			t.Fatalf("%s permissions = %o", directory, info.Mode().Perm())
		}
	}
}

func TestConversationAndWorkspaceRoundTrip(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	workspace := filepath.Join(t.TempDir(), "project")
	if err := os.MkdirAll(workspace, 0o700); err != nil {
		t.Fatal(err)
	}
	if _, err := store.RememberWorkspace(workspace); err != nil {
		t.Fatal(err)
	}
	conversation, err := NewConversation(workspace, "  Read   the project README  ")
	if err != nil {
		t.Fatal(err)
	}
	createdAt := time.Date(2026, time.August, 15, 9, 30, 0, 0, time.UTC)
	conversation.Messages = []DisplayMessage{
		{ID: "m1", Role: "user", Content: "Read README"},
		{
			ID: "m2", Role: "assistant", Content: "Done", CreatedAt: createdAt,
			Trace: &agentapi.Result{
				Output: "Done", Route: "inspect", Bundles: []string{"workspace"}, DurationMS: 1250,
				Steps: []agentapi.Step{{
					Number: 1, Stage: "tool", Request: &agentapi.PromptTrace{Prompt: "Read README", Bytes: 11},
					Tool: "read_file", ToolArguments: `{"path":"README.md"}`, ToolExecuted: true,
					ModelDurationMS: 800, ToolDurationMS: 450,
				}},
			},
			Trajectory: []ToolTrace{{
				Step: 1, Tool: "spawn_agents", Arguments: `{"tasks":["check docs","check code"]}`,
				Status: "completed", Subagents: []SubagentTrace{{
					Index: 1, Task: "check docs", Status: "completed", Route: "inspect",
					Bundles: []string{"workspace"}, DurationMS: 1250, Output: "done",
					Sources: []string{"https://example.test/docs"},
					Steps: []SubagentStep{{
						Step: 1, Tool: "web_search", Arguments: `{"query":"RWKV"}`, Status: "completed",
						Retries: []ToolRetryTrace{{Attempt: 1, MaxAttempts: 5, StatusCode: 429, DelayMS: 2000}},
					}},
				}},
			}},
		},
	}
	conversation.Transcript = []agentapi.ConversationMessage{{Role: "user", Content: "Read README"}}
	if err := store.SaveConversation(conversation); err != nil {
		t.Fatal(err)
	}
	if err := store.SetActiveConversation(workspace, conversation.ID); err != nil {
		t.Fatal(err)
	}
	loaded, err := store.LoadConversation(conversation.ID)
	if err != nil {
		t.Fatal(err)
	}
	if loaded.Title != "Read the project README" || len(loaded.Transcript) != 1 ||
		len(loaded.Messages) != 2 || len(loaded.Messages[1].Trajectory) != 1 ||
		loaded.Messages[1].Trajectory[0].Tool != "spawn_agents" ||
		len(loaded.Messages[1].Trajectory[0].Subagents) != 1 ||
		loaded.Messages[1].Trajectory[0].Subagents[0].Steps[0].Arguments != `{"query":"RWKV"}` ||
		loaded.Messages[1].Trajectory[0].Subagents[0].Steps[0].Retries[0].StatusCode != 429 ||
		loaded.Messages[1].Trajectory[0].Subagents[0].Steps[0].Retries[0].DelayMS != 2000 ||
		loaded.Messages[1].Trajectory[0].Subagents[0].Sources[0] != "https://example.test/docs" ||
		loaded.Messages[1].Trace == nil || loaded.Messages[1].Trace.Route != "inspect" ||
		loaded.Messages[1].Trace.Steps[0].Request.Prompt != "Read README" ||
		loaded.Messages[1].Trace.Steps[0].ModelDurationMS != 800 ||
		loaded.Messages[1].Trace.Steps[0].ToolDurationMS != 450 ||
		!loaded.Messages[1].CreatedAt.Equal(createdAt) {
		t.Fatalf("conversation = %+v", loaded)
	}
	summaries, err := store.ListConversations(workspace)
	if err != nil || len(summaries) != 1 || summaries[0].ID != conversation.ID {
		t.Fatalf("summaries = %+v, error = %v", summaries, err)
	}
	state, err := store.LoadState()
	if err != nil || state.Workspace != workspace || state.ActiveConversations[workspace] != conversation.ID {
		t.Fatalf("state = %+v, error = %v", state, err)
	}
}

func TestConversationIDCannotEscapeDataDirectory(t *testing.T) {
	t.Parallel()
	store := testStore(t)
	if _, err := store.LoadConversation("../settings"); err == nil {
		t.Fatal("path traversal conversation ID was accepted")
	}
	if err := store.DeleteConversation("../settings"); err == nil {
		t.Fatal("path traversal conversation ID was deleted")
	}
}
