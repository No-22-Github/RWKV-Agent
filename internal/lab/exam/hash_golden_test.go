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
	"bench/exam/full.json":  "c5ae05fc103d26fbb3489aab05bb61bd249a06100cd8e30f444a399c9ddec7c7",
	"bench/exam/quick.json": "4f878054600911849bce49fb31346b5973d46e69484090f2f053e81bfff0ef27",
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
