# DISTILL-CANARY-2b4691cf : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
rows = csv.DictReader(io.StringIO(case["files"]["sales/catfood_september.csv"]))
kg = {}
rev = {}
for r in rows:
    kg[r["品牌"]] = kg.get(r["品牌"], 0) + float(r["千克"])
    rev[r["品牌"]] = rev.get(r["品牌"], 0) + float(r["销售额"])
assert max(kg, key=kg.get) == max(rev, key=rev.get)
print(json.dumps({
    "expected_number": round(sum(kg.values()), 2),
    "turn_2_expected_contains": max(rev, key=rev.get),
}))
