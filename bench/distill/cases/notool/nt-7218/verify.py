# DISTILL-CANARY-c0018c46 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["cards/member_cards.csv"])))
keys = ['card_type']
got = sorted(tuple(r[k] for k in keys) for r in rows)
want = sorted(tuple(r) for r in [["团课卡"], ["私教卡"]])

problems = []
if got != want:
    problems.append("fixture no longer matches the candidate pair named in the prompt")

if problems:
    print(json.dumps({"error": "fixture drift", "details": problems}))
    sys.exit(1)

# The correct first turn asks which of the candidates to act on. The fixture check
# above re-derives the candidates; the word list below is the authored surface form.
print(json.dumps({"expected_contains_any": ["？", "?", "哪张", "哪个", "哪一种", "哪节课"]}))
