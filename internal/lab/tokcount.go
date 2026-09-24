package lab

import (
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

// RunTokcount is the `tokcount` command.
func RunTokcount(vocab string, paths []string) int {
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
