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
	local, err := LocalTools(options)
	if err != nil {
		return nil, err
	}
	tools := []agent.Tool{
		&weatherTool{provider: options.Provider},
		&nearestTransitTool{provider: options.Provider},
		&transitHoursTool{provider: options.Provider},
		&fxConvertTool{provider: options.Provider},
	}
	return append(tools, local...), nil
}

// CoreTools returns deterministic, provider-free tools that are useful to a
// general-purpose Agent. They are shared by the interactive Agent and the
// Go-native Primitive Bench profile.
func CoreTools(options Options) ([]agent.Tool, error) {
	resolver, err := agent.NewWorkspaceResolver(options.Workspace)
	if err != nil {
		return nil, err
	}
	return []agent.Tool{
		calculatorTool{},
		&dataQueryTool{workspace: resolver},
	}, nil
}

// LocalTools returns the deterministic tools suitable for the ordinary Agent.
// Unlike AssistantTools it never exposes provider-backed demo or mock facts.
func LocalTools(options Options) ([]agent.Tool, error) {
	core, err := CoreTools(options)
	if err != nil {
		return nil, err
	}
	if options.Clock == nil {
		options.Clock = systemClock{}
	}
	return append(core, &datetimeTool{clock: options.Clock}), nil
}

func ComputeTools(options Options) ([]agent.Tool, error) {
	all, err := CoreTools(options)
	if err != nil {
		return nil, err
	}
	result := make([]agent.Tool, 0, 1)
	for _, tool := range all {
		// calculator only. data_query would replace the boundary
		// suite's structured-data reasoning with a tool contract, so
		// registering it there replaces the reasoning under test with a tool
		// contract instead of measuring it. Boundary tasks compose read_file
		// with calculator; data_query stays a core/assistant and Go-native
		// Primitive tool.
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
		"Evaluate arithmetic with +, -, *, /, %, parentheses, and abs/min/max/round. Use precision to format decimal or money results.",
		`{"expression":"string","precision":"optional integer 0..15"}`,
		`{"type":"object","properties":{"expression":{"type":"string","minLength":1,"maxLength":4096},"precision":{"type":"integer","minimum":0,"maximum":15}},"required":["expression"],"additionalProperties":false}`,
	)
}

func (calculatorTool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Expression string `json:"expression"`
		Precision  *int   `json:"precision"`
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
	result, err := evaluateExpression(parsed, nil)
	if err != nil {
		return nil, invalidArguments("%v", err)
	}
	if math.IsNaN(result) || math.IsInf(result, 0) {
		return nil, invalidArguments("expression result must be finite")
	}
	if args.Precision != nil && (*args.Precision < 0 || *args.Precision > 15) {
		return nil, invalidArguments("precision must be between 0 and 15")
	}
	formatted := strconv.FormatFloat(result, 'f', -1, 64)
	if args.Precision != nil {
		factor := math.Pow10(*args.Precision)
		result = math.Round(result*factor) / factor
		formatted = strconv.FormatFloat(result, 'f', *args.Precision, 64)
	}
	return calculatorResult{Expression: expression, Result: result, Formatted: formatted}, nil
}

type calculatorResult struct {
	Expression string  `json:"expression"`
	Result     float64 `json:"result"`
	Formatted  string  `json:"formatted"`
}

func evaluateExpression(expression ast.Expr, variables map[string]float64) (float64, error) {
	switch value := expression.(type) {
	case *ast.BasicLit:
		if value.Kind != token.INT && value.Kind != token.FLOAT {
			return 0, fmt.Errorf("only numeric literals are allowed")
		}
		return strconv.ParseFloat(value.Value, 64)
	case *ast.Ident:
		result, ok := variables[value.Name]
		if !ok {
			return 0, fmt.Errorf("unknown numeric field %q", value.Name)
		}
		return result, nil
	case *ast.ParenExpr:
		return evaluateExpression(value.X, variables)
	case *ast.UnaryExpr:
		operand, err := evaluateExpression(value.X, variables)
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
		left, err := evaluateExpression(value.X, variables)
		if err != nil {
			return 0, err
		}
		right, err := evaluateExpression(value.Y, variables)
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
	case *ast.CallExpr:
		function, ok := value.Fun.(*ast.Ident)
		if !ok {
			return 0, fmt.Errorf("only abs, min, max, and round functions are allowed")
		}
		arguments := make([]float64, len(value.Args))
		for index, argument := range value.Args {
			result, err := evaluateExpression(argument, variables)
			if err != nil {
				return 0, err
			}
			arguments[index] = result
		}
		switch function.Name {
		case "abs":
			if len(arguments) != 1 {
				return 0, fmt.Errorf("abs requires one argument")
			}
			return math.Abs(arguments[0]), nil
		case "min", "max":
			if len(arguments) < 1 {
				return 0, fmt.Errorf("%s requires at least one argument", function.Name)
			}
			result := arguments[0]
			for _, argument := range arguments[1:] {
				if function.Name == "min" {
					result = math.Min(result, argument)
				} else {
					result = math.Max(result, argument)
				}
			}
			return result, nil
		case "round":
			if len(arguments) != 1 && len(arguments) != 2 {
				return 0, fmt.Errorf("round requires a value and optional decimal places")
			}
			places := 0
			if len(arguments) == 2 {
				places = int(arguments[1])
				if arguments[1] != float64(places) || places < 0 || places > 15 {
					return 0, fmt.Errorf("round decimal places must be an integer from 0 to 15")
				}
			}
			factor := math.Pow10(places)
			return math.Round(arguments[0]*factor) / factor, nil
		default:
			return 0, fmt.Errorf("function %q is not allowed", function.Name)
		}
	default:
		return 0, fmt.Errorf("expression contains an unsupported construct")
	}
}

type dataQueryTool struct{ workspace *agent.WorkspaceResolver }

type dataQueryAggregate struct {
	Op         string `json:"op"`
	Field      string `json:"field,omitempty"`
	Expression string `json:"expression,omitempty"`
	As         string `json:"as"`
}

type dataQueryRequest struct {
	Path       string         `json:"path"`
	Filter     map[string]any `json:"filter,omitempty"`
	Select     string         `json:"select,omitempty"`
	GroupBy    string         `json:"group_by,omitempty"`
	Operation  string         `json:"operation,omitempty"`
	Field      string         `json:"field,omitempty"`
	Expression string         `json:"expression,omitempty"`
}

type dataQueryResult struct {
	MatchedRows int              `json:"matched_rows"`
	Rows        []map[string]any `json:"rows,omitempty"`
	Value       any              `json:"value,omitempty"`
	Groups      []map[string]any `json:"groups,omitempty"`
}

func (*dataQueryTool) Spec() agent.ToolSpec {
	return strictSpec(
		"data_query",
		`Query tables; select="spot_sell" with filter={"currency":"EUR"}; sum with operation="sum", field="qty"; group formulas use expression.`,
		`{"path":"string","filter":{"field":"exact value"},"select":"comma-separated fields","group_by":"comma-separated fields","operation":"count|sum|avg|min|max|distinct_count","field":"numeric field","expression":"numeric row expression"}`,
		`{"type":"object","properties":{"path":{"type":"string","minLength":1},"filter":{"type":"object","additionalProperties":{}},"select":{"type":"string"},"group_by":{"type":"string"},"operation":{"type":"string","enum":["count","sum","avg","min","max","distinct_count"]},"field":{"type":"string"},"expression":{"type":"string"}},"required":["path"],"additionalProperties":false}`,
	)
}

func (t *dataQueryTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args dataQueryRequest
	if err := decodeArguments(raw, &args); err != nil {
		return nil, err
	}
	if strings.TrimSpace(args.Path) == "" {
		return nil, invalidArguments("path is required")
	}
	selectFields := splitDataFields(args.Select)
	groupFields := splitDataFields(args.GroupBy)
	aggregate, err := dataQueryAggregateSpec(args)
	if err != nil {
		return nil, invalidArguments("%v", err)
	}
	target, err := t.workspace.Resolve(args.Path)
	if err != nil {
		return nil, invalidArguments("path: %v", err)
	}
	rows, err := readStructuredRows(ctx, target)
	if err != nil {
		return nil, err
	}
	matched := make([]map[string]any, 0, len(rows))
	for _, row := range rows {
		if dataRowMatches(row, args.Filter) {
			matched = append(matched, row)
		}
	}
	result := dataQueryResult{MatchedRows: len(matched)}
	if len(groupFields) == 0 {
		if aggregate != nil {
			values, aggregateErr := aggregateDataRows(matched, []dataQueryAggregate{*aggregate})
			err = aggregateErr
			if err != nil {
				return nil, invalidArguments("%v", err)
			}
			result.Value = values["value"]
		}
		if len(selectFields) > 0 || aggregate == nil {
			result.Rows = selectDataRows(matched, selectFields, 100)
		}
		return result, nil
	}
	groups := make(map[string][]map[string]any)
	groupValues := make(map[string][]any)
	for _, row := range matched {
		values := make([]any, len(groupFields))
		for index, field := range groupFields {
			value, ok := dataFieldValue(row, field)
			if !ok {
				return nil, invalidArguments("group_by field %q is missing", field)
			}
			values[index] = value
		}
		encoded, _ := json.Marshal(values)
		key := string(encoded)
		groups[key] = append(groups[key], row)
		groupValues[key] = values
	}
	keys := make([]string, 0, len(groups))
	for key := range groups {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	for _, key := range keys {
		item := make(map[string]any, len(groupFields)+1)
		for index, field := range groupFields {
			item[field] = groupValues[key][index]
		}
		if aggregate != nil {
			aggregateValues, aggregateErr := aggregateDataRows(groups[key], []dataQueryAggregate{*aggregate})
			if aggregateErr != nil {
				return nil, invalidArguments("group %s: %v", key, aggregateErr)
			}
			item["value"] = aggregateValues["value"]
		}
		result.Groups = append(result.Groups, item)
	}
	return result, nil
}

func splitDataFields(value string) []string {
	var result []string
	for _, field := range strings.Split(value, ",") {
		if field = strings.TrimSpace(field); field != "" {
			result = append(result, field)
		}
	}
	return result
}

func dataQueryAggregateSpec(args dataQueryRequest) (*dataQueryAggregate, error) {
	op := strings.ToLower(strings.TrimSpace(args.Operation))
	field := strings.TrimSpace(args.Field)
	expression := strings.TrimSpace(args.Expression)
	if op == "" {
		if field != "" || expression != "" {
			return nil, fmt.Errorf("field or expression requires operation")
		}
		return nil, nil
	}
	aggregate := &dataQueryAggregate{Op: op, Field: field, Expression: expression, As: "value"}
	switch op {
	case "count":
		if field != "" || expression != "" {
			return nil, fmt.Errorf("count does not accept field or expression")
		}
	case "distinct_count":
		if field == "" || expression != "" {
			return nil, fmt.Errorf("distinct_count requires field and no expression")
		}
	case "sum", "avg", "min", "max":
		if (field == "") == (expression == "") {
			return nil, fmt.Errorf("%s requires exactly one of field or expression", op)
		}
	default:
		return nil, fmt.Errorf("unsupported operation %q", op)
	}
	return aggregate, nil
}

func dataRowMatches(row map[string]any, filter map[string]any) bool {
	for field, expected := range filter {
		actual, ok := dataFieldValue(row, field)
		if !ok || !dataValuesEqual(actual, expected) {
			return false
		}
	}
	return true
}

func dataValuesEqual(left, right any) bool {
	leftNumber, leftOK := dataNumber(left)
	rightNumber, rightOK := dataNumber(right)
	if leftOK && rightOK {
		return leftNumber == rightNumber
	}
	return strings.EqualFold(strings.TrimSpace(fmt.Sprint(left)), strings.TrimSpace(fmt.Sprint(right)))
}

func dataFieldValue(row map[string]any, field string) (any, bool) {
	var current any = row
	for _, part := range strings.Split(field, ".") {
		object, ok := current.(map[string]any)
		if !ok {
			return nil, false
		}
		current, ok = object[part]
		if !ok {
			return nil, false
		}
	}
	return current, true
}

func selectDataRows(rows []map[string]any, fields []string, limit int) []map[string]any {
	if len(rows) > limit {
		rows = rows[:limit]
	}
	result := make([]map[string]any, 0, len(rows))
	for _, row := range rows {
		if len(fields) == 0 {
			result = append(result, row)
			continue
		}
		selected := make(map[string]any, len(fields))
		for _, field := range fields {
			if value, ok := dataFieldValue(row, field); ok {
				selected[field] = value
			}
		}
		result = append(result, selected)
	}
	return result
}

func aggregateDataRows(rows []map[string]any, specs []dataQueryAggregate) (map[string]any, error) {
	result := make(map[string]any, len(specs))
	for _, spec := range specs {
		op := strings.ToLower(strings.TrimSpace(spec.Op))
		switch op {
		case "count":
			result[spec.As] = len(rows)
		case "distinct_count":
			values := make(map[string]struct{})
			for _, row := range rows {
				value, ok := dataFieldValue(row, spec.Field)
				if !ok {
					return nil, fmt.Errorf("field %q is missing", spec.Field)
				}
				encoded, _ := json.Marshal(value)
				values[string(encoded)] = struct{}{}
			}
			result[spec.As] = len(values)
		default:
			values := make([]float64, 0, len(rows))
			for _, row := range rows {
				value, err := dataAggregateValue(row, spec)
				if err != nil {
					return nil, err
				}
				values = append(values, value)
			}
			if len(values) == 0 {
				if op == "sum" {
					result[spec.As] = float64(0)
				} else {
					result[spec.As] = nil
				}
				continue
			}
			value := values[0]
			switch op {
			case "sum", "avg":
				value = 0
				for _, item := range values {
					value += item
				}
				if op == "avg" {
					value /= float64(len(values))
				}
			case "min":
				for _, item := range values[1:] {
					value = math.Min(value, item)
				}
			case "max":
				for _, item := range values[1:] {
					value = math.Max(value, item)
				}
			}
			result[spec.As] = value
		}
	}
	return result, nil
}

func dataAggregateValue(row map[string]any, spec dataQueryAggregate) (float64, error) {
	if spec.Field != "" {
		value, ok := dataFieldValue(row, spec.Field)
		if !ok {
			return 0, fmt.Errorf("field %q is missing", spec.Field)
		}
		number, ok := dataNumber(value)
		if !ok {
			return 0, fmt.Errorf("field %q is not numeric", spec.Field)
		}
		return number, nil
	}
	parsed, err := parser.ParseExpr(spec.Expression)
	if err != nil {
		return 0, fmt.Errorf("invalid aggregate expression %q: %v", spec.Expression, err)
	}
	variables := make(map[string]float64, len(row))
	for name, value := range row {
		if number, ok := dataNumber(value); ok {
			variables[name] = number
		}
	}
	value, err := evaluateExpression(parsed, variables)
	if err != nil {
		return 0, fmt.Errorf("aggregate expression %q: %v", spec.Expression, err)
	}
	if math.IsNaN(value) || math.IsInf(value, 0) {
		return 0, fmt.Errorf("aggregate expression result must be finite")
	}
	return value, nil
}

func dataNumber(value any) (float64, bool) {
	switch number := value.(type) {
	case float64:
		return number, true
	case float32:
		return float64(number), true
	case int:
		return float64(number), true
	case json.Number:
		parsed, err := number.Float64()
		return parsed, err == nil
	case string:
		parsed, err := strconv.ParseFloat(strings.TrimSpace(number), 64)
		return parsed, err == nil
	default:
		return 0, false
	}
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
			case ".json", ".jsonl", ".csv", ".tsv":
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
		return decodeDelimitedRows(data, ',')
	case ".tsv":
		return decodeDelimitedRows(data, '\t')
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

func decodeDelimitedRows(data []byte, comma rune) ([]map[string]any, error) {
	reader := csv.NewReader(bytes.NewReader(data))
	reader.Comma = comma
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

func parseRowTime(value string, location *time.Location) (time.Time, bool) {
	for _, layout := range []string{time.RFC3339, "2006-01-02 15:04:05", "2006-01-02"} {
		parsed, err := time.ParseInLocation(layout, value, location)
		if err == nil {
			return parsed, true
		}
	}
	return time.Time{}, false
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
