# DISTILL-CANARY-76a401f0 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["meters/output-2026-06.csv"])))
def mean(turbine):
    vals = [float(r["kwh"]) for r in rows
            if r["turbine"] == turbine and r["kwh"] not in ("-", "NA", "")]
    return round(sum(vals) / len(vals), 2)
t1 = mean("TW-01")
t2 = mean("TW-02")
assert t1 == case["turns"][0]["expect"]["expected_number"]
assert t2 == case["turns"][1]["expect"]["expected_number"]
print(json.dumps({"expected_number": t1, "turn2": t2}))
