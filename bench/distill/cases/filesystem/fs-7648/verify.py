# DISTILL-CANARY-3ae4d581 : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
lines = case["files"]["运维/存储明细.csv"].splitlines()
start = None
for i, line in enumerate(lines):
    if line.startswith("文件名,"):
        start = i
        break
if start is None:
    raise SystemExit("header row not found in the storage manifest")
rows = list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))
sizes = []
for r in rows:
    name = str(r.get("文件名") or "").strip()
    if not name or name == "合计":
        continue
    sizes.append(int(str(r["大小字节"]).strip()))
if not sizes:
    raise SystemExit("no data rows in the storage manifest")
print(json.dumps({"expected_number": max(sizes)}))
