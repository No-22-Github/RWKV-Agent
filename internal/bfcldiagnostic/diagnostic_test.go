package bfcldiagnostic

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/bfcl"
)

func TestAnalyzeDerivesSampleAccuracyAndTrigger(t *testing.T) {
	t.Parallel()
	directory := t.TempDir()
	manifestPath := filepath.Join(directory, "sample.json")
	manifest := bfcl.SampleManifest{
		SchemaVersion:   bfcl.SampleManifestSchemaVersion,
		ManifestVersion: "v1",
		DataCommit:      "commit",
		Algorithm:       bfcl.SampleAlgorithmVersion,
		Splits: []bfcl.SampleSplit{{
			Category:   "simple_python",
			Population: 30,
			SampleSize: 3,
			Strata: []bfcl.SampleStratum{{
				ToolBucket: 0, LengthBucket: 0, Population: 30, SampleSize: 3,
			}},
			IDs: []string{"simple_python_0", "simple_python_1", "simple_python_2"},
		}},
	}
	if _, err := bfcl.WriteSampleManifest(manifestPath, manifest); err != nil {
		t.Fatal(err)
	}
	scoreDir := filepath.Join(directory, "score", "model", "non_live")
	if err := os.MkdirAll(scoreDir, 0o700); err != nil {
		t.Fatal(err)
	}
	score := "{\"accuracy\":0.9,\"correct_count\":27,\"total_count\":30}\n" +
		"{\"id\":\"simple_python_0\",\"valid\":false}\n" +
		"{\"id\":\"simple_python_1\",\"valid\":false}\n" +
		"{\"id\":\"simple_python_2\",\"valid\":false}\n"
	if err := os.WriteFile(filepath.Join(scoreDir, "BFCL_v4_simple_python_score.json"), []byte(score), 0o600); err != nil {
		t.Fatal(err)
	}
	report, err := Analyze(manifestPath, filepath.Join(directory, "score"))
	if err != nil {
		t.Fatal(err)
	}
	result := report.Splits[0]
	if result.SampleCorrect != 0 || result.FullCorrect != 27 || !result.TriggerExpansion {
		t.Fatalf("result = %+v", result)
	}
}
