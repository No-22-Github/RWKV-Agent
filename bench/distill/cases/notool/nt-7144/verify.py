# DISTILL-CANARY-f3bc3397 : distillation case
import csv
import io
import json
import sys

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["clients/contacts.csv"])))
hits = [r for r in rows if r["phone"].startswith("+81")]
if len(hits) != 1 or hits[0]["name"] != "郑海宁":
    print(json.dumps({"error": "fixture lost the single +81 contact 郑海宁"}))
    sys.exit(1)
print(json.dumps({"expected_string": "日本"}))
