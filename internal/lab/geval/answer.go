package geval

import (
	"math"
	"regexp"
	"strconv"
	"strings"
)

// lastBoxed returns the content of the last \boxed{…} (or \fbox{…}) in
// text, braces balanced, or "" when there is none.
func lastBoxed(text string) string {
	idx := -1
	for _, tag := range []string{`\boxed{`, `\fbox{`} {
		if i := strings.LastIndex(text, tag); i > idx {
			idx = i + len(tag)
		}
	}
	if idx < 0 {
		// `\boxed 5` without braces.
		if i := strings.LastIndex(text, `\boxed `); i >= 0 {
			rest := strings.TrimSpace(text[i+len(`\boxed `):])
			if f := strings.FieldsFunc(rest, func(r rune) bool { return r == '$' || r == ' ' || r == '\n' }); len(f) > 0 {
				return f[0]
			}
		}
		return ""
	}
	depth := 1
	for j := idx; j < len(text); j++ {
		switch text[j] {
		case '{':
			depth++
		case '}':
			depth--
			if depth == 0 {
				return strings.TrimSpace(text[idx:j])
			}
		}
	}
	return ""
}

var reNumber = regexp.MustCompile(`-?\d[\d,]*(?:\.\d+)?|-?\.\d+`)

// gsm8kPrediction is the boxed answer reduced to a number, else the last
// number in the answer.
func gsm8kPrediction(answer string) (string, bool) {
	if boxed := lastBoxed(answer); boxed != "" {
		if nums := reNumber.FindAllString(stripLatexText(boxed), -1); len(nums) > 0 {
			return strings.ReplaceAll(nums[len(nums)-1], ",", ""), true
		}
	}
	nums := reNumber.FindAllString(answer, -1)
	if len(nums) == 0 {
		return "", false
	}
	return strings.ReplaceAll(nums[len(nums)-1], ",", ""), false
}

func numbersEqual(a, b string) bool {
	x, err1 := strconv.ParseFloat(strings.ReplaceAll(a, ",", ""), 64)
	y, err2 := strconv.ParseFloat(strings.ReplaceAll(b, ",", ""), 64)
	if err1 != nil || err2 != nil {
		return false
	}
	return math.Abs(x-y) <= 1e-6*math.Max(1, math.Abs(y))
}

var reTextCmd = regexp.MustCompile(`\\(?:text|textbf|mathrm|mbox|textrm)\{([^{}]*)\}`)

func stripLatexText(s string) string {
	return reTextCmd.ReplaceAllString(s, "$1")
}

var (
	reUnits      = regexp.MustCompile(`\\(?:text|mbox|mathrm)\{\s*[a-zA-Z ]+\}$`)
	reSqrtBare   = regexp.MustCompile(`\\sqrt(\w)`)
	reFracBare   = regexp.MustCompile(`\\frac(\d)(\d)`)
	reFracBrace  = regexp.MustCompile(`^\\frac\{(-?[\d.]+)\}\{(-?[\d.]+)\}$`)
	reSlashFrac  = regexp.MustCompile(`^(-?\d+)/(\d+)$`)
	reVarPrefix  = regexp.MustCompile(`^[a-zA-Z]\s*=`)
	reTrailZeros = regexp.MustCompile(`^(-?\d+)\.0+$`)
)

// normalizeMath is Hendrycks' MATH strip_string with a few additions
// (thousands separators, \dfrac, bare variable prefixes, text wrappers).
func normalizeMath(s string) string {
	s = strings.TrimSpace(s)
	s = strings.ReplaceAll(s, "\n", "")
	s = strings.TrimSuffix(s, ".")
	s = strings.ReplaceAll(s, `\!`, "")
	s = strings.ReplaceAll(s, `\\`, `\`)
	s = strings.ReplaceAll(s, "tfrac", "frac")
	s = strings.ReplaceAll(s, "dfrac", "frac")
	s = strings.ReplaceAll(s, `\left`, "")
	s = strings.ReplaceAll(s, `\right`, "")
	s = strings.ReplaceAll(s, `^{\circ}`, "")
	s = strings.ReplaceAll(s, `^\circ`, "")
	s = strings.ReplaceAll(s, `\$`, "")
	s = strings.ReplaceAll(s, "$", "")
	s = reUnits.ReplaceAllString(s, "")
	s = stripLatexText(s)
	s = strings.ReplaceAll(s, `\%`, "")
	s = strings.ReplaceAll(s, "%", "")
	s = strings.ReplaceAll(s, " .", " 0.")
	s = strings.ReplaceAll(s, "{.", "{0.")
	if strings.HasPrefix(s, ".") {
		s = "0" + s
	}
	if loc := reVarPrefix.FindStringIndex(s); loc != nil && len(s) > loc[1] {
		s = s[loc[1]:]
	}
	s = reSqrtBare.ReplaceAllString(s, `\sqrt{$1}`)
	s = strings.ReplaceAll(s, " ", "")
	s = reFracBare.ReplaceAllString(s, `\frac{$1}{$2}`)
	if s == "0.5" {
		s = `\frac{1}{2}`
	}
	if m := reSlashFrac.FindStringSubmatch(s); m != nil {
		s = `\frac{` + m[1] + `}{` + m[2] + `}`
	}
	// Thousands separators in a plain number.
	if strings.Contains(s, ",") && regexp.MustCompile(`^-?\d{1,3}(,\d{3})+(\.\d+)?$`).MatchString(s) {
		s = strings.ReplaceAll(s, ",", "")
	}
	s = reTrailZeros.ReplaceAllString(s, "$1")
	return s
}

// mathValue evaluates plain numbers and simple fractions, for numeric
// equality across spellings (0.25 vs \frac{1}{4}).
func mathValue(s string) (float64, bool) {
	if v, err := strconv.ParseFloat(s, 64); err == nil {
		return v, true
	}
	if m := reFracBrace.FindStringSubmatch(s); m != nil {
		a, err1 := strconv.ParseFloat(m[1], 64)
		b, err2 := strconv.ParseFloat(m[2], 64)
		if err1 == nil && err2 == nil && b != 0 {
			return a / b, true
		}
	}
	return 0, false
}

// mathEqual is the rule-based MATH verdict; scoring asks the judge only
// when this says no.
func mathEqual(pred, gold string) bool {
	if pred == "" {
		return false
	}
	a, b := normalizeMath(pred), normalizeMath(gold)
	if a == b {
		return true
	}
	x, ok1 := mathValue(a)
	y, ok2 := mathValue(b)
	return ok1 && ok2 && math.Abs(x-y) <= 1e-6*math.Max(1, math.Abs(y))
}

var (
	reChoiceAnswer = regexp.MustCompile(`答案(?:是|为|应为|应该是|选)?\s*[:：]?\s*(?:选项)?\s*[（(【\[]?\s*\**\s*([A-D])(?:[^A-Za-z]|$)`)
	reChoiceBoxed  = regexp.MustCompile(`^\(?([A-D])\)?$`)
	reChoiceEN     = regexp.MustCompile(`(?i)answer\s*(?:is)?\s*[:：]?\s*\(?\**([A-D])\b`)
	reChoiceBold   = regexp.MustCompile(`\*\*\s*(?:选项\s*)?([A-D])\s*(?:[.．、:：)）]|\*\*)`)
	reChoiceLone   = regexp.MustCompile(`(?:^|[^A-Za-z])([A-D])(?:[^A-Za-z]|$)`)
)

// choicePrediction extracts the chosen letter: the last "答案：X", a boxed
// letter, an English "answer is X", a bold option ("**C. 商业**"), and
// finally the last standalone A–D in the final line.
func choicePrediction(answer string) string {
	answer = strings.TrimSpace(answer)
	if m := reChoiceAnswer.FindAllStringSubmatch(answer, -1); len(m) > 0 {
		return m[len(m)-1][1]
	}
	if m := reChoiceBoxed.FindStringSubmatch(strings.TrimSpace(lastBoxed(answer))); m != nil {
		return m[1]
	}
	if m := reChoiceEN.FindAllStringSubmatch(answer, -1); len(m) > 0 {
		return strings.ToUpper(m[len(m)-1][1])
	}
	if m := reChoiceBold.FindAllStringSubmatch(answer, -1); len(m) > 0 {
		return m[len(m)-1][1]
	}
	lines := strings.Split(answer, "\n")
	last := strings.TrimSpace(lines[len(lines)-1])
	if m := reChoiceLone.FindAllStringSubmatch(last, -1); len(m) > 0 {
		return m[len(m)-1][1]
	}
	return ""
}
