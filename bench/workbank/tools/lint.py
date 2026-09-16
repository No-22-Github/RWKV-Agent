#!/usr/bin/env python3
"""lint.py — bank-side validator for workbank hand-written cases (schema v5).

Checks every case under --cases (a tree of <scenario>/<id>/case.json) or a
single --case directory against docs/tag-vocab.json and the authoring rules:

  tags.enum / tags.required   (a) tag vocabulary + required keys
  prompt.tool_name            (b) no tool names in any turn prompt
  prompt.forbidden_word       (b) no forbidden words of the case's own traps
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
  author.status               (l) author llm:* implies status draft
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

    # (b) prompts: tool names + this case's trap forbidden words (case-insensitive substring)
    turns = [t for t in case.get("turns") or [] if isinstance(t, dict)]
    prompts = [t.get("prompt") or "" for t in turns]
    for idx, prompt in enumerate(prompts, 1):
        low = prompt.lower()
        for tool in ctx.tools:
            if tool in low:
                bad("prompt.tool_name", f"turn {idx}: tool name {tool!r} in prompt")
        for trap in tags.get("traps") or []:
            words = ctx.traps.get(trap, {}).get("forbidden_words", []) if trap in ctx.traps else []
            for word in words:
                if word.lower() in low:
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

    # (l) llm-authored cases stay draft
    author = tags.get("author")
    if isinstance(author, str) and author.startswith("llm:") and tags.get("status") != "draft":
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
