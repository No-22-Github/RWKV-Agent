package tools

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
)

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

func TestDataQueryAggregatesFiltersAndUsesWorkspaceContainment(t *testing.T) {
	root := t.TempDir()
	if err := os.Mkdir(filepath.Join(root, "notes"), 0o700); err != nil {
		t.Fatal(err)
	}
	data := []byte("{\"event\":\"checkout\",\"status\":\"success\",\"user\":\"u1\",\"amount\":100}\n" +
		"{\"event\":\"checkout\",\"status\":\"success\",\"user\":\"u2\",\"amount\":50}\n" +
		"{\"event\":\"checkout\",\"status\":\"failed\",\"user\":\"u1\",\"amount\":900}\n")
	if err := os.WriteFile(filepath.Join(root, "notes", "expenses.jsonl"), data, 0o600); err != nil {
		t.Fatal(err)
	}
	tools, err := CoreTools(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	query := findTool(t, tools, "data_query")
	value, err := query.Execute(context.Background(), json.RawMessage(`{
		"path":"notes",
		"filter":{"event":"checkout","status":"success"},
		"operation":"sum",
		"field":"amount"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	result := value.(dataQueryResult)
	if result.MatchedRows != 2 || result.Value != float64(150) {
		t.Fatalf("query result = %+v", result)
	}
	distinct, err := query.Execute(context.Background(), json.RawMessage(`{
		"path":"notes",
		"filter":{"event":"checkout","status":"success"},
		"operation":"distinct_count",
		"field":"user"
	}`))
	if err != nil || distinct.(dataQueryResult).Value != 2 {
		t.Fatalf("distinct query result = %+v, error = %v", distinct, err)
	}
	if _, err := query.Execute(context.Background(), json.RawMessage(`{"path":"../outside.jsonl"}`)); !errors.Is(err, agent.ErrInvalidToolArguments) {
		t.Fatalf("escape error = %v, want ErrInvalidToolArguments", err)
	}
}

func TestDataQueryGroupsComputedCSVValues(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "orders.csv"), []byte("sku,qty,unit_price\nSKU-17,3,250\nSKU-42,4,180\nSKU-17,2,299.5\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	tools, err := CoreTools(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	query := findTool(t, tools, "data_query")
	value, err := query.Execute(context.Background(), json.RawMessage(`{
		"path":"orders.csv",
		"group_by":"sku",
		"operation":"sum",
		"expression":"qty*unit_price"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	result := value.(dataQueryResult)
	if len(result.Groups) != 2 || result.Groups[0]["sku"] != "SKU-17" || result.Groups[0]["value"] != float64(1349) {
		t.Fatalf("group result = %+v", result)
	}
}

func TestCalculatorEvaluatesOnlyArithmetic(t *testing.T) {
	tool := calculatorTool{}
	value, err := tool.Execute(context.Background(), json.RawMessage(`{"expression":"(4500*30 + 6200*90) * 0.082 / 365"}`))
	if err != nil {
		t.Fatal(err)
	}
	if value.(calculatorResult).Result <= 0 {
		t.Fatalf("calculator result = %+v", value)
	}
	rounded, err := tool.Execute(context.Background(), json.RawMessage(`{"expression":"round(abs(-2685.9975), 2)","precision":2}`))
	if err != nil || rounded.(calculatorResult).Formatted != "2686.00" {
		t.Fatalf("rounded calculator result = %+v, error = %v", rounded, err)
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
