// Command rwkv-lab is the repository's development tooling: the corpus,
// workbank, run-analysis and state utilities that used to be Python scripts.
//
// It is deliberately separate from rwkv-cli. rwkv-cli is the product (the
// agent, the evaluators, the server); rwkv-lab is the bench-side toolbox that
// reads the artifacts rwkv-cli produces. See
// docs/design/go-tooling-migration.md §3.
package main

import (
	"fmt"
	"os"

	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/lab/bank"
	"github.com/no22/RWKV-Agent/internal/lab/bench"
	"github.com/no22/RWKV-Agent/internal/lab/corpus"
	"github.com/no22/RWKV-Agent/internal/lab/exam"
	"github.com/no22/RWKV-Agent/internal/lab/geval"
	"github.com/no22/RWKV-Agent/internal/lab/runs"
	"github.com/no22/RWKV-Agent/internal/lab/state"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
	buildversion "github.com/no22/RWKV-Agent/internal/version"
)

const usage = `rwkv-lab — development tooling for the RWKV-Agent bench

usage: rwkv-lab <group> <command> [flags]

  bank    lint | dedup | build | coverage | calibrate | hitcheck | verify
  corpus  paths | render | rows | decontam
  exam    build | lint | import-builtin | select-quick | panel
  geval   build | decontam | run | score | report  (general-ability eval)
  run     wire | check | gate | audit | compare | ledger | replicate
  bench   sweep | rank
  state   run | probe | sanity
  tokcount  count tokens with the RWKV World vocabulary (--jsonl: per-line string fields; --vocab-sha256: print its digest)

Run "rwkv-lab <group> <command> --help" for a command's flags.
Also: rwkv-lab --version | version
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
	case "exam":
		return exam.Run(args[1:])
	case "geval":
		return geval.Run(args[1:])
	case "run":
		return runs.Run(args[1:])
	case "bench":
		return bench.Run(args[1:])
	case "state":
		return state.Run(args[1:])
	case "tokcount":
		jsonl := false
		rest := args[1:]
		for len(rest) > 0 {
			if rest[0] == "--jsonl" {
				jsonl, rest = true, rest[1:]
			} else if rest[0] == "--vocab-sha256" {
				fmt.Println(tokenizer.World().VocabSHA256())
				return 0
			} else {
				break
			}
		}
		return lab.RunTokcount(jsonl, rest)
	case "--version", "version":
		buildversion.Print(os.Stdout, "rwkv-lab")
		return 0
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab: unknown group %q\n\n%s", args[0], usage)
		return 2
	}
}
