package main

import (
	"strings"
	"testing"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/agent"
	agenteval "github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/continuation/rwkvlightning"
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
	if options.thinkingMode != "off" {
		t.Fatalf("default thinking mode = %q", options.thinkingMode)
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
		profile.Reasoning || profile.ThinkingMode != "off" {
		t.Fatalf("explicit profile = %+v", profile)
	}
}

func TestThinkingModesAndLegacyAlias(t *testing.T) {
	t.Parallel()
	for _, mode := range []string{"off", "fast", "full"} {
		options, err := parseRunOptions("run", []string{"--model", "model", "--thinking", mode})
		if err != nil {
			t.Fatal(err)
		}
		if options.thinkingMode != mode || !options.thinkingExplicit {
			t.Fatalf("mode %q parsed as %+v", mode, options)
		}
	}
	legacy, err := parseRunOptions("run", []string{"--model", "model", "--reasoning"})
	if err != nil || legacy.thinkingMode != "fast" || !legacy.thinkingExplicit {
		t.Fatalf("legacy reasoning options = %+v, %v", legacy, err)
	}
	if _, err := parseRunOptions("run", []string{"--model", "model", "--thinking", "bogus"}); err == nil {
		t.Fatal("unknown thinking mode accepted")
	}
	if _, err := parseRunOptions("run", []string{"--model", "model", "--thinking", "full", "--reasoning=false"}); err == nil {
		t.Fatal("conflicting thinking controls accepted")
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
	// 0 defers to the per-protocol default: the fenced-JSON profile needs ~96,
	// the XML envelope reasons first and needs ~512.
	if options.maxTokens != 1024 || options.decisionMaxTokens != 0 {
		t.Fatalf(
			"agent token limits = answer:%d decision:%d",
			options.maxTokens,
			options.decisionMaxTokens,
		)
	}
	explicit, err := parseRunOptions("agent", []string{
		"--model", "model", "--prompt", "task", "--decision-max-tokens", "512",
	})
	if err != nil || explicit.decisionMaxTokens != 512 {
		t.Fatalf("explicit decision limit = %d, err = %v", explicit.decisionMaxTokens, err)
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "model", "--prompt", "task", "--decision-max-tokens", "-1",
	}); err == nil {
		t.Fatal("agent accepted a negative decision token limit")
	}
	if options.routeMaxTokens != 48 {
		t.Fatalf("agent route token limit = %d", options.routeMaxTokens)
	}
	// The route stage was an early scaffold for small models. It costs a model
	// call per turn and 13B-class models route correctly inside the decision
	// stage, so it is off unless asked for.
	if options.routeStage {
		t.Fatal("agent enabled the route stage by default")
	}
	if options.workspace != "." || options.maxSteps != 6 {
		t.Fatalf("agent bounds = %+v", options)
	}
	if options.progressiveTools || options.enableWeb || options.enableSubagents ||
		options.maxActiveBatch != 4 || options.remoteBatchWait != 10*time.Millisecond ||
		options.subagentMaxParallel != 4 || options.subagentMaxSteps != 4 ||
		options.subagentTimeout != 2*time.Minute {
		t.Fatalf("agent capability defaults = %+v", options)
	}
	if options.agentProtocol != string(agentapi.AgentProtocolXML) {
		t.Fatalf("agent protocol = %q", options.agentProtocol)
	}
	if options.semanticNoTool || options.deepToolAnchor {
		t.Fatalf("XML product switches defaulted on: %+v", options)
	}
	config, err := agentAPIConfig(options)
	if err != nil {
		t.Fatal(err)
	}
	if config.AgentProtocol != agentapi.AgentProtocolXML ||
		config.ProgressiveTools == nil || *config.ProgressiveTools {
		t.Fatalf("default Agent API config = %+v", config)
	}
	if options.fewShot {
		t.Fatal("agent enabled few-shot by default before A/B validation")
	}
	if options.completion != "local" ||
		options.apiPasswordEnv != "RWKV_API_PASSWORD" ||
		options.apiKeyEnv != "OPENAI_API_KEY" ||
		options.chatThinking != "auto" ||
		options.chatPromptMode != "native-chat" ||
		options.chatTokenLimit != "max-completion-tokens" {
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
	// 0 is now the "use the per-protocol default" sentinel, not an error.
	if zero, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--decision-max-tokens", "0"},
	); err != nil || zero.decisionMaxTokens != 0 {
		t.Fatalf("explicit zero decision limit = %d, err = %v", zero.decisionMaxTokens, err)
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--route-max-tokens", "0"},
	); err == nil {
		t.Fatal("agent accepted a non-positive route token limit")
	}
	if _, err := parseRunOptions(
		"agent",
		[]string{"--model", "model", "--prompt", "task", "--agent-protocol", "invalid"},
	); err == nil {
		t.Fatal("agent accepted an invalid protocol")
	}
}

func TestAgentCapabilityOptionsMapToAPIConfig(t *testing.T) {
	t.Setenv("TEST_BRAVE_KEY", "brave-secret")
	t.Setenv("TEST_TAVILY_KEY", "tavily-secret")
	options, err := parseRunOptions("agent", []string{
		"--model", "model",
		"--prompt", "research",
		"--agent-protocol", "markdown",
		"--progressive-tools=true",
		"--web",
		"--brave-api-key-env", "TEST_BRAVE_KEY",
		"--tavily-api-key-env", "TEST_TAVILY_KEY",
		"--subagents",
		"--max-active-batch", "6",
		"--remote-batch-wait", "15ms",
		"--subagent-max-parallel", "6",
		"--subagent-max-steps", "5",
		"--subagent-timeout", "3m",
		"--decision-max-tokens", "77",
		"--trace-prompt-bytes", "1234",
		"--semantic-no-tool",
		"--decision-fake-think",
	})
	if err != nil {
		t.Fatal(err)
	}
	config, err := agentAPIConfig(options)
	if err != nil {
		t.Fatal(err)
	}
	if config.ProgressiveTools == nil || !*config.ProgressiveTools || !config.EnableWeb ||
		config.BraveAPIKey != "brave-secret" || config.TavilyAPIKey != "tavily-secret" ||
		config.RouteMaxTokens != 48 || config.DecisionMaxTokens != 77 ||
		config.TracePromptBytes == nil || *config.TracePromptBytes != 1234 ||
		config.SemanticNoTool == nil || !*config.SemanticNoTool || !config.DecisionFakeThink ||
		!config.EnableSubagents || config.MaxActiveBatch != 6 || config.RemoteBatchWaitMS != 15 ||
		config.SubagentMaxParallel != 6 || config.SubagentMaxSteps != 5 ||
		config.SubagentTimeoutSeconds != 180 {
		t.Fatalf("Agent API config = %+v", config)
	}
	if config.AgentProtocol != agentapi.AgentProtocolMarkdown {
		t.Fatalf("Agent API protocol = %q", config.AgentProtocol)
	}
}

func TestAgentCapabilityOptionsRejectInvalidBounds(t *testing.T) {
	t.Parallel()
	for _, arguments := range [][]string{
		{"--max-active-batch", "9"},
		{"--remote-batch-wait", "1001ms"},
		{"--subagent-max-parallel", "1"},
		{"--subagent-max-steps", "1"},
		{"--subagent-timeout", "61m"},
	} {
		base := []string{"--model", "model", "--prompt", "task"}
		if _, err := parseRunOptions("agent", append(base, arguments...)); err == nil {
			t.Fatalf("accepted invalid capability arguments %v", arguments)
		}
	}
}

func TestAgentEvalXMLRouteStageIsConfigurable(t *testing.T) {
	t.Parallel()

	enabled := agentRunnerOptions(runOptions{routeStage: true}, agenteval.SuiteBoundary, nil)
	if enabled.Router == nil || enabled.RouteRenderer == nil {
		t.Fatal("route stage enabled but no router was attached")
	}
	disabled := agentRunnerOptions(runOptions{routeStage: false}, agenteval.SuiteBoundary, nil)
	if disabled.Router != nil || disabled.RouteRenderer != nil {
		t.Fatalf("route stage disabled but router = %+v", disabled.Router)
	}
	for _, testCase := range []struct {
		args []string
		want bool
	}{
		{args: []string{"--route-stage"}, want: true},
		{args: []string{"--route-stage=true"}, want: true},
		{args: []string{"--route-stage=false"}, want: false},
		{args: nil, want: false},
	} {
		parsed, err := parseRunOptions("agent-eval", append([]string{
			"--model", "m",
			"--suite", agenteval.SuiteBoundary,
		}, testCase.args...))
		if err != nil {
			t.Fatal(err)
		}
		if parsed.routeStage != testCase.want {
			t.Fatalf("route stage with %v = %v, want %v",
				testCase.args, parsed.routeStage, testCase.want)
		}
	}
}

func TestAgentAcceptsFewShotProfile(t *testing.T) {
	t.Parallel()
	options, err := parseRunOptions(
		"agent-eval",
		[]string{"--model", "model", "--suite", "smoke", "--few-shot"},
	)
	if err != nil {
		t.Fatal(err)
	}
	if !options.fewShot {
		t.Fatalf("few-shot option = %+v", options)
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

func TestProductAgentRejectsIgnoredThinkingMode(t *testing.T) {
	t.Parallel()

	if _, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "inspect the repository",
		"--completion", "rwkv-lightning",
		"--api-url", "https://example.test/big_batch/completions",
		"--agent-protocol", "markdown",
		"--thinking", "full",
	}); err == nil {
		t.Fatal("product markdown Agent accepted an ignored thinking mode")
	}
	options, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "inspect the repository",
		"--completion", "rwkv-lightning",
		"--api-url", "https://example.test/big_batch/completions",
		"--agent-protocol", "xml",
		"--thinking", "full",
	})
	if err != nil || options.thinkingMode != "full" {
		t.Fatalf("XML thinking options = %+v, error = %v", options, err)
	}
	// Both product prefill switches default off on XML: no JSON fence to
	// extend, and no_tool measured 0 selections on this transcript.
	if options.semanticNoTool || options.deepToolAnchor {
		t.Fatalf("XML run defaulted product switches on: %+v", options)
	}
	explicit, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "inspect the repository",
		"--completion", "rwkv-lightning",
		"--api-url", "https://example.test/big_batch/completions",
		"--agent-protocol", "xml",
		"--semantic-no-tool", "--deep-tool-anchor",
	})
	if err != nil {
		t.Fatalf("XML rejected the product prefill switches: %v", err)
	}
	// An explicit opt-in is honored so the comparison stays re-runnable.
	if !explicit.semanticNoTool || explicit.deepToolAnchor {
		t.Fatalf("XML resolved explicit product switches wrongly: %+v", explicit)
	}
	// decisionFakeThink is the one that still errors, because the XML renderer
	// prefills its own think block from --thinking.
	if _, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "task",
		"--completion", "rwkv-lightning",
		"--api-url", "https://example.test/big_batch/completions",
		"--agent-protocol", "xml",
		"--decision-fake-think",
	}); err == nil {
		t.Fatal("XML accepted --decision-fake-think")
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "model",
		"--prompt", "task",
		"--completion", "chat-completions",
		"--api-url", "https://example.test/v1/chat/completions",
		"--chat-prompt-mode", "native-chat",
		"--thinking", "full",
	}); err == nil {
		t.Fatal("native-chat accepted a non-off internal thinking mode")
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuiteBFCLProduct,
		"--thinking", "fast",
	}); err == nil {
		t.Fatal("bfcl-product accepted an ignored thinking mode")
	}
}

func TestParseAPIStopTokens(t *testing.T) {
	t.Parallel()

	for _, testCase := range []struct {
		value    string
		wantMode rwkvlightning.StopTokenMode
		wantIDs  []int
	}{
		{value: "", wantMode: rwkvlightning.StopTokenText},
		{value: "text", wantMode: rwkvlightning.StopTokenText},
		{value: "TEXT", wantMode: rwkvlightning.StopTokenText},
		{value: "cuda", wantMode: rwkvlightning.StopTokenEOS, wantIDs: []int{0, 6884, 24281}},
		{value: "CUDA", wantMode: rwkvlightning.StopTokenEOS, wantIDs: []int{0, 6884, 24281}},
		{value: "none", wantMode: rwkvlightning.StopTokenNone},
		{value: "eos", wantMode: rwkvlightning.StopTokenEOS, wantIDs: []int{0}},
		{value: "0,261", wantMode: rwkvlightning.StopTokenEOS, wantIDs: []int{0, 261}},
		{value: " 11 , 12 ", wantMode: rwkvlightning.StopTokenEOS, wantIDs: []int{11, 12}},
	} {
		mode, ids, err := parseAPIStopTokens(testCase.value)
		if err != nil {
			t.Fatalf("parse %q: %v", testCase.value, err)
		}
		if mode != testCase.wantMode {
			t.Fatalf("parse %q mode = %q, want %q", testCase.value, mode, testCase.wantMode)
		}
		if len(ids) != len(testCase.wantIDs) {
			t.Fatalf("parse %q ids = %v, want %v", testCase.value, ids, testCase.wantIDs)
		}
		for index := range testCase.wantIDs {
			if ids[index] != testCase.wantIDs[index] {
				t.Fatalf("parse %q ids = %v, want %v", testCase.value, ids, testCase.wantIDs)
			}
		}
	}
	for _, invalid := range []string{"abc", "-1", "0,", "1,two"} {
		if _, _, err := parseAPIStopTokens(invalid); err == nil {
			t.Fatalf("parse %q accepted an invalid stop token list", invalid)
		}
	}
}

func TestAgentAcceptsChatCompletionsContinuation(t *testing.T) {
	t.Parallel()

	options, err := parseRunOptions("agent", []string{
		"--model", "other-model",
		"--prompt", "inspect the repository",
		"--completion", "chat-completions",
		"--api-url", "https://example.test/v1/chat/completions",
		"--api-key-env", "OTHER_API_KEY",
		"--chat-thinking", "disabled",
		"--chat-prompt-mode", "native-chat",
		"--chat-token-limit-field", "max-tokens",
		"--api-header-env", "X-Gateway-Key=OTHER_GATEWAY_KEY",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.modelPath != "other-model" ||
		options.completion != "chat-completions" ||
		options.apiURL != "https://example.test/v1/chat/completions" ||
		options.apiKeyEnv != "OTHER_API_KEY" ||
		options.chatThinking != "disabled" ||
		options.chatPromptMode != "native-chat" ||
		options.chatTokenLimit != "max-tokens" ||
		options.tokenizer != "" ||
		len(options.apiHeaderEnvs) != 1 {
		t.Fatalf("Chat Completions options = %+v", options)
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "other-model",
		"--prompt", "task",
		"--completion", "chat-completions",
	}); err == nil {
		t.Fatal("Chat Completions agent accepted a missing API URL")
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "other-model",
		"--prompt", "task",
		"--completion", "chat-completions",
		"--api-url", "https://example.test/v1/chat/completions",
		"--chat-thinking", "sometimes",
	}); err == nil {
		t.Fatal("Chat Completions agent accepted an invalid thinking mode")
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "local-model",
		"--prompt", "task",
		"--chat-thinking", "disabled",
	}); err == nil {
		t.Fatal("local agent accepted a Chat Completions thinking mode")
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "other-model",
		"--prompt", "task",
		"--completion", "chat-completions",
		"--api-url", "https://example.test/v1/chat/completions",
		"--chat-prompt-mode", "flattened-chat",
	}); err == nil {
		t.Fatal("Chat Completions agent accepted an invalid prompt mode")
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "local-model",
		"--prompt", "task",
		"--chat-prompt-mode", "native-chat",
	}); err == nil {
		t.Fatal("local agent accepted a Chat Completions prompt mode")
	}
	if _, err := parseRunOptions("agent", []string{
		"--model", "other-model",
		"--prompt", "task",
		"--completion", "chat-completions",
		"--api-url", "https://example.test/v1/chat/completions",
		"--chat-prompt-mode", "native-chat",
		"--thinking", "fast",
	}); err == nil {
		t.Fatal("native Chat Completions agent accepted internal thinking prefill")
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
		options.decisionMaxTokens != 0 ||
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
		"--suite", "primitive-orig30",
	})
	if err != nil {
		t.Fatal(err)
	}
	if suiteOptions.evalSuite != agenteval.SuitePrimitiveOrig30 || !suiteOptions.evalSuiteExplicit {
		t.Fatalf("explicit suite options = %+v", suiteOptions)
	}
	bfclProductOptions, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuiteBFCLProduct,
	})
	if err != nil {
		t.Fatal(err)
	}
	if bfclProductOptions.evalSuite != agenteval.SuiteBFCLProduct || !bfclProductOptions.evalSuiteExplicit {
		t.Fatalf("BFCL product suite options = %+v", bfclProductOptions)
	}
	if !bfclProductOptions.progressiveTools || bfclProductOptions.routeMaxTokens != 48 ||
		bfclProductOptions.sameToolRescueLimit != agent.ProductSameToolRescueLimit {
		t.Fatalf("BFCL product profile defaults = %+v", bfclProductOptions)
	}
	bfclRunner := agentRunnerOptions(bfclProductOptions, agenteval.SuiteBFCLProduct, nil)
	if bfclRunner.Protocol.ID() != agent.G1IProductFunctionProtocolV1 ||
		bfclRunner.Renderer.ID() != agent.G1IProductFunctionRendererV1 ||
		bfclRunner.ToolRouter == nil ||
		bfclRunner.ToolRouter.ID() != (agent.G1IProgressiveToolRouteProtocol{}).ID() {
		t.Fatalf("BFCL product Runner options = %+v", bfclRunner)
	}
	experimentalOptions, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuiteBFCLProduct,
		"--semantic-no-tool",
		"--decision-fake-think",
		"--progressive-tools=false",
	})
	if err != nil {
		t.Fatal(err)
	}
	if !experimentalOptions.semanticNoTool || !experimentalOptions.decisionFakeThink || experimentalOptions.progressiveTools {
		t.Fatalf("BFCL product experiments = %+v", experimentalOptions)
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuiteBoundary,
		"--semantic-no-tool",
	}); err == nil {
		t.Fatal("non-product eval accepted a product experiment switch")
	}
	legacySuiteOptions, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", "primitive",
	})
	if err != nil {
		t.Fatal(err)
	}
	if legacySuiteOptions.evalSuite != agenteval.SuitePrimitiveOrig30 {
		t.Fatalf("legacy Primitive suite was not canonicalized: %+v", legacySuiteOptions)
	}
	nativeOptions, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", "primitive-orig30",
		"--primitive-profile", "go-native",
	})
	if err != nil {
		t.Fatal(err)
	}
	if nativeOptions.primitiveProfile != agenteval.PrimitiveProfileGoNative {
		t.Fatalf("Primitive profile options = %+v", nativeOptions)
	}
	feedbackOptions, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", "primitive-feedback30",
		"--primitive-profile", "go-native",
	})
	if err != nil {
		t.Fatal(err)
	}
	if feedbackOptions.evalSuite != agenteval.SuitePrimitiveFeedback30 ||
		feedbackOptions.primitiveProfile != agenteval.PrimitiveProfileGoNative {
		t.Fatalf("Primitive feedback options = %+v", feedbackOptions)
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--primitive-profile", "unknown",
	}); err == nil {
		t.Fatal("agent eval accepted an unknown Primitive profile")
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
