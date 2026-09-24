package state

import (
	"flag"
	"fmt"
	"os"

	"github.com/no22/RWKV-Agent/internal/lab/runs"
)

const usage = `rwkv-lab state — RWKV time-state tools

usage: rwkv-lab state <command> [flags]

  run      run a state evaluation with serial canary fingerprints
  probe    greedy continuation probe against the training corpus
  sanity   magnitude gate for uploaded time-states (exit 1 when one fails)
`

// Run dispatches a state subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "run":
		return runRunCmd(args[1:])
	case "probe":
		return runProbeCmd(args[1:])
	case "sanity":
		return runSanityCmd(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab state: unknown command %q\n\n%s", args[0], usage)
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

func runSanityCmd(argv []string) int {
	args := SanityArgs{WarnRMS: 0.05, MaxRMS: 2.0}
	fs := newFlagSet("state sanity",
		"Magnitude gate for uploaded RWKV time-states (g1k 7B layout: blocks.N.att.time_state).")
	fs.StringVar(&args.Reference, "reference", "",
		"known-good state; gate each candidate against its per-tensor RMS")
	fs.Float64Var(&args.WarnRMS, "warn-rms", 0.05,
		"warn above this median RMS (default 0.05, the coherent band)")
	fs.Float64Var(&args.MaxRMS, "max-rms", 2.0,
		"fail when median RMS exceeds this absolute ceiling (calibrated default 2.0)")
	fs.Float64Var(&args.MaxRatio, "max-ratio", 0,
		"additionally fail when median RMS exceeds the reference by this factor")
	fs.BoolVar(&args.Verbose, "verbose", false, "print every tensor")
	boolFlags := map[string]bool{"verbose": true}
	if err := runs.ParseInterspersed(fs, argv, boolFlags); err != nil {
		return 2
	}
	args.HasRatio = flagSet(fs, "max-ratio")
	args.States = fs.Args()
	if len(args.States) == 0 {
		fmt.Fprintln(os.Stderr, "error: at least one state file is required")
		return 2
	}
	return RunSanity(args)
}

func runRunCmd(argv []string) int {
	args := RunArgs{Suites: "workbank,boundary,bfcl", Root: DefaultRoot}
	fs := newFlagSet("state run",
		"Run a state evaluation with serial before/after fingerprints and file identity.")
	fs.StringVar(&args.StateID, "state-id", "", "uploaded state ID; empty uses zero state")
	fs.BoolVar(&args.Fast, "fast", false, "use the think-fast wire (sets its own history overrides)")
	fs.BoolVar(&args.LegacyHistory, "legacy-history", false, "keep the default history wire with --fast")
	fs.StringVar(&args.Wire, "wire", "", "extra wire overrides, e.g. nudge=none; incompatible with --fast")
	fs.BoolVar(&args.AllowCanaryDrift, "allow-canary-drift", false,
		"record strict canary drift and continue when the client-stop-effective fingerprint is stable")
	fs.StringVar(&args.Suites, "suites", "workbank,boundary,bfcl", "comma-separated suite names")
	fs.IntVar(&args.Parallelism, "parallelism", 0,
		"0 runs every case concurrently: Workbank 40, Boundary 18, BFCL 60")
	fs.StringVar(&args.Credentials, "credentials", "", "private JSON mapping of env names to secrets (required)")
	fs.StringVar(&args.Root, "root", DefaultRoot,
		"run root holding upload receipts, canaries and suite outputs")
	boolFlags := map[string]bool{"fast": true, "legacy-history": true, "allow-canary-drift": true}
	if err := runs.ParseInterspersed(fs, argv, boolFlags); err != nil {
		return 2
	}
	rest := fs.Args()
	if len(rest) != 1 || args.Credentials == "" {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab state run NAME --credentials FILE [--state-id ID]")
		return 2
	}
	args.Name = rest[0]
	if args.Fast && args.Wire != "" {
		fmt.Fprintln(os.Stderr, "error: --wire and --fast both set the wire overrides; pick one")
		return 2
	}
	return RunState(args)
}

func runProbeCmd(argv []string) int {
	args := ProbeArgs{
		Corpus:    "outputs/workspace-agent-700-state-tune-textonly/train.textonly.jsonl",
		Split:     "first",
		Rows:      24,
		Stride:    26,
		StateID:   "state-final.pth",
		MaxTokens: 96,
	}
	fs := newFlagSet("state probe",
		"Greedy continuation probe against the training corpus that produced a state.")
	fs.StringVar(&args.Corpus, "corpus", args.Corpus, "exported corpus JSONL")
	fs.StringVar(&args.Split, "split", "first",
		"first: probe the first decision point; last: probe the closing turn")
	fs.IntVar(&args.Rows, "rows", 24, "number of corpus rows to probe")
	fs.IntVar(&args.Stride, "stride", 26, "take every Nth row for a spread across scenarios")
	fs.StringVar(&args.StateID, "state-id", "state-final.pth", "uploaded state ID")
	fs.StringVar(&args.Credentials, "credentials", "", "private JSON mapping of env names to secrets (required)")
	fs.StringVar(&args.Output, "output", "", "output JSON path (required)")
	fs.IntVar(&args.MaxTokens, "max-tokens", 96, "generation ceiling per probe")
	if err := runs.ParseInterspersed(fs, argv, nil); err != nil {
		return 2
	}
	if args.Credentials == "" || args.Output == "" {
		fmt.Fprintln(os.Stderr, "error: --credentials and --output are required")
		return 2
	}
	if args.Split != "first" && args.Split != "last" {
		fmt.Fprintln(os.Stderr, "error: --split must be first or last")
		return 2
	}
	return RunProbe(args)
}

// flagSet reports whether a flag appeared on the command line.
func flagSet(fs *flag.FlagSet, name string) bool {
	seen := false
	fs.Visit(func(f *flag.Flag) {
		if f.Name == name {
			seen = true
		}
	})
	return seen
}
