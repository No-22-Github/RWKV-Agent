package main

import (
	"context"
	"errors"
	"strings"
	"testing"

	agentapi "github.com/no22/RWKV-Agent/api"
)

func TestFailureExplanationSummarizesToolWork(t *testing.T) {
	result := agentapi.Result{Steps: []agentapi.Step{
		{Tool: "get_weather", ToolArguments: `{"location":"合肥","days":3}`, ToolExecuted: true,
			ToolResult: `{"ok":true,"tool":"get_weather","result":{"location":"合肥，安徽，中国","current":"晴 20°C"}}`},
		{Tool: "web_fetch", ToolArguments: `{"urls":["https://tianqi.example/hefei"]}`, ToolExecuted: true,
			ToolResult: `{"ok":true,"tool":"web_fetch","result":{"pages":[]}}`},
		{Tool: "web_fetch", ToolArguments: `{"urls":["https://tianqi.example/hefei"]}`,
			ToolError: "duplicate tool call rejected"},
		{Stage: "answer", ProtocolError: "agent protocol error: empty G1 answer"},
	}}
	text := failureExplanation(result, errors.New("agent protocol error: empty G1 answer"))
	for _, want := range []string{
		"模型在作答阶段没有写出内容",
		"查询天气「合肥」：成功",
		"读取网页「https://tianqi.example/hefei」：成功，但没拿到内容",
		"读取网页「https://tianqi.example/hefei」：重复调用，已拦下",
		`查询天气：{"current":"晴 20°C","location":"合肥，安徽，中国"}`,
		"技术信息：agent protocol error: empty G1 answer",
	} {
		if !strings.Contains(text, want) {
			t.Fatalf("explanation missing %q:\n%s", want, text)
		}
	}
	if strings.Contains(text, `"pages":[]`) {
		t.Fatalf("empty fetch leaked into the data excerpt:\n%s", text)
	}
}

func TestFailureExplanationKeepsRawErrorWithoutToolWork(t *testing.T) {
	err := errors.New("agent protocol error: empty G1 answer")
	if text := failureExplanation(agentapi.Result{}, err); text != "" {
		t.Fatalf("no-tool failure should keep the raw error, got %q", text)
	}
	withTool := agentapi.Result{Steps: []agentapi.Step{{Tool: "datetime", ToolExecuted: true}}}
	if text := failureExplanation(withTool, context.Canceled); text != "" {
		t.Fatalf("cancelled run should keep the stop message, got %q", text)
	}
}
