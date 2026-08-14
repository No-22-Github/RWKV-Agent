package appstorage

import (
	"os"
	"path/filepath"
	"runtime"
	"testing"

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
	conversation.Messages = []DisplayMessage{
		{ID: "m1", Role: "user", Content: "Read README"},
		{
			ID: "m2", Role: "assistant", Content: "Done",
			Trajectory: []ToolTrace{{Step: 1, Tool: "read_file", Status: "completed"}},
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
		loaded.Messages[1].Trajectory[0].Tool != "read_file" {
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
