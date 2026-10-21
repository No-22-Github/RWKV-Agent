package product

import (
	"strings"
	"testing"
)

func TestCanonicalCatalog(t *testing.T) {
	for name, want := range map[string]string{
		"":                  "",
		"work-v1":           AgentToolV1,
		"work-v2":           AgentToolV2,
		"Work-V3":           AgentToolV3,
		"agent-tool-v2":     AgentToolV2,
		"agent-tool-v3":     AgentToolV3,
		"agent-tool-v3.1":   AgentToolV3,
		" agent-tool-v1.0 ": AgentToolV1,
	} {
		if got, err := CanonicalCatalog(name); err != nil || got != want {
			t.Fatalf("CanonicalCatalog(%q) = %q, %v; want %q", name, got, err, want)
		}
	}
	if _, err := CanonicalCatalog("agent-tool-v3.0"); err == nil || !strings.Contains(err.Error(), "no longer be run") {
		t.Fatalf("v3.0 must be refused as retired: %v", err)
	}
	if _, err := CanonicalCatalog("work-v4"); err == nil || !strings.Contains(err.Error(), AgentToolV3) {
		t.Fatalf("unknown name error = %v", err)
	}
}

func TestRecordedCatalog(t *testing.T) {
	// A run.json written before the rename says work-v3 and ran the v3.0
	// behavior; work-v1/v2 never changed.
	for name, want := range map[string]string{
		"work-v1": AgentToolV1, "work-v2": AgentToolV2, "work-v3": "agent-tool-v3.0",
		AgentToolV3: AgentToolV3, "": "", "custom": "custom",
	} {
		if got := RecordedCatalog(name); got != want {
			t.Fatalf("RecordedCatalog(%q) = %q, want %q", name, got, want)
		}
	}
}

func TestToolsAcceptsOldCatalogNames(t *testing.T) {
	for _, name := range []string{"work-v2", AgentToolV2, "work-v3", AgentToolV3, ""} {
		if _, err := Tools(ToolSet{Files: true, Catalog: name}, Backends{}); err != nil {
			t.Fatalf("Tools(%q): %v", name, err)
		}
	}
	if _, err := Tools(ToolSet{Catalog: "work-v1"}, Backends{}); err == nil {
		t.Fatal("agent-tool-v1.0 is a bank catalog, not an App directory")
	}
}
