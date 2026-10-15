package eval

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeExamFixture(t *testing.T) (root, manifestPath, casePath string) {
	t.Helper()
	root = t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "go.mod"), []byte("module x\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	caseDir := filepath.Join(root, "bench", "a", "case-1")
	if err := os.MkdirAll(caseDir, 0o755); err != nil {
		t.Fatal(err)
	}
	casePath = filepath.Join(caseDir, "case.json")
	body := `{"id":"case-1","description":"d","turns":[{"prompt":"hi","expect":{"tools":[]}}]}`
	if err := os.WriteFile(casePath, []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
	sum, err := FileSHA256(casePath)
	if err != nil {
		t.Fatal(err)
	}
	rows := []ExamCase{{ID: "case-1", Suite: "a", Path: "bench/a/case-1", SHA256: sum}}
	manifest := ExamManifest{Schema: ExamSchema, Name: "exam-test", Hash: ExamHash(rows), Cases: rows}
	data, _ := json.Marshal(manifest)
	if err := os.MkdirAll(filepath.Join(root, "bench", "exam"), 0o755); err != nil {
		t.Fatal(err)
	}
	manifestPath = filepath.Join(root, "bench", "exam", "m.json")
	if err := os.WriteFile(manifestPath, data, 0o644); err != nil {
		t.Fatal(err)
	}
	return root, manifestPath, casePath
}

func TestLoadCasesManifest(t *testing.T) {
	_, manifestPath, casePath := writeExamFixture(t)
	if !IsExamManifest(manifestPath) {
		t.Fatal("manifest not recognized")
	}
	manifest, cases, err := LoadCasesManifest(manifestPath, "")
	if err != nil {
		t.Fatal(err)
	}
	if manifest.Name != "exam-test" || len(cases) != 1 || cases[0].ID != "case-1" {
		t.Fatalf("got %+v %+v", manifest, cases)
	}
	// An edited case without a rebuild must be refused.
	if err := os.WriteFile(casePath, []byte(`{"id":"case-1","description":"changed","turns":[{"prompt":"hi","expect":{"tools":[]}}]}`), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, _, err := LoadCasesManifest(manifestPath, ""); err == nil || !strings.Contains(err.Error(), "changed since the manifest was built") {
		t.Fatalf("stale case accepted: %v", err)
	}
}
