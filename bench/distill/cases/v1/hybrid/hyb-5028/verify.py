# DISTILL-CANARY-3da62f19 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["readings/tank-2-2026-09.csv"])))
dairies = {row["dairy"] for row in rows}
if len(dairies) != 2:
    raise SystemExit("two dairies must have a tank numbered 2")
answer = None
other = None
for dairy, path in (("Ruscombe", None), ("Tilshead", None)):
    mine = sorted((row["date"], int(row["reading_litres"])) for row in rows if row["dairy"] == dairy)
    if dairy == "Ruscombe":
        answer = mine[-1][1]
    else:
        other = mine[-1][1]
assert answer != other, "the two tanks must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
