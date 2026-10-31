package geval

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"hash/fnv"
	"os"
	"sort"
	"strings"
	"unicode"
)

// Decontamination: token 13-grams of each item's source text (Raw, without
// our instructions) looked up in every training row. Tokens are lower-cased
// letter/digit runs, and each CJK character on its own, so Chinese and
// English are measured on the same footing. An item shorter than 13 tokens
// contributes its whole token run as one n-gram.
//
// One shared 13-gram is common (IFEval constraint templates, stock MCQ
// phrasing), so the verdict is coverage: the share of an item's n-grams seen
// in training. Flagged means coverage ≥ the threshold (default 0.5).

const ngramSize = 13

func ngramTokens(text string) []string {
	var tokens []string
	var word []rune
	flush := func() {
		if len(word) > 0 {
			tokens = append(tokens, string(word))
			word = word[:0]
		}
	}
	for _, r := range strings.ToLower(text) {
		switch {
		case isCJK(r):
			flush()
			tokens = append(tokens, string(r))
		case unicode.IsLetter(r) || unicode.IsDigit(r):
			word = append(word, r)
		default:
			flush()
		}
	}
	flush()
	return tokens
}

func isCJK(r rune) bool {
	return unicode.Is(unicode.Han, r) || unicode.Is(unicode.Hiragana, r) || unicode.Is(unicode.Katakana, r) || unicode.Is(unicode.Hangul, r)
}

func hashTokens(tokens []string) uint64 {
	h := fnv.New64a()
	for _, t := range tokens {
		h.Write([]byte(t))
		h.Write([]byte{0})
	}
	return h.Sum64()
}

func itemNGrams(text string) []uint64 {
	tokens := ngramTokens(text)
	if len(tokens) == 0 {
		return nil
	}
	if len(tokens) < ngramSize {
		return []uint64{hashTokens(tokens)}
	}
	seen := map[uint64]bool{}
	var out []uint64
	for i := 0; i+ngramSize <= len(tokens); i++ {
		h := hashTokens(tokens[i : i+ngramSize])
		if !seen[h] {
			seen[h] = true
			out = append(out, h)
		}
	}
	return out
}

func runDecontam(args []string) int {
	flags := flag.NewFlagSet("rwkv-lab geval decontam", flag.ContinueOnError)
	itemsPath := flags.String("items", DefaultItemsPath(), "items file; rewritten with each item's contam field")
	train := flags.String("train", "", "training rows (JSON Lines with a text field); repeatable via commas")
	field := flags.String("field", "text", "row field holding the training text")
	threshold := flags.Float64("threshold", 0.5, "coverage at or above which an item is flagged")
	if err := flags.Parse(args); err != nil {
		return 2
	}
	if *train == "" {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval decontam: --train is required")
		return 2
	}
	items, _, err := loadItems(*itemsPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval decontam:", err)
		return 1
	}
	grams := make([][]uint64, len(items))
	// For every eval n-gram, the training rows it was seen in (first few).
	seenIn := map[uint64][]int32{}
	short := map[int]bool{}
	for i, item := range items {
		grams[i] = itemNGrams(item.Raw)
		for _, g := range grams[i] {
			seenIn[g] = nil
		}
		if n := len(ngramTokens(item.Raw)); n > 0 && n < ngramSize {
			short[n] = true
		}
	}
	var shortLens []int
	for n := range short {
		shortLens = append(shortLens, n)
	}
	sort.Ints(shortLens)
	rows := 0
	for _, path := range strings.Split(*train, ",") {
		n, err := scanTraining(path, *field, seenIn, shortLens, &rows)
		if err != nil {
			fmt.Fprintln(os.Stderr, "rwkv-lab geval decontam:", err)
			return 1
		}
		fmt.Fprintf(os.Stderr, "%s: %d rows\n", path, n)
	}
	for i := range items {
		items[i].Contam = contamFor(grams[i], seenIn, *threshold)
	}
	if err := writeItems(*itemsPath, items); err != nil {
		fmt.Fprintln(os.Stderr, "rwkv-lab geval decontam:", err)
		return 1
	}
	printContamTable(items)
	return 0
}

const rowsPerGram = 8

// scanTraining records, for every eval n-gram, the first rows holding it.
// shortLens are the token lengths of items shorter than one n-gram, whose
// whole run is looked up at that length.
func scanTraining(path, field string, seenIn map[uint64][]int32, shortLens []int, rows *int) (int, error) {
	fh, err := os.Open(path)
	if err != nil {
		return 0, err
	}
	defer fh.Close()
	scanner := bufio.NewScanner(fh)
	scanner.Buffer(make([]byte, 1<<20), 512<<20)
	n := 0
	for scanner.Scan() {
		var row map[string]json.RawMessage
		if err := json.Unmarshal(scanner.Bytes(), &row); err != nil {
			return n, fmt.Errorf("%s:%d: %w", path, n+1, err)
		}
		var text string
		if err := json.Unmarshal(row[field], &text); err != nil {
			return n, fmt.Errorf("%s:%d: field %q: %w", path, n+1, field, err)
		}
		id := int32(*rows)
		*rows++
		n++
		tokens := ngramTokens(text)
		mark := func(h uint64) {
			if list, ok := seenIn[h]; ok && len(list) < rowsPerGram && (len(list) == 0 || list[len(list)-1] != id) {
				seenIn[h] = append(list, id)
			}
		}
		for _, k := range append(shortLens, ngramSize) {
			for i := 0; i+k <= len(tokens); i++ {
				mark(hashTokens(tokens[i : i+k]))
			}
		}
	}
	return n, scanner.Err()
}

func contamFor(grams []uint64, seenIn map[uint64][]int32, threshold float64) *Contam {
	c := &Contam{NGrams: len(grams), BestRow: -1}
	rowHits := map[int32]int{}
	for _, g := range grams {
		if list := seenIn[g]; len(list) > 0 {
			c.Hits++
			for _, r := range list {
				rowHits[r]++
			}
		}
	}
	for r, n := range rowHits {
		if n > c.BestHits || (n == c.BestHits && int(r) < c.BestRow) {
			c.BestRow, c.BestHits = int(r), n
		}
	}
	if c.NGrams > 0 {
		c.Coverage = float64(c.Hits) / float64(c.NGrams)
	}
	c.Coverage = float64(int(c.Coverage*1000+0.5)) / 1000
	c.Flagged = c.NGrams > 0 && c.Coverage >= threshold
	return c
}

func printContamTable(items []Item) {
	type agg struct{ n, any, c20, c50, c80, flagged int }
	by := map[string]*agg{}
	for _, item := range items {
		a := by[item.Task]
		if a == nil {
			a = &agg{}
			by[item.Task] = a
		}
		a.n++
		c := item.Contam
		if c == nil {
			continue
		}
		if c.Hits > 0 {
			a.any++
		}
		if c.Coverage >= 0.2 {
			a.c20++
		}
		if c.Coverage >= 0.5 {
			a.c50++
		}
		if c.Coverage >= 0.8 {
			a.c80++
		}
		if c.Flagged {
			a.flagged++
		}
	}
	fmt.Println("| task | items | any 13-gram hit | coverage ≥0.2 | ≥0.5 | ≥0.8 | flagged |")
	fmt.Println("|---|---:|---:|---:|---:|---:|---:|")
	for _, t := range taskOrder {
		a := by[t]
		if a == nil {
			continue
		}
		fmt.Printf("| %s | %d | %d | %d | %d | %d | %d |\n", t, a.n, a.any, a.c20, a.c50, a.c80, a.flagged)
	}
}
