package agent

import (
	"encoding/json"
	"fmt"
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
	// SubagentRawFeedback feeds spawn_agents results back as raw JSON, the
	// pre-E2 round-1 behaviour. Exists only so the E2 re-judgment (false_hit
	// as the primary metric, round-2 step 5) can A/B the block rendering
	// against the exact previous format; production keeps block rendering.
	SubagentRawFeedback bool
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
		description := "Indicate that none of the offered tools is needed. Put a brief, complete user-facing response in reason; it becomes the final reply."
		if hasMutatingToolSpec(specs) {
			// E6 finding: with file-editing tools offered, the model used
			// no_tool to CLAIM edits were done without calling any tool.
			// The description forbids claiming work instead of doing it.
			description += " Never claim that a file was read, created, or modified; the tools do all file work."
		}
		catalog = append(catalog, g1iCatalogEntry{
			Name:        SemanticNoToolName,
			Description: description,
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

// hasMutatingToolSpec reports whether any offered tool mutates workspace
// state (used to tighten the semantic no_tool description, see E6).
func hasMutatingToolSpec(specs []ToolSpec) bool {
	for _, spec := range specs {
		if spec.MutatesWorkspace {
			return true
		}
	}
	return false
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
		// Array properties flatten to a readable "array of T" string. Measured on
		// 7B class-3 e2e probes: when the catalog showed the
		// nested array schema, the model copied the schema object as the
		// argument VALUE (tasks == {"items":...,"type":"array"}), so the call
		// carried no tasks at all. A flat string leaves nothing to copy.
		if typeRaw, ok := property["type"]; ok && string(typeRaw) == `"array"` {
			items := "string"
			if itemsRaw, ok := property["items"]; ok {
				var itemsSchema struct {
					Type string `json:"type"`
				}
				if json.Unmarshal(itemsRaw, &itemsSchema) == nil && itemsSchema.Type != "" {
					items = itemsSchema.Type
				}
			}
			arguments[name] = json.RawMessage(`"array of ` + items + `"`)
			continue
		}
		// Scalar and union-type properties flatten the same way. Measured in
		// the round-3 zh e2e three-arm: web_search max_results rendered as
		// {"type":["integer","null"]} got copied verbatim as the argument
		// value on Chinese task prompts ({"query":...,"max_results":{"type":
		// ["integer","null"]}}), rejecting every search call until the step
		// budget died. Enum values stay structured: they are literals the
		// model is meant to copy.
		if _, hasEnum := property["enum"]; !hasEnum {
			if readable := readableScalarHint(property); readable != "" {
				arguments[name] = json.RawMessage(`"` + readable + `"`)
				continue
			}
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

// readableScalarHint renders a non-enum scalar or union-type schema as the
// flat placeholder the catalog shows the model ("integer 1..10"); "" means no
// readable form applies and the caller falls back to the compact schema.
func readableScalarHint(property map[string]json.RawMessage) string {
	typeRaw, ok := property["type"]
	if !ok {
		return ""
	}
	var typeName any
	if err := json.Unmarshal(typeRaw, &typeName); err != nil {
		return ""
	}
	name := ""
	switch value := typeName.(type) {
	case string:
		name = value
	case []any:
		// Union: use the first non-null member; a nullable integer is an
		// integer for catalog purposes.
		for _, member := range value {
			if memberName, ok := member.(string); ok && memberName != "null" {
				name = memberName
				break
			}
		}
		if name == "" {
			return ""
		}
	default:
		return ""
	}
	hint := name
	// Nullable unions read as optional parameters; saying so keeps the model
	// from inventing values just to fill the slot. A shown range takes
	// precedence and drops the annotation (below): the shipped round-3 catalog
	// and zh e2e traces render max_results as "integer 1..10", which is the
	// form the final window validated - wording is a prompt change and needs a
	// re-run, so keep the range form as measured.
	if raw, ok := property["type"]; ok && strings.Contains(string(raw), `"null"`) {
		hint = "optional " + hint
	}
	var minimum, maximum *float64
	if raw, ok := property["minimum"]; ok {
		_ = json.Unmarshal(raw, &minimum)
	}
	if raw, ok := property["maximum"]; ok {
		_ = json.Unmarshal(raw, &maximum)
	}
	if minimum != nil && maximum != nil {
		hint = fmt.Sprintf("%s %d..%d", name, int(*minimum), int(*maximum))
	}
	return hint
}
