#!/usr/bin/env python3
"""lint.py — bank-side validator for workbank hand-written cases (schema v5).

Checks every case under --cases (a tree of <scenario>/<id>/case.json) or a
single --case directory against docs/tag-vocab.json and the authoring rules:

  tags.enum / tags.required   (a) tag vocabulary + required keys
  prompt.tool_name            (b) no tool names in any turn prompt
  prompt.forbidden_word       (b) no forbidden words of the case's declared
                                traps, nor of traps whose vocab 'scenarios'
                                list makes them intrinsic to the case's
                                scenario (e.g. TR-NOTOOLNEED for notool)
  answer_contract             (c) exact byte contract at end of last prompt
                                (write-file cases -> DONE, answer cases -> UNKNOWN)
  canary                      (d) WORKBANK-CANARY-<8 hex> at end of description
  level                       (e) level consistent with trap count / ref_calls
  fixture_bytes               (f) matches sum of files content bytes (--fix backfills)
  trap_decoys                 (g) every trap has a decoy != expected answer
  axes.coverage               (h) axes cover every trap's axis
  m0.write_dir                (i) expect.files parent dirs pre-created in files
  dir_structure               (j) <scenario>/<id>/ with <abbrev>-<4 digits>
  verify                      (k) verify.py exists, stdlib only, references case.json
  notes                       (k) NOTES.md sections (web/hyb: 5 alternative phrasings)
  author.status               (l) author llm:* implies draft unless a human: reviewer is set
  id.unique                   (m) ids unique across the bank

Output: one JSON object {"case_id", "rule", "detail"} per violation on stdout,
human summary on stderr. Exit 1 when any violation remains. --fix only
backfills tags.fixture_bytes; it never touches anything else.

Standard library only.
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
WORKBANK_DIR = TOOLS_DIR.parent
DEFAULT_CASES = WORKBANK_DIR / "cases"
DEFAULT_VOCAB = WORKBANK_DIR / "docs" / "tag-vocab.json"

REQUIRED_TAGS = [
    "scenario", "task_type", "traps", "trap_decoys", "axes", "level",
    "ref_calls", "fixture_bytes", "status", "version", "author", "reviewer",
]
CANARY_RE = re.compile(r"WORKBANK-CANARY-[0-9a-f]{8}$")
CASE_ID_RE = re.compile(r"^([a-z]+)-(\d{4})$")
NOTES_SECTIONS = ["Traps", "Reference solution", "Why the answer is unique"]
FIVE_PHRASINGS_RE = re.compile(r"^##\s+Five alternative phrasings.*$", re.M)
NOTE_ITEM_RE = re.compile(r"^\s*(?:\d+[.)]|\*|-)\s+(\S.*)$")


class Ctx:
    def __init__(self, vocab_path):
        with open(vocab_path, encoding="utf-8") as fh:
            vocab = json.load(fh)
        self.vocab = vocab
        self.scenarios = [s["name"] for s in vocab["scenarios"]]
        self.abbrev = {s["name"]: s["abbrev"] for s in vocab["scenarios"]}
        self.task_types = vocab["task_types"]
        self.traps = vocab["traps"]
        self.axes = set(vocab["axes"])
        self.levels = set(vocab["levels"])
        self.statuses = set(vocab["statuses"])
        self.tools = vocab["tools"]
        self.contracts = vocab["answer_contracts"]
        # scenario name -> trap ids whose forbidden_words apply to every case
        # of that scenario, declared or not (trap entry carries "scenarios")
        self.scenario_traps = {}
        for trap_id, entry in self.traps.items():
            for scen in entry.get("scenarios") or []:
                self.scenario_traps.setdefault(scen, []).append(trap_id)


def load_case(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fixture_bytes_of(case):
    return sum(len(c.encode("utf-8")) for c in (case.get("files") or {}).values())


def answers_equal(decoy, expected):
    """Numeric comparison when both sides coerce to float, else string compare."""
    try:
        return float(decoy) == float(expected)
    except (TypeError, ValueError):
        return str(decoy) == str(expected)


def forbidden_phrase_re(phrase):
    """Regex for a forbidden phrase over whitespace-normalized lowercase text.

    Case-insensitive by construction (both sides are lowercased). A single
    word matches as a substring (historic semantics). A multi-word phrase
    matches when its words appear in order with at most 3 extra words
    between consecutive phrase words, so "without tools" also matches
    "without using any tools".
    """
    words = phrase.lower().split()
    if len(words) == 1:
        return re.compile(re.escape(words[0]))
    pat = re.escape(words[0])
    for word in words[1:]:
        pat += r"(?: \S+){0,3} " + re.escape(word)
    return re.compile(pat)


def normalize_prompt(text):
    return re.sub(r"\s+", " ", text.lower())


def allowed_levels(n_traps, ref_calls, n_files, multi_turn):
    """authoring-guide.md section 4 difficulty rules."""
    valid = set()
    if n_traps == 0 and ref_calls <= 3:
        valid.add("L0")
    if n_traps == 1 and ref_calls <= 4:
        valid.add("L1")
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref_calls >= 5)):
        valid.add("L2")
    if n_traps >= 3 or (multi_turn and n_traps >= 1) or ref_calls >= 8:
        valid.add("L3")
    return valid


def verify_py_violations(case_dir, cid):
    out = []
    path = case_dir / "verify.py"
    if not path.is_file():
        return [("verify", "verify.py missing")]
    text = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        out.append(("verify", f"verify.py does not parse: {exc}"))
        tree = None
    if tree is not None:
        roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    roots.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.level == 0 and node.module:
                    roots.add(node.module.split(".")[0])
        non_stdlib = sorted(m for m in roots if m not in sys.stdlib_module_names)
        if non_stdlib:
            out.append(("verify", f"non-stdlib imports: {non_stdlib}"))
    if "case.json" not in text:
        out.append(("verify", 'verify.py must reference "case.json" (it computes expectations from the case file)'))
    return out


def expected_answer_tokens(case):
    """The answer strings a NOTES.md for this case has to be able to state.

    Only the turn-level answer expectations count: these are the values that a
    reviewer reads NOTES.md to check a failing trace against, and the values
    that go stale when a case is revised without its notes. Refusal-lexicon
    lists (output_contains_any with many alternatives) are not answers and are
    skipped, as are script cases, whose answer is their stdout.
    """
    tokens = []
    for turn in case.get("turns") or []:
        expect = turn.get("expect") or {}
        if "expected_number" in expect:
            value = expect["expected_number"]
            forms = {repr(value), f"{value:g}"}
            if float(value).is_integer():
                forms.add(str(int(value)))
                forms.add(f"{int(value):,}")
            tokens.append(sorted(forms))
        if "output_equals" in expect:
            tokens.append([str(expect["output_equals"])])
        if isinstance(expect.get("output_equals_any"), list):
            tokens.append([str(v) for v in expect["output_equals_any"]])
    return tokens


def notes_answer_violations(case_dir, case):
    """NOTES.md must state the case's own expected answer.

    A case that is revised without its notes leaves the notes asserting a
    different answer than the bank scores, and the notes are what a reviewer
    triages failing traces against. nt-0001 carried a v1 reference answer of
    9437.184 through a v2 rewrite to 9000 and additionally listed 9000 as the
    "careless value" to expect in failing traces, so the file actively argued
    that the correct answer was the wrong one.
    """
    path = case_dir / "NOTES.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    out = []
    for forms in expected_answer_tokens(case):
        if not any(form and form in text for form in forms):
            out.append((
                "notes.answer",
                f"NOTES.md does not state the expected answer (any of {forms}); "
                "sync the notes with case.json",
            ))
    return out


def hidden_file_violations(case):
    """expect.run hidden inputs have to live inside the workspace.

    A hidden set written outside the project tree splits the anchors a script
    can legitimately use: a sweep rooted at the launch directory reaches it and
    a sweep rooted at the script's own directory does not, so the case turns on
    an idiom it never states. scr-0004 shipped that way.
    """
    run = ((case.get("expect") or {}).get("run")) or {}
    out = []
    for path in (run.get("hidden_files") or {}):
        normalized = path.replace("\\", "/")
        parts = normalized.split("/")
        if normalized.startswith("/") or ".." in parts:
            out.append((
                "expect.run.hidden",
                f"hidden file {path!r} must be a relative path inside the workspace",
            ))
    return out


def web_fixture_violations(case):
    """Every fixture URL must resolve back to its own entry.

    web_fetch picks the entry with the longest url_match contained in the
    requested URL. One fixture's url_match is easily a prefix of another's URL
    (".../desk-rates" vs ".../desk-rates-september"), and before the matcher
    preferred the longest match the shorter entry captured both: hyb-0004's
    September rate sheet was unreachable, which made the case unsolvable and
    made every model that answered from the June sheet look wrong.

    Asserting round-trip resolution catches the collision and a mistyped
    url_match in the same check.
    """
    entries = case.get("web_fixture") or []
    out = []
    for index, entry in enumerate(entries):
        url = (entry.get("url") or "").lower()
        own = (entry.get("url_match") or "").lower()
        if not url or not own:
            continue
        if own not in url:
            out.append((
                "web_fixture.url_match",
                f"entry[{index}] url_match {entry['url_match']!r} does not match its own url {entry['url']!r}",
            ))
            continue
        best, winner = -1, None
        for other, candidate in enumerate(entries):
            match = (candidate.get("url_match") or "").lower()
            if match and match in url and len(match) > best:
                best, winner = len(match), other
        if winner != index:
            out.append((
                "web_fixture.url_match",
                f"entry[{index}] url {entry['url']!r} resolves to entry[{winner}] "
                f"(url_match {entries[winner].get('url_match')!r}); make the url_match unambiguous",
            ))
    return out


def notes_violations(case_dir, cid, scenario):
    out = []
    path = case_dir / "NOTES.md"
    if not path.is_file():
        return [("notes", "NOTES.md missing")]
    text = path.read_text(encoding="utf-8")
    for section in NOTES_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(section)}\s*$", text, re.M):
            out.append(("notes", f"missing section '## {section}'"))
    if scenario in ("web", "hybrid"):
        match = FIVE_PHRASINGS_RE.search(text)
        if not match:
            out.append(("notes", "missing section '## Five alternative phrasings'"))
        else:
            rest = text[match.end():]
            nxt = re.search(r"^##\s+", rest, re.M)
            body = rest[: nxt.start()] if nxt else rest
            items = [line for line in body.splitlines() if NOTE_ITEM_RE.match(line)]
            if len(items) != 5:
                out.append(("notes", f"'## Five alternative phrasings' must list exactly 5 queries, found {len(items)}"))
    return out


def check_case(case_dir, case, ctx, rel_parts, violations, fixed_notes):
    cid = case.get("id") if isinstance(case.get("id"), str) else case_dir.name
    tags = case.get("tags") if isinstance(case.get("tags"), dict) else {}

    def bad(rule, detail):
        violations.append({"case_id": cid, "rule": rule, "detail": detail})

    # (a) required tag keys + enums
    for key in REQUIRED_TAGS:
        if key not in tags:
            bad("tags.required", f"missing tags.{key}")
    scenario = tags.get("scenario")
    if scenario not in ctx.scenarios:
        bad("tags.enum", f"scenario {scenario!r} not in vocabulary")
    task_type = tags.get("task_type")
    if scenario in ctx.task_types and task_type not in ctx.task_types[scenario]:
        bad("tags.enum", f"task_type {task_type!r} not allowed for scenario {scenario!r}")
    for axis in tags.get("axes") or []:
        if axis not in ctx.axes:
            bad("tags.enum", f"axis {axis!r} not in vocabulary")
    for trap in tags.get("traps") or []:
        if trap not in ctx.traps:
            bad("tags.enum", f"trap {trap!r} not in vocabulary")
    if tags.get("level") not in ctx.levels:
        bad("tags.enum", f"level {tags.get('level')!r} not in vocabulary")
    if tags.get("status") not in ctx.statuses:
        bad("tags.enum", f"status {tags.get('status')!r} not in vocabulary")

    # (f) fixture_bytes — with --fix, backfill from files content before validating
    computed_bytes = fixture_bytes_of(case)
    stored_bytes = tags.get("fixture_bytes")
    if stored_bytes != computed_bytes:
        if FIX_MODE:
            fixed_notes.append(f"{cid}: fixture_bytes {stored_bytes!r} -> {computed_bytes}")
            tags["fixture_bytes"] = computed_bytes
            with open(case_dir / "case.json", "w", encoding="utf-8") as fh:
                json.dump(case, fh, indent=2, ensure_ascii=False)
                fh.write("\n")
        else:
            bad("fixture_bytes", f"tags.fixture_bytes is {stored_bytes!r}, files sum to {computed_bytes} bytes")

    # (b) prompts: tool names + forbidden words of declared traps and of
    # traps intrinsic to this scenario (vocab trap entries with "scenarios").
    # The mandated answer contract is boilerplate, not author-written task
    # text, and may itself contain a forbidden token ("cannot"), so it is
    # stripped before the forbidden-word scan.
    turns = [t for t in case.get("turns") or [] if isinstance(t, dict)]
    prompts = [t.get("prompt") or "" for t in turns]
    forbidden_traps = list(tags.get("traps") or [])
    for trap in ctx.scenario_traps.get(scenario, []):
        if trap not in forbidden_traps:
            forbidden_traps.append(trap)
    for idx, prompt in enumerate(prompts, 1):
        low = prompt.lower()
        body = prompt
        for contract in ctx.contracts.values():
            if body.endswith(contract):
                body = body[: -len(contract)]
                break
        norm = normalize_prompt(body)
        for tool in ctx.tools:
            if tool in low:
                bad("prompt.tool_name", f"turn {idx}: tool name {tool!r} in prompt")
        for trap in forbidden_traps:
            words = ctx.traps.get(trap, {}).get("forbidden_words", []) if trap in ctx.traps else []
            for word in words:
                if forbidden_phrase_re(word).search(norm):
                    bad("prompt.forbidden_word", f"turn {idx}: forbidden word {word!r} of {trap} in prompt")

    # (c) answer contract, byte-exact, at the end of the last prompt
    case_expect = case.get("expect") or {}
    write_case = bool(case_expect.get("files") or case_expect.get("run"))
    required = ctx.contracts["done"] if write_case else ctx.contracts["unknown"]
    if prompts:
        if not prompts[-1].endswith(required):
            kind = "DONE" if write_case else "UNKNOWN"
            bad("answer_contract", f"last turn prompt must end with the exact {kind} contract")
    else:
        bad("answer_contract", "case has no turns")

    # (d) canary
    description = case.get("description") or ""
    if not CANARY_RE.search(description):
        bad("canary", "description must end with WORKBANK-CANARY-<8 lowercase hex>")

    # (e) level rule
    n_traps = len(tags.get("traps") or [])
    ref_calls = tags.get("ref_calls")
    n_files = len(case.get("files") or {})
    multi_turn = len(turns) > 1
    if isinstance(ref_calls, int) and not isinstance(ref_calls, bool):
        valid = allowed_levels(n_traps, ref_calls, n_files, multi_turn)
        if tags.get("level") not in valid:
            bad("level", f"declared {tags.get('level')!r} but traps={n_traps}, ref_calls={ref_calls}, "
                         f"files={n_files}, multi_turn={multi_turn} allows {sorted(valid) or 'no level'}")
    elif "ref_calls" in tags:
        bad("level", f"ref_calls must be an integer, got {ref_calls!r}")

    # (g) trap_decoys present and != expected answer (null allowed for write-file cases)
    decoys = tags.get("trap_decoys") or {}
    expected_answers = []
    for t in turns:
        texp = t.get("expect") or {}
        if "expected_number" in texp:
            expected_answers.append(texp["expected_number"])
        if "output_equals" in texp:
            expected_answers.append(texp["output_equals"])
        any_of = texp.get("output_equals_any")
        if isinstance(any_of, list):
            expected_answers.extend(any_of)
    for trap in tags.get("traps") or []:
        if trap not in decoys:
            bad("trap_decoys", f"no trap_decoys entry for {trap}")
            continue
        value = decoys[trap]
        if value is None:
            if not write_case:
                bad("trap_decoys", f"trap_decoys[{trap}] is null but the case has a single-value expectation")
            continue
        for answer in expected_answers:
            if answers_equal(value, answer):
                bad("trap_decoys", f"trap_decoys[{trap}] ({value!r}) equals the expected answer ({answer!r})")

    # (h) axes must cover every trap's axis
    need = {ctx.traps[tr]["axis"] for tr in tags.get("traps") or [] if tr in ctx.traps}
    missing = need - (set(tags.get("axes") or []) & ctx.axes)
    if missing:
        bad("axes.coverage", f"axes missing trap axes: {sorted(missing)}")

    # (i) M0: expect.files write targets need their directories pre-created in files
    file_keys = list((case.get("files") or {}).keys())
    for path in (case_expect.get("files") or {}):
        parent = str(path).rsplit("/", 1)[0] if "/" in str(path) else ""
        if not parent:
            continue
        if not any(k == parent or k.startswith(parent + "/") for k in file_keys):
            bad("m0.write_dir", f"expect.files target {path!r}: no files entry under {parent!r} "
                                "(workspace tools cannot create directories)")

    # (j) directory structure <scenario>/<id>/, id = <abbrev>-<4 digits>
    if len(rel_parts) != 2:
        bad("dir_structure", f"expected <scenario>/<id>/layout, got {'/'.join(rel_parts) or '(root)'}")
    else:
        scen_dir, dirname = rel_parts
        match = CASE_ID_RE.match(dirname)
        if not match:
            bad("dir_structure", f"case id {dirname!r} must be <scenario abbrev>-<4 digits>")
        if scenario in ctx.scenarios and scen_dir != scenario:
            bad("dir_structure", f"case sits under {scen_dir!r} but tags.scenario is {scenario!r}")
        if match and scenario in ctx.abbrev and match.group(1) != ctx.abbrev[scenario]:
            bad("dir_structure", f"id prefix {match.group(1)!r} != scenario abbrev {ctx.abbrev[scenario]!r}")

    # (k) verify.py + NOTES.md
    for rule, detail in verify_py_violations(case_dir, cid):
        bad(rule, detail)
    for rule, detail in notes_violations(case_dir, cid, scenario if isinstance(scenario, str) else ""):
        bad(rule, detail)

    # (m) notes must state the case's own expected answer, and expect.run
    # hidden inputs must stay inside the workspace.
    for rule, detail in notes_answer_violations(case_dir, case):
        bad(rule, detail)
    for rule, detail in hidden_file_violations(case):
        bad(rule, detail)
    for rule, detail in web_fixture_violations(case):
        bad(rule, detail)

    # (l) llm-authored cases stay draft until a human reviewer takes
    # ownership (reviewer starts with "human:"), then reviewed is allowed.
    author = tags.get("author")
    reviewer = tags.get("reviewer")
    human_reviewed = isinstance(reviewer, str) and reviewer.startswith("human:")
    if (
        isinstance(author, str) and author.startswith("llm:")
        and not human_reviewed and tags.get("status") != "draft"
    ):
        bad("author.status", f"author {author!r} requires status 'draft', got {tags.get('status')!r}")


FIX_MODE = False


def main(argv=None):
    global FIX_MODE
    parser = argparse.ArgumentParser(
        description="Validate workbank cases (schema v5) against docs/tag-vocab.json and the authoring rules.",
        epilog="Violations print as one JSON object per line; exit 1 if any remain. --fix only backfills fixture_bytes.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES),
                        help=f"cases root directory (default: {DEFAULT_CASES})")
    parser.add_argument("--case", action="append", default=[],
                        help="single case directory containing case.json (repeatable; overrides --cases)")
    parser.add_argument("--fix", action="store_true",
                        help="backfill tags.fixture_bytes from files content (nothing else is modified)")
    parser.add_argument("--vocab", default=str(DEFAULT_VOCAB),
                        help=f"tag vocabulary file (default: {DEFAULT_VOCAB})")
    args = parser.parse_args(argv)
    FIX_MODE = args.fix

    ctx = Ctx(args.vocab)
    case_dirs = []
    if args.case:
        for item in args.case:
            path = Path(item).resolve()
            if not (path / "case.json").is_file():
                parser.error(f"--case {item}: no case.json inside")
            case_dirs.append((path, (path.parent.name, path.name)))
    else:
        root = Path(args.cases).resolve()
        if not root.is_dir():
            parser.error(f"--cases {args.cases}: not a directory")
        for path in sorted(root.rglob("case.json")):
            case_dirs.append((path.parent, path.parent.relative_to(root).parts))

    violations = []
    fixed_notes = []
    seen_ids = {}
    checked = 0
    for case_dir, rel_parts in case_dirs:
        try:
            case = load_case(case_dir / "case.json")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            violations.append({"case_id": case_dir.name, "rule": "case_json",
                               "detail": f"case.json does not parse: {exc}"})
            continue
        if not isinstance(case, dict):
            violations.append({"case_id": case_dir.name, "rule": "case_json",
                               "detail": "case.json must contain a single bare case object"})
            continue
        checked += 1
        cid = case.get("id") if isinstance(case.get("id"), str) else case_dir.name
        if cid in seen_ids:
            violations.append({"case_id": cid, "rule": "id.unique",
                               "detail": f"id already used by {seen_ids[cid]}"})
        else:
            seen_ids[cid] = str(case_dir)
        check_case(case_dir, case, ctx, rel_parts, violations, fixed_notes)

    for note in fixed_notes:
        print(f"fixed: {note}", file=sys.stderr)
    for item in violations:
        print(json.dumps(item, ensure_ascii=False))
    print(f"{checked} case(s) checked, {len(violations)} violation(s)", file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
