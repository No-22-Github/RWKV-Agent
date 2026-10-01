# DISTILL-CANARY-a06470d9 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = csv.DictReader(io.StringIO(case["files"]["exports/circulation-june.csv"]))
counts = {}
for r in rows:
    item = (r.get("item_id") or "").strip()
    if item.startswith("GRAND TOTAL"):
        continue
    event = (r.get("event") or "").strip()
    counts[event] = counts.get(event, 0) + 1
if not counts:
    raise SystemExit(1)
facts = [
    "%d checkouts" % counts.get("checkout", 0),
    "%d returns" % counts.get("return", 0),
    "%d renewal" % counts.get("renewal", 0),
]
print(json.dumps({"expected_contains_any": facts}))
