# DISTILL-CANARY-864b73ac : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["benches/ore_blocks.csv"])))
answer = float(row["ore_t"]) * float(row["planned_ratio"])
print(json.dumps({"expected_number": answer}))
