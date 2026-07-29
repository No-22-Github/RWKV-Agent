package agent

import (
	"context"
	"errors"
	"fmt"
	"path/filepath"
	"strings"
	"time"

	tea "charm.land/bubbletea/v2"
	"charm.land/lipgloss/v2"
	"github.com/charmbracelet/x/ansi"
	"github.com/no22/RWKV-Agent/internal/terminal"
)

func (m *model) View() tea.View {
	width := max(m.width, 40)
	height := max(m.height, 12)
	bodyHeight := max(height-4, 6)

	header := m.renderHeader(width)
	var body string
	if width >= 88 {
		activityWidth := max(28, width/3)
		conversationWidth := width - activityWidth - 1
		body = lipgloss.JoinHorizontal(
			lipgloss.Top,
			m.renderConversation(conversationWidth, bodyHeight),
			" ",
			m.renderActivity(activityWidth, bodyHeight),
		)
	} else {
		activityHeight := min(7, max(4, bodyHeight/3))
		conversationHeight := bodyHeight - activityHeight
		body = lipgloss.JoinVertical(
			lipgloss.Left,
			m.renderConversation(width, conversationHeight),
			m.renderActivity(width, activityHeight),
		)
	}
	input := " " + m.input.View()
	if m.running {
		input = fmt.Sprintf(
			" %s Working on step %d · %s",
			spinnerFrame(m.elapsed),
			max(m.step, 1),
			formatDuration(m.elapsed),
		)
	}
	footer := " Enter submit · wheel/↑/↓ scroll · Ctrl-C cancel task · Esc quit "
	if !m.running {
		footer = " Enter submit · wheel/↑/↓ scroll · Ctrl-C/Esc quit "
	}
	content := strings.Join([]string{
		header,
		body,
		ansi.Truncate(input, width, ""),
		ansi.Truncate(m.theme.Muted.Render(footer), width, ""),
	}, "\n")
	view := tea.NewView(content)
	view.AltScreen = true
	view.MouseMode = tea.MouseModeCellMotion
	view.WindowTitle = "RWKV read-only agent"
	return view
}

func (m *model) renderHeader(width int) string {
	modelName := strings.TrimSpace(m.meta.Model)
	if modelName == "" {
		modelName = "RWKV"
	}
	provider := strings.ToUpper(strings.TrimSpace(m.meta.Provider))
	if provider == "" {
		provider = "LOCAL"
	}
	left := fmt.Sprintf(" %s · %s · Agent", modelName, provider)
	right := m.theme.Warning.Render("READ ONLY") + " "
	padding := max(1, width-lipgloss.Width(left)-lipgloss.Width(right))
	return ansi.Truncate(left+strings.Repeat(" ", padding)+right, width, "")
}

func (m *model) renderConversation(width, height int) string {
	contentWidth := max(width-2, 1)
	contentHeight := max(height-2, 1)
	lines := m.conversationLines(contentWidth)
	body := tailWindow(lines, contentHeight, m.scroll)
	for len(body) < contentHeight {
		body = append(body, "")
	}
	return m.theme.PaneFocus.
		Width(contentWidth).
		Height(contentHeight).
		Render(strings.Join(body, "\n"))
}

func (m *model) conversationLines(contentWidth int) []string {
	lines := []string{m.theme.Title.Render(" Conversation")}
	for _, item := range m.turns {
		lines = append(lines, "")
		lines = append(lines, wrappedStyledLines(
			m.theme.Prompt.Render("You ›")+" "+terminal.SanitizeModelText(item.prompt),
			contentWidth,
		)...)
		if item.output != "" {
			lines = append(lines, wrappedStyledLines(
				m.theme.Success.Render("Agent ›")+" "+item.output,
				contentWidth,
			)...)
		}
		if item.err != nil {
			label := "Error › "
			if errors.Is(item.err, context.Canceled) {
				label = "Cancelled › "
			}
			lines = append(lines, wrappedStyledLines(
				m.theme.Warning.Render(label)+terminal.SanitizeModelText(item.err.Error()),
				contentWidth,
			)...)
		}
	}
	if m.current != "" {
		lines = append(lines, "")
		lines = append(lines, wrappedStyledLines(
			m.theme.Prompt.Render("You ›")+" "+terminal.SanitizeModelText(m.current),
			contentWidth,
		)...)
		lines = append(lines, m.theme.Muted.Render("Agent › working…"))
	}
	if len(m.turns) == 0 && m.current == "" {
		lines = append(lines, "", m.theme.Muted.Render("Ask a question about the workspace to begin."))
	}
	return lines
}

func (m *model) renderActivity(width, height int) string {
	contentWidth := max(width-2, 1)
	contentHeight := max(height-2, 1)
	lines := []string{m.theme.Title.Render(" Activity")}
	available := max(contentHeight-2, 1)
	start := max(0, len(m.activities)-available)
	for _, item := range m.activities[start:] {
		prefix := "◇ "
		style := m.theme.Muted
		switch item.style {
		case activityAccent:
			style = m.theme.Accent
		case activitySuccess:
			prefix = "✓ "
			style = m.theme.Success
		case activityWarning:
			prefix = "! "
			style = m.theme.Warning
		}
		line := style.Render(prefix) + terminal.SanitizeModelText(item.text)
		lines = append(lines, ansi.Truncate(line, contentWidth, "…"))
	}
	for len(lines) < contentHeight-1 {
		lines = append(lines, "")
	}
	workspace := m.meta.Workspace
	if workspace == "" {
		workspace = "."
	}
	workspace = filepath.Clean(workspace)
	lines = append(lines, ansi.Truncate(
		m.theme.Muted.Render("workspace · ")+workspace,
		contentWidth,
		"…",
	))
	if len(lines) > contentHeight {
		lines = append(lines[:1], lines[len(lines)-(contentHeight-1):]...)
	}
	return m.theme.Pane.
		Width(contentWidth).
		Height(contentHeight).
		Render(strings.Join(lines, "\n"))
}

func wrappedStyledLines(value string, width int) []string {
	if value == "" {
		return nil
	}
	rendered := lipgloss.NewStyle().Width(max(width, 1)).Render(value)
	return strings.Split(rendered, "\n")
}

func tailWindow(lines []string, height, scroll int) []string {
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

func (m *model) conversationGeometry() (width, height int) {
	width = max(m.width, 40)
	screenHeight := max(m.height, 12)
	bodyHeight := max(screenHeight-4, 6)
	if width >= 88 {
		activityWidth := max(28, width/3)
		return width - activityWidth - 1, bodyHeight
	}
	activityHeight := min(7, max(4, bodyHeight/3))
	return width, bodyHeight - activityHeight
}

func (m *model) maxConversationScroll() int {
	width, height := m.conversationGeometry()
	contentWidth := max(width-2, 1)
	contentHeight := max(height-2, 1)
	return max(0, len(m.conversationLines(contentWidth))-contentHeight)
}

func (m *model) scrollBy(delta int) {
	m.scroll = min(max(m.scroll+delta, 0), m.maxConversationScroll())
}

func (m *model) conversationContains(x, y int) bool {
	width, height := m.conversationGeometry()
	return x >= 0 && x < width && y >= 1 && y < 1+height
}

func spinnerFrame(elapsed time.Duration) string {
	frames := []string{"◐", "◓", "◑", "◒"}
	index := int(elapsed/(100*time.Millisecond)) % len(frames)
	return frames[index]
}

func formatDuration(value time.Duration) string {
	if value <= 0 {
		return "00:00.0"
	}
	minutes := int(value.Minutes())
	seconds := value.Seconds() - float64(minutes*60)
	return fmt.Sprintf("%02d:%04.1f", minutes, seconds)
}
