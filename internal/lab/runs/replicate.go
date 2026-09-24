package runs

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"sort"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Summarize an explicit, complete set of comparable repeated runs, offline.
//
// Never mutates the append-only ledger and never launches model requests.
// pass_all_k / pass_any_k are empirical per-case all/any outcomes, not pass@k
// estimators or uncertainty bounds. Mismatched or incomplete replicas are
// refused rather than pooled.

// ReplicateArgs are the `run replicate` flags.
type ReplicateArgs struct {
	Runs []string
	K    int
	Out  string
}

// RunReplicate is the `run replicate` command.
func RunReplicate(args ReplicateArgs) int {
	result, err := Summarize(args.Runs, args.K)
	if err != nil {
		fmt.Fprintf(stderr, "error: %s\n", err)
		return 1
	}
	data, err := lab.EncodeOrderedJSON(result, lab.EncodeOptions{Indent: 2})
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	if err := os.MkdirAll(filepath.Dir(args.Out), 0o755); err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	if err := os.WriteFile(args.Out, append(data, '\n'), 0o644); err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}

	// stdout carries everything but the two big lists.
	summary := lab.NewOrderedMap()
	for _, key := range result.Keys {
		if key == "runs" || key == "cases" {
			continue
		}
		summary.Set(key, result.Values[key])
	}
	out, err := lab.EncodeOrderedJSON(summary, lab.EncodeOptions{SpacedSeparators: true})
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 1
	}
	fmt.Println(string(out))
	return 0
}

// Summarize is replicate_summary.summarize.
func Summarize(runs []string, k int) (*lab.OrderedMap, error) {
	if k < 2 || len(runs) != k {
		return nil, fmt.Errorf("exactly %d distinct runs are required, received %d", k, len(runs))
	}
	type record struct {
		path          string
		runID         string
		summarySHA256 string
		scores        map[string]bool
	}
	var records []record
	var signatures []string
	runIDs := map[string]bool{}

	for _, runPath := range runs {
		manifest, err := LoadJSONFile(filepath.Join(runPath, "run.json"), true)
		if err != nil {
			return nil, err
		}
		summary, err := LoadJSONFile(filepath.Join(runPath, "summary.json"), true)
		if err != nil {
			return nil, err
		}
		meta, err := LoadJSONFile(filepath.Join(runPath, "experiment.json"), true)
		if err != nil {
			return nil, err
		}
		runID := stringOf(manifest, "run_id")
		if runID == "" || runIDs[runID] || stringOf(summary, "run_id") != runID {
			return nil, fmt.Errorf("missing, duplicated, or inconsistent run_id: %s", runPath)
		}
		runIDs[runID] = true
		if truthy(meta["infrastructure_errors"]) {
			return nil, fmt.Errorf("infrastructure errors: %s", runPath)
		}
		if stringOf(meta, "binary_sha256") == "" {
			return nil, fmt.Errorf("binary provenance is required: %s", runPath)
		}

		specs := mapSlice(manifest["cases"])
		ids := map[string]bool{}
		for _, c := range specs {
			ids[stringOf(c, "id")] = true
		}
		summaryCases := mapSlice(summary["cases"])
		summaryIDs := map[string]bool{}
		for _, c := range summaryCases {
			summaryIDs[stringOf(c, "id")] = true
		}
		if len(ids) != len(specs) || len(summaryCases) != len(ids) || len(summaryIDs) != len(ids) {
			return nil, fmt.Errorf("missing or duplicate case rows: %s", runPath)
		}
		specByID := map[string]map[string]any{}
		for _, c := range specs {
			specByID[stringOf(c, "id")] = c
		}
		for _, c := range summaryCases {
			cid := stringOf(c, "id")
			if _, isBool := c["passed"].(bool); !isBool {
				return nil, fmt.Errorf("missing score or incomplete turns: %s", cid)
			}
			spec := specByID[cid]
			if spec == nil || len(mapSlice(c["turns"])) != len(mapSlice(spec["turns"])) {
				return nil, fmt.Errorf("missing score or incomplete turns: %s", cid)
			}
			failures := append([]string{}, stringList(c["failures"])...)
			if errText := stringOf(c, "error"); errText != "" {
				failures = append(failures, errText)
			}
			for _, t := range mapSlice(c["turns"]) {
				failures = append(failures, stringList(t["failures"])...)
				if runnerError := stringOf(t, "runner_error"); runnerError != "" {
					failures = append(failures, runnerError)
				}
			}
			for _, f := range failures {
				if f != "" && InfrastructureFailure(f) {
					return nil, fmt.Errorf("infrastructure failure in %s", cid)
				}
			}
		}

		sortedSpecs := append([]map[string]any(nil), specs...)
		sort.SliceStable(sortedSpecs, func(i, j int) bool {
			return stringOf(sortedSpecs[i], "id") < stringOf(sortedSpecs[j], "id")
		})
		signatureInput := lab.NewOrderedMap()
		signatureInput.Set("model", manifest["model"])
		signatureInput.Set("sampling", manifest["sampling"])
		signatureInput.Set("harness", manifest["harness"])
		signatureInput.Set("cases", toAnyMapSlice(sortedSpecs))
		signatureInput.Set("binary_sha256", meta["binary_sha256"])
		stateID := ""
		if s, ok := meta["state_id"].(string); ok {
			stateID = s
		}
		signatureInput.Set("state_id", stateID)
		signatures = append(signatures, canonicalJSON(signatureInput))

		summaryBytes, err := os.ReadFile(filepath.Join(runPath, "summary.json"))
		if err != nil {
			return nil, err
		}
		sum := sha256.Sum256(summaryBytes)
		scores := map[string]bool{}
		for _, c := range summaryCases {
			passed, _ := c["passed"].(bool)
			scores[stringOf(c, "id")] = passed
		}
		records = append(records, record{
			path: runPath, runID: runID,
			summarySHA256: hex.EncodeToString(sum[:]), scores: scores,
		})
	}

	for i := 1; i < len(signatures); i++ {
		if signatures[i] != signatures[0] {
			return nil, fmt.Errorf("replicas differ in frozen cases, scorer/harness, model, state, " +
				"sampling, or binary; do not pool them")
		}
	}

	caseIDs := make([]string, 0, len(records[0].scores))
	for cid := range records[0].scores {
		caseIDs = append(caseIDs, cid)
	}
	sort.Strings(caseIDs)
	if len(caseIDs) == 0 {
		return nil, fmt.Errorf("no cases")
	}

	allCount, anyCount, passedReplicasTotal := 0, 0, 0
	var unstable []string
	casesOut := make([]any, 0, len(caseIDs))
	for _, cid := range caseIDs {
		outcomes := make([]any, 0, len(records))
		passedReplicas := 0
		all, any := true, false
		for _, r := range records {
			ok := r.scores[cid]
			outcomes = append(outcomes, ok)
			if ok {
				passedReplicas++
				any = true
			} else {
				all = false
			}
		}
		passedReplicasTotal += passedReplicas
		if all {
			allCount++
		}
		if any {
			anyCount++
		}
		if passedReplicas > 0 && passedReplicas < k {
			unstable = append(unstable, cid)
		}
		entry := lab.NewOrderedMap()
		entry.Set("id", cid)
		entry.Set("outcomes", outcomes)
		entry.Set("passed_replicas", passedReplicas)
		entry.Set("pass_all_k", all)
		entry.Set("pass_any_k", any)
		casesOut = append(casesOut, entry)
	}
	n := len(caseIDs)

	runsOut := make([]any, 0, len(records))
	for _, r := range records {
		entry := lab.NewOrderedMap()
		entry.Set("path", r.path)
		entry.Set("run_id", r.runID)
		entry.Set("summary_sha256", r.summarySHA256)
		runsOut = append(runsOut, entry)
	}

	passAll := lab.NewOrderedMap()
	passAll.Set("passed", allCount)
	passAll.Set("total", n)
	passAll.Set("rate", float64(allCount)/float64(n))
	passAny := lab.NewOrderedMap()
	passAny.Set("passed", anyCount)
	passAny.Set("total", n)
	passAny.Set("rate", float64(anyCount)/float64(n))

	sigSum := sha256.Sum256([]byte(signatures[0]))
	result := lab.NewOrderedMap()
	result.Set("k", k)
	result.Set("cases_per_replica", n)
	result.Set("pass_mean", float64(passedReplicasTotal)/float64(n*k))
	result.Set("pass_all_k", passAll)
	result.Set("pass_any_k", passAny)
	result.Set("unstable_cases", toAnySlice(unstable))
	result.Set("definition", "Observed all/any across this explicit replica group. "+
		"No confidence interval or pass@k estimator.")
	result.Set("comparability_sha256", hex.EncodeToString(sigSum[:]))
	result.Set("runs", runsOut)
	result.Set("cases", casesOut)
	return result, nil
}

func toAnyMapSlice(items []map[string]any) []any {
	out := make([]any, len(items))
	for i, item := range items {
		out[i] = item
	}
	return out
}
