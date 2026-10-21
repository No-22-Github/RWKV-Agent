package eval

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"sort"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/product"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	tools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// The fixed tool catalogs, by version (product/catalog_version.go explains
// the numbering and the old work-vN names).
const (
	// AgentToolV1 (was agent-tool-v1.0) is the work bank's twelve tools.
	AgentToolV1 = product.AgentToolV1
	// AgentToolV2 (was agent-tool-v2.0) is v1 plus the sandboxed bash tool (just-bash
	// sidecar) and get_weather backed by the case's weather fixture.
	AgentToolV2 = product.AgentToolV2
	// AgentToolV3 (was agent-tool-v3) is the 2026-10-19 refactor
	// (docs/design/agent-tool-v3.md): read_file absorbs read_lines, web_fetch
	// cuts long pages to a shared budget. It is always the App directory
	// (product.Tools).
	AgentToolV3 = product.AgentToolV3
)

// IsFixedToolCatalog reports whether name selects one of the fixed catalogs,
// under its version or an old work-vN name.
func IsFixedToolCatalog(name string) bool {
	catalog, err := product.CanonicalCatalog(name)
	return err == nil && catalog != ""
}

// workToolCatalogClock is the fixed datetime every agent-tool-v1.0 case runs against
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

var workV3ToolCatalogNames = []string{
	"list_files", "read_file", "search_text",
	"write_file", "replace_lines", "append_file",
	"calculator", "data_query", "datetime",
	"web_search", "web_fetch", "get_weather", "bash",
}

func workCatalogNames(name string) []string {
	catalog, _ := product.CanonicalCatalog(name)
	switch catalog {
	case AgentToolV2:
		return workV2ToolCatalogNames
	case AgentToolV3:
		return workV3ToolCatalogNames
	}
	return workToolCatalogNames
}

// WorkCatalogNames returns a copy of the named bank catalog's tool names
// (agent-tool-v1.0 for any other name).
func WorkCatalogNames(name string) []string {
	return append([]string(nil), workCatalogNames(name)...)
}

// WorkToolCatalogNames returns a copy of the agent-tool-v1.0 catalog's tool names,
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
	if name == AgentToolV3 {
		return buildWorkV3Catalog(workspace, fixture, weather, tokenCount)
	}
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
	if name == AgentToolV2 {
		bash, err := tools.BashTools(tools.BashOptions{Workspace: workspace, ApplyToDisk: true, Now: workToolCatalogClock})
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

// buildWorkV3Catalog is agent-tool-v3 outside the App harness: the same
// product.Tools assembly on the case workspace (no staged view, bash applies
// to disk).
func buildWorkV3Catalog(workspace string, fixture []WebFixtureEntry, weather []WeatherFixtureEntry, tokenCount func(string) int) ([]agent.Tool, error) {
	web := webFixtureProviders{entries: fixture}
	set := product.AppDefaultToolSet()
	set.Catalog = product.AgentToolV3
	catalog, err := product.Tools(set, product.Backends{
		Workspace: workspace,
		Clock:     fixedAssistantClock{value: workToolCatalogClock},
		Web:       product.WebBackend{Search: web, Fetch: web, TokenCount: tokenCount},
		Weather:   weatherFixtureProvider{entries: weather},
		Bash:      product.BashBackend{ApplyToDisk: true},
	})
	if err != nil {
		return nil, err
	}
	if err := requireWorkCatalogShape(AgentToolV3, catalog); err != nil {
		return nil, err
	}
	return catalog, nil
}
