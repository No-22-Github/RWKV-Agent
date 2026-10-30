// expectationaudit exports current native-suite substring expectations without
// contacting a model or changing the frozen scoring rules.
package main

import (
	"encoding/json"
	"os"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

func main() {
	if len(os.Args) != 2 {
		panic("usage: expectationaudit WORKBANK_CASE_DIRECTORY")
	}
	boundary, err := eval.BoundaryCases()
	must(err)
	assistant, err := eval.AssistantCases()
	must(err)
	bfcl, err := eval.BFCLProductCases()
	must(err)
	bank, err := eval.LoadCasesDir(os.Args[1], true)
	must(err)
	suites := map[string][]eval.Case{"smoke": eval.SmokeCases(), "boundary": boundary, "assistant": assistant, "bfcl-product": bfcl, "workbank": bank}
	var rows []map[string]any
	counts := make(map[string]int)
	for _, suite := range []string{"smoke", "boundary", "assistant", "bfcl-product", "workbank"} {
		counts[suite] = len(suites[suite])
		for _, c := range suites[suite] {
			for ti, turn := range c.Turns {
				for _, field := range []string{"output_contains", "output_contains_any"} {
					values := turn.Expect.OutputContains
					if field == "output_contains_any" {
						values = turn.Expect.OutputContainsAny
					}
					for _, value := range values {
						rows = append(rows, map[string]any{"suite": suite, "case_id": c.ID, "turn": ti + 1, "field": field, "value": value, "prompt": turn.Prompt})
					}
				}
			}
		}
	}
	must(json.NewEncoder(os.Stdout).Encode(map[string]any{"case_counts": counts, "expectations": rows}))
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
