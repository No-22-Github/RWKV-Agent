package bench

import (
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab/runs"
)

const usage = `rwkv-lab bench — sampling sweep tools

usage: rwkv-lab bench <command> [flags]

  sweep      run a grid of sampling arms x suites x replicas against the endpoint
  rank       rank the arms that came back, by the pre-registered rules
`

// Run dispatches a bench subcommand.
func Run(args []string) int {
	if len(args) == 0 {
		fmt.Fprint(os.Stderr, usage)
		return 2
	}
	switch args[0] {
	case "sweep":
		return runSweepCmd(args[1:])
	case "rank":
		return runRankCmd(args[1:])
	case "-h", "--help", "help":
		fmt.Print(usage)
		return 0
	default:
		fmt.Fprintf(os.Stderr, "rwkv-lab bench: unknown command %q\n\n%s", args[0], usage)
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

func runSweepCmd(argv []string) int {
	args := SweepArgs{
		Suites:         []string{"workbank", "bfcl-product"},
		K:              "0",
		Model:          "rwkv-g1k-7b-temp-3601",
		APIURL:         "https://api-7b.rwkvos.com/v1",
		Prefix:         "g1k",
		MaxConcurrency: 64,
		MaxAttempts:    2,
	}
	var arms, suites string
	fs := newFlagSet("bench sweep",
		"Run a grid of sampling arms x suites x replicas against an RWKV endpoint.")
	fs.StringVar(&args.Out, "out", "", "output directory for the run directories (required)")
	fs.StringVar(&arms, "arms", "", "comma-separated arm names: "+strings.Join(runs.ArmNames(), ", "))
	fs.StringVar(&suites, "suites", "workbank,bfcl-product", "comma-separated suite names")
	fs.StringVar(&args.K, "k", "0", "replica indices: 0 | 0-2 | 1,2")
	fs.StringVar(&args.Model, "model", "rwkv-g1k-7b-temp-3601", "model id")
	fs.StringVar(&args.APIURL, "api-url", "https://api-7b.rwkvos.com/v1", "endpoint base URL")
	fs.StringVar(&args.Prefix, "prefix", "g1k", "run directory prefix")
	fs.StringVar(&args.StateID, "state-id", "",
		"rwkv_lightning state id attached to every run of this invocation")
	fs.IntVar(&args.MaxConcurrency, "max-concurrency", 64,
		"total in-flight cases across concurrently running suites")
	fs.IntVar(&args.MaxAttempts, "max-attempts", 2,
		"whole-run attempts on infra errors; the last attempt is kept")
	fs.BoolVar(&args.DryRun, "dry-run", false, "print the commands only")
	if err := runs.ParseInterspersed(fs, argv, map[string]bool{"dry-run": true}); err != nil {
		return 2
	}
	if args.Out == "" || arms == "" {
		fmt.Fprintln(os.Stderr, "error: --out and --arms are required")
		return 2
	}
	args.Arms = strings.Split(arms, ",")
	args.Suites = strings.Split(suites, ",")
	return RunSweep(args)
}

func runRankCmd(argv []string) int {
	args := RankArgs{Prefix: "g1k", Baseline: "greedy", Floor: 5}
	fs := newFlagSet("bench rank",
		"Rank sampling arms from sweep runs using the pre-registered rules.")
	fs.StringVar(&args.Prefix, "prefix", "g1k", "run directory prefix")
	fs.StringVar(&args.Baseline, "baseline", "greedy", "arm to pair against")
	fs.IntVar(&args.Floor, "floor", 5, "workbank resolution floor")
	fs.StringVar(&args.Save, "save", "", "also write the markdown here")
	if err := runs.ParseInterspersed(fs, argv, nil); err != nil {
		return 2
	}
	rest := fs.Args()
	if len(rest) != 1 {
		fmt.Fprintln(os.Stderr, "error: usage: rwkv-lab bench rank OUT_DIR [--prefix g1k]")
		return 2
	}
	args.Out = rest[0]
	return RunRank(args)
}
