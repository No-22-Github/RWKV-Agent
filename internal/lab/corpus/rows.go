package corpus

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"sort"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

// Turn a scripted agent-eval run into training rows. This is the former
// moved into rwkv-lab unchanged (§2.6): the logic lives in
// internal/agent/eval/corpus.go and is not touched.
//
// Each row's text is a turn's final rendered prompt plus the turn's last
// scripted output, so every byte between the teacher's actions (tool receipts,
// reminders, duplicate rejections, forced-answer blocks) is exactly what the
// eval harness feeds a model under the same wire flags. loss_spans cover the
// outputs the script marks supervised. A case is rejected, never patched, when
// the harness diverged from the script or (with --require-pass, the default)
// when the teacher trajectory fails the case's own expectations.
//
// The rows are written with encoding/json's default HTML escaping, which turns
// < into <. That is not an oversight and must not be "fixed" to match
// P2: the harness writes the same escaping into the trace, and the training row
// adopts the harness bytes because those are the bytes the model saw
// (docs/harness-corpus-render.md).

// RowsArgs are the `corpus rows` flags.
type RowsArgs struct {
	Run     string
	Script  string
	Cases   string
	Source  string
	Out     string
	Rejects string
	// RequirePass drops cases whose teacher trajectory fails the case's own
	// expectations.
	RequirePass bool
}

type rowsRunFile struct {
	Harness struct {
		Version string `json:"version"`
	} `json:"harness"`
	CaseWires []struct {
		ID            string `json:"id"`
		WireCanonical string `json:"wire_canonical"`
		WireHash      string `json:"wire_hash"`
	} `json:"case_wires"`
}

type rowsReject struct {
	CaseID string `json:"case_id"`
	Reason string `json:"reason"`
}

// RunRows is the `corpus rows` command.
func RunRows(args RowsArgs) int {
	if args.Run == "" || args.Script == "" || args.Out == "" {
		fmt.Fprintln(stderr, "error: --run, --script and --out are required")
		return 2
	}
	if args.Cases == "" {
		fmt.Fprintln(stderr, "error: --cases is required: every row's labels come from the case it was rendered from")
		return 2
	}
	if args.Source == "" {
		fmt.Fprintln(stderr, "error: --source is required: a row without a source cannot be told apart from another batch's")
		return 1
	}
	bankCases, err := Load(args.Cases)
	if err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	cases, err := ByID(bankCases)
	if err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	world, err := lab.OpenWorld()
	if err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	entries, err := eval.LoadScript(args.Script)
	if err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	var manifest rowsRunFile
	if err := readJSONFile(args.Run+"/run.json", &manifest); err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	var summary eval.Summary
	if err := readJSONFile(args.Run+"/summary.json", &summary); err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	calls, turns, err := readModelCalls(args.Run + "/trace.jsonl")
	if err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	wires := map[string][2]string{}
	for _, wire := range manifest.CaseWires {
		wires[wire.ID] = [2]string{wire.WireCanonical, wire.WireHash}
	}

	out, err := os.OpenFile(args.Out, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	defer out.Close()
	writer := bufio.NewWriter(out)
	var rejects []rowsReject
	written, rowCases := 0, 0
	for _, result := range summary.Cases {
		entry, ok := entries[result.ID]
		if !ok {
			rejects = append(rejects, rowsReject{result.ID, "no script entry"})
			continue
		}
		if args.RequirePass && !result.Passed {
			rejects = append(rejects, rowsReject{result.ID, "teacher trajectory fails the case expectations"})
			continue
		}
		texts, buildErr := eval.BuildCorpusTurns(calls[result.ID], turns[result.ID], entry)
		if buildErr != nil {
			rejects = append(rejects, rowsReject{result.ID, buildErr.Error()})
			continue
		}
		caseObj, ok := cases[result.ID]
		if !ok {
			fmt.Fprintf(stderr, "rows: script entry %s has no case under %s\n", result.ID, args.Cases)
			return 1
		}
		caseTags, seeded := TagsFromCase(caseObj)
		runExpect := truthy(mapValue(caseObj, "expect"))
		turnsTotal := len(caseTurns(caseObj))
		if turnsTotal == 0 {
			turnsTotal = len(turns[result.ID])
		}
		for _, built := range texts {
			traj := BuildTraj(entry.Outputs, built.FirstOutput, built.Generations, built.Turn,
				turnsTotal, world.Count(built.Text), turnExpect(caseObj, built.Turn))
			row := eval.CorpusRow{
				Text:      built.Text,
				LossSpans: built.LossSpans,
				Meta: eval.CorpusMeta{
					CaseID:         result.ID,
					Turn:           built.Turn,
					Passed:         result.Passed,
					Generations:    built.Generations,
					Supervised:     built.Supervised,
					Canonicalized:  built.Canonicalized,
					WireCanonical:  wires[result.ID][0],
					WireHash:       wires[result.ID][1],
					HarnessVersion: manifest.Harness.Version,
					Source:         args.Source,
					SeededFromTest: seeded,
					CaseTags:       caseTags,
					Traj:           traj,
					Kind:           DeriveKind(caseTags, traj, built.Turn, runExpect),
				},
			}
			line, err := json.Marshal(row)
			if err != nil {
				fmt.Fprintf(stderr, "rows: %v\n", err)
				return 1
			}
			writer.Write(line)
			writer.WriteByte('\n')
			written++
		}
		rowCases++
	}
	if err := writer.Flush(); err != nil {
		fmt.Fprintf(stderr, "rows: %v\n", err)
		return 1
	}
	if args.Rejects != "" {
		if err := writeRowsRejects(args.Rejects, rejects); err != nil {
			fmt.Fprintf(stderr, "rows: %v\n", err)
			return 1
		}
	}
	fmt.Printf("rows: %d rows written from %d cases, %d cases rejected\n",
		written, rowCases, len(rejects))
	// The console summary groups by a truncated reason; rejects.jsonl keeps the
	// full text.
	reasons := map[string]int{}
	for _, item := range rejects {
		reason := item.Reason
		if len(reason) > 120 {
			reason = reason[:120] + "…"
		}
		reasons[reason]++
	}
	keys := make([]string, 0, len(reasons))
	for reason := range reasons {
		keys = append(keys, reason)
	}
	sort.Slice(keys, func(i, j int) bool { return reasons[keys[i]] > reasons[keys[j]] })
	for _, reason := range keys {
		fmt.Printf("  %4d  %s\n", reasons[reason], reason)
	}
	return 0
}

// readModelCalls groups the trace's model calls by case, in sequence order,
// with the turn each call belongs to.
func readModelCalls(path string) (map[string][]eval.ModelCallTrace, map[string][]int, error) {
	var records []eval.TraceRecord
	err := scanJSONLines(path, func(record *eval.TraceRecord) {
		if record.Kind == "model_call" && record.ModelCall != nil {
			records = append(records, *record)
		}
	})
	if err != nil {
		return nil, nil, err
	}
	sort.SliceStable(records, func(i, j int) bool { return records[i].Sequence < records[j].Sequence })
	calls, turns := map[string][]eval.ModelCallTrace{}, map[string][]int{}
	for _, record := range records {
		calls[record.CaseID] = append(calls[record.CaseID], *record.ModelCall)
		turns[record.CaseID] = append(turns[record.CaseID], record.Turn)
	}
	return calls, turns, nil
}

func writeRowsRejects(path string, rejects []rowsReject) error {
	file, err := os.OpenFile(path, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if err != nil {
		return err
	}
	defer file.Close()
	encoder := json.NewEncoder(file)
	for _, item := range rejects {
		if err := encoder.Encode(item); err != nil {
			return err
		}
	}
	return nil
}
