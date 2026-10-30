// Package labtest holds helpers shared by the lab packages' tests.
package labtest

import (
	"errors"
	"io/fs"
	"os"
	"testing"
)

// RequireBench skips the test when path, a file or directory in the bench/
// data checkout, is absent. bench/ is its own repository (docs/guides/data.md),
// so a code-only clone runs everything else and skips these.
func RequireBench(t testing.TB, path string) {
	t.Helper()
	if _, err := os.Stat(path); errors.Is(err, fs.ErrNotExist) {
		t.Skipf("%s not found: no bench/ data checkout (docs/guides/data.md)", path)
	}
}
