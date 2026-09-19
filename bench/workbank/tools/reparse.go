// Run with: go run ./bench/workbank/tools/reparse.go RUN_DIR ...
// Offline parser audit only: recovered calls are not executed or rescored.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/wire"
)

func main() {
	for _, path := range os.Args[1:] {
		data, err := os.ReadFile(filepath.Join(path, "summary.json"))
		must(err)
		var summary struct {
			Cases []struct {
				ID    string `json:"id"`
				Turns []struct {
					Result agent.Result `json:"result"`
				} `json:"turns"`
			} `json:"cases"`
		}
		must(json.Unmarshal(data, &summary))
		for _, mode := range []string{"preamble", "salvage", "json"} {
			p := agent.G1Protocol{SemanticNoTool: true, Experiments: wire.Experiments{Recovery: mode}}
			changes := []map[string]any{}
			for _, c := range summary.Cases {
				for ti, turn := range c.Turns {
					for _, st := range turn.Result.Steps {
						if st.Channel == "native" || st.Stage == agent.StageAnswer {
							continue
						}
						a, err := p.Parse(st.ModelOutput, st.FinishReason)
						if err == nil && a.ProtocolRepaired && (a.Type == agent.ActionTypeTool || a.Type == agent.ActionTypeNoTool) && (st.ActionType != a.Type || st.Tool != a.Name) {
							changes = append(changes, map[string]any{"case": c.ID, "turn": ti + 1, "step": st.Number, "old_action": st.ActionType, "new_action": a.Type, "name": a.Name, "arguments": a.Arguments, "repairs": a.Repairs})
						}
					}
				}
			}
			out, err := json.Marshal(map[string]any{"run": path, "recovery": mode, "changes": changes})
			must(err)
			fmt.Println(string(out))
		}
	}
}

func must(err error) {
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
