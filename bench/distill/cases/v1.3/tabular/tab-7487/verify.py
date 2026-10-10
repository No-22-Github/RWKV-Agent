# DISTILL-CANARY-9aef7f9e : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
rep = list(csv.DictReader(io.StringIO(case["files"]["exports/repairs-2026-09.csv"])))
pts = list(csv.DictReader(io.StringIO(case["files"]["exports/parts-2026-09.csv"])))
rep_cols = cols(rep)
pts_cols = cols(pts)
# Positive control: both tables carry their documented columns and join cleanly.
if rep_cols != ["工单号", "车牌", "进场日期", "维修项目", "技师"]:
    raise SystemExit("fixture guard failed: repair columns are broken")
if pts_cols != ["工单号", "配件", "数量", "领用日期"]:
    raise SystemExit("fixture guard failed: parts columns are broken")
rep_ids = {r["工单号"] for r in rep}
if not {p["工单号"] for p in pts} <= rep_ids or len(rep) != 8:
    raise SystemExit("fixture guard failed: join keys are broken")

# The case premise: neither table carries an hours or labour-fee field.
for cs in (rep_cols, pts_cols):
    for c in cs:
        if "工时" in c or "工费" in c or "hour" in c.lower() or "fee" in c.lower():
            raise SystemExit("fixture has a hours/fee column; the missing-column case is broken")

accepted = ["工时", "技师工时"]
print(json.dumps({"expected_contains_any": accepted}))
