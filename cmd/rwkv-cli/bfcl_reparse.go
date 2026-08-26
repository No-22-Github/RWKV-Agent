package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/no22/RWKV-Agent/internal/bfcl"
)

type bfclReparseOptions struct {
	source string
	output string
	parser string
}

func runBFCLReparse(args []string) error {
	options, err := parseBFCLReparseOptions(args)
	if err != nil {
		return err
	}
	if _, err := os.Stat(options.output); err == nil {
		return fmt.Errorf("BFCL output already exists: %s", options.output)
	} else if !errors.Is(err, os.ErrNotExist) {
		return err
	}

	manifestPath := filepath.Join(options.source, "run.json")
	manifestBytes, err := os.ReadFile(manifestPath)
	if err != nil {
		return fmt.Errorf("read source BFCL manifest: %w", err)
	}
	var manifest bfcl.Manifest
	if err := json.Unmarshal(manifestBytes, &manifest); err != nil {
		return fmt.Errorf("decode source BFCL manifest: %w", err)
	}
	if manifest.DataCommit != bfclDataCommit || manifest.EvaluatorVersion != bfclEvaluatorVersion {
		return fmt.Errorf(
			"source BFCL versions do not match pinned data/evaluator: %s/%s",
			manifest.DataCommit,
			manifest.EvaluatorVersion,
		)
	}
	if manifest.Tier != "baseline" || manifest.Transport != string(bfcl.TransportRWKVContinuation) ||
		len(manifest.Splits) != 1 || manifest.Splits[0] != "simple_python" {
		return fmt.Errorf("M2.5 requires the RWKV M2 simple_python baseline run")
	}

	var cases []bfcl.Case
	for _, split := range manifest.Splits {
		loaded, err := bfcl.LoadSplit(manifest.DataDir, split)
		if err != nil {
			return err
		}
		cases = append(cases, loaded...)
	}
	if len(manifest.CaseIDs) > 0 {
		cases, err = filterBFCLCases(cases, manifest.CaseIDs)
		if err != nil {
			return err
		}
	}

	tracePath := filepath.Join(options.source, "trace.jsonl")
	traceBytes, err := os.ReadFile(tracePath)
	if err != nil {
		return fmt.Errorf("read source BFCL trace: %w", err)
	}
	trace, err := bfcl.LoadTrace(tracePath)
	if err != nil {
		return err
	}
	mode := bfcl.ParserMode(options.parser)
	result, err := bfcl.ReparseTrace(cases, trace, mode)
	if err != nil {
		return err
	}
	if err := bfcl.WriteResults(filepath.Join(options.output, "result"), manifest.ModelDirName, result.Entries); err != nil {
		return fmt.Errorf("write reparsed BFCL results: %w", err)
	}
	traceHash := sha256.Sum256(traceBytes)
	manifest.StartedAt = time.Now().UTC()
	manifest.Tier = "m2.5-compat-reparse"
	manifest.ParserMode = options.parser
	manifest.SourceRun = filepath.Clean(options.source)
	manifest.SourceTraceSHA256 = hex.EncodeToString(traceHash[:])
	if err := bfcl.WriteArtifacts(options.output, manifest, result); err != nil {
		return fmt.Errorf("write reparsed BFCL artifacts: %w", err)
	}
	fmt.Fprintf(
		os.Stderr,
		"BFCL reparse complete: total=%d repaired=%d parse_failed=%d elapsed=%s\n",
		len(result.Trace),
		result.Repaired,
		result.ParseFailed,
		result.Elapsed.Round(time.Millisecond),
	)
	return nil
}

func parseBFCLReparseOptions(args []string) (bfclReparseOptions, error) {
	var options bfclReparseOptions
	fs := flag.NewFlagSet("bfcl-reparse", flag.ContinueOnError)
	fs.StringVar(&options.source, "source", "", "source BFCL run directory containing run.json and trace.jsonl")
	fs.StringVar(&options.output, "output", "", "new output directory for reparsed BFCL artifacts")
	fs.StringVar(&options.parser, "parser", string(bfcl.ParserRWKVWireCompatV1), "parser mode: strict or rwkv-wire-compat-v1")
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	options.source = filepath.Clean(options.source)
	options.output = filepath.Clean(options.output)
	mode, err := bfcl.ParseParserMode(options.parser)
	if err != nil {
		return options, err
	}
	options.parser = string(mode)
	if options.source == "." || options.output == "." {
		fs.Usage()
		return options, fmt.Errorf("bfcl-reparse requires --source and --output")
	}
	return options, nil
}
