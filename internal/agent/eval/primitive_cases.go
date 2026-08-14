package eval

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

const (
	// SuitePrimitive is retained for trusted external Primitive case directories
	// and as a legacy alias for the original built-in suite.
	SuitePrimitive           = "primitive"
	SuitePrimitiveOrig30     = "primitive-orig30"
	SuitePrimitiveFeedback30 = "primitive-feedback30"
	maxPrimitiveCaseCount    = 512
	maxPrimitiveSuiteBytes   = 64 << 20
	primitiveSourceBase      = "https://github.com/RWKV-Vibe/rwkv-Primitive-Bench/blob/416b073d2c5442ae34bfbf8a3b84ed414b5b85ff"
)

// CanonicalBuiltinSuiteName maps legacy built-in names to their explicit,
// dataset-qualified names. External Primitive directories continue to use the
// generic SuitePrimitive manifest value.
func CanonicalBuiltinSuiteName(name string) string {
	if name == SuitePrimitive {
		return SuitePrimitiveOrig30
	}
	return name
}

// IsPrimitiveSuite reports whether a built-in suite uses the Primitive Bench
// protocol, case-specific turn budgets, tools, and scoring runtime.
func IsPrimitiveSuite(name string) bool {
	return name == SuitePrimitive ||
		name == SuitePrimitiveOrig30 ||
		name == SuitePrimitiveFeedback30
}

var primitiveToolSets = map[string][]string{
	"multiply":           {"multiply"},
	"file":               {"list_files", "read_file", "write_file", "search", "run_tests"},
	"nav":                {"list_files", "read_file", "search", "run_lua", "submit"},
	"write":              {"list_files", "read_file", "write_file", "search", "run_tests", "run_lua", "submit"},
	"run":                {"list_files", "read_file", "ls", "stat", "chmod", "run_file", "run_lua", "submit"},
	"awk":                {"list_files", "read_file", "write_file", "run_awk", "run_lua", "submit"},
	"open_probe":         {"list_files", "read_file", "write_file", "search", "run_tests", "ls", "stat", "chmod", "run_file", "run_awk", "run_lua"},
	"nav_plus_schedule":  {"list_files", "read_file", "search", "run_lua", "submit", "list_schedules"},
	"file_plus_schedule": {"list_files", "read_file", "write_file", "search", "run_tests", "list_schedules"},
	"chmod_run_submit":   {"chmod", "run_file", "submit"},
	"run_file_submit":    {"run_file", "submit"},
	"run_tests_submit":   {"run_tests", "submit"},
}

var primitiveToolNames = map[string]struct{}{
	"multiply": {}, "list_files": {}, "ls": {}, "stat": {},
	"read_file": {}, "write_file": {}, "chmod": {}, "run_file": {},
	"run_awk": {}, "run_lua": {}, "search": {}, "run_tests": {},
	"submit": {}, "list_schedules": {},
}

// primitiveRuntime holds mutable implementation details that native v3 case
// files cannot inject. PrimitiveMetadata is the read-only, manifest-visible
// projection of the same source-side contract.
type primitiveRuntime struct {
	toolNames      []string
	modes          map[string]string
	runOutputs     map[string]string
	requiredTools  []string
	forbiddenTools []string
	expectedSubmit *string
	scenario       string
	scorer         string
	tolerance      float64
}

type primitiveCaseFile struct {
	Name        string               `json:"name"`
	Title       string               `json:"title"`
	Mode        string               `json:"mode"`
	System      json.RawMessage      `json:"system"`
	Prompt      string               `json:"prompt"`
	Tools       json.RawMessage      `json:"tools"`
	Environment primitiveEnvironment `json:"environment"`
	Evaluation  json.RawMessage      `json:"evaluation"`
	MaxTurns    int                  `json:"max_turns"`
	Suite       string               `json:"suite"`
}

type primitiveEnvironment struct {
	Kind           string                     `json:"kind"`
	Files          map[string]json.RawMessage `json:"files"`
	Modes          map[string]string          `json:"modes"`
	RunOutputs     map[string]string          `json:"run_outputs"`
	ExpectedSubmit *string                    `json:"expected_submit"`
	RequiredTools  []string                   `json:"required_tools"`
	ForbiddenTools []string                   `json:"forbidden_tools"`
	Scenario       string                     `json:"scenario"`
}

type primitiveEvaluation struct {
	Scorer    string   `json:"scorer"`
	Tolerance *float64 `json:"tolerance"`
}

// LoadPrimitiveCases imports declarative Primitive Bench cases from a trusted
// local checkout. It never downloads or executes cases.py. This remains useful
// for comparing the embedded snapshot with a newer upstream checkout.
func LoadPrimitiveCases(directory string) ([]Case, error) {
	info, err := os.Stat(directory)
	if err != nil {
		return nil, err
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("Primitive Bench cases path is not a directory")
	}
	entries, err := os.ReadDir(directory)
	if err != nil {
		return nil, err
	}
	paths := make([]string, 0, len(entries))
	for _, entry := range entries {
		if entry.IsDir() || !strings.EqualFold(filepath.Ext(entry.Name()), ".json") {
			continue
		}
		paths = append(paths, filepath.Join(directory, entry.Name()))
	}
	sort.Strings(paths)
	if len(paths) == 0 {
		return nil, fmt.Errorf("Primitive Bench directory contains no JSON cases")
	}
	if len(paths) > maxPrimitiveCaseCount {
		return nil, fmt.Errorf("Primitive Bench directory contains %d cases; maximum is %d", len(paths), maxPrimitiveCaseCount)
	}

	cases := make([]Case, 0, len(paths))
	fixtureBytes := 0
	for _, path := range paths {
		testCase, err := loadPrimitiveCase(path)
		if err != nil {
			return nil, err
		}
		for _, content := range testCase.Files {
			fixtureBytes += len(content)
		}
		if fixtureBytes > maxPrimitiveSuiteBytes {
			return nil, fmt.Errorf("Primitive Bench fixtures exceed %d bytes", maxPrimitiveSuiteBytes)
		}
		cases = append(cases, testCase)
	}
	if err := ValidateCases(cases); err != nil {
		return nil, err
	}
	return cases, nil
}

func loadPrimitiveCase(path string) (Case, error) {
	handle, err := os.Open(path)
	if err != nil {
		return Case{}, err
	}
	defer handle.Close()
	data, err := io.ReadAll(io.LimitReader(handle, maxCaseFileBytes+1))
	if err != nil {
		return Case{}, err
	}
	if len(data) > maxCaseFileBytes {
		return Case{}, fmt.Errorf("%s exceeds %d bytes", path, maxCaseFileBytes)
	}
	sourceURL := primitiveSourceBase + "/" + filepath.Base(filepath.Dir(path)) + "/" + filepath.Base(path)
	return decodePrimitiveCase(data, path, sourceURL)
}

func decodePrimitiveCase(data []byte, path, sourceURL string) (Case, error) {
	var source primitiveCaseFile
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&source); err != nil {
		return Case{}, fmt.Errorf("%s: decode Primitive Bench case: %w", path, err)
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return Case{}, fmt.Errorf("%s: trailing JSON value", path)
	}
	if source.Name == "" || source.Title == "" || strings.TrimSpace(source.Prompt) == "" {
		return Case{}, fmt.Errorf("%s: name, title, and prompt are required", path)
	}
	if source.Mode == "" {
		source.Mode = "benchmark"
	}
	if source.Mode != "benchmark" {
		return Case{}, fmt.Errorf("%s: only benchmark cases are supported; got mode %q", path, source.Mode)
	}
	if err := validatePrimitiveSystem(source.System); err != nil {
		return Case{}, fmt.Errorf("%s: %w", path, err)
	}
	if source.MaxTurns <= 0 {
		return Case{}, fmt.Errorf("%s: max_turns must be positive", path)
	}
	if source.Environment.Kind == "" {
		source.Environment.Kind = "emulated"
	}
	if source.Environment.Kind != "emulated" {
		return Case{}, fmt.Errorf("%s: unsupported environment kind %q", path, source.Environment.Kind)
	}
	toolNames, err := decodePrimitiveTools(source.Tools)
	if err != nil {
		return Case{}, fmt.Errorf("%s: %w", path, err)
	}
	if err := validatePrimitiveEnvironment(source.Environment, toolNames); err != nil {
		return Case{}, fmt.Errorf("%s: %w", path, err)
	}
	scorer, tolerance, err := decodePrimitiveEvaluation(source.Evaluation)
	if err != nil {
		return Case{}, fmt.Errorf("%s: %w", path, err)
	}
	switch scorer {
	case "submit", "submit_after_tests", "line_change_submit",
		"numeric_submit_tolerance", "file_changed_submit", "truthfulness":
		if source.Environment.ExpectedSubmit == nil {
			return Case{}, fmt.Errorf("%s: scorer %q requires environment.expected_submit", path, scorer)
		}
	}
	files := make(map[string]string, len(source.Environment.Files))
	for name, raw := range source.Environment.Files {
		content, err := decodePrimitiveFileContent(raw)
		if err != nil {
			return Case{}, fmt.Errorf("%s: file %q: %w", path, name, err)
		}
		files[name] = content
	}

	expect := Expectation{
		Route:          "inspect",
		RequiredTools:  append([]string(nil), source.Environment.RequiredTools...),
		ForbiddenTools: append([]string(nil), source.Environment.ForbiddenTools...),
	}
	if scorer == "arithmetic" {
		expect.RequiredTools = []string{"multiply"}
		expect.OutputContains = []string{"1887357"}
	}
	if scorer == "invoice" && len(expect.RequiredTools) == 0 {
		expect.RequiredTools = []string{"run_tests"}
	}
	if len(expect.RequiredTools) == 0 && len(expect.ForbiddenTools) == 0 {
		// ValidateCases requires an explicit tool contract. An empty exact list is
		// correct only for a tool-free imported case.
		expect.Tools = []string{}
	}

	var toleranceMetadata *float64
	if scorer == "numeric_submit_tolerance" {
		value := tolerance
		toleranceMetadata = &value
	}
	metadata := &PrimitiveMetadata{
		ToolNames:      append([]string(nil), toolNames...),
		Modes:          cloneStringMap(source.Environment.Modes),
		RunOutputs:     cloneStringMap(source.Environment.RunOutputs),
		ExpectedSubmit: source.Environment.ExpectedSubmit,
		Scenario:       source.Environment.Scenario,
		Scorer:         scorer,
		Tolerance:      toleranceMetadata,
		MaxTurns:       source.MaxTurns,
	}
	return Case{
		ID:          source.Name,
		Description: source.Title,
		Category:    "Primitive Bench / " + firstNonEmpty(source.Suite, "imported"),
		Source:      sourceURL,
		Files:       files,
		Turns: []Turn{{
			Prompt: source.Prompt,
			Expect: expect,
		}},
		Primitive: metadata,
		primitive: &primitiveRuntime{
			toolNames:      toolNames,
			modes:          cloneStringMap(source.Environment.Modes),
			runOutputs:     cloneStringMap(source.Environment.RunOutputs),
			requiredTools:  append([]string(nil), source.Environment.RequiredTools...),
			forbiddenTools: append([]string(nil), source.Environment.ForbiddenTools...),
			expectedSubmit: source.Environment.ExpectedSubmit,
			scenario:       source.Environment.Scenario,
			scorer:         scorer,
			tolerance:      tolerance,
		},
	}, nil
}

func validatePrimitiveSystem(raw json.RawMessage) error {
	if len(raw) == 0 || bytes.Equal(bytes.TrimSpace(raw), []byte("null")) {
		return nil
	}
	var value string
	if err := json.Unmarshal(raw, &value); err != nil {
		return fmt.Errorf("system must be a string")
	}
	if value != "base" {
		return fmt.Errorf("unsupported Primitive Bench system %q; only base maps to the RWKV-Agent harness", value)
	}
	return nil
}

func validatePrimitiveEnvironment(environment primitiveEnvironment, toolNames []string) error {
	offered := make(map[string]struct{}, len(toolNames))
	for _, name := range toolNames {
		offered[name] = struct{}{}
	}
	for _, name := range environment.RequiredTools {
		if _, known := primitiveToolNames[name]; !known {
			return fmt.Errorf("unknown required tool %q", name)
		}
		if _, available := offered[name]; !available {
			return fmt.Errorf("required tool %q is not offered by the case", name)
		}
	}
	for _, name := range environment.ForbiddenTools {
		if _, known := primitiveToolNames[name]; !known {
			return fmt.Errorf("unknown forbidden tool %q", name)
		}
	}
	for name := range environment.Modes {
		if err := validateFixturePath(name); err != nil {
			return fmt.Errorf("mode path %q: %w", name, err)
		}
		if _, ok := environment.Files[name]; !ok {
			return fmt.Errorf("mode path %q does not name a fixture file", name)
		}
	}
	for name := range environment.RunOutputs {
		if err := validateFixturePath(name); err != nil {
			return fmt.Errorf("run output path %q: %w", name, err)
		}
		if _, ok := environment.Files[name]; !ok {
			return fmt.Errorf("run output path %q does not name a fixture file", name)
		}
	}
	switch environment.Scenario {
	case "", "awk_tabs_justify", "patch_config", "malformed_edit_recovery",
		"run_tests_before_claim", "read_only_repo_explain",
		"tool_result_truthfulness", "two_step_program_output", "date_parser_patch":
		return nil
	default:
		return fmt.Errorf("unsupported Primitive Bench scenario %q", environment.Scenario)
	}
}

func decodePrimitiveTools(raw json.RawMessage) ([]string, error) {
	var setName string
	if json.Unmarshal(raw, &setName) == nil {
		names, ok := primitiveToolSets[setName]
		if !ok {
			return nil, fmt.Errorf("unknown Primitive Bench tool set %q", setName)
		}
		return append([]string(nil), names...), nil
	}
	var names []string
	if err := json.Unmarshal(raw, &names); err != nil {
		return nil, fmt.Errorf("tools must be a tool-set name or list of tool names")
	}
	seen := make(map[string]struct{}, len(names))
	for _, name := range names {
		if _, ok := primitiveToolNames[name]; !ok {
			return nil, fmt.Errorf("unknown Primitive Bench tool %q", name)
		}
		if _, duplicate := seen[name]; duplicate {
			return nil, fmt.Errorf("duplicate Primitive Bench tool %q", name)
		}
		seen[name] = struct{}{}
	}
	return names, nil
}

func decodePrimitiveEvaluation(raw json.RawMessage) (string, float64, error) {
	var name string
	if json.Unmarshal(raw, &name) == nil {
		if !supportedPrimitiveScorer(name) {
			return "", 0, fmt.Errorf("unsupported Primitive Bench scorer %q", name)
		}
		if name == "numeric_submit_tolerance" {
			return "", 0, fmt.Errorf("numeric_submit_tolerance requires an evaluation object with tolerance")
		}
		return name, 0, nil
	}
	var value primitiveEvaluation
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&value); err != nil {
		return "", 0, fmt.Errorf("evaluation must be a scorer name or object: %w", err)
	}
	if !supportedPrimitiveScorer(value.Scorer) {
		return "", 0, fmt.Errorf("unsupported Primitive Bench scorer %q", value.Scorer)
	}
	if value.Scorer == "numeric_submit_tolerance" &&
		(value.Tolerance == nil || *value.Tolerance < 0) {
		return "", 0, fmt.Errorf("numeric_submit_tolerance requires a non-negative tolerance")
	}
	if value.Tolerance == nil {
		return value.Scorer, 0, nil
	}
	return value.Scorer, *value.Tolerance, nil
}

func supportedPrimitiveScorer(name string) bool {
	switch name {
	case "arithmetic", "invoice", "submit", "submit_after_tests",
		"line_change_submit", "numeric_submit_tolerance", "file_changed_submit",
		"repo_explain", "truthfulness":
		return true
	default:
		return false
	}
}

func decodePrimitiveFileContent(raw json.RawMessage) (string, error) {
	var text string
	if json.Unmarshal(raw, &text) == nil {
		return text, nil
	}
	var lines []string
	if json.Unmarshal(raw, &lines) == nil {
		if len(lines) == 0 {
			return "", nil
		}
		return strings.Join(lines, "\n") + "\n", nil
	}
	var object struct {
		Text   *string   `json:"text"`
		Lines  *[]string `json:"lines"`
		Repeat *struct {
			Text  string `json:"text"`
			Count int    `json:"count"`
		} `json:"repeat"`
	}
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&object); err != nil {
		return "", fmt.Errorf("content must be a string, line array, {text}, {lines}, or {repeat}")
	}
	configured := 0
	if object.Text != nil {
		configured++
	}
	if object.Lines != nil {
		configured++
	}
	if object.Repeat != nil {
		configured++
	}
	if configured != 1 {
		return "", fmt.Errorf("content object must set exactly one of text, lines, or repeat")
	}
	if object.Text != nil {
		return *object.Text, nil
	}
	if object.Lines != nil {
		if len(*object.Lines) == 0 {
			return "", nil
		}
		return strings.Join(*object.Lines, "\n") + "\n", nil
	}
	if object.Repeat.Count < 0 || object.Repeat.Count > 100000 {
		return "", fmt.Errorf("repeat count must be between 0 and 100000")
	}
	if object.Repeat.Count > 0 && len(object.Repeat.Text) > maxCaseFileBytes/object.Repeat.Count {
		return "", fmt.Errorf("expanded repeat content exceeds %d bytes", maxCaseFileBytes)
	}
	return strings.Repeat(object.Repeat.Text, object.Repeat.Count), nil
}

func cloneStringMap(source map[string]string) map[string]string {
	if len(source) == 0 {
		return nil
	}
	result := make(map[string]string, len(source))
	for key, value := range source {
		result[key] = value
	}
	return result
}

func firstNonEmpty(values ...string) string {
	for _, value := range values {
		if strings.TrimSpace(value) != "" {
			return value
		}
	}
	return ""
}
