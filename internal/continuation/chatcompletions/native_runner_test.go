//go:build chatcompletions

package chatcompletions

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
)

func TestNativeToolsRunThroughAgentWithOfficialMessageChain(t *testing.T) {
	t.Parallel()
	var requests []requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		var received requestBody
		if err := json.NewDecoder(request.Body).Decode(&received); err != nil {
			t.Error(err)
			return
		}
		requests = append(requests, received)
		writer.Header().Set("Content-Type", "application/json")
		if len(requests) == 1 {
			writeJSON(writer, `{
				"choices":[{"index":0,"message":{"content":null,"reasoning_content":"inspect first","tool_calls":[{
					"id":"call_native_1","type":"function",
					"function":{"name":"native_echo","arguments":"{\"value\":\"hello\"}"}
				}]},"finish_reason":"tool_calls"}]
			}`)
			return
		}
		writeJSON(writer, `{
			"choices":[{"index":0,"message":{"content":"native answer"},"finish_reason":"stop"}]
		}`)
	}))
	defer server.Close()

	client, err := New(Config{
		Endpoint:   server.URL,
		Model:      "native-model",
		PromptMode: PromptNativeChat,
	})
	if err != nil {
		t.Fatal(err)
	}
	runner, err := agent.NewRunner(client, []agent.Tool{nativeEchoTool{}}, agent.Options{
		MaxSteps:                3,
		ProtocolRetries:         1,
		DecisionMaxOutputTokens: 64,
		TracePromptBytes:        -1,
		Generation: continuation.Request{
			MaxOutputTokens: 128,
			Sampling: continuation.Sampling{
				Temperature:  1,
				TopK:         1,
				TopP:         1,
				PenaltyDecay: 1,
			},
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := runner.Run(context.Background(), "Echo hello and answer.")
	if err != nil {
		t.Fatal(err)
	}
	if result.Output != "native answer" || len(result.Steps) != 2 ||
		result.Steps[0].FinishReason != continuation.FinishToolCalls ||
		!result.Steps[0].ToolExecuted {
		t.Fatalf("result = %+v", result)
	}
	if result.Steps[0].Request == nil ||
		!strings.Contains(result.Steps[0].Request.Prompt, `"tool_choice":"required"`) ||
		!strings.Contains(result.Steps[0].Request.Prompt, `"name":"native_echo"`) {
		t.Fatalf("native prompt trace = %+v", result.Steps[0].Request)
	}
	if len(requests) != 2 || len(requests[0].Tools) != 1 ||
		requests[0].ToolChoice != "required" || requests[0].ParallelToolCalls == nil ||
		*requests[0].ParallelToolCalls {
		t.Fatalf("first native request = %+v", requests)
	}
	second := requests[1]
	if second.ToolChoice != "auto" || len(second.Messages) < 4 {
		t.Fatalf("second native request = %+v", second)
	}
	var assistantCall *message
	var toolResult *message
	for index := range second.Messages {
		candidate := &second.Messages[index]
		if candidate.Role == "assistant" && len(candidate.ToolCalls) > 0 {
			assistantCall = candidate
		}
		if candidate.Role == "tool" {
			toolResult = candidate
		}
	}
	if assistantCall == nil || assistantCall.ToolCalls[0].ID != "call_native_1" ||
		assistantCall.ReasoningContent != "inspect first" ||
		assistantCall.Content != nil || toolResult == nil ||
		toolResult.ToolCallID != "call_native_1" || toolResult.Content == nil ||
		strings.Contains(*toolResult.Content, "<tool_result>") ||
		!strings.Contains(*toolResult.Content, `"tool":"native_echo"`) {
		t.Fatalf("native tool history = %+v", second.Messages)
	}
}

type nativeEchoTool struct{}

func (nativeEchoTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "native_echo",
		Description: "Return a value.",
		Arguments:   `{"value":"string"}`,
		Parameters: json.RawMessage(
			`{"type":"object","properties":{"value":{"type":"string"}},"required":["value"],"additionalProperties":false}`,
		),
		Strict: true,
	}
}

func (nativeEchoTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var arguments struct {
		Value string `json:"value"`
	}
	if err := json.Unmarshal(raw, &arguments); err != nil {
		return nil, err
	}
	return map[string]string{"value": arguments.Value}, nil
}
