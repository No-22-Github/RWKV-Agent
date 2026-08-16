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
	"net/url"
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
	SchemaVersion = 1
	// SettingsSchemaVersion 独立于 State/Conversation 的 SchemaVersion：
	// 设置从"单档 Provider"演进为"多档连接档案 + active"，需要单独的版本与迁移，
	// 而不能连带升 State/Conversation 的版本（否则既有状态/会话会因版本不符而拒读）。
	SettingsSchemaVersion = 2
	maxSettingsBytes      = 4 << 20
	maxStateBytes         = 4 << 20
	maxConversationBytes  = 64 << 20
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
	Provider      agentapi.Config `json:"provider"` // 兼容字段：镜像当前 active 档案的 Config（旧版本读取路径仍可用）
	Providers     []SavedProvider `json:"providers,omitempty"`
	ActiveID      string          `json:"activeProviderId,omitempty"`
	UpdatedAt     time.Time       `json:"updatedAt"`
}

// SavedProvider 是一条可复用的"连接档案/预设"：配置一次、持久化，之后从下拉栏直接切换重连。
type SavedProvider struct {
	ID         string          `json:"id"`
	Label      string          `json:"label"`
	Config     agentapi.Config `json:"config"`
	LastUsedAt time.Time       `json:"lastUsedAt"`
}

type State struct {
	SchemaVersion       int               `json:"schemaVersion"`
	Workspace           string            `json:"workspace,omitempty"`
	RecentWorkspaces    []string          `json:"recentWorkspaces,omitempty"`
	ActiveConversations map[string]string `json:"activeConversations,omitempty"`
	UpdatedAt           time.Time         `json:"updatedAt"`
}

type DisplayMessage struct {
	ID         string           `json:"id"`
	Role       string           `json:"role"`
	Content    string           `json:"content"`
	Meta       string           `json:"meta,omitempty"`
	Trajectory []ToolTrace      `json:"trajectory,omitempty"`
	Trace      *agentapi.Result `json:"trace,omitempty"`
	CreatedAt  time.Time        `json:"createdAt,omitempty"`
}

// ToolTrace is the compact, presentation-safe record retained beside an
// assistant message. Full tool payloads remain in the Harness transcript.
type ToolTrace struct {
	Step      int              `json:"step"`
	Tool      string           `json:"tool"`
	Arguments string           `json:"arguments,omitempty"`
	Status    string           `json:"status"`
	Error     string           `json:"error,omitempty"`
	Retries   []ToolRetryTrace `json:"retries,omitempty"`
	Subagents []SubagentTrace  `json:"subagents,omitempty"`
}

type ToolRetryTrace struct {
	Attempt     int   `json:"attempt"`
	MaxAttempts int   `json:"maxAttempts"`
	StatusCode  int   `json:"statusCode,omitempty"`
	DelayMS     int64 `json:"delayMs"`
}

type SubagentStep struct {
	Step      int              `json:"step"`
	Tool      string           `json:"tool"`
	Arguments string           `json:"arguments,omitempty"`
	Status    string           `json:"status"`
	Error     string           `json:"error,omitempty"`
	Retries   []ToolRetryTrace `json:"retries,omitempty"`
}

type SubagentTrace struct {
	Index      int            `json:"index"`
	Task       string         `json:"task"`
	Status     string         `json:"status"`
	Error      string         `json:"error,omitempty"`
	Route      string         `json:"route,omitempty"`
	Bundles    []string       `json:"bundles,omitempty"`
	DurationMS int64          `json:"durationMs"`
	Output     string         `json:"output,omitempty"`
	Sources    []string       `json:"sources,omitempty"`
	Steps      []SubagentStep `json:"steps,omitempty"`
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
		return Settings{SchemaVersion: SettingsSchemaVersion}, nil
	}
	if err != nil {
		return Settings{}, err
	}
	switch value.SchemaVersion {
	case SettingsSchemaVersion:
		return value, nil
	case 1:
		// 迁移：把旧的单档 Provider 合成为一条连接档案并置为 active。
		return migrateSettingsV1(value), nil
	default:
		return Settings{}, fmt.Errorf("unsupported settings schema version %d", value.SchemaVersion)
	}
}

// migrateSettingsV1 把 v1（单档 Provider）转换为 v2（档案列表 + active）。仅在内存中转换，
// 下次写入时落盘为 v2。
func migrateSettingsV1(value Settings) Settings {
	value.SchemaVersion = SettingsSchemaVersion
	if strings.TrimSpace(value.Provider.Model) == "" {
		value.Providers = nil
		value.ActiveID = ""
		return value
	}
	id, err := randomID()
	if err != nil {
		id = "migrated"
	}
	when := value.UpdatedAt
	if when.IsZero() {
		when = time.Now().UTC()
	}
	entry := SavedProvider{ID: id, Label: providerLabel(value.Provider), Config: value.Provider, LastUsedAt: when}
	value.Providers = []SavedProvider{entry}
	value.ActiveID = id
	return value
}

// SaveActiveProvider upsert 一条连接档案（按 协议+地址+模型 去重）、置为 active 并落盘，返回该档案。
// "连接成功即自动存档"由 appservice.Configure 在成功后调用。
func (s *Store) SaveActiveProvider(config agentapi.Config) (SavedProvider, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	settings, err := s.loadLocked()
	if err != nil {
		return SavedProvider{}, err
	}
	now := time.Now().UTC()
	key := providerKey(config)
	var saved SavedProvider
	found := false
	for i := range settings.Providers {
		if providerKey(settings.Providers[i].Config) == key {
			settings.Providers[i].Config = config
			settings.Providers[i].LastUsedAt = now
			if strings.TrimSpace(settings.Providers[i].Label) == "" {
				settings.Providers[i].Label = providerLabel(config)
			}
			saved = settings.Providers[i]
			found = true
			break
		}
	}
	if !found {
		id, idErr := randomID()
		if idErr != nil {
			return SavedProvider{}, idErr
		}
		saved = SavedProvider{ID: id, Label: providerLabel(config), Config: config, LastUsedAt: now}
		settings.Providers = append(settings.Providers, saved)
	}
	settings.ActiveID = saved.ID
	settings.Provider = config
	if err := s.writeSettingsLocked(settings); err != nil {
		return SavedProvider{}, err
	}
	return saved, nil
}

// RemoveProvider 删除一条档案；若删的是 active，则把 active 指向最近使用的一条（无则清空）。
func (s *Store) RemoveProvider(id string) (Settings, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	settings, err := s.loadLocked()
	if err != nil {
		return Settings{}, err
	}
	filtered := settings.Providers[:0:0]
	for _, entry := range settings.Providers {
		if entry.ID != id {
			filtered = append(filtered, entry)
		}
	}
	settings.Providers = filtered
	if settings.ActiveID == id {
		settings.ActiveID = ""
		settings.Provider = agentapi.Config{}
		var latest *SavedProvider
		for i := range settings.Providers {
			if latest == nil || settings.Providers[i].LastUsedAt.After(latest.LastUsedAt) {
				latest = &settings.Providers[i]
			}
		}
		if latest != nil {
			settings.ActiveID = latest.ID
			settings.Provider = latest.Config
		}
	}
	if err := s.writeSettingsLocked(settings); err != nil {
		return Settings{}, err
	}
	return settings, nil
}

// SaveSettings 保留旧签名：等价于"保存并置为 active"，供既有调用方/测试使用。
func (s *Store) SaveSettings(config agentapi.Config) error {
	_, err := s.SaveActiveProvider(config)
	return err
}

func (s *Store) loadLocked() (Settings, error) {
	var value Settings
	err := readJSON(s.paths.ConfigFile, maxSettingsBytes, &value)
	if errors.Is(err, os.ErrNotExist) {
		return Settings{SchemaVersion: SettingsSchemaVersion}, nil
	}
	if err != nil {
		return Settings{}, err
	}
	switch value.SchemaVersion {
	case SettingsSchemaVersion:
		return value, nil
	case 1:
		return migrateSettingsV1(value), nil
	default:
		return Settings{}, fmt.Errorf("unsupported settings schema version %d", value.SchemaVersion)
	}
}

func (s *Store) writeSettingsLocked(settings Settings) error {
	settings.SchemaVersion = SettingsSchemaVersion
	settings.UpdatedAt = time.Now().UTC()
	return writeJSON(s.paths.ConfigFile, settings)
}

// providerKey 是去重键：同一 协议+地址(小写)+模型 视为同一档案。
func providerKey(config agentapi.Config) string {
	return strings.ToLower(strings.TrimSpace(string(config.Provider))) + "|" +
		strings.ToLower(strings.TrimSpace(config.Endpoint)) + "|" +
		strings.TrimSpace(config.Model)
}

// providerLabel 派生一个可读标签：远端 = "模型 · 主机"，本地退回模型路径末段。
func providerLabel(config agentapi.Config) string {
	model := strings.TrimSpace(config.Model)
	if config.Provider == agentapi.ProviderLocal {
		if model == "" {
			return "本地模型"
		}
		if idx := strings.LastIndexAny(model, "/\\"); idx >= 0 && idx+1 < len(model) {
			return model[idx+1:]
		}
		return model
	}
	host := ""
	if endpoint := strings.TrimSpace(config.Endpoint); endpoint != "" {
		if parsed, err := url.Parse(endpoint); err == nil && parsed.Host != "" {
			host = parsed.Host
		} else {
			host = endpoint
		}
	}
	switch {
	case model != "" && host != "":
		return model + " · " + host
	case model != "":
		return model
	case host != "":
		return host
	default:
		return "远端连接"
	}
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
