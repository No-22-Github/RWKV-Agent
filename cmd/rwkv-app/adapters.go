package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"strings"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
)

const adapterUploadProgressEvent = "adapter:upload-progress"

// AdapterEntry is one MiSS adapter ID on the deployment, joined with how this
// machine registered it, if it did. Several content versions can share an ID;
// generations bind the newest one.
type AdapterEntry struct {
	ID string `json:"id"`
	// Version is the version this machine registered last when the server
	// still holds it, otherwise the only version listed. It is empty when the
	// server holds several versions this machine cannot tell apart.
	Version  string  `json:"version,omitempty"`
	Versions int     `json:"versions"`
	Rank     int     `json:"rank,omitempty"`
	Alpha    float64 `json:"alpha,omitempty"`
	// ServerPath / LocalPath say where the registration came from (see
	// appstorage.AdapterRegistration); LocalAvailable reports whether the
	// local file still exists for a re-upload.
	ServerPath     string `json:"serverPath,omitempty"`
	LocalPath      string `json:"localPath,omitempty"`
	LocalAvailable bool   `json:"localAvailable,omitempty"`
}

// AdapterListing is the server list plus local records whose adapter the
// server no longer holds (registrations live in RAM and die with a restart).
type AdapterListing struct {
	Adapters []AdapterEntry `json:"adapters"`
	Missing  []AdapterEntry `json:"missing"`
}

// AdapterUploadProgress is emitted while an adapter file is being uploaded.
type AdapterUploadProgress struct {
	Path  string `json:"path"`
	Sent  int64  `json:"sent"`
	Total int64  `json:"total"`
}

// ChooseAdapterFile opens the native file picker for a MiSS package
// (adapter-final.pth or a checkpoint's training.pth).
func (s *AppService) ChooseAdapterFile() (string, error) {
	s.mu.Lock()
	app := s.app
	s.mu.Unlock()
	if app == nil || app.Dialog == nil {
		return "", fmt.Errorf("桌面窗口不可用，请直接填写适配器文件路径")
	}
	dialog := app.Dialog.OpenFile().
		CanChooseFiles(true).
		CanChooseDirectories(false).
		SetTitle("选择 MiSS 适配器文件")
	dialog.AddFilter("MiSS 适配器", "*.pth")
	dialog.AddFilter("所有文件", "*")
	return dialog.PromptForSingleSelection()
}

// ListAdapters lists the deployment's adapters and joins local records.
func (s *AppService) ListAdapters(ctx context.Context, config agentapi.Config) (AdapterListing, error) {
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	adapters, err := s.currentService().ListAdapters(ctx, config)
	if err != nil {
		return AdapterListing{}, adapterError(err)
	}
	records, err := s.storage.AdapterRegistrations(stateServerKey(config.Endpoint))
	if err != nil {
		return AdapterListing{}, err
	}
	return joinAdapters(adapters, records), nil
}

// RegisterAdapter registers path under id. upload=false hands path to the
// server as a path on the inference host; upload=true sends the local file.
// Re-registering an existing ID adds a version that becomes its default.
func (s *AppService) RegisterAdapter(ctx context.Context, config agentapi.Config, id, path string, upload bool) (AdapterEntry, error) {
	id, path = strings.TrimSpace(id), strings.TrimSpace(path)
	if id == "" {
		return AdapterEntry{}, fmt.Errorf("请填写适配器 ID")
	}
	if path == "" {
		return AdapterEntry{}, fmt.Errorf("请填写适配器文件路径")
	}
	record := appstorage.AdapterRegistration{Server: stateServerKey(config.Endpoint), AdapterID: id}
	var version string
	var err error
	if upload {
		info, statErr := os.Stat(path)
		if statErr != nil {
			return AdapterEntry{}, fmt.Errorf("读取适配器文件失败: %w", statErr)
		}
		if info.IsDir() {
			return AdapterEntry{}, fmt.Errorf("%s 是目录，请选择 .pth 文件", path)
		}
		// Uploads share the state-upload lock: concurrent large uploads have
		// knocked the shared deployment over before.
		s.stateUpload.Lock()
		defer s.stateUpload.Unlock()
		uploadCtx, cancel := context.WithTimeout(ctx, 10*time.Minute)
		defer cancel()
		var lastPercent int64 = -1
		version, err = s.currentService().UploadAdapter(uploadCtx, config, id, path, func(sent, total int64) {
			percent := int64(100)
			if total > 0 {
				percent = sent * 100 / total
			}
			if percent == lastPercent {
				return
			}
			lastPercent = percent
			s.emit(adapterUploadProgressEvent, AdapterUploadProgress{Path: path, Sent: sent, Total: total})
		})
		record.LocalPath = path
	} else {
		registerCtx, cancel := context.WithTimeout(ctx, 2*time.Minute)
		defer cancel()
		version, err = s.currentService().RegisterAdapterPath(registerCtx, config, id, path)
		record.ServerPath = path
	}
	if err != nil {
		return AdapterEntry{}, adapterError(err)
	}
	record.Version = version
	record.RegisteredAt = time.Now().UTC()
	entry := adapterEntryFromRecord(record)
	if err := s.storage.RecordAdapterRegistration(record); err != nil {
		return entry, fmt.Errorf("适配器已注册，但记录来源失败: %w", err)
	}
	return entry, nil
}

// DeleteAdapter removes every version of id from the shared deployment and
// forgets the local record. Records for adapters already gone from the
// server are only forgotten.
func (s *AppService) DeleteAdapter(ctx context.Context, config agentapi.Config, id string, serverSide bool) error {
	id = strings.TrimSpace(id)
	if serverSide {
		ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
		defer cancel()
		if err := s.currentService().DeleteAdapter(ctx, config, id, ""); err != nil {
			return adapterError(err)
		}
	}
	return s.storage.ForgetAdapterRegistration(stateServerKey(config.Endpoint), id)
}

// verifyAdapterAvailable refuses to connect with an adapter the deployment
// no longer holds, or on a deployment too old to have adapters at all (it
// would ignore adapter_id and quietly answer as the base model). Any other
// failed list request (network) does not block the connection.
func (s *AppService) verifyAdapterAvailable(ctx context.Context, config agentapi.Config) error {
	id := strings.TrimSpace(config.AdapterID)
	if id == "" || !agentapi.SupportsAdapter(config.Provider) {
		return nil
	}
	ctx, cancel := context.WithTimeout(ctx, 15*time.Second)
	defer cancel()
	adapters, err := s.currentService().ListAdapters(ctx, config)
	if errors.Is(err, agentapi.ErrAdaptersUnsupported) {
		return fmt.Errorf("%w；已选的适配器 %s 用不上，请改回基模或换一台支持 MiSS 的部署", adapterError(err), id)
	}
	if err != nil {
		return nil
	}
	for _, adapter := range adapters {
		if adapter.ID == id {
			return nil
		}
	}
	return fmt.Errorf("MiSS 适配器 %s 已不在服务器上（服务端重启会清空注册）。请在连接设置的 MiSS 分组里重新注册，或改回基模", id)
}

// runtimeAdapterID is the MiSS adapter the running provider generates with.
func (s *AppService) runtimeAdapterID() string {
	s.mu.Lock()
	defer s.mu.Unlock()
	if !agentapi.SupportsAdapter(s.config.Provider) {
		return ""
	}
	return strings.TrimSpace(s.config.AdapterID)
}

// adapterError turns the old-deployment case into a sentence the settings
// page can show instead of the server's 404 page.
func adapterError(err error) error {
	if errors.Is(err, agentapi.ErrAdaptersUnsupported) {
		return fmt.Errorf("这台部署不支持 MiSS 适配器（没有 /v1/adapters，rwkv_lightning 版本较旧）")
	}
	return err
}

func joinAdapters(adapters []agentapi.RemoteAdapter, records []appstorage.AdapterRegistration) AdapterListing {
	byID := make(map[string]appstorage.AdapterRegistration, len(records))
	for _, record := range records {
		byID[record.AdapterID] = record
	}
	versions := map[string][]agentapi.RemoteAdapter{}
	var order []string
	for _, adapter := range adapters {
		if _, seen := versions[adapter.ID]; !seen {
			order = append(order, adapter.ID)
		}
		versions[adapter.ID] = append(versions[adapter.ID], adapter)
	}
	listing := AdapterListing{Adapters: []AdapterEntry{}, Missing: []AdapterEntry{}}
	for _, id := range order {
		listed := versions[id]
		record, known := byID[id]
		// The version shown is the one this machine registered last if the
		// server still holds it, else the only one; several unknown versions
		// leave it blank because the list does not say which is newest.
		shown := listed[0]
		version := ""
		if len(listed) == 1 {
			version = shown.Version
		}
		for _, adapter := range listed {
			if known && adapter.Version == record.Version {
				shown, version = adapter, adapter.Version
			}
		}
		entry := AdapterEntry{ID: id, Version: version, Versions: len(listed), Rank: shown.Rank, Alpha: shown.Alpha}
		if known {
			entry.ServerPath, entry.LocalPath, entry.LocalAvailable = record.ServerPath, record.LocalPath, localFileExists(record.LocalPath)
		}
		listing.Adapters = append(listing.Adapters, entry)
	}
	for _, record := range records {
		if _, onServer := versions[record.AdapterID]; onServer {
			continue
		}
		listing.Missing = append(listing.Missing, adapterEntryFromRecord(record))
	}
	return listing
}

func adapterEntryFromRecord(record appstorage.AdapterRegistration) AdapterEntry {
	return AdapterEntry{
		ID: record.AdapterID, Version: record.Version, Versions: 1,
		ServerPath: record.ServerPath, LocalPath: record.LocalPath,
		LocalAvailable: localFileExists(record.LocalPath),
	}
}

func localFileExists(path string) bool {
	if path == "" {
		return false
	}
	info, err := os.Stat(path)
	return err == nil && !info.IsDir()
}
