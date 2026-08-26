package bfcl

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestNaturalIDLessUsesNumericComponents(t *testing.T) {
	t.Parallel()
	less, err := naturalIDLess("live_simple", "live_simple_2-0-0", "live_simple_10-0-0")
	if err != nil {
		t.Fatal(err)
	}
	if !less {
		t.Fatal("natural order did not place 2 before 10")
	}
}

func TestSampleSplitUsesLargestRemainderTieBreakAndEvenIndices(t *testing.T) {
	t.Parallel()
	cases := []Case{
		sampleCase("simple_python", "simple_python_0", 1, 20),
		sampleCase("simple_python", "simple_python_1", 1, 20),
		sampleCase("simple_python", "simple_python_2", 1, 30),
		sampleCase("simple_python", "simple_python_3", 1, 30),
		sampleCase("simple_python", "simple_python_4", 1, 40),
		sampleCase("simple_python", "simple_python_5", 1, 40),
	}
	split, err := sampleSplit(cases, 3)
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"simple_python_0", "simple_python_2", "simple_python_4"}
	if !reflect.DeepEqual(split.IDs, want) {
		t.Fatalf("ids = %v, want %v", split.IDs, want)
	}
}

func TestGenerateSampleManifestIsByteDeterministic(t *testing.T) {
	t.Parallel()
	directory := t.TempDir()
	content := ""
	for index := 0; index < 10; index++ {
		content += sampleRecord(fmt.Sprintf("simple_python_%d", index), index+1) + "\n"
	}
	if err := os.WriteFile(filepath.Join(directory, "BFCL_v4_simple_python.json"), []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
	first, err := GenerateSampleManifest(directory, "commit", "v1", []SampleTarget{{Category: "simple_python", Count: 4}})
	if err != nil {
		t.Fatal(err)
	}
	second, err := GenerateSampleManifest(directory, "commit", "v1", []SampleTarget{{Category: "simple_python", Count: 4}})
	if err != nil {
		t.Fatal(err)
	}
	firstBytes, _ := MarshalSampleManifest(first)
	secondBytes, _ := MarshalSampleManifest(second)
	if !reflect.DeepEqual(firstBytes, secondBytes) {
		t.Fatal("sample manifests differ across identical runs")
	}
}

func TestFilterBySampleList(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "sample.json")
	manifest := SampleManifest{
		SchemaVersion:   SampleManifestSchemaVersion,
		ManifestVersion: "v1",
		DataCommit:      "commit",
		Algorithm:       SampleAlgorithmVersion,
		Splits: []SampleSplit{{
			Category:   "simple_python",
			Population: 2,
			SampleSize: 1,
			Strata: []SampleStratum{{
				ToolBucket: 0, LengthBucket: 0, Population: 2, SampleSize: 1,
			}},
			IDs: []string{"simple_python_2"},
		}},
	}
	if _, err := WriteSampleManifest(path, manifest); err != nil {
		t.Fatal(err)
	}
	filtered, err := FilterBySampleList([]Case{
		{ID: "simple_python_1", Category: "simple_python"},
		{ID: "simple_python_2", Category: "simple_python"},
	}, path)
	if err != nil {
		t.Fatal(err)
	}
	if len(filtered) != 1 || filtered[0].ID != "simple_python_2" {
		t.Fatalf("filtered = %+v", filtered)
	}
}

func TestExpandedSampleTargetsUsesMechanicalRules(t *testing.T) {
	t.Parallel()
	manifest := SampleManifest{Splits: []SampleSplit{
		{Category: "live_parallel", Population: 16, SampleSize: 16},
		{Category: "multiple", Population: 200, SampleSize: 30},
		{Category: "simple_python", Population: 400, SampleSize: 40},
	}}
	targets, err := ExpandedSampleTargets(manifest, map[string]bool{
		"live_parallel": true,
		"multiple":      true,
		"simple_python": true,
	})
	if err != nil {
		t.Fatal(err)
	}
	want := []SampleTarget{
		{Category: "live_parallel", Count: 16},
		{Category: "multiple", Count: 60},
		{Category: "simple_python", Count: 60},
	}
	if !reflect.DeepEqual(targets, want) {
		t.Fatalf("targets = %+v, want %+v", targets, want)
	}
}

func sampleCase(category, id string, functions, functionLength int) Case {
	raw := json.RawMessage(`{"name":"f"}`)
	if functionLength > len(raw) {
		raw = append(raw, make([]byte, functionLength-len(raw))...)
	}
	values := make([]json.RawMessage, functions)
	for index := range values {
		values[index] = raw
	}
	return Case{ID: id, Category: category, Functions: values}
}

func sampleRecord(id string, padding int) string {
	return fmt.Sprintf(
		`{"id":%q,"question":[[{"role":"user","content":"x"}]],"function":[{"name":"f","description":%q,"parameters":{"type":"dict","properties":{}}}]}`,
		id,
		fmt.Sprintf("%0*d", padding, 0),
	)
}
