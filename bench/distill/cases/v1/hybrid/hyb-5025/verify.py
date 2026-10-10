# DISTILL-CANARY-a4d7f268 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["collections/september-2026.csv"])))
hill = [row for row in rows if row["flock"] == "Hill flock"]
holdings = {row["holding"] for row in hill}
if len(holdings) != 2:
    raise SystemExit("two holdings must keep a Hill flock")
answer = max(int(row["eggs"]) for row in hill if row["holding"] == "Nethercote Farm")
other = max(int(row["eggs"]) for row in hill if row["holding"] != "Nethercote Farm")
assert answer != other, "the two Hill flocks must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
