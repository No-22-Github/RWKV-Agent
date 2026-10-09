package agent

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestToolChoiceGuidanceFollowsCatalog(t *testing.T) {
	base := []ToolSpec{{Name: "read_file", Description: "Read a file.", Arguments: `{"path":"p"}`}}
	extended := append(append([]ToolSpec(nil), base...),
		ToolSpec{Name: "bash", Description: "Run a bash command.", Arguments: `{"command":"c"}`},
		ToolSpec{Name: "get_weather", Description: "Get the weather.", Arguments: `{"location":"l","days":"n"}`},
	)
	for name, protocol := range map[string]interface {
		Instructions([]ToolSpec, inference.ThinkingMode) string
	}{
		"g1k":     G1Protocol{AlignQwen36: true, SemanticNoTool: true},
		"md":      G1FunctionProtocol{Product: true, SemanticNoTool: true},
		"xml-raw": G1Protocol{},
	} {
		plain := protocol.Instructions(base, inference.ThinkingOff)
		if strings.Contains(plain, "sandbox") || strings.Contains(plain, "get_weather") {
			t.Fatalf("%s: guidance leaked into a catalog without bash/get_weather:\n%s", name, plain)
		}
		full := protocol.Instructions(extended, inference.ThinkingOff)
		for _, want := range []string{"bash runs in a sandbox", "use get_weather, not web search"} {
			if !strings.Contains(full, want) {
				t.Fatalf("%s: missing %q:\n%s", name, want, full)
			}
		}
		if testing.Verbose() && name == "g1k" {
			t.Log("\n" + full)
		}
	}
	native := toolControlPrompt(G1Protocol{}, extended, inference.ThinkingOff, true)
	if strings.Contains(native, "bash, shell, terminal, and command execution are not available") {
		t.Fatal("native prompt still denies bash while offering it")
	}
}
