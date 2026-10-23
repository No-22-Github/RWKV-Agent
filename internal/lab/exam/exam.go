// Package exam assembles the exam: one list of cases drawn from every
// authored collection (workbank, the holdout, the probes, the imported
// built-in suites), with uniform derived metadata, a content hash, and a
// generated summary table. See bench/exam/SUITES.md.
package exam

import (
	"fmt"
	"os"
)

const usage = `rwkv-lab exam — the exam manifests under bench/exam

usage: rwkv-lab exam <command> [flags]

  build           regenerate full.json, quick.json, suites/*.json and SUITES.md (--check: verify only)
  lint            check the manifests against the case files and the exam rules
  import-builtin  export the built-in bfcl-product and boundary suites to case.json files
  select-quick    pick the quick exam from the full one and local run history
  panel           score runs by task kind, difficulty, language and source
  rescore         re-judge finished runs under the current scorer and case files
`

// Run dispatches an exam subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "build":
		return runBuild(args[1:])
	case "lint":
		return runLint(args[1:])
	case "import-builtin":
		return runImportBuiltin(args[1:])
	case "select-quick":
		return runSelectQuick(args[1:])
	case "panel":
		return runPanel(args[1:])
	case "rescore":
		return runRescore(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab exam: unknown command %q\n\n%s", args[0], usage)
		return 2
	}
}
