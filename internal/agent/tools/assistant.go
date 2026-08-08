package tools

import (
	"bytes"
	"context"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"io"
	"math"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

var ErrProviderUnavailable = agent.ErrProviderUnavailable

type Clock interface {
	Now() time.Time
}

type Provider interface {
	Weather(context.Context, string) (WeatherFact, error)
	NearestTransit(context.Context, string) (TransitFact, error)
	TransitHours(context.Context, string) (HoursFact, error)
	FXRate(context.Context, string, string) (RateFact, error)
}

type WeatherFact struct {
	City       string    `json:"city"`
	Condition  string    `json:"condition"`
	TempC      float64   `json:"temp_c"`
	ObservedAt time.Time `json:"observed_at"`
}

type TransitFact struct {
	Name      string   `json:"name"`
	DistanceM int      `json:"distance_m"`
	Lines     []string `json:"lines"`
}

type HoursFact struct {
	Station string `json:"station"`
	Open    string `json:"open"`
	Close   string `json:"close"`
	Weekday string `json:"weekday"`
}

type RateFact struct {
	Rate     float64   `json:"rate"`
	QuotedAt time.Time `json:"quoted_at"`
}

type Options struct {
	Provider  Provider
	Clock     Clock
	Workspace string
}

type systemClock struct{}

func (systemClock) Now() time.Time { return time.Now() }

func AssistantTools(options Options) ([]agent.Tool, error) {
	resolver, err := agent.NewWorkspaceResolver(options.Workspace)
	if err != nil {
		return nil, err
	}
	if options.Clock == nil {
		options.Clock = systemClock{}
	}
	return []agent.Tool{
		&weatherTool{provider: options.Provider},
		&nearestTransitTool{provider: options.Provider},
		&transitHoursTool{provider: options.Provider},
		&fxConvertTool{provider: options.Provider},
		calculatorTool{},
		&structuredQueryTool{workspace: resolver, clock: options.Clock},
		&datetimeTool{clock: options.Clock},
	}, nil
}

func ComputeTools(options Options) ([]agent.Tool, error) {
	all, err := AssistantTools(options)
	if err != nil {
		return nil, err
	}
	result := make([]agent.Tool, 0, 1)
	for _, tool := range all {
		// calculator only. structured_query cannot express the boundary
		// suite's multi-metric, computed and column-selecting aggregates, so
		// registering it there replaces the reasoning under test with a tool
		// contract instead of measuring it. Boundary tasks compose read_file
		// with calculator; structured_query stays an assistant-suite tool.
		if tool.Spec().Name == "calculator" {
			result = append(result, tool)
		}
	}
	return result, nil
}

type weatherTool struct{ provider Provider }

func (*weatherTool) Spec() agent.ToolSpec {
	return strictSpec(
		"weather",
		"Get the current observed weather for a city.",
		`{"city":"string"}`,
		`{"type":"object","properties":{"city":{"type":"string"}},"required":["city"],"additionalProperties":false}`,
	)
}

func (t *weatherTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		City string `json:"city"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	args.City = strings.TrimSpace(args.City)
	if args.City == "" {
		return nil, invalidArguments("city is required")
	}
	if t.provider == nil {
		return nil, ErrProviderUnavailable
	}
	return t.provider.Weather(ctx, args.City)
}

type nearestTransitTool struct{ provider Provider }

func (*nearestTransitTool) Spec() agent.ToolSpec {
	return strictSpec(
		"nearest_transit",
		"Find the nearest subway or bus station.",
		`{"kind":"subway|bus"}`,
		`{"type":"object","properties":{"kind":{"type":"string","enum":["subway","bus"]}},"required":["kind"],"additionalProperties":false}`,
	)
}

func (t *nearestTransitTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Kind string `json:"kind"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	args.Kind = strings.ToLower(strings.TrimSpace(args.Kind))
	if args.Kind != "subway" && args.Kind != "bus" {
		return nil, invalidArguments("kind must be subway or bus")
	}
	if t.provider == nil {
		return nil, ErrProviderUnavailable
	}
	return t.provider.NearestTransit(ctx, args.Kind)
}

type transitHoursTool struct{ provider Provider }

func (*transitHoursTool) Spec() agent.ToolSpec {
	return strictSpec(
		"transit_hours",
		"Get opening and closing hours for a transit station.",
		`{"station":"string"}`,
		`{"type":"object","properties":{"station":{"type":"string"}},"required":["station"],"additionalProperties":false}`,
	)
}

func (t *transitHoursTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Station string `json:"station"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	args.Station = strings.TrimSpace(args.Station)
	if args.Station == "" {
		return nil, invalidArguments("station is required")
	}
	if t.provider == nil {
		return nil, ErrProviderUnavailable
	}
	return t.provider.TransitHours(ctx, args.Station)
}

type fxConvertTool struct{ provider Provider }

func (*fxConvertTool) Spec() agent.ToolSpec {
	return strictSpec(
		"fx_convert",
		"Convert an amount using a provider exchange-rate quote.",
		`{"amount":"number","from":"string","to":"string"}`,
		`{"type":"object","properties":{"amount":{"type":"number"},"from":{"type":"string"},"to":{"type":"string"}},"required":["amount","from","to"],"additionalProperties":false}`,
	)
}

func (t *fxConvertTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Amount json.Number `json:"amount"`
		From   string      `json:"from"`
		To     string      `json:"to"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	amount, err := args.Amount.Float64()
	if err != nil || math.IsNaN(amount) || math.IsInf(amount, 0) {
		return nil, invalidArguments("amount must be a finite number")
	}
	from := strings.ToUpper(strings.TrimSpace(args.From))
	to := strings.ToUpper(strings.TrimSpace(args.To))
	if from == "" || to == "" || from == to {
		return nil, invalidArguments("from and to must be different currency codes")
	}
	if t.provider == nil {
		return nil, ErrProviderUnavailable
	}
	rate, err := t.provider.FXRate(ctx, from, to)
	if err != nil {
		return nil, err
	}
	return struct {
		Amount   float64   `json:"amount"`
		Rate     float64   `json:"rate"`
		Result   float64   `json:"result"`
		QuotedAt time.Time `json:"quoted_at"`
	}{Amount: amount, Rate: rate.Rate, Result: amount * rate.Rate, QuotedAt: rate.QuotedAt}, nil
}

type calculatorTool struct{}

func (calculatorTool) Spec() agent.ToolSpec {
	return strictSpec(
		"calculator",
		"Evaluate a finite arithmetic expression with +, -, *, /, %, and parentheses.",
		`{"expression":"string"}`,
		`{"type":"object","properties":{"expression":{"type":"string","minLength":1,"maxLength":4096}},"required":["expression"],"additionalProperties":false}`,
	)
}

func (calculatorTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Expression string `json:"expression"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	expression := strings.TrimSpace(args.Expression)
	if expression == "" || len(expression) > 4096 {
		return nil, invalidArguments("expression must contain 1 to 4096 bytes")
	}
	parsed, err := parser.ParseExpr(expression)
	if err != nil {
		return nil, invalidArguments("invalid expression: %v", err)
	}
	result, err := evaluateExpression(parsed)
	if err != nil {
		return nil, invalidArguments("%v", err)
	}
	if math.IsNaN(result) || math.IsInf(result, 0) {
		return nil, invalidArguments("expression result must be finite")
	}
	return struct {
		Expression string  `json:"expression"`
		Result     float64 `json:"result"`
	}{Expression: expression, Result: result}, nil
}

func evaluateExpression(expression ast.Expr) (float64, error) {
	switch value := expression.(type) {
	case *ast.BasicLit:
		if value.Kind != token.INT && value.Kind != token.FLOAT {
			return 0, fmt.Errorf("only numeric literals are allowed")
		}
		return strconv.ParseFloat(value.Value, 64)
	case *ast.ParenExpr:
		return evaluateExpression(value.X)
	case *ast.UnaryExpr:
		operand, err := evaluateExpression(value.X)
		if err != nil {
			return 0, err
		}
		switch value.Op {
		case token.ADD:
			return operand, nil
		case token.SUB:
			return -operand, nil
		default:
			return 0, fmt.Errorf("operator %s is not allowed", value.Op)
		}
	case *ast.BinaryExpr:
		left, err := evaluateExpression(value.X)
		if err != nil {
			return 0, err
		}
		right, err := evaluateExpression(value.Y)
		if err != nil {
			return 0, err
		}
		switch value.Op {
		case token.ADD:
			return left + right, nil
		case token.SUB:
			return left - right, nil
		case token.MUL:
			return left * right, nil
		case token.QUO:
			if right == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			return left / right, nil
		case token.REM:
			if right == 0 {
				return 0, fmt.Errorf("division by zero")
			}
			return math.Mod(left, right), nil
		default:
			return 0, fmt.Errorf("operator %s is not allowed", value.Op)
		}
	default:
		return 0, fmt.Errorf("expression contains an unsupported construct")
	}
}

type structuredQueryTool struct {
	workspace *agent.WorkspaceResolver
	clock     Clock
}

func (*structuredQueryTool) Spec() agent.ToolSpec {
	return strictSpec(
		"structured_query",
		"Filter JSON, JSONL, or CSV rows deterministically. filter must be empty, 本周/this week, or exact field=value predicates joined by comma or &&; comparison expressions are unsupported. sum/avg use the first numeric amount, total, value, revenue, or result field.",
		`{"path":"string","filter":"string","aggregate":"sum|count|avg"}`,
		`{"type":"object","properties":{"path":{"type":"string"},"filter":{"type":"string"},"aggregate":{"type":"string","enum":["sum","count","avg"]}},"required":["path","filter","aggregate"],"additionalProperties":false}`,
	)
}

type structuredQueryResult struct {
	MatchedRows  []map[string]any `json:"matched_rows"`
	Total        float64          `json:"total"`
	ExcludedRows []map[string]any `json:"excluded_rows"`
}

func (t *structuredQueryTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Path      string `json:"path"`
		Filter    string `json:"filter"`
		Aggregate string `json:"aggregate"`
	}
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	if strings.TrimSpace(args.Path) == "" {
		return nil, invalidArguments("path is required")
	}
	args.Aggregate = strings.ToLower(strings.TrimSpace(args.Aggregate))
	if args.Aggregate != "sum" && args.Aggregate != "count" && args.Aggregate != "avg" {
		return nil, invalidArguments("aggregate must be sum, count, or avg")
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, invalidArguments("path: %v", err)
	}
	rows, err := readStructuredRows(ctx, target)
	if err != nil {
		return nil, err
	}
	predicates, weekFilter, err := parseFilter(args.Filter)
	if err != nil {
		return nil, invalidArguments("filter: %v", err)
	}
	result := structuredQueryResult{
		MatchedRows:  make([]map[string]any, 0, len(rows)),
		ExcludedRows: make([]map[string]any, 0, len(rows)),
	}
	var values []float64
	for _, row := range rows {
		matched := rowMatches(row, predicates)
		if matched && weekFilter {
			matched = rowInCurrentWeek(row, t.clock.Now())
		}
		if !matched {
			result.ExcludedRows = append(result.ExcludedRows, row)
			continue
		}
		result.MatchedRows = append(result.MatchedRows, row)
		if args.Aggregate != "count" {
			value, ok := numericRowValue(row)
			if !ok {
				return nil, fmt.Errorf("matched row has no numeric amount, total, value, revenue, or result field")
			}
			values = append(values, value)
		}
	}
	switch args.Aggregate {
	case "count":
		result.Total = float64(len(result.MatchedRows))
	case "sum", "avg":
		for _, value := range values {
			result.Total += value
		}
		if args.Aggregate == "avg" && len(values) > 0 {
			result.Total /= float64(len(values))
		}
	}
	return result, nil
}

func readStructuredRows(ctx context.Context, target string) ([]map[string]any, error) {
	info, err := os.Stat(target)
	if err != nil {
		return nil, err
	}
	paths := []string{target}
	if info.IsDir() {
		paths = paths[:0]
		err = filepath.WalkDir(target, func(path string, entry os.DirEntry, walkErr error) error {
			if walkErr != nil {
				return walkErr
			}
			if err := ctx.Err(); err != nil {
				return err
			}
			if entry.IsDir() {
				return nil
			}
			switch strings.ToLower(filepath.Ext(path)) {
			case ".json", ".jsonl", ".csv":
				paths = append(paths, path)
			}
			return nil
		})
		if err != nil {
			return nil, err
		}
	}
	sort.Strings(paths)
	var result []map[string]any
	for _, path := range paths {
		rows, err := readStructuredFile(path)
		if err != nil {
			return nil, fmt.Errorf("read %s: %w", filepath.Base(path), err)
		}
		result = append(result, rows...)
	}
	return result, nil
}

func readStructuredFile(path string) ([]map[string]any, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}
	switch strings.ToLower(filepath.Ext(path)) {
	case ".csv":
		return decodeCSVRows(data)
	case ".json":
		var array []map[string]any
		decoder := json.NewDecoder(bytes.NewReader(data))
		decoder.UseNumber()
		if err := decoder.Decode(&array); err == nil {
			return array, nil
		}
		var object map[string]any
		decoder = json.NewDecoder(bytes.NewReader(data))
		decoder.UseNumber()
		if err := decoder.Decode(&object); err != nil {
			return nil, err
		}
		return []map[string]any{object}, nil
	default:
		decoder := json.NewDecoder(bytes.NewReader(data))
		decoder.UseNumber()
		var rows []map[string]any
		for {
			var row map[string]any
			if err := decoder.Decode(&row); err == io.EOF {
				break
			} else if err != nil {
				return nil, err
			}
			rows = append(rows, row)
		}
		return rows, nil
	}
}

func decodeCSVRows(data []byte) ([]map[string]any, error) {
	reader := csv.NewReader(bytes.NewReader(data))
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}
	if len(records) < 2 {
		return nil, nil
	}
	headers := records[0]
	rows := make([]map[string]any, 0, len(records)-1)
	for _, record := range records[1:] {
		if len(record) != len(headers) {
			return nil, fmt.Errorf("CSV row has %d fields, want %d", len(record), len(headers))
		}
		row := make(map[string]any, len(headers))
		for index, name := range headers {
			value := strings.TrimSpace(record[index])
			if number, err := strconv.ParseFloat(value, 64); err == nil {
				row[strings.TrimSpace(name)] = number
			} else {
				row[strings.TrimSpace(name)] = value
			}
		}
		rows = append(rows, row)
	}
	return rows, nil
}

func parseFilter(value string) (map[string]string, bool, error) {
	value = strings.TrimSpace(value)
	if value == "" {
		return nil, false, nil
	}
	week := strings.Contains(value, "本周") || strings.EqualFold(value, "this week")
	value = strings.ReplaceAll(value, "本周", "")
	value = strings.ReplaceAll(strings.ToLower(value), "this week", "")
	value = strings.NewReplacer("&&", ",", ";", ",", "，", ",").Replace(value)
	predicates := make(map[string]string)
	for _, item := range strings.Split(value, ",") {
		item = strings.TrimSpace(item)
		if item == "" {
			continue
		}
		parts := strings.SplitN(item, "=", 2)
		if len(parts) != 2 || strings.TrimSpace(parts[0]) == "" {
			return nil, false, fmt.Errorf("unsupported predicate %q; use field=value", item)
		}
		field := strings.TrimSpace(parts[0])
		expected := strings.TrimSpace(parts[1])
		if strings.ContainsAny(field, "<>!~") || strings.HasPrefix(expected, "=") {
			return nil, false, fmt.Errorf("unsupported predicate %q; only exact field=value is supported", item)
		}
		predicates[field] = expected
	}
	return predicates, week, nil
}

func rowMatches(row map[string]any, predicates map[string]string) bool {
	for key, expected := range predicates {
		actual, ok := row[key]
		if !ok || !strings.EqualFold(strings.TrimSpace(fmt.Sprint(actual)), expected) {
			return false
		}
	}
	return true
}

func rowInCurrentWeek(row map[string]any, now time.Time) bool {
	var raw string
	for _, key := range []string{"date", "time", "timestamp", "occurred_at", "created_at"} {
		if value, ok := row[key]; ok {
			raw = fmt.Sprint(value)
			break
		}
	}
	if raw == "" {
		return false
	}
	when, ok := parseRowTime(raw, now.Location())
	if !ok {
		return false
	}
	weekdayOffset := (int(now.Weekday()) + 6) % 7
	start := time.Date(now.Year(), now.Month(), now.Day()-weekdayOffset, 0, 0, 0, 0, now.Location())
	end := start.AddDate(0, 0, 7)
	return !when.Before(start) && when.Before(end)
}

func parseRowTime(value string, location *time.Location) (time.Time, bool) {
	for _, layout := range []string{time.RFC3339, "2006-01-02 15:04:05", "2006-01-02"} {
		parsed, err := time.ParseInLocation(layout, value, location)
		if err == nil {
			return parsed, true
		}
	}
	return time.Time{}, false
}

func numericRowValue(row map[string]any) (float64, bool) {
	for _, key := range []string{"amount", "total", "value", "revenue", "result"} {
		value, ok := row[key]
		if !ok {
			continue
		}
		switch number := value.(type) {
		case float64:
			return number, true
		case json.Number:
			parsed, err := number.Float64()
			return parsed, err == nil
		case string:
			parsed, err := strconv.ParseFloat(number, 64)
			return parsed, err == nil
		}
	}
	return 0, false
}

type datetimeTool struct{ clock Clock }

func (*datetimeTool) Spec() agent.ToolSpec {
	return agent.ToolSpec{
		Name:        "datetime",
		Description: "Read, compare, or add to dates and times deterministically.",
		Arguments:   `{"op":"now|compare|add","args":{...}}`,
		Parameters: json.RawMessage(`{
			"type":"object",
			"properties":{
				"op":{"type":"string","enum":["now","compare","add"]},
				"args":{"type":"object","description":"now uses {}; compare uses left and right; add uses time and duration."}
			},
			"required":["op","args"]
		}`),
		Strict: false,
	}
}

func strictSpec(name string, description string, arguments string, parameters string) agent.ToolSpec {
	return agent.ToolSpec{
		Name:        name,
		Description: description,
		Arguments:   arguments,
		Parameters:  json.RawMessage(parameters),
		Strict:      true,
	}
}

func (t *datetimeTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var request struct {
		Op   string          `json:"op"`
		Args json.RawMessage `json:"args"`
	}
	if err := decodeArguments(raw, &request); err != nil {
		return nil, err
	}
	switch strings.ToLower(strings.TrimSpace(request.Op)) {
	case "now":
		if len(bytes.TrimSpace(request.Args)) > 0 && string(bytes.TrimSpace(request.Args)) != "{}" {
			return nil, invalidArguments("now args must be empty")
		}
		now := t.clock.Now()
		return map[string]any{"now": now.Format(time.RFC3339), "timezone": now.Location().String()}, nil
	case "compare":
		var args struct {
			Left  string `json:"left"`
			Right string `json:"right"`
		}
		if err := decodeArguments(request.Args, &args); err != nil {
			return nil, err
		}
		left, leftOK := parseRowTime(args.Left, t.clock.Now().Location())
		right, rightOK := parseRowTime(args.Right, t.clock.Now().Location())
		if !leftOK || !rightOK {
			return nil, invalidArguments("left and right must be RFC3339 or YYYY-MM-DD times")
		}
		relation := 0
		if left.Before(right) {
			relation = -1
		} else if left.After(right) {
			relation = 1
		}
		return map[string]any{"left": args.Left, "right": args.Right, "relation": relation}, nil
	case "add":
		var args struct {
			Time     string `json:"time"`
			Duration string `json:"duration"`
		}
		if err := decodeArguments(request.Args, &args); err != nil {
			return nil, err
		}
		base, ok := parseRowTime(args.Time, t.clock.Now().Location())
		if !ok {
			return nil, invalidArguments("time must be RFC3339 or YYYY-MM-DD")
		}
		duration, err := time.ParseDuration(args.Duration)
		if err != nil {
			return nil, invalidArguments("duration: %v", err)
		}
		return map[string]any{"time": base.Format(time.RFC3339), "duration": args.Duration, "result": base.Add(duration).Format(time.RFC3339)}, nil
	default:
		return nil, invalidArguments("op must be now, compare, or add")
	}
}

func decodeArguments(raw json.RawMessage, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.DisallowUnknownFields()
	decoder.UseNumber()
	if err := decoder.Decode(target); err != nil {
		return invalidArguments("%v", err)
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return invalidArguments("trailing data")
	}
	return nil
}

func invalidArguments(format string, args ...any) error {
	return fmt.Errorf("%w: %s", agent.ErrInvalidToolArguments, fmt.Sprintf(format, args...))
}
