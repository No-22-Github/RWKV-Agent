// Package similarity ports scripts/corpus/similarity.py: the model-visible
// text features and overlap scores shared by the decontamination gate
// (corpus decontam) and the bank's near-duplicate marker (bank dedup).
//
// A case reduces to three feature sets — prompt word shingles, fixture line
// shingles, and the distinctive names appearing in either — compared by
// Jaccard (prompt, names) or containment of the candidate in the test case
// (files). Shingle identity is the ordered tuple of its parts; Go has no
// tuple, so the parts are joined with NUL, which the source alphabets cannot
// contain.
package similarity

import (
	"regexp"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Kinds are the three feature sets, in the order the originals iterate them.
var Kinds = []string{"prompt", "files", "names"}

var (
	wordRe = regexp.MustCompile(`[a-z0-9]+`)
	nameRe = regexp.MustCompile(`\b[A-Za-z][A-Za-z0-9]*(?:[-_.][A-Za-z0-9]+)+\b`)
)

// commonNames are too common across any workspace task to count as a shared
// identity.
var commonNames = map[string]struct{}{
	"readme.md": {}, "e.g": {}, "i.e": {},
}

// Features is one case reduced to the three sets.
type Features struct {
	Prompt map[string]struct{}
	Files  map[string]struct{}
	Names  map[string]struct{}
}

// PromptOf joins every turn's prompt with a newline.
func PromptOf(caseObj map[string]any) string {
	turns, _ := caseObj["turns"].([]any)
	parts := make([]string, 0, len(turns))
	for _, turn := range turns {
		tm, _ := turn.(map[string]any)
		if tm == nil {
			continue
		}
		s, _ := tm["prompt"].(string)
		parts = append(parts, s)
	}
	return strings.Join(parts, "\n")
}

// WordShingles is the set of word size-grams over the lowercased text.
func WordShingles(text string, size int) map[string]struct{} {
	words := wordRe.FindAllString(strings.ToLower(text), -1)
	out := map[string]struct{}{}
	for i := 0; i+size <= len(words); i++ {
		out[strings.Join(words[i:i+size], "\x00")] = struct{}{}
	}
	return out
}

// LineShingles is the set of non-empty line size-grams across every fixture
// file. A file with fewer lines than the window contributes its whole line
// list as one shingle, so short fixtures still compare.
func LineShingles(files map[string]any, size int) map[string]struct{} {
	out := map[string]struct{}{}
	for _, content := range files {
		var lines []string
		for _, line := range lab.SplitLines(contentString(content)) {
			if trimmed := strings.TrimSpace(line); trimmed != "" {
				lines = append(lines, trimmed)
			}
		}
		for i := 0; i+size <= len(lines); i++ {
			out[strings.Join(lines[i:i+size], "\x00")] = struct{}{}
		}
		if len(lines) > 0 && len(lines) < size {
			out[strings.Join(lines, "\x00")] = struct{}{}
		}
	}
	return out
}

// Names is the set of hyphenated or dotted identifiers across the prompt and
// the fixture files, lowercased, minus the ones too common to mean anything.
func Names(caseObj map[string]any) map[string]struct{} {
	files := filesOf(caseObj)
	var contents []string
	var names []string
	for name, content := range files {
		contents = append(contents, contentString(content))
		names = append(names, name)
	}
	text := PromptOf(caseObj) + "\n" + strings.Join(contents, "\n") + "\n" + strings.Join(names, "\n")
	out := map[string]struct{}{}
	for _, name := range nameRe.FindAllString(text, -1) {
		lowered := strings.ToLower(name)
		if _, common := commonNames[lowered]; common {
			continue
		}
		out[lowered] = struct{}{}
	}
	return out
}

// FeaturesOf reduces a case to its three feature sets.
func FeaturesOf(caseObj map[string]any) Features {
	return Features{
		Prompt: WordShingles(PromptOf(caseObj), 5),
		Files:  LineShingles(filesOf(caseObj), 3),
		Names:  Names(caseObj),
	}
}

// Jaccard is |a n b| / |a u b|, or 0 when either side is empty.
func Jaccard(a, b map[string]struct{}) float64 {
	if len(a) == 0 || len(b) == 0 {
		return 0
	}
	inter := 0
	for k := range a {
		if _, ok := b[k]; ok {
			inter++
		}
	}
	union := len(a) + len(b) - inter
	return float64(inter) / float64(union)
}

// Containment is |part n whole| / |part|, or 0 when part is empty.
func Containment(part, whole map[string]struct{}) float64 {
	if len(part) == 0 {
		return 0
	}
	inter := 0
	for k := range part {
		if _, ok := whole[k]; ok {
			inter++
		}
	}
	return float64(inter) / float64(len(part))
}

// Scores compares a candidate against a test case, per kind.
func Scores(candidate, test Features) map[string]float64 {
	return map[string]float64{
		"prompt": Jaccard(candidate.Prompt, test.Prompt),
		"files":  Containment(candidate.Files, test.Files),
		"names":  Jaccard(candidate.Names, test.Names),
	}
}

// Boilerplate finds the features present in more than share of the population,
// per kind: shared templates should not read as shared tasks.
func Boilerplate(population []Features, share float64) Features {
	limit := share * float64(len(population))
	out := Features{
		Prompt: map[string]struct{}{},
		Files:  map[string]struct{}{},
		Names:  map[string]struct{}{},
	}
	for _, kind := range Kinds {
		counts := map[string]int{}
		for _, item := range population {
			for feature := range pick(item, kind) {
				counts[feature]++
			}
		}
		target := pick(out, kind)
		for feature, count := range counts {
			if float64(count) > limit {
				target[feature] = struct{}{}
			}
		}
	}
	return out
}

// Strip removes the boilerplate features from an item.
func Strip(item, common Features) Features {
	return Features{
		Prompt: difference(item.Prompt, common.Prompt),
		Files:  difference(item.Files, common.Files),
		Names:  difference(item.Names, common.Names),
	}
}

func difference(a, b map[string]struct{}) map[string]struct{} {
	out := map[string]struct{}{}
	for k := range a {
		if _, ok := b[k]; !ok {
			out[k] = struct{}{}
		}
	}
	return out
}

func pick(f Features, kind string) map[string]struct{} {
	switch kind {
	case "prompt":
		return f.Prompt
	case "files":
		return f.Files
	default:
		return f.Names
	}
}

func filesOf(caseObj map[string]any) map[string]any {
	if files, ok := caseObj["files"].(map[string]any); ok {
		return files
	}
	return map[string]any{}
}

func contentString(v any) string {
	if s, ok := v.(string); ok {
		return s
	}
	return ""
}
