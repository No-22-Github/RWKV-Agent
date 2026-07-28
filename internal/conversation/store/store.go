package store

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"
	"unicode/utf8"

	"github.com/no22/RWKV-Agent/internal/inference"
)

const (
	maxManifestBytes   = 1 << 20
	maxTranscriptBytes = 64 << 20
	maxStateBytes      = 1 << 30
)

type Snapshot struct {
	SchemaVersion           int
	Revision                string
	TranscriptHash          string
	Model                   inference.ModelInfo
	Profile                 inference.PromptProfile
	InitialStateFingerprint string
	RuntimeABIVersion       int
	RWKVMobileCommit        string
	Transcript              []inference.Message
	StateDescriptor         inference.StateDescriptor
	NativeState             []byte
}

type manifest struct {
	SchemaVersion           int                       `json:"schema_version"`
	Revision                string                    `json:"revision"`
	TranscriptHash          string                    `json:"transcript_hash"`
	TranscriptChecksum      string                    `json:"transcript_checksum"`
	Model                   inference.ModelInfo       `json:"model"`
	Profile                 inference.PromptProfile   `json:"prompt_profile"`
	InitialStateFingerprint string                    `json:"initial_state_fingerprint"`
	RuntimeABIVersion       int                       `json:"runtime_abi_version"`
	RWKVMobileCommit        string                    `json:"rwkv_mobile_commit"`
	StateDescriptor         inference.StateDescriptor `json:"state_descriptor,omitempty"`
	StateChecksum           string                    `json:"state_checksum,omitempty"`
	SavedAt                 time.Time                 `json:"saved_at"`
}

func Save(path string, snapshot Snapshot) error {
	if path == "" || snapshot.Revision == "" {
		return fmt.Errorf("%w: bundle path and revision are required", inference.ErrInvalidArgument)
	}
	if len(snapshot.NativeState) > maxStateBytes {
		return fmt.Errorf("%w: native State exceeds size limit", inference.ErrInvalidArgument)
	}
	root, err := filepath.Abs(path)
	if err != nil {
		return err
	}
	revisions := filepath.Join(root, "revisions")
	if err := os.MkdirAll(revisions, 0o700); err != nil {
		return err
	}
	revisionDirectory := "sha256-" + strings.TrimPrefix(snapshot.Revision, "sha256:")
	if !validRevisionDirectory(revisionDirectory) {
		return fmt.Errorf("%w: invalid revision", inference.ErrInvalidArgument)
	}
	finalDirectory := filepath.Join(revisions, revisionDirectory)
	if _, err := os.Stat(finalDirectory); err == nil {
		if err := updateCurrent(root, revisionDirectory); err != nil {
			return err
		}
		return nil
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}
	temporary, err := os.MkdirTemp(revisions, ".save-")
	if err != nil {
		return err
	}
	cleanup := true
	defer func() {
		if cleanup {
			_ = os.RemoveAll(temporary)
		}
	}()

	transcriptData, err := encodeTranscript(snapshot.Transcript)
	if err != nil {
		return err
	}
	if len(transcriptData) > maxTranscriptBytes {
		return fmt.Errorf("%w: transcript exceeds size limit", inference.ErrInvalidArgument)
	}
	transcriptChecksum := checksum(transcriptData)
	stateChecksum := ""
	if len(snapshot.NativeState) > 0 {
		stateChecksum = checksum(snapshot.NativeState)
	}
	value := manifest{
		SchemaVersion:           snapshot.SchemaVersion,
		Revision:                snapshot.Revision,
		TranscriptHash:          snapshot.TranscriptHash,
		TranscriptChecksum:      transcriptChecksum,
		Model:                   snapshot.Model,
		Profile:                 snapshot.Profile,
		InitialStateFingerprint: snapshot.InitialStateFingerprint,
		RuntimeABIVersion:       snapshot.RuntimeABIVersion,
		RWKVMobileCommit:        snapshot.RWKVMobileCommit,
		StateDescriptor:         snapshot.StateDescriptor,
		StateChecksum:           stateChecksum,
		SavedAt:                 time.Now().UTC(),
	}
	manifestData, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	manifestData = append(manifestData, '\n')
	if err := writeSynced(filepath.Join(temporary, "transcript.jsonl"), transcriptData); err != nil {
		return err
	}
	if len(snapshot.NativeState) > 0 {
		if err := writeSynced(filepath.Join(temporary, "state.bin"), snapshot.NativeState); err != nil {
			return err
		}
	}
	if err := writeSynced(filepath.Join(temporary, "session.json"), manifestData); err != nil {
		return err
	}
	if err := syncDirectory(temporary); err != nil {
		return err
	}
	if err := os.Rename(temporary, finalDirectory); err != nil {
		return err
	}
	cleanup = false
	if err := syncDirectory(revisions); err != nil {
		return err
	}
	if err := updateCurrent(root, revisionDirectory); err != nil {
		return err
	}
	garbageCollect(revisions, revisionDirectory, 2)
	return nil
}

func Load(path string) (Snapshot, error) {
	root, err := filepath.Abs(path)
	if err != nil {
		return Snapshot{}, err
	}
	currentInfo, err := os.Lstat(filepath.Join(root, "CURRENT"))
	if err != nil {
		return Snapshot{}, err
	}
	if currentInfo.Mode()&os.ModeSymlink != 0 || !currentInfo.Mode().IsRegular() {
		return Snapshot{}, fmt.Errorf("%w: CURRENT must be a regular file", inference.ErrCorruptState)
	}
	currentData, err := readLimited(filepath.Join(root, "CURRENT"), 4096)
	if err != nil {
		return Snapshot{}, err
	}
	revisionDirectory := strings.TrimSpace(string(currentData))
	if !validRevisionDirectory(revisionDirectory) {
		return Snapshot{}, fmt.Errorf("%w: invalid CURRENT revision", inference.ErrCorruptState)
	}
	directory := filepath.Join(root, "revisions", revisionDirectory)
	if err := verifyContainedDirectory(root, directory); err != nil {
		return Snapshot{}, err
	}
	manifestData, err := readLimited(filepath.Join(directory, "session.json"), maxManifestBytes)
	if err != nil {
		return Snapshot{}, err
	}
	var value manifest
	decoder := json.NewDecoder(strings.NewReader(string(manifestData)))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&value); err != nil {
		return Snapshot{}, fmt.Errorf("%w: invalid session manifest: %v", inference.ErrCorruptState, err)
	}
	if "sha256-"+strings.TrimPrefix(value.Revision, "sha256:") != revisionDirectory {
		return Snapshot{}, fmt.Errorf("%w: revision directory mismatch", inference.ErrCorruptState)
	}
	transcriptData, err := readLimited(filepath.Join(directory, "transcript.jsonl"), maxTranscriptBytes)
	if err != nil {
		return Snapshot{}, err
	}
	if checksum(transcriptData) != value.TranscriptChecksum {
		return Snapshot{}, fmt.Errorf("%w: transcript checksum mismatch", inference.ErrCorruptState)
	}
	transcript, err := decodeTranscript(transcriptData)
	if err != nil {
		return Snapshot{}, err
	}
	var nativeState []byte
	if value.StateChecksum != "" {
		nativeState, err = readLimited(filepath.Join(directory, "state.bin"), maxStateBytes)
		if err != nil {
			if !errors.Is(err, os.ErrNotExist) {
				return Snapshot{}, err
			}
			nativeState = nil
		}
		if len(nativeState) > 0 && checksum(nativeState) != value.StateChecksum {
			return Snapshot{}, fmt.Errorf("%w: native State checksum mismatch", inference.ErrCorruptState)
		}
	}
	return Snapshot{
		SchemaVersion:           value.SchemaVersion,
		Revision:                value.Revision,
		TranscriptHash:          value.TranscriptHash,
		Model:                   value.Model,
		Profile:                 value.Profile,
		InitialStateFingerprint: value.InitialStateFingerprint,
		RuntimeABIVersion:       value.RuntimeABIVersion,
		RWKVMobileCommit:        value.RWKVMobileCommit,
		Transcript:              transcript,
		StateDescriptor:         value.StateDescriptor,
		NativeState:             nativeState,
	}, nil
}

func encodeTranscript(messages []inference.Message) ([]byte, error) {
	var output strings.Builder
	encoder := json.NewEncoder(&output)
	encoder.SetEscapeHTML(false)
	for _, message := range messages {
		if !utf8.ValidString(message.Name) || !utf8.ValidString(message.ToolCallID) {
			return nil, fmt.Errorf("%w: transcript contains invalid UTF-8", inference.ErrInvalidArgument)
		}
		switch message.Role {
		case inference.RoleSystem, inference.RoleUser, inference.RoleAssistant, inference.RoleTool:
		default:
			return nil, fmt.Errorf("%w: invalid transcript role %q", inference.ErrInvalidArgument, message.Role)
		}
		for _, part := range message.Parts {
			if part.Kind != inference.ContentText || !utf8.ValidString(part.Text) {
				return nil, fmt.Errorf("%w: invalid transcript content", inference.ErrInvalidArgument)
			}
		}
		if err := encoder.Encode(message); err != nil {
			return nil, err
		}
	}
	return []byte(output.String()), nil
}

func decodeTranscript(data []byte) ([]inference.Message, error) {
	scanner := bufio.NewScanner(strings.NewReader(string(data)))
	scanner.Buffer(make([]byte, 64*1024), maxTranscriptBytes)
	var messages []inference.Message
	for scanner.Scan() {
		var message inference.Message
		decoder := json.NewDecoder(strings.NewReader(scanner.Text()))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&message); err != nil {
			return nil, fmt.Errorf("%w: invalid transcript JSONL: %v", inference.ErrCorruptState, err)
		}
		switch message.Role {
		case inference.RoleSystem, inference.RoleUser, inference.RoleAssistant, inference.RoleTool:
		default:
			return nil, fmt.Errorf("%w: invalid transcript role", inference.ErrCorruptState)
		}
		if len(message.Parts) == 0 {
			return nil, fmt.Errorf("%w: empty transcript message", inference.ErrCorruptState)
		}
		for _, part := range message.Parts {
			if part.Kind != inference.ContentText || !utf8.ValidString(part.Text) {
				return nil, fmt.Errorf("%w: invalid transcript content", inference.ErrCorruptState)
			}
		}
		messages = append(messages, message)
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return messages, nil
}

func checksum(data []byte) string {
	sum := sha256.Sum256(data)
	return "sha256:" + hex.EncodeToString(sum[:])
}

func writeSynced(path string, data []byte) error {
	handle, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o600)
	if err != nil {
		return err
	}
	if _, err := handle.Write(data); err != nil {
		_ = handle.Close()
		return err
	}
	if err := handle.Sync(); err != nil {
		_ = handle.Close()
		return err
	}
	return handle.Close()
}

func updateCurrent(root, revisionDirectory string) error {
	temporary, err := os.CreateTemp(root, ".CURRENT-")
	if err != nil {
		return err
	}
	name := temporary.Name()
	defer os.Remove(name)
	if _, err := io.WriteString(temporary, revisionDirectory+"\n"); err != nil {
		_ = temporary.Close()
		return err
	}
	if err := temporary.Sync(); err != nil {
		_ = temporary.Close()
		return err
	}
	if err := temporary.Close(); err != nil {
		return err
	}
	if err := os.Rename(name, filepath.Join(root, "CURRENT")); err != nil {
		return err
	}
	return syncDirectory(root)
}

func syncDirectory(path string) error {
	handle, err := os.Open(path)
	if err != nil {
		return err
	}
	defer handle.Close()
	return handle.Sync()
}

func readLimited(path string, limit int) ([]byte, error) {
	info, err := os.Lstat(path)
	if err != nil {
		return nil, err
	}
	if info.Mode()&os.ModeSymlink != 0 || !info.Mode().IsRegular() {
		return nil, fmt.Errorf("%w: %s must be a regular file", inference.ErrCorruptState, filepath.Base(path))
	}
	if info.Size() > int64(limit) {
		return nil, fmt.Errorf("%w: %s exceeds size limit", inference.ErrCorruptState, filepath.Base(path))
	}
	return os.ReadFile(path)
}

func verifyContainedDirectory(root, directory string) error {
	info, err := os.Lstat(directory)
	if err != nil {
		return err
	}
	if info.Mode()&os.ModeSymlink != 0 || !info.IsDir() {
		return fmt.Errorf("%w: revision must be a real directory", inference.ErrCorruptState)
	}
	resolvedRoot, err := filepath.EvalSymlinks(root)
	if err != nil {
		return err
	}
	resolvedDirectory, err := filepath.EvalSymlinks(directory)
	if err != nil {
		return err
	}
	relative, err := filepath.Rel(resolvedRoot, resolvedDirectory)
	if err != nil || relative == ".." || strings.HasPrefix(relative, ".."+string(filepath.Separator)) {
		return fmt.Errorf("%w: revision escapes bundle", inference.ErrCorruptState)
	}
	return nil
}

func validRevisionDirectory(value string) bool {
	if !strings.HasPrefix(value, "sha256-") || len(value) != len("sha256-")+64 {
		return false
	}
	for _, character := range value[len("sha256-"):] {
		if !(character >= '0' && character <= '9') &&
			!(character >= 'a' && character <= 'f') {
			return false
		}
	}
	return true
}

func garbageCollect(revisions, current string, keep int) {
	entries, err := os.ReadDir(revisions)
	if err != nil {
		return
	}
	type candidate struct {
		name string
		time time.Time
	}
	var candidates []candidate
	for _, entry := range entries {
		if !entry.IsDir() || !validRevisionDirectory(entry.Name()) {
			continue
		}
		info, err := entry.Info()
		if err == nil {
			candidates = append(candidates, candidate{entry.Name(), info.ModTime()})
		}
	}
	sort.Slice(candidates, func(i, j int) bool { return candidates[i].time.After(candidates[j].time) })
	retainedNonCurrent := 0
	for _, candidate := range candidates {
		if candidate.name == current {
			continue
		}
		if retainedNonCurrent < max(0, keep-1) {
			retainedNonCurrent++
			continue
		}
		_ = os.RemoveAll(filepath.Join(revisions, candidate.name))
	}
}
