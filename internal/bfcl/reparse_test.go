package bfcl

import (
	"os"
	"path/filepath"
	"testing"
)

func TestReparseTraceUsesSavedContentWithoutModelCalls(t *testing.T) {
	t.Parallel()
	cases := []Case{testBaselineCase("simple_python_0"), testBaselineCase("simple_python_1")}
	source := []TraceEntry{
		{ResultEntry: ResultEntry{ID: "simple_python_0", ModelCalls: 1}, Content: `{"name":"math.tool","arguments":{"value":true}}`},
		{ResultEntry: ResultEntry{ID: "simple_python_1", ModelCalls: 1}, Content: `{"name":"math.tool","arguments":"{\"value\":true}"}`},
	}
	result, err := ReparseTrace(cases, source, ParserRWKVWireCompatV1)
	if err != nil {
		t.Fatal(err)
	}
	if result.ParseFailed != 0 || result.Repaired != 1 ||
		result.RepairCounts[RepairArgumentsUnwrapped] != 1 ||
		result.Entries[0].Result != `[math.tool(value=True)]` ||
		result.Entries[1].Result != `[math.tool(value=True)]` ||
		result.Entries[0].ModelCalls != 1 || result.Entries[1].ModelCalls != 1 {
		t.Fatalf("result = %+v", result)
	}
}

func TestLoadTraceReadsJSONL(t *testing.T) {
	t.Parallel()
	path := filepath.Join(t.TempDir(), "trace.jsonl")
	if err := os.WriteFile(path, []byte("{\"id\":\"one\",\"content\":\"a\"}\n{\"id\":\"two\",\"content\":\"b\"}"), 0o600); err != nil {
		t.Fatal(err)
	}
	entries, err := LoadTrace(path)
	if err != nil {
		t.Fatal(err)
	}
	if len(entries) != 2 || entries[0].ID != "one" || entries[1].Content != "b" {
		t.Fatalf("entries = %+v", entries)
	}
}
