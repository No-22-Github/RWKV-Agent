// Package tokenizer provides in-process token counting with the real RWKV
// World vocabulary (rwkv_vocab_v20230424.txt). It replaces the char-ratio
// estimator (agent.EstimateTokens) everywhere a token count decides harness
// behavior: the fetch budget and the fetch-compression threshold (round 3,
// step 1). The greedy longest-match byte trie mirrors
// rwkv_lightning_cuda/include/rwkv_trie.hpp, the same algorithm the temporary
// corpus builder and the BFCL pysidecar count_tokens op use, so all channels
// share one ruler; the fixture test
// world_test.go verifies per-text count equality against 551,860 Python-counted
// tokens spanning every corpus family.
package tokenizer

import (
	"bufio"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync"
)

const eodTokenText = "<EOD>"

var (
	cacheMu    sync.Mutex
	worldCache = map[string]*World{}
)

// OpenWorldCached loads the vocabulary once per path and returns the shared
// instance. The eval runner and the App session both call this per case or per
// session, and the ~65k-line vocab parse should run once per process.
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
type World struct {
	root     trieNode
	sha256   string
	maxDepth int
}

type trieNode struct {
	children map[byte]*trieNode
	tokenID  int
	hasToken bool
}

// OpenWorld loads and validates the vocabulary file. It verifies that every
// byte value 0..255 has a single-byte token so encoding always makes progress,
// and that each parsed literal's UTF-8 length matches the declared byte length.
func OpenWorld(vocabPath string) (*World, error) {
	file, err := os.Open(vocabPath)
	if err != nil {
		return nil, fmt.Errorf("tokenizer: open vocab: %w", err)
	}
	defer file.Close()
	digest := sha256.New()
	world := &World{root: trieNode{children: map[byte]*trieNode{}}}
	covered := [256]bool{}
	lineNumber := 0
	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 0, 1024*1024), 1024*1024)
	for scanner.Scan() {
		lineNumber++
		line := scanner.Text()
		digest.Write(scanner.Bytes())
		digest.Write([]byte{'\n'})
		if strings.TrimSpace(line) == "" {
			continue
		}
		id, literal, byteLength, err := parseVocabLine(line)
		if err != nil {
			return nil, fmt.Errorf("tokenizer: vocab line %d: %w", lineNumber, err)
		}
		if id == 0 && string(literal) == eodTokenText {
			// Duplicated by the loader below for parity with the reference
			// implementations; nothing to add.
			continue
		}
		if len(literal) != byteLength {
			return nil, fmt.Errorf("tokenizer: vocab line %d: declared length %d, parsed %d",
				lineNumber, byteLength, len(literal))
		}
		world.add(id, literal)
		if len(literal) == 1 {
			covered[literal[0]] = true
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, fmt.Errorf("tokenizer: read vocab: %w", err)
	}
	// rwkv_trie.hpp defines token 0 as "<EOD>"; add it like the reference
	// implementations do.
	world.add(0, []byte(eodTokenText))
	for b := 0; b < 256; b++ {
		if !covered[b] {
			return nil, fmt.Errorf("tokenizer: vocab has no single-byte token for 0x%02x", b)
		}
	}
	world.sha256 = hex.EncodeToString(digest.Sum(nil))
	return world, nil
}

func (w *World) add(id int, literal []byte) {
	node := &w.root
	for i := 0; i < len(literal); i++ {
		b := literal[i]
		next, ok := node.children[b]
		if !ok {
			next = &trieNode{children: map[byte]*trieNode{}}
			node.children[b] = next
		}
		node = next
	}
	if len(literal) > w.maxDepth {
		w.maxDepth = len(literal)
	}
	node.tokenID = id
	node.hasToken = true
}

// SHA256 returns the hex digest of the vocabulary file bytes, so manifests can
// pin which ruler produced a count.
func (w *World) SHA256() string { return w.sha256 }

// Count returns the number of tokens text encodes to.
func (w *World) Count(text string) int {
	count := 0
	source := text
	position := 0
	for position < len(source) {
		node := &w.root
		cursor := position
		bestEnd := -1
		for cursor < len(source) {
			next, ok := node.children[source[cursor]]
			if !ok {
				break
			}
			node = next
			cursor++
			if node.hasToken {
				bestEnd = cursor
			}
		}
		if bestEnd <= position {
			// OpenWorld validates single-byte coverage, so this is unreachable.
			bestEnd = position + 1
		}
		position = bestEnd
		count++
	}
	return count
}

// Encode returns the token IDs of text (greedy longest match). Used by tests
// and by callers that need more than a count.
func (w *World) Encode(text string) []int {
	ids := []int{}
	position := 0
	source := text
	for position < len(source) {
		node := &w.root
		cursor := position
		bestEnd := -1
		bestID := 0
		for cursor < len(source) {
			next, ok := node.children[source[cursor]]
			if !ok {
				break
			}
			node = next
			cursor++
			if node.hasToken {
				bestEnd = cursor
				bestID = node.tokenID
			}
		}
		if bestEnd <= position {
			bestEnd = position + 1
		}
		position = bestEnd
		ids = append(ids, bestID)
	}
	return ids
}

// parseVocabLine parses "id 'python literal' byteLength" as written by the
// World vocab file (a Python repr of the token between two spaces). The
// literal is either a str literal (rune escapes, UTF-8 encoded to token bytes
// like the reference loader's eval() + .encode("utf-8")) or a b” bytes
// literal (escapes decode directly to token bytes).
func parseVocabLine(line string) (id int, literal []byte, byteLength int, err error) {
	first := strings.IndexByte(line, ' ')
	if first <= 0 {
		return 0, nil, 0, fmt.Errorf("missing id separator")
	}
	id, err = strconv.Atoi(line[:first])
	if err != nil {
		return 0, nil, 0, fmt.Errorf("bad id: %w", err)
	}
	last := strings.LastIndexByte(line, ' ')
	if last <= first+1 {
		return 0, nil, 0, fmt.Errorf("missing byte-length separator")
	}
	byteLength, err = strconv.Atoi(line[last+1:])
	if err != nil {
		return 0, nil, 0, fmt.Errorf("bad byte length: %w", err)
	}
	raw := line[first+1 : last]
	if strings.HasPrefix(raw, "b'") || strings.HasPrefix(raw, `b"`) {
		literal, err = parseBytesLiteral(raw)
	} else {
		literal, err = parseStrLiteral(raw)
	}
	if err != nil {
		return 0, nil, 0, err
	}
	return id, literal, byteLength, nil
}

// parseLiteralBody decodes the escape sequences of one Python literal between
// its quotes. byteMode selects bytes-literal semantics: \xNN and octal escapes
// produce raw bytes instead of Unicode codepoints, and unrecognized escapes
// are errors rather than Unicode escapes.
func parseLiteralBody(body string, byteMode bool) ([]byte, error) {
	var out []byte
	appendRune := func(r rune) {
		out = append(out, []byte(string(r))...)
	}
	for i := 0; i < len(body); i++ {
		c := body[i]
		if c != '\\' {
			// Copy raw bytes verbatim: str literals carry UTF-8 directly from
			// the file, and bytes literals are single raw bytes.
			out = append(out, c)
			continue
		}
		i++
		if i >= len(body) {
			return nil, fmt.Errorf("dangling escape")
		}
		switch body[i] {
		case 'n':
			out = append(out, '\n')
		case 't':
			out = append(out, '\t')
		case 'r':
			out = append(out, '\r')
		case 'a':
			out = append(out, '\a')
		case 'b':
			out = append(out, '\b')
		case 'f':
			out = append(out, '\f')
		case 'v':
			out = append(out, '\v')
		case '\\':
			out = append(out, '\\')
		case '\'':
			out = append(out, '\'')
		case '"':
			out = append(out, '"')
		case 'x':
			if i+2 >= len(body) {
				return nil, fmt.Errorf("short \\x escape")
			}
			value, err := strconv.ParseUint(body[i+1:i+3], 16, 8)
			if err != nil {
				return nil, fmt.Errorf("bad \\x escape: %w", err)
			}
			if byteMode {
				out = append(out, byte(value))
			} else {
				appendRune(rune(value))
			}
			i += 2
		case 'u', 'U':
			if byteMode {
				return nil, fmt.Errorf("unsupported escape \\%c in bytes literal", body[i])
			}
			width := 4
			if body[i] == 'U' {
				width = 8
			}
			if i+width >= len(body) {
				return nil, fmt.Errorf("short \\%c escape", body[i])
			}
			value, err := strconv.ParseUint(body[i+1:i+1+width], 16, 32)
			if err != nil {
				return nil, fmt.Errorf("bad \\%c escape: %w", body[i], err)
			}
			appendRune(rune(value))
			i += width
		case '0', '1', '2', '3', '4', '5', '6', '7':
			digits := 0
			value := 0
			for digits < 3 && i < len(body) && body[i] >= '0' && body[i] <= '7' {
				value = value*8 + int(body[i]-'0')
				i++
				digits++
			}
			i--
			if byteMode {
				out = append(out, byte(value))
			} else {
				appendRune(rune(value))
			}
		default:
			return nil, fmt.Errorf("unsupported escape \\%c", body[i])
		}
	}
	return out, nil
}

func parseStrLiteral(raw string) ([]byte, error) {
	if len(raw) < 2 {
		return nil, fmt.Errorf("literal too short")
	}
	quote := raw[0]
	if quote != '\'' && quote != '"' {
		return nil, fmt.Errorf("literal does not start with a quote")
	}
	if raw[len(raw)-1] != quote {
		return nil, fmt.Errorf("literal does not end with the opening quote")
	}
	return parseLiteralBody(raw[1:len(raw)-1], false)
}

func parseBytesLiteral(raw string) ([]byte, error) {
	if len(raw) < 2 {
		return nil, fmt.Errorf("bytes literal too short")
	}
	quote := raw[1]
	if quote != '\'' && quote != '"' {
		return nil, fmt.Errorf("bytes literal does not start with a quote")
	}
	if raw[len(raw)-1] != quote {
		return nil, fmt.Errorf("bytes literal does not end with the opening quote")
	}
	return parseLiteralBody(raw[2:len(raw)-1], true)
}
