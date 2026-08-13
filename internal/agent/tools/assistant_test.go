package tools

import (
	"context"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strings"
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

func TestLocalToolsExcludeProviderBackedFacts(t *testing.T) {
	tools, err := LocalTools(Options{Workspace: t.TempDir()})
	if err != nil {
		t.Fatal(err)
	}
	names := make(map[string]bool, len(tools))
	for _, tool := range tools {
		names[tool.Spec().Name] = true
	}
	for _, required := range []string{"calculator", "data_query", "datetime"} {
		if !names[required] {
			t.Errorf("local tools are missing %q: %v", required, names)
		}
	}
	for _, forbidden := range []string{"weather", "nearest_transit", "transit_hours", "fx_convert"} {
		if names[forbidden] {
			t.Errorf("local tools unexpectedly expose provider-backed %q: %v", forbidden, names)
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

func TestNarrowTableToolsSelectAndAggregateRows(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "events.jsonl"), []byte(
		"{\"event\":\"checkout\",\"status\":\"success\",\"user\":\"u1\",\"amount\":49.99}\n"+
			"{\"event\":\"checkout\",\"status\":\"failed\",\"user\":\"u2\",\"amount\":19.99}\n"+
			"{\"event\":\"checkout\",\"status\":\"success\",\"user\":\"u2\",\"amount\":80}\n",
	), 0o600); err != nil {
		t.Fatal(err)
	}
	tools, err := TableTools(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	selectTool := findTool(t, tools, "table_select")
	selected, err := selectTool.Execute(context.Background(), json.RawMessage(`{
		"path":"events.jsonl",
		"filter":{"event":"checkout","status":"success"},
		"columns":"user,amount"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	selection := selected.(tableSelectResult)
	if selection.RowsRead != 3 || selection.MatchedRows != 2 || len(selection.Rows) != 2 {
		t.Fatalf("selection = %+v", selection)
	}

	aggregateTool := findTool(t, tools, "table_sum")
	summed, err := aggregateTool.Execute(context.Background(), json.RawMessage(`{
		"path":"events.jsonl",
		"filter":{"event":"checkout","status":"success"},
		"value":"amount"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	summary := summed.(tableAggregateResult)
	if summary.RowsRead != 3 || summary.MatchedRows != 2 || summary.Value != float64(129.99) {
		t.Fatalf("sum = %+v", summary)
	}
	countTool := findTool(t, tools, "table_count")
	distinct, err := countTool.Execute(context.Background(), json.RawMessage(`{
		"path":"events.jsonl",
		"filter":{"event":"checkout","status":"success"},
		"group_by":"user"
	}`))
	if err != nil || distinct.(tableAggregateResult).GroupCount != 2 {
		t.Fatalf("distinct = %+v, error = %v", distinct, err)
	}
}

func TestTableAggregateGroupsExpressionsAndGuidesInvalidFields(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "orders.csv"), []byte(
		"sku,qty,unit_price\nSKU-17,3,250\nSKU-42,4,180\nSKU-17,2,299.5\n",
	), 0o600); err != nil {
		t.Fatal(err)
	}
	tools, err := TableTools(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	aggregateTool := findTool(t, tools, "table_sum")
	value, err := aggregateTool.Execute(context.Background(), json.RawMessage(`{
		"path":"orders.csv",
		"value":"qty*unit_price",
		"group_by":"sku"
	}`))
	if err != nil {
		t.Fatal(err)
	}
	result := value.(tableAggregateResult)
	if result.RowsRead != 3 || len(result.Groups) != 2 ||
		result.Groups[0]["sku"] != "SKU-17" || result.Groups[0]["value"] != float64(1349) {
		t.Fatalf("groups = %+v", result)
	}
	_, err = aggregateTool.Execute(context.Background(), json.RawMessage(`{
		"path":"orders.csv","value":"missing"
	}`))
	if !errors.Is(err, agent.ErrInvalidToolArguments) || !strings.Contains(err.Error(), "available columns: qty, sku, unit_price") {
		t.Fatalf("invalid field error = %v", err)
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

func TestAggregateSumMarshalsCleanDecimal(t *testing.T) {
	rows := []map[string]any{
		{"amount": 49.99}, {"amount": 80.00}, {"amount": 12.50},
		{"amount": 100.25}, {"amount": 63.00}, {"amount": 132.98},
	}
	result, err := aggregateDataRows(rows, []dataQueryAggregate{{Op: "sum", Field: "amount", As: "value"}})
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := json.Marshal(result["value"])
	if err != nil {
		t.Fatal(err)
	}
	if string(encoded) != "438.72" {
		t.Fatalf("aggregated sum marshals as %s, want 438.72", encoded)
	}
}

func TestCleanFloatNoisePreservesSubCentPrecision(t *testing.T) {
	if value := cleanFloatNoise(0.1888); value != 0.1888 {
		t.Fatalf("cleanFloatNoise(0.1888) = %v", value)
	}
	if value := cleanFloatNoise(438.72000000000003); value != 438.72 {
		t.Fatalf("cleanFloatNoise(438.72000000000003) = %v", value)
	}
}
