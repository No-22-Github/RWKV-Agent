package bank

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/no22/RWKV-Agent/internal/lab"
)

var (
	phrasingsHeadingRe = regexp.MustCompile(`(?m)^##\s+Five alternative phrasings.*$`)
	nextHeadingRe      = regexp.MustCompile(`(?m)^##\s+`)
	phrasingItemRe     = regexp.MustCompile(`^\s*(?:\d+[.)]|\*|-)\s+(\S.*?)\s*$`)
)

// runHitcheck ports web_hitcheck.py: every one of a web case's five NOTES
// phrasings must hit at least one fixture entry under the harness substring
// rule, or the case is unsolvable as written.
func runHitcheck(args []string) int {
	fs := newFlagSet("bank hitcheck",
		"Check that the 5 alternative phrasings in each web/hybrid case's NOTES "+
			"hit at least one web_fixture entry under the harness substring rule.")
	casesRoot := fs.String("cases", DefaultCases(), "cases root directory")
	var caseArgs stringList
	fs.Var(&caseArgs, "case", "single case directory containing case.json (repeatable; overrides --cases)")
	if err := fs.Parse(args); err != nil {
		return 2
	}

	var caseDirs []string
	if len(caseArgs) > 0 {
		for _, item := range caseArgs {
			abs, err := filepath.Abs(item)
			if err != nil || !fileExists(filepath.Join(abs, "case.json")) {
				fmt.Fprintf(os.Stderr, "error: --case %s: no case.json inside\n", item)
				return 2
			}
			caseDirs = append(caseDirs, abs)
		}
	} else {
		abs, err := filepath.Abs(*casesRoot)
		if err != nil || !isDir(abs) {
			fmt.Fprintf(os.Stderr, "error: --cases %s: not a directory\n", *casesRoot)
			return 2
		}
		paths, err := caseFilePaths(abs)
		if err != nil {
			fmt.Fprintf(os.Stderr, "error: %s\n", err)
			return 2
		}
		for _, path := range paths {
			caseDirs = append(caseDirs, filepath.Dir(path))
		}
	}

	checked, failed := 0, 0
	for _, caseDir := range caseDirs {
		caseObj, err := loadCaseJSON(filepath.Join(caseDir, "case.json"))
		if err != nil {
			fmt.Fprintf(os.Stderr, "FAIL %s: case.json does not parse: %s\n", filepath.Base(caseDir), err)
			failed++
			continue
		}
		scenario := stringField(tagsOf(caseObj), "scenario")
		if (scenario != "web" && scenario != "hybrid") || len(anySlice(caseObj["web_fixture"])) == 0 {
			continue
		}
		checked++
		cid, problems, warnings := checkCaseFixture(caseDir, caseObj)
		for _, problem := range problems {
			line, err := lab.EncodeJSON(map[string]any{"case_id": cid, "miss": problem}, 0)
			if err == nil {
				fmt.Println(string(line))
			}
		}
		for _, warning := range warnings {
			fmt.Fprintf(os.Stderr, "warning %s: %s\n", cid, warning)
		}
		if len(problems) > 0 {
			failed++
		} else {
			fmt.Fprintf(os.Stderr, "ok %s: 5/5 phrasings hit the fixture\n", cid)
		}
	}

	fmt.Fprintf(os.Stderr, "%d web/hybrid case(s) with fixture checked, %d failed\n", checked, failed)
	if failed > 0 {
		return 1
	}
	return 0
}

func checkCaseFixture(caseDir string, caseObj map[string]any) (string, []string, []string) {
	cid, _ := caseObj["id"].(string)
	if cid == "" {
		cid = filepath.Base(caseDir)
	}
	var problems, warnings []string
	entries := anySlice(caseObj["web_fixture"])
	if len(entries) == 0 {
		return cid, []string{"web_fixture is empty for a web/hybrid case"}, nil
	}

	queries, problem := parsePhrasings(filepath.Join(caseDir, "NOTES.md"))
	if problem != "" {
		return cid, []string{problem}, nil
	}

	var patterns []string
	for _, entry := range entries {
		em, _ := entry.(map[string]any)
		if em == nil {
			continue
		}
		qm, _ := em["query_match"].(string)
		url, _ := em["url"].(string)
		if qm != "" && url != "" {
			patterns = append(patterns, strings.ToLower(qm))
		}
	}
	for idx, query := range queries {
		lowered := strings.ToLower(query)
		hit := false
		for _, pattern := range patterns {
			if strings.Contains(lowered, pattern) {
				hit = true
				break
			}
		}
		if !hit {
			shown := "none"
			if len(patterns) > 0 {
				shown = pyReprList(patterns)
			}
			problems = append(problems, fmt.Sprintf(
				"phrasing %d %s hits no fixture entry (searchable query_match values: %s)",
				idx+1, pyRepr(query), shown))
		}
	}

	for _, entry := range entries {
		em, _ := entry.(map[string]any)
		if em == nil {
			continue
		}
		url, _ := em["url"].(string)
		urlMatch, _ := em["url_match"].(string)
		if url != "" && !(urlMatch != "" && strings.Contains(strings.ToLower(url), strings.ToLower(urlMatch))) {
			warnings = append(warnings, fmt.Sprintf(
				"entry url %s can never resolve in web_fetch "+
					"(no url_match that is a substring of it; fetch would return the not-found page)",
				pyRepr(url)))
		}
	}
	return cid, problems, warnings
}

// parsePhrasings reads the five rewritten queries from a case's NOTES.md.
func parsePhrasings(notesPath string) ([]string, string) {
	if !fileExists(notesPath) {
		return nil, "NOTES.md missing"
	}
	text, err := lab.ReadText(notesPath)
	if err != nil {
		return nil, "NOTES.md missing"
	}
	loc := phrasingsHeadingRe.FindStringIndex(text)
	if loc == nil {
		return nil, "no '## Five alternative phrasings' section in NOTES.md"
	}
	rest := text[loc[1]:]
	if nxt := nextHeadingRe.FindStringIndex(rest); nxt != nil {
		rest = rest[:nxt[0]]
	}
	var queries []string
	for _, line := range lab.SplitLines(rest) {
		if m := phrasingItemRe.FindStringSubmatch(line); m != nil {
			queries = append(queries, m[1])
		}
	}
	if len(queries) != 5 {
		return queries, fmt.Sprintf("expected exactly 5 phrasings, found %d", len(queries))
	}
	return queries, ""
}

// pyRepr renders a string the way Python's repr() does, because the miss
// messages quote the query and the fixture patterns that way and §4.3 wants
// those strings byte-identical.
func pyRepr(s string) string {
	quote := byte('\'')
	if strings.Contains(s, "'") && !strings.Contains(s, `"`) {
		quote = '"'
	}
	var b strings.Builder
	b.WriteByte(quote)
	for _, r := range s {
		switch r {
		case '\\':
			b.WriteString(`\\`)
		case '\n':
			b.WriteString(`\n`)
		case '\r':
			b.WriteString(`\r`)
		case '\t':
			b.WriteString(`\t`)
		default:
			if r == rune(quote) {
				b.WriteByte('\\')
				b.WriteRune(r)
			} else if r < 0x20 || r == 0x7f {
				fmt.Fprintf(&b, `\x%02x`, r)
			} else {
				b.WriteRune(r)
			}
		}
	}
	b.WriteByte(quote)
	return b.String()
}

func pyReprList(items []string) string {
	parts := make([]string, 0, len(items))
	for _, item := range items {
		parts = append(parts, pyRepr(item))
	}
	return "[" + strings.Join(parts, ", ") + "]"
}

// stringList is a repeatable string flag, matching argparse's action="append".
type stringList []string

func (s *stringList) String() string { return strings.Join(*s, ",") }

func (s *stringList) Set(value string) error {
	*s = append(*s, value)
	return nil
}

func fileExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && !info.IsDir()
}

func isDir(path string) bool {
	info, err := os.Stat(path)
	return err == nil && info.IsDir()
}
