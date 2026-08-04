package eval

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"strings"
)

const maxCaseFileBytes = 4 << 20

var caseIDPattern = regexp.MustCompile(`^[a-z0-9][a-z0-9_-]{0,63}$`)

func LoadCases(path string) ([]Case, error) {
	handle, err := os.Open(path)
	if err != nil {
		return nil, err
	}
	defer handle.Close()
	data, err := io.ReadAll(io.LimitReader(handle, maxCaseFileBytes+1))
	if err != nil {
		return nil, err
	}
	if len(data) > maxCaseFileBytes {
		return nil, fmt.Errorf("case file exceeds %d bytes", maxCaseFileBytes)
	}
	return decodeCases(data)
}

func decodeCases(data []byte) ([]Case, error) {
	var value caseFile
	decoder := json.NewDecoder(strings.NewReader(string(data)))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&value); err != nil {
		return nil, fmt.Errorf("decode cases: %w", err)
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return nil, fmt.Errorf("decode cases: trailing JSON value")
	}
	if value.SchemaVersion != SchemaVersion {
		return nil, fmt.Errorf(
			"unsupported case schema version %d; expected %d",
			value.SchemaVersion,
			SchemaVersion,
		)
	}
	if err := ValidateCases(value.Cases); err != nil {
		return nil, err
	}
	return value.Cases, nil
}

func SelectCases(cases []Case, ids []string) ([]Case, error) {
	if len(ids) == 0 {
		return append([]Case(nil), cases...), nil
	}
	available := make(map[string]Case, len(cases))
	for _, testCase := range cases {
		available[testCase.ID] = testCase
	}
	selected := make([]Case, 0, len(ids))
	seen := make(map[string]struct{}, len(ids))
	for _, id := range ids {
		if _, duplicate := seen[id]; duplicate {
			return nil, fmt.Errorf("duplicate selected case %q", id)
		}
		testCase, ok := available[id]
		if !ok {
			return nil, fmt.Errorf("unknown eval case %q", id)
		}
		seen[id] = struct{}{}
		selected = append(selected, testCase)
	}
	return selected, nil
}

func ValidateCases(cases []Case) error {
	if len(cases) == 0 {
		return fmt.Errorf("at least one eval case is required")
	}
	seen := make(map[string]struct{}, len(cases))
	for _, testCase := range cases {
		if !caseIDPattern.MatchString(testCase.ID) {
			return fmt.Errorf("invalid eval case ID %q", testCase.ID)
		}
		if _, duplicate := seen[testCase.ID]; duplicate {
			return fmt.Errorf("duplicate eval case ID %q", testCase.ID)
		}
		seen[testCase.ID] = struct{}{}
		if strings.TrimSpace(testCase.Description) == "" {
			return fmt.Errorf("case %q requires a description", testCase.ID)
		}
		for path := range testCase.Files {
			if err := validateFixturePath(path); err != nil {
				return fmt.Errorf("case %q file %q: %w", testCase.ID, path, err)
			}
		}
		for path := range testCase.OutsideFiles {
			if err := validateFixturePath(path); err != nil {
				return fmt.Errorf("case %q outside file %q: %w", testCase.ID, path, err)
			}
			if firstPathPart(path) == "workspace" {
				return fmt.Errorf("case %q outside file cannot enter the workspace", testCase.ID)
			}
		}
		for _, name := range testCase.ProviderUnavailable {
			if strings.TrimSpace(name) == "" {
				return fmt.Errorf("case %q has an empty unavailable provider name", testCase.ID)
			}
		}
		if len(testCase.Turns) == 0 {
			return fmt.Errorf("case %q requires at least one turn", testCase.ID)
		}
		for index, turn := range testCase.Turns {
			if strings.TrimSpace(turn.Prompt) == "" {
				return fmt.Errorf("case %q turn %d requires a prompt", testCase.ID, index+1)
			}
			if turn.Expect.Route != "" &&
				turn.Expect.Route != "respond" &&
				turn.Expect.Route != "inspect" {
				return fmt.Errorf(
					"case %q turn %d has invalid route %q",
					testCase.ID,
					index+1,
					turn.Expect.Route,
				)
			}
			if turn.Expect.Tools == nil &&
				len(turn.Expect.RequiredTools) == 0 &&
				len(turn.Expect.ForbiddenTools) == 0 &&
				len(turn.Expect.RequiredCalls) == 0 {
				return fmt.Errorf(
					"case %q turn %d must declare exact, required, or forbidden tool expectations",
					testCase.ID,
					index+1,
				)
			}
			if turn.Expect.Tools != nil && len(turn.Expect.RequiredTools) > 0 {
				return fmt.Errorf(
					"case %q turn %d cannot combine tools with required_tools",
					testCase.ID,
					index+1,
				)
			}
			if err := validateToolSets(testCase.ID, index+1, turn.Expect); err != nil {
				return err
			}
			for _, call := range turn.Expect.Calls {
				if strings.TrimSpace(call.Name) == "" {
					return fmt.Errorf(
						"case %q turn %d has an expected call without a name",
						testCase.ID,
						index+1,
					)
				}
			}
			if len(turn.Expect.Calls) > len(turn.Expect.Tools) {
				return fmt.Errorf(
					"case %q turn %d declares more calls than tools",
					testCase.ID,
					index+1,
				)
			}
			for callIndex, call := range turn.Expect.Calls {
				if call.Name != turn.Expect.Tools[callIndex] {
					return fmt.Errorf(
						"case %q turn %d call %d does not match expected tool %q",
						testCase.ID,
						index+1,
						callIndex+1,
						turn.Expect.Tools[callIndex],
					)
				}
			}
			for _, call := range turn.Expect.RequiredCalls {
				if strings.TrimSpace(call.Name) == "" {
					return fmt.Errorf(
						"case %q turn %d has a required call without a name",
						testCase.ID,
						index+1,
					)
				}
			}
			if turn.Expect.ExpectedNumber != nil {
				if turn.Expect.OutputEquals != nil {
					return fmt.Errorf(
						"case %q turn %d cannot combine output_equals with expected_number",
						testCase.ID,
						index+1,
					)
				}
				if turn.Expect.Tolerance == nil || *turn.Expect.Tolerance < 0 {
					return fmt.Errorf(
						"case %q turn %d expected_number requires a non-negative tolerance",
						testCase.ID,
						index+1,
					)
				}
			} else if turn.Expect.Tolerance != nil {
				return fmt.Errorf(
					"case %q turn %d tolerance requires expected_number",
					testCase.ID,
					index+1,
				)
			}
			if plan := turn.Expect.Plan; plan != nil {
				if plan.SubtaskCount < 1 {
					return fmt.Errorf("case %q turn %d plan subtask_count must be positive", testCase.ID, index+1)
				}
				for _, reference := range plan.References {
					if reference.Subtask < 1 || strings.TrimSpace(reference.Argument) == "" || strings.TrimSpace(reference.Source) == "" {
						return fmt.Errorf("case %q turn %d has an invalid plan reference", testCase.ID, index+1)
					}
				}
			}
		}
	}
	return nil
}

func validateToolSets(caseID string, turn int, expect Expectation) error {
	required := make(map[string]struct{}, len(expect.RequiredTools))
	for _, name := range expect.RequiredTools {
		name = strings.TrimSpace(name)
		if name == "" {
			return fmt.Errorf("case %q turn %d has an empty required tool", caseID, turn)
		}
		if _, duplicate := required[name]; duplicate {
			return fmt.Errorf(
				"case %q turn %d repeats required tool %q",
				caseID,
				turn,
				name,
			)
		}
		required[name] = struct{}{}
	}
	forbidden := make(map[string]struct{}, len(expect.ForbiddenTools))
	for _, name := range expect.ForbiddenTools {
		name = strings.TrimSpace(name)
		if name == "" {
			return fmt.Errorf("case %q turn %d has an empty forbidden tool", caseID, turn)
		}
		if _, duplicate := forbidden[name]; duplicate {
			return fmt.Errorf(
				"case %q turn %d repeats forbidden tool %q",
				caseID,
				turn,
				name,
			)
		}
		if _, conflict := required[name]; conflict {
			return fmt.Errorf(
				"case %q turn %d both requires and forbids tool %q",
				caseID,
				turn,
				name,
			)
		}
		forbidden[name] = struct{}{}
	}
	return nil
}

func createWorkspace(tempRoot string, testCase Case) (string, func(), error) {
	root, err := os.MkdirTemp(tempRoot, "rwkv-agent-eval-")
	if err != nil {
		return "", nil, err
	}
	cleanup := func() {
		_ = os.RemoveAll(root)
	}
	workspace := filepath.Join(root, "workspace")
	if err := os.Mkdir(workspace, 0o700); err != nil {
		cleanup()
		return "", nil, err
	}
	for path, content := range testCase.Files {
		if err := writeFixture(workspace, path, content); err != nil {
			cleanup()
			return "", nil, err
		}
	}
	for path, content := range testCase.OutsideFiles {
		if err := writeFixture(root, path, content); err != nil {
			cleanup()
			return "", nil, err
		}
	}
	return workspace, cleanup, nil
}

func writeFixture(root string, path string, content string) error {
	if err := validateFixturePath(path); err != nil {
		return err
	}
	target := filepath.Join(root, filepath.FromSlash(path))
	if err := os.MkdirAll(filepath.Dir(target), 0o700); err != nil {
		return err
	}
	return os.WriteFile(target, []byte(content), 0o600)
}

func validateFixturePath(path string) error {
	if path == "" || strings.Contains(path, `\`) {
		return fmt.Errorf("path must be a non-empty slash-separated relative path")
	}
	native := filepath.FromSlash(path)
	if filepath.IsAbs(native) || filepath.VolumeName(native) != "" {
		return fmt.Errorf("path must be relative")
	}
	clean := filepath.Clean(native)
	if clean == "." || clean == ".." ||
		strings.HasPrefix(clean, ".."+string(filepath.Separator)) {
		return fmt.Errorf("path escapes its fixture root")
	}
	if clean != native {
		return fmt.Errorf("path must be clean and cannot contain traversal segments")
	}
	return nil
}

func firstPathPart(path string) string {
	value, _, _ := strings.Cut(path, "/")
	return value
}
