package geval

import (
	"bufio"
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Version names the item set. A change to sampling, prompts or sources is a
// new version; runs record the items sha so mismatched comparisons show.
const Version = "v1.0"

// Task names, in report order.
const (
	TaskIFEvalEN  = "ifeval-en"
	TaskIFEvalZH  = "ifeval-zh"
	TaskMTBenchEN = "mtbench-en"
	TaskMTBenchZH = "mtbench-zh"
	TaskGSM8K     = "gsm8k"
	TaskMATH500   = "math500"
	TaskCEval     = "ceval"
	TaskCMMLU     = "cmmlu"
)

var taskOrder = []string{TaskIFEvalEN, TaskIFEvalZH, TaskMTBenchEN, TaskMTBenchZH, TaskGSM8K, TaskMATH500, TaskCEval, TaskCMMLU}

// Item is one eval question. Turns are the user messages exactly as sent
// (task instructions already appended); Raw is the source question alone,
// which is what decontamination compares.
type Item struct {
	ID      string   `json:"id"`
	Task    string   `json:"task"`
	Lang    string   `json:"lang"`
	Stratum string   `json:"stratum,omitempty"`
	Quick   bool     `json:"quick"`
	Source  string   `json:"source"`
	Turns   []string `json:"turns"`
	Raw     string   `json:"raw"`
	// Answer is the gold answer: a number (GSM8K), a LaTeX expression
	// (MATH-500) or a choice letter (C-Eval, CMMLU).
	Answer string `json:"answer,omitempty"`
	// Reference holds MT-Bench reference answers, one per turn, for the
	// categories the judge grades against a reference.
	Reference    []string         `json:"reference,omitempty"`
	Instructions []string         `json:"instruction_id_list,omitempty"`
	Kwargs       []map[string]any `json:"kwargs,omitempty"`
	Contam       *Contam          `json:"contam,omitempty"`
}

// Contam is the decontamination result for one item: the share of its
// n-grams found in the training rows and the row that holds most of them.
type Contam struct {
	NGrams   int     `json:"ngrams"`
	Hits     int     `json:"hits"`
	Coverage float64 `json:"coverage"`
	BestRow  int     `json:"best_row"`
	BestHits int     `json:"best_row_hits"`
	Flagged  bool    `json:"flagged"`
}

// DefaultItemsPath is bench/general-eval/<Version>/items.jsonl.
func DefaultItemsPath() string {
	return filepath.Join(lab.RepoRoot(), "bench", "general-eval", Version, "items.jsonl")
}

func loadItems(path string) ([]Item, string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, "", err
	}
	sum := sha256.Sum256(data)
	var items []Item
	for i, line := range lab.SplitJSONLLines(string(data)) {
		if line == "" {
			continue
		}
		var item Item
		dec := json.NewDecoder(bytes.NewReader([]byte(line)))
		dec.UseNumber()
		if err := dec.Decode(&item); err != nil {
			return nil, "", fmt.Errorf("%s:%d: %w", path, i+1, err)
		}
		items = append(items, item)
	}
	return items, hex.EncodeToString(sum[:]), nil
}

func writeItems(path string, items []Item) error {
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		return err
	}
	var buf bytes.Buffer
	for _, item := range items {
		line, err := lab.EncodeJSON(item, 0)
		if err != nil {
			return err
		}
		buf.Write(line)
		buf.WriteByte('\n')
	}
	return os.WriteFile(path, buf.Bytes(), 0o644)
}

// readJSONL decodes every line of a JSON Lines file into maps, numbers kept
// as json.Number.
func readJSONL(path string) ([]map[string]any, error) {
	fh, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer fh.Close()
	var out []map[string]any
	scanner := bufio.NewScanner(fh)
	scanner.Buffer(make([]byte, 1<<20), 64<<20)
	for n := 1; scanner.Scan(); n++ {
		line := bytes.TrimSpace(scanner.Bytes())
		if len(line) == 0 {
			continue
		}
		row, err := decodeRow(line)
		if err != nil {
			return nil, fmt.Errorf("%s:%d: %w", path, n, err)
		}
		out = append(out, row)
	}
	return out, scanner.Err()
}

func decodeRow(line []byte) (map[string]any, error) {
	dec := json.NewDecoder(bytes.NewReader(line))
	dec.UseNumber()
	var row map[string]any
	if err := dec.Decode(&row); err != nil {
		return nil, err
	}
	return row, nil
}
