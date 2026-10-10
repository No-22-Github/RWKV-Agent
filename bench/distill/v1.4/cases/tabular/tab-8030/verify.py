# DISTILL-CANARY-f12291ee : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
a = list(csv.DictReader(io.StringIO(files["更换/恒信环保-2026-09.csv"])))
b = list(csv.DictReader(io.StringIO(files["更换/蓝漾水务-2026-09.csv"])))
assert a and set(a[0]) == {"工单号", "日期", "网点", "滤芯型号"}
assert b and set(b[0]) == {"工单号", "日期", "网点", "滤芯型号"}
assert max(r["日期"] for r in a) <= "2026-09-30"
assert max(r["日期"] for r in b) <= "2026-09-12"
print(json.dumps({"expected_number": len(a)}))
