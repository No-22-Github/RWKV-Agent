package terminal

import (
	"strings"
	"unicode"

	"github.com/charmbracelet/x/ansi"
)

func SanitizeModelText(value string) string {
	value = ansi.Strip(value)
	var result strings.Builder
	for _, current := range value {
		switch current {
		case '\n':
			result.WriteRune(current)
		case '\t':
			result.WriteString("    ")
		case '\r':
			// Ignore carriage returns so generated text cannot rewrite output.
		default:
			if !unicode.IsControl(current) {
				result.WriteRune(current)
			}
		}
	}
	return result.String()
}
