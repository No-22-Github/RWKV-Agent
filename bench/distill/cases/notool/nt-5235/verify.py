# DISTILL-CANARY-cd810116 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["benches/bench_cards.csv"])))
answer = float(row["waste_m3"]) / float(row["ore_t"])
print(json.dumps({"expected_number": answer}))
