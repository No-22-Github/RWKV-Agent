package product

import (
	"encoding/json"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
	"github.com/no22/RWKV-Agent/internal/agent/wire"
	"github.com/no22/RWKV-Agent/internal/continuation"
	"github.com/no22/RWKV-Agent/internal/inference"
	"github.com/no22/RWKV-Agent/internal/tokenizer"
)

// StagedFileControl tells the model that file changes are staged for review.
// It rides in the task-specific block whenever the session writes through a
// staged workspace.
const StagedFileControl = "本会话的 bash 和所有文件工具共享同一暂存文件系统。新增、修改和删除都只暂存在内存，读回、列目录和搜索会看到暂存后的内容。只有用户在文件改动面板确认后才会写入真实磁盘。回答中应说明文件改动已暂存待确认，不要声称已保存到磁盘。"

// NoWorkspaceControl is the system hint for a session without an open
// workspace.
const NoWorkspaceControl = "工作区未打开：本地文件工具（list_files/read_file/search_text）需要先打开一个工作区才能使用。如果用户需要读取或搜索本地文件，请直接告诉用户先在应用中打开一个工作区（例如“打开工作区”按钮），不要尝试调用任何文件工具，也不要假装读取了文件。"

// AnswerStageLead enters the forced answer stage one step before the budget
// runs out, so a model that still emits a tool call there gets one strict
// re-ask instead of ending the turn on "agent reached the step limit" with all
// gathered evidence thrown away.
const AnswerStageLead = 1

// SessionTimeContext is the separate context message carrying the session's
// start time. The zero time yields no message.
func SessionTimeContext(startedAt time.Time) string {
	if startedAt.IsZero() {
		return ""
	}
	local := startedAt.Local()
	weekday := [...]string{"星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"}[local.Weekday()]
	return "<session_time>\n会话启动时间为 " + local.Format("2006年01月02日 ") + weekday + local.Format(" 15时04分（UTC-07:00）") + "。这是会话启动时的时间，后续轮次保持不变。\n</session_time>"
}

// TaskControl composes the task-specific block: the no-workspace hint, then the
// user's own contract (verbatim, trimmed), then the staged-files notice.
func TaskControl(workspaceOpen, staged bool, user string) string {
	var parts []string
	if !workspaceOpen {
		parts = append(parts, NoWorkspaceControl)
	}
	if user = strings.TrimSpace(user); user != "" {
		parts = append(parts, user)
	}
	if staged {
		parts = append(parts, StagedFileControl)
	}
	return strings.Join(parts, "\n\n")
}

// TokenCounter opens the World vocabulary at path and returns its token
// counter. It is best effort: without a loadable vocabulary it returns nil,
// which keeps the fetch-compression hook off (it must never arm on the
// estimator) and makes the web budget fall back to the estimator, never the
// reverse.
func TokenCounter(tokenizerPath string) func(string) int {
	if strings.TrimSpace(tokenizerPath) == "" {
		return nil
	}
	world, err := tokenizer.OpenWorldCached(tokenizerPath)
	if err != nil {
		return nil
	}
	return world.Count
}

// ProgressiveEnabled resolves the optional capability-router switch: unset is
// off so the decision stage owns tool selection directly.
func ProgressiveEnabled(value *bool) bool { return value != nil && *value }

// SwitchEnabled resolves a tri-state Markdown-profile switch. Unset is on for
// semantic no_tool and the deep anchor; XML normalization supplies false.
func SwitchEnabled(value *bool) bool { return value == nil || *value }

// HarnessConfig is everything HarnessOptions needs, in plain terms that do not
// depend on the api package. api.Config converts into it; the evaluation
// builds it directly.
type HarnessConfig struct {
	// Markdown selects the Markdown continuation profile instead of the XML
	// envelope (the App's default transcript).
	Markdown bool
	// Profile and Wire are the wire preset and longhand overrides applied on top
	// of the protocol defaults. Both are expected to be validated already.
	Profile string
	Wire    string
	// Thinking is the XML renderer's prefill mode (a wire profile overrides it).
	Thinking string

	Model             string
	StateID           string
	MaxSteps          int
	MaxTokens         int
	DecisionMaxTokens int
	RouteMaxTokens    int
	// TracePromptBytes nil keeps agent.DefaultTracePromptBytes.
	TracePromptBytes *int
	Sampling         continuation.Sampling

	ProgressiveTools  *bool
	SemanticNoTool    *bool
	DeepToolAnchor    *bool
	DecisionFakeThink bool
	CompressFetch     bool

	// WorkspaceOpen and Staged drive the system-side task control hints.
	WorkspaceOpen bool
	Staged        bool
	// UserTaskControl is the user's free-text contract, appended verbatim.
	UserTaskControl string

	// SessionStart, when non-zero, injects the <session_time> context message.
	SessionStart time.Time

	// TokenCount counts real tokens; nil resolves TokenizerPath instead.
	TokenCount    func(string) int
	TokenizerPath string

	// Tools is the directory the Runner will receive; its bundles select the
	// progressive router's catalog.
	Tools []agent.Tool
	// Observe receives Runner events (evaluation tracing); the App sets its
	// observer per run, so it leaves this nil.
	Observe func(agent.Event)
}

// HarnessOptions assembles the Runner Options for one session: the Markdown
// protocol uses the product profile with its post-tool reminders, the XML
// profile carries the thinking mode instead, and the loop-policy limits are
// the shared product constants. Profile and Wire then compose on top.
func HarnessOptions(config HarnessConfig) agent.Options {
	tokenCount := config.TokenCount
	if tokenCount == nil {
		tokenCount = TokenCounter(config.TokenizerPath)
	}
	toolBundles := agent.EnabledToolBundles(config.Tools, agent.DefaultToolBundles())
	taskControl := TaskControl(config.WorkspaceOpen, config.Staged, config.UserTaskControl)
	generation := continuation.Request{
		Model:           config.Model,
		MaxOutputTokens: config.MaxTokens,
		StateID:         config.StateID,
		Sampling:        config.Sampling,
	}
	tracePromptBytes := agent.DefaultTracePromptBytes
	if config.TracePromptBytes != nil {
		tracePromptBytes = *config.TracePromptBytes
	}
	decision := min(config.DecisionMaxTokens, config.MaxTokens)
	route := min(config.RouteMaxTokens, config.MaxTokens)
	var options agent.Options
	if config.Markdown {
		// The Markdown protocol answers directly (plain Markdown or fenced code)
		// once it has enough evidence; there is no submit gate, so the model
		// never has to pack the user-visible answer into a JSON tool argument
		// (which is where Markdown fences get lost).
		options = agent.ProductHarnessOptions(agent.ProductHarnessConfig{
			MaxSteps:                 config.MaxSteps,
			DecisionMaxOutputTokens:  decision,
			RouteMaxOutputTokens:     route,
			TracePromptBytes:         tracePromptBytes,
			DuplicateReplayLimit:     agent.ProductDuplicateReplayLimit,
			DuplicateRescueThreshold: agent.ProductDuplicateRescueThreshold,
			SameToolRescueLimit:      agent.ProductSameToolRescueLimit,
			Generation:               generation,
			ProgressiveTools:         ProgressiveEnabled(config.ProgressiveTools),
			ToolBundles:              toolBundles,
			SemanticNoTool:           SwitchEnabled(config.SemanticNoTool),
			DecisionFakeThink:        config.DecisionFakeThink,
			DeepToolAnchor:           SwitchEnabled(config.DeepToolAnchor),
			TaskControl:              taskControl,
			PostToolHook:             markdownPostToolHook,
			Observe:                  config.Observe,
			CompressFetch:            config.CompressFetch,
			TokenCount:               tokenCount,
			AnswerStageLead:          AnswerStageLead,
		})
	} else {
		options = agent.XMLHarnessOptions(agent.XMLHarnessConfig{
			MaxSteps:                 config.MaxSteps,
			DecisionMaxOutputTokens:  decision,
			RouteMaxOutputTokens:     route,
			TracePromptBytes:         tracePromptBytes,
			DuplicateReplayLimit:     agent.ProductDuplicateReplayLimit,
			DuplicateRescueThreshold: agent.ProductDuplicateRescueThreshold,
			SameToolRescueLimit:      agent.ProductSameToolRescueLimit,
			Generation:               generation,
			ProgressiveTools:         ProgressiveEnabled(config.ProgressiveTools),
			ToolBundles:              toolBundles,
			TaskControl:              taskControl,
			Observe:                  config.Observe,
			ThinkingMode:             inference.ThinkingMode(config.Thinking),
			CompressFetch:            config.CompressFetch,
			TokenCount:               tokenCount,
			AnswerStageLead:          AnswerStageLead,
		})
	}
	if strings.TrimSpace(config.Profile) != "" {
		// The profile was validated upstream, so a failure here would mean the
		// base profile and the wire profile disagree; in that case the base
		// options stay in force rather than silently half-applying.
		if spec, _, err := wire.Resolve(config.Profile); err == nil {
			if applied, applyErr := agent.OptionsWithWire(options, spec); applyErr == nil {
				options = applied
			}
		}
	}
	if strings.TrimSpace(config.Wire) != "" {
		// The longhand overrides compose on top of the profile/default: only the
		// named axes change.
		if overrides, err := wire.ParseOverrides(config.Wire); err == nil {
			if spec, specErr := agent.WireSpecOf(options); specErr == nil {
				if overridden, overrideErr := spec.WithOverrides(overrides); overrideErr == nil {
					if applied, applyErr := agent.OptionsWithWire(options, overridden); applyErr == nil {
						options = applied
					}
				}
			}
		}
	}
	if !config.SessionStart.IsZero() {
		options.SessionContext = SessionTimeContext(config.SessionStart)
	}
	return options
}

// markdownPostToolHook is the Markdown protocol's post-tool reminder for the
// tools whose result should end the search.
func markdownPostToolHook(name string, _ json.RawMessage, _ any, _ error) string {
	switch name {
	case "web_fetch":
		return "NEXT: Use the fetched page content above and answer the user directly now. Do not call web_search or web_fetch again."
	case "spawn_agents":
		return "NEXT: Synthesize the ordered child results above and answer the user directly now. Do not spawn another batch."
	default:
		return ""
	}
}
