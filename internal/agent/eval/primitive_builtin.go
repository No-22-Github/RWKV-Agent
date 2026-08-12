package eval

import (
	"embed"
	"fmt"
	"io/fs"
	"path"
	"strings"
)

const (
	primitiveOrig30Directory = "testdata/primitive_orig30"
	primitiveOrig30Count     = 30
)

//go:embed testdata/primitive_orig30/*.json
var primitiveOrig30FS embed.FS

// PrimitiveCases loads the repository-pinned agent_cases_orig30 snapshot. The
// JSON is embedded in the CLI binary so CI and external model runs always use
// the same fixtures and scoring contracts.
func PrimitiveCases() ([]Case, error) {
	entries, err := fs.ReadDir(primitiveOrig30FS, primitiveOrig30Directory)
	if err != nil {
		return nil, fmt.Errorf("read embedded Primitive Bench cases: %w", err)
	}
	if len(entries) != primitiveOrig30Count {
		return nil, fmt.Errorf(
			"embedded Primitive Bench case count = %d; want %d",
			len(entries),
			primitiveOrig30Count,
		)
	}

	cases := make([]Case, 0, primitiveOrig30Count)
	fixtureBytes := 0
	for _, entry := range entries {
		if entry.IsDir() || !strings.EqualFold(path.Ext(entry.Name()), ".json") {
			return nil, fmt.Errorf("unexpected embedded Primitive Bench entry %q", entry.Name())
		}
		location := path.Join(primitiveOrig30Directory, entry.Name())
		data, err := primitiveOrig30FS.ReadFile(location)
		if err != nil {
			return nil, fmt.Errorf("read embedded Primitive Bench case %q: %w", entry.Name(), err)
		}
		if len(data) > maxCaseFileBytes {
			return nil, fmt.Errorf("%s exceeds %d bytes", location, maxCaseFileBytes)
		}
		sourceURL := primitiveSourceBase + "/agent_cases_orig30/" + entry.Name()
		testCase, err := decodePrimitiveCase(data, location, sourceURL)
		if err != nil {
			return nil, err
		}
		for _, content := range testCase.Files {
			fixtureBytes += len(content)
		}
		if fixtureBytes > maxPrimitiveSuiteBytes {
			return nil, fmt.Errorf("embedded Primitive Bench fixtures exceed %d bytes", maxPrimitiveSuiteBytes)
		}
		cases = append(cases, testCase)
	}
	if err := ValidateCases(cases); err != nil {
		return nil, err
	}
	return cases, nil
}
