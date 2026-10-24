package agent

import (
	"errors"
	"strings"
	"testing"
)

func TestJoinUserContentKeepsEvidenceLast(t *testing.T) {
	evidence := `<tool_response>{"ok":true,"tool":"read_file","result":"port: 8443"}</tool_response>`
	cases := []struct {
		name, previous, next, want string
		evidenceLast               bool
	}{
		{"merged appends", evidence, "Answer now.", evidence + "\n\nAnswer now.", false},
		{"lead inserts before the response", evidence, "Answer now.", "Answer now.\n\n" + evidence, true},
		{"lead keeps earlier instructions first", "Answer now.\n\n" + evidence, "Tools are unavailable.",
			"Answer now.\n\nTools are unavailable.\n\n" + evidence, true},
		{"lead appends after plain text", "Read a.txt.", "Answer now.", "Read a.txt.\n\nAnswer now.", true},
	}
	for _, tc := range cases {
		if got := joinUserContent(tc.previous, tc.next, tc.evidenceLast); got != tc.want {
			t.Errorf("%s:\n got %q\nwant %q", tc.name, got, tc.want)
		}
	}
}

func TestRetryEchoTruncationAddsNoBlankLine(t *testing.T) {
	// A cut that lands right after a newline must not leave "\n\n" inside the
	// Assistant block; RWKV reads a blank line as the end of the block.
	output := strings.Repeat("x", retryEchoBudget-1) + "\n" + strings.Repeat("y", 50)
	echoed := retryEcho(output, errors.New("invalid"))
	if strings.Contains(echoed, "\n\n") {
		t.Fatalf("echo contains a blank line: %q", echoed[len(echoed)-20:])
	}
	if !strings.HasSuffix(echoed, "x\n[truncated]") {
		t.Fatalf("echo = %q", echoed[len(echoed)-20:])
	}
}
