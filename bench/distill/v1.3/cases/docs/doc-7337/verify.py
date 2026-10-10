# DISTILL-CANARY-6fccaaa0 : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["帮助导航.csv"]))
missing = sorted({r["链接路径"] for r in rows if r["链接路径"] not in case["files"]})
print(json.dumps({"expected_number": len(missing)}))
