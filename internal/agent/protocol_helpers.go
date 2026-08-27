package agent

import (
	"encoding/json"
	"regexp"
	"strings"
)

func looksLikeBareToolCall(candidate string) bool {
	var object map[string]json.RawMessage
	if json.Unmarshal([]byte(candidate), &object) != nil || object == nil {
		return false
	}
	_, hasName := object["name"]
	_, hasArguments := object["arguments"]
	return hasName || hasArguments
}

const (
	maxAnswerToolStringRunes = 2400
	answerToolPrefixRunes    = 320
	answerToolChunkRunes     = maxAnswerToolStringRunes - answerToolPrefixRunes - 40
)

var relevanceTerm = regexp.MustCompile(`(?i)[a-z0-9_./-]+|[\p{Han}]`)

func compactToolResult(task string, wrapped string) string {
	const (
		open  = "<tool_result>"
		close = "</tool_result>"
	)
	if !strings.HasPrefix(wrapped, open) || !strings.HasSuffix(wrapped, close) {
		return wrapped
	}
	payload := strings.TrimSuffix(strings.TrimPrefix(wrapped, open), close)
	var value any
	if json.Unmarshal([]byte(payload), &value) != nil {
		return wrapped
	}
	value = compactToolValue(task, value)
	encoded, err := json.Marshal(value)
	if err != nil {
		return wrapped
	}
	return open + string(encoded) + close
}

func compactToolValue(task string, value any) any {
	switch typed := value.(type) {
	case string:
		return relevantExcerpt(task, typed)
	case []any:
		for index := range typed {
			typed[index] = compactToolValue(task, typed[index])
		}
		return typed
	case map[string]any:
		for key, item := range typed {
			typed[key] = compactToolValue(task, item)
		}
		return typed
	default:
		return value
	}
}

func relevantExcerpt(task string, value string) string {
	runes := []rune(value)
	if len(runes) <= maxAnswerToolStringRunes {
		return value
	}
	prefix := string(runes[:answerToolPrefixRunes])
	terms := uniqueTerms(task)
	bestStart := answerToolPrefixRunes
	bestScore := -1
	const overlap = 160
	for start := answerToolPrefixRunes; start < len(runes); start += answerToolChunkRunes - overlap {
		end := min(start+answerToolChunkRunes, len(runes))
		candidate := strings.ToLower(string(runes[start:end]))
		score := 0
		for _, term := range terms {
			score += strings.Count(candidate, term)
		}
		if score > bestScore {
			bestStart = start
			bestScore = score
		}
	}
	bestEnd := min(bestStart+answerToolChunkRunes, len(runes))
	return prefix + "\n...[tool result compacted]...\n" + string(runes[bestStart:bestEnd])
}

func uniqueTerms(value string) []string {
	matches := relevanceTerm.FindAllString(strings.ToLower(value), -1)
	seen := make(map[string]struct{}, len(matches))
	result := make([]string, 0, len(matches))
	for _, match := range matches {
		if len(match) == 1 {
			continue
		}
		if _, exists := seen[match]; exists {
			continue
		}
		seen[match] = struct{}{}
		result = append(result, match)
	}
	return result
}
