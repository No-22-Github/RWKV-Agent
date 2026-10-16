package product

import (
	"context"
	"encoding/json"
	"errors"
	"reflect"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/tools"
)

func names(tools []agent.Tool) []string {
	var result []string
	for _, tool := range tools {
		result = append(result, tool.Spec().Name)
	}
	return result
}

func TestToolsCanonicalOrder(t *testing.T) {
	t.Parallel()
	set := AppDefaultToolSet()
	set.Subagents = true
	tools, err := Tools(set, Backends{Workspace: t.TempDir(), Bash: BashBackend{CatalogOnly: true}})
	if err != nil {
		t.Fatal(err)
	}
	want := []string{
		"list_files", "read_file", "search_text",
		"read_lines", "write_file", "replace_lines", "append_file",
		"calculator", "data_query", "datetime",
		"web_search", "web_fetch", "get_weather", "bash", "spawn_agents",
	}
	if got := names(tools); !reflect.DeepEqual(got, want) {
		t.Fatalf("order = %v, want %v", got, want)
	}
}

func TestToolsSwitchesDropGroups(t *testing.T) {
	t.Parallel()
	tools, err := Tools(ToolSet{Files: true}, Backends{})
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"list_files", "read_file", "search_text", "calculator", "data_query", "datetime"}
	if got := names(tools); !reflect.DeepEqual(got, want) {
		t.Fatalf("names = %v, want %v", got, want)
	}
}

func TestMissingWebProvidersAreProviderUnavailable(t *testing.T) {
	t.Parallel()
	tools, err := Tools(ToolSet{Web: true}, Backends{})
	if err != nil {
		t.Fatal(err)
	}
	for _, tool := range tools {
		var raw string
		switch tool.Spec().Name {
		case "web_search":
			raw = `{"query":"x","max_results":2}`
		case "web_fetch":
			raw = `{"urls":["https://example.com/"]}`
		default:
			continue
		}
		_, err := tool.Execute(context.Background(), json.RawMessage(raw))
		if !errors.Is(err, agent.ErrProviderUnavailable) || !strings.Contains(err.Error(), "设置") {
			t.Fatalf("%s error = %v", tool.Spec().Name, err)
		}
	}
}

func TestTaskControlComposition(t *testing.T) {
	t.Parallel()
	if got := TaskControl(true, false, "  "); got != "" {
		t.Fatalf("empty control = %q", got)
	}
	got := TaskControl(false, true, " 用中文 ")
	want := NoWorkspaceControl + "\n\n用中文\n\n" + StagedFileControl
	if got != want {
		t.Fatalf("control = %q", got)
	}
}

func TestMarkdownPostToolHookEmptyFetchAllowsRecovery(t *testing.T) {
	empty := map[string]any{"pages": []tools.WebFetchResult{{URL: "https://example.com", Content: ""}}}
	hook := markdownPostToolHook("web_fetch", nil, empty, nil)
	if strings.Contains(hook, "fetched page content") || !strings.Contains(hook, "could not be read") {
		t.Fatalf("empty fetch hook = %q", hook)
	}
	full := map[string]any{"pages": []tools.WebFetchResult{{Content: "body"}}}
	if hook := markdownPostToolHook("web_fetch", nil, full, nil); !strings.Contains(hook, "fetched page content") {
		t.Fatalf("full fetch hook = %q", hook)
	}
}
