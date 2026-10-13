package main

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/tools"
)

// TestMain points the bash tool at the repository's sidecar build: tests run
// from cmd/rwkv-app, where the default local/bin lookup finds nothing, and
// parallel tests cannot use t.Setenv.
func TestMain(m *testing.M) {
	if os.Getenv(tools.BashSidecarEnv) == "" {
		if binary, err := tools.ResolveBashSidecar(filepath.Join("..", "..", "local", "bin", "justbash-sidecar")); err == nil {
			_ = os.Setenv(tools.BashSidecarEnv, binary)
		}
	}
	os.Exit(m.Run())
}

// requireBashSidecar skips tests whose agent session registers the bash tool.
func requireBashSidecar(t *testing.T) {
	t.Helper()
	if _, err := tools.ResolveBashSidecar(""); err != nil {
		t.Skip("bash sidecar not built; run scripts/build-justbash.sh")
	}
}
