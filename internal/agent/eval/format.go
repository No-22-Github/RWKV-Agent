package eval

import (
	"encoding/json"
	"regexp"
	"strings"
	"unicode"
)

// outputFormats are the values Expectation.OutputFormat accepts.
var outputFormats = map[string]struct{}{"json": {}, "markdown_table": {}, "zh": {}, "en": {}}

var (
	fencedBlock    = regexp.MustCompile("(?s)```[A-Za-z0-9_-]*\n(.*?)```")
	inlineCode     = regexp.MustCompile("`[^`\n]*`")
	tableSeparator = regexp.MustCompile(`^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$`)
)

// checkOutputFormat returns "" when output has the shape format names, or a
// failure message.
func checkOutputFormat(output, format string) string {
	switch format {
	case "json":
		candidate := strings.TrimSpace(output)
		if blocks := fencedBlock.FindAllStringSubmatch(output, -1); len(blocks) == 1 {
			candidate = strings.TrimSpace(blocks[0][1])
		}
		if !json.Valid([]byte(candidate)) {
			return "output_format json: neither the reply nor its one fenced code block is valid JSON"
		}
	case "markdown_table":
		lines := strings.Split(output, "\n")
		for i := 1; i < len(lines); i++ {
			if tableSeparator.MatchString(strings.TrimSpace(lines[i])) && strings.Contains(lines[i-1], "|") {
				return ""
			}
		}
		return "output_format markdown_table: no header row followed by a |---| separator row"
	case "zh", "en":
		prose := inlineCode.ReplaceAllString(fencedBlock.ReplaceAllString(output, ""), "")
		han := 0
		for _, r := range prose {
			if unicode.Is(unicode.Han, r) {
				han++
			}
		}
		// Count Han characters against Latin words: a Chinese reply that keeps
		// file names and terms in English still has far more characters than
		// words, and an English reply quoting one Chinese name stays English.
		words := len(strings.FieldsFunc(prose, func(r rune) bool { return !(r < unicode.MaxASCII && unicode.IsLetter(r)) }))
		if format == "zh" && han < words {
			return "output_format zh: the reply is mostly not Chinese"
		}
		if format == "en" && han >= words {
			return "output_format en: the reply is not in English"
		}
	default:
		return "output_format: unknown format " + format
	}
	return ""
}
