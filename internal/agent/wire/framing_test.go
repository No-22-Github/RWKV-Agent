package wire

import "testing"

func TestStripLeadingThinkBlocks(t *testing.T) {
	t.Parallel()
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"no block", "hello", "hello"},
		{"one block", "<think>a</think>\nhello", "hello"},
		{"several blocks", "<think>a</think>\n<think>b</think>\nhello", "hello"},
		{"leading whitespace", "  <think>a</think>  hello", "hello"},
		{"unterminated block is left alone", "<think>unclosed", "<think>unclosed"},
		{"block not at the start", "hello <think>a</think>", "hello <think>a</think>"},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			if got := StripLeadingThinkBlocks(testCase.in); got != testCase.want {
				t.Fatalf("StripLeadingThinkBlocks(%q) = %q, want %q", testCase.in, got, testCase.want)
			}
		})
	}
}

func TestTrimWithheldOpening(t *testing.T) {
	t.Parallel()
	cases := []struct {
		name string
		in   string
		want string
	}{
		{"envelope", ">" + EnvelopePrefix + `{"name":"x"}`, EnvelopePrefix + `{"name":"x"}`},
		{"array envelope", "> " + "<tool_calls>[]</tool_calls>", "<tool_calls>[]</tool_calls>"},
		{"prose after the byte is not framing", ">hello", ">hello"},
		{"no withheld byte", "hello", "hello"},
		{"bare object is not an envelope", `>{"name":"x"}`, `>{"name":"x"}`},
	}
	for _, testCase := range cases {
		t.Run(testCase.name, func(t *testing.T) {
			t.Parallel()
			if got := TrimWithheldOpening(testCase.in); got != testCase.want {
				t.Fatalf("TrimWithheldOpening(%q) = %q, want %q", testCase.in, got, testCase.want)
			}
		})
	}
}

func TestAnchorConstantsCompose(t *testing.T) {
	t.Parallel()
	if DeepFencePrefix != FencePrefix+CallBodyAnchor {
		t.Fatalf("DeepFencePrefix = %q", DeepFencePrefix)
	}
	if ArrayCallAnchor != "["+CallBodyAnchor {
		t.Fatalf("ArrayCallAnchor = %q", ArrayCallAnchor)
	}
}
