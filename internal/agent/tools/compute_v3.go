package tools

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"go/parser"
	"math"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/agent"
)

// work-v3 calculator and data_query (docs/design/work-v3-tools.md §2.9–§2.10).
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
	expression := strings.TrimSpace(args.Expression)
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
}

// Execute relaxes the aggregate argument combinations that made a third of
// work-v2's data_query calls fail on the 10-17 exam, then runs work-v2's query.
func (t *dataQueryV3Tool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	var args map[string]any
	if err := json.Unmarshal(raw, &args); err != nil {
		return t.inner.Execute(ctx, raw)
	}
	text := func(key string) string {
		value, _ := args[key].(string)
		return strings.TrimSpace(value)
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
	if ignored == "" {
		return t.inner.Execute(ctx, raw)
	}
	rewritten, err := json.Marshal(args)
	if err != nil {
		return nil, err
	}
	value, err := t.inner.Execute(ctx, rewritten)
	if err != nil {
		return nil, err
	}
	result, ok := value.(dataQueryResult)
	if !ok {
		return nil, errors.New("data_query: unexpected result type")
	}
	return dataQueryV3Result{dataQueryResult: result, Ignored: ignored}, nil
}

// LocalToolsV3 is work-v3's always-present compute group: calculator,
// data_query and datetime, in work-v2's order.
func LocalToolsV3(options Options) ([]agent.Tool, error) {
	resolver, err := agent.NewWorkspaceResolverWithFS(options.Workspace, options.Filesystem)
	if err != nil {
		return nil, err
	}
	if options.Clock == nil {
		options.Clock = systemClock{}
	}
	return []agent.Tool{
		calculatorV3Tool{},
		&dataQueryV3Tool{inner: &dataQueryTool{workspace: resolver}},
		&datetimeTool{clock: options.Clock},
	}, nil
}
