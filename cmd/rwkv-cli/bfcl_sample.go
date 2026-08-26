package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/bfcl"
)

type bfclSampleOptions struct {
	dataDir string
	output  string
	version string
	verify  string
}

func runBFCLSample(args []string) error {
	options, err := parseBFCLSampleOptions(args)
	if err != nil {
		return err
	}
	manifest, err := bfcl.GenerateSampleManifest(
		options.dataDir,
		bfclDataCommit,
		options.version,
		bfcl.DefaultSampleTargets,
	)
	if err != nil {
		return err
	}
	encoded, err := bfcl.MarshalSampleManifest(manifest)
	if err != nil {
		return err
	}
	if options.verify != "" {
		frozen, err := os.ReadFile(options.verify)
		if err != nil {
			return fmt.Errorf("read frozen BFCL sample manifest: %w", err)
		}
		if string(encoded) != string(frozen) {
			return fmt.Errorf("generated BFCL sample manifest differs from %s", options.verify)
		}
		_, digest, err := bfcl.LoadSampleManifest(options.verify)
		if err != nil {
			return err
		}
		fmt.Fprintf(os.Stderr, "BFCL sample manifest verified: %s sha256=%s\n", options.verify, digest)
		return nil
	}
	if _, err := os.Stat(options.output); err == nil {
		return fmt.Errorf("BFCL sample manifest already exists: %s", options.output)
	} else if !os.IsNotExist(err) {
		return err
	}
	digest, err := bfcl.WriteSampleManifest(options.output, manifest)
	if err != nil {
		return err
	}
	total := 0
	for _, split := range manifest.Splits {
		total += split.SampleSize
		fmt.Fprintf(os.Stderr, "Sampled BFCL %s: %d/%d\n", split.Category, split.SampleSize, split.Population)
	}
	fmt.Fprintf(os.Stderr, "BFCL sample manifest written: %s total=%d sha256=%s\n", options.output, total, digest)
	return nil
}

func parseBFCLSampleOptions(args []string) (bfclSampleOptions, error) {
	var options bfclSampleOptions
	fs := flag.NewFlagSet("bfcl-sample", flag.ContinueOnError)
	fs.StringVar(&options.dataDir, "data-dir", "third_party/gorilla/berkeley-function-call-leaderboard/bfcl_eval/data", "BFCL data directory")
	fs.StringVar(&options.output, "output", "configs/bfcl-sample-v1.json", "new frozen BFCL sample manifest")
	fs.StringVar(&options.version, "version", "v1", "sample manifest version")
	fs.StringVar(&options.verify, "verify", "", "regenerate and byte-compare with a frozen manifest")
	if err := fs.Parse(args); err != nil {
		return options, err
	}
	options.dataDir = filepath.Clean(options.dataDir)
	options.output = filepath.Clean(options.output)
	if options.verify != "" {
		options.verify = filepath.Clean(options.verify)
	}
	if options.version == "" {
		return options, fmt.Errorf("BFCL sample manifest version is required")
	}
	return options, nil
}
