package agent

import (
	"context"
	"encoding/json"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
)

// compressionPage builds the web_fetch payload with one page of the given text.
func compressionPage(content string) string {
	encoded, _ := json.Marshal(content)
	return `{"ok":true,"result":{"pages":[{"url":"https://example.com/page","content":` +
		string(encoded) + `}]}}`
}

func fakeGenerator(text string) continuation.Generator {
	return continuation.GenerateFunc(func(
		context.Context, continuation.Request, continuation.EventSink,
	) (continuation.Result, error) {
		return continuation.Result{Text: text, FinishReason: continuation.FinishStop}, nil
	})
}

func TestCompressWebFetchFeedbackRequiresRealCounter(t *testing.T) {
	runner := &Runner{options: Options{CompressFetch: true}}
	turn := &runnerTurn{r: runner, ctx: context.Background(), task: "find the number"}
	payload := compressionPage(strings.Repeat("page body ", 1000))
	got, changed := turn.compressWebFetchFeedback(turn.ctx, payload)
	if changed {
		t.Fatal("compression armed without Options.TokenCount; it must never arm on the estimator")
	}
	if got != payload {
		t.Fatal("payload changed without Options.TokenCount")
	}
}

func TestCompressWebFetchFeedbackUsesRealCount(t *testing.T) {
	pages := map[string]int{"below": 100, "above": 5000}
	runner := &Runner{
		generator: fakeGenerator("extracted sentence"),
		options: Options{
			CompressFetch: true,
			TokenCount: func(text string) int {
				if strings.Contains(text, "below") {
					return pages["below"]
				}
				return pages["above"]
			},
		},
	}
	turn := &runnerTurn{r: runner, ctx: context.Background(), task: "find the number"}

	below := compressionPage("a page below the threshold that mentions below")
	if _, changed := turn.compressWebFetchFeedback(turn.ctx, below); changed {
		t.Fatal("page counted under the threshold must not be compressed")
	}

	above := compressionPage("a page above the threshold that mentions above")
	got, changed := turn.compressWebFetchFeedback(turn.ctx, above)
	if !changed {
		t.Fatal("page counted over the threshold must be compressed")
	}
	if !strings.Contains(got, `"content":"extracted sentence"`) {
		t.Fatalf("compressed content missing from feedback: %s", got)
	}
	if !strings.Contains(got, `"truncated":true`) {
		t.Fatalf("truncated flag missing from feedback: %s", got)
	}
}
