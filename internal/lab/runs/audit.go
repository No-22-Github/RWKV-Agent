package runs

import (
	"fmt"
	"regexp"
	"sort"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// Mechanical failure observations. The flags overlap on purpose: they are
// observations, not causal buckets, and an empty output is not proof that
// reasoning was absent.

var toolResponseRe = regexp.MustCompile(`(?s)<tool_response>(.*?)</tool_response>`)

// AuditArgs are the `run audit` flags.
type AuditArgs struct {
	Run string
}

// RunAudit is the `run audit` command.
func RunAudit(args AuditArgs) int {
	report, err := Audit(args.Run)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	data, err := lab.EncodeJSON(report, 2)
	if err != nil {
		fmt.Fprintln(stderr, err)
		return 2
	}
	fmt.Println(string(data))
	return 0
}

// Audit is failure_audit.audit.
func Audit(runDir string) (map[string]any, error) {
	summary, err := LoadJSONFile(runDir+"/summary.json", true)
	if err != nil {
		return nil, err
	}
	rows := []any{}
	totals := map[string]int{}

	for _, caseObj := range mapSlice(summary["cases"]) {
		flags := map[string]bool{}
		var traces []any
		for _, turn := range mapSlice(caseObj["turns"]) {
			result := mapOf(turn, "result")
			steps := mapSlice(result["steps"])

			if reason := stringOf(result, "forced_answer_reason"); reason != "" {
				flags[reason] = true
			}
			if stringOf(result, "output") == "" {
				flags["empty_output"] = true
			}
			for _, f := range stringList(turn["failures"]) {
				if InfrastructureFailure(f) {
					flags["infrastructure_failure"] = true
				}
			}
			for _, st := range steps {
				if stringOf(st, "stage") == "answer" && stringOf(st, "action_type") == "tool" {
					flags["answer_stage_tool"] = true
				}
				tool := stringOf(st, "tool")
				if (tool == "read_file" || tool == "read_lines") && toolResultOK(st) {
					flags["successful_file_read"] = true
				}
			}

			for i := 0; i+1 < len(steps); i++ {
				a, b := steps[i], steps[i+1]
				receipt, hasReceipt := a["tool_result"]
				if !hasReceipt || receipt == nil {
					continue
				}
				prompt := stringOf(mapOf(b, "request"), "prompt")
				var payloads []any
				for _, match := range toolResponseRe.FindAllStringSubmatch(prompt, -1) {
					if obj, err := lab.DecodeJSONBytes([]byte(match[1])); err == nil {
						payloads = append(payloads, obj)
					}
				}
				totals["receipts_checked"]++
				if containsDeep(payloads, receipt) {
					totals["receipts_present_in_next_prompt"]++
				}
			}

			actions := make([]any, 0, len(steps))
			for _, st := range steps {
				actions = append(actions, map[string]any{
					"step":           st["number"],
					"stage":          st["stage"],
					"action":         st["action_type"],
					"tool":           st["tool"],
					"arguments":      st["tool_arguments"],
					"tool_ok":        toolResultField(st, "ok"),
					"tool_error":     toolResultField(st, "error"),
					"protocol_error": st["protocol_error"],
				})
			}
			turnFailures := turn["failures"]
			if turnFailures == nil {
				turnFailures = []any{}
			}
			traces = append(traces, map[string]any{
				"output":   result["output"],
				"failures": turnFailures,
				"actions":  actions,
			})
		}
		caseFailures := caseObj["failures"]
		if caseFailures == nil {
			caseFailures = []any{}
		}
		sortedFlags := make([]string, 0, len(flags))
		for flag := range flags {
			sortedFlags = append(sortedFlags, flag)
		}
		sort.Strings(sortedFlags)
		for _, flag := range sortedFlags {
			totals[flag]++
		}
		totals["cases"]++
		if passed, _ := caseObj["passed"].(bool); passed {
			totals["passed"]++
		}
		rows = append(rows, map[string]any{
			"id":            caseObj["id"],
			"passed":        caseObj["passed"],
			"case_failures": caseFailures,
			"case_error":    caseObj["error"],
			"flags":         toAnySlice(sortedFlags),
			"turns":         traces,
		})
	}

	totalsOut := make(map[string]any, len(totals))
	for k, v := range totals {
		totalsOut[k] = v
	}
	return map[string]any{
		"run":     runDir,
		"warning": "Flags overlap. Empty output is not proof that reasoning was absent.",
		"totals":  totalsOut,
		"cases":   rows,
	}, nil
}

func toolResultOK(step map[string]any) bool {
	ok, _ := toolResultField(step, "ok").(bool)
	return ok
}

func toolResultField(step map[string]any, key string) any {
	result, _ := step["tool_result"].(map[string]any)
	if result == nil {
		return nil
	}
	return result[key]
}

// containsDeep is Python's `receipt in payloads`, which compares dicts by
// value rather than identity.
func containsDeep(payloads []any, receipt any) bool {
	want := canonicalJSON(receipt)
	for _, payload := range payloads {
		if canonicalJSON(payload) == want {
			return true
		}
	}
	return false
}

var _ = strings.TrimSpace
