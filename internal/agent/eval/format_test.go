package eval

import "testing"

func TestCheckOutputFormat(t *testing.T) {
	for _, tc := range []struct {
		format, output string
		ok             bool
	}{
		{"json", `{"city": "杭州", "orders": 4}`, true},
		{"json", "Here you go:\n```json\n[1, 2, 3]\n```\nStaged for review.", true},
		{"json", "city: 杭州, orders: 4", false},
		{"json", "```json\n{\"a\": 1,}\n```", false},
		{"markdown_table", "| 城市 | 订单数 |\n|---|---:|\n| 杭州 | 4 |", true},
		{"markdown_table", "城市 | 订单数\n:--- | ---:\n杭州 | 4", true},
		{"markdown_table", "- 杭州：4\n- 苏州：3", false},
		{"zh", "我看了 `config/app.yaml`，超时是 30 秒，用的是 retry_backoff_ms 这个键。", true},
		{"zh", "The timeout in config/app.yaml is 30 seconds.", false},
		{"en", "The timeout in config/app.yaml is 30 seconds, set by 张伟.", true},
		{"en", "超时是 30 秒。", false},
	} {
		if got := checkOutputFormat(tc.output, tc.format) == ""; got != tc.ok {
			t.Errorf("%s %q: ok = %v, want %v", tc.format, tc.output, got, tc.ok)
		}
	}
}
