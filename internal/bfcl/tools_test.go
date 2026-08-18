package bfcl

import (
	"encoding/json"
	"testing"
)

func TestNativeToolsMapsNamesAndSchemaTypesRecursively(t *testing.T) {
	t.Parallel()
	entry := Case{
		ID: "multiple_0",
		Functions: []json.RawMessage{json.RawMessage(`{
            "name":"math.tool",
            "description":"nested",
            "parameters":{
                "type":"dict",
                "properties":{
                    "value":{"type":"float"},
                    "items":{"type":"list","items":{"type":"tuple","items":{"type":"any"}}}
                }
            }
        }`)},
	}
	tools, names, err := NativeTools(entry)
	if err != nil {
		t.Fatal(err)
	}
	if len(tools) != 1 || tools[0].Name != "math_tool" || names["math_tool"] != "math.tool" {
		t.Fatalf("tools = %+v names = %+v", tools, names)
	}
	var schema map[string]any
	if err := json.Unmarshal(tools[0].Parameters, &schema); err != nil {
		t.Fatal(err)
	}
	properties := schema["properties"].(map[string]any)
	items := properties["items"].(map[string]any)
	inner := items["items"].(map[string]any)
	leaf := inner["items"].(map[string]any)
	if schema["type"] != "object" || properties["value"].(map[string]any)["type"] != "number" ||
		items["type"] != "array" || inner["type"] != "array" || leaf["type"] != "string" {
		t.Fatalf("schema = %#v", schema)
	}
}

func TestNativeToolsRejectsNameCollisions(t *testing.T) {
	t.Parallel()
	entry := Case{ID: "collision", Functions: []json.RawMessage{
		json.RawMessage(`{"name":"a.b","parameters":{"type":"dict"}}`),
		json.RawMessage(`{"name":"a_b","parameters":{"type":"dict"}}`),
	}}
	if _, _, err := NativeTools(entry); err == nil {
		t.Fatal("expected normalized name collision")
	}
}
