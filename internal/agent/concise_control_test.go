package agent

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/inference"
)

func TestConciseControlUsesTheOfficialToolsLayout(t *testing.T) {
	specs := []ToolSpec{
		{Name: "list_files", Description: "List files.", Arguments: `{"path":"optional relative directory"}`},
		{Name: "read_file", Description: "Read one file.", Arguments: `{"path":"relative file path"}`},
	}
	for _, control := range []string{"concise", "concise-paths"} {
		prompt := G1Protocol{ConciseControl: control, AlignQwen36: true}.Instructions(specs, inference.ThinkingOff)
		if !strings.HasPrefix(prompt, "Tools:\n[\n") {
			t.Errorf("%s: prompt does not open with the Tools: catalog:\n%s", control, prompt)
		}
		if strings.Contains(prompt, "<think>") || strings.Contains(prompt, "Examples:") {
			t.Errorf("%s: prompt carries the standard control text:\n%s", control, prompt)
		}
		if got := strings.Contains(prompt, "call list_files first"); got != (control == "concise-paths") {
			t.Errorf("%s: path sentence present = %v", control, got)
		}
	}
}
