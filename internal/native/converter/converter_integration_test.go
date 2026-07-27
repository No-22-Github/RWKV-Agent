//go:build cgo && converter

package converter

import (
	"crypto/sha256"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"testing"
)

func TestNativeConversion(t *testing.T) {
	input := os.Getenv("RWKV_TEST_PTH")
	tokenizer := os.Getenv("RWKV_TEST_TOKENIZER")
	if input == "" || tokenizer == "" {
		t.Skip("set RWKV_TEST_PTH and RWKV_TEST_TOKENIZER to run native conversion")
	}

	output := filepath.Join(t.TempDir(), "model")
	if err := Convert(Options{
		InputPath:     input,
		OutputPath:    output,
		TokenizerPath: tokenizer,
		Precision:     "bf16",
	}); err != nil {
		t.Fatalf("Convert() error: %v", err)
	}

	for _, name := range []string{
		"config.json",
		"model.safetensors",
		"rwkv_vocab_v20230424.txt",
	} {
		if info, err := os.Stat(filepath.Join(output, name)); err != nil || info.Size() == 0 {
			t.Fatalf("invalid output %s: info=%v error=%v", name, info, err)
		}
	}

	reference := os.Getenv("RWKV_TEST_CONVERTER_REFERENCE")
	if reference == "" {
		return
	}
	got, err := fileSHA256(filepath.Join(output, "model.safetensors"))
	if err != nil {
		t.Fatal(err)
	}
	want, err := fileSHA256(reference)
	if err != nil {
		t.Fatal(err)
	}
	if got != want {
		t.Fatalf("safetensors SHA-256 = %x, want %x", got, want)
	}
}

func fileSHA256(path string) ([sha256.Size]byte, error) {
	file, err := os.Open(path)
	if err != nil {
		return [sha256.Size]byte{}, err
	}
	defer file.Close()

	hash := sha256.New()
	if _, err := io.Copy(hash, file); err != nil {
		return [sha256.Size]byte{}, err
	}
	var sum [sha256.Size]byte
	if copied := copy(sum[:], hash.Sum(nil)); copied != len(sum) {
		return [sha256.Size]byte{}, fmt.Errorf("unexpected SHA-256 length: %d", copied)
	}
	return sum, nil
}
