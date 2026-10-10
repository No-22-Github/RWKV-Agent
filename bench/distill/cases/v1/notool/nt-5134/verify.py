# DISTILL-CANARY-24a8e0b1 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["clamp/silage_cards.csv"])))
answer = float(card["weighed_t"]) * float(card["dry_matter_pct"]) / 100.0
print(json.dumps({"expected_number": answer}))
