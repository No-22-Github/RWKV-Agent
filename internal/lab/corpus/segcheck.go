package corpus

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"slices"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// SegcheckArgs are the `corpus segcheck` arguments.
type SegcheckArgs struct {
	Path    string
	Verbose bool
}

func segcheckFlagSet(args *SegcheckArgs) *flag.FlagSet {
	fs := lab.NewFlagSet("corpus segcheck",
		"Verify segment-wise tokenization matches whole-text tokenization and train segments follow Assistant:.")
	fs.BoolVar(&args.Verbose, "verbose", false, "print details for mismatched lines")
	return fs
}

func runSegcheckCmd(argv []string) int {
	var args SegcheckArgs
	fs := segcheckFlagSet(&args)
	if err := fs.Parse(argv); err != nil {
		return 2
	}
	if fs.NArg() > 0 {
		args.Path = fs.Arg(0)
	}
	if args.Path == "" {
		fmt.Fprintln(os.Stderr, "error: segments.jsonl path is required")
		return 2
	}
	return RunSegcheck(args)
}

type segmentItem struct {
	Text  string `json:"text"`
	Train bool   `json:"train"`
}

type segmentLine struct {
	Segments []segmentItem `json:"segments"`
}

// RunSegcheck executes the segcheck verification against a segments.jsonl file.
func RunSegcheck(args SegcheckArgs) int {
	file, err := os.Open(args.Path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "segcheck: open %s: %v\n", args.Path, err)
		return 1
	}
	defer file.Close()

	world, err := lab.OpenWorld()
	if err != nil {
		fmt.Fprintf(os.Stderr, "segcheck: load world tokenizer: %v\n", err)
		return 1
	}

	scanner := bufio.NewScanner(file)
	// Buffer up to 10MB per line for long trajectories
	buf := make([]byte, 1024*1024)
	scanner.Buffer(buf, 10*1024*1024)

	lineNum := 0
	mismatches := 0
	printedDetails := 0

	for scanner.Scan() {
		lineNum++
		line := scanner.Bytes()
		if len(line) == 0 {
			continue
		}

		var row segmentLine
		if err := json.Unmarshal(line, &row); err != nil {
			mismatches++
			if args.Verbose || printedDetails < 5 {
				fmt.Fprintf(os.Stderr, "line %d: invalid JSON: %v\n", lineNum, err)
				printedDetails++
			}
			continue
		}

		var wholeBuilder strings.Builder
		prefixOK := true
		var segTokens []int

		for i, seg := range row.Segments {
			if seg.Train {
				if i == 0 || !strings.HasSuffix(row.Segments[i-1].Text, "Assistant:") {
					prefixOK = false
				}
			}
			wholeBuilder.WriteString(seg.Text)
			segTokens = append(segTokens, world.Encode(seg.Text)...)
		}

		wholeText := wholeBuilder.String()
		wholeTokens := world.Encode(wholeText)

		tokensMatch := slices.Equal(wholeTokens, segTokens)
		if !prefixOK || !tokensMatch {
			mismatches++
			if args.Verbose || printedDetails < 5 {
				if !prefixOK {
					fmt.Fprintf(os.Stderr, "line %d: train segment not immediately preceded by 'Assistant:'\n", lineNum)
				}
				if !tokensMatch {
					fmt.Fprintf(os.Stderr, "line %d: token mismatch: whole=%d tokens, segments sum=%d tokens\n",
						lineNum, len(wholeTokens), len(segTokens))
				}
				printedDetails++
			}
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Fprintf(os.Stderr, "segcheck: read %s: %v\n", args.Path, err)
		return 1
	}

	fmt.Printf("segcheck: %s: %d lines checked, %d mismatches\n", args.Path, lineNum, mismatches)
	if mismatches > 0 {
		return 1
	}
	return 0
}
