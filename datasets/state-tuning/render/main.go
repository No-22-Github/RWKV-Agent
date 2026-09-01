// Command render is stage 2 of the state-tuning pipeline: it turns the semantic
// layer into training bytes using the product's own prompt renderer, so a
// trained state matches what the model sees at inference time.
//
// Stage 2 is free and re-runnable by design. A prompt-format change costs a
// re-render, not a re-collection, which matters because a trained state does
// not survive leaving the format it was trained on.
//
//	go run ./datasets/state-tuning/render --out datasets/state-tuning/train
//
// The byte contract, from internal/inference/prompt.go and
// internal/agent/protocol_messages.go:
//
//	prompt     ...\n\nAssistant: <think></think        <- final ">" withheld
//	completion >{action}
//
// The ">" is withheld because RWKV tokenises it together with the text that
// follows, so supplying it would start generation from a token boundary the
// model never saw. reconstructOutput prepends the block before parsing, which
// means the model's own first byte is ">". Training a completion that omits it
// would teach a different boundary than the one inference uses.
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/inference"
)

// semanticCase mirrors one record in datasets/state-tuning/semantic/batch-*.json.
type semanticCase struct {
	ID      string   `json:"id"`
	Subtype string   `json:"subtype"`
	Lang    string   `json:"lang"`
	Tools   []string `json:"tools"`
	User    string   `json:"user"`
	Action  string   `json:"action"`
	Call    *struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	} `json:"call"`
	Answer     string         `json:"answer"`
	Think      string         `json:"think"`
	PairedWith string         `json:"paired_with"`
	Steps      []semanticStep `json:"steps"`
}

// semanticStep is one turn of a multi_step case. Every step but the last is a
// call carrying the tool's real result shape; the last is the answer stage.
type semanticStep struct {
	Action string `json:"action"`
	Call   *struct {
		Name      string          `json:"name"`
		Arguments json.RawMessage `json:"arguments"`
	} `json:"call"`
	Result json.RawMessage `json:"result"`
	Answer string          `json:"answer"`
	Think  string          `json:"think"`
}

// toolSchema mirrors one entry in tool_schemas.json, exported from Go by
// export_schemas_test.go so descriptions cannot drift from the product.
type toolSchema struct {
	Name        string          `json:"name"`
	Description string          `json:"description"`
	Parameters  json.RawMessage `json:"parameters"`
	Arguments   string          `json:"arguments_hint"`
}

// trainingRecord carries the rendered bytes plus enough provenance to audit a
// sample later. prompt/completion are the authoritative pair; text is their
// concatenation for trainers that consume a single field.
type trainingRecord struct {
	ID         string   `json:"id"`
	Subtype    string   `json:"subtype"`
	Lang       string   `json:"lang"`
	Action     string   `json:"action"`
	Prompt     string   `json:"prompt"`
	Completion string   `json:"completion"`
	Text       string   `json:"text"`
	ToolOrder  []string `json:"tool_order"`
	PromptSHA  string   `json:"prompt_sha256"`
	// StepOf and StepIndex are set only for multi_step expansions, so a sample
	// can be traced back to the chain it came from.
	StepOf    int `json:"step_of,omitempty"`
	StepIndex int `json:"step_index,omitempty"`
}

func main() {
	var (
		semanticDir = flag.String("semantic", "datasets/state-tuning/semantic", "directory of batch-*.json")
		schemaPath  = flag.String("schemas", "datasets/state-tuning/tool_schemas.json", "exported tool schemas")
		outDir      = flag.String("out", "datasets/state-tuning/train", "output directory")
		seed        = flag.Int64("seed", 42, "tool-order shuffle seed")
		thinking    = flag.String("thinking", "fast", "thinking mode: fast, full, or off")
		limit       = flag.Int("limit", 0, "render at most N cases (0 = all)")
	)
	flag.Parse()

	mode, err := parseThinking(*thinking)
	if err != nil {
		fail(err)
	}
	schemas, err := loadSchemas(*schemaPath)
	if err != nil {
		fail(err)
	}
	cases, err := loadCases(*semanticDir)
	if err != nil {
		fail(err)
	}
	if *limit > 0 && *limit < len(cases) {
		cases = cases[:*limit]
	}
	if err := os.MkdirAll(*outDir, 0o755); err != nil {
		fail(err)
	}

	// One shuffler for the whole run, seeded, so a re-render with the same seed
	// reproduces byte-identical output.
	shuffler := rand.New(rand.NewSource(*seed))
	records := make([]trainingRecord, 0, len(cases))
	for _, entry := range cases {
		if len(entry.Steps) > 0 {
			expanded, err := expandMultiStep(entry, schemas, mode, shuffler)
			if err != nil {
				fail(fmt.Errorf("case %s: %w", entry.ID, err))
			}
			records = append(records, expanded...)
			continue
		}
		record, err := renderCase(entry, schemas, mode, shuffler)
		if err != nil {
			fail(fmt.Errorf("case %s: %w", entry.ID, err))
		}
		records = append(records, record)
	}

	if err := writeJSONL(filepath.Join(*outDir, "train.jsonl"), records); err != nil {
		fail(err)
	}
	report(records, mode)
}

func fail(err error) {
	fmt.Fprintln(os.Stderr, "render:", err)
	os.Exit(1)
}

func parseThinking(value string) (inference.ThinkingMode, error) {
	switch strings.ToLower(strings.TrimSpace(value)) {
	case "fast":
		return inference.ThinkingFast, nil
	case "full":
		return inference.ThinkingFull, nil
	case "off":
		return inference.ThinkingOff, nil
	default:
		return "", fmt.Errorf("unknown thinking mode %q", value)
	}
}

func loadSchemas(path string) (map[string]toolSchema, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read schemas: %w", err)
	}
	var schemas map[string]toolSchema
	if err := json.Unmarshal(raw, &schemas); err != nil {
		return nil, fmt.Errorf("decode schemas: %w", err)
	}
	if len(schemas) == 0 {
		return nil, fmt.Errorf("no schemas in %s", path)
	}
	return schemas, nil
}

func loadCases(dir string) ([]semanticCase, error) {
	paths, err := filepath.Glob(filepath.Join(dir, "batch-*.json"))
	if err != nil {
		return nil, err
	}
	sort.Strings(paths)
	var all []semanticCase
	seen := map[string]string{}
	for _, path := range paths {
		raw, err := os.ReadFile(path)
		if err != nil {
			return nil, err
		}
		var batch []semanticCase
		if err := json.Unmarshal(raw, &batch); err != nil {
			return nil, fmt.Errorf("%s: %w", filepath.Base(path), err)
		}
		for _, entry := range batch {
			if prior, ok := seen[entry.ID]; ok {
				return nil, fmt.Errorf("duplicate id %s in %s and %s",
					entry.ID, prior, filepath.Base(path))
			}
			seen[entry.ID] = filepath.Base(path)
		}
		all = append(all, batch...)
	}
	if len(all) == 0 {
		return nil, fmt.Errorf("no cases found in %s", dir)
	}
	sort.Slice(all, func(i, j int) bool { return all[i].ID < all[j].ID })
	return all, nil
}

func writeJSONL(path string, records []trainingRecord) error {
	file, err := os.Create(path)
	if err != nil {
		return err
	}
	defer file.Close()
	writer := bufio.NewWriter(file)
	for _, record := range records {
		encoded, err := json.Marshal(record)
		if err != nil {
			return err
		}
		if _, err := writer.Write(append(encoded, '\n')); err != nil {
			return err
		}
	}
	return writer.Flush()
}
