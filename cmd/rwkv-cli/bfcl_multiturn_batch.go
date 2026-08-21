package main

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"

	"github.com/no22/RWKV-Agent/internal/bfcl"
	"github.com/no22/RWKV-Agent/internal/bfcl/pysidecar"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

// selectMultiTurnCases resolves --case into one or more entries. "all" runs the
// whole split; a comma list runs exactly those IDs.
func selectMultiTurnCases(cases []bfcl.MultiTurnCase, options bfclMultiTurnOptions) ([]bfcl.MultiTurnCase, error) {
	if strings.TrimSpace(options.caseID) == "all" {
		return cases, nil
	}
	wanted := map[string]struct{}{}
	for _, id := range strings.Split(options.caseID, ",") {
		if id = strings.TrimSpace(id); id != "" {
			wanted[id] = struct{}{}
		}
	}
	selected := make([]bfcl.MultiTurnCase, 0, len(wanted))
	for _, entry := range cases {
		if _, ok := wanted[entry.ID]; ok {
			selected = append(selected, entry)
		}
	}
	if len(selected) != len(wanted) {
		found := map[string]struct{}{}
		for _, entry := range selected {
			found[entry.ID] = struct{}{}
		}
		missing := make([]string, 0, len(wanted))
		for id := range wanted {
			if _, ok := found[id]; !ok {
				missing = append(missing, id)
			}
		}
		sort.Strings(missing)
		return nil, fmt.Errorf("BFCL multi-turn cases not found in %s: %s", options.split, strings.Join(missing, ","))
	}
	return selected, nil
}

type multiTurnCellOutcome struct {
	ID      string
	Skipped bool
	Err     error
	Trace   bfcl.MultiTurnTrace
}

// runBFCLMultiTurnCells drives many cases concurrently against one generator.
// Each case keeps its own sidecar session, so simulator state never crosses
// cases; only the HTTP client and its batch window are shared.
func runBFCLMultiTurnCells(
	entries []bfcl.MultiTurnCase,
	options bfclMultiTurnOptions,
	generator continuation.Generator,
	headers http.Header,
	repoRoot string,
) error {
	if err := os.MkdirAll(options.output, 0o700); err != nil {
		return err
	}
	sidecar, err := pysidecar.Start(pysidecar.Config{Python: options.python, Script: options.sidecarScript, WorkingDir: repoRoot})
	if err != nil {
		return err
	}
	defer sidecar.Close()

	ctx, cancel := signalContext()
	defer cancel()

	var tokenizerVocabSHA256 string
	var tokenCounter func(string) (int, error)
	if options.maxPromptTokens > 0 {
		vocab := options.tokenizerVocab
		if _, sha, err := sidecar.CountTokens(ctx, vocab, "probe"); err != nil {
			return fmt.Errorf("prompt token guard requires a working tokenizer: %w", err)
		} else {
			tokenizerVocabSHA256 = sha
		}
		tokenCounter = func(prompt string) (int, error) {
			tokens, _, err := sidecar.CountTokens(ctx, vocab, prompt)
			return tokens, err
		}
	}

	concurrency := options.caseConcurrency
	if concurrency <= 0 {
		concurrency = 1
	}
	if concurrency > len(entries) {
		concurrency = len(entries)
	}

	outcomes := make([]multiTurnCellOutcome, len(entries))
	queue := make(chan int)
	var wait sync.WaitGroup
	for worker := 0; worker < concurrency; worker++ {
		wait.Add(1)
		go func() {
			defer wait.Done()
			for index := range queue {
				outcomes[index] = runOneMultiTurnCell(ctx, entries[index], options, generator, headers, sidecar, tokenCounter, tokenizerVocabSHA256)
			}
		}()
	}
	for index := range entries {
		select {
		case queue <- index:
		case <-ctx.Done():
			close(queue)
			wait.Wait()
			return ctx.Err()
		}
	}
	close(queue)
	wait.Wait()

	var ran, skipped, failed int
	for _, outcome := range outcomes {
		switch {
		case outcome.Skipped:
			skipped++
		case outcome.Err != nil:
			failed++
			fmt.Fprintf(os.Stderr, "case %s: %v\n", outcome.ID, outcome.Err)
		default:
			ran++
		}
	}
	fmt.Fprintf(os.Stderr, "BFCL multi-turn cell complete: cases=%d ran=%d skipped=%d failed=%d output=%s\n",
		len(entries), ran, skipped, failed, options.output)
	if ran == 0 && failed > 0 {
		return fmt.Errorf("every attempted BFCL multi-turn case failed")
	}
	return nil
}

func runOneMultiTurnCell(
	ctx context.Context,
	entry bfcl.MultiTurnCase,
	options bfclMultiTurnOptions,
	generator continuation.Generator,
	headers http.Header,
	sidecar *pysidecar.Client,
	tokenCounter func(string) (int, error),
	tokenizerVocabSHA256 string,
) multiTurnCellOutcome {
	outcome := multiTurnCellOutcome{ID: entry.ID}
	caseOutput := filepath.Join(options.output, entry.ID)
	// Resumable: an existing case directory is left untouched so an interrupted
	// cell can be re-run without repeating work or overwriting evidence.
	if _, err := os.Stat(caseOutput); err == nil {
		outcome.Skipped = true
		return outcome
	} else if !errors.Is(err, os.ErrNotExist) {
		outcome.Err = err
		return outcome
	}
	catalog, err := bfcl.LoadMultiTurnCatalog(options.dataDir, entry)
	if err != nil {
		outcome.Err = err
		return outcome
	}
	sessionID, err := sidecar.NewSession(ctx, pysidecar.SessionOptions{
		ID: entry.ID + "-" + options.tier, InitialConfig: entry.InitialConfig,
		InvolvedClasses: entry.InvolvedClasses,
		LongContext:     strings.Contains(options.split, "long_context"), TestEntryID: entry.ID,
	})
	if err != nil {
		outcome.Err = err
		return outcome
	}
	trace := bfcl.RunMultiTurnCase(ctx, entry, catalog, multiTurnRunnerOptions(options, generator, sidecar, sessionID, tokenCounter))
	if err := sidecar.CloseSession(context.Background(), sessionID); err != nil && outcome.Err == nil {
		outcome.Err = err
	}
	outcome.Trace = trace
	if err := bfcl.WriteMultiTurnResult(filepath.Join(caseOutput, "result"), bfclModelDirName, trace); err != nil {
		outcome.Err = err
		return outcome
	}
	manifest := multiTurnManifest(options, headers, tokenizerVocabSHA256)
	manifest.CaseID = entry.ID
	if err := bfcl.WriteMultiTurnArtifacts(caseOutput, manifest, trace); err != nil {
		outcome.Err = err
		return outcome
	}
	if trace.Error != "" {
		outcome.Err = fmt.Errorf("%s [%s]", trace.Error, trace.FailureKind)
	}
	return outcome
}
