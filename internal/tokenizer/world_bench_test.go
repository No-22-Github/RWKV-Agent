package tokenizer

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func loadFixtureTexts(tb testing.TB) []string {
	tb.Helper()
	file, err := os.Open(filepath.Join("testdata", fixtureTexts))
	if err != nil {
		tb.Skipf("fixture texts not found: %v", err)
	}
	defer file.Close()
	decoder := json.NewDecoder(file)
	var texts []string
	for decoder.More() {
		var row struct {
			Text string `json:"text"`
		}
		if err := decoder.Decode(&row); err != nil {
			tb.Fatalf("decode fixture text: %v", err)
		}
		texts = append(texts, row.Text)
	}
	return texts
}

func BenchmarkCountCorpus(b *testing.B) {
	world, err := OpenWorld(findVocab(b))
	if err != nil {
		b.Fatal(err)
	}
	texts := loadFixtureTexts(b)
	total := 0
	for _, text := range texts {
		total += len(text)
	}
	b.SetBytes(int64(total))
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		for _, text := range texts {
			world.Count(text)
		}
	}
}

func BenchmarkOpenWorld(b *testing.B) {
	vocab := findVocab(b)
	for i := 0; i < b.N; i++ {
		if _, err := OpenWorld(vocab); err != nil {
			b.Fatal(err)
		}
	}
}
