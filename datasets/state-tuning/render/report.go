package main

import (
	"fmt"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

const vocabPath = "third_party/rwkv-mobile/assets/rwkv_vocab_v20230424.txt"

// report prints the token distribution the training config depends on. Context
// length must cover prompt+completion: ChatProcessor DISCARDS a sample longer
// than max_context_length rather than truncating it, so an under-sized context
// silently drops data instead of failing.
func report(records []trainingRecord, mode inference.ThinkingMode) {
	fmt.Printf("rendered %d cases, thinking=%s\n", len(records), mode)

	bySubtype := map[string]int{}
	byAction := map[string]int{}
	for _, record := range records {
		bySubtype[record.Subtype]++
		byAction[record.Action]++
	}
	fmt.Print("  actions: ")
	printCounts(byAction)
	fmt.Print("  subtypes: ")
	printCounts(bySubtype)

	world, err := tokenizer.OpenWorld(vocabPath)
	if err != nil {
		fmt.Printf("  token counts unavailable: %v\n", err)
		return
	}
	totals := make([]int, 0, len(records))
	completions := make([]int, 0, len(records))
	widest := trainingRecord{}
	widestTokens := 0
	for _, record := range records {
		total := world.Count(record.Text)
		totals = append(totals, total)
		completions = append(completions, world.Count(record.Completion))
		if total > widestTokens {
			widestTokens, widest = total, record
		}
	}
	sort.Ints(totals)
	sort.Ints(completions)
	fmt.Printf("  prompt+completion tokens: min=%d p50=%d p95=%d max=%d\n",
		totals[0], pct(totals, 50), pct(totals, 95), totals[len(totals)-1])
	fmt.Printf("  completion tokens:        min=%d p50=%d p95=%d max=%d\n",
		completions[0], pct(completions, 50), pct(completions, 95),
		completions[len(completions)-1])
	fmt.Printf("  longest case: %s (%d tokens)\n", widest.ID, widestTokens)

	// context_length must be a multiple of 16 and cover the longest sample.
	suggested := ((totals[len(totals)-1] + 63) / 16) * 16
	fmt.Printf("  suggested max_context_length: %d (max sample + headroom, multiple of 16)\n",
		suggested)

	if len(records) > 0 {
		sample := records[0]
		fmt.Printf("\n--- sample %s (%s / %s) ---\n", sample.ID, sample.Subtype, sample.Action)
		fmt.Printf("prompt tail: %q\n", tail(sample.Prompt, 72))
		fmt.Printf("completion:  %q\n", head(sample.Completion, 120))
		fmt.Printf("tool order:  %s\n", strings.Join(sample.ToolOrder, ", "))
	}
}

func printCounts(counts map[string]int) {
	keys := make([]string, 0, len(counts))
	for key := range counts {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	parts := make([]string, 0, len(keys))
	for _, key := range keys {
		parts = append(parts, fmt.Sprintf("%s=%d", key, counts[key]))
	}
	fmt.Println(strings.Join(parts, " "))
}

func pct(sorted []int, percentile int) int {
	if len(sorted) == 0 {
		return 0
	}
	index := len(sorted) * percentile / 100
	if index >= len(sorted) {
		index = len(sorted) - 1
	}
	return sorted[index]
}

func tail(value string, runes int) string {
	converted := []rune(value)
	if len(converted) <= runes {
		return value
	}
	return string(converted[len(converted)-runes:])
}

func head(value string, runes int) string {
	converted := []rune(value)
	if len(converted) <= runes {
		return value
	}
	return string(converted[:runes])
}
