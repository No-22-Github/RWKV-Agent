package agent

import (
	"strings"
	"testing"
)

func TestDelegationRouteExamples(t *testing.T) {
	prompt := G1IProgressiveToolRouteProtocol{}.Instructions([]ToolBundle{
		{Name: ToolBundleWorkspace, Description: "files"},
		{Name: ToolBundleDelegate, Description: "delegate", Delegation: true},
	})
	if !strings.Contains(prompt, "Delegate two subtasks") {
		t.Fatalf("delegation examples missing from route prompt:\n%s", prompt)
	}
}
