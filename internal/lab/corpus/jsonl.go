package corpus

import (
	"fmt"
	"os"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// JSON Lines helpers. Outputs are opened exclusively by default: a pipeline
// never overwrites an earlier product (§4.1).
//
// Python writes these lines with json.dumps(row, ensure_ascii=False), which
// keeps <, > and & literal and uses ", " / ": " separators. Both details show
// up in script.jsonl, whose bytes are replayed into a training corpus, so the
// encoder is configured to match rather than left at Go's defaults (P2).

// ReadJSONL parses every non-blank line into an ordered object.
func ReadJSONL(path string) ([]*lab.OrderedMap, error) {
	text, err := lab.ReadText(path)
	if err != nil {
		return nil, err
	}
	var rows []*lab.OrderedMap
	for _, line := range lab.SplitLines(text) {
		if isBlank(line) {
			continue
		}
		obj, err := lab.DecodeOrderedJSON([]byte(line))
		if err != nil {
			return nil, fmt.Errorf("parse %s: %w", path, err)
		}
		om, ok := obj.(*lab.OrderedMap)
		if !ok {
			return nil, fmt.Errorf("%s: line is not a JSON object", path)
		}
		rows = append(rows, om)
	}
	return rows, nil
}

// WriteJSONL writes rows as one JSON object per line. mode is "x" (create,
// fail if it exists) or "a" (append).
func WriteJSONL(path string, rows []*lab.OrderedMap, mode string) error {
	flags := os.O_WRONLY | os.O_CREATE
	switch mode {
	case "a":
		flags |= os.O_APPEND
	default:
		flags |= os.O_EXCL
	}
	file, err := os.OpenFile(path, flags, 0o644)
	if err != nil {
		return err
	}
	defer file.Close()
	for _, row := range rows {
		data, err := lab.EncodeOrderedJSON(row, lab.EncodeOptions{SpacedSeparators: true})
		if err != nil {
			return err
		}
		if _, err := file.Write(append(data, '\n')); err != nil {
			return err
		}
	}
	return nil
}

func isBlank(line string) bool {
	for _, r := range line {
		switch r {
		case ' ', '\t', '\n', '\r', '\v', '\f':
		default:
			return false
		}
	}
	return true
}
