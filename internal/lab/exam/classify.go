package exam

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// classify labels any case collection with the exam's own task kind,
// difficulties, language and answer form, so training data drawn from those
// cases can be split along the same axes the panel scores.

type classifyRow struct {
	ID           string   `json:"id"`
	Task         string   `json:"task"`
	Block        string   `json:"block"`
	Difficulties []string `json:"difficulties"`
	Language     string   `json:"language"`
	AnswerForm   string   `json:"answer_form"`
	Scenario     string   `json:"scenario,omitempty"`
	TaskType     string   `json:"task_type,omitempty"`
}

func runClassify(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam classify", flag.ContinueOnError)
	casesRoot := flags.String("cases", "bench/distill", "case directory (searched recursively, cases-shelved skipped)")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	cases, err := eval.LoadCasesDir(*casesRoot, true)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam classify:", err)
		return 1
	}
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetEscapeHTML(false)
	for _, c := range cases {
		task := Task(c, "")
		row := classifyRow{
			ID:           c.ID,
			Task:         task,
			Block:        Block(c, "", task),
			Difficulties: Difficulties(c),
			Language:     Language(c),
			AnswerForm:   AnswerForm(c),
			Scenario:     tagString(c, "scenario"),
			TaskType:     tagString(c, "task_type"),
		}
		if err := encoder.Encode(row); err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab exam classify:", err)
			return 1
		}
	}
	return 0
}
