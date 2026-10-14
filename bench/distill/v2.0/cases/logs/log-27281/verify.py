# DISTILL-CANARY-7a0029a0 : distillation case
import csv
import io
import json
case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["exports/inspect-2026-09.csv"])))
fieldnames = list(rows[0].keys()) if rows else []
# Positive control: the export carries exactly the five documented columns.
if fieldnames != ["日期", "设备编号", "巡检人", "结果", "备注"]:
    raise SystemExit("fixture guard failed: inspection columns are broken")

# The case premise: no vibration measurement column exists anywhere.
if any("振动" in c or "vibration" in c.lower() for c in fieldnames):
    raise SystemExit("fixture has a vibration column; the missing-column case is broken")
marks = [r["备注"] for r in rows if "振动偏大" in r["备注"]]
if len(marks) != 2:
    raise SystemExit("fixture guard failed: hand-written vibration notes are broken")

accepted = ["振动", "vibration"]
print(json.dumps({"expected_contains_any": accepted}))
