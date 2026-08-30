package bfcl

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

const AdditionalFunctionPrompt = "I have updated some more functions you can choose from. What about now?"

type MultiTurnCase struct {
	ID               string
	Category         string
	Turns            [][]Message
	InitialConfig    map[string]any
	Path             []string
	InvolvedClasses  []string
	MissedFunction   map[string][]string
	ExcludedFunction []string
}

type multiTurnRecord struct {
	ID               string              `json:"id"`
	Question         [][]Message         `json:"question"`
	InitialConfig    map[string]any      `json:"initial_config"`
	Path             []string            `json:"path"`
	InvolvedClasses  []string            `json:"involved_classes"`
	MissedFunction   map[string][]string `json:"missed_function"`
	ExcludedFunction []string            `json:"excluded_function"`
}

type MultiTurnFunction struct {
	Name  string
	Class string
	Raw   json.RawMessage
}

type MultiTurnCatalog struct {
	Functions []MultiTurnFunction
	HoldoutAt map[string]int
}

var multiTurnFunctionDocFiles = map[string]string{
	"GorillaFileSystem": "gorilla_file_system.json",
	"MathAPI":           "math_api.json",
	"MessageAPI":        "message_api.json",
	"TwitterAPI":        "posting_api.json",
	"TicketAPI":         "ticket_api.json",
	"TradingBot":        "trading_bot.json",
	"TravelAPI":         "travel_booking.json",
	"VehicleControlAPI": "vehicle_control.json",
	"WebSearchAPI":      "web_search.json",
	"MemoryAPI_kv":      "memory_kv.json",
	"MemoryAPI_vector":  "memory_vector.json",
	"MemoryAPI_rec_sum": "memory_rec_sum.json",
}

func LoadMultiTurnSplit(dataDir, category string) ([]MultiTurnCase, error) {
	category = strings.TrimSpace(category)
	if !strings.HasPrefix(category, "multi_turn_") || strings.ContainsAny(category, `/\\`) {
		return nil, fmt.Errorf("invalid BFCL multi-turn category %q", category)
	}
	return readJSONLSplit(dataDir, category, decodeMultiTurnCase)
}

func decodeMultiTurnCase(line []byte, category string) (MultiTurnCase, error) {
	decoder := json.NewDecoder(bytes.NewReader(line))
	decoder.UseNumber()
	var record multiTurnRecord
	if err := decoder.Decode(&record); err != nil {
		return MultiTurnCase{}, err
	}
	if strings.TrimSpace(record.ID) == "" || len(record.Question) == 0 || len(record.InvolvedClasses) == 0 {
		return MultiTurnCase{}, fmt.Errorf("multi-turn case requires id, at least one turn, and involved_classes")
	}
	for turn, messages := range record.Question {
		if len(messages) == 0 {
			if _, holdout := record.MissedFunction[strconv.Itoa(turn)]; !holdout {
				return MultiTurnCase{}, fmt.Errorf("case %q turn %d is empty without a holdout function", record.ID, turn)
			}
			continue
		}
		for index, message := range messages {
			if message.Role != "system" && message.Role != "user" && message.Role != "assistant" {
				return MultiTurnCase{}, fmt.Errorf("case %q turn %d message %d has unsupported role %q", record.ID, turn, index, message.Role)
			}
		}
	}
	return MultiTurnCase{
		ID: record.ID, Category: category, Turns: record.Question,
		InitialConfig: record.InitialConfig, Path: record.Path,
		InvolvedClasses: record.InvolvedClasses, MissedFunction: record.MissedFunction,
		ExcludedFunction: record.ExcludedFunction,
	}, nil
}

func LoadMultiTurnCatalog(dataDir string, entry MultiTurnCase) (MultiTurnCatalog, error) {
	excluded := make(map[string]struct{}, len(entry.ExcludedFunction))
	for _, name := range entry.ExcludedFunction {
		excluded[name] = struct{}{}
	}
	holdout := make(map[string]int)
	for turnValue, names := range entry.MissedFunction {
		turn, err := strconv.Atoi(turnValue)
		if err != nil || turn < 0 {
			return MultiTurnCatalog{}, fmt.Errorf("case %q has invalid holdout turn %q", entry.ID, turnValue)
		}
		for _, name := range names {
			holdout[name] = turn
		}
	}
	var functions []MultiTurnFunction
	for _, className := range entry.InvolvedClasses {
		fileName, ok := multiTurnFunctionDocFiles[className]
		if !ok {
			return MultiTurnCatalog{}, fmt.Errorf("case %q has unsupported involved class %q", entry.ID, className)
		}
		path := filepath.Join(dataDir, "multi_turn_func_doc", fileName)
		file, err := os.Open(path)
		if err != nil {
			return MultiTurnCatalog{}, fmt.Errorf("open BFCL function docs for %s: %w", className, err)
		}
		scanner := bufio.NewScanner(file)
		scanner.Buffer(make([]byte, 64*1024), 4*1024*1024)
		for scanner.Scan() {
			raw := append(json.RawMessage(nil), scanner.Bytes()...)
			var definition map[string]json.RawMessage
			if err := json.Unmarshal(raw, &definition); err != nil {
				file.Close()
				return MultiTurnCatalog{}, fmt.Errorf("decode BFCL function docs %s: %w", path, err)
			}
			var name string
			if err := json.Unmarshal(definition["name"], &name); err != nil || strings.TrimSpace(name) == "" {
				file.Close()
				return MultiTurnCatalog{}, fmt.Errorf("decode BFCL function name in %s", path)
			}
			if _, skip := excluded[name]; skip {
				continue
			}
			delete(definition, "response")
			promptRaw, err := json.Marshal(definition)
			if err != nil {
				file.Close()
				return MultiTurnCatalog{}, err
			}
			functions = append(functions, MultiTurnFunction{Name: name, Class: className, Raw: promptRaw})
		}
		if err := scanner.Err(); err != nil {
			file.Close()
			return MultiTurnCatalog{}, err
		}
		file.Close()
	}
	return MultiTurnCatalog{Functions: functions, HoldoutAt: holdout}, nil
}

func (catalog MultiTurnCatalog) ForTurn(turn int, classes []string) []MultiTurnFunction {
	selectedClasses := make(map[string]struct{}, len(classes))
	for _, className := range classes {
		selectedClasses[className] = struct{}{}
	}
	result := make([]MultiTurnFunction, 0, len(catalog.Functions))
	for _, function := range catalog.Functions {
		if len(selectedClasses) > 0 {
			if _, ok := selectedClasses[function.Class]; !ok {
				continue
			}
		}
		if releaseTurn, held := catalog.HoldoutAt[function.Name]; held && turn < releaseTurn {
			continue
		}
		result = append(result, function)
	}
	return result
}

func MultiTurnFunctionNames(functions []MultiTurnFunction) []string {
	names := make([]string, 0, len(functions))
	for _, function := range functions {
		names = append(names, function.Name)
	}
	return names
}
