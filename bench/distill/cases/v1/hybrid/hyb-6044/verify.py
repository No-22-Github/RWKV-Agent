# DISTILL-CANARY-e0b48b22 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["charges/september-2026.csv"])))
def parse(s):
    if s in ("NA", "-", ""):
        return None
    return float(s.replace("$", "").replace(",", ""))
def avg(route):
    vals = [parse(r["demurrage"]) for r in rows if r["route"] == route]
    vals = [v for v in vals if v is not None]
    return round(sum(vals) / len(vals), 2)
t1 = avg("Felixstowe-Duisburg")
t2 = avg("Tilbury-Lyon")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
