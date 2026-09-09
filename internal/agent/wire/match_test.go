package wire

import (
	"strings"
	"testing"
)

func TestMatchPreset(t *testing.T) {
	t.Parallel()
	// A concrete loop policy is excluded from the match: a run with real step
	// budgets still reports the preset it started from.
	md, _, err := Resolve("md-v1")
	if err != nil {
		t.Fatal(err)
	}
	md.Loop = Loop{MaxSteps: 6, AnswerMaxOutputTokens: 1024, SameToolRescueLimit: 3}
	name, ok := md.MatchPreset()
	if !ok || name != "md-v1" {
		t.Fatalf("MatchPreset = %q/%v, want md-v1", name, ok)
	}

	// An ad-hoc combination is anonymous but still fully identified. A custom
	// terminal tool is valid and matches no registered preset.
	adHoc := md
	adHoc.Terminal = Terminal("echo")
	if name, ok := adHoc.MatchPreset(); ok {
		t.Fatalf("ad-hoc spec matched preset %q", name)
	}
	if adHoc.Hash() == md.Hash() {
		t.Fatal("ad-hoc and preset must not share a hash")
	}

	// "default" and "xml-v1" have identical axes; the informative name wins.
	xmlName, ok := Default().MatchPreset()
	if !ok || xmlName == "default" {
		t.Fatalf("default axes matched %q/%v, want a non-default preset", xmlName, ok)
	}
}

func TestDocsListPresetsAndRepairs(t *testing.T) {
	t.Parallel()
	docs := DocsMarkdown()
	for _, want := range []string{
		"## Registered presets",
		"## Axis domain",
		"## Recovery vocabulary",
		"## Modifiers",
		"## Override keys",
		"`md-v1`",
		string(RepairNameInferred),
	} {
		if !strings.Contains(docs, want) {
			t.Fatalf("generated docs missing %q", want)
		}
	}
}
