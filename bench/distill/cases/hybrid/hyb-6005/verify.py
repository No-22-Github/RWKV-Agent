# DISTILL-CANARY-d8c0613a : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]['spraying/july-2026.csv']))
total = round(sum(float(row['hectares']) for row in rows if row['farm'] == 'Grange Farm' and row['field'] == 'Long Meadow'), 2)
print(json.dumps({"expected_number": total}))
