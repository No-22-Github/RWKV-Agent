#!/usr/bin/env python3
"""web_hitcheck.py — verify that a web/hybrid case's fixture answers its own NOTES.

For every case with scenario web/hybrid and a non-empty web_fixture, parse the
five rewritten queries from the NOTES.md section "## Five alternative phrasings"
and apply the harness rule (internal/agent/eval/webfixture.go): a search hits an
entry when the entry's query_match is a case-insensitive substring of the query
and the entry has both query_match and url (entries without a url are never
returned by the fixture search provider). Every one of the 5 queries must hit
at least one fixture entry; any miss exits 1.

Additionally warns (does not fail) about entries whose advertised url can never
resolve through the fixture fetch provider, i.e. no url_match that is a
case-insensitive substring of the entry's own url.
Standard library only.
"""

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
WORKBANK_DIR = TOOLS_DIR.parent
DEFAULT_CASES = WORKBANK_DIR / "cases"
PHRASINGS_RE = re.compile(r"^##\s+Five alternative phrasings.*$", re.M)
NEXT_HEADING_RE = re.compile(r"^##\s+", re.M)
ITEM_RE = re.compile(r"^\s*(?:\d+[.)]|\*|-)\s+(\S.*?)\s*$")


def parse_phrasings(notes_path):
    """Return (queries, problem) — five rewritten queries from NOTES.md."""
    if not notes_path.is_file():
        return [], "NOTES.md missing"
    text = notes_path.read_text(encoding="utf-8")
    match = PHRASINGS_RE.search(text)
    if not match:
        return [], "no '## Five alternative phrasings' section in NOTES.md"
    rest = text[match.end():]
    nxt = NEXT_HEADING_RE.search(rest)
    body = rest[: nxt.start()] if nxt else rest
    queries = [m.group(1) for line in body.splitlines() if (m := ITEM_RE.match(line))]
    if len(queries) != 5:
        return queries, f"expected exactly 5 phrasings, found {len(queries)}"
    return queries, None


def check_case(case_dir, case):
    cid = case.get("id") or case_dir.name
    problems = []
    warnings = []
    entries = case.get("web_fixture") or []
    if not entries:
        return cid, ["web_fixture is empty for a web/hybrid case"], warnings

    queries, problem = parse_phrasings(case_dir / "NOTES.md")
    if problem:
        return cid, [problem], warnings

    searchable = [e for e in entries if e.get("query_match") and e.get("url")]
    patterns = [e["query_match"].lower() for e in searchable]
    for idx, query in enumerate(queries, 1):
        hits = [p for p in patterns if p in query.lower()]
        if not hits:
            problems.append(
                f"phrasing {idx} {query!r} hits no fixture entry "
                f"(searchable query_match values: {patterns or 'none'})")

    for entry in entries:
        url, url_match = entry.get("url") or "", entry.get("url_match") or ""
        if url and not (url_match and url_match.lower() in url.lower()):
            warnings.append(
                f"entry url {url!r} can never resolve in web_fetch "
                f"(no url_match that is a substring of it; fetch would return the not-found page)")
    return cid, problems, warnings


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check that the 5 alternative phrasings in each web/hybrid case's NOTES "
                    "hit at least one web_fixture entry under the harness substring rule.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES),
                        help=f"cases root directory (default: {DEFAULT_CASES})")
    parser.add_argument("--case", action="append", default=[],
                        help="single case directory containing case.json (repeatable; overrides --cases)")
    args = parser.parse_args(argv)

    case_dirs = []
    if args.case:
        for item in args.case:
            path = Path(item).resolve()
            if not (path / "case.json").is_file():
                parser.error(f"--case {item}: no case.json inside")
            case_dirs.append(path)
    else:
        root = Path(args.cases).resolve()
        if not root.is_dir():
            parser.error(f"--cases {args.cases}: not a directory")
        case_dirs = [p.parent for p in sorted(root.rglob("case.json"))]

    checked = failed = 0
    for case_dir in case_dirs:
        try:
            with open(case_dir / "case.json", encoding="utf-8") as fh:
                case = json.load(fh)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            print(f"FAIL {case_dir.name}: case.json does not parse: {exc}", file=sys.stderr)
            failed += 1
            continue
        tags = case.get("tags") or {}
        if tags.get("scenario") not in ("web", "hybrid") or not (case.get("web_fixture") or []):
            continue
        checked += 1
        cid, problems, warnings = check_case(case_dir, case)
        for problem in problems:
            print(json.dumps({"case_id": cid, "miss": problem}, ensure_ascii=False))
        for warning in warnings:
            print(f"warning {cid}: {warning}", file=sys.stderr)
        if problems:
            failed += 1
        else:
            print(f"ok {cid}: 5/5 phrasings hit the fixture", file=sys.stderr)

    print(f"{checked} web/hybrid case(s) with fixture checked, {failed} failed", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
