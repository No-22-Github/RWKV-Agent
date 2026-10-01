# DISTILL-CANARY-b5dfa0ef : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["stock/goods-log.csv"])))
if not rows:
    raise SystemExit(1)
biggest = max(rows, key=lambda r: float((r.get("大小_mb") or "0").strip()))
readme = case["files"]["README.md"]
if "草稿" not in readme:
    raise SystemExit(1)
facts = [
    (biggest.get("大小_mb") or "").strip(),
    (biggest.get("周边") or "").strip(),
    "草稿",
]
print(json.dumps({"expected_contains_any": facts}))
