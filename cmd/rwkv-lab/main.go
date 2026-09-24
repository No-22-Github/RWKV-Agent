// Command rwkv-lab is the repository's development tooling: the corpus,
// workbank, run-analysis and state utilities that used to be Python scripts.
//
// It is deliberately separate from rwkv-cli. rwkv-cli is the product (the
// agent, the evaluators, the server); rwkv-lab is the bench-side toolbox that
// reads the artifacts rwkv-cli produces. See
// docs/go-tooling-migration.md §3.
package main

import (
	"fmt"
	"os"

	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/lab/bank"
	"github.com/no22/RWKV-Agent/internal/lab/bench"
	"github.com/no22/RWKV-Agent/internal/lab/corpus"
	"github.com/no22/RWKV-Agent/internal/lab/runs"
	"github.com/no22/RWKV-Agent/internal/lab/state"
)

const usage = `rwkv-lab — development tooling for the RWKV-Agent bench

usage: rwkv-lab <group> <command> [flags]

  bank    lint | dedup | build | coverage | calibrate | hitcheck | verify
  corpus  paths | render | rows | decontam
  run     wire | check | gate | audit | compare | ledger | replicate
  bench   sweep | rank
  state   run | probe | sanity
  tokcount  count tokens with the RWKV World vocabulary

Run "rwkv-lab <group> <command> --help" for a command's flags.
`

func main() {
	os.Exit(run(os.Args[1:]))
}

func run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "bank":
		return bank.Run(args[1:])
	case "corpus":
		return corpus.Run(args[1:])
	case "run":
		return runs.Run(args[1:])
	case "bench":
		return bench.Run(args[1:])
	case "state":
		return state.Run(args[1:])
	case "tokcount":
		vocab := ""
		rest := args[1:]
		if len(rest) > 1 && rest[0] == "--vocab" {
			vocab, rest = rest[1], rest[2:]
		}
		return lab.RunTokcount(vocab, rest)
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab: unknown group %q\n\n%s", args[0], usage)
		return 2
	}
}
