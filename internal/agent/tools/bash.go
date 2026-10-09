package tools

import (
	"bufio"
	"context"
	"crypto/sha256"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// The bash tool runs commands in just-bash, a TypeScript bash interpreter
// with its own builtin coreutils (grep, sed, awk, jq, find, sort, tar, ...),
// compiled with Bun into a single sidecar binary (native/justbash,
// scripts/build-justbash.sh). The workspace is mounted read-write at
// /workspace, which is also the cwd; everything outside it, /tmp included,
// is in memory and never touches the host. There is no network, no python
// and no host binaries.

const (
	// BashSidecarEnv overrides the sidecar binary location.
	BashSidecarEnv = "RWKV_JUSTBASH_SIDECAR"

	bashDefaultTimeout   = 20 * time.Second
	bashMaxCommandBytes  = 16 * 1024
	bashMaxStreamBytes   = 8 * 1024
	bashFingerprintLimit = 5000
)

// ErrBashSidecarMissing reports that no sidecar binary was found.
var ErrBashSidecarMissing = errors.New("bash sidecar binary not found; run scripts/build-justbash.sh")

// BashOptions configures the bash tool for one workspace.
type BashOptions struct {
	Workspace string
	// Sidecar is the just-bash sidecar binary; empty resolves it through
	// ResolveBashSidecar.
	Sidecar string
	Timeout time.Duration
}

// ResolveBashSidecar finds the sidecar binary: the explicit path, then
// $RWKV_JUSTBASH_SIDECAR, then justbash-sidecar beside the running
// executable, then local/bin/justbash-sidecar under the working directory.
func ResolveBashSidecar(explicit string) (string, error) {
	candidates := []string{strings.TrimSpace(explicit), strings.TrimSpace(os.Getenv(BashSidecarEnv))}
	if executable, err := os.Executable(); err == nil {
		candidates = append(candidates, filepath.Join(filepath.Dir(executable), "justbash-sidecar"))
	}
	candidates = append(candidates, filepath.Join("local", "bin", "justbash-sidecar"))
	for _, candidate := range candidates {
		if candidate == "" {
			continue
		}
		if info, err := os.Stat(candidate); err == nil && !info.IsDir() {
			return filepath.Abs(candidate)
		}
	}
	return "", ErrBashSidecarMissing
}

// BashTools returns the bash tool bound to one workspace.
func BashTools(options BashOptions) ([]agent.Tool, error) {
	root, err := filepath.Abs(strings.TrimSpace(options.Workspace))
	if err != nil || strings.TrimSpace(options.Workspace) == "" {
		return nil, fmt.Errorf("bash tool needs a workspace directory")
	}
	if resolved, err := filepath.EvalSymlinks(root); err == nil {
		root = resolved
	}
	sidecar, err := ResolveBashSidecar(options.Sidecar)
	if err != nil {
		return nil, err
	}
	timeout := options.Timeout
	if timeout <= 0 {
		timeout = bashDefaultTimeout
	}
	return []agent.Tool{&bashTool{root: root, sidecar: sidecar, timeout: timeout}}, nil
}

type bashTool struct {
	root    string
	sidecar string
	timeout time.Duration
}

// BashResult is what the model sees. Output streams are capped; a capped
// stream says so, and how much was dropped, so the model can narrow the
// command (head, grep, wc) instead of trusting a partial listing.
type BashResult struct {
	ExitCode int    `json:"exit_code"`
	Stdout   string `json:"stdout"`
	Stderr   string `json:"stderr,omitempty"`
	changed  bool
}

func (r BashResult) WorkspaceChanged() bool { return r.changed }

func (*bashTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name: "bash",
		Description: "Run a bash command in a sandbox at /workspace (no network, python or node) and return exit_code, stdout and stderr. " +
			"Supports pipes, redirection, loops and common Unix tools: ls, cat, head, tail, grep, rg, sed, awk, sort, uniq, wc, cut, tr, find, xargs, jq, yq, diff, tar, gzip, base64, sha256sum, date, seq. " +
			"Each call starts in /workspace and does not keep cd or variables from earlier calls.",
		Arguments: `{"command":"bash command line"}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"command":{"type":"string","minLength":1,"description":"Bash command line; multiple commands may be joined with ; && | or newlines."}
			},
			"required":["command"],
			"additionalProperties":false
		}`),
		Strict:           true,
		Bundle:           agent.ToolBundleWorkspace,
		Permission:       agent.PermissionWorkspaceWrite,
		MutatesWorkspace: true,
		Example:          `{"command":"grep -rn TODO src | head -20"}`,
	}
}

func (t *bashTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Command string `json:"command"`
	}
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if strings.TrimSpace(args.Command) == "" {
		return nil, invalidArguments("command is required")
	}
	if len(args.Command) > bashMaxCommandBytes {
		return nil, invalidArguments("command is longer than %d bytes; write long content with write_file", bashMaxCommandBytes)
	}
	client, err := sharedBashSidecar(t.sidecar)
	if err != nil {
		return nil, err
	}
	before := workspaceFingerprint(t.root)
	response, err := client.run(ctx, bashSidecarRequest{
		Root: t.root, Command: args.Command, TimeoutMillis: int(t.timeout / time.Millisecond),
	}, t.timeout+5*time.Second)
	if err != nil {
		return nil, err
	}
	if response.Error != "" {
		return nil, fmt.Errorf("bash: %s", response.Error)
	}
	return BashResult{
		ExitCode: response.ExitCode,
		Stdout:   capBashStream(response.Stdout),
		Stderr:   capBashStream(response.Stderr),
		changed:  workspaceFingerprint(t.root) != before,
	}, nil
}

func capBashStream(text string) string {
	if len(text) <= bashMaxStreamBytes {
		return text
	}
	cut := bashMaxStreamBytes
	for cut > 0 && !utf8RuneStart(text[cut]) {
		cut--
	}
	return text[:cut] + fmt.Sprintf("\n... [output truncated: %d more bytes; narrow the command with head, grep or wc]", len(text)-cut)
}

func utf8RuneStart(b byte) bool { return b&0xC0 != 0x80 }

// workspaceFingerprint hashes path, size and mtime of every workspace entry
// so the runner learns whether a command changed files (duplicate policy:
// repeating a read after a real change is legitimate).
func workspaceFingerprint(root string) string {
	digest := sha256.New()
	count := 0
	_ = filepath.WalkDir(root, func(path string, entry fs.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		count++
		if count > bashFingerprintLimit {
			return filepath.SkipAll
		}
		info, infoErr := entry.Info()
		if infoErr != nil {
			return nil
		}
		fmt.Fprintf(digest, "%s\x00%d\x00%d\x00", path, info.Size(), info.ModTime().UnixNano())
		return nil
	})
	return string(digest.Sum(nil))
}

type bashSidecarRequest struct {
	ID            int64  `json:"id"`
	Root          string `json:"root"`
	Command       string `json:"command"`
	TimeoutMillis int    `json:"timeout_ms"`
}

type bashSidecarResponse struct {
	ID       int64  `json:"id"`
	Stdout   string `json:"stdout"`
	Stderr   string `json:"stderr"`
	ExitCode int    `json:"exit_code"`
	Error    string `json:"error"`
}

// bashSidecar is one long-lived sidecar process shared by every bash tool
// using the same binary; requests are multiplexed by id. A dead process is
// replaced on the next call.
type bashSidecar struct {
	binary string

	mu      sync.Mutex
	stdin   io.WriteCloser
	waiting map[int64]chan bashSidecarResponse
	nextID  int64
	alive   bool
}

var (
	bashSidecarsMu sync.Mutex
	bashSidecars   = map[string]*bashSidecar{}
)

func sharedBashSidecar(binary string) (*bashSidecar, error) {
	bashSidecarsMu.Lock()
	defer bashSidecarsMu.Unlock()
	client, ok := bashSidecars[binary]
	if !ok {
		client = &bashSidecar{binary: binary}
		bashSidecars[binary] = client
	}
	client.mu.Lock()
	defer client.mu.Unlock()
	if !client.alive {
		if err := client.startLocked(); err != nil {
			return nil, err
		}
	}
	return client, nil
}

func (s *bashSidecar) startLocked() error {
	command := exec.Command(s.binary)
	command.Env = []string{"PATH=/usr/bin:/bin", "HOME=" + os.TempDir()}
	stdin, err := command.StdinPipe()
	if err != nil {
		return err
	}
	stdout, err := command.StdoutPipe()
	if err != nil {
		return err
	}
	command.Stderr = io.Discard
	if err := command.Start(); err != nil {
		return fmt.Errorf("start bash sidecar: %w", err)
	}
	s.stdin = stdin
	s.waiting = map[int64]chan bashSidecarResponse{}
	s.alive = true
	waiting := s.waiting
	go func() {
		scanner := bufio.NewScanner(stdout)
		scanner.Buffer(make([]byte, 0, 64*1024), 64*1024*1024)
		for scanner.Scan() {
			var response bashSidecarResponse
			if json.Unmarshal(scanner.Bytes(), &response) != nil {
				continue
			}
			s.mu.Lock()
			channel := waiting[response.ID]
			delete(waiting, response.ID)
			s.mu.Unlock()
			if channel != nil {
				channel <- response
			}
		}
		_ = command.Wait()
		s.mu.Lock()
		if s.stdin == stdin {
			s.alive = false
		}
		for id, channel := range waiting {
			delete(waiting, id)
			channel <- bashSidecarResponse{ID: id, Error: "sidecar exited"}
		}
		s.mu.Unlock()
	}()
	return nil
}

func (s *bashSidecar) run(ctx context.Context, request bashSidecarRequest, deadline time.Duration) (bashSidecarResponse, error) {
	channel := make(chan bashSidecarResponse, 1)
	s.mu.Lock()
	if !s.alive {
		if err := s.startLocked(); err != nil {
			s.mu.Unlock()
			return bashSidecarResponse{}, err
		}
	}
	s.nextID++
	request.ID = s.nextID
	s.waiting[request.ID] = channel
	line, _ := json.Marshal(request)
	_, err := s.stdin.Write(append(line, '\n'))
	if err != nil {
		delete(s.waiting, request.ID)
		s.alive = false
		s.mu.Unlock()
		return bashSidecarResponse{}, fmt.Errorf("bash sidecar: %w", err)
	}
	s.mu.Unlock()
	timer := time.NewTimer(deadline)
	defer timer.Stop()
	select {
	case response := <-channel:
		return response, nil
	case <-timer.C:
		s.forget(request.ID)
		return bashSidecarResponse{}, fmt.Errorf("bash: command timed out after %s", deadline-5*time.Second)
	case <-ctx.Done():
		s.forget(request.ID)
		return bashSidecarResponse{}, ctx.Err()
	}
}

func (s *bashSidecar) forget(id int64) {
	s.mu.Lock()
	delete(s.waiting, id)
	s.mu.Unlock()
}
