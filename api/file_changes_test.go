package api

import (
	"context"
	assistanttools "github.com/no22/RWKV-Agent/internal/agent/tools"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"io"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestStagedSessionReadsBackBeforeUserApproval(t *testing.T) {
	root := t.TempDir()
	binary, e := assistanttools.ResolveBashSidecar(filepath.Join("..", "local", "bin", "justbash-sidecar"))
	if e != nil {
		t.Skip("build just-bash sidecar first")
	}
	view, e := assistanttools.NewStagedWorkspace(root, binary)
	if e != nil {
		t.Fatal(e)
	}
	defer view.Close()
	service, e := NewService(Options{Workspace: root})
	if e != nil {
		t.Fatal(e)
	}
	cfg, e := normalizeConfig(Config{Provider: ProviderChatCompletions, Model: "scripted", Endpoint: "https://example.test/v1/chat/completions", MaxSteps: 5, AgentProtocol: AgentProtocolXML})
	if e != nil {
		t.Fatal(e)
	}
	service.config = cfg
	outputs := []string{`<tool_call>{"name":"write_file","arguments":{"path":"a.txt","content":"staged value"}}</tool_call>`, `<tool_call>{"name":"read_file","arguments":{"path":"a.txt"}}</tool_call>`, "已暂存待确认。"}
	generator := continuation.GenerateFunc(func(_ context.Context, req continuation.Request, _ continuation.EventSink) (continuation.Result, error) {
		if len(outputs) == 0 {
			t.Fatal("unexpected extra generation")
		}
		if len(outputs) == 1 && !strings.Contains(req.Prompt, "staged value") {
			t.Fatal("native read did not observe staged write")
		}
		if !strings.Contains(req.Prompt, stagedFileControl) {
			t.Fatal("missing staged file contract")
		}
		text := outputs[0]
		outputs = outputs[1:]
		return continuation.Result{Text: text, FinishReason: continuation.FinishStop}, nil
	})
	session, e := newSessionAtDepth(service, generator, io.NopCloser(strings.NewReader("")), root, Status{Model: "scripted"}, 0, view)
	if e != nil {
		t.Fatal(e)
	}
	defer session.Close()
	if _, e = session.Run(context.Background(), "创建 a.txt，再读回内容"); e != nil {
		t.Fatal(e)
	}
	if _, e = os.Stat(filepath.Join(root, "a.txt")); !os.IsNotExist(e) {
		t.Fatal("unapproved write reached disk")
	}
	changes, e := session.FileChanges()
	if e != nil || len(changes) != 1 {
		t.Fatalf("changes %+v %v", changes, e)
	}
	if _, e = session.ResolveFileChanges(changes, true); e != nil {
		t.Fatal(e)
	}
	b, e := os.ReadFile(filepath.Join(root, "a.txt"))
	if e != nil || string(b) != "staged value" {
		t.Fatalf("file %q %v", b, e)
	}
}
