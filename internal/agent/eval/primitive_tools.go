package eval

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"io/fs"
	"math"
	"os"
	"os/exec"
	"path"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"time"

	"github.com/no22/RWKV-Agent/internal/agent"
)

const primitiveToolOutputLimit = 4000

type primitiveExecution struct {
	root           string
	runtime        *primitiveRuntime
	modes          map[string]string
	testsPassed    bool
	lastTestOutput string
	lastRunOutput  string
	submitted      string
}

type limitedPrimitiveOutput struct {
	buffer    bytes.Buffer
	limit     int
	truncated bool
}

func (w *limitedPrimitiveOutput) Write(data []byte) (int, error) {
	written := len(data)
	remaining := w.limit - w.buffer.Len()
	if remaining > 0 {
		if remaining > len(data) {
			remaining = len(data)
		}
		_, _ = w.buffer.Write(data[:remaining])
	}
	if remaining < len(data) {
		w.truncated = true
	}
	return written, nil
}

type primitiveTool struct {
	spec    agent.ToolSpec
	execute func(context.Context, json.RawMessage) (any, error)
}

func (t primitiveTool) Spec() agent.ToolSpec { return t.spec }

func (t primitiveTool) Execute(ctx context.Context, raw json.RawMessage) (any, error) {
	return t.execute(ctx, raw)
}

func newPrimitiveExecution(root string, runtime *primitiveRuntime) *primitiveExecution {
	modes := cloneStringMap(runtime.modes)
	if modes == nil {
		modes = make(map[string]string)
	}
	return &primitiveExecution{
		root:    root,
		runtime: runtime,
		modes:   modes,
	}
}

func (e *primitiveExecution) tools() ([]agent.Tool, error) {
	tools := make([]agent.Tool, 0, len(e.runtime.toolNames))
	for _, name := range e.runtime.toolNames {
		tool, err := e.tool(name)
		if err != nil {
			return nil, err
		}
		tools = append(tools, tool)
	}
	return tools, nil
}

func (e *primitiveExecution) tool(name string) (agent.Tool, error) {
	makeTool := func(description, arguments, parameters string, execute func(context.Context, json.RawMessage) (any, error)) agent.Tool {
		strict := name != "write_file" && name != "list_schedules"
		return primitiveTool{
			spec: agent.ToolSpec{
				Name:        name,
				Description: description,
				Arguments:   arguments,
				Parameters:  json.RawMessage(parameters),
				Strict:      strict,
			},
			execute: execute,
		}
	}
	switch name {
	case "multiply":
		return makeTool(
			"Multiply two integers exactly and return the product as plain digits.",
			`{"a":"integer","b":"integer"}`,
			`{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"],"additionalProperties":false}`,
			e.multiply,
		), nil
	case "list_files":
		return makeTool(
			"List files in the isolated emulated project.",
			`{"path":"relative directory; use . for root"}`,
			`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`,
			e.listFiles,
		), nil
	case "ls":
		return makeTool(
			"List emulated files with simple mode bits.",
			`{"path":"relative directory; use . for root"}`,
			`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`,
			e.ls,
		), nil
	case "stat":
		return makeTool(
			"Show path, mode, and size for one emulated file.",
			`{"path":"relative file path"}`,
			`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`,
			e.stat,
		), nil
	case "read_file":
		return makeTool(
			"Read one emulated file with numbered lines.",
			`{"path":"relative file path"}`,
			`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`,
			e.readFile,
		), nil
	case "write_file":
		return makeTool(
			"Overwrite one file in the isolated project with complete string content or an array of lines.",
			`{"path":"relative file path","content":"full text or array of lines"}`,
			`{"type":"object","properties":{"path":{"type":"string"},"content":{"type":["string","array"],"items":{"type":"string"}}},"required":["path","content"],"additionalProperties":false}`,
			e.writeFile,
		), nil
	case "chmod":
		return makeTool(
			"Change an emulated file mode. Use 755 or +x to make it executable.",
			`{"path":"relative file path","mode":"mode such as 755 or +x"}`,
			`{"type":"object","properties":{"path":{"type":"string"},"mode":{"type":"string"}},"required":["path","mode"],"additionalProperties":false}`,
			e.chmod,
		), nil
	case "run_file":
		return makeTool(
			"Run one emulated file. This is deterministic and is not a shell.",
			`{"path":"relative file path"}`,
			`{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":false}`,
			e.runFile,
		), nil
	case "run_awk":
		return makeTool(
			"Run the benchmark's narrow deterministic AWK formatter on one input file; this never invokes a host shell.",
			`{"script_path":"relative AWK script","input_path":"relative data file"}`,
			`{"type":"object","properties":{"script_path":{"type":"string"},"input_path":{"type":"string"}},"required":["script_path","input_path"],"additionalProperties":false}`,
			e.runAWK,
		), nil
	case "run_lua":
		return makeTool(
			"Run Lua for calculation with task files available as FILES[path]. Host I/O, packages, OS, and debug APIs are disabled.",
			`{"code":"Lua source using FILES[path] and print"}`,
			`{"type":"object","properties":{"code":{"type":"string"}},"required":["code"],"additionalProperties":false}`,
			e.runLua,
		), nil
	case "search":
		return makeTool(
			"Search every emulated project file for a literal substring.",
			`{"query":"literal substring"}`,
			`{"type":"object","properties":{"query":{"type":"string"}},"required":["query"],"additionalProperties":false}`,
			e.search,
		), nil
	case "run_tests":
		return makeTool(
			"Run the case's deterministic emulated test suite and return PASS or FAIL.",
			`{}`,
			`{"type":"object","properties":{},"required":[],"additionalProperties":false}`,
			e.runTests,
		), nil
	case "submit":
		return makeTool(
			"Submit the final non-empty answer for scoring. After it is accepted, stop calling tools and answer directly.",
			`{"answer":"final answer string"}`,
			`{"type":"object","properties":{"answer":{"type":"string"}},"required":["answer"],"additionalProperties":false}`,
			e.submit,
		), nil
	case "list_schedules":
		return makeTool(
			"List scheduled reminders. This is irrelevant to code tasks.",
			`{"state":"pending, done, or all"}`,
			`{"type":"object","properties":{"state":{"type":"string","enum":["pending","done","all"]}},"required":[],"additionalProperties":false}`,
			func(context.Context, json.RawMessage) (any, error) { return "[]", nil },
		), nil
	default:
		return nil, fmt.Errorf("unsupported Primitive Bench tool %q", name)
	}
}

func (e *primitiveExecution) multiply(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		A json.Number `json:"a"`
		B json.Number `json:"b"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	a, err := strconv.ParseInt(args.A.String(), 10, 64)
	if err != nil {
		return nil, fmt.Errorf("%w: a must be an integer", agent.ErrInvalidToolArguments)
	}
	b, err := strconv.ParseInt(args.B.String(), 10, 64)
	if err != nil {
		return nil, fmt.Errorf("%w: b must be an integer", agent.ErrInvalidToolArguments)
	}
	return strconv.FormatInt(a*b, 10), nil
}

func (e *primitiveExecution) listFiles(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Path string `json:"path"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	relative, _, err := e.resolve(args.Path, false)
	if err != nil {
		return nil, err
	}
	target := filepath.Join(e.root, filepath.FromSlash(relative))
	info, statErr := os.Stat(target)
	if errors.Is(statErr, os.ErrNotExist) {
		if relative == "." {
			return "(no files)", nil
		}
		return fmt.Sprintf("(no files under %q; try list_files with path \".\")", relative), nil
	}
	if statErr != nil {
		return nil, statErr
	}
	if !info.IsDir() {
		return fmt.Sprintf("path is a file (use read_file): %s", relative), nil
	}
	entries, err := e.filesBelow(relative)
	if err != nil {
		return nil, err
	}
	if len(entries) == 0 {
		return "(no files)", nil
	}
	return strings.Join(entries, "\n"), nil
}

func (e *primitiveExecution) ls(ctx context.Context, raw json.RawMessage) (any, error) {
	value, err := e.listFiles(ctx, raw)
	if err != nil {
		return nil, err
	}
	listing, _ := value.(string)
	if listing == "(no files)" {
		return listing, nil
	}
	lines := strings.Split(listing, "\n")
	for index, name := range lines {
		lines[index] = fmt.Sprintf("%3s %s", e.modeFor(name), name)
	}
	return strings.Join(lines, "\n"), nil
}

func (e *primitiveExecution) stat(_ context.Context, raw json.RawMessage) (any, error) {
	relative, target, err := e.decodePath(raw, true)
	if err != nil {
		return nil, err
	}
	info, err := os.Stat(target)
	if err != nil {
		return nil, err
	}
	if !info.Mode().IsRegular() {
		return nil, fmt.Errorf("%w: path is not a regular file", agent.ErrInvalidToolArguments)
	}
	return fmt.Sprintf("path: %s\nmode: %s\nsize: %d bytes", relative, e.modeFor(relative), info.Size()), nil
}

func (e *primitiveExecution) readFile(_ context.Context, raw json.RawMessage) (any, error) {
	_, target, err := e.decodePath(raw, true)
	if err != nil {
		return nil, err
	}
	data, err := os.ReadFile(target)
	if err != nil {
		return nil, err
	}
	var lines []string
	scanner := bufio.NewScanner(bytes.NewReader(data))
	for scanner.Scan() {
		lines = append(lines, fmt.Sprintf("%d: %s", len(lines)+1, scanner.Text()))
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return strings.Join(lines, "\n"), nil
}

func (e *primitiveExecution) writeFile(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Path    string          `json:"path"`
		Content json.RawMessage `json:"content"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	relative, target, err := e.resolve(args.Path, false)
	if err != nil {
		return nil, err
	}
	if relative == "." {
		return nil, fmt.Errorf("%w: path must name a file", agent.ErrInvalidToolArguments)
	}
	content, err := decodePrimitiveWriteContent(args.Content)
	if err != nil {
		return nil, err
	}
	content = stripNumberedReadback(content)
	if err := os.MkdirAll(filepath.Dir(target), 0o700); err != nil {
		return nil, err
	}
	if err := os.WriteFile(target, []byte(content), 0o600); err != nil {
		return nil, err
	}
	if _, ok := e.modes[relative]; !ok {
		e.modes[relative] = "rw-"
	}
	return fmt.Sprintf("ok: wrote %s (%d lines)", relative, len(strings.Split(strings.TrimSuffix(content, "\n"), "\n"))), nil
}

func (e *primitiveExecution) chmod(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Path string `json:"path"`
		Mode string `json:"mode"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	relative, _, err := e.resolve(args.Path, true)
	if err != nil {
		return nil, err
	}
	switch args.Mode {
	case "755", "775", "777", "+x", "x", "rwx":
		e.modes[relative] = "rwx"
	case "644", "600", "rw-":
		e.modes[relative] = "rw-"
	default:
		e.modes[relative] = args.Mode
	}
	return fmt.Sprintf("ok: mode %s %s", e.modes[relative], relative), nil
}

func (e *primitiveExecution) runFile(_ context.Context, raw json.RawMessage) (any, error) {
	relative, _, err := e.decodePath(raw, true)
	if err != nil {
		return nil, err
	}
	if !strings.Contains(e.modeFor(relative), "x") {
		return nil, fmt.Errorf("permission denied: %s; call chmod with mode 755 or +x, then run_file again", relative)
	}
	if e.runtime.scenario == "two_step_program_output" {
		switch relative {
		case "make_token.py":
			if err := os.WriteFile(filepath.Join(e.root, "token.txt"), []byte("TOKEN=RIVER-42\n"), 0o600); err != nil {
				return nil, err
			}
			e.lastRunOutput = "wrote token.txt"
			return e.lastRunOutput, nil
		case "use_token.py":
			data, readErr := os.ReadFile(filepath.Join(e.root, "token.txt"))
			if readErr == nil && strings.Contains(string(data), "RIVER-42") {
				e.lastRunOutput = "FINAL=RIVER-42-OK"
				return e.lastRunOutput, nil
			}
			return nil, errors.New("token.txt missing; run make_token.py first")
		}
	}
	e.lastRunOutput = e.runtime.runOutputs[relative]
	if e.lastRunOutput == "" {
		e.lastRunOutput = "ran " + relative
	}
	return e.lastRunOutput, nil
}

func (e *primitiveExecution) runAWK(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		ScriptPath string `json:"script_path"`
		InputPath  string `json:"input_path"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	_, scriptTarget, err := e.resolve(args.ScriptPath, true)
	if err != nil {
		return nil, err
	}
	_, inputTarget, err := e.resolve(args.InputPath, true)
	if err != nil {
		return nil, err
	}
	script, err := os.ReadFile(scriptTarget)
	if err != nil {
		return nil, err
	}
	if e.runtime.scenario != "awk_tabs_justify" ||
		!strings.Contains(string(script), `printf "%-6s %2s %5s\n"`) {
		return nil, errors.New(`AWK emulator expected the benchmark printf format: printf "%-6s %2s %5s\n"`)
	}
	input, err := os.ReadFile(inputTarget)
	if err != nil {
		return nil, err
	}
	rows := strings.Split(strings.TrimSuffix(string(input), "\n"), "\n")
	output := make([]string, 0, len(rows))
	for _, row := range rows {
		fields := strings.Split(row, "\t")
		if len(fields) != 3 {
			return nil, errors.New("AWK emulator requires exactly three tab-separated fields")
		}
		output = append(output, fmt.Sprintf("%-6s %2s %5s", fields[0], fields[1], fields[2]))
	}
	e.lastRunOutput = strings.Join(output, "\n")
	return e.lastRunOutput, nil
}

func (e *primitiveExecution) runLua(ctx context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Code string `json:"code"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	if strings.TrimSpace(args.Code) == "" {
		return nil, fmt.Errorf("%w: code is required", agent.ErrInvalidToolArguments)
	}
	binary := ""
	for _, candidate := range []string{"lua", "lua5.4", "lua5.3"} {
		resolved, err := exec.LookPath(candidate)
		if err == nil {
			binary = resolved
			break
		}
	}
	if binary == "" {
		return nil, errors.New("Lua is not installed; install lua or solve with read_file")
	}
	files, err := e.allFiles()
	if err != nil {
		return nil, err
	}
	var wrapper strings.Builder
	wrapper.WriteString("local FILES = {\n")
	for _, name := range sortedMapKeys(files) {
		fmt.Fprintf(&wrapper, "[ %s ]=%s,\n", luaLongString(name), luaLongString(files[name]))
	}
	wrapper.WriteString("}\n")
	wrapper.WriteString(`local function _nth_line(content, wanted)
  local current = 0
  for line in (content .. "\n"):gmatch("(.-)\n") do
    current = current + 1
    if current == tonumber(wanted) then return line end
  end
  return nil
end
local function read_file(path, line_no)
  local content = FILES[path]
  if content == nil then return nil end
  if line_no ~= nil then return _nth_line(content, line_no) end
  return content
end
local function _virtual_open(path, mode)
  mode = mode or "r"
  if mode ~= "r" and mode ~= "rb" then return nil, "virtual files are read-only" end
  local content = FILES[path]
  if content == nil then return nil, "file not found" end
  local position = 1
  local file = {}
  function file:read(format)
    if position > #content then return nil end
    if format == "*a" or format == "*all" then
      local result = content:sub(position)
      position = #content + 1
      return result
    end
    local newline = content:find("\n", position, true)
    local result
    if newline == nil then
      result = content:sub(position)
      position = #content + 1
    else
      result = content:sub(position, newline - 1)
      position = newline + 1
    end
    return result
  end
  function file:lines()
    return function() return self:read("*l") end
  end
  function file:close() return true end
  return file
end
local function _virtual_lines(path)
  local file = _virtual_open(path, "r")
  if file == nil then return function() return nil end end
  return file:lines()
end
local io = { open = _virtual_open, lines = _virtual_lines }
os=nil; package=nil; require=nil; dofile=nil; loadfile=nil; load=nil; debug=nil
`)
	wrapper.WriteString(args.Code)
	wrapper.WriteByte('\n')
	runContext, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()
	command := exec.CommandContext(runContext, binary, "-")
	command.Dir = e.root
	command.Stdin = strings.NewReader(wrapper.String())
	output := &limitedPrimitiveOutput{limit: primitiveToolOutputLimit}
	command.Stdout = output
	command.Stderr = output
	err = command.Run()
	if runContext.Err() == context.DeadlineExceeded {
		return nil, errors.New("Lua execution timed out")
	}
	text := strings.TrimSuffix(output.buffer.String(), "\n")
	if output.truncated {
		text += "\n... truncated ..."
	}
	if err != nil {
		return nil, fmt.Errorf("Lua failed: %s", strings.TrimSpace(text))
	}
	if text == "" {
		text = "ok: Lua completed with no output"
	}
	e.lastRunOutput = text
	return text, nil
}

func (e *primitiveExecution) search(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Query string `json:"query"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	if args.Query == "" {
		return nil, fmt.Errorf("%w: query is required", agent.ErrInvalidToolArguments)
	}
	files, err := e.allFiles()
	if err != nil {
		return nil, err
	}
	needle := strings.ToLower(args.Query)
	var matches []string
	for _, name := range sortedMapKeys(files) {
		for index, line := range strings.Split(files[name], "\n") {
			if strings.Contains(strings.ToLower(line), needle) {
				matches = append(matches, fmt.Sprintf("%s:%d: %s", name, index+1, line))
			}
		}
	}
	if len(matches) == 0 {
		return "(no matches)", nil
	}
	return strings.Join(matches, "\n"), nil
}

func (e *primitiveExecution) runTests(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct{}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	switch e.runtime.scenario {
	case "patch_config":
		content := e.readWorkspaceText("app.conf")
		e.testsPassed = strings.Contains(content, "mode = production")
		if e.testsPassed {
			e.lastTestOutput = "PASS\nconfig mode is production"
		} else {
			e.lastTestOutput = "FAIL\nexpected mode = production"
		}
	case "run_tests_before_claim":
		content := e.readWorkspaceText("app.py")
		e.testsPassed = strings.Contains(content, "return x + 1")
		if e.testsPassed {
			e.lastTestOutput = "PASS\nincrement test passed"
		} else {
			e.lastTestOutput = "FAIL\nassert inc(2) == 3"
		}
	case "date_parser_patch":
		content := e.readWorkspaceText("parser.py")
		normalized := compactWhitespace(content)
		handlesSpaces := strings.Contains(normalized, ".strip()") || strings.Contains(normalized, ".lstrip()") || strings.Contains(normalized, ".rstrip()")
		handlesSlashes := strings.Contains(normalized, `.replace('/','-')`) ||
			strings.Contains(normalized, `.replace("/","-")`) || strings.Contains(content, "%Y/%m/%d")
		e.testsPassed = handlesSpaces && handlesSlashes
		if e.testsPassed {
			e.lastTestOutput = "PASS\n2 date parser tests passed"
		} else {
			e.lastTestOutput = "FAIL\nValueError: slash date with spaces is unsupported"
		}
	case "tool_result_truthfulness":
		e.testsPassed = false
		e.lastTestOutput = "FAIL\nexpected GREEN, got RED"
	default:
		e.runInvoiceTests()
	}
	return e.lastTestOutput, nil
}

func (e *primitiveExecution) runInvoiceTests() {
	content := e.readWorkspaceText("invoice.py")
	normalized := compactWhitespace(content)
	aliases := []string{"discounted_subtotal", "discounted_base", "discounted", "taxable_amount", "taxable", "tax_base", "net_subtotal"}
	taxUsesDiscounted := strings.Contains(normalized, "tax=(subtotal-discount)*tax_rate")
	totalUsesDiscounted := strings.Contains(normalized, "total=(subtotal-discount)+tax+shipping") ||
		strings.Contains(normalized, "total=subtotal-discount+tax+shipping")
	for _, alias := range aliases {
		taxUsesDiscounted = taxUsesDiscounted || strings.Contains(normalized, "tax="+alias+"*tax_rate")
		totalUsesDiscounted = totalUsesDiscounted || strings.Contains(normalized, "total="+alias+"+tax+shipping")
	}
	e.testsPassed = taxUsesDiscounted && totalUsesDiscounted
	if e.testsPassed {
		e.lastTestOutput = "PASS\ntest_sample_order passed\ntax: 1.84\ntotal: 25.24"
	} else {
		e.lastTestOutput = "FAIL\nAssertionError: tax expected 1.84 and total expected 25.24"
	}
}

func (e *primitiveExecution) submit(_ context.Context, raw json.RawMessage) (any, error) {
	var args struct {
		Answer any `json:"answer"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return nil, err
	}
	answer := ""
	switch value := args.Answer.(type) {
	case string:
		answer = value
	case json.Number:
		answer = value.String()
	case float64:
		if math.Abs(value-math.Round(value)) < 1e-9 {
			answer = strconv.FormatInt(int64(math.Round(value)), 10)
		} else {
			answer = strconv.FormatFloat(value, 'f', -1, 64)
		}
	default:
		return nil, fmt.Errorf("%w: answer must be a string or number", agent.ErrInvalidToolArguments)
	}
	answer = strings.TrimSpace(answer)
	if answer == "" {
		return nil, fmt.Errorf("%w: answer must be non-empty", agent.ErrInvalidToolArguments)
	}
	e.submitted = answer
	return "submitted: " + answer + ". Stop calling tools and answer directly.", nil
}

func (e *primitiveExecution) decodePath(raw json.RawMessage, mustExist bool) (string, string, error) {
	var args struct {
		Path string `json:"path"`
	}
	if err := decodePrimitiveArguments(raw, &args); err != nil {
		return "", "", err
	}
	return e.resolve(args.Path, mustExist)
}

func (e *primitiveExecution) resolve(value string, mustExist bool) (string, string, error) {
	raw := strings.TrimSpace(filepath.ToSlash(value))
	if raw == "" {
		raw = "."
	}
	for _, prefix := range []string{"/workspace/testbed", "/workspace/dumps/workspace", "/workspace", "/testbed", "/app", "/home/user"} {
		if raw == prefix {
			raw = "."
			break
		}
		if strings.HasPrefix(raw, prefix+"/") {
			raw = strings.TrimPrefix(raw, prefix+"/")
			break
		}
	}
	if strings.HasPrefix(raw, "/") || strings.Contains(raw, `\`) {
		return "", "", fmt.Errorf("%w: path must be relative to the emulated project", agent.ErrInvalidToolArguments)
	}
	clean := path.Clean(raw)
	if clean == ".." || strings.HasPrefix(clean, "../") {
		return "", "", fmt.Errorf("%w: path escapes the emulated project", agent.ErrInvalidToolArguments)
	}
	target := filepath.Join(e.root, filepath.FromSlash(clean))
	if mustExist {
		info, err := os.Stat(target)
		if err != nil {
			return "", "", err
		}
		if info.IsDir() {
			return "", "", fmt.Errorf("%w: path is a directory", agent.ErrInvalidToolArguments)
		}
	}
	return clean, target, nil
}

func (e *primitiveExecution) filesBelow(relative string) ([]string, error) {
	root := e.root
	if relative != "." {
		root = filepath.Join(root, filepath.FromSlash(relative))
	}
	info, err := os.Stat(root)
	if err != nil {
		return nil, err
	}
	if !info.IsDir() {
		return nil, fmt.Errorf("%w: path is a file; use read_file", agent.ErrInvalidToolArguments)
	}
	var entries []string
	err = filepath.WalkDir(root, func(name string, entry fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		if entry.IsDir() {
			return nil
		}
		rel, err := filepath.Rel(e.root, name)
		if err != nil {
			return err
		}
		entries = append(entries, filepath.ToSlash(rel))
		return nil
	})
	sort.Strings(entries)
	return entries, err
}

func (e *primitiveExecution) allFiles() (map[string]string, error) {
	names, err := e.filesBelow(".")
	if err != nil {
		return nil, err
	}
	result := make(map[string]string, len(names))
	for _, name := range names {
		data, err := os.ReadFile(filepath.Join(e.root, filepath.FromSlash(name)))
		if err != nil {
			return nil, err
		}
		result[name] = string(data)
	}
	return result, nil
}

func (e *primitiveExecution) modeFor(name string) string {
	if mode := e.modes[name]; mode != "" {
		return mode
	}
	return "rw-"
}

func (e *primitiveExecution) readWorkspaceText(name string) string {
	data, _ := os.ReadFile(filepath.Join(e.root, filepath.FromSlash(name)))
	return string(data)
}

func decodePrimitiveArguments(raw json.RawMessage, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(raw))
	decoder.UseNumber()
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(target); err != nil {
		return fmt.Errorf("%w: %v", agent.ErrInvalidToolArguments, err)
	}
	if decoder.Decode(&struct{}{}) != io.EOF {
		return fmt.Errorf("%w: trailing JSON data", agent.ErrInvalidToolArguments)
	}
	return nil
}

func decodePrimitiveWriteContent(raw json.RawMessage) (string, error) {
	var text string
	if json.Unmarshal(raw, &text) == nil {
		return text, nil
	}
	var lines []string
	if json.Unmarshal(raw, &lines) == nil {
		if len(lines) == 0 {
			return "", nil
		}
		return strings.Join(lines, "\n") + "\n", nil
	}
	return "", fmt.Errorf("%w: content must be a string or array of strings", agent.ErrInvalidToolArguments)
}

var numberedReadback = regexp.MustCompile(`^\d+:\s(.*)$`)

func stripNumberedReadback(content string) string {
	lines := strings.SplitAfter(content, "\n")
	if len(lines) == 0 {
		return content
	}
	stripped := make([]string, len(lines))
	numbered := 0
	for index, line := range lines {
		newline := ""
		body := line
		if strings.HasSuffix(body, "\n") {
			body = strings.TrimSuffix(body, "\n")
			newline = "\n"
		}
		match := numberedReadback.FindStringSubmatch(body)
		if len(match) == 2 {
			numbered++
			stripped[index] = match[1] + newline
		} else {
			stripped[index] = line
		}
	}
	if numbered >= max(1, (len(lines)+1)/2) {
		return strings.Join(stripped, "")
	}
	return content
}

func compactWhitespace(value string) string {
	return strings.Join(strings.Fields(value), "")
}

func luaLongString(value string) string {
	for equals := 0; ; equals++ {
		marker := strings.Repeat("=", equals)
		closer := "]" + marker + "]"
		if !strings.Contains(value, closer) {
			return "[" + marker + "[" + value + closer
		}
	}
}

func sortedMapKeys(values map[string]string) []string {
	keys := make([]string, 0, len(values))
	for key := range values {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}
