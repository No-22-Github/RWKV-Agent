# DISTILL-CANARY-e73c5be1 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["albums/batches.csv"])))
keys = ['batch']
got = sorted(tuple(r[k] for k in keys) for r in rows)
want = sorted(tuple(r) for r in [["外拍-海雾线"], ["外拍-老城线"]])

problems = []
if got != want:
    problems.append("fixture no longer matches the candidate pair named in the prompt")

if problems:
    print(json.dumps({"error": "fixture drift", "details": problems}))
    sys.exit(1)

# The correct first turn asks which of the candidates to act on. The fixture check
# above re-derives the candidates; the word list below is the authored surface form.
print(json.dumps({"expected_contains_any": ["？", "?", "哪批", "哪一批", "哪条", "哪个"]}))
