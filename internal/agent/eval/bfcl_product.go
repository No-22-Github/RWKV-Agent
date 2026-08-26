package eval

import "fmt"

type bfclProductPair struct {
	ID       string
	Kind     string
	Path     string
	Label    string
	Query    string
	Value    string
	Contents string
}

type bfclProductMulti struct {
	BaseID   string
	Path     string
	Value    string
	Contents string
}

var bfclProductIrrelevancePrompts = []struct {
	ID     string
	Prompt string
}{
	{ID: "irrelevance_0", Prompt: "Calculate the area of a triangle given the base is 10 meters and height is 5 meters."},
	{ID: "irrelevance_1", Prompt: "Solve the quadratic equation with coefficients a = 1, b = 2, and c = 3."},
	{ID: "irrelevance_2", Prompt: "Solve for the roots of the equation 3x^2 - 2x - 5."},
	{ID: "irrelevance_3", Prompt: "What is the slope of the line which is perpendicular to the line with the equation y = 3x + 2?"},
	{ID: "irrelevance_4", Prompt: "What is the roots of linear equation bx + c = 0?"},
	{ID: "irrelevance_5", Prompt: "What is the perimeter of a rectangle with length 5 meters and width 4 meters?"},
	{ID: "irrelevance_6", Prompt: "What's the area of a rectangle that has width of 5m and length of 7m?"},
	{ID: "irrelevance_7", Prompt: "What is the area under the curve of the function f(x) = 3x^2 from x = 1 to x = 5?"},
	{ID: "irrelevance_8", Prompt: "Find the integral of x^3 from 1 to 5."},
	{ID: "irrelevance_9", Prompt: "Find the definite integral of f(x)=x^2 from x=1 to x=3."},
	{ID: "irrelevance_10", Prompt: "Compute the derivative of the function '2x' within the at 1."},
	{ID: "irrelevance_11", Prompt: "What is the closest integer to 30?"},
	{ID: "irrelevance_13", Prompt: "Calculate the prime factors of 100."},
	{ID: "irrelevance_14", Prompt: "What is the acceleration a ball will reach if it's thrown straight upwards with a velocity of 5 m/s?"},
	{ID: "irrelevance_16", Prompt: "How far will a car travel in time 't' when launched with velocity 'v' at an angle 'theta'?"},
	{ID: "irrelevance_18", Prompt: "How do I find the angle of the force for a given momentum?"},
	{ID: "irrelevance_19", Prompt: "Find the volume of a cone with base radius 3 cm and height 5 cm."},
	{ID: "irrelevance_21", Prompt: "What's the magnetic field at a point 4m away from a wire carrying a current of 2A?"},
	{ID: "irrelevance_22", Prompt: "What is the magnetic field at a point located at distance 'r' from a wire carrying current 'I'?"},
	{ID: "irrelevance_28", Prompt: "How many sides does a hexagon have?"},
}

var bfclProductPairs = []bfclProductPair{
	{ID: "simple_python_0", Kind: "read", Path: "config/app.env", Label: "TOKEN", Value: "CEDAR-5510", Contents: "TOKEN=CEDAR-5510\n"},
	{ID: "simple_python_1", Kind: "read", Path: "metrics/summary.txt", Label: "score", Value: "98", Contents: "score=98\n"},
	{ID: "simple_python_5", Kind: "read", Path: "docs/release.md", Label: "marker", Value: "RELEASE-2048", Contents: "marker=RELEASE-2048\n"},
	{ID: "simple_python_14", Kind: "read", Path: "data/owner.txt", Label: "owner", Value: "ORCHID-2048", Contents: "owner=ORCHID-2048\n"},
	{ID: "simple_python_35", Kind: "read", Path: "notes/version.txt", Label: "version", Value: "v4.2", Contents: "version=v4.2\n"},
	{ID: "simple_python_44", Kind: "search", Path: "logs/run.log", Query: "BUILD-STATUS", Value: "GREEN", Contents: "BUILD-STATUS=GREEN\n"},
	{ID: "simple_python_49", Kind: "search", Path: "docs/guide.md", Query: "ROUTE-SENTINEL-4821", Value: "docs/guide.md", Contents: "ROUTE-SENTINEL-4821\n"},
	{ID: "simple_python_51", Kind: "search", Path: "reports/audit.txt", Query: "AUDIT-OK", Value: "reports/audit.txt", Contents: "AUDIT-OK\n"},
	{ID: "simple_python_74", Kind: "search", Path: "src/main.go", Query: "func main", Value: "src/main.go", Contents: "package main\nfunc main() {}\n"},
	{ID: "simple_python_79", Kind: "search", Path: "config/flags.txt", Query: "FEATURE_X=on", Value: "config/flags.txt", Contents: "FEATURE_X=on\n"},
}

var bfclProductMultiTurns = []bfclProductMulti{
	{BaseID: "multi_turn_base_0", Path: "facts/report.txt", Value: "BUDGET-READY", Contents: "BUDGET-READY\n"},
	{BaseID: "multi_turn_base_1", Path: "facts/owner.txt", Value: "ALEX", Contents: "owner=ALEX\n"},
	{BaseID: "multi_turn_base_2", Path: "facts/release.txt", Value: "RELEASED", Contents: "status=RELEASED\n"},
	{BaseID: "multi_turn_base_3", Path: "facts/region.txt", Value: "APAC", Contents: "region=APAC\n"},
	{BaseID: "multi_turn_base_4", Path: "facts/checksum.txt", Value: "CHECKSUM-OK", Contents: "CHECKSUM-OK\n"},
	{BaseID: "multi_turn_base_5", Path: "facts/incident.txt", Value: "P2", Contents: "severity=P2\n"},
	{BaseID: "multi_turn_base_6", Path: "facts/deploy.txt", Value: "CANARY", Contents: "target=CANARY\n"},
	{BaseID: "multi_turn_base_7", Path: "facts/branch.txt", Value: "main", Contents: "branch=main\n"},
	{BaseID: "multi_turn_base_8", Path: "facts/queue.txt", Value: "EMPTY", Contents: "queue=EMPTY\n"},
	{BaseID: "multi_turn_base_9", Path: "facts/approval.txt", Value: "APPROVED", Contents: "approval=APPROVED\n"},
}

func BFCLProductCases() ([]Case, error) {
	cases := make([]Case, 0, 60)
	for _, prompt := range bfclProductIrrelevancePrompts {
		cases = append(cases, Case{
			ID:          "bfcl_" + prompt.ID,
			Description: "BFCL irrelevance case translated to the product workspace tool catalog.",
			Category:    "bfcl-irrelevance",
			Source:      "BFCL v4 irrelevance " + prompt.ID + " @ 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8",
			Difficulty:  "no-call",
			Turns: []Turn{{
				Prompt: prompt.Prompt,
				Expect: Expectation{
					Route:               "respond",
					Tools:               []string{},
					RequireActiveNoCall: true,
					ForbidRouteFallback: true,
				},
			}},
		})
	}
	for _, pair := range bfclProductPairs {
		cases = append(cases, bfclMissingCase(pair), bfclSuppliedCase(pair))
	}
	for _, multi := range bfclProductMultiTurns {
		cases = append(cases, bfclStateCase(multi), bfclRecoveryCase(multi))
	}
	if len(cases) != 60 {
		return nil, fmt.Errorf("BFCL product suite generated %d cases, want 60", len(cases))
	}
	if err := ValidateCases(cases); err != nil {
		return nil, err
	}
	return cases, nil
}

func bfclMissingCase(pair bfclProductPair) Case {
	toolHint := "路径"
	if pair.Kind == "search" {
		toolHint = "关键词"
	}
	return Case{
		ID:          "bfcl_missing_" + pair.ID,
		Description: "Ask for missing required information before selecting a product tool.",
		Category:    "bfcl-missing-required",
		Source:      "BFCL v4 paired required-information case " + pair.ID + " @ 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8",
		Difficulty:  "no-call",
		Files:       map[string]string{pair.Path: pair.Contents},
		Turns: []Turn{{
			Prompt: fmt.Sprintf("我需要你处理 %s，但没有提供具体%s。先向我询问%s，不要调用工具。", pair.Label, toolHint, toolHint),
			Expect: Expectation{
				Route:               "respond",
				Tools:               []string{},
				RequireActiveNoCall: true,
				ForbidRouteFallback: true,
				OutputContains:      []string{toolHint},
			},
		}},
	}
}

func bfclSuppliedCase(pair bfclProductPair) Case {
	tool := "read_file"
	arguments := map[string]any{"path": pair.Path}
	if pair.Kind == "search" {
		tool = "search_text"
		arguments = map[string]any{"query": pair.Query}
	}
	return Case{
		ID:          "bfcl_supplied_" + pair.ID,
		Description: "Use the supplied required information and execute the mapped product tool.",
		Category:    "bfcl-missing-required",
		Source:      "BFCL v4 paired supplied-information case " + pair.ID + " @ 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8",
		Difficulty:  "single-tool",
		Files:       map[string]string{pair.Path: pair.Contents},
		Turns: []Turn{{
			Prompt: fmt.Sprintf("请处理 %s：具体位置是 %s。", pair.Label, pair.Path),
			Expect: Expectation{
				Route:          "inspect",
				Tools:          []string{tool},
				Calls:          []ExpectedCall{{Name: tool, Arguments: arguments}},
				OutputContains: []string{pair.Value},
			},
		}},
	}
}

func bfclStateCase(multi bfclProductMulti) Case {
	return Case{
		ID:          "bfcl_state_" + multi.BaseID,
		Description: "Carry verified evidence into a follow-up without repeating the lookup.",
		Category:    "bfcl-multiturn",
		Source:      "BFCL v4 multi-turn state shape " + multi.BaseID + " @ 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8",
		Difficulty:  "two-turn",
		Files:       map[string]string{multi.Path: multi.Contents},
		Turns: []Turn{
			{
				Prompt: fmt.Sprintf("读取 %s，并报告其中的已验证值。", multi.Path),
				Expect: Expectation{
					Route:          "inspect",
					Tools:          []string{"read_file"},
					Calls:          []ExpectedCall{{Name: "read_file", Arguments: map[string]any{"path": multi.Path}}},
					OutputContains: []string{multi.Value},
				},
			},
			{
				Prompt: "不要调用工具，根据上一轮已读取的证据重复这个值。",
				Expect: Expectation{
					Route:               "respond",
					Tools:               []string{},
					RequireActiveNoCall: true,
					OutputContains:      []string{multi.Value},
				},
			},
		},
	}
}

func bfclRecoveryCase(multi bfclProductMulti) Case {
	missingPath := multi.Path[:len(multi.Path)-len(".txt")] + ".yaml"
	return Case{
		ID:          "bfcl_recovery_" + multi.BaseID,
		Description: "Recover from a failed lookup after the user supplies the corrected path.",
		Category:    "bfcl-multiturn",
		Source:      "BFCL v4 multi-turn recovery shape " + multi.BaseID + " @ 6ea57973c7a6097fd7c5915698c54c17c5b1b6c8",
		Difficulty:  "two-turn",
		Files:       map[string]string{multi.Path: multi.Contents},
		Turns: []Turn{
			{
				Prompt: fmt.Sprintf("读取 %s；如果不存在，明确告诉我没有找到。", missingPath),
				Expect: Expectation{
					Route:          "inspect",
					Tools:          []string{"read_file"},
					Calls:          []ExpectedCall{{Name: "read_file", Arguments: map[string]any{"path": missingPath}}},
					OutputContains: []string{"不存在"},
				},
			},
			{
				Prompt: fmt.Sprintf("实际文件是 %s，请读取并报告其中的值。", multi.Path),
				Expect: Expectation{
					Route:          "inspect",
					Tools:          []string{"read_file"},
					Calls:          []ExpectedCall{{Name: "read_file", Arguments: map[string]any{"path": multi.Path}}},
					OutputContains: []string{multi.Value},
				},
			},
		},
	}
}
