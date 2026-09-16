package eval

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"slices"
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

// LoadCasesDir recursively loads bank-style single-case case.json files
// (schema v5: a bare Case object per file) below root. Cases whose
// tags.status is "draft" are skipped unless includeDraft is set. Files are
// read in sorted path order so a bank directory produces a deterministic
// case order.
func LoadCasesDir(root string, includeDraft bool) ([]Case, error) {
	var cases []Case
	seenIDs := make(map[string]string)
	err := filepath.WalkDir(root, func(path string, entry os.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			switch entry.Name() {
			case ".git", "build", "dist", "node_modules":
				return filepath.SkipDir
			}
			return nil
		}
		if entry.Name() != "case.json" {
			return nil
		}
		handle, err := os.Open(path)
		if err != nil {
			return err
		}
		defer handle.Close()
		data, err := io.ReadAll(io.LimitReader(handle, maxCaseFileBytes+1))
		if err != nil {
			return err
		}
		if len(data) > maxCaseFileBytes {
			return fmt.Errorf("%s: case file exceeds %d bytes", path, maxCaseFileBytes)
		}
		var testCase Case
		decoder := json.NewDecoder(strings.NewReader(string(data)))
		decoder.DisallowUnknownFields()
		if err := decoder.Decode(&testCase); err != nil {
			return fmt.Errorf("decode %s: %w", path, err)
		}
		if decoder.Decode(&struct{}{}) != io.EOF {
			return fmt.Errorf("decode %s: trailing JSON value", path)
		}
		if !includeDraft && caseIsDraft(testCase) {
			return nil
		}
		if err := ValidateCases([]Case{testCase}); err != nil {
			return fmt.Errorf("%s: %w", path, err)
		}
		if previous, duplicate := seenIDs[testCase.ID]; duplicate {
			return fmt.Errorf("duplicate eval case ID %q in %s and %s", testCase.ID, previous, path)
		}
		seenIDs[testCase.ID] = path
		cases = append(cases, testCase)
		return nil
	})
	if err != nil {
		return nil, err
	}
	if len(cases) == 0 {
		return nil, fmt.Errorf("no case.json files found below %s", root)
	}
	slices.SortFunc(cases, func(a, b Case) int {
		return strings.Compare(a.ID, b.ID)
	})
	return cases, nil
}

func caseIsDraft(testCase Case) bool {
	if testCase.Tags == nil {
		return false
	}
	status, ok := testCase.Tags["status"].(string)
	return ok && status == "draft"
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
	if value.SchemaVersion != CaseSchemaVersion &&
		value.SchemaVersion != caseSchemaVersionLegacy {
		return nil, fmt.Errorf(
			"unsupported case schema version %d; expected %d or %d",
			value.SchemaVersion,
			CaseSchemaVersion,
			caseSchemaVersionLegacy,
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
		if testCase.Primitive != nil && testCase.primitive == nil {
			return fmt.Errorf("case %q cannot set reserved primitive metadata in the native case schema", testCase.ID)
		}
		if err := validateCaseExpect(testCase); err != nil {
			return err
		}
		if !caseIsDraft(testCase) {
			if status, ok := testCase.Tags["status"].(string); ok &&
				status != "draft" && status != "reviewed" && status != "frozen" {
				return fmt.Errorf("case %q has invalid tags.status %q", testCase.ID, status)
			}
		}
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
			if turn.Expect.RequireActiveNoCall &&
				(turn.Expect.Tools == nil || len(turn.Expect.Tools) != 0) {
				return fmt.Errorf(
					"case %q turn %d requires active no-call but does not declare tools as an exact empty list",
					testCase.ID,
					index+1,
				)
			}
			if turn.Expect.Tools == nil &&
				len(turn.Expect.RequiredTools) == 0 &&
				len(turn.Expect.ForbiddenTools) == 0 &&
				len(turn.Expect.RequiredCalls) == 0 &&
				!turnDeclaresResultExpectation(turn.Expect) &&
				!caseDeclaresResultExpectation(testCase) {
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

// turnDeclaresResultExpectation reports whether a turn expects a result
// (answer or output contract) rather than only tool behavior, which is the
// v5 relaxation of the "every turn must declare tool expectations" rule.
func turnDeclaresResultExpectation(expect Expectation) bool {
	return expect.ExpectedNumber != nil ||
		expect.OutputEquals != nil ||
		len(expect.OutputContains) > 0 ||
		len(expect.OutputContainsAny) > 0 ||
		len(expect.OutputExcludes) > 0
}

// caseDeclaresResultExpectation reports whether the case-level expect block
// scores end state (files / offline run / call budgets), which also releases
// turns from declaring tool expectations.
func caseDeclaresResultExpectation(testCase Case) bool {
	if testCase.Expect == nil {
		return false
	}
	return len(testCase.Expect.Files) > 0 ||
		testCase.Expect.Run != nil ||
		len(testCase.Expect.MaxCalls) > 0
}

func validateCaseExpect(testCase Case) error {
	if testCase.Expect == nil {
		return nil
	}
	expect := testCase.Expect
	for path, fileExpect := range expect.Files {
		if err := validateFixturePath(path); err != nil {
			return fmt.Errorf("case %q expect.files %q: %w", testCase.ID, path, err)
		}
		set := 0
		if fileExpect.Equals != nil {
			set++
		}
		if len(fileExpect.Contains) > 0 {
			set++
		}
		if fileExpect.Absent {
			set++
		}
		if fileExpect.Unchanged {
			set++
		}
		if set > 1 {
			return fmt.Errorf(
				"case %q expect.files %q combines equals/contains/absent/unchanged",
				testCase.ID,
				path,
			)
		}
		if set == 0 {
			return fmt.Errorf(
				"case %q expect.files %q declares no expectation",
				testCase.ID,
				path,
			)
		}
		if fileExpect.Unchanged {
			if _, initial := testCase.Files[path]; !initial {
				return fmt.Errorf(
					"case %q expect.files %q unchanged requires the file in files",
					testCase.ID,
					path,
				)
			}
		}
		if fileExpect.Absent {
			if _, initial := testCase.Files[path]; initial {
				return fmt.Errorf(
					"case %q expect.files %q absent cannot apply to an initial fixture file",
					testCase.ID,
					path,
				)
			}
		}
	}
	if run := expect.Run; run != nil {
		if strings.TrimSpace(run.Path) == "" {
			return fmt.Errorf("case %q expect.run requires a script path", testCase.ID)
		}
		if err := validateFixturePath(run.Path); err != nil {
			return fmt.Errorf("case %q expect.run %q: %w", testCase.ID, run.Path, err)
		}
		if _, scripted := testCase.Files[run.Path]; !scripted {
			return fmt.Errorf(
				"case %q expect.run script %q must exist in files (the model may rewrite it, but the bank ships a reference)",
				testCase.ID,
				run.Path,
			)
		}
		if run.TimeoutMillis < 0 {
			return fmt.Errorf("case %q expect.run timeout_millis must be non-negative", testCase.ID)
		}
		for path := range run.HiddenFiles {
			if err := validateFixturePath(path); err != nil {
				return fmt.Errorf("case %q expect.run hidden file %q: %w", testCase.ID, path, err)
			}
			if firstPathPart(path) == "workspace" {
				return fmt.Errorf("case %q expect.run hidden file cannot enter the workspace", testCase.ID)
			}
		}
	}
	for tool, budget := range expect.MaxCalls {
		if strings.TrimSpace(tool) == "" {
			return fmt.Errorf("case %q expect.max_calls has an empty tool name", testCase.ID)
		}
		if budget < 1 {
			return fmt.Errorf("case %q expect.max_calls[%q] must be at least 1", testCase.ID, tool)
		}
	}
	return nil
}

func validateToolSets(caseID string, turn int, expect Expectation) error {	required := make(map[string]struct{}, len(expect.RequiredTools))
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

// normalizeSubtaskText makes keyword matching tolerant of the model's
// punctuation and casing: case-folded, hyphens and underscores become spaces
// so "bramblewick-register" matches "Bramblewick register".
func normalizeSubtaskText(text string) string {
	lowered := strings.ToLower(text)
	lowered = strings.ReplaceAll(lowered, "-", " ")
	lowered = strings.ReplaceAll(lowered, "_", " ")
	return lowered
}

func firstPathPart(path string) string {
	value, _, _ := strings.Cut(path, "/")
	return value
}
