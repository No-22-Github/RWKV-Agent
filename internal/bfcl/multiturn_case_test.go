package bfcl

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadMultiTurnCaseAndCatalogAppliesHoldoutAndExclusion(t *testing.T) {
	directory := t.TempDir()
	record := `{"id":"multi_turn_miss_func_0","question":[[{"role":"user","content":"first"}],[],[{"role":"user","content":"third"}]],"initial_config":{"MathAPI":{}},"path":["MathAPI.add"],"involved_classes":["MathAPI"],"missed_function":{"1":["add"]},"excluded_function":["subtract"]}`
	if err := os.WriteFile(filepath.Join(directory, "BFCL_v4_multi_turn_miss_func.json"), []byte(record+"\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	docDir := filepath.Join(directory, "multi_turn_func_doc")
	if err := os.MkdirAll(docDir, 0o700); err != nil {
		t.Fatal(err)
	}
	docs := "{\"name\":\"add\",\"parameters\":{\"type\":\"dict\"}}\n{\"name\":\"subtract\",\"parameters\":{\"type\":\"dict\"}}\n"
	if err := os.WriteFile(filepath.Join(docDir, "math_api.json"), []byte(docs), 0o600); err != nil {
		t.Fatal(err)
	}
	cases, err := LoadMultiTurnSplit(directory, "multi_turn_miss_func")
	if err != nil {
		t.Fatal(err)
	}
	catalog, err := LoadMultiTurnCatalog(directory, cases[0])
	if err != nil {
		t.Fatal(err)
	}
	if names := MultiTurnFunctionNames(catalog.ForTurn(0, nil)); len(names) != 0 {
		t.Fatalf("turn zero names = %q", names)
	}
	if names := MultiTurnFunctionNames(catalog.ForTurn(1, nil)); len(names) != 1 || names[0] != "add" {
		t.Fatalf("holdout names = %q", names)
	}
}

func TestPinnedMultiTurnDataLoadsAll800Cases(t *testing.T) {
	dataDir := filepath.Join("..", "..", "third_party", "gorilla", "berkeley-function-call-leaderboard", "bfcl_eval", "data")
	for _, category := range []string{"multi_turn_base", "multi_turn_long_context", "multi_turn_miss_func", "multi_turn_miss_param"} {
		cases, err := LoadMultiTurnSplit(dataDir, category)
		if err != nil {
			t.Fatal(err)
		}
		if len(cases) != 200 {
			t.Fatalf("%s cases = %d", category, len(cases))
		}
		if _, err := LoadMultiTurnCatalog(dataDir, cases[0]); err != nil {
			t.Fatal(err)
		}
	}
}
