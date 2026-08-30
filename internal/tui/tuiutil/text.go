// Package tuiutil holds rendering helpers shared by the Bubble Tea views.
package tuiutil

import (
	"fmt"
	"strings"
	"time"

	"charm.land/lipgloss/v2"
	"github.com/charmbracelet/x/ansi"
)

// WrappedLines soft-wraps value to width and splits it into render lines.
func WrappedLines(value string, width int) []string {
	if value == "" {
		return nil
	}
	rendered := lipgloss.NewStyle().Width(max(width, 1)).Render(value)
	return strings.Split(rendered, "\n")
}

// TailWindow returns the last height lines of lines offset by scroll, keeping
// scroll saturated within the content so over-scrolling parks at the top edge.
// The first visible line is truncated with a leading ellipsis when content
// continues above the window.
func TailWindow(lines []string, height, scroll int) []string {
	if height <= 0 || len(lines) == 0 {
		return nil
	}
	maxScroll := max(0, len(lines)-height)
	scroll = min(max(scroll, 0), maxScroll)
	end := len(lines) - scroll
	start := max(0, end-height)
	result := append([]string(nil), lines[start:end]...)
	if start > 0 && len(result) > 0 {
		result[0] = ansi.Truncate("…"+result[0], lipgloss.Width(result[0]), "…")
	}
	return result
}

// FormatDuration renders an elapsed duration as MM:SS.d.
func FormatDuration(value time.Duration) string {
	if value <= 0 {
		return "00:00.0"
	}
	minutes := int(value.Minutes())
	seconds := value.Seconds() - float64(minutes*60)
	return fmt.Sprintf("%02d:%04.1f", minutes, seconds)
}
