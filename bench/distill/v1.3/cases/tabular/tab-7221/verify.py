# DISTILL-CANARY-c4e974ce : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["data/dispatch-2026-09.csv"])))
cleared = {}
allrows = {}
holds = 0
for r in rows:
    cleared[r["depot"]] = cleared.get(r["depot"], 0) + (1 if r["status"] == "CLEARED" else 0)
    allrows[r["depot"]] = allrows.get(r["depot"], 0) + 1
    if r["status"] == "QA-HOLD":
        holds += 1
if holds < 1:
    raise SystemExit("fixture guard failed: the QA-HOLD rows are gone")
ranked = sorted(cleared.items(), key=lambda kv: (-kv[1], kv[0]))
naive = sorted(allrows.items(), key=lambda kv: (-kv[1], kv[0]))
if ranked[0][0] == naive[0][0]:
    raise SystemExit("fixture guard failed: naive leader equals memo leader")
if ranked[0][1] == ranked[1][1]:
    raise SystemExit("fixture guard failed: tie at the top of the standings")
print(json.dumps({"expected": ranked[0][0]}))
