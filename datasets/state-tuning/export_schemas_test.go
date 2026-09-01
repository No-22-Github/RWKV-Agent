// Package statetuning exports the product's real tool schemas so the teacher
// collector sees byte-identical descriptions and JSON Schemas. Hand-copying
// them would drift, and a trained state does not survive a prompt change.
//
// Run: go test -run TestExportToolSchemas ./datasets/state-tuning/
package statetuning

import (
	"encoding/json"
	"os"
	"sort"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/tools"
)

// The 8 tools the state-tuning dataset targets. Anything outside this set is
// dropped, so adding a product tool does not silently widen the dataset.
var wanted = map[string]bool{
	"read_lines": true, "write_file": true, "replace_lines": true,
	"append_file": true, "web_search": true, "web_fetch": true,
	"datetime": true, "spawn_agents": true,
}

// openAIFunction is the shape a chat-completions tools array expects, plus the
// product's own compact Arguments hint. The hint is hand-written in the Go
// source and is what G1IProtocol.Instructions prints in the tool catalog, so a
// renderer must reuse it verbatim rather than synthesising one from Parameters.
type openAIFunction struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Parameters  json.RawMessage `json:"parameters"`
	Arguments   string          `json:"arguments_hint"`
}

func TestExportToolSchemas(t *testing.T) {
	root := t.TempDir()
	var all []agent.Tool

	fileEdit, err := tools.FileEditTools(root, tools.FileEditLines)
	if err != nil {
		t.Fatal(err)
	}
	all = append(all, fileEdit...)

	local, err := tools.LocalTools(tools.Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	all = append(all, local...)

	all = append(all, tools.WebTools(tools.WebOptions{})...)
	all = append(all, tools.DelegationTools(tools.DelegationOptions{})...)

	out := map[string]openAIFunction{}
	for _, tool := range all {
		spec := tool.Spec()
		if !wanted[spec.Name] {
			continue
		}
		if len(spec.Parameters) == 0 {
			t.Errorf("tool %q has no Parameters schema", spec.Name)
			continue
		}
		var compact json.RawMessage
		if compact, err = compactJSON(spec.Parameters); err != nil {
			t.Fatalf("tool %q parameters: %v", spec.Name, err)
		}
		if strings.TrimSpace(spec.Arguments) == "" {
			t.Errorf("tool %q has no Arguments hint", spec.Name)
		}
		out[spec.Name] = openAIFunction{
			Name:        spec.Name,
			Description: spec.Description,
			Parameters:  compact,
			Arguments:   spec.Arguments,
		}
	}

	names := make([]string, 0, len(out))
	for name := range out {
		names = append(names, name)
	}
	sort.Strings(names)
	t.Logf("exported %d/%d tools: %v", len(out), len(wanted), names)
	for name := range wanted {
		if _, ok := out[name]; !ok {
			t.Errorf("wanted tool %q was not produced by any constructor", name)
		}
	}

	encoded, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile("tool_schemas.json", append(encoded, '\n'), 0o644); err != nil {
		t.Fatal(err)
	}
}

func compactJSON(raw json.RawMessage) (json.RawMessage, error) {
	var value any
	if err := json.Unmarshal(raw, &value); err != nil {
		return nil, err
	}
	return json.Marshal(value)
}
