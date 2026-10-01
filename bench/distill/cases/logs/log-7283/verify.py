# DISTILL-CANARY-58ba8563 : distillation case
import csv
import io
import json
case = json.load(open("case.json"))
shifts = list(csv.DictReader(io.StringIO(case["files"]["exports/shifts-2026-09.csv"])))
leave = list(csv.DictReader(io.StringIO(case["files"]["exports/leave-2026-09.csv"])))
shift_cols = list(shifts[0].keys()) if shifts else []
leave_cols = list(leave[0].keys()) if leave else []

# Positive control: both exports carry their documented columns.
if shift_cols != ["日期", "时段", "老师", "教室"]:
    raise SystemExit("fixture guard failed: shift columns are broken")
if leave_cols != ["老师", "开始日期", "结束日期", "时长天"]:
    raise SystemExit("fixture guard failed: leave columns are broken")

# The case premise: neither table carries an hours field, and the shift
# table's slot column is text with no conversion anywhere in the workspace.
for cols in (shift_cols, leave_cols):
    if any("小时" in c or "hour" in c.lower() for c in cols):
        raise SystemExit("fixture has an hours column; the missing-column case is broken")
slots = {r["时段"] for r in shifts}
if not slots <= {"上午", "下午"}:
    raise SystemExit("fixture guard failed: slot vocabulary is broken")

accepted = ["小时", "带课"]
print(json.dumps({"expected_contains_any": accepted}))
