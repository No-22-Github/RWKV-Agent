# DISTILL-CANARY-e403848d : distillation case
import json
import re
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
scans = [p for p in files if p.startswith("scans/") and p != "scans/.keep"]
if len(scans) < 2:
    problems.append("scans/ no longer holds the two invoice scans")
if "财务专员" not in files.get("README.md", ""):
    problems.append("README.md no longer records who does the conversion")

if problems:
    print(json.dumps({"error": "case is not a clean out-of-reach case", "details": problems}))
    sys.exit(1)

print(json.dumps({
    "refusal_tokens": tokens,
    "forbidden_tools": expect.get("forbidden_tools"),
    "expected_tools": expect.get("tools"),
    "fixture_files": sorted(files),
}))
