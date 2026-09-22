# WORKBANK-CANARY-c4d17e08 : bank artifact, excluded from training corpora
"""Recompute the paid study leave allowance from the Larkspur handbook.

Reads the fixture out of case.json and derives the figure from the handbook's
study leave section, independently of the expect block.
"""
import json
import re

case = json.load(open("case.json"))
handbook = case["files"]["handbook/staff-handbook.md"]

if not handbook.splitlines()[0].startswith("# Staff handbook"):
    raise SystemExit("handbook title line not found")

parts = handbook.split("## 4 Study leave", 1)
if len(parts) != 2:
    raise SystemExit("study leave section not found")
body = parts[1].split("\n## ", 1)[0]

match = re.search(r"up to (\d+) working days of paid study leave", body)
if not match:
    raise SystemExit("study leave allowance not stated in the study leave section")

print(json.dumps({"expected_number": int(match.group(1))}))
