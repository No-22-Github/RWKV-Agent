package product

import (
	"fmt"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// ToolSet selects which optional tool groups the directory contains. The local
// compute tools (calculator, data_query, datetime) are always present.
type ToolSet struct {
	// Files adds the workspace read tools (list_files, read_file, search_text).
	// Without an open workspace they stay in the directory and answer with a
	// clear "open a workspace first" error, so the model still knows the
	// capability exists.
	Files bool
	// Edit adds the line-form file editing tools (read_lines, write_file,
	// replace_lines, append_file). The caller decides when editing is allowed;
	// the App only offers it when writes land in a staged view.
	Edit bool
	// Web adds web_search and web_fetch.
	Web bool
	// Weather adds get_weather.
	Weather bool
	// Bash adds the sandboxed bash tool (just-bash sidecar).
	Bash bool
	// Subagents adds spawn_agents.
	Subagents bool
	// Catalog picks the tool generation (catalog_version.go): AgentToolV3
	// (the zero value) or AgentToolV2, kept frozen so historical runs can be
	// reproduced (docs/design/agent-tool-v3.md §4.1). Old work-vN names are
	// accepted.
	Catalog string
}

// AppDefaultToolSet is the directory a new App connection offers: files, line
// editing, web, weather and bash; sub-agents stay opt-in.
func AppDefaultToolSet() ToolSet {
	return ToolSet{Files: true, Edit: true, Web: true, Weather: true, Bash: true}
}

// WebBackend carries the web providers and the fetch budget.
type WebBackend struct {
	// Search and Fetch default to providers that answer "not configured" when
	// nil, so listing the tools never depends on having API keys.
	Search assistanttools.WebSearchProvider
	Fetch  assistanttools.WebFetchProvider
	// FetchBudgetTokens overrides the per-call fetched-page token budget
	// (0 = the calibrated default).
	FetchBudgetTokens int
	// TokenCount counts real World-vocabulary tokens for that budget; nil falls
	// back to the estimator.
	TokenCount func(string) int
}

// BashBackend configures the bash tool.
type BashBackend struct {
	// Overlay is the staged workspace bash edits through. Nil uses Backends.View.
	Overlay *assistanttools.StagedWorkspace
	// ApplyToDisk writes every bash change straight back to the workspace
	// (evaluation without a staged view). The App keeps changes staged.
	ApplyToDisk bool
	// CatalogOnly lists the tool without starting a sidecar (prompt previews).
	CatalogOnly bool
	// Sidecar overrides the sidecar binary location.
	Sidecar string
}

// DelegationBackend configures spawn_agents.
type DelegationBackend struct {
	Run         assistanttools.AgentTaskRunner
	MaxParallel int
	Timeout     time.Duration
}

// Backends are the implementations behind the tool directory. The zero value
// is a workspace-less App with real clock and disk access.
type Backends struct {
	// Workspace is the workspace root; empty means none is open.
	Workspace string
	// View is the staged workspace shared by every file tool and bash. When set
	// it becomes the filesystem for all tools and wraps them so executions are
	// serialized against it.
	View *assistanttools.StagedWorkspace
	// Filesystem overrides the filesystem the file tools use; nil means View
	// when set, otherwise the disk.
	Filesystem agent.WorkspaceFS
	// Clock is the datetime tool's clock; nil is the real clock. Evaluations
	// pass a fixed one.
	Clock assistanttools.Clock
	Web   WebBackend
	// Weather defaults to the keyless Open-Meteo provider.
	Weather    assistanttools.WeatherProvider
	Bash       BashBackend
	Delegation DelegationBackend
}

// Tools assembles the tool directory in its canonical order:
//
//	list_files, read_file, search_text            (Files)
//	read_lines, write_file, replace_lines, append_file (Edit)
//	calculator, data_query, datetime              (always)
//	web_search, web_fetch                         (Web)
//	get_weather                                   (Weather)
//	bash                                          (Bash)
//	spawn_agents                                  (Subagents)
//
// The order is part of the prompt (the control prompt lists tools in catalog
// order), so it is fixed here and nowhere else.
func Tools(set ToolSet, b Backends) ([]agent.Tool, error) {
	catalog, err := CanonicalCatalog(set.Catalog)
	if err != nil {
		return nil, err
	}
	switch catalog {
	case AgentToolV2:
		return toolsV2(set, b)
	case "", AgentToolV3:
		return toolsV3(set, b)
	default:
		return nil, fmt.Errorf("tool catalog %s is not an App directory (%s or %s)", catalog, AgentToolV3, AgentToolV2)
	}
}

// toolsV2 is the agent-tool-v2.0 directory, unchanged since the 10-17 exam.
func toolsV2(set ToolSet, b Backends) ([]agent.Tool, error) {
	var filesystem agent.WorkspaceFS
	switch {
	case b.Filesystem != nil:
		filesystem = b.Filesystem
	case b.View != nil:
		filesystem = b.View
	}
	var tools []agent.Tool
	if set.Files {
		files, err := agent.WorkspaceToolsWithFS(b.Workspace, filesystem)
		if err != nil {
			return nil, fmt.Errorf("initialize workspace tools: %w", err)
		}
		tools = append(tools, files...)
	}
	if set.Edit {
		edits, err := assistanttools.FileEditToolsWithFS(b.Workspace, assistanttools.FileEditLines, filesystem)
		if err != nil {
			return nil, fmt.Errorf("initialize edit tools: %w", err)
		}
		tools = append(tools, edits...)
	}
	local, err := assistanttools.LocalTools(assistanttools.Options{
		Clock: b.Clock, Workspace: b.Workspace, Filesystem: filesystem,
	})
	if err != nil {
		return nil, fmt.Errorf("initialize local tools: %w", err)
	}
	tools = append(tools, local...)
	if set.Web {
		search, fetch := b.Web.Search, b.Web.Fetch
		if search == nil {
			search = MissingWebSearch()
		}
		if fetch == nil {
			fetch = MissingWebFetch()
		}
		tools = append(tools, assistanttools.WebTools(assistanttools.WebOptions{
			Search: search, Fetch: fetch,
			FetchBudgetTokens: b.Web.FetchBudgetTokens, TokenCount: b.Web.TokenCount,
		})...)
	}
	if set.Weather {
		weather := b.Weather
		if weather == nil {
			weather, err = assistanttools.NewWeatherProvider(assistanttools.WeatherBackendOpenMeteo)
			if err != nil {
				return nil, err
			}
		}
		tools = append(tools, assistanttools.WeatherTools(weather)...)
	}
	if set.Bash {
		overlay := b.Bash.Overlay
		if overlay == nil {
			overlay = b.View
		}
		bash, err := assistanttools.BashTools(assistanttools.BashOptions{
			Workspace: b.Workspace, Sidecar: b.Bash.Sidecar, Overlay: overlay,
			CatalogOnly: b.Bash.CatalogOnly, ApplyToDisk: b.Bash.ApplyToDisk,
		})
		if err != nil {
			return nil, fmt.Errorf("initialize bash tool: %w", err)
		}
		tools = append(tools, bash...)
	}
	if set.Subagents {
		tools = append(tools, assistanttools.DelegationTools(assistanttools.DelegationOptions{
			MaxParallel: b.Delegation.MaxParallel,
			Timeout:     b.Delegation.Timeout,
			Run:         b.Delegation.Run,
		})...)
	}
	if b.View != nil {
		tools = b.View.WrapTools(tools)
	}
	return tools, nil
}
