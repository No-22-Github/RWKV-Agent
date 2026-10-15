package exam

import (
	"bytes"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"slices"
	"sort"
	"strings"
)

// legacyContract is the bank's old value-only tail. Exam prompts are written
// the way an App user talks, so the contract must not survive into the exam.
var legacyContracts = []string{
	"Reply with only the final answer",
	"reply exactly UNKNOWN",
	"When finished, reply DONE",
	"reply DONE",
	"回复 DONE",
	"回复DONE",
}

func runLint(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab exam lint", flag.ContinueOnError)
	if err := flags.Parse(args); err != nil {
		return 2
	}
	paths := DefaultPaths()
	exam, err := Assemble(paths)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab exam lint:", err)
		return 1
	}
	violations := exam.Lint(paths)
	for _, violation := range violations {
		fmt.Println(violation)
	}
	fmt.Printf("%d violation(s) across %d exam case(s)\n", len(violations), len(exam.Full.Cases))
	if len(violations) > 0 {
		return 1
	}
	return 0
}

// Lint checks the generated files and the exam rules. Every violation is one
// line "<id or file>: <rule>: <detail>".
func (exam *Exam) Lint(paths Paths) []string {
	var out []string
	add := func(subject, rule, detail string) {
		out = append(out, fmt.Sprintf("%s: %s: %s", subject, rule, detail))
	}
	if len(exam.Missing) > 0 {
		add("quick-ids.txt", "quick-subset", fmt.Sprintf("ids outside the full exam: %v", exam.Missing))
	}
	outputs, err := exam.Outputs()
	if err != nil {
		add("build", "render", err.Error())
	}
	names := make([]string, 0, len(outputs))
	for name := range outputs {
		names = append(names, name)
	}
	sort.Strings(names)
	for _, name := range names {
		current, _ := os.ReadFile(filepath.Join(paths.Root, filepath.FromSlash(name)))
		if !bytes.Equal(current, outputs[name]) {
			add(name, "stale", "regenerate with rwkv-lab exam build")
		}
	}
	cases := map[string]loaded{}
	for _, items := range exam.Suites {
		for _, item := range items {
			cases[item.Row.ID] = item
		}
	}
	for _, row := range exam.Full.Cases {
		item := cases[row.ID]
		if row.Leaked {
			add(row.ID, "leaked", "leaked cases must not be in the exam")
		}
		if !slices.Contains(TaskOrder, row.Task) {
			add(row.ID, "task", fmt.Sprintf("unknown task %q", row.Task))
		}
		for _, d := range row.Difficulties {
			if !slices.Contains(DifficultyOrder, d) {
				add(row.ID, "difficulty", fmt.Sprintf("unknown difficulty %q", d))
			}
		}
		if row.Scenario == "" {
			add(row.ID, "tags", "missing tags.scenario")
		}
		if row.Author == "" {
			add(row.ID, "tags", "missing tags.author")
		}
		for i, turn := range item.Case.Turns {
			for _, contract := range legacyContracts {
				if strings.Contains(turn.Prompt, contract) {
					add(row.ID, "natural-prompt", fmt.Sprintf("turn %d keeps the legacy contract %q", i+1, contract))
				}
			}
			if slices.Contains(turn.Expect.OutputContains, "DONE") {
				add(row.ID, "natural-prompt", fmt.Sprintf("turn %d still requires the legacy DONE reply", i+1))
			}
			if turn.Expect.MaxOutputChars > 0 {
				add(row.ID, "no-length-cap", fmt.Sprintf("turn %d caps the answer at %d chars", i+1, turn.Expect.MaxOutputChars))
			}
		}
	}
	return out
}
