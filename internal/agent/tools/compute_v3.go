package tools

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"go/parser"
	"math"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// agent-tool-v3 calculator and data_query (docs/design/agent-tool-v3.md §2.9–§2.10).
// "^" is not added: Go's parser gives it the precedence of "+", so 2*3^2
// would silently mean (2*3)^2. Powers go through pow(a, b) instead, and the
// error for "^" or "**" says so.
const calculatorV3Description = "Evaluate arithmetic with +, -, *, /, %, parentheses, and abs/min/max/round/sqrt/pow/ln/log10/exp. Use precision to format decimal or money results."

const calculatorV3Hint = "calculator 只做四则运算和 abs/min/max/round/sqrt/pow/ln/log10/exp，乘方写 pow(a, b)，开方写 sqrt(x)；更复杂的计算用 bash：awk 'BEGIN{printf \"%.4f\\n\", 表达式}'。"

func extendedFunction(name string, arguments []float64) (float64, bool, error) {
	one := func(apply func(float64) float64, domain func(float64) bool) (float64, bool, error) {
		if len(arguments) != 1 {
			return 0, true, fmt.Errorf("%s requires one argument", name)
		}
		if domain != nil && !domain(arguments[0]) {
			return 0, true, fmt.Errorf("%s(%s) is undefined", name, strconv.FormatFloat(arguments[0], 'g', -1, 64))
		}
		return apply(arguments[0]), true, nil
	}
	positive := func(x float64) bool { return x > 0 }
	switch name {
	case "sqrt":
		return one(math.Sqrt, func(x float64) bool { return x >= 0 })
	case "ln":
		return one(math.Log, positive)
	case "log10":
		return one(math.Log10, positive)
	case "exp":
		return one(math.Exp, nil)
	case "pow":
		if len(arguments) != 2 {
			return 0, true, fmt.Errorf("pow requires two arguments: pow(base, exponent)")
		}
		return math.Pow(arguments[0], arguments[1]), true, nil
	}
	return 0, false, nil
}

var (
	mathPrefix        = regexp.MustCompile(`\bmath\.`)
	functionCall      = regexp.MustCompile(`[A-Za-z_]\s*\(`)
	thousandsNumber   = regexp.MustCompile(`\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b`)
	percentOfNumber   = regexp.MustCompile(`(\d+(?:\.\d+)?)\s*%(\s*(?:$|[)+\-*/,]))`)
	expressionSymbols = strings.NewReplacer("×", "*", "÷", "/", "（", "(", "）", ")", "，", ",", "＋", "+", "－", "-", "＊", "*", "／", "/", "　", " ")
)

// normalizeExpression rewrites the ways people write arithmetic that Go's
// parser rejects (each a hard error on the 10-21 probe): × ÷ and full-width
// punctuation, a math. prefix, thousands separators (only outside function
// calls, where "pow(2,100)" must keep its comma), a percent sign after a
// number ("200*15%" is 200*(15/100); "10%3" stays a remainder), and a
// trailing "=".
func normalizeExpression(expression string) string {
	expression = strings.TrimSpace(expressionSymbols.Replace(expression))
	expression = strings.TrimSpace(strings.TrimSuffix(expression, "="))
	expression = mathPrefix.ReplaceAllString(expression, "")
	if !functionCall.MatchString(expression) {
		expression = thousandsNumber.ReplaceAllStringFunc(expression, func(number string) string {
			return strings.ReplaceAll(number, ",", "")
		})
	}
	return percentOfNumber.ReplaceAllString(expression, "($1/100)$2")
}

type calculatorV3Tool struct{}

func (calculatorV3Tool) Spec() agent.ToolSpec {
	spec := calculatorTool{}.Spec()
	spec.Description = calculatorV3Description
	return spec
}

func (calculatorV3Tool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Expression string `json:"expression"`
		Precision  *int   `json:"precision"`
	}
	if err := agent.DecodeToolArguments(raw, &args); err != nil {
		return nil, err
	}
	expression := normalizeExpression(args.Expression)
	if expression == "" || len(expression) > 4096 {
		return nil, invalidArguments("expression must contain 1 to 4096 bytes")
	}
	if strings.Contains(expression, "^") || strings.Contains(expression, "**") {
		return nil, invalidArguments("不支持 ^ 或 ** 写乘方。%s", calculatorV3Hint)
	}
	parsed, err := parser.ParseExpr(expression)
	if err != nil {
		return nil, invalidArguments("invalid expression: %v。%s", err, calculatorV3Hint)
	}
	result, err := evaluateWith(parsed, nil, true)
	if err != nil {
		return nil, invalidArguments("%v。%s", err, calculatorV3Hint)
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

type dataQueryV3Tool struct{ inner *dataQueryTool }

func (t *dataQueryV3Tool) Spec() agent.ToolSpec { return t.inner.Spec() }

type dataQueryV3Result struct {
	dataQueryResult
	Ignored string `json:"ignored,omitempty"`
	Note    string `json:"note,omitempty"`
}

const (
	dataQueryV3RowCap   = 100
	dataQueryV3MoreNote = "共匹配 %d 行，只列出了前 %d 行。要统计全部行用 operation（count/sum/avg/min/max），或加 filter 缩小范围。"
)

// Execute relaxes the aggregate argument combinations that made a third of
// agent-tool-v2.0's data_query calls fail on the 10-17 exam, accepts a limit on the
// listed rows, then runs agent-tool-v2.0's query and says when rows were left out.
func (t *dataQueryV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args map[string]any
	if err := json.Unmarshal(raw, &args); err != nil {
		return t.inner.Execute(ctx, raw)
	}
	text := func(key string) string {
		value, _ := args[key].(string)
		return strings.TrimSpace(value)
	}
	changed := false
	limit := dataQueryV3RowCap
	if value, ok := args["limit"]; ok {
		delete(args, "limit")
		changed = true
		if number, ok := dataNumber(value); ok && number >= 1 {
			limit = min(int(number), dataQueryV3RowCap)
		}
	}
	op := strings.ToLower(text("operation"))
	field, expression := text("field"), text("expression")
	ignored := ""
	switch op {
	case "count":
		if field != "" {
			delete(args, "field")
			ignored = "field"
		}
		if expression != "" {
			delete(args, "expression")
			ignored = strings.Trim(ignored+",expression", ",")
		}
	case "sum", "avg", "min", "max":
		if field != "" && expression != "" {
			delete(args, "field")
			ignored = "field"
		}
		if field == "" && expression == "" {
			return nil, invalidArguments(`%s 需要 field（列名）或 expression（按行计算的式子），例如 {"operation":"%s","field":"qty"}。`, op, op)
		}
	}
	if ignored != "" || changed {
		rewritten, err := json.Marshal(args)
		if err != nil {
			return nil, err
		}
		raw = rewritten
	}
	value, err := t.inner.Execute(ctx, raw)
	if err != nil {
		return nil, err
	}
	result, ok := value.(dataQueryResult)
	if !ok {
		return nil, errors.New("data_query: unexpected result type")
	}
	out := dataQueryV3Result{dataQueryResult: result, Ignored: ignored}
	if len(out.Rows) > limit {
		out.Rows = out.Rows[:limit]
	}
	if len(out.Rows) > 0 && len(out.Rows) < out.MatchedRows {
		out.Note = fmt.Sprintf(dataQueryV3MoreNote, out.MatchedRows, len(out.Rows))
	}
	return out, nil
}

// formattedNumberPattern is a number written for people: thousands
// separators and/or a currency sign ("1,200", "$12.50", "¥ 3,480.00").
var formattedNumberPattern = regexp.MustCompile(`^([-+]?)\s*[$¥€£]?\s*([-+]?)(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)$`)

// formattedNumber reads such a cell as a number. A plain number without a
// sign or separators is left to dataNumber, so this changes nothing agent-tool-v2.0
// already parsed.
func formattedNumber(value string) (float64, bool) {
	text := strings.TrimSpace(value)
	match := formattedNumberPattern.FindStringSubmatch(text)
	if match == nil || !strings.ContainsAny(text, ",$¥€£") {
		return 0, false
	}
	number, err := strconv.ParseFloat(strings.ReplaceAll(match[3], ",", ""), 64)
	if err != nil {
		return 0, false
	}
	if match[1] == "-" || match[2] == "-" {
		number = -number
	}
	return number, true
}

// normalizeRowsV3 turns formatted number cells into numbers, so sum/avg and
// comparisons work on a CSV column such as price "1,200" (agent-tool-v2.0 reported
// it as not numeric).
func normalizeRowsV3(rows []map[string]any) {
	for _, row := range rows {
		for key, value := range row {
			if text, ok := value.(string); ok {
				if number, ok := formattedNumber(text); ok {
					row[key] = number
				}
			}
		}
	}
}

// filterComparisons are the operator prefixes a agent-tool-v3 filter value may
// carry, longest first so ">=" is not read as ">".
var filterComparisons = []string{">=", "<=", "!=", "<>", "==", ">", "<", "="}

// dataRowMatchesV3 extends agent-tool-v2.0's exact-match filter with what models
// write anyway: a value such as ">3" or ">=2026-10-01" is a comparison, and a
// list is "any of". agent-tool-v2.0 read ">3" as the literal text and answered
// matched_rows 0 without an error, which the model took as "no such rows".
func dataRowMatchesV3(row map[string]any, filter map[string]any) bool {
	for field, expected := range filter {
		actual, ok := dataFieldValue(row, field)
		if !ok || !filterValueMatches(actual, expected) {
			return false
		}
	}
	return true
}

func filterValueMatches(actual, expected any) bool {
	switch value := expected.(type) {
	case []any:
		for _, item := range value {
			if filterValueMatches(actual, item) {
				return true
			}
		}
		return false
	case string:
		text := strings.TrimSpace(value)
		if number, ok := formattedNumber(text); ok {
			return dataValuesEqual(actual, number)
		}
		for _, op := range filterComparisons {
			operand, found := strings.CutPrefix(text, op)
			operand = strings.TrimSpace(operand)
			if !found || operand == "" {
				continue
			}
			return compareFilterValue(actual, op, operand)
		}
	}
	return dataValuesEqual(actual, expected)
}

// compareFilterValue orders numbers as numbers, dates and times as times,
// and anything else as text.
func compareFilterValue(actual any, op, operand string) bool {
	switch op {
	case "==", "=":
		return dataValuesEqual(actual, operand)
	case "!=", "<>":
		return !dataValuesEqual(actual, operand)
	}
	if number, ok := formattedNumber(operand); ok {
		operand = strconv.FormatFloat(number, 'f', -1, 64)
	}
	order := 0
	left, leftOK := dataNumber(actual)
	right, rightOK := dataNumber(operand)
	if leftOK && rightOK {
		order = compareFloat(left, right)
	} else {
		text := strings.TrimSpace(fmt.Sprint(actual))
		leftTime, leftTimeOK := parseRowTime(text, time.UTC)
		rightTime, rightTimeOK := parseRowTime(operand, time.UTC)
		if leftTimeOK && rightTimeOK {
			order = leftTime.Compare(rightTime)
		} else {
			order = strings.Compare(text, operand)
		}
	}
	switch op {
	case ">":
		return order > 0
	case ">=":
		return order >= 0
	case "<":
		return order < 0
	default: // "<="
		return order <= 0
	}
}

func compareFloat(left, right float64) int {
	switch {
	case left < right:
		return -1
	case left > right:
		return 1
	}
	return 0
}

// LocalToolsV3 is agent-tool-v3's always-present compute group: calculator,
// data_query and datetime, in agent-tool-v2.0's order.
func LocalToolsV3(options Options) ([]agent.Tool, error) {
	resolver, err := agent.NewWorkspaceResolverV3(options.Workspace, options.Filesystem)
	if err != nil {
		return nil, err
	}
	if options.Clock == nil {
		options.Clock = systemClock{}
	}
	return []agent.Tool{
		calculatorV3Tool{},
		&dataQueryV3Tool{inner: &dataQueryTool{workspace: resolver, match: dataRowMatchesV3, normalize: normalizeRowsV3}},
		&datetimeV3Tool{inner: &datetimeTool{clock: options.Clock}},
	}, nil
}

// datetimeV3Tool is agent-tool-v2.0's datetime with the answers models asked for and
// could not get (10-21 review), under the same description and arguments:
// compare also gives the days between, add takes days, weeks, months and
// years ("3d", "2w", "1 month", "3天"), every date comes with its weekday,
// and the op spellings diff/between/today are accepted.
type datetimeV3Tool struct{ inner *datetimeTool }

func (t *datetimeV3Tool) Spec() agent.ToolSpec { return t.inner.Spec() }

var (
	datetimeV3Ops = map[string]string{
		"now": "now", "today": "now", "current": "now",
		"compare": "compare", "diff": "compare", "difference": "compare", "between": "compare", "days_between": "compare",
		"add": "add", "plus": "add", "shift": "add",
	}
	weekdaysZH       = []string{"星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"}
	calendarDuration = regexp.MustCompile(`^([+-]?\d+)\s*(months?|mo|个月|月|years?|y|年)$`)
	dayDuration      = regexp.MustCompile(`(\d+(?:\.\d+)?)\s*(weeks?|days?|w|d|天|周|星期)`)
)

func (t *datetimeV3Tool) Execute(_ context.Context, raw json.RawMessage) (any, error) {
	var request struct {
		Op   string          `json:"op"`
		Args json.RawMessage `json:"args"`
	}
	if err := agent.DecodeToolArguments(raw, &request); err != nil {
		return nil, err
	}
	op, ok := datetimeV3Ops[strings.ToLower(strings.TrimSpace(request.Op))]
	if !ok {
		return nil, invalidArguments(`op must be now, compare, or add，例如 {"op":"compare","args":{"left":"2026-10-21","right":"2026-12-25"}}`)
	}
	location := t.inner.clock.Now().Location()
	switch op {
	case "now":
		// Any args are ignored; agent-tool-v2.0 rejected anything but {}.
		now := t.inner.clock.Now()
		return map[string]any{"now": now.Format(time.RFC3339), "timezone": now.Location().String(), "weekday": weekdaysZH[now.Weekday()]}, nil
	case "compare":
		var args struct {
			Left  string `json:"left"`
			Right string `json:"right"`
		}
		if err := agent.DecodeToolArguments(request.Args, &args); err != nil {
			return nil, err
		}
		left, leftOK := parseRowTime(strings.TrimSpace(args.Left), location)
		right, rightOK := parseRowTime(strings.TrimSpace(args.Right), location)
		if !leftOK || !rightOK {
			return nil, invalidArguments("left and right must be RFC3339 or YYYY-MM-DD times")
		}
		relation := left.Compare(right)
		days := right.Sub(left).Hours() / 24
		if left.Location() == right.Location() && isMidnight(left) && isMidnight(right) {
			// Calendar dates: count days, not 24-hour spans (a DST change
			// would otherwise give 64.96).
			days = float64(dateNumber(right) - dateNumber(left))
		}
		return map[string]any{
			"left": args.Left, "right": args.Right, "relation": relation,
			"days_between":  math.Abs(math.Round(days*100) / 100),
			"left_weekday":  weekdaysZH[left.Weekday()],
			"right_weekday": weekdaysZH[right.Weekday()],
		}, nil
	default:
		var args struct {
			Time     string `json:"time"`
			Duration string `json:"duration"`
		}
		if err := agent.DecodeToolArguments(request.Args, &args); err != nil {
			return nil, err
		}
		base, ok := parseRowTime(strings.TrimSpace(args.Time), location)
		if !ok {
			return nil, invalidArguments("time must be RFC3339 or YYYY-MM-DD")
		}
		result, err := addDuration(base, strings.TrimSpace(args.Duration))
		if err != nil {
			return nil, invalidArguments("duration: %v；写法如 72h、3d、2w、1 month、-30m", err)
		}
		return map[string]any{
			"time": base.Format(time.RFC3339), "duration": args.Duration,
			"result": result.Format(time.RFC3339), "weekday": weekdaysZH[result.Weekday()],
		}, nil
	}
}

// addDuration adds a Go duration, with days and weeks written as such, or a
// whole number of calendar months or years.
func addDuration(base time.Time, duration string) (time.Time, error) {
	if match := calendarDuration.FindStringSubmatch(strings.ToLower(duration)); match != nil {
		count, err := strconv.Atoi(match[1])
		if err != nil {
			return time.Time{}, err
		}
		if strings.HasPrefix(match[2], "y") || match[2] == "年" {
			return base.AddDate(count, 0, 0), nil
		}
		return base.AddDate(0, count, 0), nil
	}
	spelled := dayDuration.ReplaceAllStringFunc(strings.ToLower(duration), func(piece string) string {
		match := dayDuration.FindStringSubmatch(piece)
		count, _ := strconv.ParseFloat(match[1], 64)
		hours := count * 24
		if strings.HasPrefix(match[2], "w") || match[2] == "周" || match[2] == "星期" {
			hours *= 7
		}
		return strconv.FormatFloat(hours, 'f', -1, 64) + "h"
	})
	value, err := time.ParseDuration(strings.ReplaceAll(spelled, " ", ""))
	if err != nil {
		return time.Time{}, err
	}
	return base.Add(value), nil
}

func isMidnight(value time.Time) bool {
	return value.Hour() == 0 && value.Minute() == 0 && value.Second() == 0 && value.Nanosecond() == 0
}

// dateNumber is a day count for calendar arithmetic on a date's own fields.
func dateNumber(value time.Time) int {
	return int(time.Date(value.Year(), value.Month(), value.Day(), 0, 0, 0, 0, time.UTC).Unix() / 86400)
}
