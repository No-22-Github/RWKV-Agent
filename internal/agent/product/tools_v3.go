package product

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/agent"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
)

// toolsV3 assembles work-v3 (docs/design/work-v3-tools.md) in the canonical
// order, which is work-v2's minus read_lines:
//
//	list_files, read_file, search_text            (Files)
//	write_file, replace_lines, append_file        (Edit)
//	calculator, data_query, datetime              (always)
//	web_search, web_fetch                         (Web)
//	get_weather                                   (Weather)
//	bash                                          (Bash)
//	spawn_agents                                  (Subagents)
//
// web_fetch archives long pages under .web/: inside the staged view when there
// is one (bash sees them, the file-changes panel does not), otherwise in a
// per-assembly host directory the read tools map ".web/..." onto.
func toolsV3(set ToolSet, b Backends) ([]agent.Tool, error) {
	var filesystem agent.WorkspaceFS
	switch {
	case b.Filesystem != nil:
		filesystem = b.Filesystem
	case b.View != nil:
		filesystem = b.View
	}
	var store assistanttools.PageStore
	options := agent.WorkspaceV3Options{}
	if b.View != nil && b.Workspace != "" {
		b.View.HideFromReview(agent.WebScratchDir)
		store = assistanttools.StagedPageStore{View: b.View}
	} else {
		dir, err := scratchDir()
		if err != nil {
			return nil, err
		}
		options.ScratchDir = dir
		store = assistanttools.DirPageStore{Dir: dir}
	}
	read, edits, err := assistanttools.FileToolsV3(b.Workspace, filesystem, options)
	if err != nil {
		return nil, fmt.Errorf("initialize file tools: %w", err)
	}
	var tools []agent.Tool
	if set.Files {
		workspace, err := agent.WorkspaceToolsV3(b.Workspace, filesystem, options)
		if err != nil {
			return nil, fmt.Errorf("initialize workspace tools: %w", err)
		}
		// workspace is list_files, search_text; read_file sits between them.
		tools = append(tools, workspace[0], read, workspace[1])
	}
	if set.Edit {
		tools = append(tools, edits...)
	}
	local, err := assistanttools.LocalToolsV3(assistanttools.Options{
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
		tools = append(tools, assistanttools.WebToolsV3(assistanttools.WebOptions{
			Search: search, Fetch: fetch, TokenCount: b.Web.TokenCount,
		}, assistanttools.NewWebArchive(store))...)
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

// scratchDir names a fresh host directory for the web archive. It is created
// only when the first long page is saved.
func scratchDir() (string, error) {
	var id [8]byte
	if _, err := rand.Read(id[:]); err != nil {
		return "", err
	}
	return filepath.Join(os.TempDir(), "rwkv-agent-web-"+hex.EncodeToString(id[:])), nil
}
