# DISTILL-CANARY-2f60b5d8 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["logs/energy-2026-09.csv"])))
shop = [r for r in rows if r["meter"] in ("M-3A", "M-3B")]
kept = [r for r in shop if r["date"] not in ("2026-09-14", "2026-09-15", "2026-09-16")]
out = {
    "expected_number": sum(int(r["kwh"]) for r in shop),
    "expected_turn_2": sum(int(r["kwh"]) for r in kept),
    "expected_turn_4": sum(int(r["kwh"]) for r in kept if r["meter"] == "M-3B"),
}
print(json.dumps(out))
