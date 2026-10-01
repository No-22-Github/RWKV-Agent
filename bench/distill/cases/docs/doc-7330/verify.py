# DISTILL-CANARY-de5d2dfa : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["docs/云打印发布目录.csv"]))
kept = [r for r in rows if r["产品"] == "云打印服务端"]
latest = max(kept, key=lambda r: r["发布日期"])
print(json.dumps({"expected_contains_any": [latest["版本号"]]}))
