package runs

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// wireGateReport runs the validity gate over a minimal run.json and returns its
// report. Most gates fail because the fixture is minimal; the tests below only
// read the wire line.
func wireGateReport(t *testing.T, wirePreset string) string {
	t.Helper()
	dir := t.TempDir()
	run, err := os.Create(filepath.Join(dir, "run.json"))
	if err != nil {
		t.Fatal(err)
	}
	if _, err := run.WriteString(`{"harness":{"wire_preset":"` + wirePreset + `"},"model":{}}`); err != nil {
		t.Fatal(err)
	}
	run.Close()
	if err := os.WriteFile(filepath.Join(dir, "summary.json"), []byte(`{}`), 0o644); err != nil {
		t.Fatal(err)
	}
	report, _ := RunCheckCaptured(CheckArgs{RunDir: dir, Arm: "greedy", RWKV: true})
	return report
}

// A run.json from before 2026-10-21 records g1k; a current one records
// agent-wire-v1.0. Both name the same wire, so both pass.
func TestWireGateAcceptsOldAndNewRecordedNames(t *testing.T) {
	for _, recorded := range []string{"g1k", "agent-wire-v1.0"} {
		report := wireGateReport(t, recorded)
		if !strings.Contains(report, "PASS wire_preset is agent-wire-v1.0") {
			t.Errorf("wire_preset %q did not pass the gate:\n%s", recorded, report)
		}
	}
}

func TestWireGateRejectsAnotherWire(t *testing.T) {
	report := wireGateReport(t, "xml-v1")
	if !strings.Contains(report, "FAIL wire_preset is agent-wire-v1.0") {
		t.Errorf("wire_preset xml-v1 passed the agent-wire gate:\n%s", report)
	}
}
