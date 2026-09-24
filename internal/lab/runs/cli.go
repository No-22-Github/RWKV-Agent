package runs

import (
	"flag"
	"fmt"
	"os"
	"strings"
)

const usage = `rwkv-lab run — run analysis tools

usage: rwkv-lab run <command> [flags]

  wire       read-only wire audit of one or more runs
  check      validity gate for one run (exit 1 when a gate fails)
  gate       layered failure attribution: is the score a capability reading?
  audit      mechanical failure observations (flags overlap)
  compare    compare two runs or two ledger configs case by case
  ledger     append-only scoring ledger: ingest | matrix
  replicate  summarize an explicit set of comparable repeated runs
`

// Run dispatches a run subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "wire":
		return runWireCmd(args[1:])
	case "check":
		return runCheckCmd(args[1:])
	case "gate":
		return runGateCmd(args[1:])
	case "audit":
		return runAuditCmd(args[1:])
	case "compare":
		return runCompareCmd(args[1:])
	case "ledger":
		return runLedgerCmd(args[1:])
	case "replicate":
		return runReplicateCmd(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab run: unknown command %q\n\n%s", args[0], usage)
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

// ParseInterspersed parses argv with flags and positionals in any order, which
// argparse allows and Go's flag package does not (it stops at the first
// non-flag). boolFlags names the flags that take no value, so a following token
// is not mistaken for one.
func ParseInterspersed(fs *flag.FlagSet, argv []string, boolFlags map[string]bool) error {
	var flags, positional []string
	for i := 0; i < len(argv); i++ {
		arg := argv[i]
		if arg == "--" {
			positional = append(positional, argv[i+1:]...)
			break
		}
		if len(arg) > 1 && arg[0] == '-' {
			name := strings.TrimLeft(arg, "-")
			flags = append(flags, arg)
			if strings.Contains(name, "=") || boolFlags[name] {
				continue
			}
			if i+1 < len(argv) {
				flags = append(flags, argv[i+1])
				i++
			}
			continue
		}
		positional = append(positional, arg)
	}
	return fs.Parse(append(flags, positional...))
}

func runWireCmd(argv []string) int {
	var args WireArgs
	fs := newFlagSet("run wire", "Read-only wire audit. Official case passes are never replaced by text heuristics.")
	fs.StringVar(&args.Bank, "bank", "", "merged bank file (build command output) for the answer-text diagnostic")
	fs.BoolVar(&args.JSON, "json", false, "emit the reports as JSON")
	if err := ParseInterspersed(fs, argv, map[string]bool{"json": true}); err != nil {
		return 2
	}
	args.Runs = fs.Args()
	if len(args.Runs) == 0 {
		fmt.Fprintln(os.Stderr, "error: at least one run directory is required")
		return 2
	}
	return RunWire(args)
}

func runCheckCmd(argv []string) int {
	args := CheckArgs{MaxSteps: 16, MaxTokens: 4096, DecisionMaxTokens: 2048, CaseTimeoutSeconds: 1800}
	fs := newFlagSet("run check", "Validity gate for one agent-eval run.")
	fs.StringVar(&args.Arm, "arm", "", "sampling arm (required)")
	fs.BoolVar(&args.RWKV, "rwkv", false, "RWKV run: require wire_preset g1k")
	fs.BoolVar(&args.Primitive, "primitive", false, "Primitive suite: skip the g1k wire gate")
	fs.IntVar(&args.Cases, "cases", 0, "expected case count")
	fs.IntVar(&args.MaxSteps, "max-steps", 16, "expected harness.max_steps")
	fs.IntVar(&args.MaxTokens, "max-tokens", 4096, "expected answer_max_output_tokens")
	fs.IntVar(&args.DecisionMaxTokens, "decision-max-tokens", 2048, "expected decision_max_output_tokens")
	fs.IntVar(&args.CaseTimeoutSeconds, "case-timeout-seconds", 1800, "expected case_timeout_seconds")
	boolFlags := map[string]bool{"rwkv": true, "primitive": true}
	if err := ParseInterspersed(fs, argv, boolFlags); err != nil {
		return 2
	}
	rest := fs.Args()
	if len(rest) != 1 || args.Arm == "" {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab run check RUN_DIR --arm NAME [--rwkv]")
		return 2
	}
	args.RunDir = rest[0]
	args.HasCases = flagWasSet(fs, "cases")
	return RunCheck(args)
}

func runGateCmd(argv []string) int {
	var args GateArgs
	fs := newFlagSet("run gate",
		"Layered failure attribution: is a run's score a capability reading at all?")
	fs.StringVar(&args.Label, "label", "", "name for this model/config group")
	fs.StringVar(&args.JSON, "json", "", "write the full report here")
	if err := ParseInterspersed(fs, argv, nil); err != nil {
		return 2
	}
	args.Runs = fs.Args()
	if len(args.Runs) == 0 {
		fmt.Fprintln(os.Stderr, "error: at least one run directory is required")
		return 2
	}
	return RunGate(args)
}

func runAuditCmd(argv []string) int {
	fs := newFlagSet("run audit", "Mechanical failure observations; overlapping flags are not causal buckets.")
	if err := ParseInterspersed(fs, argv, nil); err != nil {
		return 2
	}
	rest := fs.Args()
	if len(rest) != 1 {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab run audit RUN_DIR")
		return 2
	}
	return RunAudit(AuditArgs{Run: rest[0]})
}

func runCompareCmd(argv []string) int {
	fs := newFlagSet("run compare",
		"Compare two runs (directories) or two config names (ledger) case by case.")
	if err := ParseInterspersed(fs, argv, nil); err != nil {
		return 2
	}
	rest := fs.Args()
	if len(rest) != 2 {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab run compare A B")
		return 2
	}
	return RunCompare(CompareArgs{A: rest[0], B: rest[1]})
}

func runLedgerCmd(argv []string) int {
	if len(argv) == 0 {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab run ledger {ingest,matrix}")
		return 2
	}
	switch argv[0] {
	case "ingest":
		args := IngestArgs{LedgerDir: DefaultLedgerDir()}
		fs := newFlagSet("run ledger ingest", "Ingest one run directory into the ledger.")
		fs.StringVar(&args.ConfigName, "config-name", "", "logical config name for this run (required)")
		fs.IntVar(&args.KIndex, "k-index", 0, "replica index (0-based) of this run (required)")
		fs.StringVar(&args.BankVersion, "bank-version", "",
			"bank_version the run was produced from (e.g. sha256:...)")
		fs.StringVar(&args.LedgerDir, "ledger-dir", DefaultLedgerDir(),
			"ledger directory holding runs.jsonl and cases.jsonl")
		if err := ParseInterspersed(fs, argv[1:], nil); err != nil {
			return 2
		}
		rest := fs.Args()
		if len(rest) != 1 || args.ConfigName == "" || !flagWasSet(fs, "k-index") {
			fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab run ledger ingest --config-name NAME --k-index N RUN_DIR")
			return 2
		}
		args.RunDir = rest[0]
		return RunLedgerIngest(args)
	case "matrix":
		args := MatrixArgs{LedgerDir: DefaultLedgerDir()}
		fs := newFlagSet("run ledger matrix", "Aggregate the ledger into a markdown matrix.")
		fs.StringVar(&args.BankVersion, "bank-version", "", "only include runs with this bank_version")
		fs.StringVar(&args.LedgerDir, "ledger-dir", DefaultLedgerDir(),
			"ledger directory holding runs.jsonl and cases.jsonl")
		if err := ParseInterspersed(fs, argv[1:], nil); err != nil {
			return 2
		}
		return RunLedgerMatrix(args)
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab run ledger: unknown command %q\n", argv[0])
		return 2
	}
}

func runReplicateCmd(argv []string) int {
	args := ReplicateArgs{K: 3}
	fs := newFlagSet("run replicate",
		"Summarize an explicit, complete set of comparable repeated runs, offline.")
	fs.IntVar(&args.K, "k", 3, "number of distinct runs required")
	fs.StringVar(&args.Out, "out", "", "output JSON path (required)")
	if err := ParseInterspersed(fs, argv, nil); err != nil {
		return 2
	}
	args.Runs = fs.Args()
	if len(args.Runs) == 0 || args.Out == "" {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab run replicate RUN... --k N --out FILE")
		return 2
	}
	return RunReplicate(args)
}

// flagWasSet reports whether a flag appeared on the command line, which
// argparse distinguishes from a flag left at its default.
func flagWasSet(fs *flag.FlagSet, name string) bool {
	seen := false
	fs.Visit(func(f *flag.Flag) {
		if f.Name == name {
			seen = true
		}
	})
	return seen
}
