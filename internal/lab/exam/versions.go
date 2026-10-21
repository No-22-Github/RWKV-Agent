package exam

import (
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

// ExamVersion is one row of bench/exam/versions.json: the version a case set
// was published under, the hash that identifies it, and when it took effect.
type ExamVersion struct {
	Version string `json:"version"`
	Hash    string `json:"hash"`
	Cases   int    `json:"cases"`
	Since   string `json:"since"`
	Note    string `json:"note"`
}

// The manifest names are the family plus the version from versions.json.
const (
	ExamFamily      = "agent-exam"
	ExamQuickFamily = "agent-exam-quick"
)

// readExamVersions loads the hand-maintained version ledger.
func readExamVersions(path string) (map[string][]ExamVersion, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read exam versions: %w", err)
	}
	var versions map[string][]ExamVersion
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&versions); err != nil {
		return nil, fmt.Errorf("decode %s: %w", path, err)
	}
	return versions, nil
}

// versionFor returns the version the case set is published under. The hash is
// never inferred from the size of a change: only a person can say whether an
// edit added cases (major) or reworded one (minor), so a hash that is not the
// last recorded one is an error, not a new version.
func versionFor(versions map[string][]ExamVersion, family, hash string, cases int) (string, error) {
	entries := versions[family]
	if len(entries) == 0 {
		return "", fmt.Errorf("versions.json has no entry for %s (computed hash %s, %d cases); add one", family, hash, cases)
	}
	last := entries[len(entries)-1]
	if last.Hash != hash {
		return "", fmt.Errorf("考卷内容变了，请在 versions.json 里加一条新版本（增删题升主版本，只改题面升次版本）：%s 现在 %d 题、hash %s，最后一条 %s 记的是 %d 题、hash %s",
			family, cases, hash, last.Version, last.Cases, last.Hash)
	}
	if !strings.HasPrefix(last.Version, "v") {
		return "", fmt.Errorf("%s: version %q must be written v<major>.<minor>", family, last.Version)
	}
	return last.Version, nil
}
