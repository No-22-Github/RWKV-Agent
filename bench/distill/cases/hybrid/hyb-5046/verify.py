# DISTILL-CANARY-9e8b51c4 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["press/reams-2026-09.csv"])))
if not rows:
    raise SystemExit("the press room book is empty")
reams = sum(int(row["reams"]) for row in rows)
pages = "\n".join(entry["content"] for entry in case["web_fixture"])
sheets = int(re.search(r"Woven cream is supplied (\d+) sheets to a ream", pages).group(1))
other = int(re.search(r"Laid ivory is supplied (\d+) sheets to a ream", pages).group(1))
if sheets == other:
    raise SystemExit("the two stocks must carry different sheet counts")
print(json.dumps({"expected_number": reams * sheets}))
