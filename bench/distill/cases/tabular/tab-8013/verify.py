# DISTILL-CANARY-f7d5d403 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Nightly export runs for Corvane Analytics")
vals = []
for r in csv.DictReader(io.StringIO(case["files"]["jobs/export-runs.csv"])):
    e = r["elapsed"]
    vals.append(float(e[:-2]) / 1000 if e.endswith("ms") else float(e[:-1]))
print(json.dumps({"expected_number": round(sum(vals) / len(vals), 2)}))
