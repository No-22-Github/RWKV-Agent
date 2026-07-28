package concurrent

type LayoutKind string

const (
	LayoutGrid    LayoutKind = "grid"
	LayoutColumns LayoutKind = "columns"
	LayoutStack   LayoutKind = "stack"
	LayoutCompact LayoutKind = "compact"
)

type Layout struct {
	Kind       LayoutKind
	Columns    int
	Rows       int
	PaneWidth  int
	PaneHeight int
	Gap        int
}

func ComputeLayout(width, height, count int) Layout {
	if count < 1 {
		count = 1
	}
	gap := 1
	availableHeight := height - 5
	columns := 1
	kind := LayoutStack
	switch {
	case count > 4 && width >= 160 && height >= 20:
		columns = 4
		kind = LayoutGrid
	case count >= 3 && width >= 100 && height >= 24:
		columns = 2
		kind = LayoutGrid
	case count == 2 && width >= 80:
		columns = 2
		kind = LayoutColumns
	}
	rows := (count + columns - 1) / columns
	paneWidth := (width - gap*(columns-1)) / columns
	paneHeight := (availableHeight - gap*(rows-1)) / rows
	if paneWidth < 24 || paneHeight < 6 {
		return Layout{
			Kind:       LayoutCompact,
			Columns:    1,
			Rows:       count,
			PaneWidth:  max(width, 1),
			PaneHeight: 1,
		}
	}
	return Layout{
		Kind:       kind,
		Columns:    columns,
		Rows:       rows,
		PaneWidth:  paneWidth,
		PaneHeight: paneHeight,
		Gap:        gap,
	}
}

func (l Layout) PaneAt(x, y, count int) (int, bool) {
	if count <= 0 || x < 0 || y < 1 {
		return 0, false
	}
	bodyY := y - 1
	if l.Kind == LayoutCompact {
		if bodyY >= count {
			return 0, false
		}
		return bodyY, true
	}
	rowSpan := l.PaneHeight + l.Gap
	columnSpan := l.PaneWidth + l.Gap
	row := bodyY / rowSpan
	column := x / columnSpan
	if row >= l.Rows || column >= l.Columns ||
		bodyY%rowSpan >= l.PaneHeight ||
		x%columnSpan >= l.PaneWidth {
		return 0, false
	}
	index := row*l.Columns + column
	if index >= count {
		return 0, false
	}
	return index, true
}
