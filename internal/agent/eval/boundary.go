package eval

import _ "embed"

//go:embed boundary_cases.json
var boundaryCasesJSON []byte

func BoundaryCases() ([]Case, error) {
	return decodeCases(boundaryCasesJSON)
}
