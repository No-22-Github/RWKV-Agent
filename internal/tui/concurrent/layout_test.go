package concurrent

import (
	"strings"
	"testing"
	"time"

	"charm.land/lipgloss/v2"
	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/terminal"
	"github.com/no22/RWKV-Agent/internal/tui/tuiutil"
)

func TestComputeLayout(t *testing.T) {
	t.Parallel()

	tests := []struct {
		name          string
		width, height int
		count         int
		kind          LayoutKind
		columns       int
	}{
		{"four wide", 120, 32, 4, LayoutGrid, 2},
		{"eight ultra wide", 180, 28, 8, LayoutGrid, 4},
		{"eight standard", 120, 32, 8, LayoutGrid, 2},
		{"two wide", 90, 24, 2, LayoutColumns, 2},
		{"narrow tall", 70, 40, 4, LayoutStack, 1},
		{"too short", 70, 20, 4, LayoutCompact, 1},
	}
	for _, test := range tests {
		test := test
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			layout := ComputeLayout(test.width, test.height, test.count)
			if layout.Kind != test.kind || layout.Columns != test.columns {
				t.Fatalf("layout = %+v", layout)
			}
			if layout.PaneWidth <= 0 || layout.PaneHeight <= 0 {
				t.Fatalf("invalid pane size: %+v", layout)
			}
		})
	}
}

func TestPaneAtMapsMouseCoordinates(t *testing.T) {
	t.Parallel()

	layout := ComputeLayout(120, 32, 8)
	for index := 0; index < 8; index++ {
		row := index / layout.Columns
		column := index % layout.Columns
		x := column*(layout.PaneWidth+layout.Gap) + 2
		y := 1 + row*(layout.PaneHeight+layout.Gap) + 2
		got, ok := layout.PaneAt(x, y, 8)
		if !ok || got != index {
			t.Fatalf("pane at (%d,%d) = %d,%t; want %d,true", x, y, got, ok, index)
		}
	}
	if _, ok := layout.PaneAt(layout.PaneWidth, 2, 8); ok {
		t.Fatal("horizontal gap was treated as a pane")
	}
}

func TestTailWindowAndSanitizationHandleWideText(t *testing.T) {
	t.Parallel()

	value := terminal.SanitizeModelText("第一行🙂\n第二行\033[2J\n第三行\n第四行")
	lines := tuiutil.WrappedLines(value, 12)
	window := tuiutil.TailWindow(lines, 2, 0)
	if len(window) != 2 {
		t.Fatalf("window lines = %d", len(window))
	}
	if !strings.HasPrefix(window[0], "…") {
		t.Fatalf("truncation marker missing: %#v", window)
	}
	for _, line := range window {
		if lipgloss.Width(line) > 12 {
			t.Fatalf("line width = %d: %q", lipgloss.Width(line), line)
		}
	}
}

func TestDashboardViewFitsRequestedCells(t *testing.T) {
	t.Parallel()

	m := &model{
		meta:   Metadata{Model: "RWKV G1", Provider: "mlx", Concurrency: 4},
		theme:  terminal.NewTheme(true),
		width:  120,
		height: 32,
		scroll: make([]int, 4),
		snapshot: concurrentcli.RunSnapshot{
			Phase:          concurrentcli.RunRunning,
			Elapsed:        3200 * time.Millisecond,
			MaxNativeBatch: 4,
			TotalTokens:    129,
			AggregateTPS:   63.2,
			Sessions: []concurrentcli.SessionSnapshot{
				{Index: 1, Phase: concurrentcli.PhaseGenerating, Output: "RWKV 是一种基于 RNN 的语言模型🙂", OutputTokens: 48, DecodeTPS: 21.3},
				{Index: 2, Phase: concurrentcli.PhasePrefill, PrefillDone: 46, PrefillTotal: 71},
				{Index: 3, Phase: concurrentcli.PhaseDone, Output: "done", OutputTokens: 39, DecodeTPS: 22.1},
				{Index: 4, Phase: concurrentcli.PhaseGenerating, Output: "long\noutput\nwith\nlines", OutputTokens: 42, DecodeTPS: 19.8},
			},
		},
	}
	view := m.View().Content
	if width := lipgloss.Width(view); width > 120 {
		t.Fatalf("view width = %d, want <= 120", width)
	}
	if height := lipgloss.Height(view); height > 32 {
		t.Fatalf("view height = %d, want <= 32", height)
	}
	for _, label := range []string{"Session 1", "Session 2", "Session 3", "Session 4", "native batch 4/4"} {
		if !strings.Contains(view, label) {
			t.Fatalf("view missing %q", label)
		}
	}
}
