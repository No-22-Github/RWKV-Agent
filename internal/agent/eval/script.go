package eval

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"strings"
	"sync"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// A script replays teacher-authored assistant outputs through the real eval
// harness in place of a model. Every prompt byte, tool receipt, reminder,
// duplicate rejection and forced-answer block then comes from the same code
// path a benchmark run uses, so a corpus rendered from the resulting trace is
// byte-identical to what the model sees at eval time by construction.

// ScriptEntry is one case's teacher trajectory: the outputs its generations
// return, in order, across all of the case's turns.
type ScriptEntry struct {
	CaseID  string         `json:"case_id"`
	Outputs []ScriptOutput `json:"outputs"`
}

// ScriptOutput is one generation's raw text. Supervised is corpus metadata
// only (the generator ignores it): false marks a context-only action such as
// a recovery prefix whose span is not trained.
type ScriptOutput struct {
	Text       string `json:"text"`
	Supervised bool   `json:"supervised"`
}

// ErrScriptExhausted reports a generation the script did not author: the
// harness took a path the teacher did not plan for (an extra retry, a forced
// answer), so the trajectory cannot be rendered faithfully.
var ErrScriptExhausted = errors.New("script exhausted")

type caseIDKey struct{}

// WithCaseID attaches the running case ID so a per-case generator factory can
// select that case's material.
func WithCaseID(ctx context.Context, id string) context.Context {
	return context.WithValue(ctx, caseIDKey{}, id)
}

// CaseIDFromContext returns the case ID attached by WithCaseID.
func CaseIDFromContext(ctx context.Context) (string, bool) {
	id, ok := ctx.Value(caseIDKey{}).(string)
	return id, ok && id != ""
}

// LoadScript reads a JSONL script (one ScriptEntry per line). Blank lines are
// skipped; duplicate or empty case IDs are errors.
func LoadScript(path string) (map[string]ScriptEntry, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer file.Close()
	return decodeScript(file)
}

func decodeScript(reader io.Reader) (map[string]ScriptEntry, error) {
	entries := map[string]ScriptEntry{}
	scanner := bufio.NewScanner(reader)
	scanner.Buffer(make([]byte, 0, 1<<20), 64<<20)
	line := 0
	for scanner.Scan() {
		line++
		text := strings.TrimSpace(scanner.Text())
		if text == "" {
			continue
		}
		var entry ScriptEntry
		decoder := json.NewDecoder(strings.NewReader(text))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&entry); err != nil {
			return nil, fmt.Errorf("script line %d: %w", line, err)
		}
		if entry.CaseID == "" {
			return nil, fmt.Errorf("script line %d: empty case_id", line)
		}
		if len(entry.Outputs) == 0 {
			return nil, fmt.Errorf("script line %d: case %s has no outputs", line, entry.CaseID)
		}
		if _, dup := entries[entry.CaseID]; dup {
			return nil, fmt.Errorf("script line %d: duplicate case_id %s", line, entry.CaseID)
		}
		entries[entry.CaseID] = entry
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return entries, nil
}

// ScriptGeneratorFactory returns a factory whose per-case generator answers
// each generation with the case's next scripted output. A generation past the
// end of the script fails with ErrScriptExhausted rather than inventing text.
func ScriptGeneratorFactory(entries map[string]ScriptEntry) GeneratorFactory {
	return func(ctx context.Context) (continuation.Generator, io.Closer, error) {
		id, ok := CaseIDFromContext(ctx)
		if !ok {
			return nil, nil, errors.New("script generator: no case ID in context")
		}
		entry, ok := entries[id]
		if !ok {
			return nil, nil, fmt.Errorf("script generator: no script for case %s", id)
		}
		var mu sync.Mutex
		next := 0
		generator := continuation.GenerateFunc(func(
			_ context.Context,
			_ continuation.Request,
			_ continuation.EventSink,
		) (continuation.Result, error) {
			mu.Lock()
			defer mu.Unlock()
			if next >= len(entry.Outputs) {
				return continuation.Result{}, fmt.Errorf(
					"%w: case %s requested generation %d of %d",
					ErrScriptExhausted, id, next+1, len(entry.Outputs),
				)
			}
			output := entry.Outputs[next].Text
			next++
			return continuation.Result{Text: output, FinishReason: continuation.FinishStop}, nil
		})
		return generator, nil, nil
	}
}
