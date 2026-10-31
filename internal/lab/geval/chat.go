package geval

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

// chatClient is a bare OpenAI-compatible /chat/completions client: the
// judge, and chat-template models (Qwen) under test. rwkv-cli's own chat
// adapter needs a build tag and speaks the agent wire, neither of which this
// needs.
type chatClient struct {
	url    string
	model  string
	key    string
	http   *http.Client
	extra  map[string]any
	maxTry int
}

type chatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type chatReply struct {
	Content          string
	Reasoning        string
	FinishReason     string
	PromptTokens     int
	CompletionTokens int
}

func newChatClient(baseURL, model, key string, extra map[string]any) *chatClient {
	url := strings.TrimRight(baseURL, "/")
	if !strings.HasSuffix(url, "/chat/completions") {
		url += "/chat/completions"
	}
	return &chatClient{url: url, model: model, key: key, extra: extra, maxTry: 4,
		http: &http.Client{Timeout: 30 * time.Minute}}
}

func (c *chatClient) complete(ctx context.Context, messages []chatMessage, params map[string]any) (chatReply, error) {
	body := map[string]any{"model": c.model, "messages": messages}
	for k, v := range c.extra {
		body[k] = v
	}
	for k, v := range params {
		body[k] = v
	}
	payload, err := json.Marshal(body)
	if err != nil {
		return chatReply{}, err
	}
	var last error
	for attempt := 0; attempt < c.maxTry; attempt++ {
		if attempt > 0 {
			select {
			case <-ctx.Done():
				return chatReply{}, ctx.Err()
			case <-time.After(time.Duration(attempt*attempt) * 3 * time.Second):
			}
		}
		reply, retry, err := c.once(ctx, payload)
		if err == nil {
			return reply, nil
		}
		last = err
		if !retry {
			break
		}
	}
	return chatReply{}, last
}

func (c *chatClient) once(ctx context.Context, payload []byte) (chatReply, bool, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.url, bytes.NewReader(payload))
	if err != nil {
		return chatReply{}, false, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.key != "" {
		req.Header.Set("Authorization", "Bearer "+c.key)
	}
	resp, err := c.http.Do(req)
	if err != nil {
		return chatReply{}, ctx.Err() == nil, err
	}
	defer resp.Body.Close()
	data, err := io.ReadAll(resp.Body)
	if err != nil {
		return chatReply{}, true, err
	}
	if resp.StatusCode != http.StatusOK {
		retry := resp.StatusCode == http.StatusTooManyRequests || resp.StatusCode >= 500
		return chatReply{}, retry, fmt.Errorf("HTTP %d: %s", resp.StatusCode, truncate(string(data), 300))
	}
	var parsed struct {
		Choices []struct {
			Message struct {
				Content          string `json:"content"`
				ReasoningContent string `json:"reasoning_content"`
				Reasoning        string `json:"reasoning"`
			} `json:"message"`
			FinishReason string `json:"finish_reason"`
		} `json:"choices"`
		Usage struct {
			PromptTokens     int `json:"prompt_tokens"`
			CompletionTokens int `json:"completion_tokens"`
		} `json:"usage"`
	}
	if err := json.Unmarshal(data, &parsed); err != nil {
		return chatReply{}, true, fmt.Errorf("decode response: %w", err)
	}
	if len(parsed.Choices) == 0 {
		return chatReply{}, true, fmt.Errorf("response has no choices: %s", truncate(string(data), 300))
	}
	msg := parsed.Choices[0].Message
	reasoning := msg.ReasoningContent
	if reasoning == "" {
		reasoning = msg.Reasoning
	}
	return chatReply{
		Content: msg.Content, Reasoning: reasoning, FinishReason: parsed.Choices[0].FinishReason,
		PromptTokens: parsed.Usage.PromptTokens, CompletionTokens: parsed.Usage.CompletionTokens,
	}, false, nil
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}
