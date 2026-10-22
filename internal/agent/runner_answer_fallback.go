package agent

import (
	"encoding/json"
	"errors"
	"fmt"
	"strings"
	"unicode"
)

// The answer stage used to end in ErrStageViolation once a model kept
// emitting tool calls after tools were withdrawn, so the App user saw a
// protocol error instead of an answer (2026-10-16 probe on g1k-7.2b without
// thinking: 48 of 112 runs). The stage now ends in one of two fallbacks.
const (
	answerFallbackOpener  = "opener"
	answerFallbackSummary = "summary"
)

// errAnswerCommitted tells the turn loop that retryProtocolAction already
// committed a final answer.
var errAnswerCommitted = errors.New("answer committed by the answer-stage fallback")

func taskIsChinese(task string) bool {
	for _, value := range task {
		if unicode.Is(unicode.Han, value) {
			return true
		}
	}
	return false
}

// answerOpener is the prose opening prefilled for the last answer generation.
// A continuation that starts mid-sentence rarely turns into a tool call.
func answerOpener(task string) string {
	if taskIsChinese(task) {
		return "根据上面的工具结果，"
	}
	return "Based on the tool results above,"
}

// answerPlanningMarkers flag prose that announces another tool call rather
// than answering; such text is no better than the call itself.
var answerPlanningMarkers = []string{
	"让我", "我需要", "我将", "我会再", "接下来", "再搜", "再查",
	"let me", "i need to", "i will", "i'll", "next,",
}

// salvageAnswerProse keeps the prose a model wrote before its tool frame when
// it is a real answer. It returns "" when nothing usable precedes the frame.
func salvageAnswerProse(modelAction, opener string) string {
	text := modelAction
	if index := strings.LastIndex(text, "</think>"); index >= 0 {
		text = text[index+len("</think>"):]
	}
	if index := strings.Index(strings.ToLower(text), "<tool_call"); index >= 0 {
		text = text[:index]
	}
	text = strings.TrimSpace(text)
	rest := strings.TrimSpace(strings.TrimPrefix(text, opener))
	if len([]rune(rest)) < 8 {
		return ""
	}
	lower := strings.ToLower(rest)
	for _, marker := range answerPlanningMarkers {
		if strings.Contains(lower, marker) {
			return ""
		}
	}
	return text
}

// answerFallbackSummaryText is the harness-written final answer: what the
// turn looked up, how each lookup came out, and what to do next. It never
// claims a fact; it only reports the tool outcomes.
func answerFallbackSummaryText(task string, steps []Step) string {
	zh := taskIsChinese(task)
	var lines []string
	seen := map[string]bool{}
	gotContent := false
	for _, step := range steps {
		if !step.ToolExecuted || step.ToolRejected != "" || step.Tool == "" {
			continue
		}
		outcome, content := describeToolOutcome(step, zh)
		gotContent = gotContent || content
		line := "- " + step.Tool
		if target := toolTarget(step.ToolArguments); target != "" && zh {
			line += "「" + target + "」"
		} else if target != "" {
			line += ` "` + target + `"`
		}
		if zh {
			line += "：" + outcome
		} else {
			line += ": " + outcome
		}
		if seen[line] {
			continue
		}
		seen[line] = true
		lines = append(lines, line)
		if len(lines) == 8 {
			break
		}
	}
	var out strings.Builder
	switch {
	case len(lines) == 0 && zh:
		return "这次没能给出回答，也没有拿到任何工具结果。请换个说法再试一次。"
	case len(lines) == 0:
		return "I could not produce an answer this time and got no tool results. Please try rephrasing the request."
	case zh:
		out.WriteString("这次没能直接给出回答。我查过的内容：\n")
	default:
		out.WriteString("I could not produce a direct answer this time. What I looked up:\n")
	}
	out.WriteString(strings.Join(lines, "\n"))
	// A single newline: the text is replayed in later turns, and "\n\n" there
	// reads as a block boundary in the RWKV transcript.
	out.WriteString("\n")
	switch {
	case gotContent && zh:
		out.WriteString("工具已经拿到了一些内容，但这次没能据此整理出回答，可以让我再试一次。")
	case zh:
		out.WriteString("没有查到能回答这个问题的信息。你可以换个说法再问，或者提供具体的网址或文件，我再查一次。")
	case gotContent:
		out.WriteString("The tools returned some content, but I could not turn it into an answer this time. You can ask me to try again.")
	default:
		out.WriteString("Nothing I found answers the question. You can rephrase it, or give me a specific URL or file to check.")
	}
	return out.String()
}

// toolTarget names what a call looked at, from the argument most tools key on.
func toolTarget(raw json.RawMessage) string {
	var args map[string]any
	if json.Unmarshal(raw, &args) != nil {
		return ""
	}
	for _, key := range []string{"query", "urls", "url", "path", "location", "command", "expression"} {
		value, ok := args[key]
		if !ok {
			continue
		}
		var text string
		switch typed := value.(type) {
		case string:
			text = typed
		case []any:
			parts := make([]string, 0, len(typed))
			for _, item := range typed {
				parts = append(parts, fmt.Sprint(item))
			}
			text = strings.Join(parts, ", ")
		default:
			continue
		}
		text = strings.TrimSpace(text)
		if runes := []rune(text); len(runes) > 60 {
			text = string(runes[:60]) + "…"
		}
		if text != "" {
			return text
		}
	}
	return ""
}

// describeToolOutcome classifies one executed call and reports whether it
// brought back content the model could have answered from.
func describeToolOutcome(step Step, zh bool) (string, bool) {
	var payload struct {
		OK     bool            `json:"ok"`
		Error  string          `json:"error"`
		Result json.RawMessage `json:"result"`
	}
	if json.Unmarshal(step.ToolResult, &payload) != nil {
		return pick(zh, "有返回结果", "returned a result"), true
	}
	if !payload.OK {
		message := payload.Error
		if runes := []rune(message); len(runes) > 60 {
			message = string(runes[:60]) + "…"
		}
		return pick(zh, "出错（"+message+"）", "failed ("+message+")"), false
	}
	switch step.Tool {
	case "web_search":
		var result struct {
			Results []json.RawMessage `json:"results"`
		}
		_ = json.Unmarshal(payload.Result, &result)
		if len(result.Results) == 0 {
			return pick(zh, "没有结果", "no results"), false
		}
		return pick(zh, fmt.Sprintf("找到 %d 条结果", len(result.Results)), fmt.Sprintf("%d results", len(result.Results))), true
	case "web_fetch":
		var result struct {
			Pages []struct {
				Content   string `json:"content"`
				Truncated bool   `json:"truncated"`
			} `json:"pages"`
		}
		_ = json.Unmarshal(payload.Result, &result)
		for _, page := range result.Pages {
			if page.Truncated || strings.TrimSpace(page.Content) != "" {
				return pick(zh, "拿到了页面正文", "got page text"), true
			}
		}
		return pick(zh, "页面没有正文", "the page had no text"), false
	}
	return pick(zh, "有返回结果", "returned a result"), true
}

func pick(zh bool, chinese, english string) string {
	if zh {
		return chinese
	}
	return english
}
