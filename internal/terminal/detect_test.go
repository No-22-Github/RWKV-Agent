package terminal

import (
	"strings"
	"testing"
)

func TestParseAndSelectUI(t *testing.T) {
	t.Parallel()

	for _, value := range []string{"auto", "tui", "plain"} {
		if _, err := ParseUIMode(value); err != nil {
			t.Fatalf("ParseUIMode(%q): %v", value, err)
		}
	}
	if _, err := ParseUIMode("pretty"); err == nil {
		t.Fatal("invalid mode accepted")
	}
	if got, err := SelectUI(UIAuto, Capability{Reason: "pipe"}); err != nil || got != UIPlain {
		t.Fatalf("auto fallback = %q, %v", got, err)
	}
	if _, err := SelectUI(UITUI, Capability{Reason: "pipe"}); err == nil {
		t.Fatal("forced TUI accepted a non-interactive terminal")
	}
}

func TestEnvironmentReason(t *testing.T) {
	t.Parallel()

	values := map[string]string{"TERM": "xterm-256color"}
	getenv := func(name string) string { return values[name] }
	if got := environmentReason(getenv); got != "" {
		t.Fatalf("interactive environment rejected: %q", got)
	}
	values["CI"] = "true"
	if got := environmentReason(getenv); !strings.Contains(got, "CI") {
		t.Fatalf("CI reason = %q", got)
	}
	delete(values, "CI")
	values["TERM"] = "dumb"
	if got := environmentReason(getenv); got != "TERM=dumb" {
		t.Fatalf("dumb reason = %q", got)
	}
}

func TestSanitizeModelText(t *testing.T) {
	t.Parallel()

	input := "你好🙂\033[2J\r\tok\x00"
	if got, want := SanitizeModelText(input), "你好🙂    ok"; got != want {
		t.Fatalf("SanitizeModelText = %q, want %q", got, want)
	}
}
