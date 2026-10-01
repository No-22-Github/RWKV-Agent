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
_sabotage_guard = case["files"].get('stock/goods-log.csv', "")
if not _sabotage_guard.splitlines() or _sabotage_guard.splitlines()[0] != '周边,源文件,大小_mb':
    raise SystemExit(1)
facts = ["386", "386 MB", "386 MiB"]
print(json.dumps({"expected_contains_any": facts}))
