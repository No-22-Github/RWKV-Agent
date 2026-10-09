package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"strings"

	agentapi "github.com/no22/RWKV-Agent/api"
)

// Bounds for the failure explanation: enough of each tool result to be useful
// on screen, never a dump of a fetched page.
const (
	failureMaxTools       = 8
	failureMaxDataEntries = 3
	failureExcerptRunes   = 280
)

// failureToolLabels names tools the way the conversation UI does.
var failureToolLabels = map[string]string{
	"get_weather":   "查询天气",
	"web_search":    "搜索网页",
	"web_fetch":     "读取网页",
	"read_file":     "读取文件",
	"read_lines":    "读取文件片段",
	"list_files":    "列出目录",
	"search_text":   "搜索代码",
	"write_file":    "写入文件",
	"append_file":   "追加文件内容",
	"replace_lines": "编辑文件",
	"calculator":    "计算",
	"datetime":      "查询时间",
	"data_query":    "查询表格",
	"spawn_agents":  "派出子 Agent",
}

// failureExplanation turns a failed turn that already ran tools into a
// readable account: what went wrong, which calls ran, and an excerpt of the
// data collected, so the work done so far is not hidden behind a bare protocol
// error. It returns "" when no tool ran (the raw error is already the whole
// story) or the run was cancelled. The runner itself still fails the turn;
// this is presentation only, so benchmarks keep scoring the failure.
func failureExplanation(result agentapi.Result, err error) string {
	if err == nil || errors.Is(err, context.Canceled) {
		return ""
	}
	var calls []agentapi.Step
	for _, step := range result.Steps {
		if strings.TrimSpace(step.Tool) != "" {
			calls = append(calls, step)
		}
	}
	if len(calls) == 0 {
		return ""
	}

	var text strings.Builder
	text.WriteString(failureReason(err))
	text.WriteString("\n\n已经执行的工具调用：\n")
	for index, step := range calls {
		if index == failureMaxTools {
			fmt.Fprintf(&text, "- ……另有 %d 次调用\n", len(calls)-failureMaxTools)
			break
		}
		fmt.Fprintf(&text, "- %s", failureToolLabel(step.Tool))
		if target := primaryArgument(step.ToolArguments); target != "" {
			fmt.Fprintf(&text, "「%s」", target)
		}
		text.WriteString("：")
		text.WriteString(failureStepStatus(step))
		text.WriteString("\n")
	}

	var data []string
	for _, step := range calls {
		if len(data) == failureMaxDataEntries {
			break
		}
		if !step.ToolExecuted || step.ToolError != "" || step.ToolRejected != "" || emptyResult(step.ToolResult) {
			continue
		}
		if excerpt := resultExcerpt(step.ToolResult); excerpt != "" {
			data = append(data, fmt.Sprintf("- %s：%s", failureToolLabel(step.Tool), excerpt))
		}
	}
	if len(data) > 0 {
		text.WriteString("\n已拿到的数据（摘录）：\n")
		text.WriteString(strings.Join(data, "\n"))
		text.WriteString("\n")
	}
	text.WriteString("\n可以点「重试」再跑一次；如果反复失败，试试把需求拆开分步问（例如先查数据，再让我整理或生成内容）。")
	fmt.Fprintf(&text, "\n\n技术信息：%s", err.Error())
	return text.String()
}

func failureReason(err error) string {
	message := err.Error()
	switch {
	case strings.Contains(message, "empty G1 answer"):
		return "这一轮没能生成最终回答：工具调用已经结束，但模型在作答阶段没有写出内容。"
	case strings.Contains(message, "step limit"):
		return "这一轮没能生成最终回答：用完了最大步数，模型仍在调用工具。"
	default:
		return "这一轮没能生成最终回答：模型输出不符合协议，重试后仍然失败。"
	}
}

func failureToolLabel(tool string) string {
	if label, ok := failureToolLabels[tool]; ok {
		return label
	}
	return "调用 " + tool
}

func failureStepStatus(step agentapi.Step) string {
	switch {
	case step.ToolRejected != "" || strings.Contains(step.ToolError, "duplicate"):
		return "重复调用，已拦下"
	case step.ToolError != "":
		return "失败（" + truncateRunes(step.ToolError, 80) + "）"
	case step.ToolExecuted && emptyResult(step.ToolResult):
		return "成功，但没拿到内容"
	case step.ToolExecuted:
		return "成功"
	default:
		return "未执行"
	}
}

// primaryArgument picks the argument that best names one call, mirroring the
// conversation UI's tool rows.
func primaryArgument(raw string) string {
	var arguments map[string]any
	if json.Unmarshal([]byte(raw), &arguments) != nil {
		return ""
	}
	for _, key := range []string{"location", "query", "path", "url", "expression", "op"} {
		if value, ok := arguments[key].(string); ok && strings.TrimSpace(value) != "" {
			return truncateRunes(strings.TrimSpace(value), 60)
		}
	}
	if urls, ok := arguments["urls"].([]any); ok && len(urls) > 0 {
		if first, ok := urls[0].(string); ok {
			if len(urls) > 1 {
				return fmt.Sprintf("%s 等 %d 个", truncateRunes(first, 60), len(urls))
			}
			return truncateRunes(first, 60)
		}
	}
	return ""
}

// resultExcerpt unwraps the {"ok","tool","result"} envelope and returns a
// one-line compact rendering of the result, cut to failureExcerptRunes.
func resultExcerpt(raw string) string {
	var envelope struct {
		Result json.RawMessage `json:"result"`
	}
	payload := []byte(raw)
	if json.Unmarshal(payload, &envelope) == nil && len(envelope.Result) > 0 {
		payload = envelope.Result
	}
	var value any
	if json.Unmarshal(payload, &value) != nil {
		return truncateRunes(strings.Join(strings.Fields(raw), " "), failureExcerptRunes)
	}
	// No HTML escaping: the excerpt is shown as text, and \u003c in place of
	// "<" would only make fetched markup harder to read.
	var compact bytes.Buffer
	encoder := json.NewEncoder(&compact)
	encoder.SetEscapeHTML(false)
	if encoder.Encode(value) != nil {
		return ""
	}
	return truncateRunes(strings.TrimSpace(compact.String()), failureExcerptRunes)
}

// emptyResult reports a call that succeeded without returning anything, e.g.
// web_fetch {"pages":[]} or web_search {"query":…,"results":[]}: every list in
// the result object is empty.
func emptyResult(raw string) bool {
	var envelope struct {
		Result map[string]any `json:"result"`
	}
	if json.Unmarshal([]byte(raw), &envelope) != nil || envelope.Result == nil {
		return false
	}
	lists := 0
	for _, value := range envelope.Result {
		if list, ok := value.([]any); ok {
			if len(list) > 0 {
				return false
			}
			lists++
		}
	}
	return lists > 0
}

func truncateRunes(value string, limit int) string {
	runes := []rune(value)
	if len(runes) <= limit {
		return value
	}
	return string(runes[:limit]) + "…"
}
