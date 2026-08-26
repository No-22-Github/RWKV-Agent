package bfcl

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"time"
)

func LoadTrace(path string) ([]TraceEntry, error) {
	file, err := os.Open(path)
	if err != nil {
		return nil, fmt.Errorf("open BFCL trace: %w", err)
	}
	defer file.Close()
	decoder := json.NewDecoder(file)
	var entries []TraceEntry
	for {
		var entry TraceEntry
		if err := decoder.Decode(&entry); err != nil {
			if err == io.EOF {
				break
			}
			return nil, fmt.Errorf("decode BFCL trace entry %d: %w", len(entries)+1, err)
		}
		entries = append(entries, entry)
	}
	if len(entries) == 0 {
		return nil, fmt.Errorf("BFCL trace is empty")
	}
	return entries, nil
}

func ReparseTrace(cases []Case, source []TraceEntry, mode ParserMode) (RunResult, error) {
	if _, err := ParseParserMode(string(mode)); err != nil {
		return RunResult{}, err
	}
	if len(cases) == 0 || len(source) != len(cases) {
		return RunResult{}, fmt.Errorf("BFCL cases/trace count mismatch: %d/%d", len(cases), len(source))
	}
	byID := make(map[string]TraceEntry, len(source))
	for _, entry := range source {
		if entry.ID == "" {
			return RunResult{}, fmt.Errorf("BFCL trace entry id is required")
		}
		if _, exists := byID[entry.ID]; exists {
			return RunResult{}, fmt.Errorf("duplicate BFCL trace id %q", entry.ID)
		}
		byID[entry.ID] = entry
	}

	started := time.Now()
	result := RunResult{
		Trace:        make([]TraceEntry, 0, len(cases)),
		Entries:      make([]ResultEntry, 0, len(cases)),
		RepairCounts: make(map[string]int),
	}
	for _, entry := range cases {
		sourceEntry, exists := byID[entry.ID]
		if !exists {
			return RunResult{}, fmt.Errorf("BFCL trace is missing case %q", entry.ID)
		}
		trace := sourceEntry
		trace.Category = entry.Category
		trace.Result = ""
		trace.ToolCalls = nil
		trace.Repairs = nil
		trace.ParseError = ""
		if trace.Skipped {
			result.Skipped++
		} else if trace.Error != "" {
			result.Failed++
		} else {
			outcome, err := ParseMarkdownCallsWithMode(trace.Content, entry.Functions, mode)
			if err != nil {
				trace.ParseError = err.Error()
				result.ParseFailed++
			} else {
				trace.ToolCalls = outcome.Calls
				trace.Repairs = outcome.Repairs
				trace.Result, err = ToResultString(outcome.Calls, nil, LanguagePython)
				if err != nil {
					trace.ParseError = err.Error()
					result.ParseFailed++
				} else if len(outcome.Repairs) > 0 {
					result.Repaired++
					for _, repair := range outcome.Repairs {
						result.RepairCounts[repair]++
					}
				}
			}
		}
		result.Trace = append(result.Trace, trace)
		result.Entries = append(result.Entries, trace.ResultEntry)
		result.Usage.PromptTokens += trace.InputTokens
		result.Usage.CompletionTokens += trace.OutputTokens
		delete(byID, entry.ID)
	}
	if len(byID) != 0 {
		return RunResult{}, fmt.Errorf("BFCL trace contains cases outside selected data")
	}
	result.Elapsed = time.Since(started)
	return result, nil
}
