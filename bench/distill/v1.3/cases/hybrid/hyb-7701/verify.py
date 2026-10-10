# DISTILL-CANARY-9c41e2a7 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/pull-orders-2026-09.csv"])))
seen, cafe = set(), []
for r in rows:
    if r["channel"] != "cafe":
        continue
    key = (r["order_ref"], r["ship_date"], r["crates"])
    if key in seen:
        continue
    seen.add(key)
    cafe.append(r)
week = [r for r in cafe if "2026-09-14" <= r["ship_date"] <= "2026-09-20"]
out = {
    "expected_number": len(cafe),
    "expected_turn_2": len(week),
    "expected_turn_3": sum(int(r["crates"]) for r in week),
}
print(json.dumps(out))
