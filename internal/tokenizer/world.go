// Package tokenizer is the project's one handle on the RWKV World vocabulary
// (rwkv_vocab_v20230424.txt). Encoding, counting and the vocabulary itself all
// live in rwkvtok (github.com/No-22-Github/rwkv-tokenizer-go); new tokenizer
// needs go there, not here. This package only fixes the configuration every
// caller shares, so counts stay on one ruler, and puts the embedded vocabulary
// on disk for the native engine, which only takes a path. The fixture test
// world_test.go verifies per-text count equality against 551,860
// Python-counted tokens spanning every corpus family.
package tokenizer

import (
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"sync"

	rwkvtok "github.com/No-22-Github/rwkv-tokenizer-go"
)

const vocabFilename = "rwkv_vocab_v20230424.txt"

// World returns the shared tokenizer, loaded on first use. "<EOD>" is token 0
// as in rwkv_lightning_cuda/include/rwkv_trie.hpp. Balanced keeps ~90% of the
// speed preset's throughput on the fixture corpus with roughly half the build
// allocation (17 vs 31 MB); memory drops to ~30% throughput for 1 MB less.
var World = sync.OnceValue(func() *rwkvtok.Tokenizer {
	tok, err := rwkvtok.New(rwkvtok.WithPreset(rwkvtok.PresetBalanced), rwkvtok.WithEOD())
	if err != nil {
		// The vocabulary is embedded and pinned by tests, so this is a broken build.
		panic(fmt.Errorf("tokenizer: embedded vocabulary: %w", err))
	}
	return tok
})

// VocabPath writes the embedded vocabulary under the user cache directory and
// returns its path. An existing file with the same bytes is reused.
func VocabPath() (string, error) {
	data, err := rwkvtok.DefaultVocab()
	if err != nil {
		return "", fmt.Errorf("tokenizer: %w", err)
	}
	cache, err := os.UserCacheDir()
	if err != nil {
		return "", fmt.Errorf("tokenizer: %w", err)
	}
	return writeVocab(filepath.Join(cache, "rwkv-agent"), data)
}

func writeVocab(dir string, data []byte) (string, error) {
	path := filepath.Join(dir, vocabFilename)
	if existing, err := os.ReadFile(path); err == nil && bytes.Equal(existing, data) {
		return path, nil
	}
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return "", fmt.Errorf("tokenizer: %w", err)
	}
	// Rename into place so a concurrent reader never sees a partial file.
	file, err := os.CreateTemp(dir, vocabFilename+".*")
	if err != nil {
		return "", fmt.Errorf("tokenizer: %w", err)
	}
	defer os.Remove(file.Name())
	_, err = file.Write(data)
	if closeErr := file.Close(); err == nil {
		err = closeErr
	}
	if err == nil {
		err = os.Chmod(file.Name(), 0o644)
	}
	if err == nil {
		err = os.Rename(file.Name(), path)
	}
	if err != nil {
		return "", fmt.Errorf("tokenizer: %w", err)
	}
	return path, nil
}
