package agent

import (
	"context"
	"errors"
	"fmt"
	"io"
	"strings"
	"time"

	"charm.land/bubbles/v2/textinput"
	tea "charm.land/bubbletea/v2"
	agentcore "github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/terminal"
)

type Metadata struct {
	Model     string
	Provider  string
	Workspace string
	Thinking  string
}

type Session interface {
	RunWithObserver(context.Context, string, func(agentcore.Event)) (agentcore.Result, error)
	Reset()
}

type Summary struct {
	Tasks     int
	Failed    int
	Cancelled bool
}

type turn struct {
	prompt string
	output string
	err    error
	steps  int
}

type activity struct {
	text  string
	style activityStyle
}

type activityStyle int

const (
	activityMuted activityStyle = iota
	activityAccent
	activitySuccess
	activityWarning
)

type model struct {
	parent  context.Context
	session Session
	meta    Metadata
	theme   terminal.Theme
	input   textinput.Model

	width  int
	height int
	scroll int

	turns         []turn
	current       string
	activities    []activity
	step          int
	started       time.Time
	elapsed       time.Duration
	running       bool
	cancelling    bool
	exitAfterRun  bool
	cancel        context.CancelFunc
	messages      <-chan tea.Msg
	operationDone <-chan struct{}

	summary Summary
}

type tickMsg time.Time
type eventMsg agentcore.Event
type doneMsg struct {
	result agentcore.Result
	err    error
}
type taskChannelClosedMsg struct{}

func newModel(parent context.Context, session Session, meta Metadata, initialPrompt string) *model {
	input := textinput.New()
	input.Prompt = "Ask › "
	input.Placeholder = "ask the read-only repository agent"
	input.CharLimit = 4096
	value := &model{
		parent:  parent,
		session: session,
		meta:    meta,
		theme:   terminal.NewTheme(true),
		input:   input,
	}
	if prompt := strings.TrimSpace(initialPrompt); prompt != "" {
		value.beginTask(prompt)
	} else {
		value.input.Focus()
	}
	return value
}

func (m *model) Init() tea.Cmd {
	commands := []tea.Cmd{tickCommand()}
	if m.running {
		commands = append(commands, waitTaskMessage(m.messages))
	} else {
		commands = append(commands, m.input.Focus())
	}
	return tea.Batch(commands...)
}

func tickCommand() tea.Cmd {
	return tea.Tick(100*time.Millisecond, func(value time.Time) tea.Msg {
		return tickMsg(value)
	})
}

func waitTaskMessage(messages <-chan tea.Msg) tea.Cmd {
	return func() tea.Msg {
		message, ok := <-messages
		if !ok {
			return taskChannelClosedMsg{}
		}
		return message
	}
}

func (m *model) beginTask(prompt string) {
	m.current = strings.TrimSpace(prompt)
	m.activities = []activity{{text: "Task accepted", style: activityAccent}}
	m.step = 0
	m.scroll = 0
	m.started = time.Now()
	m.elapsed = 0
	m.running = true
	m.cancelling = false
	m.exitAfterRun = false
	m.input.Blur()
	m.input.Reset()

	ctx, cancel := context.WithCancel(m.parent)
	m.cancel = cancel
	messages := make(chan tea.Msg, 128)
	m.messages = messages
	operationDone := make(chan struct{})
	m.operationDone = operationDone
	session := m.session
	task := m.current
	go func() {
		defer close(operationDone)
		defer close(messages)
		observe := func(event agentcore.Event) {
			select {
			case messages <- eventMsg(event):
			case <-ctx.Done():
			}
		}
		result, err := session.RunWithObserver(ctx, task, observe)
		messages <- doneMsg{result: result, err: err}
	}()
}

func (m *model) Update(message tea.Msg) (tea.Model, tea.Cmd) {
	switch value := message.(type) {
	case tea.WindowSizeMsg:
		m.width = value.Width
		m.height = value.Height
		m.input.SetWidth(max(value.Width-8, 12))
	case tickMsg:
		if m.running {
			m.elapsed = time.Time(value).Sub(m.started)
		}
		return m, tickCommand()
	case eventMsg:
		m.recordEvent(agentcore.Event(value))
		return m, waitTaskMessage(m.messages)
	case doneMsg:
		m.finishTask(value)
		if m.exitAfterRun {
			return m, tea.Quit
		}
		return m, tea.Batch(waitTaskMessage(m.messages), m.input.Focus())
	case taskChannelClosedMsg:
		return m, nil
	case tea.KeyPressMsg:
		return m.updateKey(value)
	case tea.MouseWheelMsg:
		return m.updateMouseWheel(value)
	}
	if !m.running {
		var command tea.Cmd
		m.input, command = m.input.Update(message)
		return m, command
	}
	return m, nil
}

func (m *model) updateKey(message tea.KeyPressMsg) (tea.Model, tea.Cmd) {
	key := message.Keystroke()
	if m.running {
		switch key {
		case "ctrl+c":
			if !m.cancelling {
				m.cancelling = true
				m.activities = append(m.activities, activity{
					text:  "Cancelling current task…",
					style: activityWarning,
				})
				m.cancel()
			}
		case "q", "esc":
			m.exitAfterRun = true
			if !m.cancelling {
				m.cancelling = true
				m.cancel()
			}
		case "up", "pgup":
			step := 1
			if key == "pgup" {
				step = 5
			}
			m.scrollBy(step)
		case "down", "pgdown":
			step := 1
			if key == "pgdown" {
				step = 5
			}
			m.scrollBy(-step)
		}
		return m, nil
	}

	switch key {
	case "ctrl+c", "esc":
		return m, tea.Quit
	case "enter":
		prompt := strings.TrimSpace(m.input.Value())
		if prompt == "" {
			return m, nil
		}
		switch prompt {
		case "/new", "/reset":
			m.session.Reset()
			m.turns = nil
			m.activities = []activity{{
				text:  "Conversation reset",
				style: activitySuccess,
			}}
			m.scroll = 0
			m.input.Reset()
			return m, nil
		case "/exit", "/quit":
			return m, tea.Quit
		}
		m.beginTask(prompt)
		return m, waitTaskMessage(m.messages)
	case "up", "pgup":
		step := 1
		if key == "pgup" {
			step = 5
		}
		m.scrollBy(step)
		return m, nil
	case "down", "pgdown":
		step := 1
		if key == "pgdown" {
			step = 5
		}
		m.scrollBy(-step)
		return m, nil
	default:
		var command tea.Cmd
		m.input, command = m.input.Update(message)
		return m, command
	}
}

func (m *model) updateMouseWheel(message tea.MouseWheelMsg) (tea.Model, tea.Cmd) {
	mouse := message.Mouse()
	if !m.conversationContains(mouse.X, mouse.Y) {
		return m, nil
	}
	switch mouse.Button {
	case tea.MouseWheelUp:
		m.scrollBy(3)
	case tea.MouseWheelDown:
		m.scrollBy(-3)
	}
	return m, nil
}

func (m *model) recordEvent(event agentcore.Event) {
	m.step = max(m.step, event.Step)
	switch event.Kind {
	case agentcore.EventRouteStart:
		m.activities = append(m.activities, activity{
			text:  "Routing · checking whether workspace evidence is needed",
			style: activityAccent,
		})
	case agentcore.EventRouteDone:
		text := fmt.Sprintf("Route · %s", event.Route)
		style := activitySuccess
		if event.Err != nil {
			text = fmt.Sprintf("Route · respond fallback: %v", event.Err)
			style = activityWarning
		}
		m.activities = append(m.activities, activity{text: text, style: style})
	case agentcore.EventModelStart:
		m.activities = append(m.activities, activity{
			text:  fmt.Sprintf("Step %d · deciding next action", event.Step),
			style: activityAccent,
		})
	case agentcore.EventRetry:
		m.activities = append(m.activities, activity{
			text:  fmt.Sprintf("Step %d · retrying invalid action", event.Step),
			style: activityWarning,
		})
	case agentcore.EventToolStart:
		m.activities = append(m.activities, activity{
			text:  fmt.Sprintf("Step %d · %s", event.Step, event.Tool),
			style: activityAccent,
		})
	case agentcore.EventToolDone:
		text := fmt.Sprintf("Step %d · %s complete", event.Step, event.Tool)
		style := activitySuccess
		if event.Err != nil {
			text = fmt.Sprintf("Step %d · %s failed: %v", event.Step, event.Tool, event.Err)
			style = activityWarning
		}
		m.activities = append(m.activities, activity{text: text, style: style})
	}
	if len(m.activities) > 40 {
		m.activities = append([]activity(nil), m.activities[len(m.activities)-40:]...)
	}
}

func (m *model) finishTask(message doneMsg) {
	if m.cancel != nil {
		m.cancel()
	}
	m.running = false
	m.cancelling = false
	m.elapsed = time.Since(m.started)
	m.summary.Tasks++
	if message.err != nil {
		if errors.Is(message.err, context.Canceled) {
			m.summary.Cancelled = true
			m.activities = append(m.activities, activity{
				text:  "Task cancelled",
				style: activityWarning,
			})
		} else {
			m.summary.Failed++
			m.activities = append(m.activities, activity{
				text:  "Task failed: " + message.err.Error(),
				style: activityWarning,
			})
		}
	} else {
		m.activities = append(m.activities, activity{
			text:  fmt.Sprintf("Completed in %d step(s)", len(message.result.Steps)),
			style: activitySuccess,
		})
	}
	m.turns = append(m.turns, turn{
		prompt: m.current,
		output: terminal.SanitizeModelText(message.result.Output),
		err:    message.err,
		steps:  len(message.result.Steps),
	})
	m.current = ""
	m.input.Reset()
	m.input.Focus()
}

func Run(
	ctx context.Context,
	session Session,
	meta Metadata,
	initialPrompt string,
	input io.Reader,
	output io.Writer,
) (Summary, error) {
	if session == nil {
		return Summary{}, errors.New("agent TUI session is required")
	}
	initial := newModel(ctx, session, meta, initialPrompt)
	program := tea.NewProgram(
		initial,
		tea.WithContext(ctx),
		tea.WithInput(input),
		tea.WithOutput(output),
	)
	finalValue, programErr := program.Run()
	final, ok := finalValue.(*model)
	if !ok {
		if initial.cancel != nil {
			initial.cancel()
		}
		if initial.operationDone != nil {
			<-initial.operationDone
		}
		return Summary{}, fmt.Errorf("unexpected TUI model %T", finalValue)
	}
	if final.running {
		final.cancel()
		<-final.operationDone
		final.summary.Cancelled = true
	}
	if programErr != nil && !errors.Is(programErr, tea.ErrProgramKilled) {
		return final.summary, programErr
	}
	return final.summary, nil
}
