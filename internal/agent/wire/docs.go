package wire

import (
	"fmt"
	"strings"
)

// DocsMarkdown renders the profile table, the axis domain and the recovery
// vocabulary from the registry and the enums. It is embedded between the
// generated markers in docs/wire-configuration.md and compared by a test, so a
// new preset, axis value or repair ID cannot land without the documentation
// following.
func DocsMarkdown() string {
	var out strings.Builder
	out.WriteString("## Registered presets\n\n")
	out.WriteString("| preset | canonical | short |\n| --- | --- | --- |\n")
	for _, name := range Names() {
		spec, _ := Lookup(name)
		fmt.Fprintf(&out, "| `%s` | `%s` | `%s` |\n", name, spec.Canonical(), spec.Short())
	}

	out.WriteString("\n## Axis domain\n\n")
	out.WriteString("| axis | values |\n| --- | --- |\n")
	axes := []struct {
		name   string
		values []string
	}{
		{"format", FormatValues},
		{"transcript", TranscriptValues},
		{"transport", TransportValues},
		{"thinking", ThinkingValues},
		{"prefill", PrefillValues},
		{"abstain", AbstainValues},
		{"terminal", append([]string{string(TerminalNone)}, "any tool name (e.g. submit)")},
		{"route", RouteValues},
		{"catalog", CatalogValues},
		{"control", ControlValues},
		{"feedback", FeedbackValues},
		{"subagent", SubagentFeedbackValues},
		{"firstcall", FirstCallValues},
		{"usermsg", UserMergeValues},
	}
	for _, axis := range axes {
		fmt.Fprintf(&out, "| `%s` | %s |\n", axis.name, "`"+strings.Join(axis.values, "`, `")+"`")
	}

	out.WriteString("\n## Recovery vocabulary\n\n")
	out.WriteString("| transcript | recoveries |\n| --- | --- |\n")
	xmlSpec := Default()
	mdSpec := Default()
	mdSpec.Format = FormatMDFence
	for _, entry := range []struct {
		label string
		spec  Spec
	}{
		{"xml", xmlSpec},
		{"md-fence", mdSpec},
	} {
		ids := make([]string, 0, len(entry.spec.ParseRepairs()))
		for _, repair := range entry.spec.ParseRepairs() {
			ids = append(ids, string(repair))
		}
		fmt.Fprintf(&out, "| `%s` | `%s` |\n", entry.label, strings.Join(ids, "`, `"))
	}

	out.WriteString("\n## Modifiers\n\n")
	fmt.Fprintf(&out, "`%s`\n", strings.Join(ModifierNames(), "`, `"))

	out.WriteString("\n## Override keys\n\n")
	fmt.Fprintf(&out, "`%s`\n", strings.Join(OverrideKeys(), "`, `"))
	return out.String()
}
