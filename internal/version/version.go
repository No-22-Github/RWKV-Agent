// Package version prints what a binary is, in a form a script can grep.
package version

import (
	"fmt"
	"io"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/agent/product"
	"github.com/no22/RWKV-Agent/internal/buildinfo"
)

// Print writes the version block: one "key: value" line each, the tool-catalog
// and wire values read from the code that owns them so they cannot drift from
// the App's defaults. The commit is "unknown" for a binary built without VCS
// stamping (`go run`, `go test`).
func Print(w io.Writer, name string) {
	commit, dirty := buildinfo.Revision()
	if commit == "" {
		commit = "unknown"
	}
	fmt.Fprintln(w, name)
	fmt.Fprintf(w, "commit: %s\n", commit)
	fmt.Fprintf(w, "dirty: %t\n", dirty)
	fmt.Fprintf(w, "go: %s\n", buildinfo.GoVersion())
	fmt.Fprintf(w, "harness: %s\n", eval.HarnessVersion)
	fmt.Fprintf(w, "scorer: %s\n", eval.ScorerVersion)
	fmt.Fprintf(w, "outcome: %s\n", eval.OutcomeTaxonomyVersion)
	fmt.Fprintf(w, "tool-catalog: %s\n", product.AgentToolV3)
	fmt.Fprintf(w, "wire: %s\n", agentapi.NewConfigProfile)
}
