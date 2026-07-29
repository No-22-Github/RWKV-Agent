package agent

import (
	"context"
	"errors"
	"strings"
	"testing"
	"time"

	tea "charm.land/bubbletea/v2"
	"charm.land/lipgloss/v2"
	agentcore "github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/terminal"
)

func TestViewFitsWideAndNarrowTerminals(t *testing.T) {
	t.Parallel()

	for _, size := range []struct {
		width  int
		height int
	}{
		{width: 110, height: 28},
		{width: 64, height: 22},
	} {
		value := &model{
			meta: Metadata{
				Model:     "rwkv-g1",
				Provider:  "mlx",
				Workspace: "/tmp/example",
			},
			theme:  terminal.NewTheme(true),
			width:  size.width,
			height: size.height,
			turns: []turn{{
				prompt: "阅读 README 并总结🙂",
				output: "这是一个只读 Agent。",
				steps:  2,
			}},
			activities: []activity{
				{text: "Step 1 · deciding next action", style: activityAccent},
				{text: "Step 1 · read_file complete", style: activitySuccess},
			},
		}
		value.input = newModel(context.Background(), nil, Metadata{}, "").input
		rendered := value.View()
		view := rendered.Content
		if rendered.MouseMode != tea.MouseModeCellMotion {
			t.Fatalf("%dx%d mouse mode = %v", size.width, size.height, rendered.MouseMode)
		}
		if got := lipgloss.Width(view); got > size.width {
			t.Fatalf("%dx%d view width = %d", size.width, size.height, got)
		}
		if got := lipgloss.Height(view); got > size.height {
			t.Fatalf("%dx%d view height = %d", size.width, size.height, got)
		}
		for _, fragment := range []string{"READ ONLY", "Conversation", "Activity", "read_file"} {
			if !strings.Contains(view, fragment) {
				t.Fatalf("%dx%d view missing %q", size.width, size.height, fragment)
			}
		}
	}
}

func TestTailWindowClampsOverscrollToAFullViewport(t *testing.T) {
	t.Parallel()

	lines := []string{"one", "two", "three", "four", "five", "six"}
	window := tailWindow(lines, 3, 100)
	if got, want := strings.Join(window, ","), "one,two,three"; got != want {
		t.Fatalf("overscrolled window = %q, want %q", got, want)
	}
}

func TestMouseWheelScrollsOnlyConversationAndClampsOffset(t *testing.T) {
	t.Parallel()

	value := newModel(context.Background(), &fakeSession{}, Metadata{}, "")
	value.width = 100
	value.height = 24
	value.turns = []turn{{
		prompt: "long answer",
		output: strings.Repeat("line\n", 40),
	}}
	maxScroll := value.maxConversationScroll()
	if maxScroll <= 0 {
		t.Fatal("test conversation is not scrollable")
	}
	for range 100 {
		_, _ = value.Update(tea.MouseWheelMsg{
			X:      2,
			Y:      2,
			Button: tea.MouseWheelUp,
		})
	}
	if value.scroll != maxScroll {
		t.Fatalf("scroll = %d, want clamped max %d", value.scroll, maxScroll)
	}
	_, _ = value.Update(tea.MouseWheelMsg{
		X:      2,
		Y:      2,
		Button: tea.MouseWheelDown,
	})
	if value.scroll != maxScroll-3 {
		t.Fatalf("scroll after wheel down = %d", value.scroll)
	}
	unchanged := value.scroll
	_, _ = value.Update(tea.MouseWheelMsg{
		X:      90,
		Y:      2,
		Button: tea.MouseWheelUp,
	})
	if value.scroll != unchanged {
		t.Fatalf("activity-pane wheel changed conversation scroll: %d", value.scroll)
	}
}

func TestModelCanRunMultipleConversationTurns(t *testing.T) {
	t.Parallel()

	session := &fakeSession{}
	value := newModel(context.Background(), session, Metadata{}, "first")
	message := (<-value.messages).(eventMsg)
	_, command := value.Update(message)
	if command == nil {
		t.Fatal("event did not schedule the next task message")
	}
	done := (<-value.messages).(doneMsg)
	value.finishTask(done)
	value.beginTask("second")
	for message := range value.messages {
		if completed, ok := message.(doneMsg); ok {
			value.finishTask(completed)
		}
	}
	if len(session.prompts) != 2 ||
		session.prompts[0] != "first" ||
		session.prompts[1] != "second" {
		t.Fatalf("prompts = %#v", session.prompts)
	}
	if value.summary.Tasks != 2 || len(value.turns) != 2 {
		t.Fatalf("summary=%+v turns=%d", value.summary, len(value.turns))
	}
}

func TestCancelledTaskReturnsToInput(t *testing.T) {
	t.Parallel()

	session := &fakeSession{block: true}
	value := newModel(context.Background(), session, Metadata{}, "wait")
	value.cancel()
	var completed doneMsg
	select {
	case message := <-value.messages:
		var ok bool
		completed, ok = message.(doneMsg)
		if !ok {
			t.Fatalf("message = %T", message)
		}
	case <-time.After(time.Second):
		t.Fatal("cancelled task did not finish")
	}
	value.finishTask(completed)
	if value.running || !errors.Is(value.turns[0].err, context.Canceled) {
		t.Fatalf("running=%t turn=%+v", value.running, value.turns[0])
	}
}

type fakeSession struct {
	prompts []string
	block   bool
	resets  int
}

func (s *fakeSession) RunWithObserver(
	ctx context.Context,
	prompt string,
	observe func(agentcore.Event),
) (agentcore.Result, error) {
	s.prompts = append(s.prompts, prompt)
	if s.block {
		<-ctx.Done()
		return agentcore.Result{}, ctx.Err()
	}
	observe(agentcore.Event{Kind: agentcore.EventModelStart, Step: 1})
	return agentcore.Result{
		Output: "answer: " + prompt,
		Steps:  []agentcore.Step{{Number: 1}},
	}, nil
}

func (s *fakeSession) Reset() {
	s.resets++
}
