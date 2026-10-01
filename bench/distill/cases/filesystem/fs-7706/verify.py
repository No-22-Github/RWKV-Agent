# DISTILL-CANARY-bff6dcb6 : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
current = list(csv.DictReader(io.StringIO(case["files"]["patterns/index-2026.csv"])))
archived = list(csv.DictReader(io.StringIO(case["files"]["patterns/index-2024.csv"])))
if not current or not archived:
    raise SystemExit(1)
batik = sum(1 for r in current if (r.get("工艺") or "").strip() == "蜡染")
readme = case["files"]["README.md"]
if "2024" not in readme:
    raise SystemExit(1)
facts = [
    "%d 幅" % len(current),
    "%d 幅蜡染" % batik,
    "%d 幅" % len(archived),
]
print(json.dumps({"expected_contains_any": facts}))
