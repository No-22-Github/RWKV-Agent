package geval

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"unicode"

	"github.com/abadojack/whatlanggo"
)

// IFEval instruction checkers, ported from google-research
// instruction_following_eval (English) and Marco-Bench-MIF's multilingual
// fork of it (Chinese, mode "zh"). Where Python leans on libraries Go does
// not have, the port approximates and says so:
//
//   - langdetect → whatlanggo (script first, then trigrams), mapped to
//     ISO 639-1; Chinese reports "zh-cn" as langdetect does.
//   - nltk punkt sentence counting → a rule splitter on . ! ? (English) and
//     Marco's split_into_sentences terminators 。！？… (Chinese; Marco itself
//     kept punkt, which never splits Chinese text).
//   - nltk.word_tokenize (capital word frequency) → a regex word tokenizer.
//   - Python's Unicode \b → an explicit word-character boundary check.
//   - Chinese quotation: Marco's list misses “…”, which is the natural
//     reading of 用双引号括起来, so mode zh also accepts it.

// IFEvalResult is one item's verdict under both IFEval variants.
type IFEvalResult struct {
	Strict []bool `json:"strict"`
	Loose  []bool `json:"loose"`
}

func scoreIFEval(item Item, response string) (IFEvalResult, error) {
	mode := "en"
	if item.Task == TaskIFEvalZH {
		mode = "zh"
	}
	res := IFEvalResult{}
	variants := looseVariants(response)
	for i, id := range item.Instructions {
		check, err := ifevalChecker(id, item.Kwargs[i], mode)
		if err != nil {
			return res, fmt.Errorf("%s: %w", item.ID, err)
		}
		res.Strict = append(res.Strict, strings.TrimSpace(response) != "" && check(response))
		ok := false
		for _, v := range variants {
			if strings.TrimSpace(v) != "" && check(v) {
				ok = true
				break
			}
		}
		res.Loose = append(res.Loose, ok)
	}
	return res, nil
}

// looseVariants are IFEval's loose responses: without the first and/or last
// line, and each of those with asterisks removed.
func looseVariants(response string) []string {
	lines := strings.Split(response, "\n")
	first := strings.TrimSpace(strings.Join(lines[min(1, len(lines)):], "\n"))
	last := strings.TrimSpace(strings.Join(lines[:max(len(lines)-1, 0)], "\n"))
	both := ""
	if len(lines) > 2 {
		both = strings.TrimSpace(strings.Join(lines[1:len(lines)-1], "\n"))
	}
	base := []string{response, first, last, both}
	out := append([]string(nil), base...)
	for _, b := range base {
		out = append(out, strings.ReplaceAll(b, "*", ""))
	}
	return out
}

type checker func(string) bool

func kwString(kw map[string]any, key string) string {
	switch v := kw[key].(type) {
	case string:
		return v
	case json.Number:
		return v.String()
	case nil:
		return ""
	default:
		return fmt.Sprint(v)
	}
}

func kwInt(kw map[string]any, key string) (int, error) {
	s := kwString(kw, key)
	n, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("kwarg %s=%q is not an integer", key, s)
	}
	return n, nil
}

func kwStrings(kw map[string]any, key string) []string {
	var out []string
	if list, ok := kw[key].([]any); ok {
		for _, v := range list {
			out = append(out, fmt.Sprint(v))
		}
	}
	return out
}

// compare applies IFEval's relation: "less than" or "at least".
func compare(relation string, n, threshold int) bool {
	if relation == "less than" {
		return n < threshold
	}
	return n >= threshold
}

func ifevalChecker(id string, kw map[string]any, mode string) (checker, error) {
	intArg := func(key string) int {
		n, _ := kwInt(kw, key)
		return n
	}
	for _, key := range requiredInts[id] {
		if _, err := kwInt(kw, key); err != nil {
			return nil, fmt.Errorf("%s: %w", id, err)
		}
	}
	switch id {
	case "language:response_language":
		want := kwString(kw, "language")
		return func(v string) bool {
			got := detectLanguage(v)
			return got == "" || got == want
		}, nil
	case "length_constraints:number_sentences":
		rel, n := kwString(kw, "relation"), intArg("num_sentences")
		return func(v string) bool { return compare(rel, countSentences(v, mode), n) }, nil
	case "detectable_content:number_placeholders":
		n := intArg("num_placeholders")
		return func(v string) bool { return len(rePlaceholder.FindAllString(v, -1)) >= n }, nil
	case "detectable_format:number_bullet_lists":
		n := intArg("num_bullets")
		return func(v string) bool {
			return len(reBulletStar.FindAllString(v, -1))+len(reBulletDash.FindAllString(v, -1)) == n
		}, nil
	case "detectable_format:constrained_response":
		options := constrainedEN
		if mode == "zh" {
			options = constrainedMulti
		}
		return func(v string) bool {
			v = strings.TrimSpace(v)
			for _, o := range options {
				if strings.Contains(v, o) {
					return true
				}
			}
			return false
		}, nil
	case "detectable_format:number_highlighted_sections":
		n := intArg("num_highlights")
		return func(v string) bool { return countHighlights(v) >= n }, nil
	case "detectable_format:multiple_sections":
		splitter, n := kwString(kw, "section_spliter"), intArg("num_sections")
		return func(v string) bool { return countSections(v, splitter, mode) >= n }, nil
	case "length_constraints:number_paragraphs":
		n := intArg("num_paragraphs")
		return func(v string) bool { return starParagraphs(v) == n }, nil
	case "detectable_content:postscript":
		marker := kwString(kw, "postscript_marker")
		return func(v string) bool { return hasPostscript(v, marker) }, nil
	case "keywords:existence":
		keywords := kwStrings(kw, "keywords")
		return func(v string) bool {
			for _, k := range keywords {
				if !keywordRegexp(k).MatchString(v) {
					return false
				}
			}
			return true
		}, nil
	case "keywords:frequency":
		re, rel, n := keywordRegexp(kwString(kw, "keyword")), kwString(kw, "relation"), intArg("frequency")
		return func(v string) bool { return compare(rel, len(re.FindAllString(v, -1)), n) }, nil
	case "length_constraints:number_words":
		rel, n := kwString(kw, "relation"), intArg("num_words")
		return func(v string) bool { return compare(rel, countWords(v, mode), n) }, nil
	case "detectable_format:json_format":
		return isJSONResponse, nil
	case "length_constraints:nth_paragraph_first_word":
		n, nth, word := intArg("num_paragraphs"), intArg("nth_paragraph"), kwString(kw, "first_word")
		return func(v string) bool { return nthParagraphFirstWord(v, n, nth, word, mode) }, nil
	case "keywords:forbidden_words":
		words := kwStrings(kw, "forbidden_words")
		return func(v string) bool {
			for _, w := range words {
				if containsWord(v, w) {
					return false
				}
			}
			return true
		}, nil
	case "combination:two_responses":
		return twoResponses, nil
	case "combination:repeat_prompt":
		prompt := strings.ToLower(strings.TrimSpace(kwString(kw, "prompt_to_repeat")))
		return func(v string) bool { return strings.HasPrefix(strings.ToLower(strings.TrimSpace(v)), prompt) }, nil
	case "startend:end_checker":
		end := strings.ToLower(strings.TrimSpace(kwString(kw, "end_phrase")))
		return func(v string) bool {
			return strings.HasSuffix(strings.ToLower(strings.Trim(strings.TrimSpace(v), `"`)), end)
		}, nil
	case "detectable_format:title":
		return func(v string) bool {
			for _, t := range reTitle.FindAllString(v, -1) {
				if strings.TrimSpace(strings.TrimRight(strings.TrimLeft(t, "<"), ">")) != "" {
					return true
				}
			}
			return false
		}, nil
	case "keywords:letter_frequency":
		letter := strings.ToLower(strings.TrimSpace(kwString(kw, "letter")))
		rel, n := kwString(kw, "let_relation"), intArg("let_frequency")
		return func(v string) bool { return compare(rel, strings.Count(strings.ToLower(v), letter), n) }, nil
	case "change_case:english_capital":
		return func(v string) bool { return pyIsUpper(v) && detectLanguageOr(v, "en") == "en" }, nil
	case "change_case:english_lowercase":
		return func(v string) bool { return pyIsLower(v) && detectLanguageOr(v, "en") == "en" }, nil
	case "punctuation:no_comma":
		commas := ","
		if mode == "zh" {
			commas = ",，،"
		}
		return func(v string) bool { return !strings.ContainsAny(v, commas) }, nil
	case "change_case:capital_word_frequency":
		rel, n := kwString(kw, "capital_relation"), intArg("capital_frequency")
		return func(v string) bool {
			count := 0
			for _, w := range reWordToken.FindAllString(v, -1) {
				if pyIsUpper(w) {
					count++
				}
			}
			return compare(rel, count, n)
		}, nil
	case "startend:quotation":
		return func(v string) bool { return quoted(v, mode) }, nil
	}
	return nil, fmt.Errorf("unknown instruction %q", id)
}

var requiredInts = map[string][]string{
	"length_constraints:number_sentences":           {"num_sentences"},
	"detectable_content:number_placeholders":        {"num_placeholders"},
	"detectable_format:number_bullet_lists":         {"num_bullets"},
	"detectable_format:number_highlighted_sections": {"num_highlights"},
	"detectable_format:multiple_sections":           {"num_sections"},
	"length_constraints:number_paragraphs":          {"num_paragraphs"},
	"keywords:frequency":                            {"frequency"},
	"length_constraints:number_words":               {"num_words"},
	"length_constraints:nth_paragraph_first_word":   {"num_paragraphs", "nth_paragraph"},
	"keywords:letter_frequency":                     {"let_frequency"},
	"change_case:capital_word_frequency":            {"capital_frequency"},
}

var (
	rePlaceholder = regexp.MustCompile(`\[.*?\]`)
	reBulletStar  = regexp.MustCompile(`(?m)^\s*\*[^\*].*$`)
	reBulletDash  = regexp.MustCompile(`(?m)^\s*-.*$`)
	reHighlight   = regexp.MustCompile(`\*[^\n\*]*\*`)
	reHighlight2  = regexp.MustCompile(`\*\*[^\n\*]*\*\*`)
	reStarSplit   = regexp.MustCompile(`\s?\*\*\*\s?`)
	reTitle       = regexp.MustCompile(`<<[^\n]+>>`)
	reWords       = regexp.MustCompile(`[\p{L}\p{N}\p{Mn}\p{Mc}_]+`)
	reWordToken   = regexp.MustCompile(`[\p{L}\p{N}]+(?:['’.\-][\p{L}\p{N}]+)*`)
	reCJKChars    = regexp.MustCompile(`[\p{Han}\p{Hiragana}\p{Katakana}\p{Hangul}\p{Arabic}\p{Hebrew}\p{Thai}\p{Bengali}\p{Devanagari}]`)
)

var constrainedEN = []string{"My answer is yes.", "My answer is no.", "My answer is maybe."}

// constrainedMulti is Marco-Bench-MIF's extended list (the Chinese and
// English entries; the rest are other languages and harmless).
var constrainedMulti = append(append([]string(nil), constrainedEN...),
	"我的答案是肯定的。", "我的答案是否定的。", "我的答案是可能。", "我的答案是也许。",
	"我的答案是\"是的\"。", "我的答案是\"不是\"", "我的答案是\"不好说\"。")

func countHighlights(v string) int {
	n := 0
	for _, h := range reHighlight.FindAllString(v, -1) {
		if strings.TrimSpace(strings.Trim(h, "*")) != "" {
			n++
		}
	}
	for _, h := range reHighlight2.FindAllString(v, -1) {
		if strings.TrimSpace(strings.TrimSuffix(strings.TrimPrefix(h, "**"), "**")) != "" {
			n++
		}
	}
	return n
}

// countSections counts section headers. English follows the original
// (`\s?SPLITTER\s?\d+\s?`); Chinese follows Marco (`\bSPLITTER\s+(\d+|roman)\b`).
func countSections(v, splitter, mode string) int {
	if mode != "zh" {
		re, err := regexp.Compile(`\s?` + splitter + `\s?\d+\s?`)
		if err != nil {
			re = regexp.MustCompile(`\s?` + regexp.QuoteMeta(splitter) + `\s?\d+\s?`)
		}
		return len(re.FindAllStringIndex(v, -1))
	}
	re := regexp.MustCompile(regexp.QuoteMeta(splitter) + `\s+(?:\d+|[IVX]+)`)
	n := 0
	for _, loc := range re.FindAllStringIndex(v, -1) {
		if isBoundary(v, loc[0]) && isBoundary(v, loc[1]) {
			n++
		}
	}
	return n
}

func starParagraphs(v string) int {
	parts := reStarSplit.Split(v, -1)
	n := len(parts)
	for i, p := range parts {
		if strings.TrimSpace(p) == "" {
			if i == 0 || i == len(parts)-1 {
				n--
			} else {
				return -1
			}
		}
	}
	return n
}

func hasPostscript(v, marker string) bool {
	v = strings.ToLower(v)
	var pattern string
	switch marker {
	case "P.P.S":
		pattern = `\s*p\.\s?p\.\s?s.*$`
	case "P.S.":
		pattern = `\s*p\.\s?s\..*$`
	default:
		pattern = `\s*` + strings.ToLower(marker) + `.*$`
	}
	re, err := regexp.Compile(`(?m)` + pattern)
	if err != nil {
		re = regexp.MustCompile(`(?m)\s*` + regexp.QuoteMeta(strings.ToLower(marker)) + `.*$`)
	}
	return re.MatchString(v)
}

// keywordRegexp compiles a keyword the way IFEval does (as a regex,
// ignoring case), falling back to a literal when it is not valid RE2.
func keywordRegexp(k string) *regexp.Regexp {
	re, err := regexp.Compile(`(?i)` + k)
	if err != nil {
		re = regexp.MustCompile(`(?i)` + regexp.QuoteMeta(k))
	}
	return re
}

func isJSONResponse(v string) bool {
	v = strings.TrimSpace(v)
	for _, p := range []string{"```json", "```Json", "```JSON", "```"} {
		if strings.HasPrefix(v, p) {
			v = v[len(p):]
			break
		}
	}
	v = strings.TrimSpace(strings.TrimSuffix(v, "```"))
	return json.Valid([]byte(v))
}

var zhParagraphPunct = ".,?!:;'\"-—()[]{}、。，；：“”‘’《》（）【】؟،؛׳״ๆฯ๏「」『』〜¿¡«»„‟·…"

func nthParagraphFirstWord(v string, num, nth int, word, mode string) bool {
	parts := strings.Split(v, "\n\n")
	count := len(parts)
	for _, p := range parts {
		if strings.TrimSpace(p) == "" {
			count--
		}
	}
	if nth > count || nth < 1 {
		return false
	}
	paragraph := strings.TrimSpace(parts[nth-1])
	if paragraph == "" {
		return false
	}
	if mode == "zh" {
		cleaned := strings.Trim(paragraph, zhParagraphPunct)
		return count == num && strings.HasPrefix(strings.ToLower(cleaned), strings.ToLower(word))
	}
	first := strings.Fields(paragraph)[0]
	first = strings.TrimLeft(strings.TrimLeft(first, "'"), `"`)
	var b strings.Builder
	for _, r := range first {
		if strings.ContainsRune(".,?!'\"", r) {
			break
		}
		b.WriteString(strings.ToLower(string(r)))
	}
	return count == num && b.String() == strings.ToLower(word)
}

func twoResponses(v string) bool {
	parts := strings.Split(v, "******")
	var valid []string
	for i, p := range parts {
		if strings.TrimSpace(p) == "" {
			if i != 0 && i != len(parts)-1 {
				return false
			}
			continue
		}
		valid = append(valid, p)
	}
	return len(valid) == 2 && strings.TrimSpace(valid[0]) != strings.TrimSpace(valid[1])
}

func quoted(v, mode string) bool {
	r := []rune(strings.TrimSpace(v))
	if len(r) <= 1 {
		return false
	}
	first, last := r[0], r[len(r)-1]
	if first == '"' && last == '"' {
		return true
	}
	if mode != "zh" {
		return false
	}
	for _, pair := range [][2]rune{{'„', '"'}, {'«', '»'}, {'»', '«'}, {'“', '”'}} {
		if first == pair[0] && last == pair[1] {
			return true
		}
	}
	return false
}

func isWordRune(r rune) bool {
	return r == '_' || unicode.IsLetter(r) || unicode.IsDigit(r) || unicode.Is(unicode.Mn, r)
}

// isBoundary is Python's Unicode \b at byte offset i.
func isBoundary(s string, i int) bool {
	before, after := false, false
	if i > 0 {
		r := []rune(s[:i])
		before = isWordRune(r[len(r)-1])
	}
	if i < len(s) {
		for _, r := range s[i:] {
			after = isWordRune(r)
			break
		}
	}
	return before != after
}

// containsWord is re.search(r"\b" + word + r"\b", v, re.IGNORECASE).
func containsWord(v, word string) bool {
	if word == "" {
		return false
	}
	re := regexp.MustCompile(`(?i)` + regexp.QuoteMeta(word))
	for _, loc := range re.FindAllStringIndex(v, -1) {
		if isBoundary(v, loc[0]) && isBoundary(v, loc[1]) {
			return true
		}
	}
	return false
}

func countWords(v, mode string) int {
	if mode == "zh" {
		n := len(reCJKChars.FindAllString(v, -1))
		return n + len(reWords.FindAllString(reCJKChars.ReplaceAllString(v, " "), -1))
	}
	return len(reWords.FindAllString(v, -1))
}

var (
	reSentenceEN = regexp.MustCompile(`[.!?]+["')\]]*(\s+|$)`)
	reSentenceZH = regexp.MustCompile(`(?:[.;?!。？！]|……|…|〜)`)
	abbreviation = regexp.MustCompile(`(?i)(?:^|\s)(?:mr|mrs|ms|dr|prof|sr|jr|st|vs|etc|e\.g|i\.e|inc|ltd|co|no|u\.s|a\.m|p\.m)\.$`)
)

func countSentences(v, mode string) int {
	if mode == "zh" {
		n := 0
		for _, s := range reSentenceZH.Split(strings.ReplaceAll(v, "\n", " "), -1) {
			if strings.TrimSpace(s) != "" {
				n++
			}
		}
		return n
	}
	n, start := 0, 0
	for _, loc := range reSentenceEN.FindAllStringIndex(v, -1) {
		chunk := v[start:loc[1]]
		if abbreviation.MatchString(strings.TrimRight(chunk, " \t\n\"')]")) && loc[1] < len(v) {
			continue
		}
		if strings.TrimSpace(chunk) != "" {
			n++
		}
		start = loc[1]
	}
	if strings.TrimSpace(v[start:]) != "" {
		n++
	}
	return n
}

// pyIsUpper is str.isupper(): at least one cased rune, none lower case.
func pyIsUpper(s string) bool {
	cased := false
	for _, r := range s {
		if unicode.IsLower(r) {
			return false
		}
		if unicode.IsUpper(r) || unicode.IsTitle(r) {
			cased = true
		}
	}
	return cased
}

// pyIsLower is str.islower().
func pyIsLower(s string) bool {
	cased := false
	for _, r := range s {
		if unicode.IsUpper(r) || unicode.IsTitle(r) {
			return false
		}
		if unicode.IsLower(r) {
			cased = true
		}
	}
	return cased
}

// detectLanguage returns an ISO 639-1 code as langdetect would ("zh-cn"
// for Chinese), or "" when the text has no letters to judge.
func detectLanguage(v string) string {
	letters := 0
	for _, r := range v {
		if unicode.IsLetter(r) {
			letters++
		}
	}
	if letters == 0 {
		return ""
	}
	info := whatlanggo.Detect(v)
	code := info.Lang.Iso6391()
	switch {
	case code == "zh" || info.Lang == whatlanggo.Cmn:
		return "zh-cn"
	case code == "":
		return ""
	}
	return code
}

// detectLanguageOr is detectLanguage with IFEval's exception path: an
// undetectable text passes as the wanted language.
func detectLanguageOr(v, want string) string {
	if got := detectLanguage(v); got != "" {
		return got
	}
	return want
}
