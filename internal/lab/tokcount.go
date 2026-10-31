package lab

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

// Count tokens with the real RWKV World vocabulary, using the same in-process
// tokenizer the harness uses. This was cmd/tokcount, merged into rwkv-lab
// because a one-purpose binary for counting tokens is not worth shipping.

// defaultVocab is the shipped vocabulary.
const defaultVocab = "third_party/rwkv-mobile/assets/rwkv_vocab_v20230424.txt"

// OpenWorld opens the shipped World vocabulary, resolving the path against
// the repository root fallback the CLI uses.
func OpenWorld() (*tokenizer.World, error) {
	path := defaultVocab
	if _, err := os.Stat(path); err != nil {
		if candidate := filepath.Join(RepoRoot(), path); FileExists(candidate) {
			path = candidate
		}
	}
	return tokenizer.OpenWorldCached(path)
}

// RunTokcount is the `tokcount` command. With jsonl set, every input line is
// a JSON object and each top-level string field gets a "<field>_tok" count
// added; other fields pass through.
func RunTokcount(vocab string, jsonl bool, paths []string) int {
	if vocab == "" {
		vocab = defaultVocab
	}
	if _, err := os.Stat(vocab); err != nil {
		// Fall back to the repository root, so the tool works from any working
		// directory.
		candidate := filepath.Join(RepoRoot(), vocab)
		if _, statErr := os.Stat(candidate); statErr == nil {
			vocab = candidate
		}
	}
	world, err := tokenizer.OpenWorldCached(vocab)
	if err != nil {
		fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
		return 1
	}
	if jsonl {
		return tokcountJSONL(world, paths)
	}
	if len(paths) == 0 {
		data, err := io.ReadAll(os.Stdin)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: read stdin: %v\n", err)
			return 1
		}
		fmt.Println(world.Count(string(data)))
		return 0
	}
	for _, path := range paths {
		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
			return 1
		}
		fmt.Printf("%d\t%s\n", world.Count(string(data)), path)
	}
	return 0
}

func tokcountJSONL(world *tokenizer.World, paths []string) int {
	inputs := []io.Reader{os.Stdin}
	if len(paths) > 0 {
		inputs = inputs[:0]
		for _, path := range paths {
			f, err := os.Open(path)
			if err != nil {
				fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
				return 1
			}
			defer f.Close()
			inputs = append(inputs, f)
		}
	}
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()
	// Keep "<think>" and "<tool_call>" readable instead of \u003c escapes.
	encoder := json.NewEncoder(out)
	encoder.SetEscapeHTML(false)
	for _, input := range inputs {
		scanner := bufio.NewScanner(input)
		scanner.Buffer(make([]byte, 1<<20), 1<<30)
		for line := 1; scanner.Scan(); line++ {
			var row map[string]any
			if err := json.Unmarshal(scanner.Bytes(), &row); err != nil {
				fmt.Fprintf(os.Stderr, "tokcount: line %d: %v\n", line, err)
				return 1
			}
			counts := map[string]int{}
			for key, value := range row {
				if text, ok := value.(string); ok {
					counts[key+"_tok"] = world.Count(text)
				}
			}
			for key, n := range counts {
				row[key] = n
			}
			if err := encoder.Encode(row); err != nil {
				fmt.Fprintf(os.Stderr, "tokcount: line %d: %v\n", line, err)
				return 1
			}
		}
		if err := scanner.Err(); err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
			return 1
		}
	}
	return 0
}
