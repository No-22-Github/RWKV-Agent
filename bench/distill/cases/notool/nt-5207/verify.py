# DISTILL-CANARY-2e71c05b : distillation case
import json
import sys

case = json.load(open("case.json"))
turn = case["turns"][0]["expect"]

# This request cannot be carried out here, so there is no answer to recompute:
# the criterion is a refusal word list plus the ban on the bare abstention.
# The checks below only assert that the declared criterion still has that
# shape, and the script prints a non-scoring report on purpose.
problems = []
words = turn.get("output_contains_any") or []
if not words:
    problems.append("output_contains_any is empty")
if "UNKNOWN" in words:
    problems.append("output_contains_any lists UNKNOWN")
if "UNKNOWN" not in (turn.get("output_excludes") or []):
    problems.append("output_excludes does not ban UNKNOWN")
if not turn.get("forbidden_tools"):
    problems.append("forbidden_tools is empty")
if problems:
    print(json.dumps({"error": "criterion shape drifted", "details": problems}))
    sys.exit(1)

print(json.dumps({
    "refusal_words": words,
    "forbidden_tools": turn.get("forbidden_tools"),
    "output_excludes": turn.get("output_excludes"),
    "zero_call_contract": turn.get("tools"),
    "fixture_files": sorted(case["files"]),
}))
