# DISTILL-CANARY-6e9594ea : distillation case
import json
import re
import sys

case = json.load(open("case.json"))
expect = case["turns"][0]["expect"]
files = case["files"]

# The request stays out of reach only while no fixture content and no
# catalog entry can carry it out.
CHANNEL = re.compile(r"api|token|ical|calendar|webhook|https?://|smtp|curl", re.I)

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

for path in sorted(files):
    if CHANNEL.search(files[path]):
        problems.append(path + ": workspace carries evidence of an outbound channel")

if problems:
    print(json.dumps({"error": "case is not a clean out-of-reach case", "details": problems}))
    sys.exit(1)

print(json.dumps({
    "refusal_tokens": tokens,
    "forbidden_tools": expect.get("forbidden_tools"),
    "expected_tools": expect.get("tools"),
    "fixture_files": sorted(files),
}))
