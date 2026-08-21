package bfcl

import (
	"context"
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

const MultiTurnRenderProtocolV1 = "bfcl-multi-turn-json-v1"

type MultiTurnExecutor interface {
	Execute(context.Context, string, []string) ([]string, error)
}

type MultiTurnRunnerOptions struct {
	Generator                continuation.Generator
	Executor                 MultiTurnExecutor
	SessionID                string
	Model                    string
	Tier                     Tier
	Transport                Transport
	MaxOutputTokens          int
	RouteMaxTokens           int
	MaxPromptChars           int
	MaxSteps                 int
	RouteRetries             int
	DuplicateReplayLimit     int
	DuplicateRescueThreshold int
	SameToolRescueLimit      int
	Temperature              float32
	CaseTimeout              time.Duration
}

type MultiTurnEvent struct {
	Kind           string   `json:"kind"`
	Turn           int      `json:"turn"`
	Step           int      `json:"step,omitempty"`
	Reason         string   `json:"reason,omitempty"`
	Route          string   `json:"route,omitempty"`
	Bundles        []string `json:"bundles,omitempty"`
	BeforeTools    []string `json:"before_tools,omitempty"`
	AfterTools     []string `json:"after_tools,omitempty"`
	Signature      string   `json:"signature,omitempty"`
	Retry          int      `json:"retry,omitempty"`
	ExecutionError string   `json:"execution_error,omitempty"`
	Generated      string   `json:"generated_content,omitempty"`
}

type MultiTurnStepTrace struct {
	Step             int                 `json:"step"`
	PromptSHA256     string              `json:"prompt_sha256"`
	PromptBytes      int                 `json:"prompt_bytes"`
	GeneratedContent string              `json:"generated_content"`
	ToolCalls        []toolchat.ToolCall `json:"tool_calls,omitempty"`
	ExecutionCalls   []string            `json:"execution_calls,omitempty"`
	ExecutionResults []string            `json:"execution_results,omitempty"`
	ParseError       string              `json:"parse_error,omitempty"`
	Repairs          []string            `json:"repairs,omitempty"`
	InputTokens      int                 `json:"input_tokens,omitempty"`
	OutputTokens     int                 `json:"output_tokens,omitempty"`
	Latency          float64             `json:"latency,omitempty"`
}

type MultiTurnTurnTrace struct {
	Turn          int                  `json:"turn"`
	Messages      []Message            `json:"messages"`
	Catalog       []string             `json:"catalog"`
	RouteCalls    int                  `json:"route_calls,omitempty"`
	RouteDecision string               `json:"route_decision,omitempty"`
	Steps         []MultiTurnStepTrace `json:"steps"`
	EndedBy       string               `json:"ended_by"`
}

type MultiTurnTrace struct {
	ID             string               `json:"id"`
	Category       string               `json:"category"`
	Tier           string               `json:"tier"`
	Result         [][][]string         `json:"result"`
	Turns          []MultiTurnTurnTrace `json:"turns"`
	Events         []MultiTurnEvent     `json:"events,omitempty"`
	PathDiagnostic []string             `json:"path_diagnostic,omitempty"`
	ModelCalls     int                  `json:"model_calls"`
	RouteCalls     int                  `json:"route_calls,omitempty"`
	InputTokens    int                  `json:"input_tokens,omitempty"`
	OutputTokens   int                  `json:"output_tokens,omitempty"`
	Latency        float64              `json:"latency,omitempty"`
	MaxPromptBytes int                  `json:"max_prompt_bytes"`
	Error          string               `json:"error,omitempty"`
}

type multiTurnTranscript struct {
	Role    string
	Content any
}

func RunMultiTurnCase(parent context.Context, entry MultiTurnCase, catalog MultiTurnCatalog, options MultiTurnRunnerOptions) MultiTurnTrace {
	trace := MultiTurnTrace{ID: entry.ID, Category: entry.Category, Tier: string(options.Tier), PathDiagnostic: append([]string(nil), entry.Path...)}
	if options.Generator == nil || options.Executor == nil || options.SessionID == "" {
		trace.Error = "BFCL multi-turn generator, executor, and session are required"
		return trace
	}
	if options.Tier != TierBaseline && options.Tier != TierEnhanced {
		trace.Error = fmt.Sprintf("unsupported BFCL multi-turn tier %q", options.Tier)
		return trace
	}
	if options.MaxSteps <= 0 {
		options.MaxSteps = 20
	}
	if options.RouteMaxTokens <= 0 {
		options.RouteMaxTokens = 48
	}
	if options.MaxOutputTokens <= 0 {
		options.MaxOutputTokens = 1024
	}
	if options.CaseTimeout <= 0 {
		options.CaseTimeout = 2 * time.Minute
	}
	ctx, cancel := context.WithTimeout(parent, options.CaseTimeout)
	defer cancel()
	var transcript []multiTurnTranscript
	trace.Result = make([][][]string, 0, len(entry.Turns))
	for turnIndex, originalMessages := range entry.Turns {
		messages := append([]Message(nil), originalMessages...)
		if len(messages) == 0 {
			messages = []Message{{Role: "user", Content: AdditionalFunctionPrompt}}
			trace.Events = append(trace.Events, MultiTurnEvent{Kind: "holdout_released", Turn: turnIndex})
		}
		for _, message := range messages {
			transcript = append(transcript, multiTurnTranscript{Role: multiTurnRole(message.Role), Content: message.Content})
		}
		available := catalog.ForTurn(turnIndex, nil)
		turnTrace := MultiTurnTurnTrace{Turn: turnIndex, Messages: messages}
		if options.Tier == TierEnhanced {
			selected, decision, calls, events, err := routeMultiTurn(ctx, transcript, entry, available, turnIndex, options)
			turnTrace.RouteCalls = calls
			trace.RouteCalls += calls
			trace.ModelCalls += calls
			trace.Events = append(trace.Events, events...)
			turnTrace.RouteDecision = decision
			if err != nil {
				trace.Error = err.Error()
				trace.Turns = append(trace.Turns, turnTrace)
				return trace
			}
			if decision == string(agent.RouteRespond) {
				turnTrace.EndedBy = "route_respond"
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: "[]"})
				trace.Result = append(trace.Result, nil)
				trace.Turns = append(trace.Turns, turnTrace)
				continue
			}
			available = selected
		}
		turnTrace.Catalog = MultiTurnFunctionNames(available)
		turnResult := make([][]string, 0)
		var lastSignature string
		sameCallStreak := 0
		lastTool := ""
		sameToolStreak := 0
		parseRetries := 0
		for step := 0; step < options.MaxSteps; step++ {
			stepTrace, calls, noCall, err := runMultiTurnStep(ctx, transcript, entry, available, turnIndex, step, options)
			turnTrace.Steps = append(turnTrace.Steps, stepTrace)
			trace.ModelCalls++
			trace.InputTokens += stepTrace.InputTokens
			trace.OutputTokens += stepTrace.OutputTokens
			trace.Latency += stepTrace.Latency
			trace.MaxPromptBytes = max(trace.MaxPromptBytes, stepTrace.PromptBytes)
			if err != nil {
				if options.Tier == TierEnhanced && stepTrace.ParseError != "" && parseRetries < options.RouteRetries {
					parseRetries++
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "correction_retry", Turn: turnIndex, Step: step, Reason: stepTrace.ParseError, Retry: parseRetries})
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent}, multiTurnTranscript{Role: "User", Content: "The previous output was invalid. Return only one JSON function-call object, a JSON array of calls, or [] when complete."})
					continue
				}
				if stepTrace.GeneratedContent != "" {
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent})
				}
				turnTrace.EndedBy = "parse_error"
				break
			}
			if noCall {
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent})
				turnTrace.EndedBy = "empty_response"
				break
			}
			parseRetries = 0
			executionCalls, encodeErr := MultiTurnExecutionCalls(calls)
			if encodeErr != nil {
				turnTrace.Steps[len(turnTrace.Steps)-1].ParseError = encodeErr.Error()
				turnTrace.EndedBy = "result_encoding_error"
				break
			}
			signature := multiTurnCallSignature(calls)
			if signature == lastSignature {
				sameCallStreak++
			} else {
				sameCallStreak = 1
			}
			lastSignature = signature
			toolName := calls[0].Name
			if toolName == lastTool {
				sameToolStreak++
			} else {
				sameToolStreak = 1
			}
			lastTool = toolName
			if options.Tier == TierEnhanced && options.DuplicateReplayLimit > 0 && sameCallStreak > options.DuplicateReplayLimit {
				trace.Events = append(trace.Events, MultiTurnEvent{Kind: "duplicate_rejected", Turn: turnIndex, Step: step, Signature: signature})
				if options.DuplicateRescueThreshold > 0 && sameCallStreak >= options.DuplicateRescueThreshold {
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "loop_rescue", Turn: turnIndex, Step: step, Reason: "consecutive_duplicate", Signature: signature})
					transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent})
					turnTrace.EndedBy = "loop_rescue"
					break
				}
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent}, multiTurnTranscript{Role: "Tool", Content: []string{"This exact call is disabled. Use the existing result or choose another tool."}})
				continue
			}
			if options.Tier == TierEnhanced && options.SameToolRescueLimit > 0 && sameToolStreak >= options.SameToolRescueLimit {
				trace.Events = append(trace.Events, MultiTurnEvent{Kind: "loop_rescue", Turn: turnIndex, Step: step, Reason: "same_tool_spiral", Signature: signature})
				transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent})
				turnTrace.EndedBy = "loop_rescue"
				break
			}
			results, executeErr := options.Executor.Execute(ctx, options.SessionID, executionCalls)
			if executeErr != nil {
				trace.Error = executeErr.Error()
				turnTrace.EndedBy = "sidecar_error"
				trace.Turns = append(trace.Turns, turnTrace)
				return trace
			}
			turnResult = append(turnResult, executionCalls)
			turnTrace.Steps[len(turnTrace.Steps)-1].ExecutionCalls = executionCalls
			turnTrace.Steps[len(turnTrace.Steps)-1].ExecutionResults = results
			transcript = append(transcript, multiTurnTranscript{Role: "Assistant", Content: stepTrace.GeneratedContent}, multiTurnTranscript{Role: "Tool", Content: results})
			for _, result := range results {
				if strings.HasPrefix(result, "Error during execution:") {
					trace.Events = append(trace.Events, MultiTurnEvent{Kind: "execution_error_feedback", Turn: turnIndex, Step: step, ExecutionError: result})
				}
			}
		}
		if turnTrace.EndedBy == "" {
			turnTrace.EndedBy = "step_limit"
		}
		trace.Result = append(trace.Result, turnResult)
		trace.Turns = append(trace.Turns, turnTrace)
	}
	return trace
}

func runMultiTurnStep(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, turn, step int, options MultiTurnRunnerOptions) (MultiTurnStepTrace, []toolchat.ToolCall, bool, error) {
	prompt, err := RenderMultiTurnPrompt(entry, functions, transcript)
	trace := MultiTurnStepTrace{Step: step, PromptBytes: len(prompt), PromptSHA256: promptSHA256(prompt)}
	if err != nil {
		return trace, nil, false, err
	}
	if options.MaxPromptChars > 0 && len(prompt) > options.MaxPromptChars {
		err := fmt.Errorf("multi-turn prompt size %d exceeds max_prompt_chars %d", len(prompt), options.MaxPromptChars)
		trace.ParseError = err.Error()
		return trace, nil, false, err
	}
	started := time.Now()
	completion, err := options.Generator.Continue(ctx, continuation.Request{Model: options.Model, Prompt: prompt, MaxOutputTokens: options.MaxOutputTokens, Stops: baselineStops(options.Transport), Sampling: continuation.Sampling{Temperature: options.Temperature, TopK: 1, TopP: 1, PenaltyDecay: 1}}, nil)
	trace.Latency = time.Since(started).Seconds()
	if err != nil {
		return trace, nil, false, err
	}
	trace.GeneratedContent = strings.TrimSpace(completion.Text)
	trace.InputTokens = completion.Usage.PromptTokens
	trace.OutputTokens = completion.Usage.CompletionTokens
	calls, parseErr := ParseMarkdownCalls(trace.GeneratedContent)
	if parseErr != nil && options.Tier == TierEnhanced {
		rawFunctions := make([]json.RawMessage, 0, len(functions))
		for _, function := range functions {
			rawFunctions = append(rawFunctions, function.Raw)
		}
		outcome, compatErr := ParseMarkdownCallsWithMode(trace.GeneratedContent, rawFunctions, ParserRWKVWireCompatV1)
		if compatErr == nil {
			calls = outcome.Calls
			trace.Repairs = outcome.Repairs
			parseErr = nil
		}
	}
	if parseErr != nil {
		trace.ParseError = parseErr.Error()
		return trace, nil, false, parseErr
	}
	trace.ToolCalls = calls
	return trace, calls, len(calls) == 0, nil
}

func RenderMultiTurnPrompt(entry MultiTurnCase, functions []MultiTurnFunction, transcript []multiTurnTranscript) (string, error) {
	initial, err := json.Marshal(entry.InitialConfig)
	if err != nil {
		return "", err
	}
	var prompt strings.Builder
	prompt.WriteString(`System: You are a BFCL multi-turn tool agent. Use only the listed tools.
Return one JSON function-call object in exactly this shape: {"name":"TOOL_NAME","arguments":{"ARGUMENT":"VALUE"}}.
For parallel calls return a JSON array of those objects. The key is always "arguments", never "parameters" or "response". Do not predict tool results. Return [] when the current turn is complete. Output JSON only and no prose. Tool errors are evidence: correct the call instead of repeating it.
Tools:
[`)
	for index, function := range functions {
		if index > 0 {
			prompt.WriteString(",\n")
		}
		prompt.Write(function.Raw)
	}
	prompt.WriteString("\n]\nInitial state:\n")
	prompt.Write(initial)
	prompt.WriteByte('\n')
	for _, message := range transcript {
		fmt.Fprintf(&prompt, "%s: ", message.Role)
		switch value := message.Content.(type) {
		case string:
			prompt.WriteString(value)
		default:
			encoded, err := json.Marshal(value)
			if err != nil {
				return "", err
			}
			prompt.Write(encoded)
		}
		prompt.WriteByte('\n')
	}
	prompt.WriteString("Assistant: ")
	return prompt.String(), nil
}

func MultiTurnExecutionCalls(calls []toolchat.ToolCall) ([]string, error) {
	result := make([]string, 0, len(calls))
	for _, call := range calls {
		encoded, err := ToResultString([]toolchat.ToolCall{call}, nil, LanguagePython)
		if err != nil {
			return nil, err
		}
		result = append(result, strings.TrimSuffix(strings.TrimPrefix(encoded, "["), "]"))
	}
	return result, nil
}

func multiTurnCallSignature(calls []toolchat.ToolCall) string {
	var parts []string
	for _, call := range calls {
		parts = append(parts, call.Name+"\x00"+call.Arguments)
	}
	return strings.Join(parts, "\x01")
}

func multiTurnRole(role string) string {
	switch strings.ToLower(strings.TrimSpace(role)) {
	case "system":
		return "System"
	case "assistant":
		return "Assistant"
	default:
		return "User"
	}
}

func routeMultiTurn(ctx context.Context, transcript []multiTurnTranscript, entry MultiTurnCase, functions []MultiTurnFunction, turn int, options MultiTurnRunnerOptions) ([]MultiTurnFunction, string, int, []MultiTurnEvent, error) {
	bundles := make([]agent.ToolBundle, 0, len(entry.InvolvedClasses))
	for _, className := range entry.InvolvedClasses {
		bundles = append(bundles, agent.ToolBundle{Name: className, Description: "BFCL functions provided by " + className + "."})
	}
	protocol := agent.G1IProgressiveToolRouteProtocol{}
	prompt := "System: " + protocol.Instructions(bundles) + "\n"
	for _, message := range transcript {
		content, ok := message.Content.(string)
		if !ok {
			encoded, _ := json.Marshal(message.Content)
			content = string(encoded)
		}
		prompt += message.Role + ": " + content + "\n"
	}
	prompt += "Assistant: "
	var events []MultiTurnEvent
	for attempt := 0; attempt <= options.RouteRetries; attempt++ {
		completion, err := options.Generator.Continue(ctx, continuation.Request{Model: options.Model, Prompt: prompt, MaxOutputTokens: options.RouteMaxTokens, Stops: protocol.Stops(), Sampling: continuation.Sampling{Temperature: options.Temperature, TopK: 1, TopP: 1, PenaltyDecay: 1}}, nil)
		if err != nil {
			return nil, "", attempt + 1, events, err
		}
		decision, parseErr := protocol.Parse(completion.Text, completion.FinishReason, bundles)
		if parseErr == nil {
			before := MultiTurnFunctionNames(functions)
			if decision.Route == agent.RouteRespond {
				events = append(events, MultiTurnEvent{Kind: "route_decision", Turn: turn, Route: string(decision.Route), BeforeTools: before, Generated: strings.TrimSpace(completion.Text)})
				return nil, string(decision.Route), attempt + 1, events, nil
			}
			selected := make(map[string]struct{}, len(decision.Bundles))
			for _, className := range decision.Bundles {
				selected[className] = struct{}{}
			}
			var narrowed []MultiTurnFunction
			for _, function := range functions {
				if _, ok := selected[function.Class]; ok {
					narrowed = append(narrowed, function)
				}
			}
			events = append(events, MultiTurnEvent{Kind: "route_decision", Turn: turn, Route: string(decision.Route), Bundles: decision.Bundles, BeforeTools: before, AfterTools: MultiTurnFunctionNames(narrowed), Generated: strings.TrimSpace(completion.Text)})
			return narrowed, string(decision.Route), attempt + 1, events, nil
		}
		events = append(events, MultiTurnEvent{Kind: "route_retry", Turn: turn, Reason: parseErr.Error(), Retry: attempt + 1, Generated: strings.TrimSpace(completion.Text)})
		prompt += completion.Text + "\nUser: " + protocol.Correction(parseErr, bundles) + "\nAssistant: "
	}
	return nil, "", options.RouteRetries + 1, events, fmt.Errorf("BFCL multi-turn route retries exhausted")
}
