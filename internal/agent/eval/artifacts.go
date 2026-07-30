package eval

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

type ArtifactPaths struct {
	Directory string
	Run       string
	Trace     string
	Summary   string
}

func WriteArtifacts(path string, report Report) (ArtifactPaths, error) {
	if path == "" {
		return ArtifactPaths{}, fmt.Errorf("eval output directory is required")
	}
	absolute, err := filepath.Abs(path)
	if err != nil {
		return ArtifactPaths{}, err
	}
	if _, err := os.Stat(absolute); err == nil {
		return ArtifactPaths{}, fmt.Errorf("eval output already exists: %s", absolute)
	} else if !errors.Is(err, os.ErrNotExist) {
		return ArtifactPaths{}, err
	}
	parent := filepath.Dir(absolute)
	if err := os.MkdirAll(parent, 0o700); err != nil {
		return ArtifactPaths{}, err
	}
	temporary, err := os.MkdirTemp(parent, ".agent-eval-")
	if err != nil {
		return ArtifactPaths{}, err
	}
	cleanup := true
	defer func() {
		if cleanup {
			_ = os.RemoveAll(temporary)
		}
	}()
	if err := writeJSON(filepath.Join(temporary, "run.json"), report.Manifest); err != nil {
		return ArtifactPaths{}, err
	}
	if err := writeTrace(filepath.Join(temporary, "trace.jsonl"), report.Trace); err != nil {
		return ArtifactPaths{}, err
	}
	if err := writeJSON(filepath.Join(temporary, "summary.json"), report.Summary); err != nil {
		return ArtifactPaths{}, err
	}
	if err := os.Rename(temporary, absolute); err != nil {
		return ArtifactPaths{}, err
	}
	cleanup = false
	return ArtifactPaths{
		Directory: absolute,
		Run:       filepath.Join(absolute, "run.json"),
		Trace:     filepath.Join(absolute, "trace.jsonl"),
		Summary:   filepath.Join(absolute, "summary.json"),
	}, nil
}

func writeJSON(path string, value any) error {
	data, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	data = append(data, '\n')
	return os.WriteFile(path, data, 0o600)
}

func writeTrace(path string, records []TraceRecord) error {
	handle, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o600)
	if err != nil {
		return err
	}
	writer := bufio.NewWriter(handle)
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(false)
	for _, record := range records {
		if err := encoder.Encode(record); err != nil {
			_ = handle.Close()
			return err
		}
	}
	if err := writer.Flush(); err != nil {
		_ = handle.Close()
		return err
	}
	return handle.Close()
}
