# DISTILL-CANARY-6fdf506f : distillation case
import csv
import io
import json

case = json.load(open("case.json", encoding="utf-8"))
files = case["files"]
hits = []
for path in sorted(files):
    if path.startswith("档案室/") and path.endswith(".csv"):
        for row in csv.DictReader(io.StringIO(files[path])):
            if str(row["检查日期"]).strip().startswith("2026-06"):
                hits.append(path)
                break
if len(hits) != 1:
    raise SystemExit("expected exactly one June inspection sheet, found %d: %r" % (len(hits), hits))
print(json.dumps({"expected_string": hits[0]}, ensure_ascii=False))
