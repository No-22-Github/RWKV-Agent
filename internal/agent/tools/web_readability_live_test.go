package tools

import (
	"context"
	"os"
	"strings"
	"testing"
	"unicode/utf8"
)

// Live smoke for the local reader (work-v3 M2). Network only on request:
//
//	RWKV_LIVE_WEB=1 go test ./internal/agent/tools -run TestReadabilityLive -v
func TestReadabilityLive(t *testing.T) {
	if os.Getenv("RWKV_LIVE_WEB") == "" {
		t.Skip("set RWKV_LIVE_WEB=1 to fetch real pages")
	}
	urls := []string{
		"https://github.com/BlinkDL/RWKV-LM",
		"https://arxiv.org/abs/2305.13048",
		"https://www.gov.cn/",
		"https://hotels.ctrip.com/",
	}
	pages, err := ReadabilityFetch{}.Fetch(context.Background(), WebFetchRequest{URLs: urls})
	if err != nil {
		t.Fatal(err)
	}
	for _, page := range pages {
		head := page.Content
		if len(head) > 160 {
			head = head[:160]
		}
		t.Logf("%s title=%q runes=%d lines=%d head=%q", page.URL, page.Title,
			utf8.RuneCountInString(page.Content), strings.Count(page.Content, "\n")+1, head)
	}
}
