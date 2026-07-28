package rwkvmobile

import (
	"archive/zip"
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestProbeDirectPTH(t *testing.T) {
	t.Parallel()

	directory := t.TempDir()
	modelPath := filepath.Join(directory, "rwkv7-test.PTH")
	tokenizerPath := filepath.Join(directory, "rwkv_vocab_v20230424.txt")
	writeTestPTH(t, modelPath)
	if err := os.WriteFile(tokenizerPath, []byte("tokenizer"), 0o600); err != nil {
		t.Fatal(err)
	}

	info, err := New(Options{}).ProbeModel(context.Background(), inference.ModelSource{
		Path:          modelPath,
		TokenizerPath: tokenizerPath,
	})
	if err != nil {
		t.Fatal(err)
	}
	if info.ID != "rwkv7-test" {
		t.Fatalf("model ID = %q", info.ID)
	}
	if info.Format != "rwkv-pth" {
		t.Fatalf("format = %q", info.Format)
	}
	if !strings.HasPrefix(info.Fingerprint, "sha256:") {
		t.Fatalf("fingerprint = %q", info.Fingerprint)
	}
	newTime := time.Now().Add(2 * time.Second)
	if err := os.Chtimes(modelPath, newTime, newTime); err != nil {
		t.Fatal(err)
	}
	afterTouch, err := New(Options{}).ProbeModel(
		context.Background(),
		inference.ModelSource{Path: modelPath, TokenizerPath: tokenizerPath},
	)
	if err != nil {
		t.Fatal(err)
	}
	if afterTouch.Fingerprint != info.Fingerprint {
		t.Fatal("semantic PTH fingerprint changed after touching the same checkpoint")
	}
}

func writeTestPTH(t *testing.T, path string) {
	t.Helper()
	handle, err := os.Create(path)
	if err != nil {
		t.Fatal(err)
	}
	writer := zip.NewWriter(handle)
	entry, err := writer.Create("archive/data.pkl")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := entry.Write([]byte("metadata")); err != nil {
		t.Fatal(err)
	}
	if err := writer.Close(); err != nil {
		t.Fatal(err)
	}
	if err := handle.Close(); err != nil {
		t.Fatal(err)
	}
}

func TestPTHIndexPathIsStableForSource(t *testing.T) {
	t.Parallel()

	modelPath := filepath.Join(t.TempDir(), "model.pth")
	if err := os.WriteFile(modelPath, []byte("first"), 0o600); err != nil {
		t.Fatal(err)
	}
	first := pthIndexPath(modelPath)
	if first == "" || filepath.Ext(first) != ".rwkvi" {
		t.Fatalf("index path = %q", first)
	}

	newTime := time.Now().Add(2 * time.Second)
	if err := os.Chtimes(modelPath, newTime, newTime); err != nil {
		t.Fatal(err)
	}
	second := pthIndexPath(modelPath)
	if first != second {
		t.Fatal("index path changed; stale validation belongs inside the index")
	}
}

func TestRejectsNonPTHModelFile(t *testing.T) {
	t.Parallel()

	modelPath := filepath.Join(t.TempDir(), "model.bin")
	if err := os.WriteFile(modelPath, []byte("model"), 0o600); err != nil {
		t.Fatal(err)
	}
	err := validateSource(inference.ModelSource{Path: modelPath})
	if err == nil || !strings.Contains(err.Error(), ".pth") {
		t.Fatalf("validateSource error = %v", err)
	}
}
