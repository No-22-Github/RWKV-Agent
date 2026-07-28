package concurrent

import (
	"context"
	"errors"
	"fmt"
	"io"
	"strings"
	"time"

	"charm.land/bubbles/v2/textinput"
	tea "charm.land/bubbletea/v2"
	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/terminal"
)

type Metadata struct {
	Model       string
	Provider    string
	Concurrency int
}

type RunnerFactory func() (*concurrentcli.Runner, error)

type model struct {
	parent  context.Context
	factory RunnerFactory
	meta    Metadata
	theme   terminal.Theme

	runner        *concurrentcli.Runner
	runCtx        context.Context
	cancel        context.CancelFunc
	snapshot      concurrentcli.RunSnapshot
	summary       concurrentcli.Summary
	runErr        error
	result        <-chan doneMsg
	operationDone <-chan struct{}

	width        int
	height       int
	active       int
	scroll       []int
	notice       string
	running      bool
	exitAfterRun bool
	inputMode    bool
	input        textinput.Model
}

type tickMsg time.Time

type operationKind string

const (
	operationInitial  operationKind = "initial"
	operationFollowUp operationKind = "follow-up"
)

type doneMsg struct {
	summary concurrentcli.Summary
	err     error
	kind    operationKind
}

type copyMsg struct {
	err error
}

func newModel(parent context.Context, factory RunnerFactory, meta Metadata) (*model, error) {
	input := textinput.New()
	input.Prompt = "Ask › "
	input.Placeholder = "click a completed pane, then continue the conversation"
	input.CharLimit = 4096
	value := &model{
		parent:  parent,
		factory: factory,
		meta:    meta,
		theme:   terminal.NewTheme(true),
		input:   input,
	}
	if err := value.beginRun(); err != nil {
		return nil, err
	}
	return value, nil
}

func (m *model) beginRun() error {
	runner, err := m.factory()
	if err != nil {
		return err
	}
	if m.runner != nil {
		_ = m.runner.Close()
	}
	m.runner = runner
	m.runCtx, m.cancel = context.WithCancel(m.parent)
	m.snapshot = runner.Snapshot()
	m.scroll = make([]int, len(m.snapshot.Sessions))
	m.running = true
	m.exitAfterRun = false
	m.notice = ""
	m.runErr = nil
	m.inputMode = false
	m.input.Blur()
	m.input.Reset()
	result := make(chan doneMsg, 1)
	m.result = result
	operationDone := make(chan struct{})
	m.operationDone = operationDone
	runCtx := m.runCtx
	go func() {
		defer close(operationDone)
		summary, runErr := runner.Run(runCtx)
		result <- doneMsg{summary: summary, err: runErr, kind: operationInitial}
	}()
	return nil
}

func (m *model) beginFollowUp(prompt string) {
	m.runCtx, m.cancel = context.WithCancel(m.parent)
	m.running = true
	m.exitAfterRun = false
	m.notice = fmt.Sprintf("continuing Session %d…", m.active+1)
	result := make(chan doneMsg, 1)
	m.result = result
	operationDone := make(chan struct{})
	m.operationDone = operationDone
	runner := m.runner
	runCtx := m.runCtx
	sessionIndex := m.active + 1
	go func() {
		defer close(operationDone)
		_, runErr := runner.FollowUp(runCtx, sessionIndex, prompt)
		result <- doneMsg{
			summary: runner.Summary(),
			err:     runErr,
			kind:    operationFollowUp,
		}
	}()
}

func (m *model) Init() tea.Cmd {
	return tea.Batch(m.runCommand(), tickCommand())
}

func (m *model) runCommand() tea.Cmd {
	result := m.result
	return func() tea.Msg {
		return <-result
	}
}

func tickCommand() tea.Cmd {
	return tea.Tick(time.Second/25, func(value time.Time) tea.Msg {
		return tickMsg(value)
	})
}

func (m *model) Update(message tea.Msg) (tea.Model, tea.Cmd) {
	switch value := message.(type) {
	case tea.WindowSizeMsg:
		m.width = value.Width
		m.height = value.Height
		m.input.SetWidth(max(value.Width-8, 12))
	case tickMsg:
		if m.runner != nil {
			select {
			case <-m.runner.Dirty():
			default:
			}
			m.snapshot = m.runner.Snapshot()
		}
		return m, tickCommand()
	case doneMsg:
		m.snapshot = m.runner.Snapshot()
		m.summary = value.summary
		m.runErr = value.err
		m.running = false
		if m.cancel != nil {
			m.cancel()
		}
		if value.err != nil && !errors.Is(value.err, context.Canceled) {
			m.notice = "run failed: " + value.err.Error()
		}
		if m.exitAfterRun {
			return m, tea.Quit
		}
		if value.kind == operationFollowUp {
			m.notice = fmt.Sprintf("Session %d ready for another question", m.active+1)
			return m.activateInput(m.active)
		}
	case copyMsg:
		if value.err != nil {
			m.notice = value.err.Error()
		} else {
			m.notice = fmt.Sprintf("session %d output copied", m.active+1)
		}
	case tea.KeyPressMsg:
		return m.updateKey(value)
	case tea.MouseClickMsg:
		return m.updateMouse(value)
	}
	if m.inputMode {
		var command tea.Cmd
		m.input, command = m.input.Update(message)
		return m, command
	}
	return m, nil
}

func (m *model) updateKey(message tea.KeyPressMsg) (tea.Model, tea.Cmd) {
	key := message.Keystroke()
	if m.inputMode {
		switch key {
		case "esc", "ctrl+c":
			m.inputMode = false
			m.input.Blur()
			m.input.Reset()
			m.notice = fmt.Sprintf("Session %d selected", m.active+1)
			return m, nil
		case "enter":
			prompt := strings.TrimSpace(m.input.Value())
			if prompt == "" {
				return m, nil
			}
			m.inputMode = false
			m.input.Blur()
			m.input.Reset()
			m.beginFollowUp(prompt)
			return m, m.runCommand()
		default:
			var command tea.Cmd
			m.input, command = m.input.Update(message)
			return m, command
		}
	}
	count := len(m.snapshot.Sessions)
	switch key {
	case "ctrl+c", "q", "esc":
		if m.running {
			m.notice = "cancelling all sessions…"
			m.snapshot.Phase = concurrentcli.RunCancelling
			m.exitAfterRun = true
			m.cancel()
			return m, nil
		}
		return m, tea.Quit
	case "enter":
		if !m.running {
			return m.activateInput(m.active)
		}
	case "tab", "right":
		if count > 0 {
			m.active = (m.active + 1) % count
		}
	case "shift+tab", "left":
		if count > 0 {
			m.active = (m.active - 1 + count) % count
		}
	case "up", "pgup":
		if m.active < len(m.scroll) {
			step := 1
			if key == "pgup" {
				step = 5
			}
			m.scroll[m.active] += step
		}
	case "down", "pgdown":
		if m.active < len(m.scroll) {
			step := 1
			if key == "pgdown" {
				step = 5
			}
			m.scroll[m.active] = max(0, m.scroll[m.active]-step)
		}
	case "y":
		if count > 0 {
			return m, copyCommand(m.snapshot.Sessions[m.active].Output)
		}
	case "r":
		if !m.running {
			if err := m.beginRun(); err != nil {
				m.notice = "rerun failed: " + err.Error()
				return m, nil
			}
			return m, m.runCommand()
		}
	}
	return m, nil
}

func (m *model) updateMouse(message tea.MouseClickMsg) (tea.Model, tea.Cmd) {
	mouse := message.Mouse()
	if mouse.Button != tea.MouseLeft {
		return m, nil
	}
	layout := ComputeLayout(max(m.width, 40), max(m.height, 12), len(m.snapshot.Sessions))
	index, ok := layout.PaneAt(mouse.X, mouse.Y, len(m.snapshot.Sessions))
	if !ok {
		return m, nil
	}
	m.active = index
	if m.snapshot.Done && !m.running {
		return m.activateInput(index)
	}
	m.notice = fmt.Sprintf("Session %d selected", index+1)
	return m, nil
}

func (m *model) activateInput(index int) (tea.Model, tea.Cmd) {
	if index < 0 || index >= len(m.snapshot.Sessions) || m.running {
		return m, nil
	}
	m.active = index
	m.inputMode = true
	m.input.Reset()
	m.input.Placeholder = fmt.Sprintf("continue Session %d…", index+1)
	m.notice = fmt.Sprintf("continuing Session %d", index+1)
	return m, m.input.Focus()
}

func Run(
	ctx context.Context,
	factory RunnerFactory,
	meta Metadata,
	input io.Reader,
	output io.Writer,
) (concurrentcli.Summary, error) {
	initial, err := newModel(ctx, factory, meta)
	if err != nil {
		return concurrentcli.Summary{}, err
	}
	program := tea.NewProgram(
		initial,
		tea.WithContext(ctx),
		tea.WithInput(input),
		tea.WithOutput(output),
	)
	finalValue, programErr := program.Run()
	final, ok := finalValue.(*model)
	if !ok {
		initial.cancel()
		<-initial.operationDone
		_ = initial.runner.Close()
		return concurrentcli.Summary{}, fmt.Errorf("unexpected TUI model %T", finalValue)
	}
	if final.running {
		final.cancel()
		<-final.operationDone
		final.snapshot = final.runner.Snapshot()
		final.summary = final.runner.Summary()
		final.summary.Cancelled = true
	}
	closeErr := final.runner.Close()
	if programErr != nil && !errors.Is(programErr, tea.ErrProgramKilled) {
		return final.summary, programErr
	}
	if final.runErr == nil && closeErr != nil {
		return final.summary, closeErr
	}
	return final.summary, final.runErr
}
