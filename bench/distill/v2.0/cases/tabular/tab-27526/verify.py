# DISTILL-CANARY-482facee : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/pickup_records.csv"]))
seen = set()
for r in rows:
    if r["收衣月份"] == "2026-09" and r["服务类型"] == "羽绒服清理":
        seen.add(r["客户编号"])
print(json.dumps({"expected_number": len(seen)}))
