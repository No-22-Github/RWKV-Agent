# DISTILL-CANARY-5ef5ba6f : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/播放器发布记录.csv"]))
latest = max(rows, key=lambda r: r["发布日期"])
print(json.dumps({"expected_contains_any": [latest["版本号"]]}))
