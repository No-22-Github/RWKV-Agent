package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/bfcl"
	"github.com/no22/RWKV-Agent/internal/bfcldiagnostic"
)

type bfclSamplingDiagnosticOptions struct {
	manifest string
	score    string
	output   string
	v2Output string
	dataDir  string
}

func runBFCLSamplingDiagnostic(args []string) error {
	options, err := parseBFCLSamplingDiagnosticOptions(args)
	if err != nil {
		return err
	}
	if _, err := os.Stat(options.output); err == nil {
		return fmt.Errorf("BFCL sampling diagnostic already exists: %s", options.output)
	} else if !os.IsNotExist(err) {
		return err
	}
	report, err := bfcldiagnostic.Analyze(options.manifest, options.score)
	if err != nil {
		return err
	}
	v1, v1Digest, err := bfcl.LoadSampleManifest(options.manifest)
	if err != nil {
		return err
	}
	if v1.DataCommit != bfclDataCommit {
		return fmt.Errorf("BFCL sample data commit %s does not match pinned %s", v1.DataCommit, bfclDataCommit)
	}
	triggered := bfcldiagnostic.TriggeredSplits(report)
	v2Path := ""
	v2Digest := ""
	if len(triggered) > 0 {
		if _, err := os.Stat(options.v2Output); err == nil {
			return fmt.Errorf("BFCL v2 sample manifest already exists: %s", options.v2Output)
		} else if !os.IsNotExist(err) {
			return err
		}
		targets, err := bfcl.ExpandedSampleTargets(v1, triggered)
		if err != nil {
			return err
		}
		v2, err := bfcl.GenerateSampleManifest(options.dataDir, bfclDataCommit, "v2", targets)
		if err != nil {
			return err
		}
		v2.SourceManifestSHA256 = v1Digest
		v2Digest, err = bfcl.WriteSampleManifest(options.v2Output, v2)
		if err != nil {
			return err
		}
		v2Path = options.v2Output
	}
	content := bfcldiagnostic.RenderMarkdown(report, v2Path, v2Digest)
	if err := bfcldiagnostic.WriteReport(options.output, content); err != nil {
		return err
	}
	fmt.Fprintf(
		os.Stderr,
		"BFCL sampling diagnostic written: %s triggered_splits=%d\n",
		options.output,
		len(triggered),
	)
	return nil
}

func parseBFCLSamplingDiagnosticOptions(args []string) (bfclSamplingDiagnosticOptions, error) {
	var options bfclSamplingDiagnosticOptions
	fs := flag.NewFlagSet("bfcl-sampling-diagnostic", flag.ContinueOnError)
	fs.StringVar(&options.manifest, "manifest", "configs/bfcl-sample-v1.json", "frozen BFCL sample manifest")
	fs.StringVar(&options.score, "score", "", "official evaluator score root for a complete Qwen enhanced run")
	fs.StringVar(&options.output, "output", "runs/bfcl/sampling-diagnostic.md", "new sampling diagnostic report")
	fs.StringVar(&options.v2Output, "v2-output", "configs/bfcl-sample-v2.json", "new v2 manifest if mechanical expansion triggers")
	fs.StringVar(&options.dataDir, "data-dir", "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data", "BFCL data directory for mechanical v2 expansion")
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	if options.score == "" {
		fs.Usage()
		return options, fmt.Errorf("bfcl-sampling-diagnostic requires --score")
	}
	options.manifest = filepath.Clean(options.manifest)
	options.score = filepath.Clean(options.score)
	options.output = filepath.Clean(options.output)
	options.v2Output = filepath.Clean(options.v2Output)
	options.dataDir = filepath.Clean(options.dataDir)
	return options, nil
}
