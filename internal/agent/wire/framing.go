package wire

import (
	"regexp"
	"strings"
)

// leadingThinkBlocks matches one or more complete leading think blocks plus
// their surrounding whitespace. Every transcript that withholds or echoes a
// think prefix uses this rule, so a change lands in one place instead of in
// each parser.
var leadingThinkBlocks = regexp.MustCompile(`(?s)\A\s*(?:<think>.*?</think>\s*)+`)

// StripLeadingThinkBlocks removes complete leading think blocks and the
// whitespace around them, returning the rest unchanged. An unterminated block
// is deliberately left in place: the caller decides whether that is an
// unclosed-think error.
func StripLeadingThinkBlocks(text string) string {
	if match := leadingThinkBlocks.FindStringIndex(text); match != nil && match[0] == 0 {
		return strings.TrimSpace(text[match[1]:])
	}
	return text
}

// TrimWithheldOpening drops the lone ">" a gateway may retain when it closes a
// withheld thinking prefix, but only when the remainder opens a tool envelope.
// The "<tool_call" prefix also covers the array form "<tool_calls>".
func TrimWithheldOpening(text string) string {
	if !strings.HasPrefix(text, ">") {
		return text
	}
	remainder := strings.TrimSpace(strings.TrimPrefix(text, ">"))
	if strings.HasPrefix(remainder, "<tool_call") {
		return remainder
	}
	return text
}
