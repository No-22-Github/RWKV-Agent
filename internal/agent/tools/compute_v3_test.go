package tools

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func calcV3(t *testing.T, expression string) (calculatorResult, error) {
	t.Helper()
	raw, _ := json.Marshal(map[string]any{"expression": expression, "precision": nil})
	value, err := calculatorV3Tool{}.Execute(context.Background(), raw)
	if err != nil {
		return calculatorResult{}, err
	}
	return value.(calculatorResult), nil
}

func TestCalculatorV3Functions(t *testing.T) {
	for expression, want := range map[string]float64{"sqrt(2)*sqrt(2)": 2, "pow(2,10)": 1024, "round(pow(1.05,12),4)": 1.7959, "log10(1000)": 3, "ln(exp(1))": 1} {
		got, err := calcV3(t, expression)
		if err != nil || got.Result < want-1e-9 || got.Result > want+1e-9 {
			t.Fatalf("%s = %v, %v; want %v", expression, got.Result, err, want)
		}
	}
	for _, expression := range []string{"integrate(x)", "2^10", "2**3"} {
		if _, err := calcV3(t, expression); err == nil || !strings.Contains(err.Error(), "awk") {
			t.Fatalf("%s error lacks the bash hint: %v", expression, err)
		}
	}
	// work-v2 stays strict.
	raw := json.RawMessage(`{"expression":"sqrt(4)","precision":null}`)
	if _, err := (calculatorTool{}).Execute(context.Background(), raw); err == nil {
		t.Fatal("work-v2 calculator accepted sqrt")
	}
}

func TestDataQueryV3Relaxed(t *testing.T) {
	root := t.TempDir()
	if err := os.WriteFile(filepath.Join(root, "orders.csv"), []byte("sku,qty,price\na,2,3\nb,5,1\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	tools, err := LocalToolsV3(Options{Workspace: root})
	if err != nil {
		t.Fatal(err)
	}
	query := tools[1]
	run := func(args string) (map[string]any, error) {
		value, err := query.Execute(context.Background(), json.RawMessage(args))
		if err != nil {
			return nil, err
		}
		data, _ := json.Marshal(value)
		var out map[string]any
		_ = json.Unmarshal(data, &out)
		return out, nil
	}
	got, err := run(`{"path":"orders.csv","operation":"sum","field":"qty","expression":"qty*price"}`)
	if err != nil || got["value"].(float64) != 11 || got["ignored"] != "field" {
		t.Fatalf("sum with both = %v, %v", got, err)
	}
	got, err = run(`{"path":"orders.csv","operation":"count","field":"qty"}`)
	if err != nil || got["value"].(float64) != 2 || got["ignored"] != "field" {
		t.Fatalf("count with field = %v, %v", got, err)
	}
	if _, err := run(`{"path":"orders.csv","operation":"avg"}`); err == nil || !strings.Contains(err.Error(), "需要 field") {
		t.Fatalf("avg without field: %v", err)
	}
}
