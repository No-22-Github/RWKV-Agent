package lab

import (
	"crypto/sha256"
	"encoding/hex"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strings"
)

// GitOutput runs git at the repository root and returns trimmed stdout, or ""
// on any error. Provenance records use it for commit and dirty state.
func GitOutput(args ...string) string {
	cmd := exec.Command("git", args...)
	cmd.Dir = RepoRoot()
	out, err := cmd.Output()
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(out))
}

// CaseSourceSHA256 hashes every case.json under root, in sorted path order,
// as rel-path NUL contents. Unreadable files contribute only their path.
func CaseSourceSHA256(root string) string {
	digest := sha256.New()
	var paths []string
	filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if !d.IsDir() && d.Name() == "case.json" {
			paths = append(paths, path)
		}
		return nil
	})
	sort.Strings(paths)
	for _, path := range paths {
		rel, err := filepath.Rel(root, path)
		if err != nil {
			continue
		}
		digest.Write([]byte(rel))
		digest.Write([]byte{0})
		data, err := os.ReadFile(path)
		if err == nil {
			digest.Write(data)
		}
	}
	return hex.EncodeToString(digest.Sum(nil))
}

// Exists reports whether path exists, directories included.
func Exists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}

// NilIfEmpty maps "" to a JSON null.
func NilIfEmpty(s string) any {
	if s == "" {
		return nil
	}
	return s
}
