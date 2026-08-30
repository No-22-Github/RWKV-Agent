package concurrent

import (
	"fmt"
	"os/exec"
	"strings"

	tea "charm.land/bubbletea/v2"
	"charm.land/lipgloss/v2"
	"github.com/charmbracelet/x/ansi"
	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/terminal"
	"github.com/no22/RWKV-Agent/internal/tui/tuiutil"
)

func (m *model) View() tea.View {
	width := max(m.width, 40)
	height := max(m.height, 12)
	snapshot := m.snapshot
	if len(snapshot.Sessions) == 0 && m.runner != nil {
		snapshot = m.runner.Snapshot()
	}
	layout := ComputeLayout(width, height, len(snapshot.Sessions))

	header := m.renderHeader(snapshot, width)
	var body string
	if layout.Kind == LayoutCompact {
		body = m.renderCompact(snapshot, width, height-5)
	} else {
		body = m.renderPanes(snapshot, layout)
	}
	footer := m.renderFooter(snapshot, width)
	content := strings.Join([]string{header, body, footer}, "\n")
	view := tea.NewView(content)
	view.AltScreen = true
	view.MouseMode = tea.MouseModeCellMotion
	view.WindowTitle = "RWKV concurrent inference"
	return view
}

func (m *model) renderHeader(snapshot concurrentcli.RunSnapshot, width int) string {
	name := m.meta.Model
	if name == "" {
		name = "RWKV"
	}
	left := fmt.Sprintf(
		" %s · %s · Continuous Batch %d · %s",
		name,
		strings.ToUpper(m.meta.Provider),
		m.meta.Concurrency,
		snapshot.Phase,
	)
	right := tuiutil.FormatDuration(snapshot.Elapsed) + " "
	padding := max(1, width-lipgloss.Width(left)-lipgloss.Width(right))
	line := left + strings.Repeat(" ", padding) + right
	return ansi.Truncate(line, width, "")
}

func (m *model) renderPanes(snapshot concurrentcli.RunSnapshot, layout Layout) string {
	rows := make([]string, 0, layout.Rows)
	for row := 0; row < layout.Rows; row++ {
		var panes []string
		for column := 0; column < layout.Columns; column++ {
			index := row*layout.Columns + column
			if index >= len(snapshot.Sessions) {
				panes = append(panes, strings.Repeat(" ", layout.PaneWidth))
				continue
			}
			scroll := 0
			if index < len(m.scroll) {
				scroll = m.scroll[index]
			}
			panes = append(
				panes,
				m.renderPane(snapshot.Sessions[index], layout.PaneWidth, layout.PaneHeight, index == m.active, scroll),
			)
		}
		rowParts := make([]string, 0, len(panes)*2-1)
		for index, pane := range panes {
			if index > 0 {
				rowParts = append(rowParts, strings.Repeat(" ", layout.Gap))
			}
			rowParts = append(rowParts, pane)
		}
		rows = append(rows, lipgloss.JoinHorizontal(lipgloss.Top, rowParts...))
	}
	rowParts := make([]string, 0, len(rows)*2-1)
	for index, row := range rows {
		if index > 0 {
			rowParts = append(rowParts, strings.Repeat("\n", layout.Gap))
		}
		rowParts = append(rowParts, row)
	}
	return lipgloss.JoinVertical(lipgloss.Left, rowParts...)
}

func (m *model) renderPane(
	session concurrentcli.SessionSnapshot,
	width, height int,
	focused bool,
	scroll int,
) string {
	contentWidth := max(width-2, 1)
	contentHeight := max(height-2, 1)
	bodyHeight := max(contentHeight-2, 1)
	phase := m.phaseStyle(session.Phase).Render(string(session.Phase))
	status := ""
	switch session.Phase {
	case concurrentcli.PhasePrefill:
		if session.PrefillTotal > 0 {
			status = fmt.Sprintf(" · %d/%d", session.PrefillDone, session.PrefillTotal)
		}
	case concurrentcli.PhaseGenerating, concurrentcli.PhaseDone:
		if session.DecodeTPS > 0 {
			status = fmt.Sprintf(" · %.1f tok/s", session.DecodeTPS)
		}
	case concurrentcli.PhaseError:
		status = " · failed"
	}
	title := fmt.Sprintf(" Session %d · %s%s", session.Index, phase, status)
	title = ansi.Truncate(title, contentWidth, "…")

	lines := tuiutil.WrappedLines(terminal.SanitizeModelText(session.Output), contentWidth)
	body := tuiutil.TailWindow(lines, bodyHeight, scroll)
	for len(body) < bodyHeight {
		body = append(body, "")
	}
	footer := fmt.Sprintf(" %d tokens", session.OutputTokens)
	if session.Phase == concurrentcli.PhaseDone ||
		session.Phase == concurrentcli.PhaseCancelled ||
		session.Phase == concurrentcli.PhaseError {
		footer += " · " + tuiutil.FormatDuration(session.Elapsed)
	}
	if session.FinishReason != "" {
		footer += " · " + string(session.FinishReason)
	}
	footer = ansi.Truncate(footer, contentWidth, "…")

	content := strings.Join(append(append([]string{title}, body...), footer), "\n")
	style := m.theme.Pane
	if focused {
		style = m.theme.PaneFocus
	}
	return style.Width(contentWidth).Height(contentHeight).Render(content)
}

func (m *model) renderCompact(snapshot concurrentcli.RunSnapshot, width, height int) string {
	lines := make([]string, 0, len(snapshot.Sessions))
	for index, session := range snapshot.Sessions {
		marker := " "
		if index == m.active {
			marker = "›"
		}
		output := strings.ReplaceAll(terminal.SanitizeModelText(session.Output), "\n", " ")
		prefix := fmt.Sprintf(
			"%s Session %d · %-10s · %4d tok · ",
			marker,
			session.Index,
			session.Phase,
			session.OutputTokens,
		)
		lines = append(lines, ansi.Truncate(prefix+output, width, "…"))
	}
	for len(lines) < height {
		lines = append(lines, "")
	}
	if len(lines) > height {
		lines = lines[:height]
	}
	return strings.Join(lines, "\n")
}

func (m *model) renderFooter(snapshot concurrentcli.RunSnapshot, width int) string {
	status := fmt.Sprintf(
		" native batch %d/%d · total %d tokens · aggregate %.1f tok/s",
		snapshot.MaxNativeBatch,
		m.meta.Concurrency,
		snapshot.TotalTokens,
		snapshot.AggregateTPS,
	)
	keys := " click pane · Tab/←/→ select · ↑/↓ scroll · Ctrl-C/q/Esc cancel "
	if snapshot.Done {
		keys = " click/Enter continue · q quit · r rerun · y copy "
	}
	padding := max(1, width-lipgloss.Width(status)-lipgloss.Width(keys))
	first := ansi.Truncate(status+strings.Repeat(" ", padding)+keys, width, "")
	second := " " + m.theme.Muted.Render("Select a result, then continue that exact Conversation")
	if m.notice != "" {
		second = " " + terminal.SanitizeModelText(m.notice)
	}
	if m.inputMode {
		second = " " + m.input.View()
	} else if m.running && snapshot.Phase == concurrentcli.RunFollowing {
		second = fmt.Sprintf(" Continuing Session %d · streaming into the selected pane…", m.active+1)
	}
	return first + "\n" + ansi.Truncate(second, width, "")
}

func (m *model) phaseStyle(phase concurrentcli.SessionPhase) lipgloss.Style {
	switch phase {
	case concurrentcli.PhaseQueued:
		return m.theme.Muted
	case concurrentcli.PhasePrefill:
		return m.theme.Accent
	case concurrentcli.PhaseGenerating:
		return m.theme.Warning
	case concurrentcli.PhaseDone:
		return m.theme.Success
	case concurrentcli.PhaseCancelled:
		return lipgloss.NewStyle().Foreground(lipgloss.Color("201"))
	case concurrentcli.PhaseError:
		return m.theme.Danger
	default:
		return m.theme.Muted
	}
}

func copyCommand(value string) tea.Cmd {
	return func() tea.Msg {
		command := exec.Command("pbcopy")
		command.Stdin = strings.NewReader(value)
		if err := command.Run(); err != nil {
			return copyMsg{err: fmt.Errorf("copy failed: %w", err)}
		}
		return copyMsg{}
	}
}
