# DISTILL-CANARY-dcdd298c : distillation case
import csv, io, json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["到货差异登记.tsv"]), delimiter="\t")
n = sum(1 for r in rows if float(r["差异数量(公斤)"]) > 0)
print(json.dumps({"expected_number": n}))
