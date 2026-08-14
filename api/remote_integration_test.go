package api

import (
	"context"
	"os"
	"strings"
	"testing"
	"time"
)

// TestRemoteAgentReadsREADME is opt-in because it calls a real model service.
// It intentionally receives credentials only through the process environment.
func TestRemoteAgentReadsREADME(t *testing.T) {
	endpoint := strings.TrimSpace(os.Getenv("RWKV_AGENT_REMOTE_URL"))
	model := strings.TrimSpace(os.Getenv("RWKV_AGENT_REMOTE_MODEL"))
	headerID := strings.TrimSpace(os.Getenv("RWKV_AGENT_REMOTE_HEADER_ID"))
	headerSecret := strings.TrimSpace(os.Getenv("RWKV_AGENT_REMOTE_HEADER_SECRET"))
	if endpoint == "" || model == "" || headerID == "" || headerSecret == "" {
		t.Skip("remote Agent integration environment is not configured")
	}
	service, err := NewService(Options{Workspace: ".."})
	if err != nil {
		t.Fatal(err)
	}
	defer service.Close()
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	stream := false
	_, err = service.Configure(ctx, Config{
		Provider: ProviderRWKVLightning,
		Endpoint: endpoint,
		Model:    model,
		Headers: map[string]string{
			"CF-Access-Client-Id":     headerID,
			"CF-Access-Client-Secret": headerSecret,
		},
		Stream:         &stream,
		RWKVStopTokens: "none",
		MaxSteps:       6,
		MaxTokens:      1024,
	}, nil)
	if err != nil {
		t.Fatal(err)
	}
	session, err := service.NewSession(ctx)
	if err != nil {
		t.Fatal(err)
	}
	defer session.Close()
	result, err := session.Run(ctx, "Read README.md and output only its first line.")
	if err != nil {
		t.Fatalf("run: %v; steps: %+v", err, result.Steps)
	}
	if !strings.Contains(result.Output, "# RWKV-Agent") {
		t.Fatalf("output = %q, want README title; steps: %+v", result.Output, result.Steps)
	}
	read := false
	for _, step := range result.Steps {
		if step.Tool == "read_file" && step.ToolExecuted && step.ToolError == "" {
			read = true
		}
	}
	if !read {
		t.Fatalf("README answer did not execute read_file: %+v", result.Steps)
	}
}
