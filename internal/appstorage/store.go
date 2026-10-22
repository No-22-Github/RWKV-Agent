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
	// Agent 是所有连接共用的 Agent 设置；nil 表示还没从旧档案迁移过（见 AgentSettings）。
	Agent     *AgentSettings `json:"agent,omitempty"`
	UpdatedAt time.Time      `json:"updatedAt"`
}

// AgentSettingsRevision 是 AgentSettings 当前的版本：2 起生成参数、工具开关与提示词
// 也从档案搬进了这里。低于它的设置第一次读取时从旧档案补齐（见 AgentSettings）。
const AgentSettingsRevision = 2

// AgentSettings 是所有连接档案共用的 Agent 设置：和用哪个端点无关的一切——
// 采样、预算、工具开关与调度、提示词，以及搜索与抓取的 API Key、搜索路由、天气数据源。
// 只存一份，不再复制进每个档案；档案只剩连接本身和跟着端点走的 State、MiSS、对话格式。
type AgentSettings struct {
	// Revision 记录这份设置迁移到了哪一版；见 AgentSettingsRevision。
	Revision int `json:"revision,omitempty"`

	Temperature       float64 `json:"temperature"`
	TopK              int     `json:"topK"`
	TopP              float64 `json:"topP"`
	PresencePenalty   float64 `json:"presencePenalty"`
	FrequencyPenalty  float64 `json:"frequencyPenalty"`
	PenaltyDecay      float64 `json:"penaltyDecay"`
	MaxSteps          int     `json:"maxSteps,omitempty"`
	MaxTokens         int     `json:"maxTokens,omitempty"`
	DecisionMaxTokens int     `json:"decisionMaxTokens,omitempty"`

	EnableWeb              bool `json:"enableWeb"`
	EnableWeather          bool `json:"enableWeather"`
	EnableBash             bool `json:"enableBash"`
	ProgressiveTools       bool `json:"progressiveTools"`
	EnableSubagents        bool `json:"enableSubagents"`
	SubagentMaxParallel    int  `json:"subagentMaxParallel,omitempty"`
	SubagentMaxSteps       int  `json:"subagentMaxSteps,omitempty"`
	SubagentTimeoutSeconds int  `json:"subagentTimeoutSeconds,omitempty"`

	TaskControl       string `json:"taskControl,omitempty"`
	InjectSessionTime bool   `json:"injectSessionTime"`

	BraveAPIKey       string `json:"braveApiKey,omitempty"`
	TavilyAPIKey      string `json:"tavilyApiKey,omitempty"`
	DeepSeekWebAPIKey string `json:"deepseekWebApiKey,omitempty"`
	// WebSearchBackend："" 或 auto（中文先 DeepSeek，其余先 Brave）、deepseek、brave。
	WebSearchBackend string `json:"webSearchBackend,omitempty"`
	// WebFetchBackend："" 或 tavily（先 Tavily）、deepseek（先 DeepSeek）；另一个给读不到的页面兜底。
	WebFetchBackend string `json:"webFetchBackend,omitempty"`
	// WeatherBackend：open-meteo 或 wttr；空按 open-meteo。
	WeatherBackend string `json:"weatherBackend,omitempty"`
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
	// StateUploads remembers which local file produced each uploaded state, so
	// a state wiped by a deployment restart can be re-uploaded in one step.
	StateUploads []StateUpload `json:"stateUploads,omitempty"`
	// AdapterRegistrations remembers how each MiSS adapter was registered, so
	// one wiped by a deployment restart can be registered again in one step.
	AdapterRegistrations []AdapterRegistration `json:"adapterRegistrations,omitempty"`
	UpdatedAt            time.Time             `json:"updatedAt"`
}

// StateUpload links a server-assigned state_id to the local file it came from.
type StateUpload struct {
	Server     string    `json:"server"`
	StateID    string    `json:"stateId"`
	Path       string    `json:"path"`
	SHA256     string    `json:"sha256"`
	SizeBytes  int64     `json:"sizeBytes"`
	UploadedAt time.Time `json:"uploadedAt"`
}

// AdapterRegistration links a registered MiSS adapter ID to the local file
// this machine uploaded for it.
type AdapterRegistration struct {
	Server       string    `json:"server"`
	AdapterID    string    `json:"adapterId"`
	Version      string    `json:"version"`
	LocalPath    string    `json:"localPath"`
	RegisteredAt time.Time `json:"registeredAt"`
}

// maxStateUploads bounds the registry; the oldest records are dropped first.
const maxStateUploads = 200

// FileArtifact is a read-only snapshot attached to a response. It never
// restores pending filesystem writes when a conversation is reopened.
type FileArtifact struct {
	Change agentapi.FileChange `json:"change"`
	Status string              `json:"status"`
}

type DisplayMessage struct {
	Files      []FileArtifact   `json:"files,omitempty"`
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
	SchemaVersion int       `json:"schemaVersion"`
	ID            string    `json:"id"`
	Workspace     string    `json:"workspace"`
	Title         string    `json:"title"`
	CreatedAt     time.Time `json:"createdAt"`
	UpdatedAt     time.Time `json:"updatedAt"`
	// PinnedAt marks sidebar-pinned conversations; nil means unpinned.
	PinnedAt   *time.Time                     `json:"pinnedAt,omitempty"`
	Messages   []DisplayMessage               `json:"messages"`
	Transcript []agentapi.ConversationMessage `json:"transcript"`
}

type Summary struct {
	ID        string    `json:"id"`
	Workspace string    `json:"workspace"`
	Title     string    `json:"title"`
	UpdatedAt time.Time `json:"updatedAt"`
	Pinned    bool      `json:"pinned"`
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

// LoadSettings 读取当前连接档案设置；文件缺失返回零值 v2，v1 旧格式在内存中迁移。
func (s *Store) LoadSettings() (Settings, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.loadLocked()
}

// AgentSettings 返回共用的 Agent 设置。旧版本把这些值存在各个档案里：第一次读取时
// 从档案里收集并落盘，之后以这份为准。Key 与数据源逐项取第一个非空值（运行档案优先）；
// 生成参数、工具与提示词整组取自运行档案（没有就取列表第一个，一个档案都没有用新连接默认值）。
func (s *Store) AgentSettings() (AgentSettings, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	settings, err := s.loadLocked()
	if err != nil {
		return AgentSettings{}, err
	}
	if settings.Agent != nil && settings.Agent.Revision >= AgentSettingsRevision {
		return *settings.Agent, nil
	}
	var migrated AgentSettings
	if settings.Agent != nil {
		migrated = *settings.Agent
	} else {
		migrated = collectAgentSettings(settings)
	}
	applyBehavior(&migrated, behaviorSource(settings))
	migrated.Revision = AgentSettingsRevision
	settings.Agent = &migrated
	if err := s.writeSettingsLocked(settings); err != nil {
		return AgentSettings{}, err
	}
	return migrated, nil
}

// behaviorSource 是迁移生成参数与工具开关时取值的那份配置：用户最近实际在用的档案。
func behaviorSource(settings Settings) agentapi.Config {
	for _, entry := range settings.Providers {
		if entry.ID == settings.ActiveID {
			return entry.Config
		}
	}
	if len(settings.Providers) > 0 {
		return settings.Providers[0].Config
	}
	return agentapi.NewConfigDefaults()
}

// applyBehavior 把一份配置里的生成参数、工具开关与提示词抄进共用设置。
func applyBehavior(value *AgentSettings, config agentapi.Config) {
	value.Temperature, value.TopK, value.TopP = config.Temperature, config.TopK, config.TopP
	value.PresencePenalty, value.FrequencyPenalty, value.PenaltyDecay = config.PresencePenalty, config.FrequencyPenalty, config.PenaltyDecay
	value.MaxSteps, value.MaxTokens, value.DecisionMaxTokens = config.MaxSteps, config.MaxTokens, config.DecisionMaxTokens
	value.EnableWeb = config.EnableWeb
	value.EnableWeather = strings.TrimSpace(config.WeatherBackend) != ""
	value.EnableBash = config.EnableBash
	value.ProgressiveTools = config.ProgressiveTools != nil && *config.ProgressiveTools
	value.EnableSubagents = config.EnableSubagents
	value.SubagentMaxParallel, value.SubagentMaxSteps, value.SubagentTimeoutSeconds = config.SubagentMaxParallel, config.SubagentMaxSteps, config.SubagentTimeoutSeconds
	value.TaskControl = config.TaskControl
	value.InjectSessionTime = config.InjectSessionTime
}

// SaveAgentSettings 覆盖保存共用的 Agent 设置。
func (s *Store) SaveAgentSettings(value AgentSettings) error {
	s.mu.Lock()
	defer s.mu.Unlock()
	settings, err := s.loadLocked()
	if err != nil {
		return err
	}
	settings.Agent = &value
	return s.writeSettingsLocked(settings)
}

func collectAgentSettings(settings Settings) AgentSettings {
	ordered := make([]agentapi.Config, 0, len(settings.Providers))
	for _, entry := range settings.Providers {
		if entry.ID == settings.ActiveID {
			ordered = append([]agentapi.Config{entry.Config}, ordered...)
		} else {
			ordered = append(ordered, entry.Config)
		}
	}
	var value AgentSettings
	pick := func(target *string, read func(agentapi.Config) string) {
		for _, config := range ordered {
			if v := strings.TrimSpace(read(config)); v != "" {
				*target = v
				return
			}
		}
	}
	pick(&value.BraveAPIKey, func(c agentapi.Config) string { return c.BraveAPIKey })
	pick(&value.TavilyAPIKey, func(c agentapi.Config) string { return c.TavilyAPIKey })
	pick(&value.DeepSeekWebAPIKey, func(c agentapi.Config) string { return c.DeepSeekWebAPIKey })
	pick(&value.WebSearchBackend, func(c agentapi.Config) string { return c.WebSearchBackend })
	pick(&value.WebFetchBackend, func(c agentapi.Config) string { return c.WebFetchBackend })
	pick(&value.WeatherBackend, func(c agentapi.Config) string { return c.WeatherBackend })
	return value
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

// SaveProvider 保存一条连接档案。传入 id 时按档案更新，即使地址或模型发生变化也不会复制旧档案；
// id 为空时按 协议+地址+模型 去重。activate 只控制是否把该档案设为下次启动使用的 active 档案。
func (s *Store) SaveProvider(id string, label string, config agentapi.Config, activate bool) (SavedProvider, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	settings, err := s.loadLocked()
	if err != nil {
		return SavedProvider{}, err
	}
	now := time.Now().UTC()
	key := providerKey(config)
	target := -1
	cleanID := strings.TrimSpace(id)
	if cleanID != "" {
		for i := range settings.Providers {
			if settings.Providers[i].ID == cleanID {
				target = i
				break
			}
		}
		if target < 0 {
			return SavedProvider{}, fmt.Errorf("provider profile %q not found", cleanID)
		}
	}
	for i := range settings.Providers {
		if providerKey(settings.Providers[i].Config) != key {
			continue
		}
		if target < 0 {
			target = i
			break
		}
		if i != target {
			return SavedProvider{}, fmt.Errorf("another provider profile already uses this provider, endpoint, and model")
		}
	}
	cleanLabel := strings.TrimSpace(label)
	if cleanLabel == "" {
		cleanLabel = providerLabel(config)
	}
	if target < 0 {
		id, idErr := randomID()
		if idErr != nil {
			return SavedProvider{}, idErr
		}
		settings.Providers = append(settings.Providers, SavedProvider{
			ID: id, Label: cleanLabel, Config: config, LastUsedAt: now,
		})
		target = len(settings.Providers) - 1
	} else {
		settings.Providers[target].Label = cleanLabel
		settings.Providers[target].Config = config
		if activate || settings.Providers[target].LastUsedAt.IsZero() {
			settings.Providers[target].LastUsedAt = now
		}
	}
	saved := settings.Providers[target]
	if activate {
		settings.ActiveID = saved.ID
		settings.Provider = saved.Config
	} else if settings.ActiveID == saved.ID {
		settings.Provider = saved.Config
	}
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

// RecordStateUpload registers (or refreshes) one upload record.
func (s *Store) RecordStateUpload(record StateUpload) error {
	value, err := s.LoadState()
	if err != nil {
		return err
	}
	kept := []StateUpload{record}
	for _, existing := range value.StateUploads {
		if existing.Server == record.Server && existing.StateID == record.StateID {
			continue
		}
		kept = append(kept, existing)
	}
	if len(kept) > maxStateUploads {
		kept = kept[:maxStateUploads]
	}
	value.StateUploads = kept
	return s.SaveState(value)
}

// ForgetStateUpload drops the record for a state deleted from the server.
func (s *Store) ForgetStateUpload(server, stateID string) error {
	value, err := s.LoadState()
	if err != nil {
		return err
	}
	kept := value.StateUploads[:0]
	for _, existing := range value.StateUploads {
		if existing.Server != server || existing.StateID != stateID {
			kept = append(kept, existing)
		}
	}
	value.StateUploads = kept
	return s.SaveState(value)
}

// StateUploads returns the upload records for one server, newest first.
func (s *Store) StateUploads(server string) ([]StateUpload, error) {
	value, err := s.LoadState()
	if err != nil {
		return nil, err
	}
	var records []StateUpload
	for _, record := range value.StateUploads {
		if record.Server == server {
			records = append(records, record)
		}
	}
	return records, nil
}

// RecordAdapterRegistration registers (or refreshes) the record for one
// adapter ID; a newer registration of the same ID replaces the old record.
func (s *Store) RecordAdapterRegistration(record AdapterRegistration) error {
	value, err := s.LoadState()
	if err != nil {
		return err
	}
	kept := []AdapterRegistration{record}
	for _, existing := range value.AdapterRegistrations {
		if existing.Server == record.Server && existing.AdapterID == record.AdapterID {
			continue
		}
		kept = append(kept, existing)
	}
	if len(kept) > maxStateUploads {
		kept = kept[:maxStateUploads]
	}
	value.AdapterRegistrations = kept
	return s.SaveState(value)
}

// ForgetAdapterRegistration drops the record for an adapter deleted from the
// server.
func (s *Store) ForgetAdapterRegistration(server, adapterID string) error {
	value, err := s.LoadState()
	if err != nil {
		return err
	}
	kept := value.AdapterRegistrations[:0]
	for _, existing := range value.AdapterRegistrations {
		if existing.Server != server || existing.AdapterID != adapterID {
			kept = append(kept, existing)
		}
	}
	value.AdapterRegistrations = kept
	return s.SaveState(value)
}

// AdapterRegistrations returns the registration records for one server,
// newest first.
func (s *Store) AdapterRegistrations(server string) ([]AdapterRegistration, error) {
	value, err := s.LoadState()
	if err != nil {
		return nil, err
	}
	var records []AdapterRegistration
	for _, record := range value.AdapterRegistrations {
		if record.Server == server {
			records = append(records, record)
		}
	}
	return records, nil
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
		if loadErr != nil || !SamePath(value.Workspace, workspace) {
			continue
		}
		result = append(result, Summary{
			ID: value.ID, Workspace: value.Workspace, Title: value.Title, UpdatedAt: value.UpdatedAt,
			Pinned: value.PinnedAt != nil,
		})
	}
	sort.Slice(result, func(i, j int) bool {
		if result[i].Pinned != result[j].Pinned {
			return result[i].Pinned
		}
		return result[i].UpdatedAt.After(result[j].UpdatedAt)
	})
	return result, nil
}

// RenameConversation updates the display title without touching UpdatedAt.
func (s *Store) RenameConversation(id, title string) error {
	if !validID(id) {
		return fmt.Errorf("invalid conversation ID")
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	var value Conversation
	if err := readJSON(s.conversationPath(id), maxConversationBytes, &value); err != nil {
		return err
	}
	if value.SchemaVersion != SchemaVersion || value.ID != id {
		return fmt.Errorf("invalid conversation document")
	}
	value.Title = cleanTitle(title)
	return writeJSON(s.conversationPath(id), value)
}

// SetConversationPinned pins or unpins a conversation without touching UpdatedAt.
func (s *Store) SetConversationPinned(id string, pinned bool) error {
	if !validID(id) {
		return fmt.Errorf("invalid conversation ID")
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	var value Conversation
	if err := readJSON(s.conversationPath(id), maxConversationBytes, &value); err != nil {
		return err
	}
	if value.SchemaVersion != SchemaVersion || value.ID != id {
		return fmt.Errorf("invalid conversation document")
	}
	if pinned {
		now := time.Now().UTC()
		value.PinnedAt = &now
	} else {
		value.PinnedAt = nil
	}
	return writeJSON(s.conversationPath(id), value)
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
		if candidate == "" || SamePath(candidate, value) {
			continue
		}
		result = append(result, candidate)
		if len(result) == limit {
			break
		}
	}
	return result
}

// SamePath compares two filesystem paths after cleaning, case-insensitively on Windows.
func SamePath(left, right string) bool {
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
