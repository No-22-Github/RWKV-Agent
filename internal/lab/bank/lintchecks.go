package bank

import (
	"encoding/json"
	"fmt"
	"math"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

// stdlibModules is Python's sys.stdlib_module_names, which lint.py uses to
// decide whether a verify.py imports anything it should not. It is embedded
// rather than asked of an interpreter: rwkv-lab must not need Python to run.
// Generated from CPython 3.13; a module added in a later version would be
// reported as non-stdlib, which is a false positive worth re-generating for.
var stdlibModules = map[string]struct{}{
	"__future__": {}, "_abc": {}, "_aix_support": {}, "_android_support": {}, "_apple_support": {},
	"_ast": {}, "_asyncio": {}, "_bisect": {}, "_blake2": {}, "_bz2": {}, "_codecs": {},
	"_codecs_cn": {}, "_codecs_hk": {}, "_codecs_iso2022": {}, "_codecs_jp": {}, "_codecs_kr": {},
	"_codecs_tw": {}, "_collections": {}, "_collections_abc": {}, "_colorize": {},
	"_compat_pickle": {}, "_compression": {}, "_contextvars": {}, "_csv": {}, "_ctypes": {},
	"_curses": {}, "_curses_panel": {}, "_datetime": {}, "_dbm": {}, "_decimal": {},
	"_elementtree": {}, "_frozen_importlib": {}, "_frozen_importlib_external": {}, "_functools": {}, "_gdbm": {}, "_hashlib": {}, "_heapq": {}, "_imp": {}, "_interpchannels": {},
	"_interpqueues": {}, "_interpreters": {}, "_io": {}, "_ios_support": {}, "_json": {},
	"_locale": {}, "_lsprof": {}, "_lzma": {}, "_markupbase": {}, "_md5": {}, "_multibytecodec": {}, "_multiprocessing": {}, "_opcode": {}, "_opcode_metadata": {}, "_operator": {},
	"_osx_support": {}, "_overlapped": {}, "_pickle": {}, "_posixshmem": {}, "_posixsubprocess": {}, "_py_abc": {}, "_pydatetime": {}, "_pydecimal": {}, "_pyio": {}, "_pylong": {}, "_pyrepl": {}, "_queue": {}, "_random": {}, "_scproxy": {}, "_sha1": {}, "_sha2": {}, "_sha3": {},
	"_signal": {}, "_sitebuiltins": {}, "_socket": {}, "_sqlite3": {}, "_sre": {}, "_ssl": {},
	"_stat": {}, "_statistics": {}, "_string": {}, "_strptime": {}, "_struct": {}, "_suggestions": {}, "_symtable": {}, "_sysconfig": {}, "_thread": {}, "_threading_local": {}, "_tkinter": {},
	"_tokenize": {}, "_tracemalloc": {}, "_typing": {}, "_uuid": {}, "_warnings": {}, "_weakref": {}, "_weakrefset": {}, "_winapi": {}, "_wmi": {}, "_zoneinfo": {}, "abc": {}, "antigravity": {}, "argparse": {}, "array": {}, "ast": {}, "asyncio": {}, "atexit": {}, "base64": {}, "bdb": {}, "binascii": {}, "bisect": {}, "builtins": {}, "bz2": {}, "cProfile": {}, "calendar": {},
	"cmath": {}, "cmd": {}, "code": {}, "codecs": {}, "codeop": {}, "collections": {}, "colorsys": {}, "compileall": {}, "concurrent": {}, "configparser": {}, "contextlib": {}, "contextvars": {}, "copy": {}, "copyreg": {}, "csv": {}, "ctypes": {}, "curses": {}, "dataclasses": {},
	"datetime": {}, "dbm": {}, "decimal": {}, "difflib": {}, "dis": {}, "doctest": {}, "email": {},
	"encodings": {}, "ensurepip": {}, "enum": {}, "errno": {}, "faulthandler": {}, "fcntl": {},
	"filecmp": {}, "fileinput": {}, "fnmatch": {}, "fractions": {}, "ftplib": {}, "functools": {},
	"gc": {}, "genericpath": {}, "getopt": {}, "getpass": {}, "gettext": {}, "glob": {},
	"graphlib": {}, "grp": {}, "gzip": {}, "hashlib": {}, "heapq": {}, "hmac": {}, "html": {},
	"http": {}, "idlelib": {}, "imaplib": {}, "importlib": {}, "inspect": {}, "io": {},
	"ipaddress": {}, "itertools": {}, "json": {}, "keyword": {}, "linecache": {}, "locale": {},
	"logging": {}, "lzma": {}, "mailbox": {}, "marshal": {}, "math": {}, "mimetypes": {}, "mmap": {}, "modulefinder": {}, "msvcrt": {}, "multiprocessing": {}, "netrc": {}, "nt": {}, "ntpath": {}, "nturl2path": {}, "numbers": {}, "opcode": {}, "operator": {}, "optparse": {}, "os": {},
	"pathlib": {}, "pdb": {}, "pickle": {}, "pickletools": {}, "pkgutil": {}, "platform": {},
	"plistlib": {}, "poplib": {}, "posix": {}, "posixpath": {}, "pprint": {}, "profile": {},
	"pstats": {}, "pty": {}, "pwd": {}, "py_compile": {}, "pyclbr": {}, "pydoc": {}, "pydoc_data": {}, "pyexpat": {}, "queue": {}, "quopri": {}, "random": {}, "re": {}, "readline": {},
	"reprlib": {}, "resource": {}, "rlcompleter": {}, "runpy": {}, "sched": {}, "secrets": {},
	"select": {}, "selectors": {}, "shelve": {}, "shlex": {}, "shutil": {}, "signal": {}, "site": {}, "smtplib": {}, "socket": {}, "socketserver": {}, "sqlite3": {}, "sre_compile": {},
	"sre_constants": {}, "sre_parse": {}, "ssl": {}, "stat": {}, "statistics": {}, "string": {},
	"stringprep": {}, "struct": {}, "subprocess": {}, "symtable": {}, "sys": {}, "sysconfig": {},
	"syslog": {}, "tabnanny": {}, "tarfile": {}, "tempfile": {}, "termios": {}, "textwrap": {},
	"this": {}, "threading": {}, "time": {}, "timeit": {}, "tkinter": {}, "token": {}, "tokenize": {}, "tomllib": {}, "trace": {}, "traceback": {}, "tracemalloc": {}, "tty": {}, "turtle": {},
	"turtledemo": {}, "types": {}, "typing": {}, "unicodedata": {}, "unittest": {}, "urllib": {},
	"uuid": {}, "venv": {}, "warnings": {}, "wave": {}, "weakref": {}, "webbrowser": {}, "winreg": {}, "winsound": {}, "wsgiref": {}, "xml": {}, "xmlrpc": {}, "zipapp": {}, "zipfile": {},
	"zipimport": {}, "zlib": {}, "zoneinfo": {},
}

var (
	notesSectionRe = regexp.MustCompile(`(?m)^##[\s\p{Zs}]+`)
	fivePhrasingRe = regexp.MustCompile(`(?m)^##[\s\p{Zs}]+Five alternative phrasings.*$`)
	noteItemRe     = regexp.MustCompile(`^\s*(?:\d+[.)]|\*|-)\s+(\S.*?)\s*$`)
)

// foreignCanaryViolations ports the §4.1 guard: when a tree is linted under a
// canary prefix other than WORKBANK-CANARY, the test-bank canary must not
// survive anywhere in the case. Its meaning is "test case, keep out of the
// training corpus", so a distillation case carrying it would either trip the
// downstream leak scan or, worse, train everyone to ignore it.
func foreignCanaryViolations(description, caseDir, prefix string) [][2]string {
	var out [][2]string
	check := func(where, text string) {
		if strings.Contains(text, defaultCanaryPrefix) {
			out = append(out, [2]string{"canary.foreign",
				fmt.Sprintf("%s contains %s; use the configured canary prefix %s-<8 lowercase hex> instead",
					where, defaultCanaryPrefix, prefix)})
		}
	}
	check("description", description)
	for _, name := range []string{"verify.py", "NOTES.md"} {
		text, err := lab.ReadText(filepath.Join(caseDir, name))
		if err != nil {
			continue // a missing file is reported by its own rule
		}
		check(name, text)
	}
	return out
}

// verifyPyViolations ports lint.py's verify_py_violations: verify.py must exist,
// parse, import only the standard library, and read its own case.json.
func verifyPyViolations(caseDir string) [][2]string {
	path := filepath.Join(caseDir, "verify.py")
	if !fileExists(path) {
		return [][2]string{{"verify", "verify.py missing"}}
	}
	text, err := lab.ReadText(path)
	if err != nil {
		return [][2]string{{"verify", "verify.py missing"}}
	}
	var out [][2]string
	roots, ok := pythonImportRoots(text)
	if !ok {
		out = append(out, [2]string{"verify", "verify.py does not parse"})
	}
	var nonStdlib []string
	for _, root := range roots {
		if _, std := stdlibModules[root]; !std {
			nonStdlib = append(nonStdlib, root)
		}
	}
	if len(nonStdlib) > 0 {
		sort.Strings(nonStdlib)
		out = append(out, [2]string{"verify", "non-stdlib imports: " + pyReprList(nonStdlib)})
	}
	if !strings.Contains(text, "case.json") {
		out = append(out, [2]string{"verify",
			`verify.py must reference "case.json" (it computes expectations from the case file)`})
	}
	return out
}

// pythonImportRoots returns the top-level module names a script imports. It is
// a scanner rather than a parser: the port has no Python parser available, and
// verify.py files are small stdlib-only scripts. Comments and string literals
// are skipped so that a docstring mentioning "import torch" does not count.
func pythonImportRoots(text string) ([]string, bool) {
	cleaned := stripPythonStringsAndComments(text)
	var roots []string
	for _, line := range strings.Split(cleaned, "\n") {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "import ") {
			for _, part := range strings.Split(strings.TrimPrefix(trimmed, "import "), ",") {
				name := strings.TrimSpace(part)
				if idx := strings.Index(name, " as "); idx != -1 {
					name = strings.TrimSpace(name[:idx])
				}
				if root := firstDottedComponent(name); root != "" {
					roots = append(roots, root)
				}
			}
			continue
		}
		if strings.HasPrefix(trimmed, "from ") {
			rest := strings.TrimSpace(strings.TrimPrefix(trimmed, "from "))
			idx := strings.Index(rest, " import")
			if idx == -1 {
				continue
			}
			module := strings.TrimSpace(rest[:idx])
			if strings.HasPrefix(module, ".") {
				continue // relative import: ast.ImportFrom.level > 0
			}
			if root := firstDottedComponent(module); root != "" {
				roots = append(roots, root)
			}
		}
	}
	return roots, true
}

func firstDottedComponent(name string) string {
	name = strings.TrimSpace(name)
	if name == "" {
		return ""
	}
	if idx := strings.Index(name, "."); idx != -1 {
		name = name[:idx]
	}
	if !isPythonIdentifier(name) {
		return ""
	}
	return name
}

func isPythonIdentifier(s string) bool {
	if s == "" {
		return false
	}
	for i, r := range s {
		switch {
		case r == '_', r >= 'a' && r <= 'z', r >= 'A' && r <= 'Z':
		case r >= '0' && r <= '9' && i > 0:
		default:
			return false
		}
	}
	return true
}

// stripPythonStringsAndComments blanks out comments and string literals,
// including triple-quoted ones, so line-based import scanning does not trip on
// prose. It keeps the line structure intact.
func stripPythonStringsAndComments(text string) string {
	var b strings.Builder
	i := 0
	for i < len(text) {
		c := text[i]
		switch {
		case c == '#':
			for i < len(text) && text[i] != '\n' {
				i++
			}
		case c == '\'' || c == '"':
			quote := c
			triple := i+2 < len(text) && text[i+1] == quote && text[i+2] == quote
			if triple {
				i += 3
				for i+2 < len(text) && !(text[i] == quote && text[i+1] == quote && text[i+2] == quote) {
					if text[i] == '\\' {
						i++
					}
					i++
				}
				if i+2 < len(text) {
					i += 3
				} else {
					i = len(text)
				}
				continue
			}
			i++
			for i < len(text) && text[i] != quote {
				if text[i] == '\\' {
					i++
				}
				if i < len(text) && text[i] == '\n' {
					b.WriteByte('\n') // unterminated literal: keep the line break
				}
				i++
			}
			if i < len(text) {
				i++
			}
		default:
			b.WriteByte(c)
			i++
		}
	}
	return b.String()
}

// notesViolations ports lint.py's notes_violations: NOTES.md must carry the
// three mandatory sections, plus the five phrasings for web/hybrid cases.
func notesViolations(caseDir, scenario string) [][2]string {
	path := filepath.Join(caseDir, "NOTES.md")
	if !fileExists(path) {
		return [][2]string{{"notes", "NOTES.md missing"}}
	}
	text, err := lab.ReadText(path)
	if err != nil {
		return [][2]string{{"notes", "NOTES.md missing"}}
	}
	var out [][2]string
	for _, section := range notesSecs {
		re := regexp.MustCompile(`(?m)^##[\s\p{Zs}]+` + regexp.QuoteMeta(section) + `[\s\p{Zs}]*$`)
		if !re.MatchString(text) {
			out = append(out, [2]string{"notes", "missing section '## " + section + "'"})
		}
	}
	if scenario == "web" || scenario == "hybrid" {
		loc := fivePhrasingRe.FindStringIndex(text)
		if loc == nil {
			out = append(out, [2]string{"notes", "missing section '## Five alternative phrasings'"})
		} else {
			rest := text[loc[1]:]
			if nxt := regexp.MustCompile(`(?m)^##[\s\p{Zs}]+`).FindStringIndex(rest); nxt != nil {
				rest = rest[:nxt[0]]
			}
			items := 0
			for _, line := range lab.SplitLines(rest) {
				if noteItemRe.MatchString(line) {
					items++
				}
			}
			if items != 5 {
				out = append(out, [2]string{"notes",
					fmt.Sprintf("'## Five alternative phrasings' must list exactly 5 queries, found %d", items)})
			}
		}
	}
	return out
}

// notesAnswerViolations ports notes_answer_violations: NOTES.md has to state
// the answer case.json scores, or a reviewer triaging a failing trace reads a
// file that argues for a different one.
func notesAnswerViolations(caseDir string, caseObj map[string]any) [][2]string {
	path := filepath.Join(caseDir, "NOTES.md")
	if !fileExists(path) {
		return nil
	}
	text, err := lab.ReadText(path)
	if err != nil {
		return nil
	}
	var out [][2]string
	for _, forms := range expectedAnswerTokens(caseObj) {
		found := false
		for _, form := range forms {
			if form != "" && strings.Contains(text, form) {
				found = true
				break
			}
		}
		if !found {
			out = append(out, [2]string{"notes.answer",
				fmt.Sprintf("NOTES.md does not state the expected answer (any of %s); sync the notes with case.json",
					pyReprList(forms))})
		}
	}
	return out
}

// expectedAnswerTokens is the set of spellings a NOTES.md may use for each
// turn's expected answer.
func expectedAnswerTokens(caseObj map[string]any) [][]string {
	var tokens [][]string
	for _, turn := range turnObjects(caseObj) {
		expect, _ := turn["expect"].(map[string]any)
		if v, ok := expect["expected_number"]; ok {
			forms := map[string]struct{}{pyReprValue(v): {}}
			if f, ok := pyFloatValue(v); ok {
				forms[pythonG(f)] = struct{}{}
				if f == math.Trunc(f) && !math.IsInf(f, 0) {
					forms[strconv.FormatInt(int64(f), 10)] = struct{}{}
					forms[commaGroup(int64(f))] = struct{}{}
				}
			}
			tokens = append(tokens, sortedKeysOf(forms))
		}
		if v, ok := expect["output_equals"]; ok {
			tokens = append(tokens, []string{pyStrValue(v)})
		}
		if anyOf, ok := expect["output_equals_any"].([]any); ok {
			forms := make([]string, 0, len(anyOf))
			for _, v := range anyOf {
				forms = append(forms, pyStrValue(v))
			}
			tokens = append(tokens, forms)
		}
	}
	return tokens
}

// pythonG is Python's f"{value:g}": six significant digits, trailing zeros
// trimmed.
func pythonG(f float64) string {
	s := strconv.FormatFloat(f, 'g', 6, 64)
	if strings.Contains(s, "e") {
		// Python writes exponents with at least two digits: 1e+06.
		parts := strings.SplitN(s, "e", 2)
		mantissa, exp := parts[0], parts[1]
		sign := "+"
		if strings.HasPrefix(exp, "-") {
			sign = "-"
			exp = exp[1:]
		} else {
			exp = strings.TrimPrefix(exp, "+")
		}
		for len(exp) < 2 {
			exp = "0" + exp
		}
		s = mantissa + "e" + sign + exp
	}
	return s
}

func commaGroup(n int64) string {
	s := strconv.FormatInt(n, 10)
	sign := ""
	if strings.HasPrefix(s, "-") {
		sign, s = "-", s[1:]
	}
	var parts []string
	for len(s) > 3 {
		parts = append([]string{s[len(s)-3:]}, parts...)
		s = s[:len(s)-3]
	}
	parts = append([]string{s}, parts...)
	return sign + strings.Join(parts, ",")
}

// hiddenFileViolations ports hidden_file_violations: a hidden input outside the
// project tree makes the case turn on an idiom it never states.
func hiddenFileViolations(caseObj map[string]any) [][2]string {
	caseExpect, _ := caseObj["expect"].(map[string]any)
	run, _ := caseExpect["run"].(map[string]any)
	var out [][2]string
	for path := range anyMap(run["hidden_files"]) {
		normalized := strings.ReplaceAll(path, "\\", "/")
		if strings.HasPrefix(normalized, "/") || containsString(strings.Split(normalized, "/"), "..") {
			out = append(out, [2]string{"expect.run.hidden",
				fmt.Sprintf("hidden file %s must be a relative path inside the workspace", pyReprValue(path))})
		}
	}
	return out
}

// webFixtureViolations ports web_fixture_violations: every fixture URL must
// resolve back to its own entry, or a case can become unsolvable without
// anything else looking wrong.
func webFixtureViolations(caseObj map[string]any) [][2]string {
	entries := anySlice(caseObj["web_fixture"])
	var out [][2]string
	for index, entryAny := range entries {
		entry := anyMap(entryAny)
		url := strings.ToLower(asString(entry["url"]))
		own := strings.ToLower(asString(entry["url_match"]))
		if url == "" || own == "" {
			continue
		}
		if !strings.Contains(url, own) {
			out = append(out, [2]string{"web_fixture.url_match",
				fmt.Sprintf("entry[%d] url_match %s does not match its own url %s",
					index, pyReprValue(entry["url_match"]), pyReprValue(entry["url"]))})
			continue
		}
		best, winner := -1, 0
		for other, candidateAny := range entries {
			candidate := strings.ToLower(asString(anyMap(candidateAny)["url_match"]))
			if candidate != "" && strings.Contains(url, candidate) && len(candidate) > best {
				best, winner = len(candidate), other
			}
		}
		if winner != index {
			out = append(out, [2]string{"web_fixture.url_match",
				fmt.Sprintf("entry[%d] url %s resolves to entry[%d] (url_match %s); make the url_match unambiguous",
					index, pyReprValue(entry["url"]), winner,
					pyReprValue(anyMap(entries[winner])["url_match"]))})
		}
	}
	return out
}

// answersEqual is Python's numeric-when-possible, string-otherwise comparison.
func answersEqual(decoy, expected any) bool {
	df, dok := pyFloatValue(decoy)
	ef, eok := pyFloatValue(expected)
	if dok && eok {
		return df == ef
	}
	return pyStrValue(decoy) == pyStrValue(expected)
}

// pyFloatValue is Python's float(x) for the JSON types that can appear here.
func pyFloatValue(v any) (float64, bool) {
	switch t := v.(type) {
	case json.Number:
		f, err := t.Float64()
		return f, err == nil
	case string:
		s := strings.TrimSpace(t)
		switch strings.ToLower(s) {
		case "inf", "+inf", "infinity", "+infinity":
			return math.Inf(1), true
		case "-inf", "-infinity":
			return math.Inf(-1), true
		case "nan":
			return math.NaN(), true
		}
		f, err := strconv.ParseFloat(s, 64)
		return f, err == nil
	case bool:
		if t {
			return 1, true
		}
		return 0, true
	}
	return 0, false
}

// pyStrValue is Python's str(x).
func pyStrValue(v any) string {
	switch t := v.(type) {
	case nil:
		return "None"
	case bool:
		if t {
			return "True"
		}
		return "False"
	case string:
		return t
	default:
		return pyReprValue(v)
	}
}

// pyReprValue is Python's repr() for the JSON values the checks put into
// messages. Getting it wrong shows up immediately in a baseline diff, since
// the detail strings are compared byte for byte.
func pyReprValue(v any) string {
	switch t := v.(type) {
	case nil:
		return "None"
	case bool:
		if t {
			return "True"
		}
		return "False"
	case string:
		return pyRepr(t)
	case json.Number:
		s := t.String()
		if strings.ContainsAny(s, ".eE") {
			if f, err := t.Float64(); err == nil {
				return lab.PyFloat(f).String()
			}
		}
		return s
	case float64:
		return lab.PyFloat(t).String()
	case int:
		return strconv.Itoa(t)
	case []string:
		return pyReprList(t)
	case []any:
		parts := make([]string, 0, len(t))
		for _, item := range t {
			parts = append(parts, pyReprValue(item))
		}
		return "[" + strings.Join(parts, ", ") + "]"
	case map[string]any:
		keys := make([]string, 0, len(t))
		for k := range t {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		parts := make([]string, 0, len(keys))
		for _, k := range keys {
			parts = append(parts, pyRepr(k)+": "+pyReprValue(t[k]))
		}
		return "{" + strings.Join(parts, ", ") + "}"
	default:
		return fmt.Sprintf("%v", v)
	}
}

// intValue reports whether v is a Python int (not a float, not a bool).
func intValue(v any) (int, bool) {
	n, ok := v.(json.Number)
	if !ok {
		return 0, false
	}
	if strings.ContainsAny(n.String(), ".eE") {
		return 0, false
	}
	i, err := n.Int64()
	if err != nil {
		return 0, false
	}
	return int(i), true
}

// numbersEqual is Python's `stored != computed` where stored may be absent.
func numbersEqual(stored any, hasStored bool, computed int) bool {
	if !hasStored {
		return false
	}
	if f, ok := pyFloatValue(stored); ok {
		return f == float64(computed)
	}
	return false
}

func sortedKeysOf(set map[string]struct{}) []string {
	out := make([]string, 0, len(set))
	for k := range set {
		out = append(out, k)
	}
	sort.Strings(out)
	return out
}
