package lab

import (
	"fmt"
	"io"
	"os"

	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

// Count tokens with the real RWKV World vocabulary, using the same in-process
// tokenizer the harness uses. This was cmd/tokcount, merged into rwkv-lab
// because a one-purpose binary for counting tokens is not worth shipping.

// RunTokcount is the `tokcount` command. With jsonl set, every input line is
// a JSON object and each top-level string field gets a "<field>_tok" count
// added; other fields pass through.
func RunTokcount(jsonl bool, paths []string) int {
	world := tokenizer.World()
	if jsonl {
		return tokcountJSONL(paths)
	}
	if len(paths) == 0 {
		data, err := io.ReadAll(os.Stdin)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: read stdin: %v\n", err)
			return 1
		}
		fmt.Println(world.CountBytes(data))
		return 0
	}
	for _, path := range paths {
		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
			return 1
		}
		fmt.Printf("%d\t%s\n", world.CountBytes(data), path)
	}
	return 0
}

func tokcountJSONL(paths []string) int {
	if len(paths) == 0 {
		return tokcountStream(os.Stdin)
	}
	for _, path := range paths {
		f, err := os.Open(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
			return 1
		}
		code := tokcountStream(f)
		f.Close()
		if code != 0 {
			return code
		}
	}
	return 0
}

func tokcountStream(input io.Reader) int {
	if err := tokenizer.World().CountJSONL(os.Stdout, input); err != nil {
		fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
		return 1
	}
	return 0
}
