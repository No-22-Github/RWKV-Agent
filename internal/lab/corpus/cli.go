package corpus

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
)

const usage = `rwkv-lab corpus — distillation corpus tools

usage: rwkv-lab corpus <command> [flags]

  paths      pick teacher paths out of agent-eval runs -> replay script
  render     replay a script through the eval harness -> training rows
  rows       cut training rows out of a scripted run's trace
  decontam   flag candidates that are too close to the test bank
  pack       validate rows and pack a dataset directory
  loadcheck  load a bank through the real eval loader (unknown fields are fatal)
`

// Run dispatches a corpus subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "paths":
		return runPathsCmd(args[1:])
	case "render":
		return runRenderCmd(args[1:])
	case "rows":
		return runRowsCmd(args[1:])
	case "decontam":
		return runDecontamCmd(args[1:])
	case "pack":
		return runPackCmd(args[1:])
	case "loadcheck":
		return runLoadcheckCmd(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab corpus: unknown command %q\n\n%s", args[0], usage)
		return 2
	}
}

func newFlagSet(name, description string) *flag.FlagSet {
	fs := flag.NewFlagSet(name, flag.ContinueOnError)
	fs.SetOutput(os.Stderr)
	fs.Usage = func() {
		fmt.Fprintf(os.Stderr, "%s\n\nusage: rwkv-lab %s\n\nflags:\n", description, name)
		fs.PrintDefaults()
	}
	return fs
}

// The flag sets are built by their own functions so tests can assert how the
// command line parses without running the command (§6 M1 ports the CLI tests
// from test_corpus.py).

func pathsFlagSet(args *PathsArgs, runs *stringList) *flag.FlagSet {
	fs := newFlagSet("corpus paths",
		"Pick teacher paths out of agent-eval runs and write them as a replay script.")
	fs.Var(runs, "run", "teacher agent-eval run (repeatable)")
	fs.StringVar(&args.Out, "out", "", "new script JSONL")
	fs.StringVar(&args.Report, "report", "", "optional per-case JSONL: pass@k, kept paths, drop reasons")
	fs.IntVar(&args.MaxPerCase, "max-per-case", 2, "paths to keep per case")
	return fs
}

func runPathsCmd(argv []string) int {
	var args PathsArgs
	var runs stringList
	fs := pathsFlagSet(&args, &runs)
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	if len(runs) == 0 || args.Out == "" {
		fmt.Fprintln(os.Stderr, "error: --run and --out are required")
		return 2
	}
	args.Run = runs
	return RunPaths(args)
}

func runRowsCmd(argv []string) int {
	var args RowsArgs
	fs := newFlagSet("corpus rows",
		"Cut training rows out of a scripted agent-eval run's trace.")
	fs.StringVar(&args.Run, "run", "", "agent-eval output directory (run.json, summary.json, trace.jsonl)")
	fs.StringVar(&args.Script, "script", "", "the JSONL script the run replayed")
	fs.StringVar(&args.Cases, "cases", "", "bank directory holding the cases the run replayed (labels, expectations)")
	fs.StringVar(&args.Source, "source", "", "dataset name every row records, e.g. base700 (required)")
	fs.StringVar(&args.Out, "out", "", "new JSONL file for the rendered rows")
	fs.StringVar(&args.Rejects, "rejects", "", "optional JSONL file listing rejected cases and why")
	fs.BoolVar(&args.RequirePass, "require-pass", true,
		"reject cases whose teacher trajectory fails the case expectations")
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	return RunRows(args)
}

func renderFlagSet(args *RenderArgs) *flag.FlagSet {
	fs := newFlagSet("corpus render",
		"Render corpus rows by replaying teacher actions through the real eval harness.")
	fs.StringVar(&args.Records, "records", "", "normalized records JSONL")
	fs.StringVar(&args.Cases, "cases", "", "bank directory the --script case IDs resolve against")
	fs.StringVar(&args.Script, "script", "", "replay script (paths command output)")
	fs.StringVar(&args.Out, "out", "", "new output directory")
	fs.StringVar(&args.Source, "source", "", "dataset name every row records, e.g. base700 (required)")
	fs.StringVar(&args.TagMap, "tag-map", DefaultTagMap(),
		"records mode: label normalisation map (task types, behaviours)")
	fs.StringVar(&args.CLI, "cli", filepath.Join(RepoRoot(), "bin", "rwkv-cli"), "rwkv-cli binary")
	fs.IntVar(&args.Parallelism, "parallelism", 32, "agent-eval case parallelism")
	fs.BoolVar(&args.AllowTestBank, "allow-test-bank", false,
		"permit --cases inside bench/workbank (pipeline smoke tests; never train on the output)")
	fs.BoolVar(&args.KeepFailing, "keep-failing", false,
		"also emit rows whose teacher trajectory fails the case expectations")
	return fs
}

func runRenderCmd(argv []string) int {
	var args RenderArgs
	fs := renderFlagSet(&args)
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	if args.Out == "" {
		fmt.Fprintln(os.Stderr, "error: --out is required")
		return 2
	}
	args.Extra = fs.Args()
	return RunRender(args)
}

func decontamFlagSet(args *DecontamArgs) *flag.FlagSet {
	fs := newFlagSet("corpus decontam",
		"Flag distillation cases that are too close to the test bank.")
	fs.StringVar(&args.Test, "test", "", "test bank directory (case.json files)")
	fs.StringVar(&args.Candidates, "candidates", "", "candidate bank directory")
	fs.StringVar(&args.Records, "records", "", "or: normalized records JSONL")
	fs.Float64Var(&args.PromptThreshold, "prompt-threshold", 0.35, "prompt similarity threshold")
	fs.Float64Var(&args.FilesThreshold, "files-threshold", 0.30, "fixture similarity threshold")
	fs.Float64Var(&args.NamesThreshold, "names-threshold", 0.30, "identifier similarity threshold")
	fs.Float64Var(&args.Boilerplate, "boilerplate", 0.05,
		"ignore features present in more than this share of test cases")
	fs.StringVar(&args.Report, "report", "", "optional JSONL with every candidate's scores")
	return fs
}

func runDecontamCmd(argv []string) int {
	var args DecontamArgs
	fs := decontamFlagSet(&args)
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	if args.Test == "" {
		fmt.Fprintln(os.Stderr, "error: --test is required")
		return 2
	}
	if (args.Candidates != "") == (args.Records != "") {
		fmt.Fprintln(os.Stderr, "error: give exactly one of --candidates or --records")
		return 2
	}
	return RunDecontam(args)
}

// stringList is a repeatable string flag, matching argparse's action="append".
type stringList []string

func (s *stringList) String() string { return fmt.Sprintf("%v", []string(*s)) }

func (s *stringList) Set(value string) error {
	*s = append(*s, value)
	return nil
}
