package agent

import (
	"encoding/json"
	"strings"

	"github.com/no22/RWKV-Agent/internal/inference"
)

// G1IFunctionProtocol implements the JSON function-call transcript used to
// train G1i checkpoints: System: Tools, Assistant: ```json, and User: Function
// output. It is intentionally separate from the general XML agent protocol.
type G1IFunctionProtocol struct {
	// AllowRepeatedCalls preserves the upstream Primitive Bench controller,
	// which executes identical calls repeatedly. Product-facing Go-native runs
	// leave this false so the Runner can reject loops and provide recovery.
	AllowRepeatedCalls bool
	// Product preserves ordinary Markdown answers on direct-response routes
	// while using the trained fenced-JSON transcript for tool decisions.
	Product bool
	// SemanticNoTool enables the text-only no_tool protocol action. It is a
	// model-visible abstention signal, not an executable or native API tool.
	SemanticNoTool bool
	// DeepToolAnchor extends the product decision prefill from the bare fence to
	// `{"name":"`. Measured on 7B: the shallow fence leaves the arguments shape
	// to the model, which stringifies it in about half of all calls; the deep
	// anchor drops that to zero. It also removes every syntactic abstention
	// exit, so it must only be evaluated together with SemanticNoTool.
	DeepToolAnchor bool
}

func (protocol G1IFunctionProtocol) ID() string {
	if protocol.Product {
		return G1IProductFunctionProtocolV1
	}
	return G1IFunctionProtocolV1
}

func (protocol G1IFunctionProtocol) Instructions(specs []ToolSpec, _ inference.ThinkingMode) string {
	catalog := make([]g1iCatalogEntry, 0, len(specs))
	for _, spec := range specs {
		catalog = append(catalog, makeG1ICatalogEntry(spec))
	}
	if protocol.Product && protocol.SemanticNoTool {
		catalog = append(catalog, g1iCatalogEntry{
			Name:        SemanticNoToolName,
			Description: "Indicate that none of the offered tools is needed. Put a brief, complete user-facing response in reason; it becomes the final reply.",
			Arguments: map[string]json.RawMessage{
				"reason": json.RawMessage(`{"type":"string"}`),
			},
		})
	}
	entries := make([]string, 0, len(catalog))
	for _, entry := range catalog {
		encoded, _ := json.Marshal(entry)
		entries = append(entries, string(encoded))
	}
	computeGuidance := ""
	if hasToolSpec(specs, "calculator") || hasToolSpec(specs, "data_query") {
		computeGuidance = "Read relevant task files with read_file first. calculator accepts only numeric literals, operators, and its listed math functions—never file names, SQL, or prose. " +
			"For multi-row tables use data_query; filter is a direct column-to-exact-value object and each call performs one operation. " +
			"Do not repeat a successful call or reread unchanged files. "
	}
	workflowGuidance := ""
	if hasToolSpec(specs, "web_fetch") {
		workflowGuidance += "For web research, search once, fetch the selected page once, then submit; never search again after a successful fetch. "
	}
	if hasToolSpec(specs, "spawn_agents") {
		workflowGuidance += "After spawn_agents returns, synthesize its ordered results and submit; never spawn another batch. "
	}
	exactOutputGuidance := PolicyVerbatimOutput
	base := "Tools:\n[\n" + strings.Join(entries, ",\n") + "\n]\n" +
		"Exact tool names only. Paths are relative (e.g. src/a.txt), never absolute. " +
		`Call shape: {"name":"read_file","arguments":{"path":"file.txt"}}. ` +
		computeGuidance + workflowGuidance +
		"Preserve exact paths and identifier names from Function output. " +
		exactOutputGuidance +
		"read_file lines: omit leading 'N: '. Money: two decimals.\n"
	if protocol.Product {
		completionGuidance := "After each Function output, either call one tool for a specific missing fact or answer the user directly in ordinary Markdown. When the answer contains code, wrap it in a fenced code block with a language tag. " +
			"Never pack the user-visible answer into a JSON function call; answer directly in Markdown."
		if protocol.SemanticNoTool {
			completionGuidance = `When none of the offered tools is needed, return {"name":"no_tool","arguments":{"reason":"brief complete user-facing response"}}; reason becomes the final reply without another generation. This no_tool form is the only exception to the rule against packing user-visible text into a function call. ` + completionGuidance
		}
		if hasToolSpec(specs, "submit") {
			completionGuidance = "After each Function output, either call one tool for a specific missing fact, or call submit with the exact user-visible answer. " +
				"When the user asks for code or a Markdown-formatted answer, respond directly with fenced code blocks instead of calling submit. " +
				"Never mix both in one response."
		}
		return base + "When new tool evidence is needed, return exactly one fenced JSON function call and nothing else. " +
			completionGuidance +
			"Do not repeat a successful tool call or repeat Function output. " + PolicyUntrustedData
	}
	return base + "After each Function output, return the next JSON function call. " +
		"Finish with submit when it is offered. Return only a JSON function call."
}

type g1iCatalogEntry struct {
	Name        string                     `json:"name"`
	Description string                     `json:"description"`
	Arguments   map[string]json.RawMessage `json:"arguments"`
}

func makeG1ICatalogEntry(spec ToolSpec) g1iCatalogEntry {
	description := strings.TrimSpace(spec.Description)
	if index := strings.IndexAny(description, ".!?"); index >= 0 {
		description = strings.TrimSpace(description[:index+1])
	}
	if len([]rune(description)) > 140 {
		description = string([]rune(description)[:137]) + "..."
	}
	var schema struct {
		Properties map[string]json.RawMessage `json:"properties"`
	}
	_ = json.Unmarshal(spec.Parameters, &schema)
	arguments := make(map[string]json.RawMessage, len(schema.Properties))
	for name, raw := range schema.Properties {
		var property map[string]json.RawMessage
		if json.Unmarshal(raw, &property) != nil {
			continue
		}
		compact := make(map[string]json.RawMessage, 3)
		for _, key := range []string{"type", "enum", "items"} {
			if value, ok := property[key]; ok {
				compact[key] = value
			}
		}
		if len(compact) == 0 {
			compact["type"] = json.RawMessage(`"string"`)
		}
		encoded, _ := json.Marshal(compact)
		arguments[name] = encoded
	}
	return g1iCatalogEntry{Name: spec.Name, Description: description, Arguments: arguments}
}
