// Command tracecorpus turns a scripted agent-eval run into training rows.
//
//	rwkv-cli agent-eval --script script.jsonl --cases <bank dir> <wire flags> --output run/
//	tracecorpus --run run/ --script script.jsonl --out rows.jsonl [--rejects rejects.jsonl]
//
// scripts/harness_corpus.py drives both steps from normalized records.
//
// Each row's text is the case's final rendered prompt plus the last scripted
// output, so every byte between the teacher's actions (tool receipts,
// reminders, duplicate rejections, forced-answer blocks) is exactly what the
// eval harness feeds a model under the same wire flags. loss_spans cover the
// outputs the script marks supervised. A case is rejected, never patched,
// when the harness diverged from the script or (with --require-pass, the
// default) when the teacher trajectory fails the case's own expectations.
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

type runFile struct {
	Harness struct {
		Version string `json:"version"`
	} `json:"harness"`
	CaseWires []struct {
		ID            string `json:"id"`
		WireCanonical string `json:"wire_canonical"`
		WireHash      string `json:"wire_hash"`
	} `json:"case_wires"`
}

type summaryFile struct {
	Cases []struct {
		ID     string `json:"id"`
		Passed bool   `json:"passed"`
	} `json:"cases"`
}

type reject struct {
	CaseID string `json:"case_id"`
	Reason string `json:"reason"`
}

func main() {
	if err := run(); err != nil {
		fmt.Fprintf(os.Stderr, "tracecorpus: %v\n", err)
		os.Exit(1)
	}
}

func run() error {
	runDir := flag.String("run", "", "agent-eval output directory (run.json, summary.json, trace.jsonl)")
	scriptPath := flag.String("script", "", "the JSONL script the run replayed")
	outPath := flag.String("out", "", "new JSONL file for the rendered rows")
	rejectsPath := flag.String("rejects", "", "optional JSONL file listing rejected cases and why")
	requirePass := flag.Bool("require-pass", true, "reject cases whose teacher trajectory fails the case expectations")
	flag.Parse()
	if *runDir == "" || *scriptPath == "" || *outPath == "" {
		return fmt.Errorf("--run, --script and --out are required")
	}
	entries, err := eval.LoadScript(*scriptPath)
	if err != nil {
		return err
	}
	var manifest runFile
	if err := readJSON(*runDir+"/run.json", &manifest); err != nil {
		return err
	}
	var summary summaryFile
	if err := readJSON(*runDir+"/summary.json", &summary); err != nil {
		return err
	}
	calls, err := readModelCalls(*runDir + "/trace.jsonl")
	if err != nil {
		return err
	}
	wires := map[string][2]string{}
	for _, wire := range manifest.CaseWires {
		wires[wire.ID] = [2]string{wire.WireCanonical, wire.WireHash}
	}

	out, err := os.OpenFile(*outPath, os.O_WRONLY|os.O_CREATE|os.O_EXCL, 0o644)
	if err != nil {
		return err
	}
	defer out.Close()
	writer := bufio.NewWriter(out)
	var rejects []reject
	written := 0
	for _, result := range summary.Cases {
		entry, ok := entries[result.ID]
		if !ok {
			rejects = append(rejects, reject{result.ID, "no script entry"})
			continue
		}
		if *requirePass && !result.Passed {
			rejects = append(rejects, reject{result.ID, "teacher trajectory fails the case expectations"})
			continue
		}
		built, buildErr := eval.BuildCorpusText(calls[result.ID], entry)
		if buildErr != nil {
			rejects = append(rejects, reject{result.ID, buildErr.Error()})
			continue
		}
		row := eval.CorpusRow{
			Text:      built.Text,
			LossSpans: built.LossSpans,
			Meta: eval.CorpusMeta{
				CaseID:         result.ID,
				Passed:         result.Passed,
				Generations:    len(entry.Outputs),
				Supervised:     len(built.LossSpans),
				Canonicalized:  built.Canonicalized,
				WireCanonical:  wires[result.ID][0],
				WireHash:       wires[result.ID][1],
				HarnessVersion: manifest.Harness.Version,
			},
		}
		line, err := json.Marshal(row)
		if err != nil {
			return err
		}
		writer.Write(line)
		writer.WriteByte('\n')
		written++
	}
	if err := writer.Flush(); err != nil {
		return err
	}
	if *rejectsPath != "" {
		if err := writeRejects(*rejectsPath, rejects); err != nil {
			return err
		}
	}
	fmt.Fprintf(os.Stdout, "tracecorpus: %d rows written, %d cases rejected\n", written, len(rejects))
	// The console summary groups by a truncated reason; rejects.jsonl keeps
	// the full text.
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
		fmt.Fprintf(os.Stdout, "  %4d  %s\n", reasons[reason], reason)
	}
	return nil
}

func readJSON(path string, value any) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	if err := json.Unmarshal(data, value); err != nil {
		return fmt.Errorf("parse %s: %w", path, err)
	}
	return nil
}

// readModelCalls groups the trace's model calls by case, in sequence order.
func readModelCalls(path string) (map[string][]eval.ModelCallTrace, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	var records []eval.TraceRecord
	scanner := bufio.NewScanner(file)
	scanner.Buffer(make([]byte, 0, 1<<20), 256<<20)
	for scanner.Scan() {
		var record eval.TraceRecord
		if err := json.Unmarshal(scanner.Bytes(), &record); err != nil {
			return nil, fmt.Errorf("parse %s: %w", path, err)
		}
		if record.Kind == "model_call" && record.ModelCall != nil {
			records = append(records, record)
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	sort.SliceStable(records, func(i, j int) bool { return records[i].Sequence < records[j].Sequence })
	calls := map[string][]eval.ModelCallTrace{}
	for _, record := range records {
		calls[record.CaseID] = append(calls[record.CaseID], *record.ModelCall)
	}
	return calls, nil
}

func writeRejects(path string, rejects []reject) error {
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
