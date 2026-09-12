//go:build chatcompletions

package provider

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/chatcompletions"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

func TestChatFactoryPreservesNativeToolCalling(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var body struct {
			Messages []json.RawMessage `json:"messages"`
			Contents json.RawMessage   `json:"contents"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			t.Error(err)
		}
		if r.URL.Path != "/v1/chat/completions" || len(body.Messages) != 1 || body.Contents != nil {
			t.Errorf("wrong chat request %s %+v", r.URL, body)
		}
		w.Header().Set("Content-Type", "application/json")
		fmt.Fprint(w, `{"id":"test","object":"chat.completion","model":"test","choices":[{"index":0,"message":{"role":"assistant","content":"hello"},"finish_reason":"stop"}]}`)
	}))
	defer server.Close()
	generator, err := NewRemote(Config{Kind: ChatCompletions, Endpoint: server.URL, Model: "test", ChatPromptMode: chatcompletions.PromptNativeChat})
	if err != nil {
		t.Fatal(err)
	}
	chat, ok := generator.(toolchat.Completer)
	if !ok || !chat.NativeToolCalling() {
		t.Fatal("native chat capability lost")
	}
	result, err := chat.Complete(context.Background(), toolchat.Request{Messages: []toolchat.Message{{Role: toolchat.RoleUser, Content: "hello"}}, MaxOutputTokens: 10, Sampling: continuation.Sampling{Temperature: 1, TopK: 10, TopP: 1, PenaltyDecay: 1}}, nil)
	if err != nil {
		t.Fatal(err)
	}
	if result.Content != "hello" {
		t.Fatalf("result=%+v", result)
	}
}
