package terminal

import (
	"fmt"
	"io"
	"sync"
	"time"
)

type Spinner struct {
	writer io.Writer
	theme  Theme
	label  string
	done   chan struct{}
	wait   sync.WaitGroup
	once   sync.Once
}

func StartSpinner(writer io.Writer, theme Theme, label string) *Spinner {
	spinner := &Spinner{
		writer: writer,
		theme:  theme,
		label:  label,
		done:   make(chan struct{}),
	}
	if !theme.Enabled {
		fmt.Fprintln(writer, label+"...")
		return spinner
	}
	spinner.wait.Add(1)
	go spinner.loop()
	return spinner
}

func (s *Spinner) Stop(success bool, detail string) {
	s.once.Do(func() {
		close(s.done)
		s.wait.Wait()
		if !s.theme.Enabled {
			if success && detail != "" {
				fmt.Fprintln(s.writer, detail)
			}
			return
		}
		mark := s.theme.Render(s.theme.Success, "✓")
		if !success {
			mark = s.theme.Render(s.theme.Danger, "✗")
		}
		fmt.Fprintf(s.writer, "\r\033[2K%s %s\n", mark, detail)
	})
}

func (s *Spinner) loop() {
	defer s.wait.Done()
	frames := []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}
	ticker := time.NewTicker(80 * time.Millisecond)
	defer ticker.Stop()
	index := 0
	for {
		fmt.Fprintf(
			s.writer,
			"\r\033[2K%s %s",
			s.theme.Render(s.theme.Accent, frames[index]),
			s.label,
		)
		select {
		case <-s.done:
			return
		case <-ticker.C:
			index = (index + 1) % len(frames)
		}
	}
}
