// tokenaudit compares stored decoded output lengths with configured generation
// budgets. Retokenized counts are diagnostic, not authoritative server usage.
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

func main() {
	if len(os.Args) < 3 {
		panic("usage: tokenaudit VOCAB RUN...")
	}
	v, err := tokenizer.OpenWorld(os.Args[1])
	must(err)
	for _, run := range os.Args[2:] {
		data, err := os.ReadFile(filepath.Join(run, "summary.json"))
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
		var rows []map[string]any
		for _, c := range summary.Cases {
			for ti, t := range c.Turns {
				for _, s := range t.Result.Steps {
					n := v.Count(s.ModelOutput)
					rows = append(rows, map[string]any{"case": c.ID, "turn": ti + 1, "step": s.Number, "stage": s.Stage, "retokenized_output": n, "request_tokens": v.Count(s.Request.Prompt), "request_budget": s.Request.MaxOutputTokens, "finish": s.FinishReason, "protocol_error": s.ProtocolError})
				}
			}
		}
		b, err := json.Marshal(map[string]any{"run": run, "vocab_sha256": v.SHA256(), "steps": rows})
		must(err)
		fmt.Println(string(b))
	}
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
