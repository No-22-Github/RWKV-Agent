package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"sort"
	"strings"
)

type ToolPermission string

const (
	PermissionCompute       ToolPermission = "compute"
	PermissionWorkspaceRead ToolPermission = "workspace_read"
	// PermissionWorkspaceWrite marks tools that create or modify workspace
	// files (E6 file-edit toolset).
	PermissionWorkspaceWrite ToolPermission = "workspace_write"
	PermissionNetworkRead    ToolPermission = "network_read"
	PermissionDelegate       ToolPermission = "delegate"
)

const (
	ToolBundleWorkspace = "workspace"
	ToolBundleCompute   = "compute"
	ToolBundleWeb       = "web"
	ToolBundleDelegate  = "delegate"
)

type ToolBundle struct {
	Name        string
	Description string
	// Editable marks bundles whose tools can modify workspace files. The
	// router adds edit-task few-shot examples for these (E6 finding).
	Editable bool
	// Delegation marks the sub-agent bundle. The router adds delegation
	// few-shot examples for it (class-3 e2e finding: otherwise delegate
	// requests route to respond).
	Delegation bool
}

func DefaultToolBundles() []ToolBundle {
	return []ToolBundle{
		{Name: ToolBundleWorkspace, Description: "Inspect files and search text inside the configured workspace."},
		{Name: ToolBundleCompute, Description: "Perform deterministic calculations, structured-data queries, and date/time lookup."},
		{Name: ToolBundleWeb, Description: "Search the public web and fetch readable page content."},
		{Name: ToolBundleDelegate, Description: "Delegate explicit subagent requests by running several independent Agent subtasks concurrently and combining their results."},
	}
}

func EnabledToolBundles(tools []Tool, catalog []ToolBundle) []ToolBundle {
	enabled := make(map[string]struct{})
	for _, tool := range tools {
		if tool == nil {
			continue
		}
		if bundle := strings.TrimSpace(tool.Spec().Bundle); bundle != "" {
			enabled[bundle] = struct{}{}
		}
	}
	result := make([]ToolBundle, 0, len(enabled))
	for _, bundle := range catalog {
		if _, ok := enabled[bundle.Name]; ok {
			result = append(result, bundle)
		}
	}
	return result
}

type loadToolsTool struct {
	bundles map[string]struct{}
}

type loadToolsResult struct {
	Bundle string `json:"bundle"`
}

func newLoadToolsTool(bundles []ToolBundle) (*loadToolsTool, error) {
	known := make(map[string]struct{}, len(bundles))
	for _, bundle := range bundles {
		name := strings.TrimSpace(bundle.Name)
		if name == "" || strings.TrimSpace(bundle.Description) == "" {
			return nil, fmt.Errorf("tool bundle name and description are required")
		}
		if _, exists := known[name]; exists {
			return nil, fmt.Errorf("duplicate tool bundle %q", name)
		}
		known[name] = struct{}{}
	}
	if len(known) == 0 {
		return nil, fmt.Errorf("at least one tool bundle is required")
	}
	return &loadToolsTool{bundles: known}, nil
}

func (t *loadToolsTool) Spec() ToolSpec {
	names := make([]string, 0, len(t.bundles))
	for name := range t.bundles {
		names = append(names, name)
	}
	sort.Strings(names)
	enum, _ := json.Marshal(names)
	parameters := fmt.Sprintf(`{"type":"object","properties":{"bundle":{"type":"string","enum":%s}},"required":["bundle"],"additionalProperties":false}`, enum)
	return ToolSpec{
		Name:        "load_tools",
		Description: "Expose one additional capability bundle when the current tools cannot complete the task.",
		Arguments:   `{"bundle":"capability bundle name"}`,
		Parameters:  json.RawMessage(parameters),
		Strict:      true,
		Control:     true,
	}
}

func (t *loadToolsTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Bundle string `json:"bundle"`
	}
	if err := DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	if _, ok := t.bundles[args.Bundle]; !ok {
		return nil, fmt.Errorf("%w: unknown tool bundle %q", ErrInvalidToolArguments, args.Bundle)
	}
	return loadToolsResult{Bundle: args.Bundle}, nil
}

func toolSpecsForBundles(specs []ToolSpec, bundles []string) []ToolSpec {
	selected := make(map[string]struct{}, len(bundles))
	for _, bundle := range bundles {
		selected[bundle] = struct{}{}
	}
	result := make([]ToolSpec, 0, len(specs))
	for _, spec := range specs {
		if spec.Control {
			result = append(result, spec)
			continue
		}
		if _, ok := selected[spec.Bundle]; ok {
			result = append(result, spec)
		}
	}
	return result
}

func toolsForSpecs(all map[string]Tool, specs []ToolSpec) map[string]Tool {
	result := make(map[string]Tool, len(specs))
	for _, spec := range specs {
		if tool, ok := all[spec.Name]; ok {
			result[spec.Name] = tool
		}
	}
	return result
}
