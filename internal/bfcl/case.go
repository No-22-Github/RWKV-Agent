package bfcl

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"strings"
)

type Case struct {
	ID        string
	Category  string
	Messages  []Message
	Functions []json.RawMessage
}

type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type caseRecord struct {
	ID       string              `json:"id"`
	Question [][]Message         `json:"question"`
	Function []json.RawMessage   `json:"function"`
	Extra    map[string]struct{} `json:"-"`
}

func LoadSplit(dataDir, category string) ([]Case, error) {
	category = strings.TrimSpace(category)
	if category == "" || strings.ContainsAny(category, `/\\`) {
		return nil, fmt.Errorf("invalid BFCL category %q", category)
	}
	return readJSONLSplit(dataDir, category, decodeCase)
}

// readJSONLSplit reads one BFCL_v4_<category>.json JSONL file, decoding each
// non-blank line with decode. The shared loop is why the single-turn and
// multi-turn loaders report identical open/read/empty errors.
func readJSONLSplit[T any](
	dataDir string,
	category string,
	decode func(line []byte, category string) (T, error),
) ([]T, error) {
	path := filepath.Join(dataDir, "BFCL_v4_"+category+".json")
	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("open BFCL split %q: %w", category, err)
	}
	defer file.Close()

	reader := bufio.NewReader(file)
	var cases []T
	for lineNumber := 1; ; lineNumber++ {
		line, readErr := reader.ReadBytes('\n')
		if len(bytes.TrimSpace(line)) > 0 {
			entry, decodeErr := decode(line, category)
			if decodeErr != nil {
				return nil, fmt.Errorf("decode %s line %d: %w", path, lineNumber, decodeErr)
			}
			cases = append(cases, entry)
		}
		if readErr != nil {
			if readErr == io.EOF {
				break
			}
			return nil, fmt.Errorf("read %s: %w", path, readErr)
		}
	}
	if len(cases) == 0 {
		return nil, fmt.Errorf("BFCL split %q is empty", category)
	}
	return cases, nil
}

func decodeCase(line []byte, category string) (Case, error) {
	decoder := json.NewDecoder(bytes.NewReader(line))
	decoder.UseNumber()
	var record caseRecord
	if err := decoder.Decode(&record); err != nil {
		return Case{}, err
	}
	if strings.TrimSpace(record.ID) == "" {
		return Case{}, fmt.Errorf("id is required")
	}
	if len(record.Question) != 1 {
		return Case{}, fmt.Errorf("case %q has %d question turns; expected 1", record.ID, len(record.Question))
	}
	if len(record.Question[0]) == 0 {
		return Case{}, fmt.Errorf("case %q has no messages", record.ID)
	}
	for index, message := range record.Question[0] {
		if message.Role != "system" && message.Role != "user" && message.Role != "assistant" {
			return Case{}, fmt.Errorf("case %q message %d has unsupported role %q", record.ID, index, message.Role)
		}
	}
	if len(record.Function) == 0 && category != "irrelevance" && category != "live_irrelevance" {
		return Case{}, fmt.Errorf("case %q has no functions", record.ID)
	}
	return Case{
		ID:        record.ID,
		Category:  category,
		Messages:  append([]Message(nil), record.Question[0]...),
		Functions: append([]json.RawMessage(nil), record.Function...),
	}, nil
}
