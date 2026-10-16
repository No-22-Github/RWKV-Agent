package continuation

import "hash/fnv"

// Loop-guard thresholds, calibrated on 2026-10-16 against 150 saved runs
// (208 generations that ran into max_tokens, 7,009 that ended on their own):
// a generation counts as looping once fewer than 5% of the 24-character
// windows ending in its last 768 characters are new to the whole output.
// Verbatim loops of any period (a phrase, a sentence, a block of commands)
// fall to ~0 after their first cycle; clean outputs, including long tables,
// file lists and per-item shell commands, stay above 0.3. On that corpus it
// caught 184 of the 208 capped generations (saving ~74% of their tokens) and
// flagged no clean output; the misses are near-copies with a changing counter
// ("- line 451: level=fatal", "- line 452: …") and genuinely long answers.
const (
	loopGuardGram   = 24
	loopGuardWindow = 768
	// loopGuardFreshPermille is the fresh-window share, in permille, below
	// which the guard trips.
	loopGuardFreshPermille = 50
)

// LoopGuard watches one streamed generation for a verbatim repeat loop. Feed
// it the text as it arrives; once it trips the rest of the generation would
// only repeat itself until max_tokens, so callers end it early and report a
// length finish. The zero value is not usable; call NewLoopGuard.
type LoopGuard struct {
	runes   []rune
	seen    map[uint64]struct{}
	fresh   []bool
	next    int
	grams   int
	nFresh  int
	tripped bool
}

func NewLoopGuard() *LoopGuard {
	return &LoopGuard{
		seen:  make(map[uint64]struct{}),
		fresh: make([]bool, loopGuardWindow),
	}
}

// Write adds streamed text and reports whether the generation is looping.
// Once tripped it keeps reporting true.
func (g *LoopGuard) Write(text string) bool {
	if g.tripped {
		return true
	}
	for _, r := range text {
		g.runes = append(g.runes, r)
		if len(g.runes) < loopGuardGram {
			continue
		}
		hash := fnv.New64a()
		var buf [4]byte
		for _, c := range g.runes[len(g.runes)-loopGuardGram:] {
			buf[0], buf[1], buf[2], buf[3] = byte(c), byte(c>>8), byte(c>>16), byte(c>>24)
			_, _ = hash.Write(buf[:])
		}
		key := hash.Sum64()
		_, old := g.seen[key]
		if !old {
			g.seen[key] = struct{}{}
		}
		if g.grams >= loopGuardWindow && g.fresh[g.next] {
			g.nFresh--
		}
		g.fresh[g.next] = !old
		if !old {
			g.nFresh++
		}
		g.next = (g.next + 1) % loopGuardWindow
		g.grams++
		if g.grams >= loopGuardWindow && g.nFresh*1000 < loopGuardWindow*loopGuardFreshPermille {
			g.tripped = true
			return true
		}
	}
	return false
}
