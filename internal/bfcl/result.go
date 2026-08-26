package bfcl

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"unicode"

	"github.com/no22/RWKV-Agent/internal/continuation/toolchat"
)

type Language string

const (
	LanguagePython     Language = "python"
	LanguageJava       Language = "java"
	LanguageJavaScript Language = "javascript"
)

type ResultEntry struct {
	ID           string  `json:"id"`
	Category     string  `json:"-"`
	Result       string  `json:"result"`
	InputTokens  int     `json:"input_token_count,omitempty"`
	OutputTokens int     `json:"output_token_count,omitempty"`
	Latency      float64 `json:"latency,omitempty"`
	ModelCalls   int     `json:"model_calls,omitempty"`
}

type orderedObject []orderedField

type orderedField struct {
	Name  string
	Value any
}

var asciiPythonIdentifier = regexp.MustCompile(`^[A-Za-z_][A-Za-z0-9_]*$`)

func ToResultString(calls []toolchat.ToolCall, names map[string]string, language Language) (string, error) {
	if len(calls) == 0 {
		return "", nil
	}
	encoded := make([]string, 0, len(calls))
	for _, call := range calls {
		name := call.Name
		if original, ok := names[name]; ok {
			name = original
		}
		if !pythonCallable(name) {
			return "", fmt.Errorf("invalid BFCL function name %q", name)
		}
		arguments, err := decodeOrderedObject([]byte(call.Arguments))
		if err != nil {
			return "", fmt.Errorf("decode arguments for %q: %w", name, err)
		}
		parts := make([]string, 0, len(arguments))
		for _, argument := range arguments {
			if !pythonIdentifier(argument.Name) {
				return "", fmt.Errorf("invalid argument name %q for %q", argument.Name, name)
			}
			value := pythonLiteral(argument.Value)
			if language == LanguageJava || language == LanguageJavaScript {
				value = strconv.Quote(javaScriptArgumentString(argument.Value))
			}
			parts = append(parts, argument.Name+"="+value)
		}
		encoded = append(encoded, name+"("+strings.Join(parts, ", ")+")")
	}
	return "[" + strings.Join(encoded, ", ") + "]", nil
}

func decodeOrderedObject(data []byte) (orderedObject, error) {
	decoder := json.NewDecoder(bytes.NewReader(data))
	decoder.UseNumber()
	value, err := decodeJSONValue(decoder)
	if err != nil {
		return nil, err
	}
	if _, err := decoder.Token(); err != io.EOF {
		if err == nil {
			return nil, fmt.Errorf("unexpected trailing JSON value")
		}
		return nil, err
	}
	object, ok := value.(orderedObject)
	if !ok {
		return nil, fmt.Errorf("arguments must be a JSON object")
	}
	return object, nil
}

func decodeJSONValue(decoder *json.Decoder) (any, error) {
	token, err := decoder.Token()
	if err != nil {
		return nil, err
	}
	delimiter, isDelimiter := token.(json.Delim)
	if !isDelimiter {
		return token, nil
	}
	switch delimiter {
	case '{':
		var object orderedObject
		for decoder.More() {
			nameToken, err := decoder.Token()
			if err != nil {
				return nil, err
			}
			name, ok := nameToken.(string)
			if !ok {
				return nil, fmt.Errorf("object key is not a string")
			}
			value, err := decodeJSONValue(decoder)
			if err != nil {
				return nil, err
			}
			object = append(object, orderedField{Name: name, Value: value})
		}
		if _, err := decoder.Token(); err != nil {
			return nil, err
		}
		return object, nil
	case '[':
		var values []any
		for decoder.More() {
			value, err := decodeJSONValue(decoder)
			if err != nil {
				return nil, err
			}
			values = append(values, value)
		}
		if _, err := decoder.Token(); err != nil {
			return nil, err
		}
		return values, nil
	default:
		return nil, fmt.Errorf("unexpected JSON delimiter %q", delimiter)
	}
}

func pythonLiteral(value any) string {
	switch current := value.(type) {
	case nil:
		return "None"
	case bool:
		if current {
			return "True"
		}
		return "False"
	case string:
		return strconv.Quote(current)
	case json.Number:
		return current.String()
	case []any:
		parts := make([]string, 0, len(current))
		for _, child := range current {
			parts = append(parts, pythonLiteral(child))
		}
		return "[" + strings.Join(parts, ", ") + "]"
	case orderedObject:
		parts := make([]string, 0, len(current))
		for _, field := range current {
			parts = append(parts, strconv.Quote(field.Name)+": "+pythonLiteral(field.Value))
		}
		return "{" + strings.Join(parts, ", ") + "}"
	default:
		panic(fmt.Sprintf("unsupported decoded JSON value %T", value))
	}
}

func javaScriptArgumentString(value any) string {
	switch current := value.(type) {
	case nil:
		return "null"
	case bool:
		return strconv.FormatBool(current)
	case string:
		return current
	case json.Number:
		return current.String()
	case []any:
		parts := make([]string, 0, len(current))
		for _, child := range current {
			parts = append(parts, javaScriptArgumentString(child))
		}
		return "[" + strings.Join(parts, ", ") + "]"
	case orderedObject:
		parts := make([]string, 0, len(current))
		for _, field := range current {
			parts = append(parts, field.Name+": "+javaScriptArgumentString(field.Value))
		}
		return "{" + strings.Join(parts, ", ") + "}"
	default:
		panic(fmt.Sprintf("unsupported decoded JSON value %T", value))
	}
}

func pythonCallable(value string) bool {
	parts := strings.Split(value, ".")
	if len(parts) == 0 {
		return false
	}
	for _, part := range parts {
		if !pythonIdentifier(part) {
			return false
		}
	}
	return true
}

func pythonIdentifier(value string) bool {
	if asciiPythonIdentifier.MatchString(value) {
		return true
	}
	for index, current := range []rune(value) {
		if index == 0 {
			if current != '_' && !unicode.IsLetter(current) && !unicode.Is(unicode.Other_ID_Start, current) {
				return false
			}
			continue
		}
		if current != '_' && !unicode.IsLetter(current) && !unicode.IsDigit(current) &&
			!unicode.Is(unicode.Mn, current) && !unicode.Is(unicode.Mc, current) &&
			!unicode.Is(unicode.Pc, current) && !unicode.Is(unicode.Other_ID_Continue, current) {
			return false
		}
	}
	return value != ""
}

func WriteResults(resultDir, modelDirName string, entries []ResultEntry) error {
	grouped := make(map[string][]ResultEntry)
	for _, entry := range entries {
		if entry.ID == "" || entry.Category == "" {
			return fmt.Errorf("BFCL result id and category are required")
		}
		grouped[entry.Category] = append(grouped[entry.Category], entry)
	}
	categories := make([]string, 0, len(grouped))
	for category := range grouped {
		categories = append(categories, category)
	}
	sort.Strings(categories)
	for _, category := range categories {
		group := "non_live"
		if strings.HasPrefix(category, "live_") {
			group = "live"
		}
		directory := filepath.Join(resultDir, modelDirName, group)
		if err := os.MkdirAll(directory, 0o700); err != nil {
			return err
		}
		path := filepath.Join(directory, "BFCL_v4_"+category+"_result.json")
		if err := writeResultFile(path, grouped[category]); err != nil {
			return err
		}
	}
	return nil
}

func writeResultFile(path string, entries []ResultEntry) error {
	temporary, err := os.CreateTemp(filepath.Dir(path), ".bfcl-result-*")
	if err != nil {
		return err
	}
	temporaryPath := temporary.Name()
	defer os.Remove(temporaryPath)
	writer := bufio.NewWriter(temporary)
	encoder := json.NewEncoder(writer)
	encoder.SetEscapeHTML(false)
	for _, entry := range entries {
		if err := encoder.Encode(entry); err != nil {
			temporary.Close()
			return err
		}
	}
	if err := writer.Flush(); err != nil {
		temporary.Close()
		return err
	}
	if err := temporary.Sync(); err != nil {
		temporary.Close()
		return err
	}
	if err := temporary.Close(); err != nil {
		return err
	}
	return os.Rename(temporaryPath, path)
}
