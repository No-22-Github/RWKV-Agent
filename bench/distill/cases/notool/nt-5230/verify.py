# DISTILL-CANARY-48031344 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
row = next(csv.DictReader(io.StringIO(case["files"]["bins/drying_batch.csv"])))
weighed = float(row["weighed_t"])
dry_share = 100.0 - float(row["moisture_pct"])
target_share = 100.0 - float(row["target_pct"])
answer = weighed - weighed * dry_share / target_share
print(json.dumps({"expected_number": answer}))
