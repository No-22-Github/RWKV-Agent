package state

import (
	"slices"
	"strings"
	"testing"
)

// --fast carries its own history overrides unless --legacy-history keeps the
// default history wire; the Go port once parsed --legacy-history and dropped
// both, so --fast silently ran with the default history.
func TestWireExperimentCommandFastHistory(t *testing.T) {
	const override = "history=think-fast,thinkcontrol=off"
	cases := []struct {
		name string
		args RunArgs
		want []string // --wire values in order
	}{
		{"default", RunArgs{}, nil},
		{"fast", RunArgs{Fast: true}, []string{override}},
		{"fast legacy history", RunArgs{Fast: true, LegacyHistory: true}, nil},
		{"wire only", RunArgs{Wire: "nudge=none"}, []string{"nudge=none"}},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			cmd := wireExperimentCommand(tc.args, "workbank", "bin", "out", 4)
			var got []string
			for i, arg := range cmd {
				if arg == "--wire" && i+1 < len(cmd) {
					got = append(got, cmd[i+1])
				}
			}
			if !slices.Equal(got, tc.want) {
				t.Fatalf("--wire values = %q, want %q", got, tc.want)
			}
			profile := cmd[slices.Index(cmd, "--profile")+1]
			if strings.HasSuffix(profile, "+think-fast") != tc.args.Fast {
				t.Fatalf("profile %q does not match fast=%v", profile, tc.args.Fast)
			}
		})
	}
}

// The override sits after --state-id and before the stop tokens, the order
// scripts/state-experiment.py produced.
func TestWireExperimentCommandFastOrder(t *testing.T) {
	cmd := wireExperimentCommand(RunArgs{Fast: true, StateID: "s.pth"}, "bfcl", "bin", "out", 4)
	state, wire, stop := slices.Index(cmd, "--state-id"), slices.Index(cmd, "--wire"), slices.Index(cmd, "--api-stop-tokens")
	if !(state < wire && wire < stop) {
		t.Fatalf("order state=%d wire=%d stop=%d in %q", state, wire, stop, cmd)
	}
	if cmd[len(cmd)-2] != "--output" || cmd[len(cmd)-1] != "out" {
		t.Fatalf("command must end with --output out: %q", cmd)
	}
}
