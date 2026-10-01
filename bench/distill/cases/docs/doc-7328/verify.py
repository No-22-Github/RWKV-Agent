# DISTILL-CANARY-6436ad02 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/白板组件更新记录.csv"]))
kept = [r for r in rows if r["状态"] == "正式"]
latest = max(kept, key=lambda r: r["发布日期"])
print(json.dumps({"expected_contains_any": [latest["版本号"]]}))
