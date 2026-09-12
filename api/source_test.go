package api

import (
	"github.com/no22/RWKV-Agent/internal/continuation/provider"
	"testing"
)

func TestNormalizeOpenAIEndpoints(t *testing.T) {
	t.Parallel()
	for _, testCase := range []struct {
		input  string
		chat   string
		models string
	}{
		{
			input:  "https://example.test",
			chat:   "https://example.test/v1/chat/completions",
			models: "https://example.test/v1/models",
		},
		{
			input:  "https://example.test/v1/models",
			chat:   "https://example.test/v1/chat/completions",
			models: "https://example.test/v1/models",
		},
		{
			input:  "https://example.test/v1/chat/completions",
			chat:   "https://example.test/v1/chat/completions",
			models: "https://example.test/v1/models",
		},
	} {
		if got := provider.CompletionEndpoint(provider.ChatCompletions, testCase.input); got != testCase.chat {
			t.Fatalf("chat endpoint for %q = %q", testCase.input, got)
		}
		if got := provider.Endpoint(testCase.input, "models"); got != testCase.models {
			t.Fatalf("models endpoint for %q = %q", testCase.input, got)
		}
	}
}

func TestNormalizeRWKVEndpoints(t *testing.T) {
	t.Parallel()
	for _, input := range []string{
		"https://example.test",
		"https://example.test/v1",
		"https://example.test/v1/models",
		"https://example.test/v1/batch/completions",
	} {
		if got := provider.CompletionEndpoint(provider.LightningCUDA, input); got != "https://example.test/v1/batch/completions" {
			t.Fatalf("RWKV endpoint for %q = %q", input, got)
		}
		if got := provider.Endpoint(provider.CompletionEndpoint(provider.LightningCUDA, input), "models"); got != "https://example.test/v1/models" {
			t.Fatalf("models endpoint for %q = %q", input, got)
		}
	}
}

func TestNormalizeUnversionedRWKVModelsEndpoint(t *testing.T) {
	t.Parallel()
	got := provider.Endpoint("https://example.test/batch/completions", "models")
	if got != "https://example.test/v1/models" {
		t.Fatalf("models endpoint = %q", got)
	}
}

func TestValidatedHeadersRejectsInjectionAndReturnsNamesOnly(t *testing.T) {
	t.Parallel()
	headers, names, err := validatedHeaders(map[string]string{
		"cf-access-client-id":     "secret-id",
		"CF-Access-Client-Secret": "secret-value",
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(headers) != 2 || len(names) != 2 || names[0] != "Cf-Access-Client-Id" {
		t.Fatalf("headers=%v names=%v", headers, names)
	}
	if _, _, err := validatedHeaders(map[string]string{"X-Test\r\nInjected": "value"}); err == nil {
		t.Fatal("newline header name was accepted")
	}
	if _, _, err := validatedHeaders(map[string]string{"X-Test": "value\nInjected"}); err == nil {
		t.Fatal("newline header value was accepted")
	}
}
