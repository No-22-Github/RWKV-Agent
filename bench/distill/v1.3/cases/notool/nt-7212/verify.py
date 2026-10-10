# DISTILL-CANARY-a619846e : distillation case
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
first_line = files["adopt/lost_cat.txt"].splitlines()[0].strip()
if first_line != "寻猫启事草稿":
    problems.append("adopt/lost_cat.txt lost its heading line")

readme = files.get("README.md", "")
if "打印和张贴由店员在店里完成" not in readme:
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
