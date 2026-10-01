# DISTILL-CANARY-937d393c : distillation case
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["masters/episode-log.csv"])))
if not rows:
    raise SystemExit(1)
biggest = max(rows, key=lambda r: float((r.get("size_mb") or "0").strip()))
readme = case["files"]["README.md"]
if "raw-takes.csv" not in readme:
    raise SystemExit(1)
facts = [
    (biggest.get("episode") or "").strip(),
    (biggest.get("size_mb") or "").strip(),
    "raw-takes.csv",
]
print(json.dumps({"expected_contains_any": facts}))
