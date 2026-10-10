# DISTILL-CANARY-08fe7c35 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
card = next(csv.DictReader(io.StringIO(case["files"]["links/site_link.csv"])))
terms = {}
for line in case["files"]["links/loss_terms.txt"].splitlines():
    words = line.split()
    terms[words[0].lower()] = float(words[2])
answer = (float(card["km"]) * float(card["db_per_km"])
          + float(card["connectors"]) * terms["connector"]
          + float(card["splices"]) * terms["splice"])
print(json.dumps({"expected_number": answer}))
