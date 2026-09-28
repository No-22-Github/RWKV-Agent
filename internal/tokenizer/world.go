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
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
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
	// lengths[id] is the byte length of token id, and maxLength the longest
	// token: greedy matching never reads further ahead than that.
	lengths   []uint16
	maxLength int
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
	world := &World{tok: tok}
	if err := world.loadLengths(data); err != nil {
		return nil, err
	}
	digest := sha256.Sum256(data)
	world.sha256 = hex.EncodeToString(digest[:])
	return world, nil
}

// loadLengths reads each token's byte length from the last field of its vocab
// line ("id 'literal' byteLength"); rwkvtok has already validated the lines.
func (w *World) loadLengths(data []byte) error {
	w.lengths = make([]uint16, w.tok.VocabSize())
	for rest := data; len(rest) > 0; {
		line := rest
		if end := bytes.IndexByte(rest, '\n'); end >= 0 {
			line, rest = rest[:end], rest[end+1:]
		} else {
			rest = nil
		}
		line = bytes.TrimSpace(line)
		if len(line) == 0 {
			continue
		}
		first := bytes.IndexByte(line, ' ')
		last := bytes.LastIndexByte(line, ' ')
		id, idErr := strconv.Atoi(string(line[:max(first, 0)]))
		length, lengthErr := strconv.Atoi(string(line[last+1:]))
		if idErr != nil || lengthErr != nil || id < 0 || id >= len(w.lengths) || length > 0xffff {
			return fmt.Errorf("tokenizer: vocab line %q: bad id or byte length", line)
		}
		w.lengths[id] = uint16(length)
		w.maxLength = max(w.maxLength, length)
	}
	return nil
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
//
// A match starting at r reads at most maxLength bytes, so encoding only up to
// next+maxLength yields the same tokens as the full suffix for every token
// starting at or before the next occurrence. Each chunk therefore ends at most
// maxLength bytes past its occurrence, keeping the whole pass linear even for
// input made of nothing but markers.
func (w *World) encodeWithEOD(text string) []int32 {
	var out []int32
	position := 0
	for position < len(text) {
		next := nextEOD(text, position)
		if next < 0 {
			return w.tok.AppendEncode(out, text[position:])
		}
		if next == position {
			out = append(out, 0)
			position += len(eodTokenText)
			continue
		}
		chunk := len(out)
		out = w.tok.AppendEncode(out, text[position:min(len(text), next+w.maxLength)])
		// Keep tokens up to landing on or straddling the occurrence; the loop
		// above emits token 0 or finds the next occurrence from there.
		for position < next {
			position += int(w.lengths[out[chunk]])
			chunk++
		}
		out = out[:chunk]
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
