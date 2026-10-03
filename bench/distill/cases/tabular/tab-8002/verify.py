# DISTILL-CANARY-4cbb6b07 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
north = list(csv.DictReader(io.StringIO(files["售后/华北服务站-8月.csv"])))
online = list(csv.DictReader(io.StringIO(files["售后/线上客服-8月.csv"])))
assert north and set(north[0]) == {"工单号", "受理日期", "品类", "状态"}
assert max(r["受理日期"] for r in online) <= "2026-08-20"
print(json.dumps({"expected_number": len(north)}))
