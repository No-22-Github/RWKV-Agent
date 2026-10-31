package geval

import (
	"context"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
	"testing"

	"github.com/no22/RWKV-Agent/internal/lab/labtest"
)

func TestRenderPromptMatchesThinkSFTFormat(t *testing.T) {
	got := renderPrompt([]Exchange{{User: "q1\n\n  \nmore", Answer: "a1  \n\n\nnext"}}, "q2")
	want := "User: q1\nmore\n\nAssistant: <think></think>a1\nnext\n\nUser: q2\n\nAssistant: <think"
	if got != want {
		t.Fatalf("prompt:\n%q\nwant\n%q", got, want)
	}
	if got := renderPrompt(nil, "hi"); got != "User: hi\n\nAssistant: <think" {
		t.Fatalf("single turn: %q", got)
	}
}

func TestParseOutput(t *testing.T) {
	cases := []struct {
		raw                 string
		think, answer       string
		closed, emptyThinks bool
	}{
		{"<think>plan</think>\nanswer", "plan", "answer", true, false},
		{"<think></think>answer", "", "answer", true, true},
		{"<think>never closes", "never closes", "", false, false},
		{"<think missing bracket", "", "", false, false},
		{"<think>x</think>ans\n\nUser: invented", "x", "ans", true, false},
	}
	for _, c := range cases {
		p := parseOutput(c.raw)
		if p.Think != c.think || p.Answer != c.answer || p.ThinkClosed != c.closed || p.EmptyThink != c.emptyThinks {
			t.Errorf("parseOutput(%q) = %+v", c.raw, p)
		}
	}
}

func TestStratifiedSampleIsDeterministicAndProportional(t *testing.T) {
	var items []Item
	for i := 0; i < 90; i++ {
		stratum := "a"
		if i >= 60 {
			stratum = "b"
		}
		items = append(items, Item{ID: fmt.Sprintf("t/%d", i), Stratum: stratum})
	}
	one := stratifiedSample(items, 30, rngFor("t", "x"))
	two := stratifiedSample(items, 30, rngFor("t", "x"))
	if len(one) != 30 {
		t.Fatalf("len = %d", len(one))
	}
	count := map[string]int{}
	for i := range one {
		if one[i].ID != two[i].ID {
			t.Fatal("sample is not deterministic")
		}
		count[one[i].Stratum]++
	}
	if count["a"] != 20 || count["b"] != 10 {
		t.Fatalf("strata = %v, want a=20 b=10", count)
	}
}

func TestIFEvalCheckers(t *testing.T) {
	type tc struct {
		id   string
		kw   map[string]any
		mode string
		resp string
		want bool
	}
	cases := []tc{
		{"punctuation:no_comma", nil, "en", "no commas here", true},
		{"punctuation:no_comma", nil, "en", "a, b", false},
		{"punctuation:no_comma", nil, "zh", "中文，逗号", false},
		{"punctuation:no_comma", nil, "en", "中文，逗号", true},
		{"change_case:english_lowercase", nil, "en", "all lowercase english text here, nothing else to see", true},
		{"change_case:english_lowercase", nil, "en", "Not lowercase english text here", false},
		{"change_case:english_capital", nil, "en", "THIS IS ALL CAPITAL ENGLISH TEXT FOR THE TEST", true},
		{"length_constraints:number_words", map[string]any{"num_words": "5", "relation": "at least"}, "en", "one two three four five", true},
		{"length_constraints:number_words", map[string]any{"num_words": "5", "relation": "less than"}, "en", "one two three four five", false},
		{"length_constraints:number_words", map[string]any{"num_words": "6", "relation": "at least"}, "zh", "我爱北京天安门", true},
		{"length_constraints:number_words", map[string]any{"num_words": "6", "relation": "at least"}, "en", "我爱北京天安门", false},
		{"length_constraints:number_sentences", map[string]any{"num_sentences": "3", "relation": "at least"}, "en", "One. Two! Mr. Smith came.", true},
		{"length_constraints:number_sentences", map[string]any{"num_sentences": "4", "relation": "less than"}, "en", "One. Two! Mr. Smith came.", true},
		{"length_constraints:number_sentences", map[string]any{"num_sentences": "3", "relation": "at least"}, "zh", "一。二！三？", true},
		{"detectable_format:title", nil, "en", "<<Poem of Joy>>\ntext", true},
		{"detectable_format:title", nil, "en", "<<>> text", false},
		{"detectable_format:number_bullet_lists", map[string]any{"num_bullets": "2"}, "en", "* a\n* b\ntext", true},
		{"detectable_format:number_bullet_lists", map[string]any{"num_bullets": "2"}, "en", "- a\n- b\n- c", false},
		{"detectable_format:number_highlighted_sections", map[string]any{"num_highlights": "2"}, "en", "*one* and **two**", true},
		{"detectable_format:json_format", nil, "en", "```json\n{\"a\": 1}\n```", true},
		{"detectable_format:json_format", nil, "en", "{a: 1}", false},
		{"detectable_format:multiple_sections", map[string]any{"section_spliter": "Section", "num_sections": "2"}, "en", "Section 1\nfoo\nSection 2\nbar", true},
		{"detectable_format:multiple_sections", map[string]any{"section_spliter": "天", "num_sections": "2"}, "zh", "天 1 去故宫\n天 2 去长城", true},
		{"length_constraints:number_paragraphs", map[string]any{"num_paragraphs": "2"}, "en", "p1\n***\np2", true},
		{"length_constraints:number_paragraphs", map[string]any{"num_paragraphs": "2"}, "en", "p1\n***\n***\np2", false},
		{"length_constraints:nth_paragraph_first_word", map[string]any{"num_paragraphs": "2", "nth_paragraph": "2", "first_word": "then"}, "en", "First.\n\nThen, more.", true},
		{"length_constraints:nth_paragraph_first_word", map[string]any{"num_paragraphs": "2", "nth_paragraph": "2", "first_word": "太白金星"}, "zh", "一段。\n\n“太白金星来了”", true},
		{"detectable_content:postscript", map[string]any{"postscript_marker": "P.S."}, "en", "body\nP.S. hi", true},
		{"detectable_content:postscript", map[string]any{"postscript_marker": "P.P.S"}, "en", "body\nP.S. hi", false},
		{"detectable_content:number_placeholders", map[string]any{"num_placeholders": "2"}, "en", "[name] at [address]", true},
		{"keywords:existence", map[string]any{"keywords": []any{"Rain", "sun"}}, "en", "rain and SUN", true},
		{"keywords:frequency", map[string]any{"keyword": "cat", "frequency": "2", "relation": "at least"}, "en", "cat Cat dog", true},
		{"keywords:forbidden_words", map[string]any{"forbidden_words": []any{"dog"}}, "en", "a doghouse", true},
		{"keywords:forbidden_words", map[string]any{"forbidden_words": []any{"dog"}}, "en", "a Dog!", false},
		{"keywords:letter_frequency", map[string]any{"letter": "l", "let_frequency": "3", "let_relation": "at least"}, "en", "LoLl", true},
		{"combination:two_responses", nil, "en", "one\n******\ntwo", true},
		{"combination:two_responses", nil, "en", "same\n******\nsame", false},
		{"combination:repeat_prompt", map[string]any{"prompt_to_repeat": "Say hi."}, "en", "say hi. Hi!", true},
		{"startend:end_checker", map[string]any{"end_phrase": "Any other questions?"}, "en", "text. any other questions?\"", true},
		{"startend:quotation", nil, "en", "\"quoted\"", true},
		{"startend:quotation", nil, "en", "“quoted”", false},
		{"startend:quotation", nil, "zh", "“引号”", true},
		{"detectable_format:constrained_response", nil, "en", "My answer is yes.", true},
		{"detectable_format:constrained_response", nil, "zh", "我的答案是肯定的。", true},
		{"change_case:capital_word_frequency", map[string]any{"capital_frequency": "2", "capital_relation": "at least"}, "en", "USA and NASA are here", true},
		{"language:response_language", map[string]any{"language": "zh-cn"}, "zh", "这是一个完全用中文写成的回答，内容很长。", true},
		{"language:response_language", map[string]any{"language": "en"}, "zh", "这是一个完全用中文写成的回答，内容很长。", false},
		{"language:response_language", map[string]any{"language": "de"}, "en", "Das ist eine Antwort auf Deutsch, und sie ist ziemlich lang geschrieben.", true},
	}
	for _, c := range cases {
		kw := c.kw
		if kw == nil {
			kw = map[string]any{}
		}
		check, err := ifevalChecker(c.id, kw, c.mode)
		if err != nil {
			t.Fatalf("%s: %v", c.id, err)
		}
		if got := check(c.resp); got != c.want {
			t.Errorf("%s/%s(%q) = %v, want %v", c.id, c.mode, c.resp, got, c.want)
		}
	}
}

func TestIFEvalLooseDropsFirstLineAndAsterisks(t *testing.T) {
	item := Item{ID: "ifeval-en/x", Task: TaskIFEvalEN, Instructions: []string{"startend:quotation"}, Kwargs: []map[string]any{{}}}
	res, err := scoreIFEval(item, "Sure, here it is:\n\"quoted\"")
	if err != nil {
		t.Fatal(err)
	}
	if res.Strict[0] || !res.Loose[0] {
		t.Fatalf("got %+v, want strict false loose true", res)
	}
}

func TestAnswerExtraction(t *testing.T) {
	if got := lastBoxed(`so \boxed{\frac{1}{2}} and finally \boxed{x^{2}+1}`); got != `x^{2}+1` {
		t.Errorf("lastBoxed = %q", got)
	}
	if got, boxed := gsm8kPrediction(`total \boxed{\$1,250}`); got != "1250" || !boxed {
		t.Errorf("gsm8k boxed = %q %v", got, boxed)
	}
	if got, boxed := gsm8kPrediction("The answer is 42."); got != "42" || boxed {
		t.Errorf("gsm8k fallback = %q %v", got, boxed)
	}
	for _, c := range []struct {
		pred, gold string
		want       bool
	}{
		{`\dfrac{1}{2}`, `\frac{1}{2}`, true},
		{`0.5`, `\frac12`, true},
		{`1/4`, `\frac{1}{4}`, true},
		{`x = 3`, `3`, true},
		{`10\%`, `10`, true},
		{`90^\circ`, `90`, true},
		{`\left( 3, \frac{\pi}{2} \right)`, `\left( 3, \frac{\pi}{2} \right)`, true},
		{`(3,\frac{\pi}{2})`, `\left( 3, \frac{\pi}{2} \right)`, true},
		{`5`, `6`, false},
		{``, `6`, false},
	} {
		if got := mathEqual(c.pred, c.gold); got != c.want {
			t.Errorf("mathEqual(%q, %q) = %v (%q vs %q)", c.pred, c.gold, got, normalizeMath(c.pred), normalizeMath(c.gold))
		}
	}
	for _, c := range []struct{ in, want string }{
		{"分析……\n答案：B", "B"},
		{"答案是（C）。", "C"},
		{"所以选 D\n答案: **A**", "A"},
		{`\boxed{C}`, "C"},
		{"The answer is (b).", "B"},
		{"B", "B"},
		{"产生了**C. 商业**。\n**解析：**  \n商业独立。", "C"},
		{"无法确定", ""},
	} {
		if got := choicePrediction(c.in); got != c.want {
			t.Errorf("choicePrediction(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestNGramContamination(t *testing.T) {
	if got := ngramTokens("Hello, World 中文ab"); strings.Join(got, "|") != "hello|world|中|文|ab" {
		t.Fatalf("tokens = %v", got)
	}
	text := "one two three four five six seven eight nine ten eleven twelve thirteen fourteen"
	grams := itemNGrams(text)
	if len(grams) != 2 {
		t.Fatalf("grams = %d, want 2", len(grams))
	}
	seen := map[uint64][]int32{grams[0]: {7}, grams[1]: nil}
	c := contamFor(grams, seen, 0.5)
	if c.Hits != 1 || c.Coverage != 0.5 || !c.Flagged || c.BestRow != 7 {
		t.Fatalf("contam = %+v", c)
	}
}

func TestParseRatingAndSignTest(t *testing.T) {
	if got := parseRating("explanation... Rating: [[7.5]]"); got != 7.5 {
		t.Errorf("rating = %v", got)
	}
	if got := parseRating("Rating: [8]"); got != 8 {
		t.Errorf("backup rating = %v", got)
	}
	if got := parseRating("no rating"); got != -1 {
		t.Errorf("missing rating = %v", got)
	}
	if p := signTest(10, 0); p > 0.002 || p < 0.0019 {
		t.Errorf("signTest(10,0) = %v", p)
	}
	if p := signTest(3, 3); p != 1 {
		t.Errorf("signTest(3,3) = %v", p)
	}
}

type fakeGen struct {
	mu    sync.Mutex
	calls int
	fail  map[string]bool
}

func (f *fakeGen) generate(_ context.Context, history []Exchange, user string) (TurnRecord, error) {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.calls++
	if f.fail[user] {
		return TurnRecord{}, errors.New("boom")
	}
	return finishTurn(TurnRecord{Prompt: renderPrompt(history, user), Raw: "<think>t</think>\nanswer to " + user, Finish: "stop"}), nil
}

func TestExecuteResumes(t *testing.T) {
	retryDelay = 0
	dir := t.TempDir()
	items := []Item{
		{ID: "gsm8k/1", Task: TaskGSM8K, Turns: []string{"q1"}},
		{ID: "mtbench-en/2", Task: TaskMTBenchEN, Turns: []string{"q2a", "q2b"}},
		{ID: "gsm8k/3", Task: TaskGSM8K, Turns: []string{"q3"}},
	}
	cfg := RunConfig{Items: "x", ItemsSHA256: "s", Subset: "quick", Model: "m"}
	gen := &fakeGen{fail: map[string]bool{"q3": true}}
	if err := execute(context.Background(), dir, cfg, items, gen, 2); err != nil {
		t.Fatal(err)
	}
	recs, err := loadRecords(filepath.Join(dir, "results.jsonl"))
	if err != nil {
		t.Fatal(err)
	}
	if recs["gsm8k/3"].Error == "" || len(recs["mtbench-en/2"].Turns) != 2 {
		t.Fatalf("records = %+v", recs)
	}
	if p := recs["mtbench-en/2"].Turns[1].Prompt; !strings.Contains(p, "<think></think>answer to q2a\n\nUser: q2b") {
		t.Fatalf("turn 2 prompt lacks history: %q", p)
	}
	// Second pass reruns only the failed item.
	gen2 := &fakeGen{}
	if err := execute(context.Background(), dir, cfg, items, gen2, 2); err != nil {
		t.Fatal(err)
	}
	if gen2.calls != 1 {
		t.Fatalf("resume made %d calls, want 1", gen2.calls)
	}
	recs, _ = loadRecords(filepath.Join(dir, "results.jsonl"))
	if recs["gsm8k/3"].Error != "" {
		t.Fatal("failed item was not retried")
	}
	cfg.Model = "other"
	if err := execute(context.Background(), dir, cfg, items, gen2, 2); err == nil || !strings.Contains(err.Error(), "RESUME REFUSED") {
		t.Fatalf("changed config: err = %v", err)
	}
}

func TestEndWithNewlineRepairsCutLine(t *testing.T) {
	path := filepath.Join(t.TempDir(), "r.jsonl")
	if err := os.WriteFile(path, []byte(`{"id":"a"}`+"\n"+`{"id":"b`), 0o644); err != nil {
		t.Fatal(err)
	}
	fh, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0o644)
	if err != nil {
		t.Fatal(err)
	}
	if err := endWithNewline(fh); err != nil {
		t.Fatal(err)
	}
	fh.Write([]byte(`{"id":"c"}` + "\n"))
	fh.Close()
	recs, err := loadRecords(path)
	if err != nil {
		t.Fatal(err)
	}
	if _, ok := recs["c"]; !ok || len(recs) != 2 {
		t.Fatalf("records = %v", recs)
	}
}

func TestBenchItems(t *testing.T) {
	path := DefaultItemsPath()
	labtest.RequireBench(t, path)
	items, _, err := loadItems(path)
	if err != nil {
		t.Fatal(err)
	}
	want := map[string]int{TaskIFEvalEN: 541, TaskIFEvalZH: 541, TaskMTBenchEN: 80, TaskMTBenchZH: 80,
		TaskGSM8K: 500, TaskMATH500: 200, TaskCEval: 250, TaskCMMLU: 250}
	got, quick, ids := map[string]int{}, 0, map[string]bool{}
	for _, item := range items {
		got[item.Task]++
		if item.Quick {
			quick++
		}
		if ids[item.ID] {
			t.Fatalf("duplicate id %s", item.ID)
		}
		ids[item.ID] = true
		if strings.HasPrefix(item.Task, "ifeval") {
			for i, id := range item.Instructions {
				if _, err := ifevalChecker(id, item.Kwargs[i], "en"); err != nil {
					t.Fatalf("%s: %v", item.ID, err)
				}
			}
		}
		if strings.HasPrefix(item.Task, "mtbench") && len(item.Turns) != 2 {
			t.Fatalf("%s has %d turns", item.ID, len(item.Turns))
		}
	}
	for task, n := range want {
		if got[task] != n {
			t.Errorf("%s: %d items, want %d", task, got[task], n)
		}
	}
	if quick != 814 {
		t.Errorf("quick = %d, want 814", quick)
	}
}
