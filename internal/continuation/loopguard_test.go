package continuation

import (
	"fmt"
	"strings"
	"testing"
)

// feed streams text in small deltas, the way a server does, and returns the
// rune offset at which the guard tripped (-1 if it never did).
func feed(guard *LoopGuard, text string) int {
	runes := []rune(text)
	for start := 0; start < len(runes); start += 3 {
		end := min(start+3, len(runes))
		if guard.Write(string(runes[start:end])) {
			return end
		}
	}
	return -1
}

func TestLoopGuardTripsOnVerbatimLoops(t *testing.T) {
	t.Parallel()
	for name, cycle := range map[string]string{
		"phrase":   "露点温度 计算 公式 ",
		"sentence": "The user wants to know the first step to install a package. ",
		"block": "The tool \"get_current_weather\" is unknown, but we can use \"get_forecast\" " +
			"which returns forecast for a location. The user wants current weather. ",
		"command": "sed 's/^$//' | ",
	} {
		text := "Let me think about this first.\n" + strings.Repeat(cycle, 4000/len([]rune(cycle))+1)
		at := feed(NewLoopGuard(), text)
		if at < 0 {
			t.Errorf("%s: loop never tripped", name)
			continue
		}
		// One clean cycle plus the window is all the guard needs to see.
		if limit := 40 + len([]rune(cycle)) + loopGuardWindow + loopGuardGram; at > limit {
			t.Errorf("%s: tripped at rune %d, want by %d", name, at, limit)
		}
	}
}

func TestLoopGuardLeavesStructuredOutputAlone(t *testing.T) {
	t.Parallel()
	var table, commands, files strings.Builder
	table.WriteString("| SKU | Price | Qty | Value |\n|---|---|---|---|\n")
	for i := range 120 {
		fmt.Fprintf(&table, "| SKU-%04d | £%d.%02d | %d | £%d.%02d |\n", 3000+i*28, 10+i*7%90, i*13%100, 50+i*11%150, 900+i*97, i*31%100)
	}
	for i := range 80 {
		fmt.Fprintf(&commands, "wc -c assets/photos/photo-%02d.png; ", i)
	}
	for i := range 90 {
		fmt.Fprintf(&files, "- lab/press-2026-09%02d-%d.csv\n", 10+i/3, i%3+1)
	}
	for name, text := range map[string]string{
		"table": table.String(), "commands": commands.String(), "files": files.String(),
	} {
		if at := feed(NewLoopGuard(), text); at >= 0 {
			t.Errorf("%s: clean output tripped at rune %d of %d", name, at, len([]rune(text)))
		}
	}
}

func TestLoopGuardNeedsAFullWindow(t *testing.T) {
	t.Parallel()
	guard := NewLoopGuard()
	if guard.Write(strings.Repeat("ab", loopGuardWindow/2)) {
		t.Fatal("tripped before a full window of grams")
	}
	if !guard.Write(strings.Repeat("ab", loopGuardGram)) || !guard.Write("x") {
		t.Fatal("did not trip, or did not stay tripped")
	}
}
