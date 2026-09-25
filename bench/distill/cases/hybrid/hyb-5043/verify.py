# DISTILL-CANARY-a18c6d29 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["stores/bolt-bins.csv"])))
bolts = {row["finish"]: int(row["in_stock"]) for row in rows if row["item"] == "M8 bolt"}
if len(bolts) != 2:
    raise SystemExit("the list must carry two M8 bolt bins of different finish")
answer = bolts["stainless"]
other = bolts["zinc"]
assert answer != other, "the two bins must differ so the clarification matters"
print(json.dumps({"expected_number": answer}))
