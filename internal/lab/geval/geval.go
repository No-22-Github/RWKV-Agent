// Package geval is the general-ability eval: public benchmarks (IFEval in
// English and Chinese, MT-Bench in English and Chinese, GSM8K, MATH-500,
// C-Eval and CMMLU) run against an RWKV model in the think-sft training
// format, as a complement to the exam, which only covers our own tools. See
// docs/evaluations/general-eval-20261031/README.md.
//
// The data lives in bench/general-eval/ (built from the public sources by
// `geval build`); runs land in local/runs/ with one JSON line per item, so
// an interrupted run resumes where it stopped.
package geval

import (
	"fmt"
	"os"
)

const usage = `rwkv-lab geval — general-ability eval (IFEval, MT-Bench, GSM8K, MATH-500, C-Eval, CMMLU)

usage: rwkv-lab geval <command> [flags]

  build     sample the public sources into bench/general-eval/<version>/items.jsonl
  decontam  n-gram overlap of every item against a training rows file
  run       generate answers against an RWKV (or chat) endpoint; resumable
  score     judge and score a run (MT-Bench and MATH fallback use an LLM judge)
  report    side-by-side table of scored runs
`

// Run dispatches a geval subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "build":
		return runBuild(args[1:])
	case "decontam":
		return runDecontam(args[1:])
	case "run":
		return runRun(args[1:])
	case "score":
		return runScore(args[1:])
	case "report":
		return runReport(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab geval: unknown command %q\n\n%s", args[0], usage)
		return 2
	}
}
