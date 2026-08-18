package bfcl

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

func TestToResultStringUsesPythonLiteralsAndOriginalNames(t *testing.T) {
	t.Parallel()
	result, err := ToResultString([]toolchat.ToolCall{{
		Name:      "math_tool",
		Arguments: `{"enabled":true,"missing":null,"values":[1,2.5],"nested":{"line":"a\nb"}}`,
	}}, map[string]string{"math_tool": "math.tool"}, LanguagePython)
	if err != nil {
		t.Fatal(err)
	}
	want := `[math.tool(enabled=True, missing=None, values=[1, 2.5], nested={"line": "a\nb"})]`
	if result != want {
		t.Fatalf("result = %q, want %q", result, want)
	}
}

func TestToResultStringPreservesParallelCalls(t *testing.T) {
	t.Parallel()
	result, err := ToResultString([]toolchat.ToolCall{
		{Name: "play", Arguments: `{"artist":"Taylor Swift","duration":20}`},
		{Name: "play", Arguments: `{"artist":"Maroon 5","duration":15}`},
	}, nil, LanguagePython)
	if err != nil {
		t.Fatal(err)
	}
	if result != `[play(artist="Taylor Swift", duration=20), play(artist="Maroon 5", duration=15)]` {
		t.Fatalf("result = %q", result)
	}
}

func TestToResultStringAcceptsUnicodePythonArgumentNames(t *testing.T) {
	t.Parallel()
	result, err := ToResultString([]toolchat.ToolCall{{
		Name: "obtener_cotizacion_de_creditos", Arguments: `{"año_vehiculo":2024}`,
	}}, nil, LanguagePython)
	if err != nil {
		t.Fatal(err)
	}
	if result != `[obtener_cotizacion_de_creditos(año_vehiculo=2024)]` {
		t.Fatalf("result = %q", result)
	}
}

func TestToResultStringRejectsTrailingArgumentJSON(t *testing.T) {
	t.Parallel()
	_, err := ToResultString([]toolchat.ToolCall{{
		Name: "tool", Arguments: `{"value":true} {"extra":false}`,
	}}, nil, LanguagePython)
	if err == nil || !strings.Contains(err.Error(), "unexpected trailing JSON value") {
		t.Fatalf("error = %v", err)
	}
}

func TestWriteResultsUsesOfficialLayout(t *testing.T) {
	t.Parallel()
	directory := t.TempDir()
	if err := WriteResults(directory, "model", []ResultEntry{{
		ID: "live_simple_0-0-0", Category: "live_simple", Result: "[tool(x=True)]", ModelCalls: 1,
	}}); err != nil {
		t.Fatal(err)
	}
	path := filepath.Join(directory, "model", "live", "BFCL_v4_live_simple_result.json")
	data, err := os.ReadFile(path)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(data), `"result":"[tool(x=True)]"`) || !strings.HasSuffix(string(data), "\n") {
		t.Fatalf("result file = %q", data)
	}
}
