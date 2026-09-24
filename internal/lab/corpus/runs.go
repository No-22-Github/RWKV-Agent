package corpus

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// Reading agent-eval run directories (summary.json + trace.jsonl).
//
// The originals hand-rolled dict access over the trace ("record['kind']",
// "step.get('action_type')"). This port decodes into eval.TraceRecord and
// agent.Result/agent.Step instead, so a renamed trace field is a compile
// error rather than a silently empty path — which is the main payoff of
// moving the corpus tools into Go (§2.1.1).

// retryEvents are the runner events that make a run unclean: the harness took
// a path the teacher did not plan for.
var retryEvents = map[agent.EventKind]bool{agent.EventRetry: true}

// CaseRun is one case's outcome in one run directory.
type CaseRun struct {
	CaseID  string
	Passed  bool
	Turns   []agent.Result
	Retries int
}

// LoadRunDir reads a run directory's summary and trace.
func LoadRunDir(runDir string) ([]CaseRun, error) {
	var summary eval.Summary
	if err := readJSONFile(filepath.Join(runDir, "summary.json"), &summary); err != nil {
		return nil, err
	}

	type turnResult struct {
		turn   int
		result agent.Result
	}
	turns := map[string][]turnResult{}
	retries := map[string]int{}
	err := scanJSONLines(filepath.Join(runDir, "trace.jsonl"), func(record *eval.TraceRecord) {
		switch record.Kind {
		case "turn_result":
			if record.TurnResult != nil {
				turns[record.CaseID] = append(turns[record.CaseID], turnResult{record.Turn, record.TurnResult.Result})
			}
		case "runner_event":
			if record.RunnerEvent != nil && retryEvents[record.RunnerEvent.Kind] {
				retries[record.CaseID]++
			}
		}
	})
	if err != nil {
		return nil, err
	}

	runs := make([]CaseRun, 0, len(summary.Cases))
	for _, caseResult := range summary.Cases {
		collected := turns[caseResult.ID]
		sort.SliceStable(collected, func(i, j int) bool { return collected[i].turn < collected[j].turn })
		results := make([]agent.Result, 0, len(collected))
		for _, item := range collected {
			results = append(results, item.result)
		}
		runs = append(runs, CaseRun{
			CaseID:  caseResult.ID,
			Passed:  caseResult.Passed,
			Turns:   results,
			Retries: retries[caseResult.ID],
		})
	}
	return runs, nil
}

func readJSONFile(path string, value any) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	if err := json.Unmarshal(data, value); err != nil {
		return fmt.Errorf("parse %s: %w", path, err)
	}
	return nil
}

// scanJSONLines streams a JSONL file, one decoded record at a time; traces run
// to hundreds of megabytes and are not worth holding in memory twice.
func scanJSONLines(path string, fn func(*eval.TraceRecord)) error {
	file, err := os.Open(path)
	if err != nil {
		return err
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 0, 1<<20), 256<<20)
	for scanner.Scan() {
		if len(scanner.Bytes()) == 0 {
			continue
		}
		var record eval.TraceRecord
		if err := json.Unmarshal(scanner.Bytes(), &record); err != nil {
			return fmt.Errorf("parse %s: %w", path, err)
		}
		fn(&record)
	}
	return scanner.Err()
}
