//go:build chatcompletions

package chatcompletions

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

func validRequest() continuation.Request {
	seed := int64(42)
	return continuation.Request{
		Prompt:          "User: inspect the repository\n\nAssistant:",
		MaxOutputTokens: 321,
		Stops:           []string{"\nUser:", "\nSystem:"},
		Sampling: continuation.Sampling{
			Temperature:      0.8,
			TopK:             12,
			TopP:             0.7,
			PresencePenalty:  1.2,
			FrequencyPenalty: 0.2,
			PenaltyDecay:     0.996,
			Seed:             &seed,
		},
	}
}

func validToolChatRequest() toolchat.Request {
	return toolchat.Request{
		Messages: []toolchat.Message{
			{Role: toolchat.RoleSystem, Content: "Use tools when needed."},
			{Role: toolchat.RoleUser, Content: "Read README.md."},
		},
		Tools: []toolchat.Tool{{
			Name:        "read_file",
			Description: "Read one file.",
			Parameters:  json.RawMessage(`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`),
			Strict:      true,
		}},
		ToolChoice:      toolchat.ToolChoiceRequired,
		MaxOutputTokens: 128,
		Sampling:        validRequest().Sampling,
	}
}

func TestClientMapsContinuationRequestAndResponse(t *testing.T) {
	t.Parallel()
	var received requestBody
	var receivedFields map[string]json.RawMessage
	var authorization string
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		authorization = request.Header.Get("Authorization")
		body, err := io.ReadAll(request.Body)
		if err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &received); err != nil {
			t.Error(err)
		}
		if err := json.Unmarshal(body, &receivedFields); err != nil {
			t.Error(err)
		}
		writer.Header().Set("Content-Type", "application/json")
		writeJSON(writer, `{
            "choices":[{"index":0,"message":{"role":"assistant","content":"done"},"finish_reason":"stop"}],
            "usage":{"prompt_tokens":12,"completion_tokens":4}
        }`)
	}))
	defer server.Close()

	client, err := New(Config{
		Endpoint: server.URL + "/v1/chat/completions",
		Model:    "other-model",
		APIKey:   "secret",
	})
	if err != nil {
		t.Fatal(err)
	}
	var delta string
	result, err := client.Continue(
		context.Background(),
		validRequest(),
		func(event continuation.Event) error {
			delta += event.Text
			return nil
		},
	)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != "done" || result.FinishReason != continuation.FinishStop ||
		result.Usage.PromptTokens != 12 || result.Usage.CompletionTokens != 4 ||
		delta != "done" {
		t.Fatalf("result = %+v, delta = %q", result, delta)
	}
	if received.Model != "other-model" || received.MaxCompletionTokens != 321 || received.Stream ||
		len(received.Messages) != 2 || received.Messages[0].Role != "system" ||
		received.Messages[1].Role != "user" || received.Messages[1].Content == nil ||
		*received.Messages[1].Content != validRequest().Prompt ||
		received.Temperature != 0.8 || received.TopP != 0.7 ||
		received.PresencePenalty != 1.2 || received.FrequencyPenalty != 0.2 ||
		received.Seed == nil || *received.Seed != 42 {
		t.Fatalf("request = %+v", received)
	}
	if authorization != "Bearer secret" {
		t.Fatalf("authorization = %q", authorization)
	}
	if _, exists := receivedFields["top_k"]; exists {
		t.Fatal("request unexpectedly included nonstandard top_k")
	}
	if _, exists := receivedFields["penalty_decay"]; exists {
		t.Fatal("request unexpectedly included nonstandard penalty_decay")
	}
	if _, exists := receivedFields["thinking"]; exists {
		t.Fatal("default request unexpectedly included provider-specific thinking")
	}
}

func TestClientMapsOptionalThinkingMode(t *testing.T) {
	t.Parallel()
	var received requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if err := json.NewDecoder(request.Body).Decode(&received); err != nil {
			t.Error(err)
		}
		writeJSON(writer, `{"choices":[{"index":0,"message":{"content":"ok"},"finish_reason":"stop"}]}`)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint: server.URL,
		Model:    "reasoning-model",
		Thinking: ThinkingDisabled,
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Continue(context.Background(), validRequest(), nil); err != nil {
		t.Fatal(err)
	}
	if received.Thinking == nil || received.Thinking.Type != ThinkingDisabled {
		t.Fatalf("thinking = %+v", received.Thinking)
	}
}

func TestClientSupportsLegacyMaxTokensCompatibility(t *testing.T) {
	t.Parallel()
	var received requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if err := json.NewDecoder(request.Body).Decode(&received); err != nil {
			t.Error(err)
		}
		writeJSON(writer, `{"choices":[{"index":0,"message":{"content":"ok"},"finish_reason":"stop"}]}`)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint:   server.URL,
		Model:      "legacy-compatible-model",
		TokenLimit: TokenLimitMaxTokens,
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Continue(context.Background(), validRequest(), nil); err != nil {
		t.Fatal(err)
	}
	if received.MaxTokens != validRequest().MaxOutputTokens || received.MaxCompletionTokens != 0 {
		t.Fatalf("token limits = max_tokens:%d max_completion_tokens:%d", received.MaxTokens, received.MaxCompletionTokens)
	}
}

func TestClientMapsNativeToolsCallsAndResults(t *testing.T) {
	t.Parallel()
	var received requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if err := json.NewDecoder(request.Body).Decode(&received); err != nil {
			t.Error(err)
		}
		writeJSON(writer, `{
            "choices":[{
                "index":0,
                "message":{"content":null,"tool_calls":[{
                    "id":"call_new","type":"function",
                    "function":{"name":"read_file","arguments":"{\"path\":\"README.md\"}"}
                }]},
                "finish_reason":"tool_calls"
            }]
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
	request := toolchat.Request{
		Messages: []toolchat.Message{
			{Role: toolchat.RoleSystem, Content: "Choose exactly one action."},
			{Role: toolchat.RoleUser, Content: "Read README.md."},
			{Role: toolchat.RoleAssistant, ToolCalls: []toolchat.ToolCall{{
				ID: "call_old", Name: "list_files", Arguments: `{"path":null,"max_depth":1,"max_results":20}`,
			}}},
			{Role: toolchat.RoleTool, ToolCallID: "call_old", Content: `{"ok":true}`},
			{Role: toolchat.RoleUser, Content: "Continue the task."},
		},
		Tools: []toolchat.Tool{{
			Name:        "read_file",
			Description: "Read one file.",
			Parameters:  json.RawMessage(`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`),
			Strict:      true,
		}},
		ToolChoice:        toolchat.ToolChoiceRequired,
		MaxOutputTokens:   128,
		Sampling:          validRequest().Sampling,
		ParallelToolCalls: false,
	}
	result, err := client.Complete(context.Background(), request, nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.Content != "" || result.FinishReason != continuation.FinishToolCalls ||
		len(result.ToolCalls) != 1 || result.ToolCalls[0].ID != "call_new" ||
		result.ToolCalls[0].Name != "read_file" ||
		result.ToolCalls[0].Arguments != `{"path":"README.md"}` {
		t.Fatalf("result = %+v", result)
	}
	if len(received.Messages) != 5 ||
		received.Messages[0].Role != "system" ||
		received.Messages[0].Content == nil ||
		!strings.Contains(*received.Messages[0].Content, "Choose exactly one action.") ||
		received.Messages[1].Role != "user" ||
		received.Messages[2].Role != "assistant" || len(received.Messages[2].ToolCalls) != 1 ||
		received.Messages[2].ToolCalls[0].ID != "call_old" ||
		received.Messages[3].Role != "tool" || received.Messages[3].ToolCallID != "call_old" ||
		received.Messages[4].Role != "user" {
		t.Fatalf("messages = %+v", received.Messages)
	}
	if len(received.Tools) != 1 || received.Tools[0].Type != "function" ||
		received.Tools[0].Function.Name != "read_file" || !received.Tools[0].Function.Strict ||
		received.ToolChoice != "required" || received.ParallelToolCalls == nil ||
		*received.ParallelToolCalls {
		t.Fatalf("native tool request = %+v", received)
	}
}

func TestThinkingToolsPreserveReasoningAndAvoidRequiredChoice(t *testing.T) {
	t.Parallel()
	var received requestBody
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if err := json.NewDecoder(request.Body).Decode(&received); err != nil {
			t.Error(err)
		}
		writeJSON(writer, `{
			"choices":[{"index":0,"message":{"content":null,"reasoning_content":"inspect first","tool_calls":[{
				"id":"call_reasoning","type":"function",
				"function":{"name":"read_file","arguments":"{\"path\":\"README.md\"}"}
			}]} ,"finish_reason":"tool_calls"}]
		}`)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint:   server.URL,
		Model:      "reasoning-model",
		Thinking:   ThinkingEnabled,
		PromptMode: PromptNativeChat,
	})
	if err != nil {
		t.Fatal(err)
	}
	request := validToolChatRequest()
	request.Messages = append(request.Messages,
		toolchat.Message{
			Role:             toolchat.RoleAssistant,
			ReasoningContent: "previous reasoning",
			ToolCalls: []toolchat.ToolCall{{
				ID: "call_previous", Name: "read_file", Arguments: `{"path":"go.mod"}`,
			}},
		},
		toolchat.Message{
			Role: toolchat.RoleTool, ToolCallID: "call_previous", Content: `{"ok":true}`,
		},
	)
	result, err := client.Complete(context.Background(), request, nil)
	if err != nil {
		t.Fatal(err)
	}
	if received.ToolChoice != "auto" || received.Thinking == nil ||
		received.Thinking.Type != ThinkingEnabled {
		t.Fatalf("thinking request = %+v", received)
	}
	if len(received.Messages) != 4 ||
		received.Messages[2].ReasoningContent != "previous reasoning" {
		t.Fatalf("reasoning history = %+v", received.Messages)
	}
	if result.ReasoningContent != "inspect first" || len(result.ToolCalls) != 1 {
		t.Fatalf("result = %+v", result)
	}
}

func TestNativeToolsAcceptVLLMReasoningField(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		writeJSON(writer, `{
            "choices":[{
                "index":0,
                "message":{"content":null,"reasoning":"vllm trace","tool_calls":[{
                    "id":"call_1","type":"function",
                    "function":{"name":"read_file","arguments":"{\"path\":\"README.md\"}"}
                }]},
                "finish_reason":"tool_calls"
            }]
        }`)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "native-model", PromptMode: PromptNativeChat})
	if err != nil {
		t.Fatal(err)
	}
	result, err := client.Complete(context.Background(), validToolChatRequest(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.ReasoningContent != "vllm trace" {
		t.Fatalf("reasoning content = %q", result.ReasoningContent)
	}
}

func TestNewRejectsInvalidThinkingMode(t *testing.T) {
	t.Parallel()
	_, err := New(Config{
		Endpoint: "https://example.test/v1/chat/completions",
		Model:    "reasoning-model",
		Thinking: "sometimes",
	})
	if !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("error = %v, want ErrInvalidRequest", err)
	}
}

func TestNewRejectsInvalidPromptMode(t *testing.T) {
	t.Parallel()
	_, err := New(Config{
		Endpoint:   "https://example.test/v1/chat/completions",
		Model:      "native-model",
		PromptMode: "flattened-chat",
	})
	if !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("error = %v, want ErrInvalidRequest", err)
	}
}

func TestNativeChatRejectsMissingStructuredMessages(t *testing.T) {
	t.Parallel()
	client, err := New(Config{
		Endpoint:   "https://example.test/v1/chat/completions",
		Model:      "native-model",
		PromptMode: PromptNativeChat,
		HTTPClient: &http.Client{Transport: roundTripFunc(func(*http.Request) (*http.Response, error) {
			t.Fatal("native-chat made a request without structured messages")
			return nil, nil
		})},
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Complete(context.Background(), toolchat.Request{
		MaxOutputTokens: 32,
		Sampling:        validRequest().Sampling,
	}, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("error = %v, want ErrInvalidRequest", err)
	}
}

func TestNativeChatRejectsBrokenToolMessageChains(t *testing.T) {
	t.Parallel()
	client, err := New(Config{
		Endpoint:   "https://example.test/v1/chat/completions",
		Model:      "native-model",
		PromptMode: PromptNativeChat,
		HTTPClient: &http.Client{Transport: roundTripFunc(func(*http.Request) (*http.Response, error) {
			t.Fatal("invalid tool message chain reached the network")
			return nil, nil
		})},
	})
	if err != nil {
		t.Fatal(err)
	}
	request := validToolChatRequest()
	request.Messages = append(request.Messages, toolchat.Message{
		Role: toolchat.RoleTool, ToolCallID: "missing", Content: `{"ok":true}`,
	})
	if _, err := client.Complete(context.Background(), request, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("mismatched tool result error = %v", err)
	}
	request = validToolChatRequest()
	request.Messages = append(request.Messages, toolchat.Message{
		Role: toolchat.RoleAssistant,
		ToolCalls: []toolchat.ToolCall{{
			ID: "call_pending", Name: "read_file", Arguments: `{"path":"README.md"}`,
		}},
	})
	if _, err := client.Complete(context.Background(), request, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("missing tool result error = %v", err)
	}
}

func TestClientAppliesDecodedTextStops(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writeJSON(writer, `{
            "choices":[{"index":0,"message":{"content":"answer\nUser: ignored"},"finish_reason":"length"}]
        }`)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "other-model"})
	if err != nil {
		t.Fatal(err)
	}
	result, err := client.Continue(context.Background(), validRequest(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.Text != "answer" || result.FinishReason != continuation.FinishStop {
		t.Fatalf("result = %+v", result)
	}
}

func TestClientAllowsHeaderAuthorizationOverride(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, request *http.Request) {
		if value := request.Header.Get("Authorization"); value != "Custom credential" {
			t.Errorf("authorization = %q", value)
		}
		writeJSON(writer, `{"choices":[{"index":0,"message":{"content":"ok"},"finish_reason":"stop"}]}`)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint: server.URL,
		Model:    "other-model",
		APIKey:   "secret",
		Headers:  http.Header{"Authorization": []string{"Custom credential"}},
	})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Continue(context.Background(), validRequest(), nil); err != nil {
		t.Fatal(err)
	}
}

func TestClientReportsRemoteErrorsWithoutLeakingAPIKey(t *testing.T) {
	t.Parallel()
	const apiKey = "do-not-log-this"
	const gatewayKey = "gateway-secret"
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		http.Error(writer, `authentication failed for do-not-log-this and gateway-secret`, http.StatusUnauthorized)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint: server.URL,
		Model:    "other-model",
		APIKey:   apiKey,
		Headers:  http.Header{"X-Gateway-Key": []string{gatewayKey}},
	})
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.Continue(context.Background(), validRequest(), nil)
	if !errors.Is(err, ErrRemote) || !strings.Contains(err.Error(), "HTTP 401") {
		t.Fatalf("error = %v", err)
	}
	if strings.Contains(err.Error(), apiKey) || strings.Contains(err.Error(), gatewayKey) {
		t.Fatalf("credential leaked in error: %v", err)
	}
}

func TestClientRejectsOutOfRangeChatSamplingBeforeRequest(t *testing.T) {
	t.Parallel()
	client, err := New(Config{
		Endpoint: "https://example.test/v1/chat/completions",
		Model:    "other-model",
		HTTPClient: &http.Client{Transport: roundTripFunc(func(*http.Request) (*http.Response, error) {
			t.Fatal("invalid sampling reached the network")
			return nil, nil
		})},
	})
	if err != nil {
		t.Fatal(err)
	}
	request := validRequest()
	request.Sampling.Temperature = 2.1
	if _, err := client.Continue(context.Background(), request, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("temperature error = %v", err)
	}
	request = validRequest()
	request.Sampling.FrequencyPenalty = 2.1
	if _, err := client.Continue(context.Background(), request, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("penalty error = %v", err)
	}
}

func TestClientCancellationStopsRequest(t *testing.T) {
	t.Parallel()
	started := make(chan struct{})
	httpClient := &http.Client{Transport: roundTripFunc(func(
		request *http.Request,
	) (*http.Response, error) {
		close(started)
		<-request.Context().Done()
		return nil, request.Context().Err()
	})}
	client, err := New(Config{
		Endpoint:   "https://example.test/v1/chat/completions",
		Model:      "other-model",
		HTTPClient: httpClient,
	})
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithCancel(context.Background())
	done := make(chan error, 1)
	go func() {
		_, callErr := client.Continue(ctx, validRequest(), nil)
		done <- callErr
	}()
	<-started
	cancel()
	if err := <-done; !errors.Is(err, context.Canceled) {
		t.Fatalf("error = %v, want context.Canceled", err)
	}
}

func TestClientRejectsMalformedResponsesAndExcessiveStops(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writeJSON(writer, `{"choices":[]}`)
	}))
	defer server.Close()
	client, err := New(Config{Endpoint: server.URL, Model: "other-model"})
	if err != nil {
		t.Fatal(err)
	}
	if _, err := client.Continue(context.Background(), validRequest(), nil); !errors.Is(err, ErrRemote) {
		t.Fatalf("error = %v, want ErrRemote", err)
	}
	request := validRequest()
	request.Stops = []string{"1", "2", "3", "4", "5"}
	if _, err := client.Continue(context.Background(), request, nil); !errors.Is(err, continuation.ErrInvalidRequest) {
		t.Fatalf("error = %v, want ErrInvalidRequest", err)
	}
}

func TestNativeClientRejectsInconsistentToolResponses(t *testing.T) {
	t.Parallel()
	tests := []struct {
		name string
		body string
	}{
		{
			name: "missing calls",
			body: `{"choices":[{"index":0,"message":{"content":null},"finish_reason":"tool_calls"}]}`,
		},
		{
			name: "wrong finish reason",
			body: `{"choices":[{"index":0,"message":{"tool_calls":[{"id":"call_1","type":"function","function":{"name":"read_file","arguments":"{\"path\":\"README.md\"}"}}]},"finish_reason":"stop"}]}`,
		},
		{
			name: "invalid arguments",
			body: `{"choices":[{"index":0,"message":{"tool_calls":[{"id":"call_1","type":"function","function":{"name":"read_file","arguments":"not-json"}}]},"finish_reason":"tool_calls"}]}`,
		},
		{
			name: "duplicate call id",
			body: `{"choices":[{"index":0,"message":{"tool_calls":[{"id":"call_1","type":"function","function":{"name":"read_file","arguments":"{\"path\":\"a\"}"}},{"id":"call_1","type":"function","function":{"name":"read_file","arguments":"{\"path\":\"b\"}"}}]},"finish_reason":"tool_calls"}]}`,
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			t.Parallel()
			server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
				writeJSON(writer, test.body)
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
			_, err = client.Complete(context.Background(), validToolChatRequest(), nil)
			if !errors.Is(err, ErrRemote) {
				t.Fatalf("error = %v, want ErrRemote", err)
			}
		})
	}
}

func TestNativeClientSequentializesIgnoredParallelFlag(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(writer http.ResponseWriter, _ *http.Request) {
		writeJSON(writer, `{"choices":[{"index":0,"message":{"tool_calls":[
			{"id":"call_1","type":"function","function":{"name":"read_file","arguments":"{\"path\":\"a\"}"}},
			{"id":"call_2","type":"function","function":{"name":"read_file","arguments":"{\"path\":\"b\"}"}}
		]},"finish_reason":"tool_calls"}]}`)
	}))
	defer server.Close()
	client, err := New(Config{
		Endpoint: server.URL, Model: "native-model", PromptMode: PromptNativeChat,
	})
	if err != nil {
		t.Fatal(err)
	}
	result, err := client.Complete(context.Background(), validToolChatRequest(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if len(result.ToolCalls) != 1 || result.ToolCalls[0].ID != "call_1" ||
		result.ToolCalls[0].Arguments != `{"path":"a"}` {
		t.Fatalf("result = %+v", result)
	}
}

type roundTripFunc func(*http.Request) (*http.Response, error)

func writeJSON(writer http.ResponseWriter, body string) {
	writer.Header().Set("Content-Type", "application/json")
	_, _ = io.WriteString(writer, body)
}

func (f roundTripFunc) RoundTrip(request *http.Request) (*http.Response, error) {
	return f(request)
}

var _ http.RoundTripper = roundTripFunc(nil)
