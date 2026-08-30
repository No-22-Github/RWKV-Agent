package agent

import (
	"github.com/no22/RWKV-Agent/internal/inference"
)

// PromptPreview is the transcript-facing prompt contract a Runner would build
// for these options and this tool catalog. It lets front-ends show the system
// prompt without a model connection; NewRunner remains the enforcement path,
// and both read their prompt text from the same assembly helpers.
type PromptPreview struct {
	// Control is the decision-stage system prompt, including the optional
	// task contract suffix.
	Control string
	// ResponseControl is the direct-response control used on the respond
	// route and after an accepted abstention.
	ResponseControl string
	// ToolNames lists the catalog in transcript order.
	ToolNames []string
	// ProtocolID and RendererID identify the transcript contract.
	ProtocolID string
	RendererID string
	// ThinkingMode is the effective mode after renderer defaults.
	ThinkingMode inference.ThinkingMode
	// Native reports which tool variant the generator would adopt: true for
	// Chat Completions function calling, false for text continuation.
	Native bool
}

// PreviewPrompts renders the prompts for a draft configuration. The options
// are validated and defaulted exactly like NewRunner defaults them; native
// selects the tool variant a native-capable generator would adopt.
func PreviewPrompts(options Options, tools []Tool, native bool) (PromptPreview, error) {
	if err := applyRunnerDefaults(&options); err != nil {
		return PromptPreview{}, err
	}
	_, specs, err := registerTools(tools, options)
	if err != nil {
		return PromptPreview{}, err
	}
	thinkingMode := rendererThinkingMode(options.Renderer)
	names := make([]string, 0, len(specs))
	for _, spec := range specs {
		names = append(names, spec.Name)
	}
	return PromptPreview{
		Control:         controlPromptFor(options.Protocol, specs, thinkingMode, native, options.TaskControl),
		ResponseControl: responseControlPrompt(specs, thinkingMode),
		ToolNames:       names,
		ProtocolID:      options.Protocol.ID(),
		RendererID:      options.Renderer.ID(),
		ThinkingMode:    thinkingMode,
		Native:          native,
	}, nil
}
