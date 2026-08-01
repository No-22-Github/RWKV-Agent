package main

import (
	"strings"
	"testing"
	"time"

	"github.com/no22/RWKV-Agent/internal/terminal"
)

func TestOfficialG1ChatDefaults(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("run", []string{"--model", "model"})
	if err != nil {
		t.Fatal(err)
	}
	if options.reasoning {
		t.Fatal("reasoning must be opt-in for regular chat")
	}
	if options.reasoningExplicit {
		t.Fatal("omitted --reasoning must remain unspecified for Session inheritance")
	}
	if loadConversationOptions(options).Profile.TemplateID != "" {
		t.Fatal("Session load must inherit reasoning mode when the flag is omitted")
	}
	if options.temperature != 1 ||
		options.topP != 0.5 ||
		options.presencePenalty != 2 ||
		options.frequencyPenalty != 0.1 ||
		options.penaltyDecay != 0.99 {
		t.Fatalf("unexpected G1 chat defaults: %+v", options)
	}
}

func TestExplicitReasoningOverridesSessionInheritance(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions(
		"run",
		[]string{"--model", "model", "--reasoning=false"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if !options.reasoningExplicit {
		t.Fatal("--reasoning=false must count as an explicit mode selection")
	}
	if profile := loadConversationOptions(options).Profile; profile.TemplateID == "" ||
		profile.Reasoning {
		t.Fatalf("explicit profile = %+v", profile)
	}
}

func TestConcurrentUIOptions(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("concurrent", []string{"--model", "model"})
	if err != nil {
		t.Fatal(err)
	}
	if options.ui != string(terminal.UIAuto) {
		t.Fatalf("default UI = %q", options.ui)
	}
	if _, err := parseRunOptions("concurrent", []string{"--model", "model", "--ui", "invalid"}); err == nil {
		t.Fatal("invalid --ui accepted")
	}
}

func TestAgentDefaultsAreDeterministicAndBounded(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "inspect the repository"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if options.topK != 1 || options.topP != 1 ||
		options.presencePenalty != 0 || options.frequencyPenalty != 0 ||
		options.penaltyDecay != 1 {
		t.Fatalf("agent sampling defaults = %+v", options)
	}
	if options.maxTokens != 1024 || options.decisionMaxTokens != 256 {
		t.Fatalf(
			"agent token limits = answer:%d decision:%d",
			options.maxTokens,
			options.decisionMaxTokens,
		)
	}
	if options.routeMaxTokens != 16 {
		t.Fatalf("agent route token limit = %d", options.routeMaxTokens)
	}
	if options.workspace != "." || options.maxSteps != 6 {
		t.Fatalf("agent bounds = %+v", options)
	}
	if options.completion != "local" || options.apiPasswordEnv != "RWKV_API_PASSWORD" {
		t.Fatalf("agent continuation defaults = %+v", options)
	}
	interactive, err := parseRunOptions("agent", []string{"--model", "model"})
	if err != nil || interactive.ui != string(terminal.UIAuto) {
		t.Fatalf("interactive agent options = %+v, %v", interactive, err)
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--ui", "plain"},
	); err == nil {
		t.Fatal("plain agent accepted an empty prompt")
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--max-steps", "21"},
	); err == nil {
		t.Fatal("agent accepted an excessive step limit")
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--max-steps", "1"},
	); err == nil {
		t.Fatal("agent accepted a step limit without room for a final answer")
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--decision-max-tokens", "0"},
	); err == nil {
		t.Fatal("agent accepted a non-positive decision token limit")
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--route-max-tokens", "0"},
	); err == nil {
		t.Fatal("agent accepted a non-positive route token limit")
	}
}

func TestAgentAcceptsRWKVLightningContinuation(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "inspect the repository",
		"--completion", "rwkv-lightning",
		"--api-url", "https://example.test/v1/chat/completions",
		"--api-header-env", "CF-Access-Client-Id=RWKV_CF_ACCESS_CLIENT_ID",
		"--api-header-env", "CF-Access-Client-Secret=RWKV_CF_ACCESS_CLIENT_SECRET",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.modelPath != "rwkv7-13b" ||
		options.apiURL != "https://example.test/v1/chat/completions" ||
		options.tokenizer != "" ||
		len(options.apiHeaderEnvs) != 2 {
		t.Fatalf("remote agent options = %+v", options)
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "task",
		"--completion", "rwkv-lightning",
	}); err == nil {
		t.Fatal("remote agent accepted a missing API URL")
	}
}

func TestAgentEvalOptionsAreDeterministicAndIsolated(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--cases", "cases.json",
		"--case", "read_exact_file",
		"--case", "multi_turn_memory",
		"--output", "eval-output",
		"--case-timeout", "45s",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.topK != 1 ||
		options.topP != 1 ||
		options.maxTokens != 1024 ||
		options.decisionMaxTokens != 256 ||
		options.routeMaxTokens != 16 {
		t.Fatalf("agent eval defaults = %+v", options)
	}
	if options.evalCasesPath != "cases.json" ||
		options.evalSuite != "boundary" ||
		options.evalSuiteExplicit ||
		options.evalOutput != "eval-output" ||
		options.evalCaseTimeout != 45*time.Second ||
		len(options.evalCaseIDs) != 2 ||
		options.evalCaseIDs[0] != "read_exact_file" ||
		options.evalCaseIDs[1] != "multi_turn_memory" {
		t.Fatalf("agent eval options = %+v", options)
	}
	if strings.TrimSpace(options.prompt) != "" || options.workspace != "" {
		t.Fatalf("agent eval unexpectedly accepted interactive fields: %+v", options)
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--case-timeout", "0s",
	}); err == nil {
		t.Fatal("agent eval accepted a non-positive case timeout")
	}
	suiteOptions, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", "smoke",
	})
	if err != nil {
		t.Fatal(err)
	}
	if suiteOptions.evalSuite != "smoke" || !suiteOptions.evalSuiteExplicit {
		t.Fatalf("explicit suite options = %+v", suiteOptions)
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", "smoke",
		"--cases", "cases.json",
	}); err == nil {
		t.Fatal("agent eval accepted --suite with --cases")
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", "unknown",
	}); err == nil {
		t.Fatal("agent eval accepted an unknown suite")
	}
}

func TestAgentEvalAcceptsRemoteContinuation(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("agent-eval", []string{
		"--model", "rwkv7-13b",
		"--completion", "rwkv-lightning",
		"--api-url", "https://example.test/v1/chat/completions",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.completion != "rwkv-lightning" ||
		options.apiURL == "" ||
		options.tokenizer != "" ||
		options.evalCaseTimeout != 2*time.Minute {
		t.Fatalf("remote agent eval options = %+v", options)
	}
}

func TestLoadAPIHeadersFromEnvironment(t *testing.T) {
	t.Setenv("RWKV_TEST_CLIENT_ID", "client-id")
	t.Setenv("RWKV_TEST_CLIENT_SECRET", "client-secret")

	headers, err := loadAPIHeaders([]string{
		"CF-Access-Client-Id=RWKV_TEST_CLIENT_ID",
		"CF-Access-Client-Secret=RWKV_TEST_CLIENT_SECRET",
	})
	if err != nil {
		t.Fatal(err)
	}
	if headers.Get("CF-Access-Client-Id") != "client-id" ||
		headers.Get("CF-Access-Client-Secret") != "client-secret" {
		t.Fatalf("headers = %+v", headers)
	}
	if _, err := loadAPIHeaders([]string{"bad-mapping"}); err == nil {
		t.Fatal("invalid header mapping accepted")
	}
	if _, err := loadAPIHeaders([]string{"X-Test=RWKV_TEST_MISSING"}); err == nil {
		t.Fatal("missing environment variable accepted")
	}
}
