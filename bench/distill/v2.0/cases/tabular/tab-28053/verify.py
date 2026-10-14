# DISTILL-CANARY-2e2da193 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    if path.endswith(".csv"):
        assert f[path].startswith("日期,教练,班型,课时"), path
assert "按周" in f["游泳馆/说明.md"]
chosen = [p for p in f if p.endswith(".csv") and "2026-08-08" in p]
assert len(chosen) == 1, chosen
rows = list(csv.DictReader(io.StringIO(f[chosen[0]])))
dates = [r["日期"] for r in rows]
assert dates[0] == "2026-08-08" and dates[-1] == "2026-08-14"
total = round(sum(float(r["课时"]) for r in rows), 1)
ask = ["哪一周", "哪周", "哪个时间段", "时间范围", "起止日期", "日期范围", "哪几天"]
print(json.dumps({"expected_number": total, "expected_contains_any": ask}, ensure_ascii=False))
