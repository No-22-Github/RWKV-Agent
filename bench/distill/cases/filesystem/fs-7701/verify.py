# DISTILL-CANARY-377297ad : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
current = list(csv.DictReader(io.StringIO(case["files"]["catalog/print-index.csv"])))
archived = list(csv.DictReader(io.StringIO(case["files"]["archive/print-index.csv"])))
if not current or not archived:
    raise SystemExit(1)
luster = sum(1 for r in current if (r.get("paper") or "").strip() == "luster")
readme = case["files"]["README.md"]
if "2024" not in readme:
    raise SystemExit(1)
facts = [
    "%d prints" % len(current),
    "%d luster" % luster,
    "%d archived prints" % len(archived),
]
print(json.dumps({"expected_contains_any": facts}))
