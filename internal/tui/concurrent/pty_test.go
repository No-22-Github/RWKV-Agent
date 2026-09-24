package concurrent

import (
	"bytes"
	"context"
	"errors"
	"io"
	"os"
	"sync"
	"testing"
	"time"

	"github.com/creack/pty"
	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
)

const (
	// ptyRunBudget bounds one full PTY interaction, so it has to stay larger
	// than the sum of the individual wait deadlines below: a loaded runner
	// that spends the whole wait budget must still have room to send the
	// scripted keys before the context expires.
	ptyRunBudget = 20 * time.Second
	// ptyWaitTimeout bounds a single wait for expected terminal output.
	ptyWaitTimeout = 5 * time.Second
	// ptyDrainTimeout bounds how long teardown waits for the TUI to release
	// the PTY before closing the descriptors anyway.
	ptyDrainTimeout = 5 * time.Second
)

// skipUnmaintainedPTYTUI skips the PTY-backed tests in this file.
//
// They drive a real PTY through bubbletea's shutdown path, which races
// os.File.Fd() against os.File.Close() inside bubbletea v2.0.8 and
// cancelreader v0.2.2: shutdown() only waits for the input read loop when
// Cancel() reports true and kill is false, so the loop can still be parked in
// epoll_wait() when the file is closed. Under -race any hit fails the build,
// and the same window sometimes wedges the program so Run never returns.
//
// Two of the three have flaked in CI on commits that cannot affect the TUI:
// TestPTYCancelKeysStopAllSessionsAndRestoreTerminal (run 34474776406) and
// TestPTYMouseSelectsPaneAndContinuesConversation (run 34084792180).
//
// The TUI is not in active use. Re-enable these if it is kept and the upstream
// race is fixed; layout_test.go covers the pure rendering logic and still runs.
func skipUnmaintainedPTYTUI(t *testing.T) {
	t.Helper()
	t.Skip("PTY TUI tests disabled: upstream bubbletea/cancelreader shutdown race")
}

func TestPTYAlternateScreenResizeAndCleanExit(t *testing.T) {
	skipUnmaintainedPTYTUI(t)
	t.Setenv("TERM", "xterm-256color")

	model := tuiMockModel(t, mock.Config{Output: "你好🙂", ChunkSize: 1})
	session := startPTYSession(t, model, 4, pty.Winsize{Cols: 120, Rows: 32})

	time.Sleep(150 * time.Millisecond)
	if err := pty.Setsize(session.master, &pty.Winsize{Cols: 80, Rows: 24}); err != nil {
		t.Fatal(err)
	}
	time.Sleep(150 * time.Millisecond)
	if _, err := session.master.Write([]byte("q")); err != nil {
		t.Fatal(err)
	}

	result := session.waitExit(t, "TUI")
	if result.err != nil {
		t.Fatal(result.err)
	}
	if result.summary.Sessions != 4 || result.summary.Cancelled {
		t.Fatalf("summary = %+v", result.summary)
	}
	session.stop(t)

	rendered := session.output.String()
	if !bytes.Contains([]byte(rendered), []byte("\033[?1049h")) {
		t.Fatalf("alternate-screen enter sequence missing: %q", rendered)
	}
	if !bytes.Contains([]byte(rendered), []byte("\033[?1049l")) {
		t.Fatalf("alternate-screen restore sequence missing: %q", rendered)
	}
}

func TestPTYCancelKeysStopAllSessionsAndRestoreTerminal(t *testing.T) {
	skipUnmaintainedPTYTUI(t)
	t.Setenv("TERM", "xterm-256color")

	tests := []struct {
		name string
		key  []byte
	}{
		{name: "q", key: []byte("q")},
		{name: "escape", key: []byte{0x1b}},
		{name: "control-c", key: []byte{0x03}},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			testPTYCancelKey(t, test.key)
		})
	}
}

func TestPTYMouseSelectsPaneAndContinuesConversation(t *testing.T) {
	skipUnmaintainedPTYTUI(t)
	t.Setenv("TERM", "xterm-256color")

	model := tuiMockModel(t, mock.Config{Output: "answer", ChunkSize: 1})
	session := startPTYSession(t, model, 1, pty.Winsize{Cols: 100, Rows: 24})

	waitForPTYOutput(t, session.output, "click/Enter continue")
	if _, err := session.master.Write([]byte("\033[<0;4;4M\033[<0;4;4m")); err != nil {
		t.Fatal(err)
	}
	waitForPTYOutput(t, session.output, "Ask")
	if _, err := session.master.Write([]byte("follow up\r")); err != nil {
		t.Fatal(err)
	}
	waitForPTYOutput(t, session.output, "12 tokens")
	// ctrl+c blurs the follow-up input so the next q reaches the top level.
	// A bare ESC would work too, but a terminal parser is free to read "ESC"
	// followed by another key as one alt+key sequence, which drops both and
	// leaves the TUI waiting for a quit that never arrives.
	if _, err := session.master.Write([]byte{0x03}); err != nil {
		t.Fatal(err)
	}
	time.Sleep(100 * time.Millisecond)
	if _, err := session.master.Write([]byte("q")); err != nil {
		t.Fatal(err)
	}

	result := session.waitExit(t, "mouse follow-up flow")
	if result.err != nil {
		t.Fatal(result.err)
	}
	if result.summary.Tokens != 12 {
		t.Fatalf("summary = %+v, want two 6-token answers", result.summary)
	}
	session.stop(t)

	rendered := session.output.String()
	if !bytes.Contains([]byte(rendered), []byte("follow up")) ||
		!bytes.Contains([]byte(rendered), []byte("You")) {
		t.Fatalf("follow-up transcript was not rendered: %q", rendered)
	}
}

func testPTYCancelKey(t *testing.T, key []byte) {
	t.Helper()
	started := make(chan struct{}, 4)
	model := tuiMockModel(t, mock.Config{
		Output:   "blocked",
		Started:  started,
		Continue: make(chan struct{}),
	})
	session := startPTYSession(t, model, 4, pty.Winsize{Cols: 100, Rows: 24})

	select {
	case <-started:
	case <-time.After(ptyWaitTimeout):
		t.Fatal("generation did not start")
	}
	if _, err := session.master.Write(key); err != nil {
		t.Fatal(err)
	}

	result := session.waitExit(t, "TUI")
	if !errors.Is(result.err, context.Canceled) {
		t.Fatalf("Run error = %v, want context.Canceled", result.err)
	}
	if !result.summary.Cancelled {
		t.Fatalf("summary = %+v, want cancelled", result.summary)
	}
	session.stop(t)

	if !bytes.Contains(session.output.Bytes(), []byte("\033[?1049l")) {
		t.Fatal("alternate screen was not restored after cancellation")
	}
}

type ptyResult struct {
	summary concurrentcli.Summary
	err     error
}

// ptySession owns one scripted TUI run over a PTY: it streams the terminal
// output into a buffer and drives Run on its own goroutine.
type ptySession struct {
	master   *os.File
	slave    *os.File
	output   *lockedBuffer
	finished chan ptyResult
	exited   chan struct{}
	cancel   context.CancelFunc
	readDone chan struct{}
	stopOnce sync.Once
}

func startPTYSession(t *testing.T, model inference.Model, concurrency int, size pty.Winsize) *ptySession {
	t.Helper()
	master, slave, err := pty.Open()
	if err != nil {
		t.Fatal(err)
	}
	if err := pty.Setsize(master, &size); err != nil {
		_ = master.Close()
		_ = slave.Close()
		t.Fatal(err)
	}

	session := &ptySession{
		master:   master,
		slave:    slave,
		output:   &lockedBuffer{},
		finished: make(chan ptyResult, 1),
		exited:   make(chan struct{}),
		readDone: make(chan struct{}),
	}
	go func() {
		_, _ = io.Copy(session.output, master)
		close(session.readDone)
	}()

	ctx, cancel := context.WithTimeout(context.Background(), ptyRunBudget)
	session.cancel = cancel
	go func() {
		defer close(session.exited)
		summary, runErr := Run(
			ctx,
			tuiRunnerFactory(model, concurrency),
			Metadata{Model: "mock", Provider: "mlx", Concurrency: concurrency},
			slave,
			slave,
		)
		session.finished <- ptyResult{summary: summary, err: runErr}
	}()

	t.Cleanup(func() { session.stop(t) })
	return session
}

// stop releases the PTY. It always waits for Run to return before closing the
// descriptors: bubbletea keeps reading the slave fd from its own goroutine, so
// closing it while the TUI is still running trips the race detector.
func (s *ptySession) stop(t *testing.T) {
	t.Helper()
	s.stopOnce.Do(func() {
		s.cancel()
		select {
		case <-s.exited:
		case <-time.After(ptyDrainTimeout):
		}
		_ = s.slave.Close()
		_ = s.master.Close()
		select {
		case <-s.readDone:
		case <-time.After(ptyDrainTimeout):
		}
	})
}

// waitExit blocks until the TUI returns or the run budget expires.
func (s *ptySession) waitExit(t *testing.T, what string) ptyResult {
	t.Helper()
	select {
	case result := <-s.finished:
		return result
	case <-time.After(ptyRunBudget):
		t.Fatalf("%s did not exit: %q", what, s.output.String())
		return ptyResult{}
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

func waitForPTYOutput(t *testing.T, output *lockedBuffer, text string) {
	t.Helper()
	deadline := time.Now().Add(ptyWaitTimeout)
	for time.Now().Before(deadline) {
		if bytes.Contains(output.Bytes(), []byte(text)) {
			return
		}
		time.Sleep(10 * time.Millisecond)
	}
	t.Fatalf("PTY output did not contain %q: %q", text, output.String())
}

func tuiRunnerFactory(model inference.Model, count int) RunnerFactory {
	return func() (*concurrentcli.Runner, error) {
		return concurrentcli.NewRunner(model, concurrentcli.Options{
			Conversation: conversation.Options{
				Profile:     inference.DefaultPromptProfile(false),
				NativeState: "off",
			},
			Turn: conversation.TurnOptions{
				Sampling: inference.SamplingOptions{
					Temperature: 1,
					TopK:        1,
					TopP:        1,
				},
				Limits: inference.GenerationLimits{MaxOutputTokens: 32},
			},
			Prompt:      "test",
			Concurrency: count,
			BaseSeed:    42,
		})
	}
}

func tuiMockModel(t *testing.T, config mock.Config) inference.Model {
	t.Helper()
	model, err := mock.New(config).LoadModel(
		context.Background(),
		inference.LoadRequest{Source: inference.ModelSource{Path: "tui.mock"}},
		nil,
	)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { _ = model.Close() })
	return model
}
