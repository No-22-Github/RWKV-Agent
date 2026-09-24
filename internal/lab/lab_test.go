package lab

import (
	"reflect"
	"strings"
	"testing"
)

// P4: Python's str.splitlines() breaks on more than \n, and lint/decontam
// both depend on that. These cases come straight from Python's own behaviour.
func TestSplitLinesMatchesPython(t *testing.T) {
	cases := []struct {
		in   string
		want []string
	}{
		{"", nil},
		{"a", []string{"a"}},
		{"a\n", []string{"a"}},
		{"a\nb", []string{"a", "b"}},
		{"a\r\nb", []string{"a", "b"}},
		{"a\rb", []string{"a", "b"}},
		{"a\vb", []string{"a", "b"}},
		{"a\fb", []string{"a", "b"}},
		{"a\x1cb", []string{"a", "b"}},
		{"a\x1db", []string{"a", "b"}},
		{"a\x1eb", []string{"a", "b"}},
		{"a\u0085b", []string{"a", "b"}},
		{"a b", []string{"a", "b"}},
		{"a b", []string{"a", "b"}},
		{"\n", []string{""}},
		{"\n\n", []string{"", ""}},
		{"a\n\n", []string{"a", ""}},
		{"a\n\nb", []string{"a", "", "b"}},
		{"\r\n", []string{""}},
	}
	for _, tc := range cases {
		got := SplitLines(tc.in)
		if len(got) == 0 && len(tc.want) == 0 {
			continue
		}
		if !reflect.DeepEqual(got, tc.want) {
			t.Errorf("SplitLines(%q) = %q, want %q", tc.in, got, tc.want)
		}
	}
}

// P8: Python's round() is banker's rounding; Go's math.Round is not.
func TestRoundHalfEvenMatchesPython(t *testing.T) {
	cases := []struct {
		x    float64
		n    int
		want float64
	}{
		{0.5, 0, 0},
		{1.5, 0, 2},
		{2.5, 0, 2},
		{3.5, 0, 4},
		{-0.5, 0, -0},
		{-1.5, 0, -2},
		{2.675, 2, 2.67}, // 2.675 is really 2.67499... in binary
		{0.125, 2, 0.12},
		{0.375, 2, 0.38},
		{0.6785714285714286, 4, 0.6786},
		{1.0, 4, 1.0},
		{0.0, 4, 0.0},
	}
	for _, tc := range cases {
		got := RoundHalfEven(tc.x, tc.n)
		if got != tc.want {
			t.Errorf("RoundHalfEven(%v, %d) = %v, want %v", tc.x, tc.n, got, tc.want)
		}
	}
}

// The bank file's bytes depend on ints staying ints and floats staying floats
// (build.py hashes the exact output bytes). json.Number is what keeps that.
func TestEncodeJSONKeepsNumberLiterals(t *testing.T) {
	v, err := DecodeJSON(strings.NewReader(`{"a":9000.0,"b":9000,"c":0.01}`))
	if err != nil {
		t.Fatal(err)
	}
	got, err := EncodeJSON(v, 0)
	if err != nil {
		t.Fatal(err)
	}
	want := `{"a":9000.0,"b":9000,"c":0.01}`
	if string(got) != want {
		t.Errorf("EncodeJSON = %s, want %s", got, want)
	}
}

// P2: Go escapes <, > and & by default; Python with ensure_ascii=False does
// not, and that text goes into the training corpus verbatim.
func TestEncodeJSONDoesNotEscapeHTML(t *testing.T) {
	v := map[string]any{"text": "<tool_call>a & b</tool_call>"}
	got, err := EncodeJSON(v, 0)
	if err != nil {
		t.Fatal(err)
	}
	want := `{"text":"<tool_call>a & b</tool_call>"}`
	if string(got) != want {
		t.Errorf("EncodeJSON = %s, want %s", got, want)
	}
}

func TestEncodeJSONIndent(t *testing.T) {
	v, err := DecodeJSON(strings.NewReader(`[{"a":1}]`))
	if err != nil {
		t.Fatal(err)
	}
	got, err := EncodeJSON(v, 2)
	if err != nil {
		t.Fatal(err)
	}
	want := "[\n  {\n    \"a\": 1\n  }\n]"
	if string(got) != want {
		t.Errorf("EncodeJSON = %q, want %q", got, want)
	}
}
