# DISTILL-CANARY-93a5ac59 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["data/动销-2026-09-13.csv"]))
lines = [",".join([r["品类"], r["变动"], r["数量"]]) for r in rows]
print(json.dumps({"files": {"reports/库存周报.md": "\n".join(lines) + "\n"}}))
