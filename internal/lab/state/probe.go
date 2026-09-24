package state

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/lab"
	"github.com/no22/RWKV-Agent/internal/lab/runs"
)

// Greedy continuation probe against the training corpus that produced a state.
//
// Takes prefixes from the exported corpus, asks the raw continuation endpoint
// to finish each one with and without the uploaded state, and measures how much
// of the corpus's own reference continuation comes back. A state trained on
// that corpus and loaded as intended should recover the reference far better
// than the zero state; no advantage is evidence the load or the prompt format
// is off.
//
// Diagnostic only: no workbench case, scorer or run ledger is touched.

const assistantMarker = "\nAssistant: "

func splitAtLastAssistant(text string) (string, string, bool) {
	index := strings.LastIndex(text, assistantMarker)
	if index < 0 {
		return "", "", false
	}
	head := text[:index]
	tail := text[index+len(assistantMarker):]
	return head + assistantMarker[:len(assistantMarker)-1], tail, true
}

func splitAtFirstAssistant(text string) (string, string, bool) {
	index := strings.Index(text, assistantMarker)
	if index < 0 {
		return "", "", false
	}
	return text[:index+len(assistantMarker)-1], text[index+len(assistantMarker):], true
}

// firstCall extracts the first complete tool call's JSON object, if any.
func firstCall(text string) map[string]any {
	start := strings.Index(text, "<tool_call>")
	if start < 0 {
		return nil
	}
	end := strings.Index(text[start:], "</tool_call>")
	var payload string
	if end > 0 {
		payload = text[start+len("<tool_call>") : start+end]
	} else {
		payload = text[start+len("<tool_call>"):]
	}
	obj, err := lab.DecodeJSONBytes([]byte(payload))
	if err != nil {
		return nil
	}
	m, ok := obj.(map[string]any)
	if !ok {
		return nil
	}
	if _, ok := m["arguments"].(map[string]any); !ok {
		return nil
	}
	return m
}

func commonPrefix(a, b string) int {
	ar, br := []rune(a), []rune(b)
	limit := len(ar)
	if len(br) < limit {
		limit = len(br)
	}
	for i := 0; i < limit; i++ {
		if ar[i] != br[i] {
			return i
		}
	}
	return limit
}

// ProbeArgs are the `state probe` flags.
type ProbeArgs struct {
	Corpus      string
	Split       string
	Rows        int
	Stride      int
	StateID     string
	Credentials string
	Output      string
	MaxTokens   int
}

// RunProbe is the `state probe` command.
func RunProbe(args ProbeArgs) int {
	cred, err := runs.LoadJSONFile(args.Credentials, true)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	headers := map[string]string{
		"CF-Access-Client-Id":     stringOf(cred, "WIRE_CF_ID"),
		"CF-Access-Client-Secret": stringOf(cred, "WIRE_CF_SECRET"),
		"User-Agent":              "curl/8.7.1",
		"Content-Type":            "application/json",
	}

	type probeRow struct {
		row           int
		prompt        string
		reference     string
		referenceCall map[string]any
	}
	var rows []probeRow
	file, err := os.Open(args.Corpus)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	data, err := io.ReadAll(file)
	file.Close()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	for index, line := range lab.SplitLines(string(data)) {
		if index%args.Stride != 0 {
			continue
		}
		if strings.TrimSpace(line) == "" {
			continue
		}
		obj, err := lab.DecodeJSONBytes([]byte(line))
		if err != nil {
			continue
		}
		text := ""
		if m, ok := obj.(map[string]any); ok {
			text, _ = m["text"].(string)
		}
		var prompt, reference string
		var ok bool
		if args.Split == "first" {
			prompt, reference, ok = splitAtFirstAssistant(text)
		} else {
			prompt, reference, ok = splitAtLastAssistant(text)
		}
		if !ok {
			continue
		}
		if len([]rune(reference)) < 8 {
			continue
		}
		referenceCall := firstCall(reference)
		if args.Split == "first" && referenceCall == nil {
			continue
		}
		rows = append(rows, probeRow{index, prompt, reference, referenceCall})
		if len(rows) >= args.Rows {
			break
		}
	}

	corpusBytes, _ := os.ReadFile(args.Corpus)
	record := lab.NewOrderedMap()
	record.Set("corpus", args.Corpus)
	record.Set("corpus_sha256", digest(corpusBytes))
	record.Set("split", args.Split)
	record.Set("state_id", args.StateID)
	record.Set("rows", len(rows))
	record.Set("started_unix", float64(time.Now().UnixNano())/1e9)
	record.Set("arms", lab.NewOrderedMap())

	arms := record.Values["arms"].(*lab.OrderedMap)
	for _, arm := range []struct {
		name  string
		state string
	}{{"zero", ""}, {"state", args.StateID}} {
		var results []any
		for _, row := range rows {
			body := lab.NewOrderedMap()
			body.Set("model", WireModel)
			body.Set("contents", []any{row.prompt})
			body.Set("max_tokens", args.MaxTokens)
			body.Set("temperature", 1)
			body.Set("top_k", 1)
			body.Set("top_p", 1)
			body.Set("alpha_presence", 0)
			body.Set("alpha_frequency", 0)
			body.Set("alpha_decay", 1)
			body.Set("stop_tokens", []any{0})
			body.Set("stream", false)
			body.Set("chunk_size", 1)
			if arm.state != "" {
				body.Set("state_id", arm.state)
			}
			response, err := httpRequest(headers, "batch/completions", body)
			if err != nil {
				fmt.Fprintln(os.Stderr, err)
				return 1
			}
			output := firstChoiceContent(response)
			produced := firstCall(output)

			entry := lab.NewOrderedMap()
			entry.Set("row", row.row)
			entry.Set("reference", truncateRunes(row.reference, 200))
			entry.Set("output", truncateRunes(output, 200))
			entry.Set("common_prefix", commonPrefix(strings.TrimSpace(output), strings.TrimSpace(row.reference)))
			entry.Set("exact_start_16", prefixRunes(strings.TrimSpace(output), 16) == prefixRunes(strings.TrimSpace(row.reference), 16))
			if row.referenceCall != nil {
				wantedName, _ := row.referenceCall["name"].(string)
				entry.Set("reference_tool", wantedName)
				producedName := ""
				if produced != nil {
					producedName, _ = produced["name"].(string)
				}
				entry.Set("produced_tool", nilIfEmpty(producedName))
				entry.Set("tool_match", produced != nil && producedName == wantedName)
				entry.Set("call_match", produced != nil && canonicalJSON(produced) == canonicalJSON(row.referenceCall))
			}
			results = append(results, entry)
		}
		arms.Set(arm.name, results)
		fmt.Println("ARM", arm.name, "done")
	}

	summary := lab.NewOrderedMap()
	for _, arm := range []string{"zero", "state"} {
		items, _ := arms.Values[arm].([]any)
		var toolRows []*lab.OrderedMap
		commonTotal := 0
		exact16 := 0
		for _, item := range items {
			entry, _ := item.(*lab.OrderedMap)
			if _, has := entry.Values["tool_match"]; has {
				toolRows = append(toolRows, entry)
			}
			if v, ok := intOf(entry.Values["common_prefix"]); ok {
				commonTotal += v
			}
			if v, ok := entry.Values["exact_start_16"].(bool); ok && v {
				exact16++
			}
		}
		armSummary := lab.NewOrderedMap()
		meanPrefix := 0.0
		if len(items) > 0 {
			meanPrefix = float64(commonTotal) / float64(len(items))
		}
		armSummary.Set("mean_common_prefix", meanPrefix)
		armSummary.Set("exact_start_16", exact16)
		toolMatch, callMatch := 0, 0
		for _, entry := range toolRows {
			if v, ok := entry.Values["tool_match"].(bool); ok && v {
				toolMatch++
			}
			if v, ok := entry.Values["call_match"].(bool); ok && v {
				callMatch++
			}
		}
		armSummary.Set("tool_match", toolMatch)
		armSummary.Set("call_match", callMatch)
		armSummary.Set("tool_rows", len(toolRows))
		armSummary.Set("rows", len(items))
		summary.Set(arm, armSummary)
	}
	record.Set("summary", summary)

	if err := writeIndented(args.Output, record); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	data2, err := lab.EncodeOrderedJSON(summary, lab.EncodeOptions{Indent: 2})
	if err == nil {
		fmt.Println(string(data2))
	}
	return 0
}

func truncateRunes(s string, limit int) string {
	r := []rune(s)
	if len(r) <= limit {
		return s
	}
	return string(r[:limit])
}

func prefixRunes(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[:n])
}

func nilIfEmpty(s string) any {
	if s == "" {
		return nil
	}
	return s
}

func canonicalJSON(v any) string {
	data, err := lab.EncodeOrderedJSON(v, lab.EncodeOptions{SortKeys: true})
	if err != nil {
		return ""
	}
	return string(data)
}

var _ = http.MethodPost
var _ = filepath.Base
var _ = json.Marshal
