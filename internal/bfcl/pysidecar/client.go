package pysidecar

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"os/exec"
	"strings"
	"sync"
	"sync/atomic"
)

type Config struct {
	Python     string
	Script     string
	WorkingDir string
}

// lockedBuffer is written by the exec package's copy goroutine and read by
// processError, so it needs its own lock rather than relying on Client.mu.
type lockedBuffer struct {
	mu     sync.Mutex
	buffer bytes.Buffer
}

func (locked *lockedBuffer) Write(data []byte) (int, error) {
	locked.mu.Lock()
	defer locked.mu.Unlock()
	return locked.buffer.Write(data)
}

func (locked *lockedBuffer) String() string {
	locked.mu.Lock()
	defer locked.mu.Unlock()
	return locked.buffer.String()
}

type Client struct {
	command *exec.Cmd
	stdin   io.WriteCloser
	encoder *json.Encoder
	decoder *json.Decoder
	stderr  lockedBuffer
	mu      sync.Mutex
	nextID  atomic.Uint64
	closed  bool
}

type request struct {
	RequestID     uint64         `json:"request_id"`
	Operation     string         `json:"op"`
	SessionID     string         `json:"sid,omitempty"`
	InitialConfig map[string]any `json:"initial_config,omitempty"`
	Classes       []string       `json:"involved_classes,omitempty"`
	LongContext   bool           `json:"long_context,omitempty"`
	TestEntryID   string         `json:"test_entry_id,omitempty"`
	Calls         []string       `json:"calls,omitempty"`
	Prompt        string         `json:"prompt,omitempty"`
	Vocab         string         `json:"vocab,omitempty"`
}

type response struct {
	RequestID   uint64   `json:"request_id"`
	OK          bool     `json:"ok"`
	SessionID   string   `json:"sid,omitempty"`
	Results     []string `json:"results,omitempty"`
	Tokens      int      `json:"tokens,omitempty"`
	VocabSHA256 string   `json:"vocab_sha256,omitempty"`
	Error       string   `json:"error,omitempty"`
}

type SessionOptions struct {
	ID              string
	InitialConfig   map[string]any
	InvolvedClasses []string
	LongContext     bool
	TestEntryID     string
}

func Start(config Config) (*Client, error) {
	if strings.TrimSpace(config.Python) == "" || strings.TrimSpace(config.Script) == "" {
		return nil, fmt.Errorf("BFCL sidecar python and script are required")
	}
	command := exec.Command(config.Python, "-u", config.Script)
	command.Dir = config.WorkingDir
	stdin, err := command.StdinPipe()
	if err != nil {
		return nil, fmt.Errorf("open BFCL sidecar stdin: %w", err)
	}
	stdout, err := command.StdoutPipe()
	if err != nil {
		stdin.Close()
		return nil, fmt.Errorf("open BFCL sidecar stdout: %w", err)
	}
	client := &Client{
		command: command,
		stdin:   stdin,
		encoder: json.NewEncoder(stdin),
		decoder: json.NewDecoder(bufio.NewReader(stdout)),
	}
	command.Stderr = &client.stderr
	if err := command.Start(); err != nil {
		stdin.Close()
		return nil, fmt.Errorf("start BFCL sidecar: %w", err)
	}
	return client, nil
}

func (client *Client) NewSession(ctx context.Context, options SessionOptions) (string, error) {
	if strings.TrimSpace(options.ID) == "" || len(options.InvolvedClasses) == 0 {
		return "", fmt.Errorf("BFCL sidecar session ID and involved classes are required")
	}
	answer, err := client.call(ctx, request{
		Operation:     "new",
		SessionID:     options.ID,
		InitialConfig: options.InitialConfig,
		Classes:       append([]string(nil), options.InvolvedClasses...),
		LongContext:   options.LongContext,
		TestEntryID:   options.TestEntryID,
	})
	if err != nil {
		return "", err
	}
	return answer.SessionID, nil
}

func (client *Client) Execute(ctx context.Context, sessionID string, calls []string) ([]string, error) {
	answer, err := client.call(ctx, request{
		Operation: "execute",
		SessionID: sessionID,
		Calls:     append([]string(nil), calls...),
	})
	if err != nil {
		return nil, err
	}
	return answer.Results, nil
}

// CountTokens measures a prompt with the same RWKV tokenizer the E5 context
// census used, so the runtime guard and the feasibility set share one unit.
// Returns the token count and the vocabulary SHA-256 for the manifest.
func (client *Client) CountTokens(ctx context.Context, vocab, prompt string) (int, string, error) {
	answer, err := client.call(ctx, request{Operation: "count_tokens", Vocab: vocab, Prompt: prompt})
	if err != nil {
		return 0, "", err
	}
	return answer.Tokens, answer.VocabSHA256, nil
}

func (client *Client) CloseSession(ctx context.Context, sessionID string) error {
	_, err := client.call(ctx, request{Operation: "close", SessionID: sessionID})
	return err
}

func (client *Client) call(ctx context.Context, value request) (response, error) {
	client.mu.Lock()
	defer client.mu.Unlock()
	if err := ctx.Err(); err != nil {
		return response{}, err
	}
	if client.closed {
		return response{}, fmt.Errorf("BFCL sidecar is closed")
	}
	value.RequestID = client.nextID.Add(1)
	if err := client.encoder.Encode(value); err != nil {
		return response{}, client.processError("write request", err)
	}
	var answer response
	if err := client.decoder.Decode(&answer); err != nil {
		return response{}, client.processError("read response", err)
	}
	if answer.RequestID != value.RequestID {
		return response{}, fmt.Errorf("BFCL sidecar response ID %d does not match request %d", answer.RequestID, value.RequestID)
	}
	if !answer.OK {
		return response{}, fmt.Errorf("BFCL sidecar: %s", answer.Error)
	}
	return answer, nil
}

func (client *Client) Close() error {
	client.mu.Lock()
	if client.closed {
		client.mu.Unlock()
		return nil
	}
	value := request{RequestID: client.nextID.Add(1), Operation: "shutdown"}
	encodeErr := client.encoder.Encode(value)
	var answer response
	decodeErr := client.decoder.Decode(&answer)
	client.closed = true
	stdinErr := client.stdin.Close()
	client.mu.Unlock()
	waitErr := client.command.Wait()
	if encodeErr != nil {
		return client.processError("write shutdown", encodeErr)
	}
	if decodeErr != nil {
		return client.processError("read shutdown", decodeErr)
	}
	if !answer.OK || answer.RequestID != value.RequestID {
		return fmt.Errorf("BFCL sidecar rejected shutdown: %s", answer.Error)
	}
	if stdinErr != nil {
		return stdinErr
	}
	if waitErr != nil {
		return client.processError("wait", waitErr)
	}
	return nil
}

func (client *Client) processError(action string, err error) error {
	detail := strings.TrimSpace(client.stderr.String())
	if detail == "" {
		return fmt.Errorf("BFCL sidecar %s: %w", action, err)
	}
	return fmt.Errorf("BFCL sidecar %s: %w: %s", action, err, detail)
}
