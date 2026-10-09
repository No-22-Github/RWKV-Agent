package corpus

import (
	"crypto/sha256"
	"reflect"
	"slices"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/lab"
)

func rotationEntry(id string, calls []string) *lab.OrderedMap {
	e := lab.NewOrderedMap()
	e.Set("case_id", id)
	outputs := make([]any, 0, len(calls)+1)
	for _, call := range calls {
		o := lab.NewOrderedMap()
		o.Set("text", `<tool_call>{"name":"`+call+`","arguments":{}}</tool_call>`)
		outputs = append(outputs, o)
	}
	o := lab.NewOrderedMap()
	o.Set("text", "final answer")
	outputs = append(outputs, o)
	e.Set("outputs", outputs)
	return e
}

// The rotation must be a pure function of the row ID, drop only tools the row
// never calls, and leave cases with fewer than two unused tools intact.
func TestRotateCatalogsDeterministicAndSafe(t *testing.T) {
	entry := rotationEntry("tab-5001--p1", []string{"list_files", "read_file", "data_query"})
	cases := []*lab.OrderedMap{om("id", "tab-5001--p1")}
	entries := []*lab.OrderedMap{entry}

	first, err := rotateCatalogs(cases, entries, 1.0, eval.WorkToolCatalogName)
	if err != nil {
		t.Fatal(err)
	}
	if first != 1 {
		t.Fatalf("rotated = %d, want 1", first)
	}
	offeredAny, _ := cases[0].Get("offered_tools")
	offered := lab.StringList(offeredAny)
	catalog := eval.WorkToolCatalogNames()
	for _, used := range []string{"list_files", "read_file", "data_query"} {
		if !slices.Contains(offered, used) {
			t.Errorf("used tool %q was dropped: %v", used, offered)
		}
	}
	if len(offered) != len(catalog)-2 && len(offered) != len(catalog)-3 && len(offered) != len(catalog)-4 {
		t.Errorf("offered = %d tools, want catalog minus 2..4 drops (used tools stay)", len(offered))
	}
	for _, name := range offered {
		if !slices.Contains(catalog, name) {
			t.Errorf("offered tool %q is outside the catalog", name)
		}
	}

	// Same ID -> byte-identical decision on a fresh case object.
	cases2 := []*lab.OrderedMap{om("id", "tab-5001--p1")}
	entries2 := []*lab.OrderedMap{rotationEntry("tab-5001--p1", []string{"list_files", "read_file", "data_query"})}
	if _, err := rotateCatalogs(cases2, entries2, 1.0, eval.WorkToolCatalogName); err != nil {
		t.Fatal(err)
	}
	again, _ := cases2[0].Get("offered_tools")
	if !reflect.DeepEqual(offered, lab.StringList(again)) {
		t.Errorf("rotation is not deterministic: %v vs %v", offered, lab.StringList(again))
	}

	// Different ID -> (almost surely) a different subset; at minimum the two
	// draws must both be valid subsets of the catalog.
	cases3 := []*lab.OrderedMap{om("id", "tab-9999--p1")}
	entries3 := []*lab.OrderedMap{rotationEntry("tab-9999--p1", []string{"list_files"})}
	if _, err := rotateCatalogs(cases3, entries3, 1.0, eval.WorkToolCatalogName); err != nil {
		t.Fatal(err)
	}
	if _, ok := cases3[0].Get("offered_tools"); !ok {
		t.Error("share 1.0 must rotate every eligible case")
	}
}

// A trajectory that already calls nearly everything cannot be narrowed.
func TestRotateCatalogsSkipsFullyUsedTrajectories(t *testing.T) {
	catalog := eval.WorkToolCatalogNames()
	calls := append([]string(nil), catalog...)
	calls = calls[:len(catalog)-1] // one unused tool only
	cases := []*lab.OrderedMap{om("id", "scr-0001--p1")}
	entries := []*lab.OrderedMap{rotationEntry("scr-0001--p1", calls)}
	rotated, err := rotateCatalogs(cases, entries, 1.0, eval.WorkToolCatalogName)
	if err != nil {
		t.Fatal(err)
	}
	if rotated != 0 {
		t.Fatalf("rotated = %d, want 0 (only one unused tool)", rotated)
	}
	if _, ok := cases[0].Get("offered_tools"); ok {
		t.Error("an ineligible case must not gain offered_tools")
	}
}

// Authored per-case subsets (§2.12) win over the render-layer rotation.
func TestRotateCatalogsRespectsAuthoredSubsets(t *testing.T) {
	cases := []*lab.OrderedMap{om("id", "nt-6000--p1", "offered_tools", toOrdered(t, []any{"read_file"}))}
	entries := []*lab.OrderedMap{rotationEntry("nt-6000--p1", nil)}
	rotated, err := rotateCatalogs(cases, entries, 1.0, eval.WorkToolCatalogName)
	if err != nil {
		t.Fatal(err)
	}
	if rotated != 0 {
		t.Fatalf("rotated = %d, want 0 (authored subset wins)", rotated)
	}
}

// share 0.4 must be honored as a probability, not a floor: over a large
// population roughly the right share rotates, and none of the untouched cases
// carries the field.
func TestRotateCatalogsHonorsShare(t *testing.T) {
	var cases, entries []*lab.OrderedMap
	for i := 0; i < 200; i++ {
		id := "row-" + string(rune('a'+i%26)) + string(rune('a'+i/26)) + "000--p1"
		cases = append(cases, om("id", id))
		entries = append(entries, rotationEntry(id, []string{"read_file"}))
	}
	rotated, err := rotateCatalogs(cases, entries, 0.4, eval.WorkToolCatalogName)
	if err != nil {
		t.Fatal(err)
	}
	if rotated < 40 || rotated > 120 {
		t.Errorf("rotated = %d, want roughly 80 for share 0.4", rotated)
	}
	for i, caseObj := range cases {
		_, has := caseObj.Get("offered_tools")
		entryID := stringField(entries[i], "case_id")
		digest := sha256Sum(entryID)
		eligible := float64(digest[0])/255.0 < 0.4
		if eligible && !has {
			t.Errorf("%s was eligible but not rotated", entryID)
		}
		if !eligible && has {
			t.Errorf("%s was not eligible but rotated", entryID)
		}
	}
}

func sha256Sum(s string) []byte {
	sum := sha256.Sum256([]byte(s))
	return sum[:]
}

func TestRotateCatalogsKeepsWorkV2ExtrasOffered(t *testing.T) {
	cases, entries := []*lab.OrderedMap{}, []*lab.OrderedMap{}
	for i := 0; i < 40; i++ {
		id := "fs-9" + string(rune('a'+i%26)) + string(rune('a'+i/26))
		caseObj := lab.NewOrderedMap()
		caseObj.Set("id", id)
		cases = append(cases, caseObj)
		entry := lab.NewOrderedMap()
		entry.Set("case_id", id)
		entry.Set("outputs", []any{})
		entries = append(entries, entry)
	}
	rotated, err := rotateCatalogs(cases, entries, 1.0, eval.WorkV2ToolCatalogName)
	if err != nil || rotated < len(cases)/2 {
		t.Fatalf("rotated %d, err %v", rotated, err)
	}
	for _, caseObj := range cases {
		offered, ok := caseObj.Get("offered_tools")
		if !ok {
			continue // the share draw left this row whole
		}
		names := offered.([]any)
		if !slices.Contains(names, any("bash")) || !slices.Contains(names, any("get_weather")) {
			t.Fatalf("%v dropped a protected work-v2 tool: %v", caseObj, names)
		}
	}
}
