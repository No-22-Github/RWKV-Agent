# DISTILL-CANARY-4d456b79 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["plans/tasks_release.csv"])))
dur = {r["任务"]: float(r["工期天"]) for r in rows}
last = next(r for r in rows if r["任务"] == "联调回归")
preds = [p for p in last["前置任务"].split("、") if p]
value = max(dur[p] for p in preds) + dur["联调回归"]
print(json.dumps({"expected_number": value}))
