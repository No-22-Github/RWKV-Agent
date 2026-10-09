package eval

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	tools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// WorkToolCatalogName selects the work bank's fixed tool directory.
const WorkToolCatalogName = "work-v1"

// WorkV2ToolCatalogName is work-v1 plus the sandboxed bash tool (just-bash
// sidecar) and get_weather backed by the case's weather fixture.
const WorkV2ToolCatalogName = "work-v2"

// IsWorkToolCatalog reports whether name is one of the fixed bank catalogs.
func IsWorkToolCatalog(name string) bool {
	return name == WorkToolCatalogName || name == WorkV2ToolCatalogName
}

// workToolCatalogClock is the fixed datetime every work-v1 case runs against
// (bank contract, authoring-guide §2.4): no case may depend on wall-clock.
var workToolCatalogClock = time.Date(
	2026, time.September, 16, 10, 0, 0, 0,
	time.FixedZone("Asia/Shanghai", 8*60*60),
)

// workToolCatalogNames is the contract the bank lint checks against: exactly
// these twelve tools, no per-case additions or removals.
var workToolCatalogNames = []string{
	"list_files", "read_file", "search_text",
	"read_lines", "write_file", "replace_lines", "append_file",
	"calculator", "data_query", "datetime",
	"web_search", "web_fetch",
}

var workV2ToolCatalogNames = append(append([]string(nil), workToolCatalogNames...), "bash", "get_weather")

func workCatalogNames(name string) []string {
	if name == WorkV2ToolCatalogName {
		return workV2ToolCatalogNames
	}
	return workToolCatalogNames
}

// WorkCatalogNames returns a copy of the named bank catalog's tool names
// (work-v1 for any other name).
func WorkCatalogNames(name string) []string {
	return append([]string(nil), workCatalogNames(name)...)
}

// WorkToolCatalogNames returns a copy of the work-v1 catalog's tool names,
// the one source of truth for the §4.2 render-layer rotation.
func WorkToolCatalogNames() []string {
	return append([]string(nil), workToolCatalogNames...)
}

// buildWorkToolCatalog assembles the fixed directory: workspace reads,
// line-form file editing, deterministic compute (calculator / data_query /
// datetime on the fixed clock) and the web pair. Web tools register even for
// cases without web content: an empty fixture returns an empty search list
// and the deterministic not-found page, so "is there a web tool" never leaks
// which cases need one.
func buildWorkToolCatalog(
	name string,
	workspace string,
	fixture []WebFixtureEntry,
	weather []WeatherFixtureEntry,
	fetchBudgetTokens int,
	tokenCount func(string) int,
) ([]agent.Tool, error) {
	workspaceTools, err := agent.WorkspaceTools(workspace)
	if err != nil {
		return nil, err
	}
	editTools, err := assistanttools.FileEditTools(workspace, assistanttools.FileEditLines)
	if err != nil {
		return nil, err
	}
	localTools, err := assistanttools.LocalTools(assistanttools.Options{
		Clock:     fixedAssistantClock{value: workToolCatalogClock},
		Workspace: workspace,
	})
	if err != nil {
		return nil, err
	}
	providers := webFixtureProviders{entries: fixture}
	webTools := tools.WebTools(tools.WebOptions{
		Search:            providers,
		Fetch:             providers,
		FetchBudgetTokens: fetchBudgetTokens,
		TokenCount:        tokenCount,
	})
	catalog := append(append(append(workspaceTools, editTools...), localTools...), webTools...)
	if name == WorkV2ToolCatalogName {
		bash, err := tools.BashTools(tools.BashOptions{Workspace: workspace})
		if err != nil {
			return nil, err
		}
		catalog = append(catalog, bash...)
		catalog = append(catalog, tools.WeatherTools(weatherFixtureProvider{entries: weather})...)
	}
	if err := requireWorkCatalogShape(name, catalog); err != nil {
		return nil, err
	}
	return catalog, nil
}

// requireWorkCatalogShape enforces the twelve-tool contract at build time so
// an upstream tool-set change cannot silently drift the bank's catalog.
func requireWorkCatalogShape(name string, catalog []agent.Tool) error {
	names := make([]string, 0, len(catalog))
	for _, tool := range catalog {
		names = append(names, tool.Spec().Name)
	}
	sort.Strings(names)
	want := append([]string(nil), workCatalogNames(name)...)
	sort.Strings(want)
	if fmt.Sprint(names) != fmt.Sprint(want) {
		return fmt.Errorf(
			"tool catalog %s drifted: got %v, want %v",
			name,
			names,
			want,
		)
	}
	return nil
}

// workToolCatalogHash pins the exact schemas the model saw. Two runs are only
// comparable when this hash matches (ledger comparability key).
func workToolCatalogHash(catalog []agent.Tool) string {
	digest := sha256.New()
	sorted := append([]agent.Tool(nil), catalog...)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Spec().Name < sorted[j].Spec().Name
	})
	for _, tool := range sorted {
		spec := tool.Spec()
		payload, err := json.Marshal(struct {
			Name        string
			Description string
			Arguments   string
			Parameters  json.RawMessage
		}{
			Name:        spec.Name,
			Description: spec.Description,
			Arguments:   spec.Arguments,
			Parameters:  spec.Parameters,
		})
		if err != nil {
			continue
		}
		digest.Write(payload)
		digest.Write([]byte{'\n'})
	}
	return hex.EncodeToString(digest.Sum(nil))
}
