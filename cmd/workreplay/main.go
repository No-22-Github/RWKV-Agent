// Command workreplay replays teacher-authored tool trajectories against the
// frozen work-v1 tool implementations with real execution receipts.
//
// Subcommands:
//
//	init    --case <case.json> --session <dir>
//	call    --session <dir> --name <tool> --args '<json>'
//	finish  --session <dir> --answer '<text>' [--turn N] [--skip-answer]
//	replay  --case <case.json> --session <dir> --calls <calls.json> --answer '<text>'
//
// `call` executes one tool invocation against the session workspace and
// prints the receipt payload ({"ok":true,...} or the ok:false error form) as
// JSON on stdout. `finish` evaluates the answer expectation and the
// case-level end state and writes result.json. `replay` runs init + a whole
// call list + finish in one shot; calls.json is a JSON array of
// {"name":...,"arguments":{...}}.
package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"time"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/eval"
)

type receipt struct {
	Index    int             `json:"index"`
	Name     string          `json:"name"`
	Args     json.RawMessage `json:"arguments"`
	OK       bool            `json:"ok"`
	Result   any             `json:"result,omitempty"`
	Error    string          `json:"error,omitempty"`
	Rejected string          `json:"rejected,omitempty"`
	// Payload carries the exact toolResult JSON bytes the harness would feed
	// into the transcript ({ok,tool,result/error} in that field order), so
	// the corpus renderer embeds receipts without reserializing them.
	Payload string `json:"payload"`
}

// toolResultPayload mirrors agent.toolResult's field order and JSON shape.
type toolResultPayload struct {
	OK     bool   `json:"ok"`
	Tool   string `json:"tool"`
	Result any    `json:"result,omitempty"`
	Error  string `json:"error,omitempty"`
}

type sessionState struct {
	ToolCatalogHash string    `json:"tool_catalog_hash"`
	Calls           []receipt `json:"calls"`
	FinalAnswer     string    `json:"final_answer,omitempty"`
}

func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	var err error
	switch os.Args[1] {
	case "init":
		err = cmdInit(os.Args[2:])
	case "call":
		err = cmdCall(os.Args[2:])
	case "finish":
		err = cmdFinish(os.Args[2:])
	case "replay":
		err = cmdReplay(os.Args[2:])
	default:
		usage()
		os.Exit(2)
	}
	if err != nil {
		fmt.Fprintf(os.Stderr, "workreplay: %v\n", err)
		os.Exit(1)
	}
}

func usage() {
	fmt.Fprint(os.Stderr, "usage: workreplay init|call|finish|replay [flags]\n")
}

func loadCase(path string) (eval.Case, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return eval.Case{}, err
	}
	var testCase eval.Case
	if err := json.Unmarshal(data, &testCase); err != nil {
		return eval.Case{}, fmt.Errorf("parse case %s: %w", path, err)
	}
	if testCase.ID == "" {
		return eval.Case{}, fmt.Errorf("case %s has no id", path)
	}
	return testCase, nil
}

func materializeWorkspace(sessionDir string, testCase eval.Case) (string, error) {
	workspace := filepath.Join(sessionDir, "workspace")
	if err := os.MkdirAll(workspace, 0o700); err != nil {
		return "", err
	}
	for path, content := range testCase.Files {
		target := filepath.Join(workspace, filepath.FromSlash(path))
		if err := os.MkdirAll(filepath.Dir(target), 0o700); err != nil {
			return "", err
		}
		if err := os.WriteFile(target, []byte(content), 0o600); err != nil {
			return "", err
		}
	}
	return workspace, nil
}

func buildCatalog(workspace string, testCase eval.Case) ([]agent.Tool, string, error) {
	catalog, err := eval.BuildWorkCatalogForCase(workspace, testCase)
	if err != nil {
		return nil, "", err
	}
	return catalog, eval.WorkCatalogHashFor(catalog), nil
}

func cmdInit(args []string) error {
	return runInit(args, false)
}

func runInit(args []string, quiet bool) error {
	fs := flag.NewFlagSet("init", flag.ContinueOnError)
	casePath := fs.String("case", "", "case json file")
	session := fs.String("session", "", "session directory")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *casePath == "" || *session == "" {
		return fmt.Errorf("init requires --case and --session")
	}
	testCase, err := loadCase(*casePath)
	if err != nil {
		return err
	}
	if err := os.RemoveAll(*session); err != nil {
		return err
	}
	if err := os.MkdirAll(*session, 0o700); err != nil {
		return err
	}
	workspace, err := materializeWorkspace(*session, testCase)
	if err != nil {
		return err
	}
	_, hash, err := buildCatalog(workspace, testCase)
	if err != nil {
		return err
	}
	caseCopy, err := os.ReadFile(*casePath)
	if err != nil {
		return err
	}
	if err := os.WriteFile(filepath.Join(*session, "case.json"), caseCopy, 0o600); err != nil {
		return err
	}
	state := sessionState{ToolCatalogHash: hash, Calls: []receipt{}}
	if err := saveState(*session, state); err != nil {
		return err
	}
	if quiet {
		return nil
	}
	return printJSON(map[string]any{
		"status":            "initialized",
		"session":           *session,
		"tool_catalog_hash": hash,
		"files":             sortedKeys(testCase.Files),
	})
}

func cmdCall(args []string) error {
	fs := flag.NewFlagSet("call", flag.ContinueOnError)
	session := fs.String("session", "", "session directory")
	name := fs.String("name", "", "tool name")
	arguments := fs.String("args", "{}", "arguments json")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *session == "" || *name == "" {
		return fmt.Errorf("call requires --session and --name")
	}
	receipt, err := execCall(*session, *name, *arguments)
	if err != nil {
		return err
	}
	return printJSON(receipt)
}

func execCall(session, name, arguments string) (receipt, error) {
	var argAny any
	if len(arguments) > 0 {
		if err := json.Unmarshal([]byte(arguments), &argAny); err != nil {
			return receipt{}, fmt.Errorf("arguments must be valid json: %w", err)
		}
	}
	state, err := loadState(session)
	if err != nil {
		return receipt{}, err
	}
	testCase, err := loadCase(filepath.Join(session, "case.json"))
	if err != nil {
		return receipt{}, err
	}
	workspace := filepath.Join(session, "workspace")
	catalog, _, err := buildCatalog(workspace, testCase)
	if err != nil {
		return receipt{}, err
	}
	call := receipt{
		Index: len(state.Calls),
		Name:  name,
		Args:  json.RawMessage(arguments),
	}
	value, execErr := eval.ExecuteWorkCall(catalog, name, []byte(arguments))
	payload := toolResultPayload{OK: execErr == nil, Tool: name}
	if execErr != nil {
		payload.Error = execErr.Error()
		call.OK = false
		call.Error = execErr.Error()
	} else {
		payload.Result = value
		call.OK = true
		call.Result = value
	}
	encoded, err := json.Marshal(payload)
	if err != nil {
		return receipt{}, fmt.Errorf("encode tool result: %w", err)
	}
	call.Payload = string(encoded)
	state.Calls = append(state.Calls, call)
	if err := saveState(session, state); err != nil {
		return receipt{}, err
	}
	return call, nil
}

func cmdFinish(args []string) error {
	result, err := runFinish(args)
	if err != nil {
		return err
	}
	return printJSON(result)
}

func runFinish(args []string) (map[string]any, error) {
	fs := flag.NewFlagSet("finish", flag.ContinueOnError)
	session := fs.String("session", "", "session directory")
	answer := fs.String("answer", "", "final answer text")
	turn := fs.Int("turn", 0, "turn index whose expectation scores the answer")
	skipAnswer := fs.Bool("skip-answer", false, "do not score an answer expectation")
	if err := fs.Parse(args); err != nil {
		return nil, err
	}
	if *session == "" {
		return nil, fmt.Errorf("finish requires --session")
	}
	state, err := loadState(*session)
	if err != nil {
		return nil, err
	}
	testCase, err := loadCase(filepath.Join(*session, "case.json"))
	if err != nil {
		return nil, err
	}
	workspace := filepath.Join(*session, "workspace")
	counts := map[string]int{}
	for _, call := range state.Calls {
		if call.Rejected == "" {
			counts[call.Name]++
		}
	}
	caseFailures := eval.CheckCaseExpect(context.Background(), workspace, testCase, counts)
	var answerFailures []string
	if !*skipAnswer && *turn < len(testCase.Turns) {
		answerFailures = eval.CheckAnswerExpect(testCase.Turns[*turn].Expect, *answer)
	}
	artifactHashes := map[string]string{}
	err = filepath.Walk(workspace, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() {
			return nil
		}
		rel, err := filepath.Rel(workspace, path)
		if err != nil {
			return err
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		sum := sha256.Sum256(data)
		artifactHashes[filepath.ToSlash(rel)] = hex.EncodeToString(sum[:])
		return nil
	})
	if err != nil {
		return nil, err
	}
	state.FinalAnswer = *answer
	if err := saveState(*session, state); err != nil {
		return nil, err
	}
	passed := len(caseFailures) == 0 && len(answerFailures) == 0
	result := map[string]any{
		"passed":          passed,
		"case_failures":   caseFailures,
		"answer_failures": answerFailures,
		"tool_counts":     counts,
		"final_answer":    *answer,
		"artifact_hashes": artifactHashes,
		"finished_at":     time.Now().UTC().Format(time.RFC3339),
	}
	if err := writeSessionJSON(*session, "result.json", result); err != nil {
		return nil, err
	}
	return result, nil
}

func cmdReplay(args []string) error {
	fs := flag.NewFlagSet("replay", flag.ContinueOnError)
	casePath := fs.String("case", "", "case json file")
	session := fs.String("session", "", "session directory")
	callsPath := fs.String("calls", "", "calls json array file")
	answer := fs.String("answer", "", "final answer text")
	if err := fs.Parse(args); err != nil {
		return err
	}
	if *casePath == "" || *session == "" || *callsPath == "" {
		return fmt.Errorf("replay requires --case, --session and --calls")
	}
	data, err := os.ReadFile(*callsPath)
	if err != nil {
		return err
	}
	var calls []eval.ReplayCall
	if err := json.Unmarshal(data, &calls); err != nil {
		return fmt.Errorf("parse calls: %w", err)
	}
	if err := runInit([]string{"--case", *casePath, "--session", *session}, true); err != nil {
		return err
	}
	for _, call := range calls {
		argsJSON := "{}"
		if len(call.Arguments) > 0 {
			argsJSON = string(call.Arguments)
		}
		receipt, err := execCall(*session, call.Name, argsJSON)
		if err != nil {
			return err
		}
		if !receipt.OK {
			fmt.Fprintf(os.Stderr, "call %d %s failed: %s\n", receipt.Index, receipt.Name, receipt.Error)
		}
	}
	result, err := runFinish([]string{"--session", *session, "--answer", *answer})
	if err != nil {
		return err
	}
	return printJSON(result)
}

func sortedKeys(m map[string]string) []string {
	keys := make([]string, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

func saveState(session string, state sessionState) error {
	return writeSessionJSON(session, "state.json", state)
}

func loadState(session string) (sessionState, error) {
	data, err := os.ReadFile(filepath.Join(session, "state.json"))
	if err != nil {
		return sessionState{}, err
	}
	var state sessionState
	if err := json.Unmarshal(data, &state); err != nil {
		return sessionState{}, err
	}
	return state, nil
}

func writeSessionJSON(session, name string, value any) error {
	data, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(filepath.Join(session, name), data, 0o600)
}

func printJSON(value any) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	fmt.Println(string(data))
	return nil
}

var _ = strings.TrimSpace
var _ io.Writer = os.Stderr
