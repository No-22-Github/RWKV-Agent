package exam

import (
	"strings"
	"testing"
)

func TestVersionForUsesLastRecordedVersion(t *testing.T) {
	versions := map[string][]ExamVersion{
		ExamFamily: {
			{Version: "v0.9", Hash: "old", Cases: 100},
			{Version: "v1.0", Hash: "current", Cases: 568},
		},
	}
	version, err := versionFor(versions, ExamFamily, "current", 568)
	if err != nil {
		t.Fatal(err)
	}
	if version != "v1.0" {
		t.Fatalf("version = %q, want v1.0", version)
	}
}

// An unrecorded hash must stop the build: only a person can decide whether the
// case set gained cases (major) or had a prompt reworded (minor).
func TestVersionForRejectsAnUnrecordedHash(t *testing.T) {
	versions := map[string][]ExamVersion{
		ExamFamily: {{Version: "v1.0", Hash: "current", Cases: 568}},
	}
	_, err := versionFor(versions, ExamFamily, "changed", 569)
	if err == nil {
		t.Fatal("an unrecorded hash was accepted")
	}
	if !strings.Contains(err.Error(), "考卷内容变了，请在 versions.json 里加一条新版本") {
		t.Fatalf("error %q does not tell the reader what to do", err)
	}
}

func TestVersionForRejectsAMissingFamily(t *testing.T) {
	if _, err := versionFor(map[string][]ExamVersion{}, ExamFamily, "hash", 1); err == nil {
		t.Fatal("a family with no versions was accepted")
	}
}

func TestVersionForRequiresTheVersionSpelling(t *testing.T) {
	versions := map[string][]ExamVersion{
		ExamFamily: {{Version: "1.0", Hash: "hash", Cases: 1}},
	}
	if _, err := versionFor(versions, ExamFamily, "hash", 1); err == nil {
		t.Fatal("a version without the v prefix was accepted")
	}
}
