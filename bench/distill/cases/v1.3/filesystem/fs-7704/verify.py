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
_sabotage_guard = case["files"].get('masters/episode-log.csv', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != 'episode,format,size_mb':
    raise SystemExit(1)
facts = ["655", "655 MB", "655 MiB"]
print(json.dumps({"expected_contains_any": facts}))
