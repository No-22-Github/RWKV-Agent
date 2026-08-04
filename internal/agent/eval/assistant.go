package eval

import _ "embed"

//go:embed assistant_cases.json
var assistantCasesJSON []byte

func AssistantCases() ([]Case, error) {
	return decodeCases(assistantCasesJSON)
}
