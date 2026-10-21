package product

import (
	"fmt"
	"strings"
)

// Agent tool catalog versions. The major number changes when what the model
// is told changes (a tool's name, description, arguments or schema; the
// catalog hash changes with it, and training data must be re-rendered). The
// minor number changes when only what the tools do changes (argument
// leniency, notes, error wording): the hash stays, so the version is the only
// record of it. Every run.json records the full version.
//
//	agent-tool-v1.0  was work-v1: the work bank's twelve tools
//	agent-tool-v2.0  was work-v2: v1 + bash + get_weather
//	agent-tool-v3.0  was work-v3 until 2026-10-21 (no longer reproducible)
//	agent-tool-v3.1  work-v3 with the 10-21 behavior fixes (docs/design/agent-tool-v3.md §10–§11)
const (
	AgentToolV1 = "agent-tool-v1.0"
	AgentToolV2 = "agent-tool-v2.0"
	AgentToolV3 = "agent-tool-v3.1"
)

// catalogAliases maps the old work-vN names and the bare major versions to
// the version this code runs. Case files, exam manifests and old commands
// still say work-vN and stay valid; they are read, never rewritten (a case
// file's bytes are part of the exam hash).
var catalogAliases = map[string]string{
	"work-v1": AgentToolV1, "agent-tool-v1": AgentToolV1, AgentToolV1: AgentToolV1,
	"work-v2": AgentToolV2, "agent-tool-v2": AgentToolV2, AgentToolV2: AgentToolV2,
	"work-v3": AgentToolV3, "agent-tool-v3": AgentToolV3, AgentToolV3: AgentToolV3,
}

// retiredCatalogs are versions whose behavior is no longer in the code.
var retiredCatalogs = map[string]string{
	"agent-tool-v3.0": "agent-tool-v3.0 is the work-v3 behavior before the 2026-10-21 fixes and can no longer be run; use " + AgentToolV3,
}

// CanonicalCatalog returns the version a catalog name selects; "" stays ""
// (no fixed catalog).
func CanonicalCatalog(name string) (string, error) {
	key := strings.ToLower(strings.TrimSpace(name))
	if key == "" {
		return "", nil
	}
	if version, ok := catalogAliases[key]; ok {
		return version, nil
	}
	if reason, ok := retiredCatalogs[key]; ok {
		return "", fmt.Errorf("%s", reason)
	}
	return "", fmt.Errorf("unknown tool catalog %q (known: %s, %s, %s; the old names work-v1/v2/v3 also work)", name, AgentToolV1, AgentToolV2, AgentToolV3)
}

// RecordedCatalog reads a catalog name as written in an existing run record:
// work-v3 there means the behavior of its day, v3.0.
func RecordedCatalog(name string) string {
	key := strings.ToLower(strings.TrimSpace(name))
	switch key {
	case "work-v3":
		return "agent-tool-v3.0"
	case "":
		return ""
	}
	if version, ok := catalogAliases[key]; ok {
		return version
	}
	return key
}
