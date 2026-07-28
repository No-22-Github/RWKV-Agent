package store

import (
	"errors"
	"os"
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestImmutableRevisionAndCurrent(t *testing.T) {
	bundle := filepath.Join(t.TempDir(), "session")
	first := testSnapshot("sha256:"+repeat("a", 64), "one")
	if err := Save(bundle, first); err != nil {
		t.Fatal(err)
	}
	second := testSnapshot("sha256:"+repeat("b", 64), "two")
	if err := Save(bundle, second); err != nil {
		t.Fatal(err)
	}
	loaded, err := Load(bundle)
	if err != nil {
		t.Fatal(err)
	}
	if loaded.Revision != second.Revision {
		t.Fatalf("revision = %q, want %q", loaded.Revision, second.Revision)
	}
	if len(loaded.Transcript) != 1 || loaded.Transcript[0].Parts[0].Text != "two" {
		t.Fatalf("unexpected transcript: %+v", loaded.Transcript)
	}
}

func TestRejectsCurrentSymlink(t *testing.T) {
	root := t.TempDir()
	bundle := filepath.Join(root, "session")
	if err := os.MkdirAll(bundle, 0o700); err != nil {
		t.Fatal(err)
	}
	target := filepath.Join(root, "target")
	if err := os.WriteFile(target, []byte("sha256-"+repeat("a", 64)), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(target, filepath.Join(bundle, "CURRENT")); err != nil {
		t.Fatal(err)
	}
	if _, err := Load(bundle); !errors.Is(err, inference.ErrCorruptState) {
		t.Fatalf("Load error = %v, want ErrCorruptState", err)
	}
}

func TestRejectsCorruptNativeState(t *testing.T) {
	bundle := filepath.Join(t.TempDir(), "session")
	snapshot := testSnapshot("sha256:"+repeat("c", 64), "state")
	snapshot.NativeState = []byte("valid-state-bytes")
	snapshot.StateDescriptor = inference.StateDescriptor{
		FormatVersion: 1,
		CodecID:       "test",
		CodecVersion:  1,
	}
	if err := Save(bundle, snapshot); err != nil {
		t.Fatal(err)
	}
	current, err := os.ReadFile(filepath.Join(bundle, "CURRENT"))
	if err != nil {
		t.Fatal(err)
	}
	statePath := filepath.Join(
		bundle,
		"revisions",
		string(trimSpace(current)),
		"state.bin",
	)
	if err := os.WriteFile(statePath, []byte("tampered"), 0o600); err != nil {
		t.Fatal(err)
	}
	if _, err := Load(bundle); !errors.Is(err, inference.ErrCorruptState) {
		t.Fatalf("Load error = %v, want ErrCorruptState", err)
	}
}

func testSnapshot(revision, text string) Snapshot {
	message := inference.TextMessage(inference.RoleUser, text)
	data, _ := encodeTranscript([]inference.Message{message})
	return Snapshot{
		SchemaVersion:  1,
		Revision:       revision,
		TranscriptHash: checksumCanonicalForTest([]inference.Message{message}),
		Model: inference.ModelInfo{
			Fingerprint:          "model",
			TokenizerFingerprint: "tokenizer",
		},
		Profile:     inference.DefaultPromptProfile(false),
		Transcript:  []inference.Message{message},
		NativeState: append([]byte(nil), data[:0]...),
	}
}

func checksumCanonicalForTest(messages []inference.Message) string {
	data, _ := encodeTranscript(messages)
	return checksum(data)
}

func repeat(value string, count int) string {
	result := ""
	for index := 0; index < count; index++ {
		result += value
	}
	return result
}

func trimSpace(value []byte) []byte {
	start, end := 0, len(value)
	for start < end && (value[start] == ' ' || value[start] == '\n' || value[start] == '\r' || value[start] == '\t') {
		start++
	}
	for end > start && (value[end-1] == ' ' || value[end-1] == '\n' || value[end-1] == '\r' || value[end-1] == '\t') {
		end--
	}
	return value[start:end]
}
