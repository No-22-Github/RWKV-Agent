# DISTILL-CANARY-d9604a2b : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["crates/gate-log-2026-09.csv"])))
week = [row for row in rows if "2026-09-28" <= row["date"] <= "2026-10-04"]
september_part = [row for row in week if row["date"].startswith("2026-09")]
if len(week) != 7:
    raise SystemExit("the week of 28 September must hold seven gate days")
answer = sum(int(row["crates"]) for row in week)
other = sum(int(row["crates"]) for row in september_part)
assert answer != other, "the whole week must differ from its September part"
print(json.dumps({"expected_number": answer}))
