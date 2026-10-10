# DISTILL-CANARY-eab7eb6a : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["travel/train_options.csv"])))
keys = ['train']
got = sorted(tuple(r[k] for k in keys) for r in rows)
want = sorted(tuple(r) for r in [["G7315"], ["G7357"]])

problems = []
if got != want:
    problems.append("fixture no longer matches the candidate pair named in the prompt")

if problems:
    print(json.dumps({"error": "fixture drift", "details": problems}))
    sys.exit(1)

# The correct first turn asks which of the candidates to act on. The fixture check
# above re-derives the candidates; the word list below is the authored surface form.
print(json.dumps({"expected_contains_any": ["？", "?", "哪班", "哪一班", "哪趟", "哪个"]}))
