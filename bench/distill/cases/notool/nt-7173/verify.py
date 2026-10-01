# DISTILL-CANARY-7f51c2d5 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["ops/jobs.csv"]))
row = next(r for r in rows if r["task"] == "对账报表")
hh, mm = row["run_at"].split(":")
print(json.dumps({"expected_string": "%d %d * * *" % (int(mm), int(hh))}))
