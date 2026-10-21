package bench

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	agenteval "github.com/no22/RWKV-Agent/internal/agent/eval"
)

func sumOf(m map[string]int) int {
	sum := 0
	for _, n := range m {
		sum += n
	}
	return sum
}

func TestScaledParallelism(t *testing.T) {
	names := []string{"workbank", "bfcl-product"}

	t.Run("default budget keeps specs", func(t *testing.T) {
		got := scaledParallelism(names, 64)
		if got["workbank"] != 48 || got["bfcl-product"] != 16 {
			t.Fatalf("specs changed at default budget: %v", got)
		}
	})

	t.Run("below specs keeps specs", func(t *testing.T) {
		got := scaledParallelism(names, 32)
		if got["workbank"] != 48 || got["bfcl-product"] != 16 {
			t.Fatalf("specs changed below budget: %v", got)
		}
	})

	t.Run("above specs fills budget", func(t *testing.T) {
		got := scaledParallelism(names, 96)
		if got["workbank"] != 72 || got["bfcl-product"] != 24 {
			t.Fatalf("want 72/24, got %v", got)
		}
		if sum := sumOf(got); sum != 96 {
			t.Fatalf("sum %d != budget 96", sum)
		}
	})

	t.Run("remainder budget keeps spec floors", func(t *testing.T) {
		got := scaledParallelism(names, 65)
		for name, spec := range map[string]int{"workbank": 48, "bfcl-product": 16} {
			if got[name] < spec {
				t.Fatalf("%s got %d < spec floor %d", name, got[name], spec)
			}
		}
		if sum := sumOf(got); sum != 65 {
			t.Fatalf("sum %d != budget 65", sum)
		}
	})

	t.Run("single suite takes full budget", func(t *testing.T) {
		got := scaledParallelism([]string{"workbank"}, 120)
		if got["workbank"] != 120 {
			t.Fatalf("want 120, got %v", got)
		}
	})

	t.Run("p13 suite registered", func(t *testing.T) {
		spec, ok := suites["p13"]
		if !ok {
			t.Fatal("p13 suite not registered")
		}
		if spec.count != 60 || spec.parallelism != 48 || !spec.agentWire {
			t.Fatalf("unexpected p13 spec: %+v", spec)
		}
	})
}

func TestBinaryPathHonorsRWKVCLI(t *testing.T) {
	t.Setenv("RWKV_CLI", "")
	if got := binaryPath(); !strings.HasSuffix(got, filepath.Join("local", "bin", "rwkv-cli")) {
		t.Fatalf("default binaryPath = %q", got)
	}
	pinned := filepath.Join(t.TempDir(), "rwkv-cli-pinned")
	t.Setenv("RWKV_CLI", pinned)
	if got := binaryPath(); got != pinned {
		t.Fatalf("binaryPath = %q, want %q", got, pinned)
	}
}

func TestSweepResumesThroughPartialCheckpoint(t *testing.T) {
	args := SweepArgs{Model: "m", APIURL: "http://endpoint", Arms: []string{"greedy"}}
	cmd := sweepCommand(args, "workbank", "greedy", "out/run-k0")
	if cmd[len(cmd)-1] != "--resume" {
		t.Fatalf("sweep command does not resume: %v", cmd)
	}

	dir := t.TempDir()
	args.Out = dir
	output := filepath.Join(dir, "bench-workbank-greedy-k0")
	partial := agenteval.PartialDir(output)
	if err := os.MkdirAll(partial, 0o755); err != nil {
		t.Fatal(err)
	}
	progress := `{"done": 40, "invalid": 3, "total": 148}`
	if err := os.WriteFile(filepath.Join(partial, "progress.json"), []byte(progress), 0o644); err != nil {
		t.Fatal(err)
	}
	if got := partialProgress(output); got != "resume 37/148" {
		t.Fatalf("partialProgress = %q", got)
	}
	if err := os.MkdirAll(output, 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(output+".log", []byte("x\nresume refused: run configuration differs\n  harness.adapter_id: a -> b\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if reason, refused := resumeRefused(output); !refused || !strings.Contains(reason, "harness.adapter_id") {
		t.Fatalf("resumeRefused = %q, %v", reason, refused)
	}

	// A retry sets the final artifacts and log aside but keeps the checkpoint.
	if err := setAside(&args, output); err != nil {
		t.Fatal(err)
	}
	if _, err := os.Stat(output); !os.IsNotExist(err) {
		t.Fatalf("final output not set aside: %v", err)
	}
	if _, err := os.Stat(filepath.Join(partial, "progress.json")); err != nil {
		t.Fatalf("checkpoint was moved: %v", err)
	}
}

func TestSupportsResumeDetectsOldBuilds(t *testing.T) {
	dir := t.TempDir()
	for name, help := range map[string]string{
		"new": "  -output string\n  -resume\n",
		"old": "  -output string\n",
	} {
		script := "#!/bin/sh\nprintf '" + strings.ReplaceAll(help, "\n", "\\n") + "' >&2\nexit 0\n"
		if err := os.WriteFile(filepath.Join(dir, name), []byte(script), 0o755); err != nil {
			t.Fatal(err)
		}
	}
	if !supportsResume(filepath.Join(dir, "new")) {
		t.Fatal("new build not detected")
	}
	if supportsResume(filepath.Join(dir, "old")) {
		t.Fatal("old build accepted")
	}
}

func TestSweepCoalescesRemoteCalls(t *testing.T) {
	cmd := strings.Join(sweepCommand(SweepArgs{Model: "m", APIURL: "http://endpoint", BatchInflight: 4}, "workbank", "greedy", "out"), " ")
	if !strings.Contains(cmd, "--remote-batch-wait 20ms --remote-batch-max 64 --remote-batch-inflight 4") {
		t.Fatalf("sweep command does not pass the bench coalescing settings: %s", cmd)
	}
}
