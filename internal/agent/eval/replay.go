package eval

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// Replay-side exported API. The workspace-agent-700 corpus production replays
// teacher trajectories through the same frozen work-v1 tool implementations
// and the same expectation checks the harness uses; these wrappers expose the
// unexported internals without duplicating their semantics.

// ReplayCall is one teacher-selected tool call to execute.
type ReplayCall struct {
	Name      string          `json:"name"`
	Arguments json.RawMessage `json:"arguments"`
}

// BuildWorkCatalogForCase assembles the fixed work-v1 twelve-tool directory
// for a case workspace. Deterministic: fixed clock, fixture-backed web tools.
func BuildWorkCatalogForCase(workspace string, testCase Case) ([]agent.Tool, error) {
	return buildWorkToolCatalog(workspace, testCase.WebFixture, 0, nil)
}

// ExecuteWorkCall runs one call against the catalog and returns the raw tool
// value or error, exactly as the runner would hand them to the result payload.
func ExecuteWorkCall(catalog []agent.Tool, name string, args json.RawMessage) (any, error) {
	var tool agent.Tool
	for _, candidate := range catalog {
		if candidate.Spec().Name == name {
			tool = candidate
			break
		}
	}
	if tool == nil {
		return nil, &UnknownToolError{Name: name}
	}
	return tool.Execute(context.Background(), args)
}

// UnknownToolError reports a call outside the work-v1 catalog.
type UnknownToolError struct{ Name string }

func (e *UnknownToolError) Error() string {
	return "unknown tool " + e.Name
}

// CheckCaseExpect evaluates the v5 case-level end state (files, run,
// max_calls) against the final workspace. toolCounts maps tool name to the
// number of executed calls in the replayed trajectory.
func CheckCaseExpect(ctx context.Context, workspace string, testCase Case, toolCounts map[string]int) []string {
	if testCase.Expect == nil {
		return nil
	}
	failures := fileExpectFailures(workspace, testCase)
	if runFailures, err := runExpectationScript(ctx, workspace, testCase); err != nil {
		return append(failures, err.Error())
	} else {
		failures = append(failures, runFailures...)
	}
	for tool, budget := range testCase.Expect.MaxCalls {
		if toolCounts[tool] > budget {
			failures = append(failures, fmt.Sprintf(
				"expect.max_calls: tool %q issued %d calls, budget %d",
				tool, toolCounts[tool], budget,
			))
		}
	}
	return failures
}

// CheckAnswerExpect scores a final answer against a turn-level expectation
// using the frozen scorer semantics.
func CheckAnswerExpect(expect Expectation, output string) []string {
	return answerFailures(expect, output)
}

// WorkCatalogHashFor pins the exact schemas the model saw for the built
// catalog, matching the ledger comparability key.
func WorkCatalogHashFor(catalog []agent.Tool) string {
	return workToolCatalogHash(catalog)
}
