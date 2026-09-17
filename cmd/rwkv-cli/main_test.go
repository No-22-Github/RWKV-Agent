package main

import (
	"strings"
	"testing"
	"time"

	agentapi "github.com/no22/RWKV-Agent/api"
	"github.com/no22/RWKV-Agent/internal/agent"
	agenteval "github.com/no22/RWKV-Agent/internal/agent/eval"
	"github.com/no22/RWKV-Agent/internal/agent/wire"
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
		"--completion", "rwkv-lightning-python",
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
		"--completion", "rwkv-lightning-python",
	}); err == nil {
		t.Fatal("remote agent accepted a missing API URL")
	}
}

func TestProductAgentRejectsIgnoredThinkingMode(t *testing.T) {
	t.Parallel()

	if _, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "inspect the repository",
		"--completion", "rwkv-lightning-python",
		"--api-url", "https://example.test/big_batch/completions",
		"--agent-protocol", "markdown",
		"--thinking", "full",
	}); err == nil {
		t.Fatal("product markdown Agent accepted an ignored thinking mode")
	}
	options, err := parseRunOptions("agent", []string{
		"--model", "rwkv7-13b",
		"--prompt", "inspect the repository",
		"--completion", "rwkv-lightning-python",
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
		"--completion", "rwkv-lightning-python",
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
		"--completion", "rwkv-lightning-python",
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
		{value: "0,6884,24281", wantMode: rwkvlightning.StopTokenEOS, wantIDs: []int{0, 6884, 24281}},
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
	for _, invalid := range []string{"cuda", "CUDA", "abc", "-1", "0,", "1,two"} {
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
	if bfclRunner.Protocol.ID() != agent.G1ProductFunctionProtocolV1 ||
		bfclRunner.Renderer.ID() != agent.G1ProductFunctionRendererV1 ||
		bfclRunner.ToolRouter == nil ||
		bfclRunner.ToolRouter.ID() != (agent.G1ProgressiveToolRouteProtocol{}).ID() {
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
		"--completion", "rwkv-lightning-python",
		"--api-url", "https://example.test/v1/chat/completions",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.completion != "rwkv-lightning-python" ||
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

func TestWireProfileFlagWiring(t *testing.T) {
	t.Parallel()
	// A profile is accepted for the product-facing suites and reaches the
	// parsed options; the suite keeps its own loop defaults.
	options, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuiteBFCLProduct,
		"--profile", "md-v1+anchor+gate-state",
	})
	if err != nil {
		t.Fatal(err)
	}
	if options.profile != "md-v1+anchor+gate-state" || !options.profileExplicit {
		t.Fatalf("profile = %q explicit = %v", options.profile, options.profileExplicit)
	}
	runner, err := agentEvalRunnerOptions(options, agenteval.SuiteBFCLProduct)
	if err != nil {
		t.Fatal(err)
	}
	if runner.Wire == nil {
		t.Fatal("applied profile did not reach Options.Wire")
	}
	if !strings.Contains(runner.Wire.Canonical(), "abstain=no-tool+gate-state") {
		t.Fatalf("wire canonical = %q", runner.Wire.Canonical())
	}
	if runner.MaxSteps != options.maxSteps || runner.SameToolRescueLimit != options.sameToolRescueLimit {
		t.Fatalf("suite loop defaults were not preserved: %+v", runner)
	}

	// Mixing the profile with a per-axis switch is a configuration error, not
	// a silent last-writer-wins.
	for _, args := range [][]string{
		{"--profile", "md-v1", "--agent-protocol", "xml"},
		{"--profile", "md-v1", "--semantic-no-tool"},
		{"--profile", "md-v1", "--deep-tool-anchor"},
		{"--profile", "md-v1", "--thinking", "fast"},
		{"--profile", "md-v1", "--route-stage"},
	} {
		_, err := parseRunOptions("agent-eval", append([]string{
			"--model", "model",
			"--suite", agenteval.SuiteBFCLProduct,
		}, args...))
		if err == nil || !strings.Contains(err.Error(), "--profile") {
			t.Fatalf("parseRunOptions(%v) err = %v, want a --profile conflict", args, err)
		}
	}

	// Primitive suites still own their per-case protocol and renderer.
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuitePrimitiveOrig30,
		"--profile", "primitive-v1",
	}); err == nil {
		t.Fatal("primitive suite accepted --profile before P4")
	}

	// The agent command carries the profile into the API config.
	agentOptions, err := parseRunOptions("agent", []string{
		"--model", "model",
		"--prompt", "inspect",
		"--profile", "md-v1",
	})
	if err != nil {
		t.Fatal(err)
	}
	config, err := agentAPIConfig(agentOptions)
	if err != nil {
		t.Fatal(err)
	}
	if config.Profile != "md-v1" {
		t.Fatalf("api config profile = %q", config.Profile)
	}
}

// TestWorkbankSuiteDefaults locks the bank-suite measurement defaults: the
// rescue mechanisms and the native first-step tool_choice=required escalation
// mask the behaviour the bank measures, so they default off/auto for the
// workbank case directory while explicit flags and every other suite keep the
// product defaults.
func TestWorkbankSuiteDefaults(t *testing.T) {
	t.Parallel()
	parse := func(args ...string) runOptions {
		t.Helper()
		options, err := parseRunOptions("agent-eval", append([]string{"--model", "model"}, args...))
		if err != nil {
			t.Fatal(err)
		}
		return options
	}

	bank, err := agentEvalRunnerOptions(parse("--cases", "bank"), "workbank")
	if err != nil {
		t.Fatal(err)
	}
	if bank.SameToolRescueLimit != 0 || bank.DuplicateRescueThreshold != 0 {
		t.Fatalf("workbank rescues = %d/%d, want 0/0",
			bank.SameToolRescueLimit, bank.DuplicateRescueThreshold)
	}
	if bank.NativeFirstCall != "auto" {
		t.Fatalf("workbank native first call = %q, want auto", bank.NativeFirstCall)
	}

	explicit, err := agentEvalRunnerOptions(parse(
		"--cases", "bank",
		"--same-tool-rescue-limit", "8",
		"--duplicate-rescue-threshold", "5",
		"--native-first-call", "required",
	), "workbank")
	if err != nil {
		t.Fatal(err)
	}
	if explicit.SameToolRescueLimit != 8 || explicit.DuplicateRescueThreshold != 5 ||
		explicit.NativeFirstCall != "required" {
		t.Fatalf("explicit workbank options = %+v", explicit)
	}

	nonBank, err := agentEvalRunnerOptions(parse("--suite", agenteval.SuiteBoundary), agenteval.SuiteBoundary)
	if err != nil {
		t.Fatal(err)
	}
	if nonBank.SameToolRescueLimit != agent.ProductSameToolRescueLimit ||
		nonBank.DuplicateRescueThreshold != agent.ProductDuplicateRescueThreshold {
		t.Fatalf("non-bank rescues = %d/%d, want the product defaults",
			nonBank.SameToolRescueLimit, nonBank.DuplicateRescueThreshold)
	}
	if nonBank.NativeFirstCall != "required" {
		t.Fatalf("non-bank native first call = %q, want required", nonBank.NativeFirstCall)
	}

	// The profile path must not clobber the bank default, and the recorded
	// spec must carry the value that actually runs.
	profiled, err := agentEvalRunnerOptions(parse("--cases", "bank", "--profile", "xml-v1"), "workbank")
	if err != nil {
		t.Fatal(err)
	}
	if profiled.NativeFirstCall != "auto" || profiled.Wire == nil ||
		profiled.Wire.FirstCall != wire.FirstCallAuto {
		t.Fatalf("profiled workbank first call = %q wire = %+v", profiled.NativeFirstCall, profiled.Wire)
	}

	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model", "--suite", agenteval.SuiteBoundary, "--native-first-call", "force",
	}); err == nil {
		t.Fatal("invalid --native-first-call accepted")
	}
}

// TestEvalSameToolRescueLimitUnifiedWithProduct locks the 2026-09-08 decision:
// every agent-eval suite starts from the product constant 3, and the historical
// eval value 8 is an explicit experiment, not a default.
func TestEvalSameToolRescueLimitUnifiedWithProduct(t *testing.T) {
	t.Parallel()
	for _, suite := range []string{agenteval.SuiteBoundary, agenteval.SuiteSmoke, agenteval.SuitePrimitiveOrig30} {
		options, err := parseRunOptions("agent-eval", []string{"--model", "model", "--suite", suite})
		if err != nil {
			t.Fatal(err)
		}
		if options.sameToolRescueLimit != agent.ProductSameToolRescueLimit {
			t.Fatalf("suite %s same-tool rescue = %d, want %d",
				suite, options.sameToolRescueLimit, agent.ProductSameToolRescueLimit)
		}
	}
	experiment, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuiteBoundary,
		"--same-tool-rescue-limit", "8",
	})
	if err != nil {
		t.Fatal(err)
	}
	if experiment.sameToolRescueLimit != 8 || !experiment.sameToolRescueExplicit {
		t.Fatalf("explicit experiment value = %+v", experiment)
	}
}

func TestWireProfileQueryDoesNotRequireModel(t *testing.T) {
	t.Parallel()
	handled, err := runWireProfileQuery([]string{"--list-profiles"})
	if !handled || err != nil {
		t.Fatalf("list-profiles handled = %v err = %v", handled, err)
	}
	handled, err = runWireProfileQuery([]string{"--explain-profile", "md-v1+gate-state"})
	if !handled || err != nil {
		t.Fatalf("explain-profile handled = %v err = %v", handled, err)
	}
	if handled, err := runWireProfileQuery([]string{"--model", "m"}); handled || err != nil {
		t.Fatalf("unrelated args handled = %v err = %v", handled, err)
	}
	if handled, err := runWireProfileQuery([]string{"--explain-profile", "nope-v1"}); !handled || err == nil {
		t.Fatalf("unknown profile handled = %v err = %v", handled, err)
	}
}

// TestWireLonghandOverrides locks the free-composition entry point: --wire sets
// individual axes on top of the suite default or a preset, so a thinking mode
// and a tool format can be paired without a registered preset.
func TestWireLonghandOverrides(t *testing.T) {
	t.Parallel()
	parse := func(args ...string) (runOptions, error) {
		return parseRunOptions("agent-eval", append([]string{
			"--model", "model",
			"--suite", agenteval.SuiteBFCLProduct,
		}, args...))
	}

	// Longhand axes on the suite default.
	options, err := parse("--wire", "format=md-fence,prefill=fence,abstain=no-tool")
	if err != nil {
		t.Fatal(err)
	}
	runner, err := agentEvalRunnerOptions(options, agenteval.SuiteBFCLProduct)
	if err != nil {
		t.Fatal(err)
	}
	if runner.Wire == nil {
		t.Fatal("--wire did not reach Options.Wire")
	}
	canonical := runner.Wire.Canonical()
	if !strings.Contains(canonical, "prefill=fence") || !strings.Contains(canonical, "abstain=no-tool") {
		t.Fatalf("canonical = %q", canonical)
	}

	// Compose on top of a preset: xml-v1 + fast thinking drops the envelope
	// prefill because the half-open think block owns the opening.
	options, err = parse("--profile", "xml-v1", "--wire", "thinking=fast")
	if err != nil {
		t.Fatal(err)
	}
	runner, err = agentEvalRunnerOptions(options, agenteval.SuiteBFCLProduct)
	if err != nil {
		t.Fatal(err)
	}
	canonical = runner.Wire.Canonical()
	if !strings.Contains(canonical, "format=xml") || !strings.Contains(canonical, "thinking=fast") ||
		!strings.Contains(canonical, "prefill=none") {
		t.Fatalf("composed canonical = %q", canonical)
	}

	// The legacy switches and --wire are two sources for the same axis.
	if _, err := parse("--wire", "format=md-fence", "--deep-tool-anchor"); err == nil ||
		!strings.Contains(err.Error(), "--wire") {
		t.Fatalf("legacy switch with --wire err = %v", err)
	}
	if _, err := parse("--wire", "nope=xml"); err == nil ||
		!strings.Contains(err.Error(), "unknown --wire key") {
		t.Fatalf("unknown --wire key err = %v", err)
	}
	if _, err := parseRunOptions("agent-eval", []string{
		"--model", "model",
		"--suite", agenteval.SuitePrimitiveOrig30,
		"--wire", "format=xml",
	}); err == nil {
		t.Fatal("primitive suite accepted --wire")
	}

	// The agent command carries the override list into the API config.
	agentOptions, err := parseRunOptions("agent", []string{
		"--model", "model",
		"--prompt", "inspect",
		"--wire", "format=md-fence,prefill=fence",
	})
	if err != nil {
		t.Fatal(err)
	}
	config, err := agentAPIConfig(agentOptions)
	if err != nil {
		t.Fatal(err)
	}
	if config.Wire != "format=md-fence,prefill=fence" {
		t.Fatalf("api config wire = %q", config.Wire)
	}

	// --strict-spec accepts a registered point and rejects an ad-hoc one.
	strictOptions, err := parse("--strict-spec", "--profile", "md-v1")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := agentEvalRunnerOptions(strictOptions, agenteval.SuiteBFCLProduct); err != nil {
		t.Fatalf("registered preset rejected by --strict-spec: %v", err)
	}
	adHocOptions, err := parse("--strict-spec", "--wire", "terminal=echo")
	if err != nil {
		t.Fatal(err)
	}
	if _, err := agentEvalRunnerOptions(adHocOptions, agenteval.SuiteBFCLProduct); err == nil ||
		!strings.Contains(err.Error(), "--strict-spec") {
		t.Fatalf("ad-hoc spec accepted by --strict-spec: %v", err)
	}
}

func TestExplicitLightningCLIProviders(t *testing.T) {
	for _, tc := range []struct{ kind, stop string }{
		{"rwkv-lightning-python", "text"}, {"rwkv-lightning-cuda", "eos"},
	} {
		options, err := parseRunOptions("agent", []string{"--completion", tc.kind, "--api-url", "https://example.test", "--model", "test", "--prompt", "hello"})
		if err != nil {
			t.Fatal(err)
		}
		config, err := agentAPIConfig(options)
		if err != nil {
			t.Fatal(err)
		}
		if string(config.Provider) != tc.kind || config.RWKVStopTokens != tc.stop {
			t.Fatalf("lost backend settings: %s %s", config.Provider, config.RWKVStopTokens)
		}
	}
}

func TestAmbiguousLightningCLIProviderIsRejected(t *testing.T) {
	_, err := parseRunOptions("agent", []string{"--completion", "rwkv-lightning", "--api-url", "https://example.test", "--model", "test", "--prompt", "hello"})
	if err == nil {
		t.Fatal("ambiguous backend accepted")
	}
}

// TestAgentEvalRecordsEffectiveLoopInWireSpec locks Fix 6: after --profile
// resolution the recorded wire spec must carry the loop that actually runs
// (CLI flags and suite defaults), not the preset's zero loop, so
// wire_canonical/wire_hash distinguish runs with different loop config.
func TestAgentEvalRecordsEffectiveLoopInWireSpec(t *testing.T) {
	t.Parallel()
	parse := func(args ...string) runOptions {
		t.Helper()
		options, err := parseRunOptions("agent-eval", append([]string{
			"--model", "model",
			"--suite", agenteval.SuiteBFCLProduct,
		}, args...))
		if err != nil {
			t.Fatal(err)
		}
		return options
	}

	runner, err := agentEvalRunnerOptions(
		parse("--profile", "xml-v1", "--max-steps", "10"),
		agenteval.SuiteBFCLProduct,
	)
	if err != nil {
		t.Fatal(err)
	}
	if runner.Wire == nil {
		t.Fatal("applied profile did not reach Options.Wire")
	}
	canonical := runner.Wire.Canonical()
	if !strings.Contains(canonical, "loop=10,") {
		t.Fatalf("canonical records a zero loop: %q", canonical)
	}
	zeroLoop := *runner.Wire
	zeroLoop.Loop = wire.Loop{}
	if runner.Wire.Hash() == zeroLoop.Hash() {
		t.Fatalf("hash does not reflect the loop config: %q", canonical)
	}
	// Every recorded loop field mirrors the final runtime options.
	loop := runner.Wire.Loop
	if loop.MaxSteps != runner.MaxSteps ||
		loop.ProtocolRetries != runner.ProtocolRetries ||
		loop.RouteRetries != runner.RouteRetries ||
		loop.DecisionMaxOutputTokens != runner.DecisionMaxOutputTokens ||
		loop.AnswerMaxOutputTokens != runner.Generation.MaxOutputTokens ||
		loop.RouteMaxOutputTokens != runner.RouteMaxOutputTokens ||
		loop.DuplicateReplayLimit != runner.DuplicateReplayLimit ||
		loop.DuplicateRescueThreshold != runner.DuplicateRescueThreshold ||
		loop.SameToolRescueLimit != runner.SameToolRescueLimit ||
		loop.AnswerStageLead != runner.AnswerStageLead {
		t.Fatalf("recorded loop = %+v does not mirror runtime %+v", loop, runner)
	}

	// A different --max-steps must produce a different wire identity.
	other, err := agentEvalRunnerOptions(
		parse("--profile", "xml-v1", "--max-steps", "6"),
		agenteval.SuiteBFCLProduct,
	)
	if err != nil {
		t.Fatal(err)
	}
	if other.Wire.Hash() == runner.Wire.Hash() {
		t.Fatalf("max-steps 6 and 10 share a wire hash: %q", runner.Wire.Canonical())
	}
}
