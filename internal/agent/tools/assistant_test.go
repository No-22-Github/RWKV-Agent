package tools

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

type fixedClock struct{ now time.Time }

func (c fixedClock) Now() time.Time { return c.now }

func TestMockProviderContract(t *testing.T) {
	Run(t, Suite{
		NewProvider: func(t *testing.T) Provider {
			t.Helper()
			provider, err := DefaultMockProvider()
			if err != nil {
				t.Fatal(err)
			}
			return provider
		},
		ExactValues: true,
	})
}

func TestAssistantToolsRejectInvalidArguments(t *testing.T) {
	provider, err := DefaultMockProvider()
	if err != nil {
		t.Fatal(err)
	}
	tools, err := AssistantTools(Options{Provider: provider, Workspace: t.TempDir()})
	if err != nil {
		t.Fatal(err)
	}
	for _, tool := range tools {
		if _, executeErr := tool.Execute(context.Background(), json.RawMessage(`{"unexpected":true}`)); !errors.Is(executeErr, agent.ErrInvalidToolArguments) {
			t.Errorf("%s error = %v, want ErrInvalidToolArguments", tool.Spec().Name, executeErr)
		}
	}
}

func TestStructuredQueryUsesWorkspaceContainmentAndCurrentWeek(t *testing.T) {
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, "notes"), 0o700); err != nil {
		t.Fatal(err)
	}
	data := []byte("{\"date\":\"2026-08-03\",\"amount\":100}\n" +
		"{\"date\":\"2026-08-04\",\"amount\":50}\n" +
		"{\"date\":\"2026-07-31\",\"amount\":900}\n")
	if err := os.WriteFile(filepath.Join(root, "notes", "expenses.jsonl"), data, 0o600); err != nil {
		t.Fatal(err)
	}
	tools, err := AssistantTools(Options{
		Workspace: root,
		Clock:     fixedClock{now: time.Date(2026, 8, 4, 10, 0, 0, 0, time.FixedZone("CST", 8*60*60))},
	})
	if err != nil {
		t.Fatal(err)
	}
	query := findTool(t, tools, "structured_query")
	value, err := query.Execute(context.Background(), json.RawMessage(`{"path":"notes","filter":"本周","aggregate":"sum"}`))
	if err != nil {
		t.Fatal(err)
	}
	result := value.(structuredQueryResult)
	if result.Total != 150 || len(result.MatchedRows) != 2 || len(result.ExcludedRows) != 1 {
		t.Fatalf("query result = %+v", result)
	}
	if _, err := query.Execute(context.Background(), json.RawMessage(`{"path":"../outside.jsonl","filter":"","aggregate":"sum"}`)); !errors.Is(err, agent.ErrInvalidToolArguments) {
		t.Fatalf("escape error = %v, want ErrInvalidToolArguments", err)
	}
}

func TestStructuredQueryRejectsUnsupportedFilterOperators(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "rows.jsonl"), []byte("{\"date\":\"2026-08-04\",\"amount\":50}\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	tools, err := AssistantTools(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	query := findTool(t, tools, "structured_query")
	for _, filter := range []string{
		"date >= 2026-08-03",
		"date <= 2026-08-04",
		"date != 2026-08-03",
		"date == 2026-08-04",
	} {
		raw, err := json.Marshal(map[string]string{
			"path":      "rows.jsonl",
			"filter":    filter,
			"aggregate": "sum",
		})
		if err != nil {
			t.Fatal(err)
		}
		if _, err := query.Execute(context.Background(), raw); !errors.Is(err, agent.ErrInvalidToolArguments) {
			t.Errorf("filter %q error = %v, want ErrInvalidToolArguments", filter, err)
		}
	}
}

func TestCalculatorEvaluatesOnlyArithmetic(t *testing.T) {
	tool := calculatorTool{}
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"expression":"(4500*30 + 6200*90) * 0.082 / 365"}`))
	if err != nil {
		t.Fatal(err)
	}
	if value.(struct {
		Expression string  `json:"expression"`
		Result     float64 `json:"result"`
	}).Result <= 0 {
		t.Fatalf("calculator result = %+v", value)
	}
	for _, expression := range []string{"1/0", "foo(1)", "1 < 2"} {
		raw, _ := json.Marshal(map[string]string{"expression": expression})
		if _, err := tool.Execute(context.Background(), raw); !errors.Is(err, agent.ErrInvalidToolArguments) {
			t.Errorf("expression %q error = %v", expression, err)
		}
	}
}

func findTool(t *testing.T, tools []agent.Tool, name string) agent.Tool {
	t.Helper()
	for _, tool := range tools {
		if tool.Spec().Name == name {
			return tool
		}
	}
	t.Fatalf("tool %q not found", name)
	return nil
}
