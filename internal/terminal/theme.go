package terminal

import "charm.land/lipgloss/v2"

type Theme struct {
	Enabled bool

	Accent    lipgloss.Style
	Muted     lipgloss.Style
	Success   lipgloss.Style
	Warning   lipgloss.Style
	Danger    lipgloss.Style
	Title     lipgloss.Style
	Prompt    lipgloss.Style
	Pane      lipgloss.Style
	PaneFocus lipgloss.Style
}

func NewTheme(enabled bool) Theme {
	return Theme{
		Enabled:   enabled,
		Accent:    lipgloss.NewStyle().Foreground(lipgloss.Color("39")),
		Muted:     lipgloss.NewStyle().Foreground(lipgloss.Color("245")),
		Success:   lipgloss.NewStyle().Foreground(lipgloss.Color("42")),
		Warning:   lipgloss.NewStyle().Foreground(lipgloss.Color("214")),
		Danger:    lipgloss.NewStyle().Foreground(lipgloss.Color("196")),
		Title:     lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("75")),
		Prompt:    lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("39")),
		Pane:      lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).BorderForeground(lipgloss.Color("240")),
		PaneFocus: lipgloss.NewStyle().Border(lipgloss.RoundedBorder()).BorderForeground(lipgloss.Color("39")),
	}
}

func (t Theme) Render(style lipgloss.Style, value string) string {
	if !t.Enabled {
		return value
	}
	return style.Render(value)
}
