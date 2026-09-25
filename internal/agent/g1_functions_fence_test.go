package agent

import (
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// Harness v22: in the md-fence product transcript a fence is framing only
// when it wraps a tool call. Any other fence belongs to the answer.
//
// Before the fix the parser stripped a leading fence and then cut the text at
// the next fence, so a final answer that ended with a fenced table or code
// block reached the scorer truncated to its prose. `corpus paths` compared
// that committed answer with the model's raw output, reported "answer repaired
// by the harness" and discarded the trajectory.

// The regression that motivated the fix: a script-mode answer that shows its
// result in a fenced block must survive byte for byte.
func TestG1ProductAnswerKeepsFencedBlocks(t *testing.T) {
	t.Parallel()
	protocol := G1FunctionProtocol{Product: true}
	answer := "Fixed `statement.py`: the filter compared `status` to \"voided\", not \"void\".\n\n" +
		"The statement now reads:\n\n```\nBergamot Studio,2,43.75\nCorvid Ceramics,2,43.75\n" +
		"TOTAL,5,96.25\n```\n\n`firings/` was left untouched.\n\nDONE"
	action, err := protocol.Parse(answer, continuation.FinishStop)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != ActionTypeFinal {
		t.Fatalf("action type = %q, want a final answer", action.Type)
	}
	if action.Content != answer {
		t.Fatalf("answer was altered\n got: %q\nwant: %q", action.Content, answer)
	}
}

// The same rule for a tagged fence, a fence in the middle of prose, and a
// fence that is the whole answer.
func TestG1ProductAnswerKeepsEveryFenceItWasNotAskedToParse(t *testing.T) {
	t.Parallel()
	protocol := G1FunctionProtocol{Product: true}
	cases := map[string]string{
		"tagged fence":     "Run it like this:\n\n```bash\npython3 -I -S statement.py\n```\n\nDone.",
		"inline fence":     "First ```\nthe old value\n``` was wrong, so I replaced it.",
		"table in a fence": "| batch | status |\n| --- | --- |\n| B-7311 | delivered |",
		"fenced csv":       "```csv\nsupplier,sacks\nNorthline,44\n```",
	}
	for name, answer := range cases {
		t.Run(name, func(t *testing.T) {
			action, err := protocol.Parse(answer, continuation.FinishStop)
			if err != nil {
				t.Fatal(err)
			}
			if action.Type != ActionTypeFinal || action.Content != answer {
				t.Fatalf("answer = %q (type %q), want it unchanged", action.Content, action.Type)
			}
		})
	}
}

// A fence that does wrap a call is still an envelope: with the json tag,
// without it, and after a line of prose.
func TestG1ProductFencedToolCallIsStillAToolCall(t *testing.T) {
	t.Parallel()
	protocol := G1FunctionProtocol{Product: true}
	call := `{"name":"read_file","arguments":{"path":"README.md"}}`
	cases := map[string]string{
		"json tag":    "```json\n" + call + "\n```",
		"bare fence":  "```\n" + call + "\n```",
		"after prose": "I will read the readme first:\n\n```json\n" + call + "\n```",
		"unclosed":    "```json\n" + call,
	}
	for name, value := range cases {
		t.Run(name, func(t *testing.T) {
			action, err := protocol.Parse(value, continuation.FinishStop)
			if err != nil {
				t.Fatal(err)
			}
			if action.Type != ActionTypeTool || action.Name != "read_file" {
				t.Fatalf("action = %+v, want a read_file call", action)
			}
			if string(action.Arguments) != `{"path":"README.md"}` {
				t.Fatalf("arguments = %s", action.Arguments)
			}
		})
	}
}

// A fence around a JSON object that is not a call is answer content: the
// product transcript teaches Markdown answers, and a config snippet is one.
func TestG1ProductFencedDataObjectStaysInTheAnswer(t *testing.T) {
	t.Parallel()
	protocol := G1FunctionProtocol{Product: true}
	answer := "The effective setting is:\n\n```json\n{\"port\": 8431, \"replicas\": 3}\n```"
	action, err := protocol.Parse(answer, continuation.FinishStop)
	if err != nil {
		t.Fatal(err)
	}
	if action.Type != ActionTypeFinal || action.Content != answer {
		t.Fatalf("fenced data object = %+v, want it kept in the answer", action)
	}
}

// A fenced call the parser cannot turn into a call must fail the protocol:
// silently answering with the surrounding prose loses the action the model
// took.
func TestG1ProductBrokenFencedCallNeverBecomesAnAnswer(t *testing.T) {
	t.Parallel()
	protocol := G1FunctionProtocol{Product: true}
	value := "Trying the call now:\n```json\n{\"name\": \"read_file\", \"arguments\": {\"path\":\n```\n"
	action, err := protocol.Parse(value, continuation.FinishStop)
	if err == nil && action.Type == ActionTypeFinal {
		t.Fatalf("broken fenced call became a final answer: %q", action.Content)
	}
}

// A fenced object that spells a call is an envelope even when its values are
// prose, so it fails validation instead of quietly becoming an answer. That
// is the trade this rule makes: a call-shaped object is a call attempt.
func TestG1ProductFencedCallShapedObjectFailsInsteadOfAnswering(t *testing.T) {
	t.Parallel()
	protocol := G1FunctionProtocol{Product: true}
	answer := "Use this snippet:\n\n```json\n{\"name\": \"the field\", \"arguments\": \"none\"}\n```\n"
	action, err := protocol.Parse(answer, continuation.FinishStop)
	if err == nil {
		t.Fatalf("call-shaped fence parsed as %+v, want a protocol failure", action)
	}
	if !strings.Contains(err.Error(), "shape invalid") {
		t.Fatalf("error = %v, want a shape failure", err)
	}
}
