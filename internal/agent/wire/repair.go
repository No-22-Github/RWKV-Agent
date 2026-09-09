// Package wire: repair IDs.
//
// The tool-call parsers tolerate a long list of malformed shapes so a small
// model's near-miss still becomes a call. That tolerance used to be invisible:
// a step recorded only a boolean "repaired". Each recovery stage now reports a
// stable ID, so a run can be compared by which repairs fired and how often —
// a prompt or format change that silently moves work into the parser shows up
// as a repair-count shift instead of a flat score.
package wire

// Repair identifies one tolerant-recovery stage. The strings are a stable
// contract: they go into trace.jsonl and run.json verbatim, so renaming one
// breaks comparability with archived runs.
type Repair string

const (
	// RepairThinkStripped removed a leading think block before the action.
	RepairThinkStripped Repair = "think_stripped"
	// RepairArrayEnvelope recovered a call from the <tool_calls>[…] form some
	// OpenAI-compatible servers emit.
	RepairArrayEnvelope Repair = "array_envelope"
	// RepairEnvelopeRecovered accepted a call that was missing its required
	// envelope (a bare object, or the other protocol's envelope).
	RepairEnvelopeRecovered Repair = "envelope_recovered"
	// RepairJSONRepaired fixed malformed JSON (bad escapes, truncation,
	// trailing text) with the tolerant repairer.
	RepairJSONRepaired Repair = "json_repaired"
	// RepairFunctionWrapper flattened an OpenAI {"function":{…}} wrapper.
	RepairFunctionWrapper Repair = "function_wrapper"
	// RepairKeyAlias accepted an alternative key for the tool name or the
	// arguments object (command/cmd/tool, args/parameters).
	RepairKeyAlias Repair = "key_alias"
	// RepairArgumentsHoisted moved unknown top-level keys into arguments.
	RepairArgumentsHoisted Repair = "arguments_hoisted"
	// RepairStringifiedArguments parsed an arguments value that was a JSON
	// string instead of an object.
	RepairStringifiedArguments Repair = "stringified_arguments"
	// RepairNestedName recovered the tool name from inside the arguments
	// object.
	RepairNestedName Repair = "nested_name"
	// RepairNameInferred guessed the tool name from the argument keys when the
	// model omitted it entirely.
	RepairNameInferred Repair = "name_inferred"
	// RepairToolRenamed mapped a legacy tool alias (reader, file_reader) onto
	// the current name.
	RepairToolRenamed Repair = "tool_renamed"
	// RepairPathArgument recovered a bare {"path":…} payload as read_file.
	RepairPathArgument Repair = "path_argument"
	// RepairLegacyXMLCall accepted the self-closing XML function syntax of
	// older checkpoints.
	RepairLegacyXMLCall Repair = "legacy_xml_call"
	// RepairXMLPathAlias mapped the XML attribute file_path onto path.
	RepairXMLPathAlias Repair = "xml_path_alias"
)

// RepairIDs lists every repair in a stable order for help text and tests.
func RepairIDs() []string {
	return []string{
		string(RepairThinkStripped),
		string(RepairArrayEnvelope),
		string(RepairEnvelopeRecovered),
		string(RepairJSONRepaired),
		string(RepairFunctionWrapper),
		string(RepairKeyAlias),
		string(RepairArgumentsHoisted),
		string(RepairStringifiedArguments),
		string(RepairNestedName),
		string(RepairNameInferred),
		string(RepairToolRenamed),
		string(RepairPathArgument),
		string(RepairLegacyXMLCall),
		string(RepairXMLPathAlias),
	}
}

// ParseRepairs is the recovery vocabulary a transcript may use. It is declared
// data: the parsers' emitted IDs must be a subset, and a test enforces that.
// The XML parser delegates the <tool_calls> form to the fenced parser, so it
// inherits every fenced recovery in addition to its own.
func (s Spec) ParseRepairs() []Repair {
	fenced := []Repair{
		RepairThinkStripped,
		RepairArrayEnvelope,
		RepairEnvelopeRecovered,
		RepairJSONRepaired,
		RepairFunctionWrapper,
		RepairKeyAlias,
		RepairArgumentsHoisted,
		RepairStringifiedArguments,
		RepairNestedName,
		RepairNameInferred,
	}
	if s.Format != FormatXML {
		return fenced
	}
	return append(fenced,
		RepairToolRenamed,
		RepairPathArgument,
		RepairLegacyXMLCall,
		RepairXMLPathAlias,
	)
}

// AllowsRepair reports whether the transcript declares the recovery stage.
func (s Spec) AllowsRepair(repair Repair) bool {
	for _, allowed := range s.ParseRepairs() {
		if allowed == repair {
			return true
		}
	}
	return false
}
