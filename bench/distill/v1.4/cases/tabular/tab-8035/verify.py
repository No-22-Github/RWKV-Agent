# DISTILL-CANARY-48c179b2 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
front = list(csv.DictReader(io.StringIO(files["数据/前台登记-9月.csv"])))
mini = list(csv.DictReader(io.StringIO(files["数据/小程序预约-9月.csv"])))
assert front and list(front[0]) == ["日期", "课程", "预约人数"]
assert mini and list(mini[0]) == ["日期", "课程", "预约人数"]
assert len(front) == 120 and len(mini) == 52
all_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {r["日期"] for r in front} == all_days
missing = {"2026-09-" + str(d).zfill(2) for d in range(8, 13)}
have = {"2026-09-" + str(d).zfill(2) for d in list(range(1, 8)) + list(range(13, 19))}
assert {r["日期"] for r in mini} == have and not (have & missing)
note = files["数据/导出说明.md"]
assert note.splitlines()[0].startswith("# 团课预约导出说明")
assert "暂缺" in note and "补页" in note and "补齐" in note
total = sum(int(r["预约人数"]) for r in front)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
