package eval

// work-v3 drops read_lines: read_file takes the same start_line/end_line
// range (docs/design/work-v3-tools.md §2.1, §2.13). Case files keep naming
// read_lines so work-v2 runs reproduce history; a work-v3 run reads every
// read_lines reference as read_file.
var workV3ToolRenames = map[string]string{"read_lines": "read_file"}

// adaptCasesToCatalog returns the cases as the named catalog sees them. Only
// work-v3 rewrites anything; the input slice is never modified.
func adaptCasesToCatalog(cases []Case, catalog string) []Case {
	if catalog != WorkV3ToolCatalogName {
		return cases
	}
	out := make([]Case, len(cases))
	for index, testCase := range cases {
		out[index] = adaptCaseV3(testCase)
	}
	return out
}

func adaptCaseV3(c Case) Case {
	c.OfferedTools = renameTools(c.OfferedTools)
	if c.ToolPolicy != nil {
		policy := *c.ToolPolicy
		policy.MustOffer = renameTools(policy.MustOffer)
		policy.NeverOffer = renameTools(policy.NeverOffer)
		c.ToolPolicy = &policy
	}
	if c.Expect != nil {
		expect := *c.Expect
		if expect.MaxCalls != nil {
			calls := make(map[string]int, len(expect.MaxCalls))
			for name, budget := range expect.MaxCalls {
				calls[renameTool(name)] += budget
			}
			expect.MaxCalls = calls
		}
		c.Expect = &expect
	}
	turns := make([]Turn, len(c.Turns))
	for index, turn := range c.Turns {
		expect := turn.Expect
		expect.Tools = renameSequence(expect.Tools)
		expect.RequiredTools = renameTools(expect.RequiredTools)
		expect.ForbiddenTools = renameTools(expect.ForbiddenTools)
		expect.Calls = renameCalls(expect.Calls)
		expect.RequiredCalls = renameCalls(expect.RequiredCalls)
		turn.Expect = expect
		turns[index] = turn
	}
	c.Turns = turns
	return c
}

func renameTool(name string) string {
	if renamed, ok := workV3ToolRenames[name]; ok {
		return renamed
	}
	return name
}

// renameTools renames a tool set (offered, required, forbidden): nil stays
// nil, and a name the rename makes twice is kept once.
func renameTools(names []string) []string {
	if names == nil {
		return nil
	}
	out := make([]string, 0, len(names))
	seen := make(map[string]bool, len(names))
	for _, name := range names {
		name = renameTool(name)
		if !seen[name] {
			seen[name] = true
			out = append(out, name)
		}
	}
	return out
}

// renameSequence renames an ordered call list (Expectation.Tools) without
// dropping repeats.
func renameSequence(names []string) []string {
	if names == nil {
		return nil
	}
	out := make([]string, len(names))
	for index, name := range names {
		out[index] = renameTool(name)
	}
	return out
}

func renameCalls(calls []ExpectedCall) []ExpectedCall {
	if calls == nil {
		return nil
	}
	out := make([]ExpectedCall, len(calls))
	for index, call := range calls {
		call.Name = renameTool(call.Name)
		out[index] = call
	}
	return out
}
