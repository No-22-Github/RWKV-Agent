package agent

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"sync/atomic"
	"testing"
	"time"

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

func TestStripEchoPrefix(t *testing.T) {
	cases := map[string]string{
		// Measured P5-ZH echo form: blockquote + meta intro line + content.
		">根据您提供的文本，以下是所有句子的逐句复制：\n青崖湖天文台2024年访客量为8347人次。": "青崖湖天文台2024年访客量为8347人次。",
		// Echo intro without blockquote.
		"以下是相关总结：\n年访客量为6412人次。": "年访客量为6412人次。",
		// English echo.
		"Here is the summary:\nAnnual visitors: 2951.": "Annual visitors: 2951.",
		// A content line that merely STARTS with 根据 but has no colon end stays.
		"根据2024年运营摘要，年访客量为5109人次，该数字已经监督委员会核实。": "根据2024年运营摘要，年访客量为5109人次，该数字已经监督委员会核实。",
		// No echo at all.
		"年访客量 4620 人次。": "年访客量 4620 人次。",
	}
	for input, want := range cases {
		if got := stripEchoPrefix(input); got != want {
			t.Errorf("stripEchoPrefix(%q) = %q, want %q", input, got, want)
		}
	}
}

func TestIsDegenerateCompression(t *testing.T) {
	// Real loop forms from the P5-ZH probe (calibration corpus).
	loopBlock := strings.Repeat("**原文句子：**\n“青崖湖天文台2024年访客量为8347人次。”\n**翻译：**\nThe visitors were 8,347.\n", 6)
	if !isDegenerateCompression(loopBlock) {
		t.Fatal("multi-line block loop not detected")
	}
	loopLines := ">根据金顶岭天文台2024年度运营摘要，以下是相关数字：\n" +
		strings.Repeat("- 月球绕地球的轨道平均速度：1.022 km/s\n", 20)
	if !isDegenerateCompression(loopLines) {
		t.Fatal("identical-line loop not detected")
	}
	clean := "青崖湖天文台位于广东省。2024年访客量为8347人次，该数字已核实。数字来自年度运营摘要。"
	if isDegenerateCompression(clean) {
		t.Fatal("clean three-sentence summary flagged as degenerate")
	}
	distinctExtract := ""
	for i := 0; i < 8; i++ {
		distinctExtract += fmt.Sprintf("The survey team published report number %d with revised figures for quadrant %d.\n", i, i*i)
	}
	if isDegenerateCompression(distinctExtract) {
		t.Fatal("clean verbatim extract flagged as degenerate")
	}
	if isDegenerateCompression("") {
		t.Fatal("empty output must not be flagged (handled as failure separately)")
	}
}

func TestCompressionPromptLanguageSwitch(t *testing.T) {
	en := compressionPrompt("find the number", "The observatory reported 4620 visitors in 2024. Another sentence here.")
	if !strings.Contains(en, englishExtractInstruction) {
		t.Fatal("English page must use the extract instruction")
	}
	zh := compressionPrompt("查找年访客量", "青崖湖天文台位于广东省广州市。2024年访客量为8347人次。该数字已经监督委员会核实。")
	if !strings.Contains(zh, chineseExtractInstruction) {
		t.Fatal("Chinese page must use the content-locked summary instruction")
	}
	if !strings.HasSuffix(zh, compressionFastThinkSuffix) {
		t.Fatal("compression prompt must keep the fast-think prefill (P5-3)")
	}
}

func TestCompressWebFetchFeedbackParallelPreservesOrder(t *testing.T) {
	var counter atomic.Int64
	runner := &Runner{
		generator: continuation.GenerateFunc(func(
			_ context.Context, _ continuation.Request, _ continuation.EventSink,
		) (continuation.Result, error) {
			return continuation.Result{
				Text: fmt.Sprintf("extract %d", counter.Add(1)),
			}, nil
		}),
		options: Options{
			CompressFetch: true,
			TokenCount: func(text string) int {
				if len(text) < 50 {
					return 10
				}
				return 5000
			},
		},
	}
	turn := &runnerTurn{r: runner, ctx: context.Background(), task: "task"}
	payload := `{"ok":true,"result":{"pages":[` +
		`{"url":"https://a.example","content":"` + strings.Repeat("a", 100) + `"},` +
		`{"url":"https://b.example","content":"short"},` +
		`{"url":"https://c.example","content":"` + strings.Repeat("c", 100) + `"}]}}`
	got, changed := turn.compressWebFetchFeedback(turn.ctx, payload)
	if !changed {
		t.Fatal("expected compression to change the payload")
	}
	var parsed struct {
		Result struct {
			Pages []struct {
				URL       string `json:"url"`
				Content   string `json:"content"`
				Truncated bool   `json:"truncated,omitempty"`
			} `json:"pages"`
		} `json:"result"`
	}
	if err := json.Unmarshal([]byte(got), &parsed); err != nil {
		t.Fatalf("decode: %v", err)
	}
	pages := parsed.Result.Pages
	if pages[0].Content == "short" || len(pages[0].Content) == 100 {
		t.Fatalf("page 0 not replaced: %q", pages[0].Content)
	}
	if pages[1].Content != "short" || pages[1].Truncated {
		t.Fatalf("below-threshold page must stay untouched: %+v", pages[1])
	}
	if pages[0].URL != "https://a.example" || pages[2].URL != "https://c.example" {
		t.Fatal("page order changed")
	}
}

func TestCompressionDetachedTimeout(t *testing.T) {
	saved := fetchCompressionTimeout
	fetchCompressionTimeout = 50 * time.Millisecond
	defer func() { fetchCompressionTimeout = saved }()

	runner := &Runner{
		generator: continuation.GenerateFunc(func(
			ctx context.Context, _ continuation.Request, _ continuation.EventSink,
		) (continuation.Result, error) {
			// Hang until the (detached, short) call context times out.
			<-ctx.Done()
			return continuation.Result{}, ctx.Err()
		}),
		options: Options{
			CompressFetch: true,
			TokenCount:    func(string) int { return 5000 },
		},
	}
	turn := &runnerTurn{r: runner, ctx: context.Background(), task: "task"}
	payload := compressionPage(strings.Repeat("page body ", 200))
	got, changed := turn.compressWebFetchFeedback(turn.ctx, payload)
	if changed {
		t.Fatal("timed-out compression must fail open, keeping the original page")
	}
	if got != payload {
		t.Fatal("payload must be unchanged after compression timeout")
	}
}

func TestStripEchoPrefixDoesNotEatContent(t *testing.T) {
	// Two echo lines are stripped, the third line (no colon ending) stays.
	input := ">根据您提供的文本：\n以下是相关内容：\n年访客量为1875人次。"
	want := "年访客量为1875人次。"
	if got := stripEchoPrefix(input); got != want {
		t.Fatalf("stripEchoPrefix = %q, want %q", got, want)
	}
}
