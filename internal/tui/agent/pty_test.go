package agent

import (
	"bytes"
	"context"
	"errors"
	"io"
	"sync"
	"testing"
	"time"

	"github.com/creack/pty"
)

func TestPTYSubmitsFollowUpAndRestoresTerminal(t *testing.T) {
	t.Setenv("TERM", "xterm-256color")

	session := &fakeSession{}
	master, slave, err := pty.Open()
	if err != nil {
		t.Fatal(err)
	}
	defer master.Close()
	defer slave.Close()
	if err := pty.Setsize(master, &pty.Winsize{Cols: 100, Rows: 24}); err != nil {
		t.Fatal(err)
	}

	var output lockedBuffer
	readDone := make(chan struct{})
	go func() {
		_, _ = io.Copy(&output, master)
		close(readDone)
	}()

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	finished := make(chan struct {
		summary Summary
		err     error
	}, 1)
	go func() {
		summary, runErr := Run(
			ctx,
			session,
			Metadata{Model: "mock", Provider: "mlx", Workspace: "/tmp/example"},
			"first question",
			slave,
			slave,
		)
		finished <- struct {
			summary Summary
			err     error
		}{summary: summary, err: runErr}
	}()

	waitForOutput(t, &output, "answer: first question", 2*time.Second)
	if _, err := master.Write([]byte("follow up\r")); err != nil {
		t.Fatal(err)
	}
	waitForOutput(t, &output, "answer: follow up", 2*time.Second)
	if _, err := master.Write([]byte{0x1b}); err != nil {
		t.Fatal(err)
	}

	select {
	case result := <-finished:
		if result.err != nil {
			t.Fatal(result.err)
		}
		if result.summary.Tasks != 2 {
			t.Fatalf("summary = %+v", result.summary)
		}
	case <-ctx.Done():
		t.Fatalf("TUI did not exit: %q", output.String())
	}
	_ = slave.Close()
	_ = master.Close()
	<-readDone

	rendered := output.Bytes()
	if !bytes.Contains(rendered, []byte("\033[?1049h")) ||
		!bytes.Contains(rendered, []byte("\033[?1049l")) {
		t.Fatalf("alternate screen was not entered and restored: %q", rendered)
	}
}

type lockedBuffer struct {
	mu sync.Mutex
	bytes.Buffer
}

func (b *lockedBuffer) Write(value []byte) (int, error) {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.Buffer.Write(value)
}

func (b *lockedBuffer) ReadFrom(reader io.Reader) (int64, error) {
	buffer := make([]byte, 4096)
	var total int64
	for {
		count, err := reader.Read(buffer)
		if count > 0 {
			written, writeErr := b.Write(buffer[:count])
			total += int64(written)
			if writeErr != nil {
				return total, writeErr
			}
		}
		if err != nil {
			if errors.Is(err, io.EOF) {
				return total, nil
			}
			return total, err
		}
	}
}

func (b *lockedBuffer) String() string {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.Buffer.String()
}

func (b *lockedBuffer) Bytes() []byte {
	b.mu.Lock()
	defer b.mu.Unlock()
	return append([]byte(nil), b.Buffer.Bytes()...)
}

func waitForOutput(
	t *testing.T,
	output *lockedBuffer,
	text string,
	timeout time.Duration,
) {
	t.Helper()
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		if bytes.Contains(output.Bytes(), []byte(text)) {
			return
		}
		time.Sleep(10 * time.Millisecond)
	}
	t.Fatalf("PTY output did not contain %q: %q", text, output.String())
}
