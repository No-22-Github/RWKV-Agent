package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"io"
	"net/url"
	"os"
	"strings"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/appstorage"
)

const stateUploadProgressEvent = "state:upload-progress"

// StateEntry is one server-side state joined with the local upload record, if
// this machine uploaded it.
type StateEntry struct {
	agentapi.RemoteState
	LocalPath string `json:"localPath,omitempty"`
	// LocalAvailable reports whether LocalPath still exists on disk.
	LocalAvailable bool `json:"localAvailable,omitempty"`
}

// StateListing is the server list plus local records whose state no longer
// exists on the server (typically wiped by a deployment restart).
type StateListing struct {
	States  []StateEntry `json:"states"`
	Missing []StateEntry `json:"missing"`
}

// StateUploadProgress is emitted while a state file is being uploaded.
type StateUploadProgress struct {
	Path  string `json:"path"`
	Sent  int64  `json:"sent"`
	Total int64  `json:"total"`
}

// ChooseStateFile opens the native file picker for a .pth state file. Server
// builds return the Wails "file dialogs not available" error; the UI then
// falls back to a typed path.
func (s *AppService) ChooseStateFile() (string, error) {
	s.mu.Lock()
	app := s.app
	s.mu.Unlock()
	if app == nil || app.Dialog == nil {
		return "", fmt.Errorf("桌面窗口不可用，请直接填写 State 文件路径")
	}
	dialog := app.Dialog.OpenFile().
		CanChooseFiles(true).
		CanChooseDirectories(false).
		SetTitle("选择 State 文件")
	dialog.AddFilter("RWKV State", "*.pth")
	dialog.AddFilter("所有文件", "*")
	return dialog.PromptForSingleSelection()
}

// ListStates lists the deployment's states and joins local upload records.
func (s *AppService) ListStates(ctx context.Context, config agentapi.Config) (StateListing, error) {
	ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
	defer cancel()
	states, err := s.currentService().ListStates(ctx, config)
	if err != nil {
		return StateListing{}, err
	}
	records, err := s.storage.StateUploads(stateServerKey(config.Endpoint))
	if err != nil {
		return StateListing{}, err
	}
	byID := make(map[string]appstorage.StateUpload, len(records))
	for _, record := range records {
		byID[record.StateID] = record
	}
	listing := StateListing{States: make([]StateEntry, 0, len(states)), Missing: []StateEntry{}}
	onServer := make(map[string]bool, len(states))
	for _, state := range states {
		onServer[state.ID] = true
		listing.States = append(listing.States, joinStateRecord(state, byID[state.ID]))
	}
	for _, record := range records {
		if onServer[record.StateID] {
			continue
		}
		listing.Missing = append(listing.Missing, joinStateRecord(agentapi.RemoteState{
			ID: record.StateID, Filename: fileName(record.Path), SizeBytes: record.SizeBytes,
			Created: record.UploadedAt.Unix(),
		}, record))
	}
	return listing, nil
}

// UploadState uploads a local state file and records where it came from.
// Uploads are serialized: concurrent multi-hundred-MB uploads have knocked
// the shared deployment over before.
func (s *AppService) UploadState(ctx context.Context, config agentapi.Config, path string) (StateEntry, error) {
	path = strings.TrimSpace(path)
	info, err := os.Stat(path)
	if err != nil {
		return StateEntry{}, fmt.Errorf("读取 State 文件失败: %w", err)
	}
	if info.IsDir() {
		return StateEntry{}, fmt.Errorf("%s 是目录，请选择 .pth 文件", path)
	}
	digest, err := fileSHA256(path)
	if err != nil {
		return StateEntry{}, fmt.Errorf("读取 State 文件失败: %w", err)
	}
	s.stateUpload.Lock()
	defer s.stateUpload.Unlock()
	ctx, cancel := context.WithTimeout(ctx, 10*time.Minute)
	defer cancel()
	var lastPercent int64 = -1
	state, err := s.currentService().UploadState(ctx, config, path, func(sent, total int64) {
		percent := int64(100)
		if total > 0 {
			percent = sent * 100 / total
		}
		if percent == lastPercent {
			return
		}
		lastPercent = percent
		s.emit(stateUploadProgressEvent, StateUploadProgress{Path: path, Sent: sent, Total: total})
	})
	if err != nil {
		return StateEntry{}, err
	}
	record := appstorage.StateUpload{
		Server: stateServerKey(config.Endpoint), StateID: state.ID, Path: path,
		SHA256: digest, SizeBytes: info.Size(), UploadedAt: time.Now().UTC(),
	}
	if err := s.storage.RecordStateUpload(record); err != nil {
		return joinStateRecord(state, record), fmt.Errorf("State 已上传，但记录本地路径失败: %w", err)
	}
	return joinStateRecord(state, record), nil
}

// DeleteState removes a state from the shared deployment and forgets its
// local record. Records for states already gone from the server are only
// forgotten.
func (s *AppService) DeleteState(ctx context.Context, config agentapi.Config, id string, serverSide bool) error {
	if serverSide {
		ctx, cancel := context.WithTimeout(ctx, 30*time.Second)
		defer cancel()
		if err := s.currentService().DeleteState(ctx, config, id); err != nil {
			return err
		}
	}
	return s.storage.ForgetStateUpload(stateServerKey(config.Endpoint), strings.TrimSpace(id))
}

// verifyStateAvailable refuses to connect with a state_id the deployment no
// longer holds, instead of letting every generation fail later. A failed list
// request (old deployment, network) does not block the connection.
func (s *AppService) verifyStateAvailable(ctx context.Context, config agentapi.Config) error {
	id := strings.TrimSpace(config.StateID)
	if id == "" || !agentapi.SupportsUploadedState(config.Provider) {
		return nil
	}
	ctx, cancel := context.WithTimeout(ctx, 15*time.Second)
	defer cancel()
	states, err := s.currentService().ListStates(ctx, config)
	if err != nil {
		return nil
	}
	for _, state := range states {
		if state.ID == id {
			return nil
		}
	}
	return fmt.Errorf("State %s 已不在服务器上（服务端重启会清空已上传的 State）。请在连接设置的 State 分组里重新上传，或改回零状态", id)
}

func (s *AppService) currentService() *agentapi.Service {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.service
}

func joinStateRecord(state agentapi.RemoteState, record appstorage.StateUpload) StateEntry {
	entry := StateEntry{RemoteState: state}
	if record.Path != "" {
		entry.LocalPath = record.Path
		if info, err := os.Stat(record.Path); err == nil && !info.IsDir() {
			entry.LocalAvailable = true
		}
	}
	return entry
}

// stateServerKey identifies a deployment for the upload registry: states are
// per deployment process, so the scheme and host are what matter.
func stateServerKey(endpoint string) string {
	parsed, err := url.Parse(strings.TrimSpace(endpoint))
	if err != nil || parsed.Host == "" {
		return strings.ToLower(strings.TrimSpace(endpoint))
	}
	return strings.ToLower(parsed.Scheme + "://" + parsed.Host)
}

func fileSHA256(path string) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()
	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", err
	}
	return hex.EncodeToString(hash.Sum(nil)), nil
}

func fileName(path string) string {
	if index := strings.LastIndexAny(path, `/\`); index >= 0 {
		return path[index+1:]
	}
	return path
}
