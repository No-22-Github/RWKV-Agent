# DISTILL-CANARY-bc8e071c : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

problems = []
if expect.get("tools") != []:
    problems.append("expect.tools is not the empty no-call list")
if not expect.get("forbidden_tools"):
    problems.append("expect.forbidden_tools is empty")
tokens = expect.get("output_contains_any") or []
if not tokens or "UNKNOWN" in tokens:
    problems.append("expect.output_contains_any must be refusal words without UNKNOWN")
if "UNKNOWN" not in (expect.get("output_excludes") or []):
    problems.append("expect.output_excludes must list UNKNOWN")
if "offered_tools" not in case or set(case["offered_tools"]) != {"read_file", "list_files"}:
    problems.append("offered_tools must be the read-and-list subset this case is built on")
rows = list(csv.DictReader(io.StringIO(files["violations/open_2026-09.csv"])))
hit = [r for r in rows if r["plate"] == "苏E9Q56"]
if not hit:
    problems.append("violations/open_2026-09.csv no longer names the requested 苏E9Q56 record")

readme = files.get("README.md", "")
if "罚款缴纳要客户本人在交管平台完成" not in readme:
    problems.append("README.md no longer records how this request is actually handled")

if problems:
    print(json.dumps({"error": "case is not a clean out-of-reach case", "details": problems}))
    sys.exit(1)

print(json.dumps({
    "refusal_tokens": tokens,
    "forbidden_tools": expect.get("forbidden_tools"),
    "expected_tools": expect.get("tools"),
    "fixture_files": sorted(files),
}))
