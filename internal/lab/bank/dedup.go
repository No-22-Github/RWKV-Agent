package bank

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

const (
	promptJaccardThreshold  = 0.6
	numbersJaccardThreshold = 0.5
)

var (
	dedupWordRe   = regexp.MustCompile(`[a-z0-9]+`)
	dedupNumberRe = regexp.MustCompile(`-?\d+(?:,\d{3})*(?:\.\d+)?`)
)

// markedPair is the report row. The field order matches the Python dict so the
// JSON is byte-identical, not merely deep-equal.
type markedPair struct {
	CaseA          string      `json:"case_a"`
	CaseB          string      `json:"case_b"`
	PromptJaccard  json.Number `json:"prompt_jaccard"`
	NumbersJaccard json.Number `json:"numbers_jaccard"`
}

// runDedup ports dedup.py: mark near-duplicate cases within a scenario.
//
// The exit code is always 0. That is deliberate (§5, "this is not a bug"):
// dedup marks candidate pairs for a human to judge, it does not gate a
// pipeline, and making it fail on a hit would change how the bank is built.
func runDedup(args []string) int {
	fs := newFlagSet("bank dedup",
		"Mark near-duplicate workbank case pairs within the same scenario "+
			"(prompt 3-gram Jaccard > 0.6 or fixture number-set Jaccard > 0.5).")
	casesRoot := fs.String("cases", DefaultCases(), "cases root directory")
	vocabPath := fs.String("vocab", DefaultVocab(), "tag vocabulary file")
	if err := fs.Parse(args); err != nil {
		return 2
	}

	contracts, err := loadAnswerContracts(*vocabPath)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}

	paths, err := caseFilePaths(*casesRoot)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}

	type entry struct {
		id       string
		scenario string
		ngrams   map[string]struct{}
		numbers  map[string]struct{}
	}
	var entries []entry
	for _, path := range paths {
		caseObj, err := loadCaseJSON(path)
		if err != nil {
			continue // Python skips unparseable case.json silently
		}
		scenario, ok := tagsOf(caseObj)["scenario"].(string)
		if !ok {
			continue
		}
		turns, _ := caseObj["turns"].([]any)
		var prompts []string
		for _, turn := range turns {
			tm, ok := turn.(map[string]any)
			if !ok {
				continue
			}
			prompt, _ := tm["prompt"].(string)
			prompts = append(prompts, stripContracts(prompt, contracts))
		}
		id, _ := caseObj["id"].(string)
		if id == "" {
			id = filepath.Base(filepath.Dir(path))
		}
		entries = append(entries, entry{
			id:       id,
			scenario: scenario,
			ngrams:   wordNgrams(strings.Join(prompts, " "), 3),
			numbers:  numbersOfCase(caseObj),
		})
	}

	marked := make([]markedPair, 0)
	for i, a := range entries {
		for _, b := range entries[i+1:] {
			if a.scenario != b.scenario {
				continue
			}
			promptJ := jaccardSets(a.ngrams, b.ngrams)
			numbersJ := jaccardSets(a.numbers, b.numbers)
			if promptJ > promptJaccardThreshold || numbersJ > numbersJaccardThreshold {
				marked = append(marked, markedPair{
					CaseA:          a.id,
					CaseB:          b.id,
					PromptJaccard:  lab.PyFloat(lab.RoundHalfEven(promptJ, 4)),
					NumbersJaccard: lab.PyFloat(lab.RoundHalfEven(numbersJ, 4)),
				})
			}
		}
	}

	data, err := lab.EncodeJSON(marked, 2)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %s\n", err)
		return 2
	}
	fmt.Println(string(data))
	if len(marked) > 0 {
		fmt.Fprintf(os.Stderr, "WARNING: %d pair(s) flagged as near-duplicates; needs human confirmation\n", len(marked))
	} else {
		fmt.Fprintln(os.Stderr, "no near-duplicate pairs flagged")
	}
	return 0
}

// caseFilePaths lists case.json paths sorted by full path, matching Python's
// sorted(Path(root).rglob("case.json")).
func caseFilePaths(root string) ([]string, error) {
	dirs, err := findCaseFiles(root)
	if err != nil {
		return nil, err
	}
	paths := make([]string, 0, len(dirs))
	for _, dir := range dirs {
		paths = append(paths, filepath.Join(dir, "case.json"))
	}
	sort.Strings(paths)
	return paths, nil
}

// loadAnswerContracts returns the answer-contract strings in file order.
// stripContracts truncates at the last occurrence of each in turn, so the
// order changes the result when a prompt ends with more than one of them.
func loadAnswerContracts(vocabPath string) ([]string, error) {
	raw, err := os.ReadFile(vocabPath)
	if err != nil {
		return nil, err
	}
	obj, err := lab.DecodeJSONBytes(raw)
	if err != nil {
		return nil, err
	}
	m, _ := obj.(map[string]any)
	contracts, _ := m["answer_contracts"].(map[string]any)
	keys, err := lab.OrderedObjectKeys(raw, "answer_contracts")
	if err != nil {
		return nil, err
	}
	out := make([]string, 0, len(keys))
	for _, key := range keys {
		if s, ok := contracts[key].(string); ok {
			out = append(out, s)
		}
	}
	return out, nil
}

// stripContracts removes a trailing answer contract: the global contract is
// boilerplate and would otherwise dominate the prompt similarity.
func stripContracts(text string, contracts []string) string {
	for _, contract := range contracts {
		if idx := strings.LastIndex(text, contract); idx != -1 {
			text = text[:idx]
		}
	}
	return strings.TrimSpace(text)
}

func wordNgrams(text string, n int) map[string]struct{} {
	words := dedupWordRe.FindAllString(strings.ToLower(text), -1)
	out := map[string]struct{}{}
	for i := 0; i+n <= len(words); i++ {
		out[strings.Join(words[i:i+n], " ")] = struct{}{}
	}
	return out
}

// numbersOfCase is every number appearing in the case's fixture files. Python
// stores these in a set of floats, so "1" and "1.0" are one element and -0
// equals 0; the keys are the float values in canonical form so the Go set
// collapses them the same way.
func numbersOfCase(caseObj map[string]any) map[string]struct{} {
	out := map[string]struct{}{}
	files, _ := caseObj["files"].(map[string]any)
	for _, content := range files {
		s, ok := content.(string)
		if !ok {
			continue
		}
		for _, raw := range dedupNumberRe.FindAllString(s, -1) {
			f, err := strconv.ParseFloat(strings.ReplaceAll(raw, ",", ""), 64)
			if err != nil {
				continue
			}
			if f == 0 {
				f = 0 // -0.0 and 0.0 are the same set element in Python
			}
			out[strconv.FormatFloat(f, 'g', -1, 64)] = struct{}{}
		}
	}
	return out
}

func jaccardSets(a, b map[string]struct{}) float64 {
	union := len(a) + len(b)
	if union == 0 {
		return 0
	}
	inter := 0
	for k := range a {
		if _, ok := b[k]; ok {
			inter++
		}
	}
	return float64(inter) / float64(union-inter)
}
