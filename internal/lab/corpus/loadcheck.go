package corpus

import (
	"flag"
	"fmt"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// The eval loader decodes case.json with DisallowUnknownFields, so a field the
// schema does not know (a hand-written one, or a typo) makes agent-eval refuse
// the whole bank: "load Agent eval cases: decode ... unknown field". The static
// gates do not see it — lint checks tags and vocabulary, verify runs the case —
// and a teacher run that dies this way costs a full pass, so it is worth its own
// five-second check between S2 and S4.

// LoadcheckArgs are the `corpus loadcheck` flags.
type LoadcheckArgs struct {
	Cases string
}

func loadcheckFlagSet(args *LoadcheckArgs) *flag.FlagSet {
	fs := newFlagSet("corpus loadcheck",
		"Load a bank through the real eval loader (unknown fields are fatal).")
	fs.StringVar(&args.Cases, "cases", "", "bank directory to load")
	return fs
}

func runLoadcheckCmd(argv []string) int {
	var args LoadcheckArgs
	fs := loadcheckFlagSet(&args)
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	if args.Cases == "" {
		fmt.Fprintln(stderr, "error: --cases is required")
		return 2
	}
	return RunLoadcheck(args)
}

// RunLoadcheck is the `corpus loadcheck` command.
func RunLoadcheck(args LoadcheckArgs) int {
	cases, err := eval.LoadCasesDir(args.Cases, true)
	if err != nil {
		fmt.Fprintf(stderr, "loadcheck: %s does not load through the eval loader:\n  %v\n", args.Cases, err)
		return 1
	}
	// A count is cheap evidence that the directory was not simply empty.
	if len(cases) == 0 {
		fmt.Fprintf(stderr, "loadcheck: %s has no cases\n", args.Cases)
		return 1
	}
	fmt.Printf("loadcheck: %d case(s) load\n", len(cases))
	return 0
}
