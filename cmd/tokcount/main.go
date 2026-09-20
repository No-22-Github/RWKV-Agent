// Command tokcount counts tokens with the real RWKV World vocabulary using
// the same in-process tokenizer the harness uses. Reads text files given as
// arguments (or stdin when no file is given) and prints "<count>\t<path>"
// per input, or just the count for stdin.
package main

import (
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

func main() {
	vocab := "third_party/rwkv-mobile/assets/rwkv_vocab_v20230424.txt"
	if len(os.Args) > 1 && os.Args[1] == "--vocab" {
		vocab = os.Args[2]
		os.Args = append([]string{os.Args[0]}, os.Args[3:]...)
	}
	if _, err := os.Stat(vocab); err != nil {
		// Fall back to the repo root relative to the binary (dist/ sits one
		// level below), so the tool works from any working directory.
		if executable, execErr := os.Executable(); execErr == nil {
			candidate := filepath.Join(filepath.Dir(filepath.Dir(executable)), vocab)
			if _, statErr := os.Stat(candidate); statErr == nil {
				vocab = candidate
			}
		}
	}
	world, err := tokenizer.OpenWorldCached(vocab)
	if err != nil {
		fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
		os.Exit(1)
	}
	if len(os.Args) < 2 {
		data, err := io.ReadAll(os.Stdin)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: read stdin: %v\n", err)
			os.Exit(1)
		}
		fmt.Println(world.Count(string(data)))
		return
	}
	for _, path := range os.Args[1:] {
		data, err := os.ReadFile(path)
		if err != nil {
			fmt.Fprintf(os.Stderr, "tokcount: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("%d\t%s\n", world.Count(string(data)), path)
	}
}
