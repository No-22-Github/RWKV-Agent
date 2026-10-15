package runs

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type gateLine struct {
	name   string
	ok     bool
	detail string
}

func runBatchGate(harness map[string]any, wantWaitMS, wantMax int) []gateLine {
	var lines []gateLine
	checkRemoteBatch(func(name string, ok bool, detail string) {
		lines = append(lines, gateLine{name, ok, detail})
	}, harness, wantWaitMS, wantMax)
	return lines
}

func TestCheckRemoteBatchGate(t *testing.T) {
	t.Parallel()
	for _, test := range []struct {
		name    string
		harness map[string]any
		pass    bool
		note    string
	}{
		{"matching batched run", map[string]any{"remote_batch_wait_ms": 20.0, "remote_batch_max": 32.0}, true, ""},
		{"legacy unbatched run", map[string]any{"remote_batch_wait_ms": 0.0}, true, "not pair it directly"},
		{"wrong window", map[string]any{"remote_batch_wait_ms": 10.0, "remote_batch_max": 32.0}, false, ""},
		{"wrong cap", map[string]any{"remote_batch_wait_ms": 20.0, "remote_batch_max": 64.0}, false, ""},
		{"window without recorded cap", map[string]any{"remote_batch_wait_ms": 20.0}, false, ""},
		{"window missing", map[string]any{}, false, ""},
	} {
		lines := runBatchGate(test.harness, 20, 32)
		pass := true
		details := ""
		for _, line := range lines {
			pass = pass && line.ok
			details += line.detail
		}
		if pass != test.pass {
			t.Errorf("%s: pass = %v, want %v (%+v)", test.name, pass, test.pass, lines)
		}
		if test.note != "" && !strings.Contains(details, test.note) {
			t.Errorf("%s: detail %q lacks %q", test.name, details, test.note)
		}
	}
	// An explicit 0 expectation is an exact match, not the legacy allowance.
	if lines := runBatchGate(map[string]any{"remote_batch_wait_ms": 20.0}, 0, 0); len(lines) != 1 || lines[0].ok {
		t.Fatalf("wait 0 expectation accepted a batched run: %+v", lines)
	}
}

func writeRunManifest(t *testing.T, completion string, harness map[string]any) string {
	t.Helper()
	dir := t.TempDir()
	data, err := json.Marshal(map[string]any{"model": map[string]any{"completion": completion}, "harness": harness})
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(dir, "run.json"), data, 0o600); err != nil {
		t.Fatal(err)
	}
	return dir
}

func TestCompareWarnsOnDifferentBatchSettings(t *testing.T) {
	t.Parallel()
	batched := writeRunManifest(t, "rwkv-lightning-cuda", map[string]any{"remote_batch_wait_ms": 20, "remote_batch_max": 32})
	batchedToo := writeRunManifest(t, "rwkv-lightning-cuda", map[string]any{"remote_batch_wait_ms": 20, "remote_batch_max": 32})
	unbatched := writeRunManifest(t, "rwkv-lightning-cuda", map[string]any{"remote_batch_wait_ms": 0})
	api := writeRunManifest(t, "chat-completions", map[string]any{"remote_batch_wait_ms": 0})

	if warning := remoteBatchWarning(batched, unbatched); !strings.Contains(warning, "batch settings differ") {
		t.Fatalf("batched vs unbatched warning = %q", warning)
	}
	if warning := remoteBatchWarning(batched, batchedToo); warning != "" {
		t.Fatalf("matching runs warned: %q", warning)
	}
	if warning := remoteBatchWarning(batched, api); warning != "" {
		t.Fatalf("RWKV vs API run warned: %q", warning)
	}
	if warning := remoteBatchWarning(batched, "some-ledger-config"); warning != "" {
		t.Fatalf("ledger config side warned: %q", warning)
	}
}
