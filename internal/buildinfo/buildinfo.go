// Package buildinfo reports what the running binary was built from.
package buildinfo

import (
	"runtime"
	"runtime/debug"
)

// Revision returns the vcs.revision stamped into the binary by `go build` and
// whether the tree had uncommitted changes. Both are empty/false under
// `go run` and `go test`, which do not stamp VCS settings. The repository is
// deliberately never consulted at run time: a bench binary is often run on
// another machine or from another working directory, where no checkout exists.
func Revision() (commit string, dirty bool) {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		return "", false
	}
	for _, setting := range info.Settings {
		switch setting.Key {
		case "vcs.revision":
			commit = setting.Value
		case "vcs.modified":
			dirty = setting.Value == "true"
		}
	}
	return commit, dirty
}

// GoVersion is the toolchain that built the binary.
func GoVersion() string { return runtime.Version() }
