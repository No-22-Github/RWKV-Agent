// Package tokenizer provides in-process token counting with the real RWKV
// World vocabulary (rwkv_vocab_v20230424.txt). It replaces the char-ratio
// estimator (agent.EstimateTokens) everywhere a token count decides harness
// behavior: the fetch budget and the fetch-compression threshold (round 3,
// step 1). Encoding is delegated to rwkvtok
// (github.com/No-22-Github/rwkv-tokenizer-go), a greedy longest-match trie
// byte-identical to the reference tokenizer; this package only adds the
// "<EOD>" token 0 that rwkv_lightning_cuda/include/rwkv_trie.hpp inserts, so
// counts stay on the same ruler as the corpus builder and the BFCL pysidecar
// count_tokens op. The fixture test world_test.go verifies per-text count
// equality against 551,860 Python-counted tokens spanning every corpus family.
package tokenizer

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"

	rwkvtok "github.com/No-22-Github/rwkv-tokenizer-go"
)

const eodTokenText = "<EOD>"

var (
	cacheMu    sync.Mutex
	worldCache = map[string]*World{}
)

// OpenWorldCached loads the vocabulary once per path and returns the shared
// instance. The eval runner and the App session both call this per case or per
// session, and the trie build should run once per process.
func OpenWorldCached(vocabPath string) (*World, error) {
	absolute, err := filepath.Abs(vocabPath)
	if err != nil {
		return nil, fmt.Errorf("tokenizer: resolve vocab path: %w", err)
	}
	cacheMu.Lock()
	defer cacheMu.Unlock()
	if world, ok := worldCache[absolute]; ok {
		return world, nil
	}
	world, err := OpenWorld(absolute)
	if err != nil {
		return nil, err
	}
	worldCache[absolute] = world
	return world, nil
}

// World is a loaded RWKV World vocabulary with greedy longest-match encoding.
// It is safe for concurrent use.
type World struct {
	tok    *rwkvtok.Tokenizer
	sha256 string
	bufs   sync.Pool
}

// OpenWorld loads and validates the vocabulary file (rwkvtok checks each
// literal's declared byte length and rejects duplicate ids).
func OpenWorld(vocabPath string) (*World, error) {
	data, err := os.ReadFile(vocabPath)
	if err != nil {
		return nil, fmt.Errorf("tokenizer: open vocab: %w", err)
	}
	// Balanced keeps ~90% of the speed preset's throughput on the fixture
	// corpus with roughly half the build allocation (17 vs 31 MB); memory
	// drops to ~30% throughput for 1 MB less.
	tok, err := rwkvtok.NewFromBytes(data, rwkvtok.WithPreset(rwkvtok.PresetBalanced))
	if err != nil {
		return nil, fmt.Errorf("tokenizer: %w", err)
	}
	digest := sha256.Sum256(data)
	return &World{tok: tok, sha256: hex.EncodeToString(digest[:])}, nil
}

// SHA256 returns the hex digest of the vocabulary file bytes, so manifests can
// pin which ruler produced a count.
func (w *World) SHA256() string { return w.sha256 }

// Count returns the number of tokens text encodes to.
func (w *World) Count(text string) int {
	if !strings.Contains(text, eodTokenText) {
		buf, _ := w.bufs.Get().(*[]int32)
		if buf == nil {
			buf = new([]int32)
		}
		*buf = w.tok.AppendEncode((*buf)[:0], text)
		count := len(*buf)
		w.bufs.Put(buf)
		return count
	}
	return len(w.encodeWithEOD(text))
}

// Encode returns the token IDs of text (greedy longest match). Used by tests
// and by callers that need more than a count.
func (w *World) Encode(text string) []int {
	var ids32 []int32
	if strings.Contains(text, eodTokenText) {
		ids32 = w.encodeWithEOD(text)
	} else {
		ids32 = w.tok.Encode(text)
	}
	ids := make([]int, len(ids32))
	for i, id := range ids32 {
		ids[i] = int(id)
	}
	return ids
}

// encodeWithEOD reproduces the reference trie, which carries "<EOD>" as token
// 0 on top of the vocab file. The vocab has no token starting with "<EOD", so
// the reference emits token 0 exactly where greedy encoding lands on the start
// of an "<EOD>" occurrence; everywhere else the two tries pick the same match.
// An occurrence that a longer token straddles is left to the plain encoding.
func (w *World) encodeWithEOD(text string) []int32 {
	var out []int32
	start := 0
	for start < len(text) {
		ids := w.tok.Encode(text[start:])
		position := start
		next := nextEOD(text, position)
		restarted := false
		for _, id := range ids {
			if position == next {
				out = append(out, 0)
				start = position + len(eodTokenText)
				restarted = true
				break
			}
			out = append(out, id)
			position += w.tokenLength(id)
			if next >= 0 && next < position {
				next = nextEOD(text, position)
			}
		}
		if !restarted {
			break
		}
	}
	return out
}

func nextEOD(text string, from int) int {
	index := strings.Index(text[from:], eodTokenText)
	if index < 0 {
		return -1
	}
	return from + index
}

func (w *World) tokenLength(id int32) int {
	token, err := w.tok.DecodeBytes([]int32{id})
	if err != nil {
		// Encode only emits ids from the vocab, so this is unreachable.
		panic(fmt.Sprintf("tokenizer: decode own token %d: %v", id, err))
	}
	return len(token)
}
