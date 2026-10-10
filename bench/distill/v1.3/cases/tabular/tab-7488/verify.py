# DISTILL-CANARY-dcda2fd0 : distillation case
import csv
import io
import json
def cols(rows):
    return list(rows[0].keys()) if rows else []

case = json.load(open("case.json"))
jul = list(csv.DictReader(io.StringIO(case["files"]["exports/settle-2026-07.csv"])))
aug = list(csv.DictReader(io.StringIO(case["files"]["exports/settle-2026-08.csv"])))
cols_ = ["结算单号", "结算日期", "场地", "项目", "金额（元）"]
# Positive control: both registers carry their documented columns and pin the
# monthly totals the quarter-to-date figure is built from.
if cols(jul) != cols_ or cols(aug) != cols_:
    raise SystemExit("fixture guard failed: settle columns are broken")
jul_total = sum(float(r["金额（元）"]) for r in jul)
aug_total = sum(float(r["金额（元）"]) for r in aug)
if abs(jul_total - 1726.00) > 0.01 or abs(aug_total - 2601.00) > 0.01:
    raise SystemExit("fixture guard failed: monthly totals are broken")

# The case premise: the September register is not in the workspace.
if "exports/settle-2026-09.csv" in case["files"]:
    raise SystemExit("fixture contains the September register; the partial-month case is broken")

accepted = ["settle-2026-09", "9 月结算", "9月结算"]
print(json.dumps({"expected_contains_any": accepted}))
