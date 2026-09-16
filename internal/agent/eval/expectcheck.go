package eval

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// evaluateCaseExpect scores the v5 case-level end state against the final
// workspace: expect.files, expect.run and expect.max_calls. It also folds the
// per-case intervention counters (H3) out of the embedded turn results.
// Failures land on CaseResult.Failures and flip Passed, mirroring turn-level
// validation; a workspace read error is a case error, not a model failure.
func evaluateCaseExpect(
	ctx context.Context,
	workspace string,
	testCase Case,
	result *CaseResult,
) {
	aggregateCaseInterventions(testCase, result)
	if testCase.Expect == nil {
		return
	}
	failures := make([]string, 0)
	failures = append(failures, fileExpectFailures(workspace, testCase)...)
	if runFailures, err := runExpectationScript(ctx, workspace, testCase); err != nil {
		result.Error = fmt.Sprintf("expect.run: %v", err)
		result.Passed = false
		return
	} else {
		failures = append(failures, runFailures...)
	}
	failures = append(failures, maxCallsFailures(testCase, result)...)
	if len(failures) > 0 {
		result.Failures = failures
		result.Passed = false
	}
}

// aggregateCaseInterventions folds the per-turn intervention counters out of
// the embedded agent results. Duplicate rejections count every model-issued
// call to the same tool, matching the ledger's loop_rate definition.
func aggregateCaseInterventions(testCase Case, result *CaseResult) {
	for _, turn := range result.Turns {
		runResult := turn.Result
		result.Rescues += boolToInt(runResult.RescueAttempted)
		result.RescueSubmits += boolToInt(runResult.RescueSubmitted)
		if runResult.ForcedAnswerReason != "" {
			result.ForcedAnswers++
		}
		for _, step := range runResult.Steps {
			if step.Tool != "" {
				result.ToolCalls++
				if step.ToolRejected != "" {
					result.DuplicateRejects++
				}
			}
			if step.ProtocolRepaired {
				result.ProtocolRepairs++
			}
		}
	}
	_ = testCase
}

func boolToInt(value bool) int {
	if value {
		return 1
	}
	return 0
}

func fileExpectFailures(workspace string, testCase Case) []string {
	expect := testCase.Expect
	if expect == nil || len(expect.Files) == 0 {
		return nil
	}
	var failures []string
	for path, fileExpect := range expect.Files {
		full := filepath.Join(workspace, filepath.FromSlash(path))
		content, err := os.ReadFile(full)
		if err != nil {
			if fileExpect.Absent && os.IsNotExist(err) {
				continue
			}
			failures = append(failures, fmt.Sprintf(
				"expect.files %q unreadable: %v",
				path,
				err,
			))
			continue
		}
		switch {
		case fileExpect.Absent:
			failures = append(failures, fmt.Sprintf("expect.files %q must be absent", path))
		case fileExpect.Unchanged:
			initial, ok := testCase.Files[path]
			if !ok || string(content) != initial {
				failures = append(failures, fmt.Sprintf(
					"expect.files %q changed from the initial fixture",
					path,
				))
			}
		case fileExpect.Equals != nil:
			if string(content) != *fileExpect.Equals {
				failures = append(failures, fmt.Sprintf(
					"expect.files %q does not equal the expected content",
					path,
				))
			}
		default:
			for _, needle := range fileExpect.Contains {
				if !strings.Contains(string(content), needle) {
					failures = append(failures, fmt.Sprintf(
						"expect.files %q is missing required content %q",
						path,
						needle,
					))
				}
			}
		}
	}
	return failures
}

// runExpectationScript executes the bank script offline against a copy of the
// final workspace: python3 -I -S, hard timeout (default 10s), stdout compared
// line by line after stripping trailing \r. The sandbox root holds workspace/
// (the copy) plus hidden/ (HiddenFiles) for second-input scripts. The script
// never runs against the live workspace, so a broken script cannot corrupt
// other checks.
func runExpectationScript(
	parent context.Context,
	workspace string,
	testCase Case,
) ([]string, error) {
	expect := testCase.Expect
	if expect == nil || expect.Run == nil {
		return nil, nil
	}
	run := expect.Run
	sandbox, err := os.MkdirTemp("", "rwkv-agent-expect-run-")
	if err != nil {
		return nil, err
	}
	defer os.RemoveAll(sandbox)
	runWorkspace := filepath.Join(sandbox, "workspace")
	if err := copyDir(workspace, runWorkspace); err != nil {
		return nil, fmt.Errorf("copy workspace: %w", err)
	}
	for path, content := range run.HiddenFiles {
		target := filepath.Join(sandbox, filepath.FromSlash(path))
		if err := os.MkdirAll(filepath.Dir(target), 0o700); err != nil {
			return nil, err
		}
		if err := os.WriteFile(target, []byte(content), 0o600); err != nil {
			return nil, err
		}
	}
	timeout := time.Duration(run.TimeoutMillis) * time.Millisecond
	if timeout <= 0 {
		timeout = 10 * time.Second
	}
	ctx, cancel := context.WithTimeout(parent, timeout)
	defer cancel()
	scriptPath := filepath.Join(runWorkspace, filepath.FromSlash(run.Path))
	command := exec.CommandContext(ctx, "python3", append(
		[]string{"-I", "-S", scriptPath},
		run.Args...,
	)...)
	command.Dir = sandbox
	command.Env = []string{
		"PATH=/usr/bin:/bin:/usr/local/bin",
		"HOME=" + sandbox,
		"PYTHONDONTWRITEBYTECODE=1",
		"PYTHONHASHSEED=0",
	}
	var stdout, stderr bytes.Buffer
	command.Stdout = &stdout
	command.Stderr = &stderr
	if err := command.Run(); err != nil {
		return nil, fmt.Errorf(
			"script %s failed: %v; stderr: %s",
			run.Path,
			err,
			clipText(stderr.String(), 400),
		)
	}
	want := strings.Split(strings.ReplaceAll(run.ExpectedStdout, "\r\n", "\n"), "\n")
	got := strings.Split(strings.ReplaceAll(strings.TrimRight(stdout.String(), "\n"), "\r\n", "\n"), "\n")
	var failures []string
	for index := range want {
		if index >= len(got) {
			failures = append(failures, fmt.Sprintf(
				"expect.run stdout line %d missing: want %q",
				index+1,
				want[index],
			))
			continue
		}
		if strings.TrimRight(got[index], "\r") != want[index] {
			failures = append(failures, fmt.Sprintf(
				"expect.run stdout line %d = %q, want %q",
				index+1,
				got[index],
				want[index],
			))
		}
	}
	if len(got) > len(want) {
		failures = append(failures, fmt.Sprintf(
			"expect.run stdout has %d unexpected trailing lines (first: %q)",
			len(got)-len(want),
			got[len(want)],
		))
	}
	return failures, nil
}

// maxCallsFailures enforces expect.max_calls over the whole case: every
// model-issued call counts, including duplicate-rejected ones, so the
// duplicate guard cannot hide a loop behind a rejection.
func maxCallsFailures(testCase Case, result *CaseResult) []string {
	expect := testCase.Expect
	if expect == nil || len(expect.MaxCalls) == 0 {
		return nil
	}
	counts := make(map[string]int, len(expect.MaxCalls))
	for _, turn := range result.Turns {
		for _, step := range turn.Result.Steps {
			if step.Tool != "" {
				counts[step.Tool]++
			}
		}
	}
	var failures []string
	for tool, budget := range expect.MaxCalls {
		if counts[tool] > budget {
			failures = append(failures, fmt.Sprintf(
				"expect.max_calls: tool %q issued %d calls, budget %d",
				tool,
				counts[tool],
				budget,
			))
		}
	}
	return failures
}

func copyDir(source string, target string) error {
	return filepath.WalkDir(source, func(path string, entry os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		relative, err := filepath.Rel(source, path)
		if err != nil {
			return err
		}
		destination := filepath.Join(target, relative)
		if entry.IsDir() {
			return os.MkdirAll(destination, 0o700)
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		if err := os.MkdirAll(filepath.Dir(destination), 0o700); err != nil {
			return err
		}
		return os.WriteFile(destination, data, 0o600)
	})
}

func clipText(text string, limit int) string {
	if len(text) <= limit {
		return text
	}
	return text[:limit] + "..."
}
