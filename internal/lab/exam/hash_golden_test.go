package exam

import (
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/eval"

	"github.com/no22/RWKV-Agent/internal/lab/labtest"
)

// examHashes pins the hash of the committed manifests. The hash covers case
// ids and case.json digests only — not the manifest name — so renaming an exam
// leaves it unchanged. A mismatch means the case set or a case file changed;
// that needs a versions.json entry, not an updated expectation.
var examHashes = map[string]string{
	"bench/exam/full.json":  "88c8d0bf821f1b0d251611d7b3aafd000388184e55f3c6ada8e8119dd0cc9a41",
	"bench/exam/quick.json": "14f184f0e146b485cd68939869042e18ba078927acb247772dd3568ddc53dcf1",
}

func TestExamHashesArePinned(t *testing.T) {
	paths := DefaultPaths()
	labtest.RequireBench(t, paths.ExamDir)
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
