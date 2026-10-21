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

// A format ablation is checked against wire_profile; an old run records the
// retired spelling of the same profile, so either spelling on either side
// passes, and a different modifier still fails.
func TestWireProfileGateComparesCurrentNames(t *testing.T) {
	report := func(recorded, want string) string {
		t.Helper()
		dir := t.TempDir()
		if err := os.WriteFile(filepath.Join(dir, "run.json"),
			[]byte(`{"harness":{"wire_profile":"`+recorded+`"},"model":{}}`), 0o644); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(dir, "summary.json"), []byte(`{}`), 0o644); err != nil {
			t.Fatal(err)
		}
		out, _ := RunCheckCaptured(CheckArgs{RunDir: dir, Arm: "greedy", RWKV: true, Profile: want})
		return out
	}
	for _, pair := range [][2]string{
		{"g1k-think", "agent-wire-think-v1.0"},
		{"agent-wire-think-v1.0", "g1k-think"},
		{"g1k+think-fast", "agent-wire-v1.0+think-fast"},
		{"agent-wire-v1.0+think-fast", "agent-wire-v1.0+think-fast"},
	} {
		if out := report(pair[0], pair[1]); !strings.Contains(out, "PASS wire_profile == "+pair[1]) {
			t.Errorf("recorded %q, wanted %q: did not pass\n%s", pair[0], pair[1], out)
		}
	}
	if out := report("g1k+think-full", "agent-wire-v1.0+think-fast"); !strings.Contains(out, "FAIL wire_profile") {
		t.Errorf("a different modifier passed:\n%s", out)
	}
}

func TestLedgerRecordsCurrentWireNames(t *testing.T) {
	for recorded, want := range map[string]string{
		"g1k": "agent-wire-v1.0", "g1k+think-fast": "agent-wire-v1.0+think-fast",
		"g1k-think": "agent-wire-think-v1.0", "xml-v1+anchor": "xml-v1+anchor",
	} {
		if got := recordedWire(recorded); got != want {
			t.Errorf("recordedWire(%q) = %v, want %q", recorded, got, want)
		}
	}
}
