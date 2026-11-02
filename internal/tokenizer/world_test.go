package tokenizer

import (
	"bytes"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	rwkvtok "github.com/No-22-Github/rwkv-tokenizer-go"
)

// testdata/world-corpus.* was generated from the same deterministic builders
// used by the round-3 probe and e2e corpora. The truth counts come from the
// Python trie tokenizer implementation (round-3 census cross-check: 0
// mismatches on shared texts).
const (
	fixtureTexts  = "world-corpus.jsonl"
	fixtureCounts = "world-corpus-counts.json"
)

func TestWorldMatchesPythonCountsOnCorpus(t *testing.T) {
	world := World()
	countsFile, err := os.Open(filepath.Join("testdata", fixtureCounts))
	if err != nil {
		t.Skipf("fixture counts not found: %v", err)
	}
	defer countsFile.Close()
	var fixture struct {
		VocabSHA256 string         `json:"vocab_sha256"`
		NTexts      int            `json:"n_texts"`
		Counts      map[string]int `json:"counts"`
	}
	if err := json.NewDecoder(countsFile).Decode(&fixture); err != nil {
		t.Fatalf("decode fixture counts: %v", err)
	}
	if world.VocabSHA256() != fixture.VocabSHA256 {
		t.Fatalf("vocab sha256 mismatch: Go %s != fixture %s",
			world.VocabSHA256(), fixture.VocabSHA256)
	}
	textsFile, err := os.Open(filepath.Join("testdata", fixtureTexts))
	if err != nil {
		t.Skipf("fixture texts not found: %v", err)
	}
	defer textsFile.Close()
	decoder := json.NewDecoder(textsFile)
	checked := 0
	for decoder.More() {
		var row struct {
			ID   string `json:"id"`
			Text string `json:"text"`
		}
		if err := decoder.Decode(&row); err != nil {
			t.Fatalf("decode fixture text %d: %v", checked, err)
		}
		want, ok := fixture.Counts[row.ID]
		if !ok {
			t.Fatalf("fixture text %s has no truth count", row.ID)
		}
		if got := world.Count(row.Text); got != want {
			t.Fatalf("%s: Go count %d != Python count %d", row.ID, got, want)
		}
		checked++
	}
	if checked != fixture.NTexts {
		t.Fatalf("checked %d texts, fixture has %d", checked, fixture.NTexts)
	}
}

func TestWorldCountsSmallSamples(t *testing.T) {
	world := World()
	// Exact pins from the round-3 census Python runs.
	pins := map[string]int{
		"The quick brown fox jumps over the lazy dog. Observatory operations were audited in 2024.": 19,
		"中国科学院国家天文台在2024年发布了新的巡天数据，总计6,412人次参与观测。":                                                  37,
		"def align_frames(frames, reference):\n    offsets = []\n    return offsets\n":              18,
		"- Item 3: status verified on site, reference 412\n- Item 4: logs uploaded\n":               20,
		"Row 17: the entry mirrors the standard layout of the catalogue. Status remains unchanged.": 17,
		"混合文本：English mixed with 中文与数字 6412 和标点！":                                                   21,
	}
	for text, want := range pins {
		if got := world.Count(text); got != want {
			t.Fatalf("Count(%q) = %d, want %d", text, got, want)
		}
	}
	if got := world.Count("<EOD>"); got != 1 {
		t.Fatalf("Count(<EOD>) = %d, want 1 (trie hpp token 0)", got)
	}
}

func TestVocabPathMatchesWorld(t *testing.T) {
	cache := t.TempDir()
	t.Setenv("HOME", cache)
	t.Setenv("XDG_CACHE_HOME", cache)
	path, err := VocabPath()
	if err != nil {
		t.Fatal(err)
	}
	onDisk, err := rwkvtok.NewFromFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if onDisk.VocabSHA256() != World().VocabSHA256() {
		t.Fatalf("file %s differs from the embedded vocabulary", path)
	}
}

func TestWriteVocabReusesAndRepairs(t *testing.T) {
	data, err := rwkvtok.DefaultVocab()
	if err != nil {
		t.Fatal(err)
	}
	dir := filepath.Join(t.TempDir(), "cache")
	path, err := writeVocab(dir, data)
	if err != nil {
		t.Fatal(err)
	}
	if filepath.Base(path) != vocabFilename {
		t.Fatalf("path = %s, want the name the native engine looks for", path)
	}
	before, err := os.Stat(path)
	if err != nil {
		t.Fatal(err)
	}
	if again, err := writeVocab(dir, data); err != nil || again != path {
		t.Fatalf("second write = %s, %v", again, err)
	}
	after, err := os.Stat(path)
	if err != nil {
		t.Fatal(err)
	}
	if !os.SameFile(before, after) {
		t.Fatal("identical vocabulary was rewritten")
	}
	if err := os.WriteFile(path, []byte("truncated"), 0o644); err != nil {
		t.Fatal(err)
	}
	if _, err := writeVocab(dir, data); err != nil {
		t.Fatal(err)
	}
	got, err := os.ReadFile(path)
	if err != nil || !bytes.Equal(got, data) {
		t.Fatalf("damaged file not repaired: %d bytes, %v", len(got), err)
	}
	entries, err := os.ReadDir(dir)
	if err != nil || len(entries) != 1 {
		t.Fatalf("leftover temp files: %v, %v", entries, err)
	}
}
