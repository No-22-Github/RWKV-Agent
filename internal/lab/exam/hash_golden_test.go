package exam

import (
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

// examHashes pins the hash of the committed manifests. The hash covers case
// ids and case.json digests only — not the manifest name — so renaming an exam
// leaves it unchanged. A mismatch means the case set or a case file changed;
// that needs a versions.json entry, not an updated expectation.
var examHashes = map[string]string{
	"bench/exam/full.json":  "0c0101883de4a8d63a6734cf7d2e841ca6788454d533d9c4f12ab36c5fdb1e2b",
	"bench/exam/quick.json": "dc2ae8b9a8acb55d4b2aacf5477176443c8b3c7954623502b391f1a700bae623",
}

func TestExamHashesArePinned(t *testing.T) {
	paths := DefaultPaths()
	for rel, want := range examHashes {
		manifest, err := eval.ReadExamManifest(filepath.Join(paths.Root, filepath.FromSlash(rel)))
		if err != nil {
			t.Errorf("%s: %v", rel, err)
			continue
		}
		if manifest.Hash != want {
			t.Errorf("%s hash = %s, want %s (the case set changed)", rel, manifest.Hash, want)
		}
	}
}
