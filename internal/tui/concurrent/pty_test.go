package concurrent

import (
	"bytes"
	"context"
	"errors"
	"io"
	"sync"
	"testing"
	"time"

	"github.com/creack/pty"
	concurrentcli "github.com/no22/RWKV-Agent/internal/cli/concurrent"
	"github.com/no22/RWKV-Agent/internal/conversation"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/inference/backend/mock"
)

func TestPTYAlternateScreenResizeAndCleanExit(t *testing.T) {
	t.Setenv("TERM", "xterm-256color")

	model := tuiMockModel(t, mock.Config{Output: "你好🙂", ChunkSize: 1})
	factory := tuiRunnerFactory(model, 4)
	master, slave, err := pty.Open()
	if err != nil {
		t.Fatal(err)
	}
	defer master.Close()
	defer slave.Close()
	if err := pty.Setsize(master, &pty.Winsize{Cols: 120, Rows: 32}); err != nil {
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
		summary concurrentcli.Summary
		err     error
	}, 1)
	go func() {
		summary, runErr := Run(
			ctx,
			factory,
			Metadata{Model: "mock", Provider: "mlx", Concurrency: 4},
			slave,
			slave,
		)
		finished <- struct {
			summary concurrentcli.Summary
			err     error
		}{summary, runErr}
	}()

	time.Sleep(150 * time.Millisecond)
	if err := pty.Setsize(master, &pty.Winsize{Cols: 80, Rows: 24}); err != nil {
		t.Fatal(err)
	}
	time.Sleep(150 * time.Millisecond)
	if _, err := master.Write([]byte("q")); err != nil {
		t.Fatal(err)
	}

	select {
	case result := <-finished:
		if result.err != nil {
			t.Fatal(result.err)
		}
		if result.summary.Sessions != 4 || result.summary.Cancelled {
			t.Fatalf("summary = %+v", result.summary)
		}
	case <-ctx.Done():
		t.Fatal("TUI did not exit after q")
	}
	_ = slave.Close()
	_ = master.Close()
	<-readDone

	rendered := output.String()
	if !bytes.Contains([]byte(rendered), []byte("\033[?1049h")) {
		t.Fatalf("alternate-screen enter sequence missing: %q", rendered)
	}
	if !bytes.Contains([]byte(rendered), []byte("\033[?1049l")) {
		t.Fatalf("alternate-screen restore sequence missing: %q", rendered)
	}
}

func TestPTYCancelKeysStopAllSessionsAndRestoreTerminal(t *testing.T) {
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
	t.Setenv("TERM", "xterm-256color")

	model := tuiMockModel(t, mock.Config{Output: "answer", ChunkSize: 1})
	factory := tuiRunnerFactory(model, 1)
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
		summary concurrentcli.Summary
		err     error
	}, 1)
	go func() {
		summary, runErr := Run(
			ctx,
			factory,
			Metadata{Model: "mock", Provider: "mlx", Concurrency: 1},
			slave,
			slave,
		)
		finished <- struct {
			summary concurrentcli.Summary
			err     error
		}{summary, runErr}
	}()

	waitForPTYOutput(t, &output, "click/Enter continue", 2*time.Second)
	if _, err := master.Write([]byte("\033[<0;4;4M\033[<0;4;4m")); err != nil {
		t.Fatal(err)
	}
	waitForPTYOutput(t, &output, "Ask", 2*time.Second)
	if _, err := master.Write([]byte("follow up\r")); err != nil {
		t.Fatal(err)
	}
	waitForPTYOutput(t, &output, "12 tokens", 2*time.Second)
	if _, err := master.Write([]byte{0x1b}); err != nil {
		t.Fatal(err)
	}
	time.Sleep(50 * time.Millisecond)
	if _, err := master.Write([]byte("q")); err != nil {
		t.Fatal(err)
	}

	select {
	case result := <-finished:
		if result.err != nil {
			t.Fatal(result.err)
		}
		if result.summary.Tokens != 12 {
			t.Fatalf("summary = %+v, want two 6-token answers", result.summary)
		}
	case <-ctx.Done():
		t.Fatalf("mouse follow-up flow did not exit: %q", output.String())
	}
	_ = slave.Close()
	_ = master.Close()
	<-readDone
	rendered := output.String()
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
	factory := tuiRunnerFactory(model, 4)
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
		summary concurrentcli.Summary
		err     error
	}, 1)
	go func() {
		summary, runErr := Run(
			ctx,
			factory,
			Metadata{Model: "mock", Provider: "mlx", Concurrency: 4},
			slave,
			slave,
		)
		finished <- struct {
			summary concurrentcli.Summary
			err     error
		}{summary, runErr}
	}()

	select {
	case <-started:
	case <-ctx.Done():
		t.Fatal("generation did not start")
	}
	if _, err := master.Write(key); err != nil {
		t.Fatal(err)
	}
	select {
	case result := <-finished:
		if !errors.Is(result.err, context.Canceled) {
			t.Fatalf("Run error = %v, want context.Canceled", result.err)
		}
		if !result.summary.Cancelled {
			t.Fatalf("summary = %+v, want cancelled", result.summary)
		}
	case <-ctx.Done():
		t.Fatal("TUI did not exit after cancel key")
	}
	_ = slave.Close()
	_ = master.Close()
	<-readDone
	if !bytes.Contains(output.Bytes(), []byte("\033[?1049l")) {
		t.Fatal("alternate screen was not restored after cancellation")
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

func waitForPTYOutput(t *testing.T, output *lockedBuffer, text string, timeout time.Duration) {
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
