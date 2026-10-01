# DISTILL-CANARY-52284a54 : distillation case
import csv
import io
import json
import re

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
best = None
for path in sorted(files):
    if path.startswith("运维/") and path.endswith(".csv"):
        m = re.search(r"导出时间[：:]\s*(\d{4}-\d{2}-\d{2})", files[path])
        if not m:
            raise SystemExit("manifest %s lacks an export date" % path)
        if best is None or m.group(1) > best[0]:
            best = (m.group(1), path)
if best is None:
    raise SystemExit("no storage manifest found")
lines = files[best[1]].splitlines()
start = None
for i, line in enumerate(lines):
    if line.startswith("文件名,"):
        start = i
        break
if start is None:
    raise SystemExit("header row not found in %s" % best[1])
rows = list(csv.DictReader(io.StringIO("\n".join(lines[start:]))))
sizes = []
for r in rows:
    name = str(r.get("文件名") or "").strip()
    if not name or name == "合计":
        continue
    sizes.append(int(str(r["大小字节"]).strip()))
if not sizes:
    raise SystemExit("no data rows in the current manifest")
print(json.dumps({"expected_number": max(sizes)}))
