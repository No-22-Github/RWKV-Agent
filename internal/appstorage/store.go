// Package appstorage persists desktop application settings, state, and
// conversations without coupling them to the inference runtime.
package appstorage

import (
	"crypto/rand"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"
	"sync"
	"time"
	"unicode/utf8"

	"github.com/adrg/xdg"
	agentapi "github.com/no22/RWKV-Agent/api"
)

const (
	SchemaVersion        = 1
	maxSettingsBytes     = 4 << 20
	maxStateBytes        = 4 << 20
	maxConversationBytes = 64 << 20
)

type Paths struct {
	ConfigFile       string `json:"configFile"`
	DataDirectory    string `json:"dataDirectory"`
	StateFile        string `json:"stateFile"`
	CacheDirectory   string `json:"cacheDirectory"`
	ConversationData string `json:"conversationData"`
}

func DefaultPaths() Paths {
	dataDirectory := filepath.Join(xdg.DataHome, "RWKV-Agent")
	return Paths{
		ConfigFile:       filepath.Join(xdg.ConfigHome, "RWKV-Agent", "settings.json"),
		DataDirectory:    dataDirectory,
		StateFile:        filepath.Join(xdg.StateHome, "RWKV-Agent", "app-state.json"),
		CacheDirectory:   filepath.Join(xdg.CacheHome, "RWKV-Agent"),
		ConversationData: filepath.Join(dataDirectory, "conversations"),
	}
}

type Settings struct {
	SchemaVersion int             `json:"schemaVersion"`
	Provider      agentapi.Config `json:"provider"`
	UpdatedAt     time.Time       `json:"updatedAt"`
}

type State struct {
	SchemaVersion       int               `json:"schemaVersion"`
	Workspace           string            `json:"workspace,omitempty"`
	RecentWorkspaces    []string          `json:"recentWorkspaces,omitempty"`
	ActiveConversations map[string]string `json:"activeConversations,omitempty"`
	UpdatedAt           time.Time         `json:"updatedAt"`
}

type DisplayMessage struct {
	ID         string      `json:"id"`
	Role       string      `json:"role"`
	Content    string      `json:"content"`
	Meta       string      `json:"meta,omitempty"`
	Trajectory []ToolTrace `json:"trajectory,omitempty"`
}

// ToolTrace is the compact, presentation-safe record retained beside an
// assistant message. Full tool payloads remain in the Harness transcript.
type ToolTrace struct {
	Step   int    `json:"step"`
	Tool   string `json:"tool"`
	Status string `json:"status"`
	Error  string `json:"error,omitempty"`
}

type Conversation struct {
	SchemaVersion int                            `json:"schemaVersion"`
	ID            string                         `json:"id"`
	Workspace     string                         `json:"workspace"`
	Title         string                         `json:"title"`
	CreatedAt     time.Time                      `json:"createdAt"`
	UpdatedAt     time.Time                      `json:"updatedAt"`
	Messages      []DisplayMessage               `json:"messages"`
	Transcript    []agentapi.ConversationMessage `json:"transcript"`
}

type Summary struct {
	ID        string    `json:"id"`
	Workspace string    `json:"workspace"`
	Title     string    `json:"title"`
	UpdatedAt time.Time `json:"updatedAt"`
}

type Store struct {
	paths Paths
	mu    sync.Mutex
}

func New(paths Paths) *Store { return &Store{paths: paths} }

func NewDefault() *Store { return New(DefaultPaths()) }

func (s *Store) Paths() Paths { return s.paths }

// Prepare creates the application-owned configuration, data, state, and cache
// directories before the frontend starts using them.
func (s *Store) Prepare() error {
	directories := []string{
		filepath.Dir(s.paths.ConfigFile),
		s.paths.DataDirectory,
		filepath.Dir(s.paths.StateFile),
		s.paths.CacheDirectory,
		s.paths.ConversationData,
	}
	for _, directory := range directories {
		if err := os.MkdirAll(directory, 0o700); err != nil {
			return err
		}
	}
	return nil
}

func (s *Store) LoadSettings() (Settings, error) {
	var value Settings
	err := readJSON(s.paths.ConfigFile, maxSettingsBytes, &value)
	if errors.Is(err, os.ErrNotExist) {
		return Settings{SchemaVersion: SchemaVersion}, nil
	}
	if err != nil {
		return Settings{}, err
	}
	if value.SchemaVersion != SchemaVersion {
		return Settings{}, fmt.Errorf("unsupported settings schema version %d", value.SchemaVersion)
	}
	return value, nil
}

func (s *Store) SaveSettings(config agentapi.Config) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	return writeJSON(s.paths.ConfigFile, Settings{
		SchemaVersion: SchemaVersion, Provider: config, UpdatedAt: time.Now().UTC(),
	})
}

func (s *Store) LoadState() (State, error) {
	var value State
	err := readJSON(s.paths.StateFile, maxStateBytes, &value)
	if errors.Is(err, os.ErrNotExist) {
		return defaultState(), nil
	}
	if err != nil {
		return State{}, err
	}
	if value.SchemaVersion != SchemaVersion {
		return State{}, fmt.Errorf("unsupported app state schema version %d", value.SchemaVersion)
	}
	if value.ActiveConversations == nil {
		value.ActiveConversations = make(map[string]string)
	} else if runtime.GOOS == "windows" {
		normalized := make(map[string]string, len(value.ActiveConversations))
		for workspace, id := range value.ActiveConversations {
			normalized[pathKey(workspace)] = id
		}
		value.ActiveConversations = normalized
	}
	return value, nil
}

func (s *Store) SaveState(value State) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	value.SchemaVersion = SchemaVersion
	value.UpdatedAt = time.Now().UTC()
	if value.ActiveConversations == nil {
		value.ActiveConversations = make(map[string]string)
	}
	return writeJSON(s.paths.StateFile, value)
}

func (s *Store) RememberWorkspace(workspace string) (State, error) {
	value, err := s.LoadState()
	if err != nil {
		return State{}, err
	}
	workspace = filepath.Clean(workspace)
	value.Workspace = workspace
	value.RecentWorkspaces = prependUniquePath(value.RecentWorkspaces, workspace, 12)
	return value, s.SaveState(value)
}

func (s *Store) SetActiveConversation(workspace, id string) error {
	value, err := s.LoadState()
	if err != nil {
		return err
	}
	if id == "" {
		delete(value.ActiveConversations, pathKey(workspace))
	} else {
		value.ActiveConversations[pathKey(workspace)] = id
	}
	return s.SaveState(value)
}

func (s *Store) ActiveConversation(workspace string) (string, error) {
	value, err := s.LoadState()
	if err != nil {
		return "", err
	}
	return value.ActiveConversations[pathKey(workspace)], nil
}

func NewConversation(workspace, title string) (Conversation, error) {
	id, err := randomID()
	if err != nil {
		return Conversation{}, err
	}
	now := time.Now().UTC()
	return Conversation{
		SchemaVersion: SchemaVersion,
		ID:            id, Workspace: filepath.Clean(workspace), Title: cleanTitle(title),
		CreatedAt: now, UpdatedAt: now,
	}, nil
}

func (s *Store) SaveConversation(value Conversation) error {
	if !validID(value.ID) {
		return fmt.Errorf("invalid conversation ID")
	}
	if strings.TrimSpace(value.Workspace) == "" {
		return fmt.Errorf("conversation workspace is required")
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	value.SchemaVersion = SchemaVersion
	value.Workspace = filepath.Clean(value.Workspace)
	value.Title = cleanTitle(value.Title)
	if value.CreatedAt.IsZero() {
		value.CreatedAt = time.Now().UTC()
	}
	value.UpdatedAt = time.Now().UTC()
	return writeJSON(s.conversationPath(value.ID), value)
}

func (s *Store) LoadConversation(id string) (Conversation, error) {
	if !validID(id) {
		return Conversation{}, fmt.Errorf("invalid conversation ID")
	}
	var value Conversation
	if err := readJSON(s.conversationPath(id), maxConversationBytes, &value); err != nil {
		return Conversation{}, err
	}
	if value.SchemaVersion != SchemaVersion || value.ID != id {
		return Conversation{}, fmt.Errorf("invalid conversation document")
	}
	return value, nil
}

func (s *Store) ListConversations(workspace string) ([]Summary, error) {
	entries, err := os.ReadDir(s.paths.ConversationData)
	if errors.Is(err, os.ErrNotExist) {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	workspace = filepath.Clean(workspace)
	result := make([]Summary, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".json" {
			continue
		}
		id := strings.TrimSuffix(entry.Name(), ".json")
		value, loadErr := s.LoadConversation(id)
		if loadErr != nil || !samePath(value.Workspace, workspace) {
			continue
		}
		result = append(result, Summary{
			ID: value.ID, Workspace: value.Workspace, Title: value.Title, UpdatedAt: value.UpdatedAt,
		})
	}
	sort.Slice(result, func(i, j int) bool { return result[i].UpdatedAt.After(result[j].UpdatedAt) })
	return result, nil
}

func (s *Store) DeleteConversation(id string) error {
	if !validID(id) {
		return fmt.Errorf("invalid conversation ID")
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	err := os.Remove(s.conversationPath(id))
	if errors.Is(err, os.ErrNotExist) {
		return nil
	}
	return err
}

func (s *Store) conversationPath(id string) string {
	return filepath.Join(s.paths.ConversationData, id+".json")
}

func defaultState() State {
	return State{SchemaVersion: SchemaVersion, ActiveConversations: make(map[string]string)}
}

func readJSON(path string, limit int64, target any) error {
	handle, err := os.Open(path)
	if err != nil {
		return err
	}
	defer handle.Close()
	info, err := handle.Stat()
	if err != nil {
		return err
	}
	if info.Size() > limit {
		return fmt.Errorf("%s exceeds size limit", path)
	}
	decoder := json.NewDecoder(io.LimitReader(handle, limit+1))
	if err := decoder.Decode(target); err != nil {
		return fmt.Errorf("decode %s: %w", path, err)
	}
	var extra any
	if err := decoder.Decode(&extra); !errors.Is(err, io.EOF) {
		if err == nil {
			return fmt.Errorf("decode %s: multiple JSON values", path)
		}
		return fmt.Errorf("decode %s: %w", path, err)
	}
	return nil
}

func writeJSON(path string, value any) error {
	data, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	data = append(data, '\n')
	directory := filepath.Dir(path)
	if err := os.MkdirAll(directory, 0o700); err != nil {
		return err
	}
	temporary, err := os.CreateTemp(directory, ".write-*")
	if err != nil {
		return err
	}
	temporaryPath := temporary.Name()
	cleanup := true
	defer func() {
		_ = temporary.Close()
		if cleanup {
			_ = os.Remove(temporaryPath)
		}
	}()
	if err := temporary.Chmod(0o600); err != nil {
		return err
	}
	if _, err := temporary.Write(data); err != nil {
		return err
	}
	if err := temporary.Sync(); err != nil {
		return err
	}
	if err := temporary.Close(); err != nil {
		return err
	}
	if err := os.Rename(temporaryPath, path); err != nil {
		return err
	}
	cleanup = false
	return os.Chmod(path, 0o600)
}

func randomID() (string, error) {
	buffer := make([]byte, 16)
	if _, err := rand.Read(buffer); err != nil {
		return "", err
	}
	return hex.EncodeToString(buffer), nil
}

func validID(value string) bool {
	if len(value) != 32 {
		return false
	}
	_, err := hex.DecodeString(value)
	return err == nil
}

func cleanTitle(value string) string {
	value = strings.Join(strings.Fields(value), " ")
	if value == "" {
		return "新会话"
	}
	for utf8.RuneCountInString(value) > 60 {
		_, size := utf8.DecodeLastRuneInString(value)
		value = value[:len(value)-size]
	}
	return value
}

func prependUniquePath(values []string, value string, limit int) []string {
	result := []string{value}
	for _, candidate := range values {
		if candidate == "" || samePath(candidate, value) {
			continue
		}
		result = append(result, candidate)
		if len(result) == limit {
			break
		}
	}
	return result
}

func samePath(left, right string) bool {
	left = filepath.Clean(left)
	right = filepath.Clean(right)
	if runtime.GOOS == "windows" {
		return strings.EqualFold(left, right)
	}
	return left == right
}

func pathKey(value string) string {
	value = filepath.Clean(value)
	if runtime.GOOS == "windows" {
		return strings.ToLower(value)
	}
	return value
}
