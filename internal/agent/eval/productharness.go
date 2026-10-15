package eval

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/product"
	"github.com/no22/RWKV-Agent/internal/agent/tools"
)

// Product harness names. "app" scores exactly what a new App connection runs;
// "raw" is the same assembly with the duplicate/same-tool rescue switched off,
// so the model's own closing discipline is measured without the safety net.
const (
	ProductHarnessApp = "app"
	ProductHarnessRaw = "raw"
)

// IsProductHarness reports whether name selects the App's assembly.
func IsProductHarness(name string) bool {
	return name == ProductHarnessApp || name == ProductHarnessRaw
}

// productBackends are the evaluation's implementations behind the App tool
// directory: the case workspace through a staged view, the fixed bank clock,
// and the case's web and weather fixtures in place of the live providers.
func productBackends(config Config, workspace string, testCase Case, view *tools.StagedWorkspace) product.Backends {
	fixture := testCase.WebFixture
	if len(fixture) == 0 {
		fixture = config.WebFixture
	}
	web := webFixtureProviders{entries: fixture}
	return product.Backends{
		Workspace: workspace,
		View:      view,
		Clock:     fixedAssistantClock{value: workToolCatalogClock},
		Web: product.WebBackend{
			Search:            web,
			Fetch:             web,
			FetchBudgetTokens: config.FetchBudgetTokens,
			TokenCount:        config.TokenCount,
		},
		Weather: weatherFixtureProvider{entries: testCase.WeatherFixture},
	}
}

// productCaseTools builds one case's tool directory the way an App session
// does: product.Tools over a staged view of the case workspace. The caller
// owns the returned view and must finishProductCase it.
func productCaseTools(config Config, workspace string, testCase Case) ([]agent.Tool, *tools.StagedWorkspace, error) {
	view, err := tools.NewStagedWorkspace(workspace, "")
	if err != nil {
		return nil, nil, fmt.Errorf("staged workspace (needs the just-bash sidecar, scripts/build-justbash.sh): %w", err)
	}
	catalog, err := product.Tools(product.AppDefaultToolSet(), productBackends(config, workspace, testCase, view))
	if err != nil {
		_ = view.Close()
		return nil, nil, err
	}
	catalog, err = narrowOfferedTools(config.ToolCatalog, catalog, testCase)
	if err != nil {
		_ = view.Close()
		return nil, nil, err
	}
	if err := checkToolPolicyCatalog(testCase, catalog); err != nil {
		_ = view.Close()
		return nil, nil, err
	}
	return catalog, view, nil
}

// finishProductCase plays the user confirming every staged change in the App's
// file-changes panel, so the case-level file expectations score what would
// reach the disk. It always closes the view.
func finishProductCase(view *tools.StagedWorkspace) error {
	defer view.Close()
	changes, err := view.Changes()
	if err != nil {
		return fmt.Errorf("list staged changes: %w", err)
	}
	if len(changes) == 0 {
		return nil
	}
	if _, err := view.Resolve(changes, true); err != nil {
		return fmt.Errorf("accept staged changes: %w", err)
	}
	return nil
}

// productCatalogHash pins the schemas of the App directory for the manifest.
func productCatalogHash(tempDir string) string {
	root, err := os.MkdirTemp(tempDir, "rwkv-agent-catalog-")
	if err != nil {
		return ""
	}
	defer os.RemoveAll(root)
	workspace := filepath.Join(root, "workspace")
	if err := os.MkdirAll(workspace, 0o700); err != nil {
		return ""
	}
	backends := productBackends(Config{}, workspace, Case{}, nil)
	backends.Bash.CatalogOnly = true
	catalog, err := product.Tools(product.AppDefaultToolSet(), backends)
	if err != nil {
		return ""
	}
	return workToolCatalogHash(catalog)
}
